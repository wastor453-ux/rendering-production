#!/usr/bin/env python3
"""Production monitor (2026-10-10, Hamza's rule).

Watches the active GitHub production run. Designed to run every minute
via cron while a production is active.

On each check:
  - Reads ~/workspace/crackit/demo-video/.production-state/active_run.json
  - Fetches the run's current status via the GitHub API
  - Logs status changes
  - On failure: runs classify_failure.py and takes the safe action:
      ASSEMBLY_DEATH -> auto-dispatch reassemble workflow (zero re-render)
      CHUNK_FAILURE  -> auto-resume with resume_from_run_id (failed chunks only)
      PLAN_FAILURE   -> ALERT ONLY (inputs may be wrong; never auto-dispatch)
      UNKNOWN        -> ALERT ONLY
  - On success: marks done, stops monitoring

Alerts are written to .production-state/alerts.log AND printed.
The cron job's output is the alert channel.

Usage:
  python3 tools/monitor_production.py [--once]
"""
import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "wastor453-ux/rendering-production"
STATE_DIR = os.path.expanduser("~/workspace/crackit/demo-video/.production-state")
STATE_FILE = os.path.join(STATE_DIR, "active_run.json")
ALERT_LOG = os.path.join(STATE_DIR, "alerts.log")

sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response
sys.path.insert(0, os.path.join(REPO_ROOT, ".github", "scripts"))
from classify_failure import classify


def gh_api(method, path, payload=None, timeout=45, retries=3):
    body = json.dumps(payload).encode() if payload is not None else None
    for attempt in range(retries):
        req = urllib.request.Request("https://api.github.com" + path,
                                     data=body, method=method)
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("User-Agent", "cosmo-monitor")
        if body:
            req.add_header("Content-Type", "application/json")
        add_surrogate_to_request(req, "custom.github",
                                 allowed_hosts=["api.github.com"])
        try:
            return read_json_response(urllib.request.urlopen(req, timeout=timeout))
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                raise
            print(f"HTTP {e.code} on {path}", file=sys.stderr)
            return None
        except Exception:
            time.sleep(2 ** attempt)
    return None


def alert(msg):
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(f"ALERT: {line}", flush=True)
    with open(ALERT_LOG, "a") as f:
        f.write(line + "\n")


def load_state():
    if not os.path.isfile(STATE_FILE):
        return None
    with open(STATE_FILE) as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def fetch_jobs(run_id):
    data = gh_api("GET",
                  f"/repos/{REPO}/actions/runs/{run_id}/jobs?per_page=50")
    if not data:
        return None
    return [{"name": j["name"], "conclusion": j["conclusion"]}
            for j in data.get("jobs", [])]


def auto_recover(state, classification):
    """Take the safe automatic recovery action. Returns True if dispatched."""
    run_id = state["run_id"]
    cls = classification["classification"]

    if cls == "ASSEMBLY_DEATH":
        # Zero-risk: reassemble the same chunks, no re-render.
        payload = {
            "ref": "p4-4-complete-preproduction-closure",
            "inputs": {
                "composition": state.get("composition", "HousingBroke"),
                "label": f"Auto-recovery: reassemble run {run_id}",
                "start_frame": "0", "end_frame": "23150",
                "reassemble_bypass_fingerprint": True,
            },
        }
        # Use the dedicated reassemble workflow via repository_dispatch
        # for a clean single-call trigger.
        disp = {
            "event_type": "reassemble",
            "client_payload": {"source_run_id": str(run_id)},
        }
        r = gh_api("POST", f"/repos/{REPO}/dispatches", disp)
        if r is not None:
            alert(f"Run {run_id}: ASSEMBLY_DEATH -> auto-dispatched reassemble workflow")
            state["recovery_attempts"] += 1
            return True
        alert(f"Run {run_id}: ASSEMBLY_DEATH -> reassemble dispatch FAILED, manual action needed")
        return False

    if cls == "CHUNK_FAILURE":
        # Safe: resume re-renders ONLY failed chunks (recovery.py selects).
        alert(f"Run {run_id}: CHUNK_FAILURE -> manual resume needed "
              f"(dispatch_production.py --resume-from-run-id {run_id}). "
              f"Auto-resume disabled: chunk failures need a human glance first.")
        return False

    # PLAN_FAILURE and UNKNOWN: never auto-dispatch.
    alert(f"Run {run_id}: {cls} -> {classification['detail']}. "
          f"Manual action required, NOT auto-recovering.")
    return False


def check_once():
    state = load_state()
    if not state:
        print("No active run registered. Nothing to monitor.")
        return 0
    if state.get("done"):
        print(f"Run {state['run_id']} already done. Nothing to monitor.")
        return 0

    run_id = state["run_id"]
    run = gh_api("GET", f"/repos/{REPO}/actions/runs/{run_id}")
    if not run:
        print(f"Could not fetch run {run_id} (API error), will retry next minute.")
        return 0

    status = run["status"]
    conclusion = run.get("conclusion")
    prev_status = state.get("last_status")

    if status != prev_status:
        print(f"Run {run_id}: {prev_status} -> {status} "
              f"{f'({conclusion})' if conclusion else ''}")
        state["last_status"] = status

    if status == "completed":
        state["last_conclusion"] = conclusion
        if conclusion == "success":
            state["done"] = True
            save_state(state)
            alert(f"Run {run_id} SUCCEEDED. Production complete: {state['url']}")
            return 0
        # Failed: classify and act.
        jobs = fetch_jobs(run_id)
        if not jobs:
            alert(f"Run {run_id} FAILED but jobs could not be fetched; manual check: {state['url']}")
            save_state(state)
            return 0
        result = classify(jobs)
        alert(f"Run {run_id} FAILED: {result['classification']} — {result['detail']}")
        recovered = auto_recover(state, result)
        if not recovered:
            # Stay registered so the next minute re-checks (in case Hamza
            # fixed it manually), but don't spam: mark alerted.
            state["alerted"] = True
        save_state(state)
        return 0

    save_state(state)
    print(f"Run {run_id}: {status} (no change)")
    return 0


if __name__ == "__main__":
    sys.exit(check_once())
