#!/usr/bin/env python3
"""
P4.4: Pre-dispatch validation for render-production workflow.

Catches the problems that caused 5 failed Q-004 attempts BEFORE dispatching:
1. Frame range arithmetic (24,151 vs 23,151 error)
2. Composition duration mismatch
3. Audio files missing or too short for video duration
4. Workflow YAML syntax errors
5. Required files present for push

Usage:
    python3 .github/scripts/validate_dispatch.py \
        --composition HousingBroke \
        --start-frame 0 \
        --end-frame 23150 \
        --chunk-size 600 \
        --vo-file public/audio/vo_housingbroke.wav \
        --bed-file public/audio/bed.mp3 \
        --with-audio true

Exit 0 = safe to dispatch. Exit 1 = problems found (listed).
"""
import argparse
import os
import re
import subprocess
import sys

# R-2: composition contract lives next to this script; make it importable
# regardless of the caller's working directory.
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)
from composition_contract import (
    validate_for_dispatch, check_registry_consistency, check_no_duplicate_ids)


def check_frame_math(start, end, chunk_size):
    """Validate frame range arithmetic."""
    errors = []
    if start < 0:
        errors.append(f"start_frame ({start}) must be >= 0")
    if end < start:
        errors.append(f"end_frame ({end}) < start_frame ({start})")
    total = end - start + 1
    if total <= 0:
        errors.append(f"Total frames ({total}) must be positive")
    if chunk_size <= 0:
        errors.append(f"chunk_size ({chunk_size}) must be positive")
    else:
        num_chunks = (total + chunk_size - 1) // chunk_size
        last_chunk_frames = total - (num_chunks - 1) * chunk_size
        print(f"  Frames: {start}-{end} = {total} frames")
        print(f"  Chunks: {num_chunks} (last chunk: {last_chunk_frames} frames)")
        if last_chunk_frames <= 0:
            errors.append("Last chunk has zero frames (arithmetic error)")
    return errors, total


def check_composition(composition, expected_frames, repo_root):
    """Verify composition exists and duration matches."""
    errors = []
    # Find composition definition
    comp_file = None
    for root, dirs, files in os.walk(os.path.join(repo_root, "src")):
        # Skip node_modules
        dirs[:] = [d for d in dirs if d != "node_modules"]
        for f in files:
            if f.endswith((".tsx", ".ts")) and composition in f:
                comp_file = os.path.join(root, f)
                break
        if comp_file:
            break
    
    if not comp_file:
        # Try HousingBroke.tsx specifically
        hb_path = os.path.join(repo_root, "src", "housing", "HousingBroke.tsx")
        if os.path.exists(hb_path) and composition == "HousingBroke":
            comp_file = hb_path
        else:
            errors.append(f"Composition file not found for '{composition}'")
            return errors
    
    print(f"  Composition file: {comp_file}")
    
    with open(comp_file) as f:
        content = f.read()
    
    declared = None
    
    # P4.4: Try HB_TOTAL pattern (S1+S2+... constants)
    # e.g., const S1 = 2127; ... export const HB_TOTAL = S1 + S2 + ...;
    section_vals = {}
    for m in re.finditer(r'(?:const|export const)\s+(S\d+)\s*=\s*(\d+)', content):
        section_vals[m.group(1)] = int(m.group(2))
    if section_vals:
        # Check if HB_TOTAL sums these
        if re.search(r'HB_TOTAL\s*=\s*S\d+\s*\+', content):
            declared = sum(section_vals.values())
            print(f"  Sections: {section_vals}")
            print(f"  Computed HB_TOTAL: {declared}")
    
    # Fallback: direct durationInFrames
    if declared is None:
        m = re.search(r'durationInFrames[=:\s]+(\d+)', content)
        if m:
            declared = int(m.group(1))
            print(f"  Declared durationInFrames: {declared}")
    
    if declared is not None:
        if declared != expected_frames:
            errors.append(
                f"Composition has {declared} frames, "
                f"but dispatch requests {expected_frames} frames "
                f"(frames 0-{expected_frames - 1}). "
                f"Use --end-frame {declared - 1}."
            )
        else:
            print(f"  Frame count matches: {declared}")
    else:
        print(f"  WARNING: Could not determine frame count from {comp_file}")
        print(f"  (Manual verification required)")
    
    return errors


