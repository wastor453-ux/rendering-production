#!/usr/bin/env python3
"""Stable render-generation fingerprint.

P3.12: Separates WHAT is being rendered (generation) from WHICH run rendered
it (execution identity).

- Generation fingerprint: SHA-256 over every input that can affect rendered
  output. Stable across run IDs, attempts, and wall-clock time when all
  rendering inputs are identical.
- Execution identity: run-{id}-attempt-{n}-{sha8}. Unique per dispatch.
  Never part of the generation fingerprint.

Two chunk renders are interchangeable IFF:
  1. Their generation fingerprints match exactly, AND
  2. Their measured environments satisfy the compatibility contract
     (pinned fields equal; see recovery.py), AND
  3. Each chunk's manifest, checksum, frame range, and validation pass.

If any output-affecting input changes, the fingerprint changes and prior
chunks are NOT reused. When equivalence cannot be established, do not reuse.

What is included (every field below affects rendered bytes):
  source_sha, workflow_content_sha, composition, width, height, fps,
  start_frame, end_frame, chunk_size, codec, crf, with_audio,
  input_props_sha256, beats_sha256, events_sha256, payload_sha256 (sorted),
  asset_manifest_sha256, vo_sha256, bed_sha256 (when with_audio),
  package_lock_sha256, node_version, remotion_version, react_version,
  os, expected_chromium_version.

What is EXCLUDED (execution metadata, never affects output):
  run_id, run_attempt, job_identity, label, timestamps, artifact names.

Fail-closed: missing or empty required fields raise ValueError.
"""

import hashlib
import json

# Expected Chromium for the pinned Remotion version (REMOTION_VERSION in the
# workflow). This is what `npx remotion browser ensure` provides for
# remotion 4.0.532. If REMOTION_VERSION changes, update this to the version
# that remotion downloads, then verify against a real run's
# chromium_version.txt before relying on resume.
EXPECTED_CHROMIUM_VERSION = "149.0.7790.0"

# Fields that must be present and non-empty for a valid fingerprint.
REQUIRED_FIELDS = [
    "source_sha",
    "workflow_content_sha",
    "composition",
    "width",
    "height",
    "fps",
    "start_frame",
    "end_frame",
    "chunk_size",
    "codec",
    "crf",
    "with_audio",
    "asset_manifest_sha256",
    "package_lock_sha256",
    "node_version",
    "remotion_version",
    "react_version",
    "os",
    "expected_chromium_version",
]

# Optional content hashes. Included when present; their absence is recorded
# explicitly (null) so that adding them later changes the fingerprint.
OPTIONAL_HASH_FIELDS = [
    "input_props_sha256",
    "beats_sha256",
    "events_sha256",
    "vo_sha256",
    "bed_sha256",
]


def canonical_inputs(inputs: dict) -> dict:
    """Return the canonical fingerprint input dict.

    Raises ValueError on missing/empty required fields (fail closed).
    Normalizes types so that e.g. crf "18" vs 18 do not produce different
    fingerprints for the same setting.
    """
    missing = [f for f in REQUIRED_FIELDS
               if f not in inputs or inputs[f] is None
               or (isinstance(inputs[f], str) and not inputs[f].strip())]
    if missing:
        raise ValueError(
            f"compute_generation_fingerprint: missing required fields: {missing}"
        )
    canon = {}
    for f in REQUIRED_FIELDS:
        v = inputs[f]
        # Normalize: booleans stay booleans; numbers stay numbers;
        # strings are stripped. crf "18" and 18 are the same setting.
        if f == "crf":
            v = str(v).strip()
        elif f == "with_audio":
            v = bool(v)
        elif f in ("width", "height", "fps", "start_frame", "end_frame",
                   "chunk_size"):
            v = int(v)
        elif isinstance(v, str):
            v = v.strip()
        canon[f] = v
    for f in OPTIONAL_HASH_FIELDS:
        v = inputs.get(f)
        canon[f] = v.strip() if isinstance(v, str) and v.strip() else None
    # payload_sha256 is a dict {name: sha}; sort keys for stability.
    payloads = inputs.get("payload_sha256") or {}
    if not isinstance(payloads, dict):
        raise ValueError("compute_generation_fingerprint: payload_sha256 "
                         "must be a dict")
    canon["payload_sha256"] = {k: str(v).strip()
                               for k, v in sorted(payloads.items())}
    return canon


def compute_generation_fingerprint(inputs: dict) -> str:
    """Compute the stable SHA-256 generation fingerprint.

    Deterministic: same inputs -> same fingerprint, regardless of run ID,
    attempt, timestamp, or label.
    """
    canon = canonical_inputs(inputs)
    blob = json.dumps(canon, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def fingerprint_inputs_from_job_manifest(job_manifest: dict) -> dict:
    """Reconstruct fingerprint inputs from a job manifest.

    Used by recovery to recompute (not just trust) the prior run's
    fingerprint. Raises ValueError if the manifest lacks required data.
    """
    gh = job_manifest.get("github", {})
    env = job_manifest.get("expected_environment", {})
    inp = job_manifest.get("inputs", {})
    return {
        "source_sha": gh.get("source_sha"),
        "workflow_content_sha": gh.get("workflow_content_sha"),
        "composition": inp.get("composition"),
        "width": inp.get("width"),
        "height": inp.get("height"),
        "fps": inp.get("fps"),
        "start_frame": inp.get("start_frame"),
        "end_frame": inp.get("end_frame"),
        "chunk_size": inp.get("chunk_size"),
        "codec": inp.get("codec"),
        "crf": inp.get("crf"),
        "with_audio": inp.get("with_audio"),
        "input_props_sha256": inp.get("input_props_sha256"),
        "beats_sha256": inp.get("beats_sha256"),
        "events_sha256": inp.get("events_sha256"),
        "payload_sha256": inp.get("payload_sha256"),
        "asset_manifest_sha256": inp.get("asset_manifest_sha256"),
        "vo_sha256": inp.get("vo_sha256"),
        "bed_sha256": inp.get("bed_sha256"),
        "package_lock_sha256": env.get("package_lock_sha256"),
        "node_version": env.get("node_version"),
        "remotion_version": env.get("remotion_version"),
        "react_version": env.get("react_version"),
        "os": env.get("os"),
        # Prior manifests pre-P3.12 lack this; fall back to the expected
        # value so old runs get a defined (non-matching unless truly equal)
        # fingerprint rather than an exception. Recovery still requires the
        # prior run's MEASURED chromium versions to match.
        "expected_chromium_version": inp.get(
            "expected_chromium_version", EXPECTED_CHROMIUM_VERSION),
    }


def describe_fingerprint_diff(a_inputs: dict, b_inputs: dict) -> list:
    """Return human-readable list of differing fingerprint fields.

    Used in error messages when resume validation fails, so the operator
    knows exactly what changed.
    """
    try:
        ca = canonical_inputs(a_inputs)
    except ValueError as e:
        return [f"current inputs invalid: {e}"]
    try:
        cb = canonical_inputs(b_inputs)
    except ValueError as e:
        return [f"prior inputs invalid: {e}"]
    diffs = []
    for k in sorted(set(ca) | set(cb)):
        va, vb = ca.get(k), cb.get(k)
        if va != vb:
            sa = str(va)
            sb = str(vb)
            # Truncate hashes for readability
            if len(sa) > 16 and len(sb) > 16:
                sa, sb = sa[:12] + "...", sb[:12] + "..."
            diffs.append(f"{k}: current={sa} prior={sb}")
    return diffs
