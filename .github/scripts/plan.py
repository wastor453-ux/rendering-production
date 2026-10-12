#!/usr/bin/env python3
"""
Plan job: generate canonical job identity, chunk matrix, job manifest,
and asset manifest.

Invoked by the workflow's plan job. All inputs come from environment
variables (never from shell interpolation). Exits non-zero with a useful
message on any invalid input or missing file — never a bare KeyError.

Environment variables (all required unless noted):
  JOB_IDENTITY, GITHUB_RUN_ID, GITHUB_RUN_ATTEMPT, GITHUB_SHA,
  COMPOSITION, START_FRAME, END_FRAME, CHUNK_SIZE, CRF, WITH_AUDIO,
  VO_FILE, BED_FILE, LABEL (optional), OUTPUT_DIR (default /tmp/job),
  REPO_ROOT (default .)

Exit codes:
  0 - success, manifests written
  1 - invalid input
  2 - missing required file
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from manifest import build_job_manifest, build_asset_manifest, sha256_file
from composition_contract import get_contract, get_total_frames


def fatal(msg: str, code: int = 1) -> None:
    print(f"FATAL: {msg}", file=sys.stderr)
    sys.exit(code)


def get_env(name: str, required: bool = True, default: str = "") -> str:
    val = os.environ.get(name, default)
    if required and not val:
        fatal(f"missing required environment variable: {name}")
    return val


def validate_int(name: str, value: str, min_val: int = None,
                 max_val: int = None) -> int:
    try:
        n = int(value)
    except (TypeError, ValueError):
        fatal(f"{name} must be an integer, got {value!r}")
    if min_val is not None and n < min_val:
        fatal(f"{name} must be >= {min_val}, got {n}")
    if max_val is not None and n > max_val:
        fatal(f"{name} must be <= {max_val}, got {n}")
    return n


def validate_composition(value: str) -> str:
    # Allowlist format: alphanumeric + underscore, must start with letter
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", value):
        fatal(f"composition has invalid format: {value!r} "
              f"(must match [A-Za-z][A-Za-z0-9_]*)")
    # R-2: the composition must be registered in the universal contract.
    # An unregistered id previously passed this check and died later inside
    # the render matrix; fail closed here instead.
    contract = get_contract(value)
    if contract is None:
        fatal(f"composition {value!r} is not registered in the composition "
              f"contract (.github/scripts/composition_contract.py)")
    return value


def validate_audio_mode(value: str) -> bool:
    """Strictly validate the audio mode.

    Accepts exactly 'true' or 'false' (case-insensitive, stripped).
    Rejects all other values — no silent fallback to false.

    Returns True for audio enabled, False for disabled.
    """
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    fatal(f"WITH_AUDIO must be 'true' or 'false', got {value!r}")


def validate_bool_flag(name: str, value: str) -> bool:
    """Strictly validate a boolean workflow flag (Q2).

    Same semantics as validate_audio_mode but with the flag's name in
    the error message. Used for WITH_SFX_MIX, SFX_CHAIN_TEST,
    INSTALL_VERIFY, REASSEMBLE_BYPASS_FINGERPRINT.
    """
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    fatal(f"{name} must be 'true' or 'false', got {value!r}")


def validate_vo_offset(value: str) -> float:
    """Q3 (2026-10-11): validate vo_offset_seconds.

    Must be a finite, non-negative number. Returns the float value.
    The offset is the position in vo_file where the rendered range's
    audio begins; the muxer seeks to it (not to start_frame/30).
    """
    import math
    try:
        offset = float(value)
    except (TypeError, ValueError):
        fatal(f"VO_OFFSET_SECONDS must be a number, got {value!r}")
    if not math.isfinite(offset):
        fatal(f"VO_OFFSET_SECONDS must be finite, got {value!r}")
    if offset < 0:
        fatal(f"VO_OFFSET_SECONDS must be >= 0, got {offset}")
    return offset


def validate_crf(value: str) -> str:
    try:
        n = int(value)
    except (TypeError, ValueError):
        fatal(f"crf must be an integer, got {value!r}")
    if not 0 <= n <= 51:
        fatal(f"crf must be 0-51 (H.264 valid range), got {n}")
    return str(n)


def validate_frame_range(composition: str, start: int, end: int, video_id: str = "") -> int:
    """Q1 (2026-10-11): fail early on out-of-range frames.

    Resolves the composition's authoritative total frame count from the
    contract registry (verified against canonical TSX sources by
    tests/test_composition_frames.py). Frames are 0-indexed: valid range
    is [0, total_frames).

    Returns total_frames on success. Calls fatal() (exits non-zero) when:
      - the composition has no valid total_frames (fail closed)
      - start or end is outside [0, total_frames)
      - end < start
    """
    total_frames = get_total_frames(composition, video_id=video_id)
    if total_frames is None:
        fatal(f"composition {composition!r} has no valid total_frames in the "
              f"contract registry; cannot validate frame range")
    if end < start:
        fatal(f"END_FRAME ({end}) < START_FRAME ({start})")
    if start >= total_frames:
        fatal(f"START_FRAME ({start}) is outside composition {composition!r} "
              f"(valid range 0-{total_frames - 1}, total {total_frames} frames)")
    if end >= total_frames:
        fatal(f"END_FRAME ({end}) is outside composition {composition!r} "
              f"(valid range 0-{total_frames - 1}, total {total_frames} frames)")
    return total_frames


def validate_flag_combinations(with_sfx_mix: bool, sfx_chain_test: bool,
                               install_verify: bool,
                               reassemble_bypass: bool) -> None:
    """Q2 (2026-10-11): reject unsafe workflow flag combinations.

    Fail-closed rules for incompatible inputs. Each rule documents WHY the
    combination is unsafe. Calls fatal() (exits non-zero) on violation.

    Rules:
      1. reassemble_bypass + with_sfx_mix: REJECTED. Reassembly mode
         recovers a master from existing chunks with the generation
         fingerprint check bypassed. Running sfx-mix on top would produce
         a master whose SFX layer was mixed against an unverified
         generation — the mix inputs (timing, chunk boundaries) cannot be
         trusted. If a recovered master needs SFX, re-run the full
         pipeline with with_sfx_mix=true and without the bypass.
    """
    if reassemble_bypass and with_sfx_mix:
        fatal("reassemble_bypass_fingerprint=true cannot be combined with "
              "with_sfx_mix=true: sfx-mix on a reassembled master with "
              "bypassed fingerprint verification would mix against an "
              "unverified generation. Re-run the full pipeline instead.")
    # NOTE: sfx_chain_test and install_verify are mutually exclusive by
    # workflow job conditions (install-verify wins deterministically);
    # not rejected here because neither path renders or publishes.


def validate_repo_path(name: str, value: str, repo_root: str) -> str:
    # Canonical path policy (same as manifest.py::canonical_repo_path).
    # Rejects absolute paths, traversal, symlinks, non-strings.
    # Returns the canonical repo-relative path.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from manifest import canonical_repo_path
    try:
        canonical = canonical_repo_path(repo_root, value)
    except ValueError as e:
        fatal(f"{name}: {e}")
    full = os.path.join(repo_root, canonical)
    if not os.path.isfile(full):
        fatal(f"{name} file not found: {value!r}", code=2)
    return canonical


def sh(cmd: str) -> str:
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0:
        fatal(f"command failed: {cmd}: {r.stderr.strip()[:200]}")
    return r.stdout.strip()


def main() -> int:
    repo_root = os.environ.get("REPO_ROOT", ".")
    output_dir = os.environ.get("OUTPUT_DIR", "/tmp/job")

    # --- Validate all inputs before doing expensive work ---
    job_identity = get_env("JOB_IDENTITY")
    run_id = get_env("GITHUB_RUN_ID")
    attempt = get_env("GITHUB_RUN_ATTEMPT")
    source_sha = get_env("GITHUB_SHA")
    composition = validate_composition(get_env("COMPOSITION"))
    # video_id is required for EventDriven (the generic pipeline needs to know
    # which video's data to load). Fail closed if missing.
    video_id_early = os.environ.get("VIDEO_ID", "").strip()
    if composition == "EventDriven" and not video_id_early:
        fatal("VIDEO_ID is required when composition=EventDriven")
    start = validate_int("START_FRAME", get_env("START_FRAME"), min_val=0)
    end = validate_int("END_FRAME", get_env("END_FRAME"), min_val=0)
    chunk_size = validate_int("CHUNK_SIZE", get_env("CHUNK_SIZE"), min_val=1)
    max_parallel = validate_int("MAX_PARALLEL",
                                os.environ.get("MAX_PARALLEL", "20"),
                                min_val=1, max_val=50)
    crf = validate_crf(get_env("CRF"))
    with_audio = validate_audio_mode(get_env("WITH_AUDIO"))
    label = os.environ.get("LABEL", "")
    # Label is display-only; reject control characters
    if any(ord(c) < 32 for c in label):
        fatal("LABEL contains control characters")

    # Q2: workflow mode flags (all optional, default false).
    with_sfx_mix = validate_bool_flag("WITH_SFX_MIX",
                                      os.environ.get("WITH_SFX_MIX", "false"))
    sfx_chain_test = validate_bool_flag("SFX_CHAIN_TEST",
                                        os.environ.get("SFX_CHAIN_TEST", "false"))
    install_verify = validate_bool_flag("INSTALL_VERIFY",
                                        os.environ.get("INSTALL_VERIFY", "false"))
    reassemble_bypass = validate_bool_flag(
        "REASSEMBLE_BYPASS_FINGERPRINT",
        os.environ.get("REASSEMBLE_BYPASS_FINGERPRINT", "false"))
    validate_flag_combinations(with_sfx_mix, sfx_chain_test,
                               install_verify, reassemble_bypass)

    # Q3: VO offset (optional, default 0). Validated here so the muxer and
    # audio guard share one deterministic alignment contract.
    vo_offset = validate_vo_offset(os.environ.get("VO_OFFSET_SECONDS", "0"))

    # Q1: frame range validated against the composition's authoritative total.
    # (validate_frame_range also rejects end < start.)
    # F-08: EventDriven duration is dynamic; pass video_id for timeline lookup.
    video_id = os.environ.get("VIDEO_ID", "")
    total_frames = validate_frame_range(composition, start, end, video_id=video_id)

    if chunk_size > (end - start + 1):
        print(f"WARNING: CHUNK_SIZE ({chunk_size}) > total frames "
              f"({end - start + 1}); single chunk", file=sys.stderr)

    # --- Asset paths (validated, repo-relative) ---
    asset_paths = []
    vo = bed = None
    if with_audio:
        vo = validate_repo_path("VO_FILE", get_env("VO_FILE"), repo_root)
        bed = validate_repo_path("BED_FILE", get_env("BED_FILE"), repo_root)
        asset_paths = [vo, bed]

    # --- Required input files ---
    def require_file(rel: str) -> str:
        full = os.path.join(repo_root, rel)
        if not os.path.isfile(full):
            fatal(f"required input file not found: {rel}", code=2)
        return sha256_file(full)

    package_lock_sha = require_file("package-lock.json")
    
    # --- Composition-specific input files ---
    # Resolve required inputs from the selected composition's contract.
    # EventDriven uses event_timeline (not beats). Beat-based compositions
    # use their own beat_timeline.json. Never hardcode a specific video.
    beats_sha = None
    events_sha = None
    payload_shas = {}
    
    contract = get_contract(composition)
    timeline_kind = contract.get("timeline") if contract else None
    
    if timeline_kind == "event_timeline":
        # EventDriven: event timeline is generated by run_pipeline.py,
        # validated separately. No beat files required.
        pass
    else:
        # Beat-based composition: resolve beat file from BEAT_FILES
        # (validate_dispatch.py) or contract.
        try:
            import sys
            sys.path.insert(0, os.path.join(repo_root, ".github/scripts"))
            from validate_dispatch import BEAT_FILES
            beat_file = BEAT_FILES.get(composition)
            if beat_file:
                beats_sha = require_file(beat_file)
                # Events file is alongside beat file
                events_file = beat_file.replace("beat_timeline.json", "events.json")
                if os.path.isfile(os.path.join(repo_root, events_file)):
                    events_sha = require_file(events_file)
                # Payload checksums
                payload_dir = os.path.join(repo_root, os.path.dirname(beat_file), "payloads")
                if os.path.isdir(payload_dir):
                    for f in sorted(os.listdir(payload_dir)):
                        if f.endswith(".json"):
                            payload_shas[f] = sha256_file(os.path.join(payload_dir, f))
        except ImportError:
            pass

    # --- Asset manifest (genuine SHA-256) ---
    try:
        old_cwd = os.getcwd()
        os.chdir(repo_root)
        try:
            asset_m = build_asset_manifest(asset_paths)
        finally:
            os.chdir(old_cwd)
    except (FileNotFoundError, ValueError) as e:
        fatal(f"asset manifest: {e}", code=2)
    asset_sha = asset_m["manifest_sha256"]

    # --- Measure real versions (no placeholders) ---
    real_node = sh("node --version")
    real_npm = sh("npm --version")
    with open(os.path.join(repo_root, "package-lock.json")) as f:
        lock = json.load(f)
    pkgs = lock.get("packages", {})
    real_remotion = pkgs.get("node_modules/remotion", {}).get("version")
    real_react = pkgs.get("node_modules/react", {}).get("version")
    if not real_remotion:
        fatal("remotion version not found in package-lock.json", code=2)
    if not real_react:
        fatal("react version not found in package-lock.json", code=2)
    real_os = sh("lsb_release -ds")

    # --- Workflow content hash (distinguish from source commit SHA) ---
    # source_sha = the git commit; workflow_content_sha = hash of the
    # workflow file itself (detects uncommitted or mismatched workflow)
    workflow_path = ".github/workflows/render-production.yml"
    workflow_content_sha = sha256_file(os.path.join(repo_root, workflow_path))

    # --- Build job manifest ---
    # P3.12: extract per-file audio hashes for the generation fingerprint.
    vo_sha = asset_m["files"].get(vo) if with_audio else None
    bed_sha = asset_m["files"].get(bed) if with_audio else None
    m = build_job_manifest(
        job_identity=job_identity,
        run_id=run_id,
        attempt=attempt,
        source_sha=source_sha,
        workflow_path=workflow_path,
        workflow_sha=source_sha,
        workflow_content_sha=workflow_content_sha,
        node_version=real_node,
        npm_version=real_npm,
        remotion_version=real_remotion,
        react_version=real_react,
        os_info=real_os,
        runner_image="ubuntu-24.04",
        package_lock_sha=package_lock_sha,
        composition=composition,
        input_props_sha="none",
        beats_sha=beats_sha,
        events_sha=events_sha,
        payload_shas=payload_shas,
        asset_manifest_sha=asset_sha,
        width=1920, height=1080, fps=30,
        start_frame=start, end_frame=end, chunk_size=chunk_size,
        codec="h264", crf=crf,
        with_audio=with_audio,
        label=label,
        vo_sha=vo_sha,
        bed_sha=bed_sha,
        vo_offset_seconds=vo_offset,
    )

    # --- Write outputs ---
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "job_manifest.json"), "w") as f:
        json.dump(m, f, indent=2)
    with open(os.path.join(output_dir, "asset_manifest.json"), "w") as f:
        json.dump(asset_m, f, indent=2)

    print(f"Job manifest: {job_identity} ({m['plan']['chunk_count']} chunks)")
    print(f"Asset manifest SHA: {asset_sha}")
    print(f"Workflow content SHA: {workflow_content_sha[:16]}...")
    print(f"Generation fingerprint: {m['generation_fingerprint'][:16]}...")
    # P3.12: expose the generation fingerprint as a job output for render jobs.
    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a") as f:
            f.write(f"generation_fingerprint={m['generation_fingerprint']}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
