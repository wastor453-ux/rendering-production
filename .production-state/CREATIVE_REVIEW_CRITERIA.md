# Creative Review Criteria (Measurable)

**Status:** Proposed 2026-10-10. Awaiting Hamza's approval.
**Context:** Q004 visual direction REJECTED 2026-10-10. No further visual
proposals until criteria are locked.

## Why measurable?

"This looks better" is not a gate. Every criterion below has a test or
measurement. If it can't be measured, it's not a criterion — it's a preference.

---

## Criteria

### 1. Variety Law Compliance
- **Measure:** No more than 2 consecutive typography-led beats.
- **Test:** `tools/pre_render_check.py::check_variety()`
- **Pass:** Beat timeline passes automated check.

### 2. Data Visualization Coverage
- **Measure:** ≥70% of beats with measurable statistics use a data viz mode
  (chart, comparison, metric grid) instead of plain headline.
- **Test:** Manual audit of beat_timeline.json (automated check pending).
- **Pass:** Coverage ≥70%.

### 3. Canvas Utilization
- **Measure:** Content uses ≥60% of 1920px width on average across beats.
- **Test:** Render stills at beat midpoints; measure content bounding box.
- **Pass:** Mean utilization ≥60%, no beat <40%.

### 4. Visual Mode Diversity
- **Measure:** ≥5 distinct visual modes across a 7-scene video.
- **Test:** Count unique `visual_mode` in beat_timeline.json.
- **Pass:** ≥5 modes.

### 5. Muted Comprehension
- **Measure:** With audio muted, viewer can identify the main change/claim
  in each beat from visuals alone.
- **Test:** Human review (Hamza or delegate) of muted stills.
- **Pass:** ≥80% of beats comprehensible without audio.

### 6. Typography Hierarchy
- **Measure:** Clear distinction between headline (≥64px), supporting (≤36px),
  and label (≤24px). No overlap. No clipping at canvas edges.
- **Test:** Automated still analysis + human spot-check.
- **Pass:** Zero overlap, zero clipping in sampled frames.

---

## Q004 Verdict (Recorded)

**REJECTED 2026-10-10 by Hamza.**

Failures against above criteria:
1. Variety: 4-5 typography beats in a row (FAIL)
2. Data viz: ~20% coverage, mostly big numbers (FAIL)
3. Canvas: ~35% utilization, content huddles left (FAIL)
4. Modes: ~3 distinct modes (FAIL)
5. Muted: Headlines readable but relationships unclear (PARTIAL)
6. Typography: 3 defects found and fixed (was FAIL, now PASS)

**No visual redesign work begins until Hamza approves these criteria
or provides his own.**
