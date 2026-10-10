#!/usr/bin/env python3
"""P3.12 recovery planning: validate a prior run and build the resume plan.

Runs in the plan job when resume_from_run_id is set. Uses the GitHub CLI
(`gh`) with GITHUB_TOKEN to fetch the prior run's manifests via the API.

Inputs (env vars):
  RESUME_FROM_RUN_ID: prior run ID (required)
  GITHUB_TOKEN: token with actions:read (required)
  REPO: owner/repo (required)
  JOB_MANIFEST: path to current job_manifest.json (required)
  OUTPUT_DIR: directory for resume_plan.json (required)
  GITHUB_OUTPUT: for matrix output (optional; also writes render_matrix.json)

Outputs:
  $OUTPUT_DIR/resume_plan.json — the validated resume plan
  Updated $JOB_MANIFEST with the `resume` section
  $OUTPUT_DIR/render_matrix.json — [{"chunk_id","start","end"}, ...] to render
  GITHUB_OUTPUT: resume_matrix=<json>, resume_enabled=true

Fail closed: any validation failure exits non-zero with a clear error.
Never silently falls back to a full render while claiming resume.
"""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from recovery import build_resume_plan
from artifact_verify import (inspect_chunk_archive, ArchiveError,
                              ArchiveContradiction)


def fatal(msg):
    print(f"RECOVERY FATAL: {msg}", file=sys.stderr)
    sys.exit(1)


def gh_api(path):
    """GET a GitHub API path. Returns parsed JSON.

    P4.0: uses urllib directly with GITHUB_TOKEN (more reliable than gh CLI
    in runners). P3.12.2: manual pagination via gh_api_paginated_list.
    """
    import urllib.request
    import urllib.error
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        fatal("GITHUB_TOKEN is not set in environment")
    # Path may include query params; ensure it starts with /
    if not path.startswith("/"):
        path = "/" + path
    url = f"https://api.github.com{path}"
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("User-Agent", "cosmo-p4-recovery")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read().decode()
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:500]
        fatal(f"GitHub API {path} failed: HTTP {e.code}: {body}")
    except Exception as e:
        fatal(f"GitHub API {path} failed: {e}")
    if not data.strip():
        fatal(f"GitHub API {path} returned empty output")
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        fatal(f"GitHub API {path} returned invalid JSON: {e}")


def gh_api_paginated_list(base_path, list_key):
    """GET a paginated list endpoint, combining ALL pages.

    P3.12.2: manual pagination (per_page=100, page=N) until total_count
    items are collected. Never relies on the default page size covering
    a full production video (20+ chunk artifacts).
    Returns the combined list.
    """
    items = []
    page = 1
    total = None
    while True:
        sep = "&" if "?" in base_path else "?"
        data = gh_api(f"{base_path}{sep}per_page=100&page={page}")
        if total is None:
            total = data.get("total_count", 0)
        batch = data.get(list_key, [])
        items.extend(batch)
        # Stop when we've collected everything, or the API stops paging.
        if len(items) >= total or not batch:
            break
        page += 1
        if page > 100:  # sanity bound: 10,000 items max
            fatal(f"artifact pagination exceeded 100 pages for {base_path}")
    if len(items) != total:
        print(f"WARNING: expected {total} items, collected {len(items)}",
              file=sys.stderr)
    return items


