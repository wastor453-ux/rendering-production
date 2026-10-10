# Batch 2 Findings — Machine-Solvable Issues

## B-03 / B-06: Runtime dependencies

**Status:** Cannot close without Remotion runtime rendering.

**What they need:**
- B-03: Visual contract verification against rendered frames
- B-06: Full visual proof (not just static checks)

**Why blocked:** Both require actual Remotion renders to verify. The contracts
exist (test_visual_identity.py, verify_visual.py), but they validate static
properties. Runtime verification means rendering frames and checking pixel output.

**Prepared (no render dispatched):**
- `tools/verify_visual.py` — static visual verifier (PASS on Q-004)
- `tests/test_visual_identity.py` — 2/2 pass

**Accurate label:** 🟡 PARTIAL — contracts exist, runtime proof pending.
Cannot advance without authorized render.

---

## B-12 / B-20: Verification prep (no production dispatch)

**B-12: Light encode A/B needs render**
- **Prepared:** A/B test script structure documented in
  `.production-state/b12_ab_test_plan.md`
- **Blocked:** Requires two renders with different encode settings.
- **Accurate label:** 🔴 OPEN — needs render (prohibited)

**B-20: Bit-identical renders not proven**
- **Prepared:** Checksum comparison script `tools/verify_bit_identical.py`
  (compares two render outputs frame-by-frame)
- **Blocked:** Requires two renders of same input.
- **Accurate label:** 🔴 OPEN — needs render (prohibited)

---

## R-013 / F-02: Evidence labeling

**R-013 (C-12): Hosted `github.run_attempt` binding**
- **Local proof:** 6/6 guard logic tests pass. Stray `fi` fixed.
- **Hosted proof:** DEFERRED — needs production rerun.
- **Accurate label:** 🟡 PARTIAL — local proven, hosted deferred.
- **Cannot close** without hosted run.

**F-02: Selective recovery positive case**
- **Proven:** Safety property (failed closed on generation mismatch, run 38068791887)
- **Not proven:** Positive 39-chunk recovery on current code (needs fresh render)
- **Accurate label:** 🟡 PARTIAL — safety proven, positive case needs render.
- **Cannot close** without authorized render.

---

## B-21: Proposed Encode-QA Standard

**For Hamza's review** (not yet approved):

| Metric | Proposed threshold | Source |
|--------|-------------------|--------|
| Resolution | 1920×1080 exact | VISUAL_BRAIN §13 |
| Frame count | Matches beat timeline | D-01..D-04 |
| Black frames | 0 | Q-004 report |
| Frozen frames | 0 | Q-004 report |
| Text sharpness | No blur on reading layer | VISUAL_BRAIN §8 |
| Color accuracy | Tokens match design_tokens.json | VISUAL_BRAIN §9 |
| Audio sync | SFX peak ±1 frame of visual impact | SOUND_DESIGN.md |

**Status:** Proposed, awaiting Hamza's bar. Cannot finalize without his standard.

---

## Summary

| Issue | Can close now? | Blocker |
|-------|---------------|---------|
| B-03 | No | Needs Remotion runtime render |
| B-06 | No | Needs Remotion runtime render |
| B-12 | No | Needs render (prohibited) |
| B-20 | No | Needs render (prohibited) |
| R-013 | Partial only | Hosted proof deferred |
| F-02 | Partial only | Positive case needs render |
| B-21 | Proposal only | Needs Hamza's approval |

**Honest assessment:** 0 of 7 can fully close without a render or Hamza's input.
All are accurately labeled. No false closures.
