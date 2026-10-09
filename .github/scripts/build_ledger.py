#!/usr/bin/env python3
"""Chunk ledger builder (2026-10-10, Hamza's rule).

Aggregates per-chunk manifests into ONE durable ledger per job:
  chunk-ledger-<job_identity>.json

The ledger is the ground truth for "which chunks are safely rendered."
- Assembly (and reassembly) reads the ledger BEFORE concatenating.
  If the ledger is not COMPLETE, assembly fails with the exact missing
  chunk IDs — it never guesses, never silently skips, never re-renders.
- Resume reads the ledger to know which chunks are reusable without
  re-downloading and re-validating every artifact from scratch.

Ledger entry per chunk:
  chunk_id, frame_range, status (rendered_ok | reused_ok | failed | missing),
  output_sha256, provenance (origin run), validation summary.

Usage:
  python3 build_ledger.py --job-manifest job.json --chunks-dir /tmp/chunks \
      --out chunk-ledger.json
"""

import argparse
import hashlib
import json
import os
import sys


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()


def build_ledger(job_manifest, chunk_manifests):
    """Build the ledger dict from a job manifest and {chunk_id: manifest}."""
    expected = job_manifest.get("chunks", {}).get("count")
    if expected is None:
        # Fall back to explicit chunk list if present.
        expected_ids = job_manifest.get("chunks", {}).get("ids", [])
        expected = len(expected_ids)
    else:
        expected_ids = list(range(expected))

    entries = []
    for cid in expected_ids:
        cm = chunk_manifests.get(cid) or chunk_manifests.get(str(cid))
        if cm is None:
            entries.append({
                "chunk_id": cid, "status": "missing",
                "frame_range": None, "output_sha256": None,
                "provenance": None, "note": "no manifest found",
            })
            continue
        validation = cm.get("validation") or {}
        ok = validation.get("passed", False)
        provenance = cm.get("provenance", {})
        status = ("reused_ok" if provenance.get("reused") else "rendered_ok") if ok else "failed"
        entries.append({
            "chunk_id": cid,
            "status": status,
            "frame_range": cm.get("frame_range"),
            "output_sha256": cm.get("output_sha256"),
            "output_bytes": cm.get("output_bytes"),
            "provenance": {
                "reused": provenance.get("reused", False),
                "origin_run_id": provenance.get("origin_run_id"),
                "origin_job_identity": provenance.get("origin_job_identity"),
            },
            "generation_fingerprint": cm.get("generation_fingerprint"),
            "attempt": cm.get("attempt", 1),
        })

    ok_count = sum(1 for e in entries if e["status"] in ("rendered_ok", "reused_ok"))
    ledger = {
        "kind": "chunk-ledger",
        "job_identity": job_manifest.get("job_identity"),
        "expected_chunks": expected,
        "ok_chunks": ok_count,
        "complete": ok_count == expected and expected > 0,
        "entries": entries,
    }
    return ledger


def main(argv):
    p = argparse.ArgumentParser(description="Build chunk ledger from manifests")
    p.add_argument("--job-manifest", required=True)
    p.add_argument("--chunks-dir", required=True,
                   help="Directory containing chunk_manifest.json files (one per chunk subdir or flat)")
    p.add_argument("--out", required=True)
    args = p.parse_args(argv)

    job = json.load(open(args.job_manifest))

    # Collect chunk manifests: accept <dir>/chunk-<id>/chunk_manifest.json
    # or <dir>/chunk_manifest_<id>.json or flat chunk_manifest.json files.
    chunk_manifests = {}
    for root, _dirs, files in os.walk(args.chunks_dir):
        for fn in files:
            if fn == "chunk_manifest.json" or (fn.startswith("chunk_manifest") and fn.endswith(".json")):
                try:
                    cm = json.load(open(os.path.join(root, fn)))
                    cid = cm.get("chunk_id")
                    if cid is not None:
                        chunk_manifests[cid] = cm
                except (json.JSONDecodeError, OSError):
                    continue

    ledger = build_ledger(job, chunk_manifests)
    with open(args.out, "w") as f:
        json.dump(ledger, f, indent=2)

    print(f"Ledger: {ledger['ok_chunks']}/{ledger['expected_chunks']} chunks OK "
          f"-> {'COMPLETE' if ledger['complete'] else 'INCOMPLETE'}")
    if not ledger["complete"]:
        missing = [e["chunk_id"] for e in ledger["entries"] if e["status"] not in ("rendered_ok", "reused_ok")]
        print(f"Missing/failed chunks: {missing}")
        sys.exit(3)
    # Also write a sha for the ledger itself (tamper-evidence).
    print(f"ledger_sha256={sha256_file(args.out)}")


if __name__ == "__main__":
    main(sys.argv[1:])