def download_artifact_zip(artifact_id, dest_dir):
    """Download an artifact zip via GitHub API. Returns path to zip.

    P4.1: handles cross-origin redirects safely. The API returns a 302 to
    artifact storage (different host). The GitHub bearer token must NOT be
    forwarded to the storage host — the signed URL carries its own auth.
    Validates redirect is HTTPS; strips Authorization on redirect; never
    prints URLs or tokens to logs.
    """
    import urllib.request
    import urllib.error
    import urllib.parse
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        fatal("GITHUB_TOKEN is not set in environment")
    zip_path = os.path.join(dest_dir, f"artifact_{artifact_id}.zip")
    # REPO is a global set in main()
    api_url = (f"https://api.github.com/repos/{REPO}/actions/artifacts/"
               f"{artifact_id}/zip")

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    def fetch(url, with_auth):
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("User-Agent", "cosmo-p4-recovery")
        if with_auth:
            req.add_header("Authorization", "Bearer [REDACTED]")
            # Set the real header via add_unredirected_header so it is
            # NOT forwarded on manual redirects; we handle redirects
            # explicitly below.
            req.add_unredirected_header("Authorization", f"Bearer {token}")
        opener = urllib.request.build_opener(NoRedirect)
        try:
            return opener.open(req, timeout=300)
        except urllib.error.HTTPError as e:
            return e

    # Step 1: API request (with auth). Expect 302 to storage.
    resp = fetch(api_url, with_auth=True)
    if isinstance(resp, urllib.error.HTTPError):
        if resp.code in (301, 302, 303, 307, 308):
            location = resp.headers.get("Location", "")
            # Validate redirect target.
            parsed = urllib.parse.urlparse(location)
            if parsed.scheme != "https":
                fatal(f"artifact {artifact_id}: redirect to non-HTTPS URL "
                      f"(host={parsed.hostname or 'unknown'}) — refusing")
            if not parsed.hostname:
                fatal(f"artifact {artifact_id}: redirect missing host — "
                      f"refusing")
            # Never log the signed URL (contains credentials).
            print(f"Artifact {artifact_id}: following redirect to "
                  f"https://{parsed.hostname}/... (auth stripped)",
                  file=sys.stderr)
            # Step 2: Fetch from storage WITHOUT the GitHub bearer token.
            # The signed URL carries its own time-limited auth.
            resp2 = fetch(location, with_auth=False)
            if isinstance(resp2, urllib.error.HTTPError):
                fatal(f"artifact {artifact_id}: storage download failed: "
                      f"HTTP {resp2.code} from {parsed.hostname}")
            resp = resp2
        else:
            # Try to read error body safely (may be empty).
            try:
                body = resp.read().decode()[:300]
            except Exception:
                body = ""
            # Do not print token; report status and host only.
            fatal(f"artifact download failed for {artifact_id}: "
                  f"HTTP {resp.code} from api.github.com. {body}")
    # Step 3: Stream to file.
    try:
        with open(zip_path, "wb") as f:
            while True:
                chunk = resp.read(65536)
                if not chunk:
                    break
                f.write(chunk)
    except Exception as e:
        fatal(f"artifact download failed for {artifact_id}: {e}")
    finally:
        try:
            resp.close()
        except Exception:
            pass
    if not os.path.exists(zip_path) or os.path.getsize(zip_path) == 0:
        fatal(f"artifact download failed for {artifact_id}: empty file")
    return zip_path


def extract_json(zip_path, name):
    """Extract and parse a JSON file from a zip, safely (P3.12.2).

    Validates the archive before reading: rejects corrupt ZIPs, unsafe
    paths, and duplicate/ambiguous filenames.
    """
    from artifact_verify import (open_archive, _safe_members, read_manifest,
                                  ArchiveError, ArchiveContradiction)
    try:
        zf = open_archive(zip_path)
    except (ArchiveError, ArchiveContradiction) as e:
        fatal(f"prior job archive unusable: {e}")
    try:
        matches = [i for i in _safe_members(zf)
                   if os.path.basename(i.filename) == name]
        if not matches:
            fatal(f"{name} not found in {zip_path}")
        if len(matches) > 1:
            fatal(f"ambiguous {name} in {zip_path}: "
                  f"{len(matches)} matches — refusing")
        return read_manifest(zf, matches[0])
    except ArchiveError as e:
        fatal(f"prior job manifest unreadable: {e}")
    finally:
        zf.close()