# R-*: beat files consumed as checked-in JSON by beat-driven compositions.
# The beat compiler is not in the pipeline; the dispatch gate below proves the
# checked-in beats honor the canonical EDITORIAL_BEAT_SCHEMA contract instead.
BEAT_FILES = {
    "ProductionBeats": "src/compiled/beat_timeline.json",
    "B6A": "src/compiled/beat_timeline.json",
    "B6B": "src/compiled/beat_timeline.json",
    "P3Rehearsal": "src/compiled_p3/beat_timeline.json",
    "ChainTest": "src/chaintest/beat_timeline.json",
}


def beat_artifact_provenance(beat_path, repo_root):
    """Classify where a beat artifact came from.

    Returns {"file": <rel path>, "provenance": "checked-in" |
    "compiler-generated" | "unknown", "generator": <note>}.

    Provenance fact (verified 2026-10-10): beat_compiler.py is disconnected
    — zero production callers — and every beat file this gate checks predates
    it, so an artifact present in the checkout is hand-authored ("checked-in"),
    not compiler-generated. Provenance is recorded from checkout state at
    gate time; the file's content is not parsed for authorship.
    """
    rel = os.path.relpath(os.path.abspath(beat_path),
                          os.path.abspath(repo_root))
    if not os.path.exists(beat_path):
        return {"file": rel, "provenance": "unknown",
                "generator": "artifact not present in this checkout"}
    return {"file": rel, "provenance": "checked-in",
            "generator": "hand-authored; beat_compiler.py disconnected "
                         "(no production caller)"}


class BeatCheckResult(list):
    """Error list from check_beat_contract carrying the beat artifact's
    provenance record in .provenance, so callers and dispatch logs can
    report which artifact was validated and where it came from. Still a
    plain list of error strings, so existing call sites work unchanged."""

    def __init__(self, *args):
        super().__init__(*args)
        self.provenance = None


def _resolve_beat_schema(repo_root):
    """Locate the beat schema. Fail-closed: a missing schema is an error.

    Resolution order:
      1. Repo-vendored replica: <repo>/.github/schemas/EDITORIAL_BEAT_SCHEMA.json
         (pinned copy; this is what GitHub runners read — the canonical file
         lives outside the repo and is absent from runner checkouts).
      2. Canonical source: <parent-of-repo>/EDITORIAL_BEAT_SCHEMA.json
         (local-dev fallback).

    Returns (schema_path_or_None, error_list).
    """
    vendored = os.path.join(repo_root, ".github", "schemas",
                            "EDITORIAL_BEAT_SCHEMA.json")
    canonical = os.path.join(os.path.dirname(os.path.abspath(repo_root)),
                             "EDITORIAL_BEAT_SCHEMA.json")
    for path in (vendored, canonical):
        if os.path.exists(path):
            return path, []
    return None, [
        "Beat schema gate fail-closed: EDITORIAL_BEAT_SCHEMA.json not found. "
        f"Checked repo-vendored {vendored} and canonical {canonical}. "
        "Beat-driven compositions cannot be validated without the schema; "
        "dispatch is blocked."
    ]


def _load_beat_schema(schema_path):
    """Parse the beat schema. Fail-closed: malformed JSON is an error, never
    a crash that could be mistaken for a pass elsewhere in the chain.

    Returns (schema_dict_or_None, error_list).
    """
    import json
    try:
        with open(schema_path) as f:
            return json.load(f), []
    except json.JSONDecodeError as e:
        return None, [
            f"Beat schema gate fail-closed: {schema_path} is not valid "
            f"JSON: {e}"
        ]
    except OSError as e:
        return None, [
            f"Beat schema gate fail-closed: cannot read {schema_path}: {e}"
        ]


