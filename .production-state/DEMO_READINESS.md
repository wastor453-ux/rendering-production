# Demo Readiness Report (2026-10-10)

## Remaining issues: 19 total

### Need Hamza's decision (11)
| ID | Issue | What Hamza must do |
|----|-------|-------------------|
| E-02 | 9 impact sounds | Listen in review package, approve/reject each |
| F-01 | Q-001 undefined | Define what Q-001 is |
| F-05/06/07 | Q-004 verdict | DONE — rejected 2026-10-10 |
| B-16 | No imagery | Provide assets or pick from options |
| B-21 | Encode QA bar | Approve proposed standard or set own |
| H-01 | Creative criteria | Approve proposed criteria or provide own |
| E-04 | Full SFX mix | Authorize or keep disabled |

### Need render authorization (5)
| ID | Issue | Blocker |
|----|-------|---------|
| B-12 | Encode A/B test | Needs 2 renders |
| B-20 | Bit-identical proof | Needs 2 renders |
| B-03 | Runtime verification | Needs Remotion render |
| B-06 | Full visual proof | Needs Remotion render |
| F-02 | Recovery positive case | Needs fresh render |

### Partial (2)
| ID | Status |
|----|--------|
| R-013 | Local proven (6/6), hosted deferred |
| C-12 | Same as R-013 |

### Blocked (1)
| ID | Status |
|----|--------|
| N-11 | Platform quirk, no action possible |

---

## Demo plan

**Objective:** Short demo video to find issues before committing to full visual redesign.

**Scope:**
- 60-90 seconds (not full 13 minutes)
- 2-3 scenes (not all 7)
- Current code (with 3 visual defects fixed)
- No SFX mix (with_sfx_mix: false)
- No production workflow (local render only)

**Why short:**
- Faster iteration on visual direction
- Hamza can judge quickly
- Less compute, faster feedback

**Scenes:** H3 (has the fixed defects) + H4 (has $40T fix) + one more.

---

## Short-demo acceptance checklist

Before Hamza reviews the demo:

- [ ] Pre-render gate passes (`python3 tools/pre_render_check.py`)
- [ ] 1920×1080, 30fps confirmed
- [ ] No black frames
- [ ] No frozen frames
- [ ] Text: no overlap, no clipping (spot-check fixed defects)
- [ ] Audio: VO present, no SFX mix (by design)
- [ ] File size reasonable (<500MB for 90s)

After Hamza reviews:

- [ ] Creative verdict recorded (approve direction / reject / revise)
- [ ] Issues found logged in register
- [ ] Next steps defined

---

## Required authorizations (NOT yet given)

1. **Demo render** — Hamza must explicitly authorize
2. **Creative criteria** — Hamza must approve or replace proposal
3. **Visual direction** — No redesign until criteria locked

**No render will be dispatched without explicit authorization.**
