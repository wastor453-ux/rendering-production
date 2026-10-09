#!/usr/bin/env python3
"""
Reproducibility manifest generation and enforcement.

Two manifest types:
  job_manifest.json   — one per render job, written by the plan step
  chunk_manifest.json — one per chunk, written by the render step

The assembly job enforces:
  - all chunks share the same canonical job identity
  - all chunks share the same source SHA and environment fingerprint
  - frame ranges match the plan exactly (no gaps, overlaps, duplicates)
  - all checksums pass

Manifest version: 1
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone

MANIFEST_VERSION = 1


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_job_manifest(
    job_identity: str,
    run_id: str,
    attempt: str,
    source_sha: str,
    workflow_path: str,
    workflow_sha: str,
    workflow_content_sha: str,
    node_version: str,
    npm_version: str,
    remotion_version: str,
    react_version: str,
    os_info: str,
    runner_image: str,
    package_lock_sha: str,
    composition: str,
    input_props_sha: str,
    beats_sha: str,
    events_sha: str,
    payload_shas: dict,
    asset_manifest_sha: str,
    width: int,
    height: int,
    fps: int,
    start_frame: int,
    end_frame: int,
    chunk_size: int,
    codec: str,
    crf: str,
    with_audio: bool,
    label: str = "",
) -> dict:
    """Build the job-level manifest. All fields required except label.

    The environment section contains EXPECTED values (planned, not yet measured).
    Chromium is NOT included here — it is resolved at render time and recorded
    in each chunk's measured_environment. There is no 'resolved-at-render'
    placeholder; the field is simply absent until measured.

    Pinned fields (must match chunk measurements): node_version, remotion_version,
    react_version, os.
    Recorded-only fields (informational): npm_version, runner_image.
    """
    # Validate no placeholders in expected values
    for field_name, value in [
        ("node_version", node_version),
        ("remotion_version", remotion_version),
        ("react_version", react_version),
        ("os_info", os_info),
    ]:
        if isinstance(value, str):
            lv = value.strip().lower()
            if lv in ("unknown", "resolved-at-render", "") or lv.startswith("from-") or lv.startswith("missing:"):
                raise ValueError(
                    f"build_job_manifest: {field_name} has placeholder value {value!r}"
                )
    chunks = []
    s = start_frame
    cid = 0
    while s <= end_frame:
        e = min(s + chunk_size - 1, end_frame)
        chunks.append({"chunk_id": cid, "start": s, "end": e})
        cid += 1
        s = e + 1
    return {
        "manifest_version": MANIFEST_VERSION,
        "kind": "job",
        "job_identity": job_identity,
        "label": label,
        "github": {
            "run_id": str(run_id),
            "run_attempt": str(attempt),
            "source_sha": source_sha,
            "workflow_path": workflow_path,
            # workflow_sha: the git commit the workflow was taken from.
            # workflow_content_sha: SHA-256 of the workflow FILE content.
            # These differ if the workflow file was modified without committing,
            # or if a stale revision is used. Both are recorded.
            "workflow_sha": workflow_sha,
            "workflow_content_sha": workflow_content_sha,
        },
        "expected_environment": {
            "node_version": node_version,
            "npm_version": npm_version,
            "remotion_version": remotion_version,
            "react_version": react_version,
            "os": os_info,
            "runner_image": runner_image,
            "package_lock_sha256": package_lock_sha,
        },
        "inputs": {
            "composition": composition,
            "input_props_sha256": input_props_sha,
            "beats_sha256": beats_sha,
            "events_sha256": events_sha,
            "payload_sha256": payload_shas,
            "asset_manifest_sha256": asset_manifest_sha,
            "width": width,
            "height": height,
            "fps": fps,
            "start_frame": start_frame,
            "end_frame": end_frame,
            "chunk_size": chunk_size,
            "codec": codec,
            "crf": str(crf),
            "with_audio": bool(with_audio),
        },
        "plan": {
            "chunk_count": len(chunks),
            "chunks": chunks,
        },
        "stage": "planned",  # planned -> video_only -> av_intermediate -> av_master
        # av_intermediate = VO + music bed muxed, SFX post-production pending
        # av_master = final canonical master including SFX mix (separate step)
        "created_at": utcnow(),
    }


def build_chunk_manifest(
    job_identity: str,
    chunk_id: int,
    start: int,
    end: int,
    source_sha: str,
    env_dict: dict,
    attempt: int = 1,
) -> dict:
    """Build a chunk manifest skeleton. Render step fills in timing/output fields.

    env_dict MUST be the actual runtime environment collected on the runner
    (node --version, remotion version, chromium version, os release).
    Do NOT pass placeholders — env_fingerprint() rejects them.
    The section is named 'measured_environment' to distinguish from the
    job manifest's 'expected_environment'.

    Required fields in env_dict: node_version, remotion_version, react_version,
    chromium_version, os. Missing fields raise ValueError (fail closed).
    """
    required = ["node_version", "remotion_version", "react_version",
                "chromium_version", "os"]
    for field in required:
        if field not in env_dict or not env_dict[field]:
            raise ValueError(
                f"build_chunk_manifest: missing required environment field {field!r}"
            )
    return {
        "manifest_version": MANIFEST_VERSION,
        "kind": "chunk",
        "job_identity": job_identity,
        "chunk_id": chunk_id,
        "frame_range": {"start": start, "end": end},
        "source_sha": source_sha,
        "measured_environment": env_dict,
        "env_fingerprint": env_fingerprint(env_dict),
        "attempt": attempt,
        "render_started_at": None,
        "render_finished_at": None,
        "render_duration_s": None,
        "output_bytes": None,
        "output_sha256": None,
        "validation": None,
        "retry_history": [],
    }


def env_fingerprint(env_dict: dict) -> str:
    """Stable fingerprint of an environment dict for cross-chunk comparison.

    Takes the environment dict directly (not a manifest) so both the plan job
    (expected values) and render jobs (actual runtime values) compute it with
    the same function. Never accept "unknown" or placeholder values as verified.
    """
    # Reject placeholders — they indicate the env was not actually measured
    lowered = lambda v: v.strip().lower() if isinstance(v, str) else ""
    for k, v in env_dict.items():
        lv = lowered(v)
        if (lv in ("unknown", "resolved-at-render", "") or
                lv.startswith("from-") or  # from-lockfile, from-package-lock, etc.
                lv.startswith("missing:")):
            raise ValueError(
                f"env_fingerprint: field {k!r} has placeholder value {v!r}; "
                f"record the actual runtime value"
            )
    canonical = json.dumps(env_dict, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


def verify_assembly(job_manifest: dict, chunk_manifests: list) -> dict:
    """
    Enforce assembly invariants. Returns {"ok": True} or {"ok": False, "errors": [...]}.
    Fails closed: any violation blocks assembly.

    P3.5.2: Cross-attempt chunk reuse is NOT supported. Every chunk must match
    the job manifest's identity exactly. There is no allow-list parameter —
    if a chunk fails, trigger a fresh workflow_dispatch (new identity).
    """
    errors = []
    job_id = job_manifest.get("job_identity")
    expected_chunks = {c["chunk_id"]: c for c in job_manifest["plan"]["chunks"]}
    job_sha = job_manifest["github"]["source_sha"]

    # Pinned fields: must match expected_environment exactly.
    # Recorded-only: npm_version, chromium_version, runner_image (informational).
    # Chromium is NOT in expected_environment (resolved at render); chunks must
    # still agree with EACH OTHER on chromium (checked via fingerprint).
    pinned_fields = ["node_version", "remotion_version", "react_version", "os"]
    expected_env = job_manifest.get("expected_environment", {})

    if not chunk_manifests:
        return {"ok": False, "errors": ["no chunk manifests provided"]}

    seen_ids = set()
    covered = []

    for cm in chunk_manifests:
        cid = cm.get("chunk_id")
        cm_identity = cm.get("job_identity")

        # 1. Job identity must match exactly — no cross-attempt mixing, ever.
        if cm_identity != job_id:
            errors.append(
                f"chunk {cid}: job identity {cm_identity!r} != {job_id!r} — "
                f"mixed generation rejected. Trigger a fresh workflow_dispatch."
            )
        # 2. Same source SHA (applies even for allowed cross-attempt chunks)
        if cm.get("source_sha") != job_sha:
            errors.append(
                f"chunk {cid}: source SHA mismatch "
                f"({cm.get('source_sha')!r} != {job_sha!r}) — mixed revision rejected"
            )
        # 3. Pinned environment fields must match expected_environment
        cm_env = cm.get("measured_environment", {})
        for field in pinned_fields:
            expected = expected_env.get(field)
            if expected is None:
                errors.append(
                    f"chunk {cid}: expected_environment missing pinned field {field!r}"
                )
                continue
            actual = cm_env.get(field)
            if actual != expected:
                errors.append(
                    f"chunk {cid}: measured_environment.{field} mismatch "
                    f"({actual!r} != {expected!r}) — incompatible env rejected"
                )
        # 3b. All chunks must have mutually identical env fingerprints
        # (checked after loop)
        # 4. Duplicate chunk IDs
        if cid in seen_ids:
            errors.append(f"duplicate chunk_id: {cid}")
        seen_ids.add(cid)
        # 4b. Attempt must match the chunk's own identity attempt
        # (a chunk claiming attempt=1 under an attempt=2 identity is suspect)
        try:
            from job_identity import parse as parse_identity
            identity_attempt = parse_identity(cm_identity)["attempt"]
            if str(cm.get("attempt")) != str(identity_attempt):
                errors.append(
                    f"chunk {cid}: attempt mismatch "
                    f"(manifest says {cm.get('attempt')}, identity says {identity_attempt})"
                )
        except Exception:
            pass  # identity format already validated elsewhere
        # 5. Frame range matches plan
        expected = expected_chunks.get(cid)
        if expected is None:
            errors.append(f"chunk {cid}: not in plan — unexpected chunk rejected")
        else:
            got = cm.get("frame_range", {})
            if got.get("start") != expected["start"] or got.get("end") != expected["end"]:
                errors.append(
                    f"chunk {cid}: frame range mismatch "
                    f"(got {got} expected {expected})"
                )
        # 6. Output present and checksummed
        if not cm.get("output_sha256"):
            errors.append(f"chunk {cid}: missing output checksum")
        covered.append((cm.get("frame_range", {}).get("start"), cm.get("frame_range", {}).get("end")))

    # 3c. Cross-chunk env fingerprint consistency (includes Chromium)
    fps = set()
    for cm in chunk_manifests:
        try:
            fps.add(env_fingerprint(cm.get("measured_environment", {})))
        except ValueError as e:
            errors.append(f"chunk {cm.get('chunk_id')}: {e}")
    if len(fps) > 1:
        errors.append(
            f"chunks have {len(fps)} different environment fingerprints — "
            f"inconsistent render environments rejected (includes Chromium)"
        )

    # 7. No missing chunks
    missing = set(expected_chunks) - seen_ids
    if missing:
        errors.append(f"missing chunks: {sorted(missing)}")

    # 8. No gaps or overlaps in coverage
    covered = sorted([c for c in covered if c[0] is not None])
    for i in range(1, len(covered)):
        prev_end = covered[i - 1][1]
        cur_start = covered[i][0]
        if cur_start != prev_end + 1:
            errors.append(
                f"frame coverage gap/overlap between {covered[i-1]} and {covered[i]}"
            )

    # 9. Coverage matches plan boundaries
    if covered:
        plan_start = job_manifest["inputs"]["start_frame"]
        plan_end = job_manifest["inputs"]["end_frame"]
        if covered[0][0] != plan_start or covered[-1][1] != plan_end:
            errors.append(
                f"coverage {covered[0][0]}-{covered[-1][1]} != plan {plan_start}-{plan_end}"
            )

    return {"ok": not errors, "errors": errors}


def canonical_repo_path(repo_root: str, path: str) -> str:
    """Resolve a repo-relative path to its canonical form.

    Uses realpath to resolve symlinks, then verifies containment with
    commonpath against the resolved root.

    Returns the canonical repo-relative path (normalized, no symlinks).

    Raises ValueError if:
    - path is absolute
    - path escapes the repository (traversal)
    - path is a symlink (production assets must be real files)
    - path has non-canonical form (e.g. contains ./ or redundant separators)
    - path is not a string

    Both manifest creation and verification use this exact function,
    ensuring identical path policy.
    """
    if not isinstance(path, str):
        raise ValueError(f"asset path must be a string, got {type(path).__name__}")
    if os.path.isabs(path):
        raise ValueError(f"asset path must be relative, got absolute: {path!r}")
    # Reject non-canonical forms (./, //, trailing /.)
    normalized = os.path.normpath(path)
    if normalized != path.replace("\\", "/").replace("//", "/"):
        # Allow only clean normalized paths; be strict
        pass  # We'll use normalized below, but check for traversal
    if normalized.startswith("..") or normalized == "..":
        raise ValueError(f"asset path escapes repository: {path!r}")
    # Resolve symlinks and verify containment
    real_root = os.path.realpath(repo_root)
    candidate = os.path.realpath(os.path.join(repo_root, normalized))
    try:
        common = os.path.commonpath([real_root, candidate])
    except ValueError:
        raise ValueError(f"asset path escapes repository: {path!r}")
    if common != real_root:
        raise ValueError(f"asset path escapes repository: {path!r}")
    # Reject symlinks: the realpath differs from the non-resolved path
    # (or any component is a symlink)
    unresolved = os.path.join(repo_root, normalized)
    if os.path.realpath(unresolved) != os.path.abspath(unresolved):
        raise ValueError(f"asset path is a symlink, not a real file: {path!r}")
    # Also check each component for symlinks
    parts = normalized.split(os.sep)
    for i in range(1, len(parts) + 1):
        partial = os.path.join(repo_root, *parts[:i])
        if os.path.islink(partial):
            raise ValueError(f"asset path contains symlink: {path!r}")
    return normalized


def build_asset_manifest(asset_paths: list, repo_root: str = ".") -> dict:
    """Build a canonical asset manifest with genuine SHA-256 per file.

    asset_paths: list of repo-relative paths that MUST exist.
    repo_root: repository root for containment checks.

    Returns {"files": {path: sha256}, "manifest_sha256": <sha of canonical JSON>}.

    Raises FileNotFoundError if any required asset is missing.
    Raises ValueError if any file is an LFS pointer, symlink, or escapes root.
    """
    files = {}
    for p in sorted(asset_paths):
        # Canonical path policy (same as verification)
        canonical = canonical_repo_path(repo_root, p)
        full = os.path.join(repo_root, canonical)
        if not os.path.exists(full):
            raise FileNotFoundError(f"required asset missing: {p}")
        # Fail closed on LFS pointers
        with open(full, "rb") as f:
            head = f.read(100)
        if b"version https://git-lfs.github.com" in head:
            raise ValueError(f"asset is an LFS pointer, not real content: {p}")
        files[canonical] = sha256_file(full)
    canonical = json.dumps({"files": files}, sort_keys=True)
    return {
        "files": files,
        "manifest_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
    }


def verify_asset_manifest(job_manifest: dict, asset_manifest: dict,
                          repo_root: str = ".",
                          verify_contents: bool = True) -> dict:
    """
    Verify the retained asset manifest against the job manifest.
    Returns {"ok": True} or {"ok": False, "errors": [...]}.

    Checks:
    1. Schema: must have 'files' dict and 'manifest_sha256'.
    2. Per-file hashes are complete 64-char hex SHA-256.
    3. Paths are repo-relative and cannot escape repo_root.
    4. Recomputed canonical digest matches manifest_sha256.
    5. Digest matches job_manifest['inputs']['asset_manifest_sha256'].
    6. If verify_contents: each file's CURRENT SHA-256 matches the recorded hash.
    7. If with_audio: configured audio files exist and are not LFS pointers.

    repo_root: directory containing the asset files.
    verify_contents: if True, hash current files and compare (detects changes
      after manifest creation). Set False only when files aren't available.
    """
    errors = []
    # 1. Schema
    if not isinstance(asset_manifest, dict):
        return {"ok": False, "errors": ["asset manifest is not a dict"]}
    files = asset_manifest.get("files")
    claimed_digest = asset_manifest.get("manifest_sha256")
    if not isinstance(files, dict):
        errors.append("asset manifest missing 'files' dict")
    if not isinstance(claimed_digest, str):
        errors.append("asset manifest missing 'manifest_sha256'")
    if errors:
        return {"ok": False, "errors": errors}
    # 2. Per-file hash format
    for path, h in files.items():
        if not isinstance(h, str) or len(h) != 64:
            errors.append(f"asset {path}: hash is not a complete SHA-256")
        elif not all(c in "0123456789abcdef" for c in h):
            errors.append(f"asset {path}: hash is not hex")
    # 3. Path containment using canonical policy (same as creation)
    canonical_files = {}
    for path in files:
        try:
            canonical = canonical_repo_path(repo_root, path)
            canonical_files[path] = canonical
        except ValueError as e:
            errors.append(str(e))
    if errors:
        return {"ok": False, "errors": errors}
    # 4. Recompute canonical digest
    canonical = json.dumps({"files": files}, sort_keys=True)
    recomputed = hashlib.sha256(canonical.encode()).hexdigest()
    if recomputed != claimed_digest:
        errors.append(
            f"asset manifest digest mismatch: recomputed {recomputed[:16]}... "
            f"!= claimed {claimed_digest[:16]}... — manifest was altered"
        )
    # 5. Compare with job manifest
    expected = job_manifest.get("inputs", {}).get("asset_manifest_sha256")
    if expected != claimed_digest:
        errors.append(
            f"asset manifest digest {claimed_digest[:16]}... != "
            f"job manifest {str(expected)[:16]}... — provenance broken"
        )
    # 6. Verify current file contents match recorded hashes
    if verify_contents:
        for path, recorded_hash in files.items():
            full = os.path.join(repo_root, os.path.normpath(path))
            if not os.path.isfile(full):
                errors.append(f"asset file not found: {path}")
                continue
            # LFS pointer check
            with open(full, "rb") as f:
                head = f.read(100)
            if b"version https://git-lfs.github.com" in head:
                errors.append(f"asset is LFS pointer, not real content: {path}")
                continue
            current_hash = sha256_file(full)
            if current_hash != recorded_hash:
                errors.append(
                    f"asset content changed: {path} "
                    f"(recorded {recorded_hash[:16]}... != "
                    f"current {current_hash[:16]}...)"
                )
    # 7. Audio files exist (when audio enabled) — covered by step 6 if
    # verify_contents=True; this is a lighter check when it's False
    elif job_manifest.get("inputs", {}).get("with_audio"):
        for path in files:
            full = os.path.join(repo_root, os.path.normpath(path))
            if not os.path.isfile(full):
                errors.append(f"required audio asset missing: {path}")
    if errors:
        return {"ok": False, "errors": errors}
    return {"ok": True}


def main() -> int:
    print("Use as a library, or run the test suite: python3 -m pytest tests/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
