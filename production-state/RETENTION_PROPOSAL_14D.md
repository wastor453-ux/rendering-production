# Chunk-Retention Proposal — 14 days (for Hamza's review — NOT applied)

## Problem

The assembly-only recovery law depends on chunk artifacts, but chunks carry
the shortest retention fuse in the system:

| Artifact | Retention | Role in recovery |
|---|---|---|
| Chunk mp4 + manifest | **3 days** (`render-production.yml` chunk upload) | THE recovery material |
| Job manifest | 30 days | needed to reassemble |
| Chunk ledger | 90 days | proves completeness |
| Master | 30 days | final output |

The ledger can prove for 90 days exactly which chunks a reassembly needs —
but after day 3 the chunks themselves are gone, so the proof is unactionable.
Recovery is currently a 3-day capability wearing a 90-day ledger.

## Proposal

Change the chunk upload in `.github/workflows/render-production.yml` from
`retention-days: 3` to `retention-days: 14`. One line. Nothing else changes.

```diff
-          retention-days: 3
+          retention-days: 14
```

(Exact step: the `render-chunk` job's chunk artifact upload, ~line 596.)

## Measured storage impact

Measured from run 38043130687 (real HousingBroke content, CRF 18, 1080p30):
616,743 bytes for 300 frames ≈ **2.06 KB/frame**.

- One Q-004-scale run (23,151 frames): ≈ **48 MB** of chunk artifacts.
- 10 successful runs retained (the cleanup policy steady state): ≈ **480 MB**.
- Small verification runs (300f): ≈ 0.6 MB each — negligible.
- Failed runs are exempt from count-based cleanup (recovery protection) but
  still expire via this 14-day upload retention, so accumulation is bounded
  by failures-within-14-days, not unbounded.

Check the repo's current storage meter under Settings → Billing before
approving; the numbers above are the cost side.

## Longer retention for unresolved failures

For a failed run under active investigation or awaiting a reassembly decision,
14 days may still be short. Options, in increasing order of machinery:

1. **Manual (no code):** download the failed run's chunk artifacts locally
   before they expire — they are ordinary zip files; the ledger + manifests
   make them re-uploadable later.
2. **Per-run override (no code):** none exists — `retention-days` is fixed at
   upload time and cannot be extended afterward. This is a GitHub platform
   limitation, not something to work around with another workflow.
3. **Not proposed:** a "pin this run" mechanism would be new infrastructure;
   deferred unless the manual path proves insufficient.

Recommendation: approve the one-line 14-day change; use the manual path for
the rare unresolved failure. Revisit only if a real investigation outlives it.

## Not in scope

No change to the 90-day ledger, 30-day master/manifest, or the (inactive)
cleanup workflow. No deletions, no activation.
