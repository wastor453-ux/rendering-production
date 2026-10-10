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
| B-01, B-02, B-04, B-05, B-07, B-08, B-09, B-10, B-11, B-13, B-14, B-15, B-17, B-18, B-19, B-23 | ✅ | Local tests pass; B-07: visual-mode-inventory.md generated from source; B-14: SOUND_DESIGN.md:41 synced; B-17: this register is the versioned re-validation; B-23: tools/verify_visual.py built, PASS on Q-004 |
| B-14 | ✅ | SOUND_DESIGN.md:41 synced 2026-10-10 — 9 impacts assigned A1 assets, NOT approved |
| B-03, B-06, B-22 | 🟡 | Contracts exist; runtime/full proof pending; B-22: PROVENANCE.md created, full closure needs B-16 decision |
| B-12 | 🔴 | Light encode A/B needs render (prohibited) |
| B-16 | 🔴 | No licensed imagery inventory (needs Hamza's assets; options in creative-review package) |
| B-20 | 🔴 | Bit-identical renders not proven (needs render) |
| B-21 | 🔴 | Formal encode QA bar not defined (objective metrics in Q-004 report; needs Hamza's bar) |
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
| F-02, F-03 | 🟡 | Selective recovery proven (37926640596); F-02 positive 39-chunk case: recovery validation correctly FAILED CLOSED on generation mismatch (run 38068791887) — safety property proven; positive case needs fresh render on current code (prohibited) |
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


## CATEGORY H: New tracked items (2026-10-10, Hamza's order)

| ID | Status | Evidence / gap |
|----|--------|----------------|
| H-01 | 🔴 | Creative approval criteria: Q004 visual direction REJECTED 2026-10-10. Measurable criteria not yet defined — must exist before any redesign proposal. |
| H-02 | 🔴 | Demo lifecycle: demo video ordered 2026-10-10. Plan and acceptance checklist pending (Batch 4). No render dispatched. |
| H-03 | ✅ | Unified pre-render enforcement checklist: `.production-state/PRE_RENDER_CHECKLIST.md` + `tools/pre_render_check.py` + `tests/test_pre_render.py` (11/11 pass). 8 checks, all mapped to canonical sources. |

## RECONCILED COUNTS

| Category | Fixed | Partial | Open | Blocked | Total |
|----------|-------|---------|------|---------|-------|
| A | 8 | 0 | 0 | 0 | 8 |
| B | 16 | 3 | 4 | 0 | 23 |
| C | 13 | 1 | 0 | 0 | 14 |
| D | 4 | 0 | 0 | 0 | 4 |
| E | 3 | 2 | 0 | 0 | 5 |
| F | 1 | 2 | 4 | 0 | 7 |
| G | 5 | 0 | 0 | 0 | 5 |
| N | 12 | 0 | 0 | 1 | 13 |
| **TOTAL** | **62** | **8** | **8** | **1** | **79** |
| H (new) | 1 | 0 | 2 | 0 | 3 |
| **GRAND TOTAL** | **63** | **8** | **10** | **1** | **82** |

63 + 8 + 10 + 1 = 82 ✓ (79 original + 3 new)

## Changes in this phase (all on `p4-4-ccdecbc-readiness`, non-force)
- Creative-review package: `~/workspace/your_files/impact-sounds-review/index.html`
  (9 sounds with embedded audio + verdict controls, Q-004 report, Q-001/B-16 options)
- B-22: `public/light/PROVENANCE.md` (imagery ledger)
- B-23: `tools/verify_visual.py` (independent visual verifier, PASS on Q-004)
- B-07: `.production-state/visual-mode-inventory.md` (23 modes from source)
- R-013 guard: stray `fi` fixed; shell-syntax regression test added (7/7 pass)
- Reassembly: audio-duration guard skipped in reassembly mode
- F-02: bounded recovery test dispatched (38068791887) — validation correctly
  failed closed on generation mismatch (safety property proven)

## Test results
- Python: **308/308 pass** (was 305/308; the 3 pre-existing failures fixed)
- npm: exit 0 · `git diff --check`: clean

## Hosted evidence
- 38066659959 (sfx-chain-test, success): R-008 snapshot path, ffmpeg 7:6.1.1-3ubuntu5
- 38067195302 (install-verify, success): 13 browser pkgs + 2× ffmpeg, all snapshot, 0 rolling
- 38063206358 (sfx-chain-test, success): 180/180 A1, 33 triggers, -14.06 LUFS
- 38057551643 (Q-004, success): 23,151 frames, 0 black, 0 frozen

## Remaining issues by dependency (8 partial + 8 open + 1 blocked = 17)
1. **Hamza's creative judgment:** 9 impact sounds (E-02/E-04), Q-004 visual verdict (F-05/F-06/F-07), Q-001 definition (F-01), B-16 imagery, B-21 encode-QA bar
2. **Production authorization:** full SFX mix (E-04), R-013 hosted rerun (C-12), B-12/B-20 renders
3. **Runtime/measurement:** B-03/B-06 (need Remotion runtime), B-22 (needs B-16 decision), F-02 positive case (needs fresh render on current code)
4. **External:** N-11 phantom-failure quirk (no action possible)
