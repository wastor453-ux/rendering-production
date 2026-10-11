# N-11: Phantom-Failure Platform Quirk — Documented Limitation

**Status:** BLOCKED (external). Documented 2026-10-11. No fix possible.
**Note:** This documents the limitation and containment. It does not fix the
underlying platform behavior.

## Observed limitation
GitHub Actions occasionally reports a workflow run as failed when the underlying
work actually succeeded ("phantom failure"). This is a platform-side quirk,
not a repository bug.

## Evidence
- Q-004 (run 38057551643) was flagged with anomalous status but produced a
  genuine, verified successful master (23,151 frames, 0 black, 0 frozen).

## Containment (not a fix)
1. **Never trust status alone** — always verify artifacts exist and are valid
   before declaring success or failure.
2. **The production monitor** (`tools/monitor_v2.py`) classifies by job-level
   evidence, not just the top-level conclusion.
3. **The chunk ledger** (`build_ledger.py`) gates assembly on COMPLETE manifest,
   independent of run status signals.
4. If a run shows phantom failure: download artifacts, verify frame count and
   integrity, then record the verified outcome in the register.

## Why no fix is attempted
The quirk originates in GitHub's status reporting infrastructure. No repository
change can prevent it. Containment via artifact verification is the correct
response.