if __name__ == "__main__":
    RESUME_FROM_RUN_ID = os.environ.get("RESUME_FROM_RUN_ID", "").strip()
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
    REPO = os.environ.get("REPO", "")
    JOB_MANIFEST = os.environ.get("JOB_MANIFEST", "")
    OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "")

    if not RESUME_FROM_RUN_ID:
        fatal("RESUME_FROM_RUN_ID is empty")
    if not RESUME_FROM_RUN_ID.isdigit():
        fatal(f"RESUME_FROM_RUN_ID must be a numeric run ID, got "
              f"{RESUME_FROM_RUN_ID!r}")
    if not GITHUB_TOKEN:
        fatal("GITHUB_TOKEN is empty (need actions:read)")
    if not REPO or "/" not in REPO:
        fatal(f"REPO must be owner/repo, got {REPO!r}")
    if not os.path.isfile(JOB_MANIFEST):
        fatal(f"JOB_MANIFEST not found: {JOB_MANIFEST}")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(JOB_MANIFEST) as f:
        current_manifest = json.load(f)

    print(f"Recovery: validating prior run {RESUME_FROM_RUN_ID} "
          f"in {REPO}...")

    # 1. Verify the prior run exists and belongs to this repo + workflow.
    # P3.12.2: explicit run-ID agreement — the API must return the exact
    # run we asked for.
    run_info = gh_api(f"/repos/{REPO}/actions/runs/{RESUME_FROM_RUN_ID}")
    api_run_id = str(run_info.get("id", ""))
    if api_run_id != RESUME_FROM_RUN_ID:
        fatal(f"API returned run {api_run_id}, expected {RESUME_FROM_RUN_ID} "
              f"— refusing")
    if run_info.get("repository", {}).get("full_name", "").lower() != REPO.lower():
        fatal(f"prior run {RESUME_FROM_RUN_ID} belongs to "
              f"{run_info.get('repository', {}).get('full_name')}, not {REPO}")
    # P3.12.2: the source run must be the production workflow.
    # The workflow file path is the stable identity.
    api_workflow_path = (run_info.get("path") or "")
    if api_workflow_path != ".github/workflows/render-production.yml":
        fatal(f"prior run workflow path {api_workflow_path!r} is not the "
              f"production workflow — refusing")
    prior_workflow = run_info.get("workflow_id")
    print(f"Prior run workflow_id={prior_workflow}, "
          f"status={run_info.get('status')}, "
          f"conclusion={run_info.get('conclusion')}")
    if run_info.get("head_branch"):
        print(f"Prior run branch: {run_info['head_branch']}")
    # P3.12.1: explicit status policy — pass to the validator.
    prior_run_status = {"status": run_info.get("status"),
                        "conclusion": run_info.get("conclusion")}
    # P3.12.2: the API's actual source commit must match the manifest's.
    api_head_sha = run_info.get("head_sha", "")

    # 2. List prior run artifacts; find the job manifest by exact name.
    # P3.12.2: pagination-safe — retrieves every artifact, not just the
    # first page.
    all_artifacts = gh_api_paginated_list(
        f"/repos/{REPO}/actions/runs/{RESUME_FROM_RUN_ID}/artifacts",
        "artifacts")
    job_artifacts = [a for a in all_artifacts
                     if a["name"].startswith("job-") and not a["expired"]]
    if not job_artifacts:
        fatal(f"no job manifest artifact found for run {RESUME_FROM_RUN_ID}")
    if len(job_artifacts) > 1:
        fatal(f"ambiguous: {len(job_artifacts)} job manifests for run "
              f"{RESUME_FROM_RUN_ID}")
    job_artifact = job_artifacts[0]
    print(f"Prior job manifest artifact: {job_artifact['name']}")

    tmpd = tempfile.mkdtemp(prefix="recovery_")
    prior_job_zip = download_artifact_zip(job_artifact["id"], tmpd)
    prior_manifest = extract_json(prior_job_zip, "job_manifest.json")
    print(f"Prior job identity: {prior_manifest.get('job_identity')}")
    # P3.12.2: the downloaded manifest's provenance must agree with the API.
    # - run ID matches the requested source run
    # - source SHA matches the API's actual head_sha
    # - canonical identity embeds the same run/attempt
    pm_github = prior_manifest.get("github", {})
    if str(pm_github.get("run_id")) != RESUME_FROM_RUN_ID:
        fatal(f"prior manifest run_id {pm_github.get('run_id')} != "
              f"requested {RESUME_FROM_RUN_ID} — refusing")
    if pm_github.get("source_sha") != api_head_sha:
        fatal(f"prior manifest source_sha {pm_github.get('source_sha')} != "
              f"API head_sha {api_head_sha} — refusing")
    # Canonical identity format: run-{run_id}-attempt-{n}-{sha8}.
    pm_identity = prior_manifest.get("job_identity", "")
    if RESUME_FROM_RUN_ID not in pm_identity:
        fatal(f"prior manifest identity {pm_identity!r} does not embed "
              f"run {RESUME_FROM_RUN_ID} — refusing")

    # 3. Gather prior chunk manifests from chunk artifacts.
    # P3.12.2: exact names tied to the validated job identity and chunk ID.
    # Exclude the chunk ledger artifact (chunk-ledger-*) from chunk artifacts —
    # it is a build_ledger.py aggregate, not a per-chunk output, and must not
    # be subject to the per-chunk identity prefix check below.
    chunk_artifacts = [a for a in all_artifacts
                       if a["name"].startswith("chunk-")
                       and not a["name"].startswith("chunk-ledger-")
                       and not a["expired"]]
    print(f"Found {len(chunk_artifacts)} prior chunk artifacts")
    prior_chunk_manifests = {}
    # P3.12.2: safe, real output verification per archive. Each archive is
    # validated (ZIP integrity -> safe members -> exact chunk files) before
    # any content is trusted. Individual archive failures -> rerender that
    # chunk; contradictions -> fail closed.
    real_shas = {}
    real_sizes = {}
    manifest_shas = {}
    for ca in chunk_artifacts:
        # P3.12.2: artifact names must tie to the validated prior identity.
        # Format: chunk-{identity}-{chunk_id}.
        expected_prefix = f"chunk-{prior_manifest.get('job_identity')}-"
        if not ca["name"].startswith(expected_prefix):
            fatal(f"chunk artifact {ca['name']!r} does not match validated "
                  f"prior identity — refusing")
        czip = download_artifact_zip(ca["id"], tmpd)
        # Chunk artifact names: chunk-{identity}-{id}. Parse the ID.
        try:
            cid = int(ca["name"].rsplit("-", 1)[1])
        except (ValueError, IndexError):
            print(f"WARNING: cannot parse chunk ID from {ca['name']}; skipping",
                  file=sys.stderr)
            continue
        if cid in prior_chunk_manifests:
            fatal(f"duplicate prior chunk artifact for chunk_id {cid}")
        try:
            inspected = inspect_chunk_archive(czip, cid)
        except ArchiveContradiction as e:
            fatal(f"archive contradiction for chunk {cid}: {e}")
        except ArchiveError as e:
            # Individual chunk unusable -> it will be rerendered. Do not
            # record it, so selection treats it as missing.
            print(f"Chunk {cid} archive unusable ({e}); will rerender",
                  file=sys.stderr)
            continue
        cm = inspected["manifest"]
        prior_chunk_manifests[cid] = cm
        real_shas[cid] = inspected["video_sha256"]
        real_sizes[cid] = inspected["video_bytes"]
        # P3.12.2: origin_manifest_sha256 is the hash of the manifest FILE
        # bytes, not a copy of the video hash.
        manifest_shas[cid] = inspected["manifest_sha256"]
        # Cross-check manifest's claim against reality (informational;
        # _chunk_eligible enforces the comparison that matters).
        if cm.get("output_sha256") != inspected["video_sha256"]:
            print(f"WARNING: chunk {cid} manifest checksum != actual "
                  f"video bytes; will rerender", file=sys.stderr)

    # 4. Build current fingerprint inputs from the current manifest.
    from generation import fingerprint_inputs_from_job_manifest
    current_inputs = fingerprint_inputs_from_job_manifest(current_manifest)
    current_plan = current_manifest["plan"]["chunks"]
    current_asset_digest = current_manifest["inputs"]["asset_manifest_sha256"]

    # P3.12.1: measured-environment compatibility policy for candidates.
    # Built from the current run's EXPECTED values (what the new chunks will
    # be measured against). Each candidate's measured env must satisfy it.
    expected_env = {
        "node_version": current_inputs["node_version"],
        "remotion_version": current_inputs["remotion_version"],
        "react_version": current_inputs["react_version"],
        "os": current_inputs["os"],
        "chromium_version": current_inputs["expected_chromium_version"],
    }

    # 5. Validate and select.
    # P4.4 SPLIT (§6.1): REASSEMBLE_BYPASS_FINGERPRINT env var selects
    # assembly-only mode. The split fingerprint means assembly-logic changes
    # no longer invalidate the render fingerprint — the mode flag declares
    # intent (zero render jobs), not a validation bypass.
    import os as _os
    _mode = "assembly_only" if _os.environ.get(
        "REASSEMBLE_BYPASS_FINGERPRINT", "false").lower() == "true" else "chunk_recovery"
    if _mode == "assembly_only":
        print("P4.4 REASSEMBLY MODE: assembly-only (zero render jobs expected)")
    result = build_resume_plan(prior_manifest, prior_chunk_manifests,
                               current_inputs, current_plan,
                               current_asset_digest,
                               artifact_shas=real_shas,
                               artifact_sizes=real_sizes,
                               manifest_shas=manifest_shas,
                               expected_env=expected_env,
                               prior_run_status=prior_run_status,
                               mode=_mode)
    if not result["ok"]:
        print("RESUME REJECTED:", file=sys.stderr)
        for e in result["errors"]:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    resume_plan = result["resume_plan"]
    # build_resume_plan already sets allowed_source_run_ids.

    # 6. Persist: resume plan file, updated job manifest, render matrix.
    with open(os.path.join(OUTPUT_DIR, "resume_plan.json"), "w") as f:
        json.dump(resume_plan, f, indent=2)

    current_manifest["resume"] = resume_plan
    with open(JOB_MANIFEST, "w") as f:
        json.dump(current_manifest, f, indent=2)

    render_list = [{"chunk_id": c["chunk_id"], "start": c["start"],
                    "end": c["end"]} for c in resume_plan["render"]]
    with open(os.path.join(OUTPUT_DIR, "render_matrix.json"), "w") as f:
        json.dump(render_list, f)

    print(f"Resume plan: {resume_plan['reused_count']} chunks reusable, "
          f"{resume_plan['render_count']} to render")
    for r in resume_plan["reuse"]:
        print(f"  reuse chunk {r['chunk_id']} from run {r['origin_run_id']}")
    for r in resume_plan["render"]:
        print(f"  render chunk {r['chunk_id']}: {r['reason']}")

    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a") as f:
            f.write(f"resume_enabled=true\n")
            f.write(f"resume_matrix={json.dumps({'chunk': render_list})}\n")