def check_beat_contract(composition, repo_root):
    """Validate checked-in beats against the canonical beat schema.

    Applies only to beat-driven compositions (timeline=compiled_beats).
    Fixed-timeline compositions have no beat file and skip cleanly.

    Schema source (single source of truth):
      ~/workspace/crackit/EDITORIAL_BEAT_SCHEMA.json
    Repo-vendored replica (pinned copy so GitHub runners can enforce the
    gate — the canonical file lives outside the repo):
      .github/schemas/EDITORIAL_BEAT_SCHEMA.json
    A sync test (TestBeatSchemaSync) proves the replica is byte-identical
    to the canonical source. The gate reads the replica first, then the
    canonical path as a local-dev fallback.

    FAIL-CLOSED: a missing schema, an unreadable schema, malformed schema
    JSON, or a malformed beat file all produce errors — never a silent skip.
    The artifact's provenance record is printed and attached to the returned
    BeatCheckResult as .provenance.
    """
    errors = BeatCheckResult()
    beat_rel = BEAT_FILES.get(composition)
    if not beat_rel:
        return errors
    beat_path = os.path.join(repo_root, beat_rel)
    prov = beat_artifact_provenance(beat_path, repo_root)
    errors.provenance = prov
    print(f"  Provenance: {prov['file']} [{prov['provenance']}]")
    schema_path, schema_errs = _resolve_beat_schema(repo_root)
    errors.extend(schema_errs)
    schema = None
    if schema_path is not None:
        print(f"  Beat schema: "
              f"{os.path.relpath(schema_path, os.path.abspath(repo_root))}")
        schema, load_errs = _load_beat_schema(schema_path)
        errors.extend(load_errs)
    if not os.path.exists(beat_path):
        errors.append(f"Beat file missing for '{composition}': {beat_rel}")
        return errors
    if schema is None:
        # Fail-closed: the reason is already recorded above.
        return errors
    import json
    try:
        with open(beat_path) as f:
            doc = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        errors.append(f"Beat file {beat_rel} unreadable: {e}")
        return errors
    beats = doc.get("beats", doc if isinstance(doc, list) else [])
    if not isinstance(beats, list) or not beats:
        errors.append(f"Beat file {beat_rel} contains no beats")
        return errors
    print(f"  Beat file: {beat_rel} ({len(beats)} beats)")
    for b in beats:
        bid = b.get("beat_id", "?")
        for field in schema.get("required", []):
            if field not in b or b[field] is None:
                errors.append(f"Beat '{bid}': missing required field '{field}'")
        for field, enum_key in (("semantic_role", "semantic_role_enum"),
                                ("visual_verb", "visual_verb_enum"),
                                ("visual_mode", "visual_mode_enum"),
                                ("duration_class", "duration_class_enum"),
                                ("sfx_policy", "sfx_policy_enum")):
            if b.get(field) not in schema.get(enum_key, []):
                errors.append(
                    f"Beat '{bid}': {field}={b.get(field)!r} not in {enum_key}")
        if b.get("data_presence") and not b.get("data_payload_ref"):
            errors.append(
                f"Beat '{bid}': data_presence=true but no data_payload_ref "
                f"(payload values must never be invented)")
    if not errors:
        print(f"  Beat contract: {len(beats)} beats satisfy the canonical schema")
    return errors


