#!/usr/bin/env python3
"""
run_pipeline.py — Canonical production pipeline entry point.

Orchestrates every mandatory stage for a video:
    1. Validate inputs (VO, script, patterns exist)
    2. Align voiceover (faster-whisper → word timestamps)
    3. Generate event timeline (alignment + patterns → events)
    4. Validate event timeline (non-empty, valid types, timing)
    5. Report readiness for render

This is the ONLY approved way to process a video through the pipeline.
Do not run stages manually. Do not skip stages.

Usage:
    python3 tools/run_pipeline.py --video <video-id>
    python3 tools/run_pipeline.py --video credit-score --skip-align  # reuse cached alignment

Each video's data lives in src/videos/{video-id}/data/:
    - vo.wav (or audio/vo.wav): the video's voiceover
    - semantic_patterns.json: the video's phrase→visual mappings
    - alignment.json: generated word timestamps (cached)
    - event_timeline.json: generated visual events

FAIL-CLOSED: Any stage failure stops the pipeline with exit 1.
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent
TOOLS_DIR = REPO_ROOT / "tools"


def sha256_file(path):
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()
TOOLS_DIR = REPO_ROOT / "tools"


def run_stage(name, cmd, cwd=None):
    """Run a pipeline stage. Fail-closed on error."""
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"STAGE: {name}", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)
    
    result = subprocess.run(cmd, cwd=cwd or REPO_ROOT, capture_output=False)
    if result.returncode != 0:
        print(f"\n❌ STAGE FAILED: {name} (exit {result.returncode})", file=sys.stderr)
        print(f"   Pipeline halted. Fix the issue and re-run.", file=sys.stderr)
        sys.exit(1)
    print(f"✅ Stage complete: {name}", file=sys.stderr)


def validate_inputs(video_dir):
    """Stage 1: Validate that all required inputs exist."""
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"STAGE: Validate inputs", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)
    
    errors = []
    
    # Check VO file (in data/ or audio/)
    vo_paths = [
        video_dir / "data" / "vo.wav",
        video_dir / "audio" / "vo.wav",
    ]
    vo_file = next((p for p in vo_paths if p.exists()), None)
    if not vo_file:
        errors.append(f"Missing VO: checked {[str(p) for p in vo_paths]}")
    
    # Check semantic patterns
    patterns_file = video_dir / "data" / "semantic_patterns.json"
    if not patterns_file.exists():
        errors.append(f"Missing semantic patterns: {patterns_file}")
    else:
        try:
            with open(patterns_file) as f:
                data = json.load(f)
            patterns = data.get("patterns", data) if isinstance(data, dict) else data
            if not patterns:
                errors.append(f"Empty semantic patterns: {patterns_file}")
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in {patterns_file}: {e}")
    
    if errors:
        print(f"❌ INPUT VALIDATION FAILED:", file=sys.stderr)
        for e in errors:
            print(f"   • {e}", file=sys.stderr)
        sys.exit(1)
    
    print(f"✅ Inputs valid:", file=sys.stderr)
    print(f"   VO: {vo_file}", file=sys.stderr)
    print(f"   Patterns: {patterns_file}", file=sys.stderr)
    return vo_file, patterns_file


def main():
    parser = argparse.ArgumentParser(description="Canonical production pipeline")
    parser.add_argument("--video", required=True, help="Video ID (directory under src/videos/)")
    parser.add_argument("--skip-align", action="store_true",
                        help="Reuse cached alignment.json instead of re-aligning")
    parser.add_argument("--venv", default=sys.executable,
                        help="Python with faster-whisper (default: same interpreter running the pipeline). "
                             "F-04 fix: was .venv/bin/python which the workflow never creates.")
    args = parser.parse_args()
    
    video_id = args.video
    video_dir = REPO_ROOT / "src" / "videos" / video_id
    data_dir = video_dir / "data"
    
    if not video_dir.exists():
        print(f"FATAL: Video directory not found: {video_dir}", file=sys.stderr)
        sys.exit(1)
    
    print(f"🎬 Pipeline starting for video: {video_id}", file=sys.stderr)
    print(f"   Directory: {video_dir}", file=sys.stderr)
    
    # Stage 1: Validate inputs
    vo_file, patterns_file = validate_inputs(video_dir)
    
    # Stage 2: Align voiceover
    alignment_file = data_dir / "alignment.json"
    if args.skip_align and alignment_file.exists():
        print(f"\n⏭️  Skipping alignment (using cached {alignment_file})", file=sys.stderr)
        # Validate cached alignment provenance: VO hash must match
        with open(alignment_file) as f:
            cached = json.load(f)
        cached_hash = cached.get("source_sha256", "")  # align_vo.py writes source_sha256
        current_hash = sha256_file(vo_file)
        if cached_hash != current_hash:
            print(f"❌ FATAL: Cached alignment source hash mismatch", file=sys.stderr)
            print(f"   Cached: {cached_hash[:16]}...", file=sys.stderr)
            print(f"   Current VO: {current_hash[:16]}...", file=sys.stderr)
            print(f"   The VO file changed. Re-run without --skip-align.", file=sys.stderr)
            sys.exit(1)
        print(f"   Cached: {cached.get('word_count', '?')} words, hash verified ✅", file=sys.stderr)
    else:
        # F-04: Fail closed if the alignment interpreter does not exist.
        venv_py = Path(args.venv)
        if not venv_py.exists():
            print(f"❌ FATAL: Alignment Python not found: {args.venv}", file=sys.stderr)
            print(f"   Install faster-whisper for this interpreter or pass --venv.", file=sys.stderr)
            sys.exit(1)
        run_stage(
            "Align voiceover (faster-whisper)",
            [args.venv, str(TOOLS_DIR / "align_vo.py"),
             str(vo_file), str(alignment_file)]
        )
    
    # Stage 3: Generate event timeline
    events_file = data_dir / "event_timeline.json"
    run_stage(
        "Generate event timeline",
        ["python3", str(TOOLS_DIR / "generate_event_timeline.py"),
         str(alignment_file), str(patterns_file), str(events_file)]
    )
    
    # Stage 4: Validate event timeline
    run_stage(
        "Validate event timeline (quality gates)",
        ["python3", str(TOOLS_DIR / "validate_timeline.py"), str(events_file)]
    )
    
    # Stage 5: Validate typography
    run_stage(
        "Validate typography (readability gates)",
        ["python3", str(TOOLS_DIR / "validate_typography.py"), "--strict"]
    )
    
    # Summary
    with open(events_file) as f:
        event_count = len(json.load(f).get("events", []))
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"✅ PIPELINE COMPLETE for {video_id}", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)
    print(f"   Events: {event_count}", file=sys.stderr)
    print(f"   Timeline: {events_file}", file=sys.stderr)
    print(f"   Ready for render.", file=sys.stderr)


if __name__ == "__main__":
    main()
