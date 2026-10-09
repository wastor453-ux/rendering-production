#!/usr/bin/env python3
"""Failure classifier for the render pipeline (2026-10-10, Hamza's rule).

Given a production run's job statuses, classifies WHAT died so the RIGHT
recovery runs — never a blind full restart.

Classifications:
  PLAN_FAILURE   — the plan job failed. Recovery: fix inputs, dispatch fresh.
  CHUNK_FAILURE  — one or more render chunks failed. Recovery: resume with
                   resume_from_run_id; only failed chunks re-render.
  ASSEMBLY_DEATH — all chunks rendered, but assembly failed/was killed.
                   Recovery: dispatch the reassemble-only workflow.
                   ZERO re-render. This is the case Hamza's rule targets.
  SUCCESS        — everything passed. Nothing to recover.
  UNKNOWN        — cannot classify. Manual investigation required.

Usage:
  python3 classify_failure.py --run-id 12345 [--token TOKEN] [--repo owner/repo]
  python3 classify_failure.py --jobs-json jobs.json   # offline / testing

The pure function classify() takes a list of {"name":..., "conclusion":...}
and returns {"classification":..., "recovery":..., "detail":...}.
"""

import json
import os
import sys
import urllib.request
import urllib.error

# Canonical job names in render-production.yml
PLAN_JOB = "plan"
RENDER_JOB = "render-chunk"
ASSEMBLE_JOB = "assemble"

TERMINAL_FAILURE = {"failure", "cancelled", "timed_out", "action_required"}


def _conclusion(jobs, name):
    """Return the conclusion of the named job, or None if not found."""
    for j in jobs:
        # Matrix jobs appear as "render-chunk (0)" etc.; match prefix.
        jname = j.get("name", "")
        if jname == name or jname.startswith(name + " ("):
            return j.get("conclusion")
    return None


def _render_chunks_status(jobs):
    """Aggregate status across all render-chunk matrix jobs."""
    conclusions = [
        j.get("conclusion")
        for j in jobs
        if j.get("name", "") == RENDER_JOB
        or j.get("name", "").startswith(RENDER_JOB + " (")
    ]
    if not conclusions:
        return None
    if all(c == "success" for c in conclusions):
        return "success"
    if all(c == "skipped" for c in conclusions):
        return "skipped"
    if any(c in TERMINAL_FAILURE for c in conclusions):
        failed = sum(1 for c in conclusions if c in TERMINAL_FAILURE)
        return f"failure({failed}/{len(conclusions)})"
    return "incomplete"


def classify(jobs):
    """Classify a run's failure from its job conclusions.

    jobs: list of {"name": str, "conclusion": str|None}
    Returns {"classification", "recovery", "detail"}.
    """
    plan = _conclusion(jobs, PLAN_JOB)
    render = _render_chunks_status(jobs)
    assemble = _conclusion(jobs, ASSEMBLE_JOB)

    # 1. Plan never succeeded -> nothing downstream is valid.
    if plan in TERMINAL_FAILURE or plan is None:
        return {
            "classification": "PLAN_FAILURE",
            "recovery": "fix_dispatch_inputs",
            "detail": f"plan job concluded '{plan}'; no chunks are trustworthy, dispatch fresh",
        }

    # 2. Any chunk failed -> chunk-level recovery.
    if render and render.startswith("failure"):
        return {
            "classification": "CHUNK_FAILURE",
            "recovery": "resume_render_failed_chunks",
            "detail": f"render-chunk status '{render}'; resume with resume_from_run_id, "
                      "re-render ONLY failed chunks (recovery.py selects them)",
        }

    # 3. Chunks OK (or legitimately skipped via zero-render resume),
    #    but assembly died -> REASSEMBLE ONLY. Hamza's rule.
    if render in ("success", "skipped") and assemble in TERMINAL_FAILURE:
        return {
            "classification": "ASSEMBLY_DEATH",
            "recovery": "dispatch_reassemble_only",
            "detail": f"chunks '{render}', assembly '{assemble}'; "
                      "dispatch render-production-reassemble.yml with source_run_id. "
                      "ZERO re-render.",
        }

    # 4. Everything green.
    if render == "success" and assemble == "success":
        return {
            "classification": "SUCCESS",
            "recovery": "none",
            "detail": "all jobs succeeded; nothing to recover",
        }

    # 5. Anything else (still running, weird states).
    return {
        "classification": "UNKNOWN",
        "recovery": "manual_investigation",
        "detail": f"plan={plan} render={render} assemble={assemble}; "
                  "state not classifiable, investigate before recovering",
    }


def fetch_jobs(repo, run_id, token):
    """Fetch job conclusions for a run via the GitHub API (auth-stripped redirects)."""
    url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/jobs?per_page=100"

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("User-Agent", "cosmo-failure-classifier")
    opener = urllib.request.build_opener(NoRedirect)
    try:
        with opener.open(req, timeout=60) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        print(f"FATAL: API {e.code} fetching jobs for run {run_id}", file=sys.stderr)
        sys.exit(1)
    return [
        {"name": j["name"], "conclusion": j["conclusion"]}
        for j in data.get("jobs", [])
    ]


def main(argv):
    import argparse
    p = argparse.ArgumentParser(description="Classify a render run's failure")
    p.add_argument("--run-id", help="GitHub Actions run ID to classify")
    p.add_argument("--repo", default=os.environ.get("REPO", "wastor453-ux/rendering-production"))
    p.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"))
    p.add_argument("--jobs-json", help="Path to jobs JSON (offline mode: [{\"name\":..,\"conclusion\":..}])")
    args = p.parse_args(argv)

    if args.jobs_json:
        jobs = json.load(open(args.jobs_json))
    elif args.run_id:
        if not args.token:
            print("FATAL: --token or GITHUB_TOKEN required", file=sys.stderr)
            sys.exit(2)
        jobs = fetch_jobs(args.repo, args.run_id, args.token)
    else:
        print("FATAL: provide --run-id or --jobs-json", file=sys.stderr)
        sys.exit(2)

    result = classify(jobs)
    print(json.dumps(result, indent=2))
    # Exit code signals the recovery path for automation:
    # 0=SUCCESS/none, 10=ASSEMBLY_DEATH, 11=CHUNK_FAILURE, 12=PLAN_FAILURE, 13=UNKNOWN
    codes = {"SUCCESS": 0, "ASSEMBLY_DEATH": 10, "CHUNK_FAILURE": 11,
             "PLAN_FAILURE": 12, "UNKNOWN": 13}
    sys.exit(codes[result["classification"]])


if __name__ == "__main__":
    main(sys.argv[1:])