def get_audio_duration(filepath):
    """Get audio duration in seconds via ffprobe."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", filepath],
            capture_output=True, text=True, timeout=30
        )
        return float(result.stdout.strip())
    except Exception as e:
        return None


def check_audio(vo_file, bed_file, with_audio, video_duration_s, repo_root):
    """Verify audio files exist and are long enough."""
    errors = []
    if not with_audio:
        print("  Audio disabled (--with-audio false), skipping audio checks")
        return errors
    
    print(f"  Video duration: {video_duration_s:.1f}s")
    
    for label, fpath in [("VO", vo_file), ("Bed", bed_file)]:
        full_path = os.path.join(repo_root, fpath)
        if not os.path.isfile(full_path):
            errors.append(f"{label} file not found: {fpath}")
            continue
        
        # Check for LFS pointer
        with open(full_path, "rb") as f:
            header = f.read(100)
            if b"version https://git-lfs.github.com" in header:
                errors.append(f"{label} is a Git LFS pointer, not real audio: {fpath}")
                continue
        
        dur = get_audio_duration(full_path)
        if dur is None:
            errors.append(f"{label}: could not read duration: {fpath}")
            continue
        
        print(f"  {label}: {fpath} = {dur:.1f}s")
        
        # VO must cover the video (or be very close)
        # Bed can be shorter (it loops), but warn if very short
        if label == "VO":
            if dur < video_duration_s - 30:  # Allow 30s tolerance
                errors.append(
                    f"VO too short: {dur:.1f}s < video {video_duration_s:.1f}s. "
                    f"The master will have {video_duration_s - dur:.1f}s of silence. "
                    f"Concatenate all VO parts first."
                )
            elif dur < video_duration_s:
                print(f"  WARNING: VO {dur:.1f}s slightly shorter than video "
                      f"{video_duration_s:.1f}s ({video_duration_s - dur:.1f}s gap)")
        elif label == "Bed":
            if dur < 60:
                print(f"  WARNING: Bed very short ({dur:.1f}s), will loop many times")
    
    return errors


def check_workflow_yaml(repo_root):
    """Validate workflow YAML syntax."""
    errors = []
    try:
        import yaml
    except ImportError:
        print("  WARNING: PyYAML not available, skipping YAML check")
        return errors
    
    for wf in ["render-production.yml", "render-production-reassemble.yml"]:
        path = os.path.join(repo_root, ".github", "workflows", wf)
        if not os.path.exists(path):
            continue
        try:
            with open(path) as f:
                yaml.safe_load(f)
            print(f"  YAML OK: {wf}")
        except Exception as e:
            errors.append(f"YAML error in {wf}: {e}")
    
    return errors


def check_push_coverage(repo_root):
    """Verify all workflows are in the push script (regression test).

    Workflows listed in NOT_DEPLOYED are deliberately excluded: they exist
    in the tree as inactive proposals and must NOT be pushed to any branch.
    """
    # P4.4: cleanup-artifacts.yml is an inactive proposal (header-marked
    # "not active"). It must never be deployed, so the coverage gate
    # explicitly exempts it instead of demanding it in the push script.
    NOT_DEPLOYED = {"cleanup-artifacts.yml"}
    errors = []
    wf_dir = os.path.join(repo_root, ".github", "workflows")
    push_script = os.path.expanduser("~/workspace/skills/github/bin/push_p40_branch.py")
    
    if not os.path.exists(push_script):
        print("  WARNING: Push script not found, skipping coverage check")
        return errors
    
    with open(push_script) as f:
        script_content = f.read()
    
    workflows = [f for f in os.listdir(wf_dir) if f.endswith(".yml")]
    for wf in workflows:
        if wf in NOT_DEPLOYED:
            print(f"  Push coverage SKIP (deliberately not deployed): {wf}")
            continue
        path = f".github/workflows/{wf}"
        if path not in script_content:
            errors.append(f"Push script missing workflow: {path} (will not be deployed!)")
        else:
            print(f"  Push coverage OK: {wf}")
    
    return errors


def main():
    parser = argparse.ArgumentParser(description="Pre-dispatch validation")
    parser.add_argument("--composition", required=True)
    parser.add_argument("--start-frame", type=int, required=True)
    parser.add_argument("--end-frame", type=int, required=True)
    parser.add_argument("--chunk-size", type=int, default=600)
    parser.add_argument("--vo-file", default="public/audio/vo_p3.wav")
    parser.add_argument("--bed-file", default="public/audio/bed.mp3")
    parser.add_argument("--with-audio", default="true")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    
    with_audio = args.with_audio.lower() == "true"
    repo_root = os.path.abspath(args.repo_root)
    
    print("=" * 60)
    print("P4.4 Pre-Dispatch Validation")
    print("=" * 60)
    
    all_errors = []
    
    print("\n[1] Frame arithmetic...")
    errs, total_frames = check_frame_math(args.start_frame, args.end_frame, args.chunk_size)
    all_errors.extend(errs)
    
    print("\n[2] Composition...")
    errs = check_composition(args.composition, total_frames, repo_root)
    all_errors.extend(errs)
    
    print("\n[3] Audio files...")
    video_duration_s = total_frames / 30.0  # 30fps
    errs = check_audio(args.vo_file, args.bed_file, with_audio, video_duration_s, repo_root)
    all_errors.extend(errs)
    
    print("\n[4] Workflow YAML...")
    errs = check_workflow_yaml(repo_root)
    all_errors.extend(errs)
    
    print("\n[5] Push script coverage...")
    errs = check_push_coverage(repo_root)
    all_errors.extend(errs)

    print("\n[6] Composition contract (R-2)...")
    errs = check_registry_consistency(repo_root)
    all_errors.extend(errs)
    errs = check_no_duplicate_ids()
    all_errors.extend(errs)
    errs = validate_for_dispatch(args.composition, with_audio)
    all_errors.extend(errs)
    if not errs:
        from composition_contract import get_contract
        c = get_contract(args.composition)
        print(f"  Contract: role={c['role']} brain={c['brain']} "
              f"timeline={c['timeline']} audio={c['audio']} qa={c['qa']}")
        if c.get("exemption"):
            print(f"  Exemption: {c['exemption']}")

    print("\n[7] Beat contract (canonical schema)...")
    errs = check_beat_contract(args.composition, repo_root)
    all_errors.extend(errs)

    print("\n" + "=" * 60)
    if all_errors:
        print(f"FAILED: {len(all_errors)} problem(s) found:")
        for e in all_errors:
            print(f"  ✗ {e}")
        print("\nFix these before dispatching.")
        sys.exit(1)
    else:
        print("PASSED: Safe to dispatch.")
        print(f"  Composition: {args.composition}")
        print(f"  Frames: {args.start_frame}-{args.end_frame} ({total_frames})")
        print(f"  Audio: {'enabled' if with_audio else 'disabled'}")
        sys.exit(0)


if __name__ == "__main__":
    main()
