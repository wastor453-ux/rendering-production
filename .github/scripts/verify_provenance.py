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
    with open("src/videos/_active/manifest.json") as f:
        video_id = json.load(f)["videoId"]

    timeline_path = "src/videos/_active/timeline.json"
    alignment_path = f"src/videos/{video_id}/data/alignment.json"
    patterns_path = f"src/videos/{video_id}/data/semantic_patterns.json"

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
