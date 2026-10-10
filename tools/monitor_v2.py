#!/usr/bin/env python3
"""Production monitor v2 — watches GitHub directly, no stale state files.

Queries the GitHub API for the latest run on the branch and reports
status changes. No manual active_run.json updates needed.

Usage:
  python3 monitor_v2.py [--watch] [--run-id ID]

  --watch: continuous monitoring, reports on changes
  --run-id: monitor a specific run (default: latest on branch)
"""
import sys, os, json, time, argparse
sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import add_surrogate_to_request
import urllib.request, urllib.error

REPO = "wastor453-ux/rendering-production"
BRANCH = "p4-4-complete-preproduction-closure"
WORKFLOW = "render-production.yml"
STATE_FILE = os.path.expanduser("~/workspace/crackit/demo-video/.production-state/monitor_v2.json")

def api_get(path):
    req = urllib.request.Request(f"https://api.github.com{path}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "cosmo-monitor-v2")
    add_surrogate_to_request(req, "custom.github", allowed_hosts=["api.github.com"])
    return json.load(urllib.request.urlopen(req, timeout=30))

def get_latest_run():
    """Get the most recent run on the branch."""
    d = api_get(f"/repos/{REPO}/actions/workflows/{WORKFLOW}/runs?per_page=5&branch={BRANCH}")
    runs = d.get("workflow_runs", [])
    # Filter to runs on our branch
    for r in runs:
        if r.get("head_branch") == BRANCH:
            return r
    return runs[0] if runs else None

def get_run(run_id):
    return api_get(f"/repos/{REPO}/actions/runs/{run_id}")

def get_jobs(run_id):
    d = api_get(f"/repos/{REPO}/actions/runs/{run_id}/jobs?per_page=50")
    return d.get("jobs", [])

def classify(jobs):
    """Classify run outcome from job statuses."""
    by_name = {}
    for j in jobs:
        n = j["name"]
        if n not in by_name:
            by_name[n] = j
    
    plan = by_name.get("plan", {})
    assemble = by_name.get("assemble", {})
    renders = [j for n, j in by_name.items() if n.startswith("render-chunk")]
    
    plan_c = plan.get("conclusion")
    asm_c = assemble.get("conclusion")
    render_failed = [j for j in renders if j.get("conclusion") == "failure"]
    
    if plan_c == "failure":
        return "PLAN_FAILURE", "plan job failed; no chunks trustworthy"
    if render_failed:
        return "CHUNK_FAILURE", f"{len(render_failed)} chunks failed"
    if plan_c == "success" and asm_c == "failure":
        return "ASSEMBLY_DEATH", "chunks OK, assembly failed; reassemble with zero re-render"
    if plan_c == "success" and asm_c == "success":
        return "SUCCESS", "master produced"
    if asm_c == "skipped":
        return "ASSEMBLY_SKIPPED", "assemble was skipped; check workflow condition"
    return "UNKNOWN", f"plan={plan_c} assemble={asm_c} renders={len(renders)}"

def load_state():
    try:
        return json.load(open(STATE_FILE))
    except:
        return {}

def save_state(s):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    json.dump(s, open(STATE_FILE, "w"), indent=2)

def check_once(run_id=None):
    """Check once and report if status changed."""
    if run_id:
        run = get_run(run_id)
    else:
        run = get_latest_run()
    
    if not run:
        print("No runs found")
        return
    
    rid = str(run["id"])
    status = run["status"]
    conclusion = run.get("conclusion")
    
    state = load_state()
    prev = state.get(rid, {})
    
    changed = (prev.get("status") != status or prev.get("conclusion") != conclusion)
    
    if changed or not prev:
        jobs = get_jobs(rid)
        cls, msg = classify(jobs)
        
        print(f"Run {rid}: {prev.get('status', '?')} -> {status} ({conclusion})")
        print(f"  Classification: {cls} — {msg}")
        print(f"  URL: https://github.com/{REPO}/actions/runs/{rid}")
        
        if conclusion in ("failure", "success") or cls in ("ASSEMBLY_DEATH", "PLAN_FAILURE", "CHUNK_FAILURE", "ASSEMBLY_SKIPPED"):
            print(f"ALERT: Run {rid} {cls}: {msg}")
        
        state[rid] = {"status": status, "conclusion": conclusion, "classification": cls}
        # Keep only last 10 runs
        for k in list(state.keys())[:-10]:
            del state[k]
        save_state(state)
    else:
        print(f"Run {rid}: no change ({status})")

def watch(poll_secs=60):
    """Continuous monitoring."""
    print(f"Watching {REPO} branch {BRANCH} every {poll_secs}s (Ctrl+C to stop)")
    while True:
        try:
            check_once()
        except Exception as e:
            print(f"Check failed: {e}")
        time.sleep(poll_secs)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--watch", action="store_true")
    p.add_argument("--run-id", type=str, default=None)
    p.add_argument("--interval", type=int, default=60)
    a = p.parse_args()
    
    if a.watch:
        watch(a.interval)
    else:
        check_once(a.run_id)
