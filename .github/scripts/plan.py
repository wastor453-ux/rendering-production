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


def validate_crf(value: str) -> str:
    try:
        n = int(value)
    except (TypeError, ValueError):
        fatal(f"crf must be an integer, got {value!r}")
    if not 0 <= n <= 51:
        fatal(f"crf must be 0-51 (H.264 valid range), got {n}")
    return str(n)


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

    if end < start:
        fatal(f"END_FRAME ({end}) < START_FRAME ({start})")
    if chunk_size > (end - start + 1):
        print(f"WARNING: CHUNK_SIZE ({chunk_size}) > total frames "
              f"({end - start + 1}); single chunk", file=sys.stderr)

    # --- Asset paths (validated, repo-relative) ---
    asset_paths = []
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
    beats_sha = require_file("src/compiled_p3/beat_timeline.json")
    events_sha = require_file("src/compiled_p3/events.json")

    # --- Payload checksums ---
    payload_shas = {}
    payload_dir = os.path.join(repo_root, "src/compiled_p3/payloads")
    if os.path.isdir(payload_dir):
        for f in sorted(os.listdir(payload_dir)):
            if f.endswith(".json"):
                payload_shas[f] = sha256_file(os.path.join(payload_dir, f))

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
    return 0


if __name__ == "__main__":
    sys.exit(main())
