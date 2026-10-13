#!/usr/bin/env python3
"""Production monitor v3 — watches ALL GitHub workflows, not just render.

Queries the GitHub API for the latest runs across ALL workflows on the branch
and reports status changes. Fixes v2's blind spot: CI failures (test.yml,
ci.yml) were never monitored, only render-production.yml.

Usage:
  python3 monitor_v3.py [--watch] [--run-id ID]

  --watch: continuous monitoring, reports on changes
  --run-id: monitor a specific run (default: latest across all workflows)
"""
import sys, os, json, time, argparse
sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import add_surrogate_to_request
import urllib.request, urllib.error

REPO = "wastor453-ux/rendering-production"
BRANCH = "p4-4-ccdecbc-readiness"
STATE_FILE = os.path.expanduser("~/workspace/crackit/production/.production-state/monitor_v3.json")

# Workflows to monitor (all of them on the branch)
MONITORED_WORKFLOWS = [
    "render-production.yml",  # Main render pipeline
    "test.yml",               # CI Tests (pytest)
    "ci.yml",                 # CI (visual contracts)
    "cleanup-runs.yml",       # Cleanup automation
]

def api_get(path, retries=3):
    """GET with retry and exponential backoff. Raises after all retries fail.
    
    Does NOT retry 404s — those are permanent (missing workflow/run).
    """
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(f"https://api.github.com{path}")
            req.add_header("Accept", "application/vnd.github+json")
            req.add_header("User-Agent", "cosmo-monitor-v3")
            add_surrogate_to_request(req, "custom.github", allowed_hosts=["api.github.com"])
            return json.load(urllib.request.urlopen(req, timeout=30))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise  # Don't retry 404s
            last_err = e
            if attempt < retries - 1:
                wait = 2 ** attempt
                print(f"API retry {attempt+1}/{retries} for {path}: {e}", file=sys.stderr)
                time.sleep(wait)
        except Exception as e:
            last_err = e
            if attempt < retries - 1:
                wait = 2 ** attempt
                print(f"API retry {attempt+1}/{retries} for {path}: {e}", file=sys.stderr)
                time.sleep(wait)
    raise last_err

def get_latest_runs():
    """Get recent runs for EACH monitored workflow on the branch.
    
    Fetches up to 5 recent runs per workflow (not just 1) so fast runs
    that start and finish between checks are not missed.
    """
    runs = []
    errors = []
    for wf in MONITORED_WORKFLOWS:
        try:
            d = api_get(f"/repos/{REPO}/actions/workflows/{wf}/runs?per_page=5&branch={BRANCH}")
            count = 0
            for r in d.get("workflow_runs", []):
                if r.get("head_branch") == BRANCH:
                    r["_workflow_file"] = wf
                    runs.append(r)
                    count += 1
                    if count >= 3:  # Track 3 most recent per workflow
                        break
        except urllib.error.HTTPError as e:
            if e.code == 404:
                # Workflow not present on this branch (e.g. cleanup-runs.yml
                # exists locally but was never pushed). Not an error, not a
                # coverage gap — there is nothing to monitor.
                print(f"Info: {wf} not found on branch {BRANCH} (404) — skipping",
                      file=sys.stderr)
                continue
            errors.append(f"{wf}: HTTP {e.code}")
        except Exception as e:
            errors.append(f"{wf}: {e}")
    if errors:
        print(f"Monitor warnings: {'; '.join(errors)}", file=sys.stderr)
    return runs

def get_run(run_id):
    return api_get(f"/repos/{REPO}/actions/runs/{run_id}")

def get_jobs(run_id):
    d = api_get(f"/repos/{REPO}/actions/runs/{run_id}/jobs?per_page=50")
    return d.get("jobs", [])

def classify_render(jobs):
    """Classify render-production workflow outcome from job statuses."""
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
    if plan_c == "skipped" and asm_c == "skipped":
        test = by_name.get("sfx-chain-test", {})
        iv = by_name.get("install-verify", {})
        if test.get("conclusion") == "success":
            return "TEST_SUCCESS", "sfx-chain-test passed; production jobs skipped by design"
        if test.get("conclusion") == "failure":
            return "TEST_FAILURE", "sfx-chain-test failed"
        if iv.get("conclusion") == "success":
            return "INSTALL_VERIFY_SUCCESS", "install-verify passed; production jobs skipped by design"
        if iv.get("conclusion") == "failure":
            return "INSTALL_VERIFY_FAILURE", "install-verify failed"
        return "UNKNOWN", f"test-mode run"
    if asm_c == "skipped" and plan_c != "skipped":
        return "ASSEMBLY_SKIPPED", "assemble was skipped; check workflow condition"
    return "UNKNOWN", f"plan={plan_c} assemble={asm_c} renders={len(renders)}"

def classify_ci(jobs, workflow_name):
    """Classify CI workflow outcome."""
    failed = [j for j in jobs if j.get("conclusion") == "failure"]
    if failed:
        names = ", ".join(j["name"] for j in failed[:3])
        return "CI_FAILURE", f"{workflow_name}: {len(failed)} job(s) failed ({names})"
    
    # Check if all completed successfully
    completed = [j for j in jobs if j.get("conclusion") in ("success", "skipped")]
    if completed and len(completed) == len(jobs):
        return "CI_SUCCESS", f"{workflow_name}: all jobs passed"
    
    return "CI_UNKNOWN", f"{workflow_name}: status unclear"

