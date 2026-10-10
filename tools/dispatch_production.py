#!/usr/bin/env python3
"""Errorless production dispatch (2026-10-10, Hamza's rule).

NEVER dispatches without passing pre-dispatch validation first.
This is the ONLY approved way to start a production render.

Usage:
  python3 tools/dispatch_production.py \
      --composition HousingBroke --start-frame 0 --end-frame 23150 \
      --label "Q-004" [--dry-run]

Steps:
  1. Run .github/scripts/validate_dispatch.py — abort if ANY check fails.
  2. Verify the branch is pushed (local HEAD == remote HEAD).
  3. Dispatch via the GitHub API.
  4. Register the run with the monitor (writes state file).
  5. Print the run URL.

Exit 0 = dispatched. Exit 1 = validation failed (nothing dispatched).
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "wastor453-ux/rendering-production"
BRANCH = "p4-4-ccdecbc-readiness"
WORKFLOW = "render-production.yml"
STATE_DIR = os.path.expanduser("~/workspace/crackit/demo-video/.production-state")

sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response


def gh_api(method, path, payload=None, timeout=60, retries=4):
    body = json.dumps(payload).encode() if payload is not None else None
    for attempt in range(retries):
        req = urllib.request.Request("https://api.github.com" + path,
                                     data=body, method=method)
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("User-Agent", "cosmo-dispatch")
        if body:
            req.add_header("Content-Type", "application/json")
        add_surrogate_to_request(req, "custom.github",
                                 allowed_hosts=["api.github.com"])
        try:
            return read_json_response(urllib.request.urlopen(req, timeout=timeout))
        except urllib.error.HTTPError as e:
            print(f"HTTP {e.code}: {e.read().decode()[:300]}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"  retry {attempt+1}: {e.__class__.__name__}", file=sys.stderr)
            time.sleep(2 ** attempt)
    print("FATAL: API failed after retries", file=sys.stderr)
    sys.exit(1)


def run_validator(args):
    cmd = [sys.executable, ".github/scripts/validate_dispatch.py",
           "--composition", args.composition,
           "--start-frame", str(args.start_frame),
           "--end-frame", str(args.end_frame),
           "--chunk-size", str(args.chunk_size),
           "--vo-file", args.vo_file,
           "--bed-file", args.bed_file,
           "--with-audio", "true" if args.with_audio else "false"]
    print("Running pre-dispatch validation...")
    r = subprocess.run(cmd, cwd=REPO_ROOT)
    return r.returncode == 0


def check_branch_pushed():
    """Remote branch must carry the same tree as local HEAD — the runner uses GitHub's copy.

    Compares tree SHAs, not commit SHAs: pushes made via the Git Data API
    create new commit objects (new SHAs) for the same tree, so a strict
    commit-SHA check would fail forever after an API push.
    """
    local_tree = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=REPO_ROOT,
                                capture_output=True, text=True).stdout.strip()
    ref = gh_api("GET", f"/repos/{REPO}/git/ref/heads/{BRANCH}")
    remote = ref["object"]["sha"]
    remote_commit = gh_api("GET", f"/repos/{REPO}/git/commits/{remote}")
    remote_tree = remote_commit["tree"]["sha"]
    if local_tree != remote_tree:
        print(f"FATAL: branch not pushed (local tree {local_tree[:8]} != remote tree {remote_tree[:8]}). "
              f"Push first.", file=sys.stderr)
        return False
    print(f"Branch pushed: {BRANCH} @ {remote[:8]} (tree {local_tree[:8]})")
    return True


def main():
    p = argparse.ArgumentParser(description="Errorless production dispatch")
    p.add_argument("--composition", required=True)
    p.add_argument("--start-frame", type=int, default=0)
    p.add_argument("--end-frame", type=int, required=True)
    p.add_argument("--chunk-size", type=int, default=600)
    p.add_argument("--max-parallel", type=int, default=20)
    p.add_argument("--crf", type=int, default=18)
    p.add_argument("--with-audio", action="store_true", default=True)
    p.add_argument("--no-audio", dest="with_audio", action="store_false")
    p.add_argument("--vo-file", default="public/audio/vo_housingbroke.wav")
    p.add_argument("--bed-file", default="public/audio/bed.mp3")
    p.add_argument("--label", default="")
    p.add_argument("--resume-from-run-id", default="")
    p.add_argument("--dry-run", action="store_true",
                   help="Validate only, do not dispatch")
    args = p.parse_args()

    # GATE 1: pre-dispatch validation (catches input errors like wrong VO).
    if not run_validator(args):
        print("\nDISPATCH ABORTED: fix validation errors above.", file=sys.stderr)
        sys.exit(1)
    print("Validation PASSED.")

    if args.dry_run:
        print("Dry run: validation passed, not dispatching.")
        sys.exit(0)

    # GATE 2: branch must be pushed.
    if not check_branch_pushed():
        sys.exit(1)

    # Dispatch.
    inputs = {
        "composition": args.composition,
        "label": args.label or f"{args.composition} production",
        "start_frame": str(args.start_frame),
        "end_frame": str(args.end_frame),
        "chunk_size": str(args.chunk_size),
        "max_parallel": str(args.max_parallel),
        "crf": str(args.crf),
        "with_audio": args.with_audio,
        "vo_file": args.vo_file,
        "bed_file": args.bed_file,
    }
    if args.resume_from_run_id:
        inputs["resume_from_run_id"] = args.resume_from_run_id

    gh_api("POST",
           f"/repos/{REPO}/actions/workflows/{WORKFLOW}/dispatches",
           {"ref": BRANCH, "inputs": inputs})
    print("Dispatch sent. Waiting for run to appear...")

    # Find the new run.
    run_id = None
    for _ in range(12):
        time.sleep(10)
        runs = gh_api("GET",
                      f"/repos/{REPO}/actions/workflows/{WORKFLOW}/runs?per_page=3")
        for r in runs["workflow_runs"]:
            if r["head_branch"] == BRANCH and r["event"] == "workflow_dispatch":
                # The newest dispatch on this branch is ours.
                run_id = r["id"]
                break
        if run_id:
            break
    if not run_id:
        print("WARNING: dispatch sent but run not found yet", file=sys.stderr)
        sys.exit(0)

    url = f"https://github.com/{REPO}/actions/runs/{run_id}"
    print(f"Run {run_id}: {url}")

    # Register with the monitor.
    os.makedirs(STATE_DIR, exist_ok=True)
    state = {
        "run_id": run_id,
        "url": url,
        "composition": args.composition,
        "dispatched_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "last_status": "queued",
        "last_conclusion": None,
        "recovery_attempts": 0,
        "done": False,
    }
    with open(os.path.join(STATE_DIR, "active_run.json"), "w") as f:
        json.dump(state, f, indent=2)
    print(f"Monitor registered: {STATE_DIR}/active_run.json")


if __name__ == "__main__":
    main()
