# Demo Scene Options — Comparison

## Scene durations (from src/housing/HousingBroke.tsx)

| Scene | Frames | Duration | Content |
|-------|--------|----------|---------|
| H1 | 2,127 | 70.9s | Hook: rates collapse, prices don't |
| H2 | 1,626 | 54.2s | Mortgage spike 7.45% |
| H3 | 5,448 | 181.6s | Autopsy: 3 forces (has 2 fixed defects) |
| H4 | 3,603 | 120.1s | Debt $40T (has 1 fixed defect) |
| H5 | 3,618 | 120.6s | Freeze |
| H6 | 5,574 | 185.8s | Escape |
| H7 | 1,155 | 38.5s | Close |

## The three fixed defects

1. **H3 text overlap** — supporting line through headline (BEAT 2, ~180s)
2. **H3 clipped headline** — "Three forces hit at once" cut off (~250s)
3. **H4 $40.0T** — decimal noise at rest (~330s)

---

## Option A: H2 + H7 (92.7s)

| Aspect | Detail |
|--------|--------|
| Duration | 54.2 + 38.5 = **92.7s** ✅ fits 60-90s |
| Defects shown | **0 of 3** ❌ |
| New edit logic | No — full scenes, just concatenated |
| Risks | Doesn't demonstrate the fixes; Hamza can't verify the work |

## Option B: H3 excerpt (60s slice)

| Aspect | Detail |
|--------|--------|
| Duration | **60s** (frames 5,400–7,200 of H3) ✅ |
| Defects shown | **2 of 3** (text overlap, clipped headline) ✅ |
| New edit logic | **Yes** — requires a demo composition that renders a frame range, not a full scene. Must handle: audio sync (slice the WAV), beat timing (offset), Sequence alignment. |
| Risks | Excerpt boundaries may cut mid-beat; audio slice needs verification; more engineering than full scenes |

## Option C: Full H3 (181.6s)

| Aspect | Detail |
|--------|--------|
| Duration | **181.6s** (3 minutes) ⚠️ 2× over target |
| Defects shown | **2 of 3** (both H3 defects) ✅ |
| New edit logic | No — existing composition, just render H3 alone |
| Risks | Too long for a "quick demo"; Hamza's time; but zero new code |

## Option D: H3 excerpt + H4 excerpt (90s)

| Aspect | Detail |
|--------|--------|
| Duration | **90s** (60s H3 slice + 30s H4 slice) ✅ |
| Defects shown | **3 of 3** ✅✅✅ |
| New edit logic | **Yes** — two excerpts, two audio slices, transition between them |
| Risks | Most engineering; two slice points to verify; transition needs design |

---

## Recommendation

**Option D** shows all three fixes in 90 seconds, but requires new excerpt logic.

**Option C** is the safest (no new code) but is 3 minutes, not a "demo."

**Option A** is the fastest but proves nothing about the fixes.

**The excerpt logic (B/D) is the real work.** It needs:
1. A `DemoExcerpt` composition that takes `startFrame` and `durationInFrames`
2. Audio slicing: `ffmpeg -ss <start> -t <duration>` on the scene WAV
3. Verification that the slice doesn't cut mid-word (check VO timing)

If Hamza wants speed over completeness: **Option C** (full H3, 3 min, no new code).
If Hamza wants the 90s target with all fixes: **Option D** (requires excerpt engineering).