def classify(run, jobs):
    """Classify based on workflow type."""
    wf = run.get("_workflow_file", "")
    if wf == "render-production.yml":
        return classify_render(jobs)
    elif wf in ("test.yml", "ci.yml"):
        return classify_ci(jobs, wf)
    elif wf == "cleanup-runs.yml":
        failed = [j for j in jobs if j.get("conclusion") == "failure"]
        if failed:
            return "CLEANUP_FAILURE", "cleanup workflow failed"
        return "CLEANUP_SUCCESS", "cleanup completed"
    else:
        return "UNKNOWN", f"unmonitored workflow: {wf}"

def load_state():
    """Load state with corruption recovery. Returns {} on any error."""
    try:
        with open(STATE_FILE) as f:
            data = json.load(f)
        # Validate it's a dict
        if not isinstance(data, dict):
            print("State file corrupted (not a dict), starting fresh", file=sys.stderr)
            return {}
        return data
    except FileNotFoundError:
        return {}
    except (json.JSONDecodeError, OSError) as e:
        # Backup corrupted file and start fresh
        try:
            backup = STATE_FILE + ".corrupt"
            os.rename(STATE_FILE, backup)
            print(f"State file corrupted, backed up to {backup}", file=sys.stderr)
        except:
            pass
        return {}

def save_state(s):
    """Atomic state save (write temp + rename) to prevent corruption."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    # Keep the most recent runs per workflow (5 each), not a flat global
    # last-30: render-production run IDs (3817...) are numerically older than
    # ci/test IDs (3821...), so a global trim evicted every render-production
    # entry on every save and re-alerted it as "?" the next tick.
    by_wf = {}
    for k, v in s.items():
        by_wf.setdefault(v.get("workflow", "unknown"), {})[k] = v
    trimmed = {}
    for wf, entries in by_wf.items():
        for k in sorted(entries, key=int)[-5:]:
            trimmed[k] = entries[k]
    s = trimmed
    tmp = STATE_FILE + ".tmp"
    try:
        with open(tmp, "w") as f:
            json.dump(s, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.rename(tmp, STATE_FILE)
    except Exception as e:
        print(f"Failed to save state: {e}", file=sys.stderr)
        try:
            os.unlink(tmp)
        except:
            pass

def check_once(run_id=None):
    """Check all workflows and report status changes."""
    if run_id:
        run = get_run(run_id)
        run["_workflow_file"] = "manual"
        runs = [run]
    else:
        runs = get_latest_runs()
    
    if not runs:
        print("No runs found")
        return
    
    state = load_state()
    alerts = []
    
    for run in runs:
        rid = str(run["id"])
        wf = run.get("_workflow_file", "unknown")
        status = run["status"]
        conclusion = run.get("conclusion")
        
        prev = state.get(rid, {})
        changed = (prev.get("status") != status or prev.get("conclusion") != conclusion)
        
        if changed or not prev:
            try:
                jobs = get_jobs(rid)
                cls, msg = classify(run, jobs)
            except Exception as e:
                cls, msg = "CHECK_FAILED", f"could not classify: {e}"
            
            print(f"[{wf}] Run {rid}: {prev.get('status', '?')} -> {status} ({conclusion})")
            print(f"  Classification: {cls} — {msg}")
            print(f"  URL: https://github.com/{REPO}/actions/runs/{rid}")
            
            # Alert conditions
            is_failure = conclusion == "failure" or cls in (
                "PLAN_FAILURE", "CHUNK_FAILURE", "ASSEMBLY_DEATH", 
                "ASSEMBLY_SKIPPED", "TEST_FAILURE", "CI_FAILURE", 
                "CLEANUP_FAILURE", "INSTALL_VERIFY_FAILURE"
            )
            is_success = conclusion == "success" and cls not in (
                "TEST_SUCCESS", "INSTALL_VERIFY_SUCCESS", "CLEANUP_SUCCESS", "CI_SUCCESS"
            )
            
            if is_failure or is_success:
                alert_line = f"ALERT: [{wf}] Run {rid} {cls}: {msg}"
                print(alert_line)
                print(f"  URL: https://github.com/{REPO}/actions/runs/{rid}")
                alerts.append(alert_line)
            
            state[rid] = {
                "status": status, 
                "conclusion": conclusion, 
                "classification": cls,
                "workflow": wf,
            }
        else:
            print(f"[{wf}] Run {rid}: no change ({status}/{conclusion})")
    
    save_state(state)

    # Health check: report monitor's own status
    workflows_seen = set(r.get("_workflow_file", "?") for r in runs)
    print(f"Monitor health: OK — checked {len(runs)} runs across {len(workflows_seen)} workflows "
          f"({', '.join(sorted(workflows_seen))}), {len(alerts)} alert(s)", file=sys.stderr)
    return alerts

def watch(poll_secs=60):
    """Continuous monitoring."""
    print(f"Watching {REPO} branch {BRANCH} (all workflows) every {poll_secs}s")
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
