# R-013 Hosted-Proof Limitation (2026-10-10)

## What is proven
- Guard logic extracted to `.github/scripts/rerun_guard.sh` and regression-tested
  (6/6 tests: attempt 1 passes, attempts 2/5 fail closed, invalid input fails closed).
- Workflow binds `github.run_attempt` → guard argument (verified by test).
- Guard is the first plan step after checkout, before any installation,
  rendering, or publication (verified by test).

## What is NOT proven (deferred)
A faithful hosted test of `github.run_attempt` itself. GitHub controls the
attempt number; a fresh dispatch always has attempt=1. The only way to observe
attempt=2 is to rerun an existing workflow run. Rerunning a test-mode run
(sfx_chain_test) does not execute `plan`, so the guard would not be exercised.
Rerunning a production run is forbidden by standing order (no production reruns).

## Safest hosted procedure (when authorized)
1. Hamza authorizes a rerun of a completed production run.
2. Click "Re-run all jobs" on that run.
3. Expected: attempt 2 fails at the "R-013 stale-rerun guard" step with
   "FATAL: R-013 - This is run attempt 2 (a rerun)" before any install/render.
4. Capture run ID, attempt number, and guard log as proof.

Status: R-013 LOGIC PROVEN (local) / HOSTED PROOF DEFERRED.
