# CONSOLIDATED ACCEPTANCE MATRIX — CrackIt production readiness
Date: 2026-10-10 · Branch: p4-4-complete-preproduction-closure · HEAD: 0f0b9e6
Source: integrated workstreams A–F gap analyses (local only — no production execution).

Columns: **CC** = code-complete · **IT** = integration-tested · **PP** = production-proven.
Rule: a unit-test pass ≠ integration ≠ production proof. "GREEN locally" means local evidence only.

| Capability | CC | IT | PP | Status |
|---|---|---|---|---|
| Composition contract (24 ids, roles, exemptions) | ✅ | ✅ gate [6] in validate_dispatch + plan.py + q002 workflow step; 27/27 unit | ❌ no production dispatch through it yet | GREEN locally, uncommitted |
| Beat gate [7] (canonical schema at dispatch) | ✅ | ✅ checked-in beats proven: ProductionBeats/B6A/B6B/ChainTest 0 violations; P3Rehearsal = exactly 8 pinned | ❌ | GREEN locally, uncommitted; debt pinned not hidden. Known gap: gate fails OPEN (skips) when schema file absent from checkout |
| Beat-artifact provenance recording | ✅ (phase 2) | ✅ unit | ❌ | Provenance "checked-in" recorded by gate [7]; compiler disconnected |
| Evidence independence (buildEvidence from payloads, fail-closed "none") | ✅ | ✅ 14/14 node counterexample tests vs REAL builder; both TSX renderers wired | ❌ no rendered-frame proof | GREEN locally, uncommitted |
| Selector authority (D2) | ⚠️ log-only | ✅ 7/7 bundle tests (log-only); select.test.ts 18/18 but orphan (no runner) | ❌ | PARTIAL: plan-authority + challenge + disputed flag done; **R-4 throw NOT active** (needs Hamza's order) |
| Token sync (design_tokens.json → tokens.ts) | ✅ codegen (phase 2) | ✅ sync test (phase 2) | n/a | Values in sync; automated enforcement now exists locally |
| SFX chain | ✅ A1 library canonical (180/180 SHA-verified) | ⚠️ migration test 14/14; compile_sfx_triggers.py DISCONNECTED and interface-incompatible; mix_*.py route retired pools | ❌ | Library proven; production wiring disconnected; no behavior change authorized |
| verify-render wiring (R-8 / D4) | ✅ script (trial + production modes) | ⚠️ warn-only step in production workflow (phase 2); blocking enforcement point in q002-test (conditional, pending harness) | ❌ | Partially wired; audio model stale; M1–M4 gates don't exist |
| Recovery / reassembly | ✅ classify + ledger + API-dispatchable reassemble | ✅ 19/19 safety + 41/41 recovery unit; 2 stale-contract failures (test_recovery_split/decisive — pre-existing on pristine HEAD, encode abandoned invariant) | ⚠️ Q-002 selective recovery proven hosted (run 37926640596); 39-chunk assembly-only NOT proven hosted | Partially proven |
| Q-002 | — | — | ✅ proven 19/20 hosted selective recovery | PROVEN (historical) |
| Q-003 | — | — | ⚠️ historical benchmarks only; no new production benchmark authorized | NOT RE-PROVEN |
| Q-004 (full 13.4-min HousingBroke) | — | — | ❌ | OPEN — no green run; run 37990979375 built 23,151-frame intermediate but concluded failed |
| A-001 (intermediate ≠ master naming) | ✅ | ✅ | — | FIXED AND TESTED LOCALLY |
| A-002 (canonical post path + SFX-complete final mix) | ⚠️ | ❌ | ❌ | OPEN — blocked on Q-004 green + audio authorization |
| A-003 (SFX event timing verification) | ⚠️ laws documented | ❌ | ❌ | OPEN — timing laws documented, no machinery |
| 23-mode gate | ✅ 23/23 in registry | ✅ reachability; contact sheet + report exist | ❌ TS runtime rendering not proven | Wiring proven; **1.28× universal-scale NOT promoted** (awaiting Hamza's verdict) |
| R-008 (Ubuntu package reproducibility) | ❌ | ❌ | ❌ | OPEN — platform limitation |
| R-011 (seam inspection) | ⚠️ | ❌ hosted auth blocked | ❌ | OPEN — artifact-download auth |
| R-013 (stale rerun guard) | ✅ guard exists | ❌ no hosted integration test | ❌ | OPEN |
| REG-001 (register reconciliation) | — | — | — | OPEN |
| P3Rehearsal data | ❌ | ✅ pinned: exactly 8 violations | n/a | BLOCKED — 6× music_intensity (no derivation rule), b2 'allocation' ∉ enum, b6 'emphasize' ∉ enum |
| npm test chain | ⚠️ | ❌ masks failures via tail; broken final grep → false exit 1 | n/a | BROKEN (uncommitted edit) — needs repair pass |
| CI test job | ❌ | ❌ | ❌ | NO workflow runs pytest; local CLI/Studio policy-only bypasses |

## What is genuinely solid
Composition contract + beat gate (+ provenance) + evidence independence + recovery unit tests are locally green against real implementations.

## What is not
Nothing above has production proof except Q-002's historical selective recovery. The gates that would make regressions hard (CI pytest, verify-render blocking enforcement, selector throw, token codegen) are newly wired locally but unproven in production. Thumbnails paused; P3 rehearsal stopped; no SFX behavior change authorized.
