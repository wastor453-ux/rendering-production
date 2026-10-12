#!/usr/bin/env python3
"""
verify_provenance.py — Verify timeline was generated from current inputs.

Prevents stale timelines from passing validation. Checks that the timeline's
provenance hashes match the current alignment and semantic patterns files.

Usage:
    python3 .github/scripts/verify_provenance.py

Reads:
    src/videos/_active/manifest.json (for video_id)
    src/videos/_active/timeline.json (the timeline to verify)
    src/videos/{video_id}/data/alignment.json
    src/videos/{video_id}/data/semantic_patterns.json

Exits 0 on success, 1 on failure (with FATAL message to stderr).
"""
import hashlib
import json
import sys


def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    try:
        with open("src/videos/_active/manifest.json") as f:
            video_id = json.load(f)["videoId"]
    except FileNotFoundError:
        print("FATAL: Manifest not found: src/videos/_active/manifest.json", file=sys.stderr)
        print("  (Prepare event-driven manifest step did not run or failed)", file=sys.stderr)
        sys.exit(1)
    except (json.JSONDecodeError, KeyError) as e:
        print(f"FATAL: Invalid manifest: {e}", file=sys.stderr)
        sys.exit(1)

    timeline_path = "src/videos/_active/timeline.json"
    alignment_path = f"src/videos/{video_id}/data/alignment.json"
    patterns_path = f"src/videos/{video_id}/data/semantic_patterns.json"

    for p in [timeline_path, alignment_path, patterns_path]:
        try:
            with open(p, "rb") as f:
                pass
        except FileNotFoundError:
            print(f"FATAL: Required file not found: {p}", file=sys.stderr)
            sys.exit(1)

    with open(timeline_path) as f:
        tl = json.load(f)

    prov = tl.get("provenance", {})
    if not prov:
        print("FATAL: Timeline has no provenance info (stale format)", file=sys.stderr)
        sys.exit(1)

    current_align = file_hash(alignment_path)
    current_pat = file_hash(patterns_path)

    if prov.get("alignment_sha256") != current_align:
        print("FATAL: Timeline alignment hash mismatch (stale timeline)", file=sys.stderr)
        print(f"  Expected: {current_align[:16]}...", file=sys.stderr)
        print(f"  Found: {prov.get('alignment_sha256', 'none')[:16]}...", file=sys.stderr)
        sys.exit(1)

    if prov.get("patterns_sha256") != current_pat:
        print("FATAL: Timeline patterns hash mismatch (stale timeline)", file=sys.stderr)
        sys.exit(1)

    print("✅ Timeline provenance verified (fresh)")


if __name__ == "__main__":
    main()
