# MASTER ISSUE REGISTER — Consolidated Closure (2026-10-10)

**Scope:** Deduplicated reconciliation of `COSMO_MASTER_ISSUE_LIST.md` (66 items)
plus N-01..N-13 (13 items). **79 unique items.** Statuses assigned by evidence,
not prior labels.

**Legend:** ✅ FIXED (implementation + test/hosted proof) · 🟡 PARTIAL
(implementation exists, proof incomplete) · 🔴 OPEN · ⏸️ BLOCKED (external)

---

## CATEGORY A: Visual Identity (8/8 fixed)

| ID | Status | Evidence |
|----|--------|----------|
| A-01..A-08 | ✅ | Dark brain deleted; 11 scenes migrated; VISUAL_BRAIN v2.0 Permanent; test_visual_identity 2/2 |

## CATEGORY B: Visual Chain (13 fixed / 4 partial / 6 open)

| ID | Status | Evidence / gap |
|----|--------|----------------|
| B-01, B-02, B-04, B-05, B-08, B-09, B-10, B-11, B-13, B-15, B-18, B-19 | ✅ | Local tests pass |
| B-14 | ✅ | SOUND_DESIGN.md:41 synced 2026-10-10 — 9 impacts assigned A1 assets, NOT approved |
| B-03, B-06, B-07, B-17 | 🟡 | Contracts exist; runtime/full proof pending |
| B-12 | 🔴 | Light encode A/B needs render (prohibited) |
| B-16 | 🔴 | No licensed imagery inventory (needs Hamza's assets) |
| B-20 | 🔴 | Bit-identical renders not proven (needs render) |
| B-21 | 🔴 | Material B encode QA not formally measured (Q-004 objective report written; formal QA needs plan) |
| B-22 | 🔴 | Imagery provenance not tracked |
| B-23 | 🔴 | No independent visual verifier |

## CATEGORY C: Infrastructure & Recovery (13 fixed / 1 partial)

| ID | Status | Evidence / gap |
|----|--------|----------------|
| C-01..C-10, C-14 | ✅ | Recovery law, ledger, reassembly proven |
| C-11 (R-008) | ✅ | install_snapshot.sh; runs 38066659959 + 38067195302; 16/16 tests |
| C-13 (R-011) | ✅ | Artifacts 11673718243/11673134490 downloaded; evidence preserved |
| C-12 (R-013) | 🟡 | Guard logic 6/6 tests; hosted `github.run_attempt` binding deferred (needs production rerun) |

## CATEGORY D: Frame & Media (4/4 fixed)

| ID | Status | Evidence |
|----|--------|----------|
| D-01..D-04 | ✅ | Exact 23,151 frames; zero duplicates |

## CATEGORY E: Audio & SFX (3 fixed / 2 partial)

| ID | Status | Evidence / gap |
|----|--------|----------------|
| E-01, E-03, E-05 | ✅ | A1 canonical; triggers compiled; timing preserved |
| E-02 | 🟡 | A1 curation done; 9 impact sounds await Hamza's listening approval |
| E-04 | 🟡 | Mixer + sfx-mix job built (flag-gated, default false); full mix NOT done |

## CATEGORY F: Production Gates (1 fixed / 2 partial / 4 open)

| ID | Status | Evidence / gap |
|----|--------|----------------|
| F-04 | ✅ | Q-004 run 38057551643 green (technical). CREATIVE VERDICT SEPARATE: Hamza ruled below quality, no rerender |
| F-02, F-03 | 🟡 | Selective recovery proven; 39-chunk assembly-only not hosted; benchmarks historical |
| F-01 | 🔴 | Q-001 needs definition (Hamza) |
| F-05, F-06, F-07 | 🔴 | Await Hamza's visual verdict on Q-004 master |

## CATEGORY G: Evidence & Package (5/5 fixed)

| ID | Status | Evidence |
|----|--------|----------|
| G-01..G-05 | ✅ | Checksums, manifests, ZIP verified |

## CATEGORY N: New issues (12 fixed / 1 blocked)

| ID | Status | Evidence / gap |
|----|--------|----------------|
| N-01, N-02, N-03, N-04, N-05, N-06, N-07, N-08, N-09, N-10, N-12, N-13 | ✅ | Guards, validators, A1 vendoring, mixer, verify-report binding |
| N-11 | ⏸️ | Phantom-failure platform quirk; cannot fix; Q-004 was genuine success |

---

## RECONCILED COUNTS

| Category | Fixed | Partial | Open | Blocked | Total |
|----------|-------|---------|------|---------|-------|
| A | 8 | 0 | 0 | 0 | 8 |
| B | 13 | 4 | 6 | 0 | 23 |
| C | 13 | 1 | 0 | 0 | 14 |
| D | 4 | 0 | 0 | 0 | 4 |
| E | 3 | 2 | 0 | 0 | 5 |
| F | 1 | 2 | 4 | 0 | 7 |
| G | 5 | 0 | 0 | 0 | 5 |
| N | 12 | 0 | 0 | 1 | 13 |
| **TOTAL** | **59** | **9** | **10** | **1** | **79** |

59 + 9 + 10 + 1 = 79 ✓

## Changes in this closure batch (all on `p4-4-ccdecbc-readiness`, non-force)
- `de3105ce` — Monitor: classify install-verify dispatches (no false UNKNOWN alert)
- `2b56c539` — Fix 3 pre-existing test failures (push-script FILES + shell env vars);
  B-14 doc sync; Q-004 VISUAL_QUALITY_REPORT.md
- (workspace, not repo) `push_p40_branch.py` FILES completed; `SOUND_DESIGN.md:41` synced

## Test results
- Python: **308/308 pass** (was 305/308; the 3 pre-existing failures fixed)
- npm: exit 0 · `git diff --check`: clean

## Hosted evidence
- 38066659959 (sfx-chain-test, success): R-008 snapshot path, ffmpeg 7:6.1.1-3ubuntu5
- 38067195302 (install-verify, success): 13 browser pkgs + 2× ffmpeg, all snapshot, 0 rolling
- 38063206358 (sfx-chain-test, success): 180/180 A1, 33 triggers, -14.06 LUFS
- 38057551643 (Q-004, success): 23,151 frames, 0 black, 0 frozen

## Remaining issues by dependency
1. **Hamza's creative judgment:** 9 impact sounds (E-02/E-04), Q-004 visual verdict (F-05/F-06/F-07), Q-001 definition (F-01), B-16 imagery assets
2. **Production authorization:** full SFX mix (E-04), R-013 hosted rerun (C-12), B-12/B-20 renders
3. **Measurement plans:** B-21 formal encode QA, B-22 provenance, B-23 verifier, B-03/B-06/B-07/B-17 runtime proofs, F-02 39-chunk recovery
4. **External:** N-11 phantom-failure quirk (no action possible)
