# Q004 Visual Shortcomings — Targeted Upgrade Proposal

**Source:** `~/workspace/your_files/Q004_HousingBroke_master.mp4` (23,151f, 772s)  
**Inspected:** 2026-10-10, 10 sample frames across all 7 scenes  
**Status:** PROPOSAL ONLY — no code changed, no rerender (awaiting authorization)

## Defect 1: Text overlap — H3 BEAT 2 (~180s) [HIGH]

**What:** The supporting line "highest since 2004 · 10-year at 5.2%, highest since 2007"
renders THROUGH the "30-year Treasury:" headline during its entrance animation.

**Root cause:** `src/housing/H3Autopsy.tsx:89-97` — the supporting `<div>` sits OUTSIDE
the `<Sequence from={1200}>` that wraps the HeroTypography. The headline animates
`translateY(44px → 0)` over 16 frames while the supporting text is static, so they
collide mid-entrance.

**Fix (2 lines):** Move the supporting div INSIDE the Sequence, after the
HeroTypography component, so both animate as one unit. Or: delay the supporting
text opacity to start after the headline settles (frame 1200+28).

## Defect 2: Headline clipped at left edge — H3 BEAT 3 (~250s) [HIGH]

**What:** "Three forces hit at once" — the "T" of "Three" is cut off at the left
canvas edge.

**Root cause:** `HeroTypography` (`src/light/editorial.tsx:13`) uses fixed
`fontSize: 104, letterSpacing: -2`. "Three forces hit at once" at 104px exceeds
the `CARD_W.L` container width; left-aligned text overflows past the PAGE margin.

**Fix (targeted):** Add a `maxWidth` guard in HeroTypography: measure text width
(via canvas or a width table) and scale fontSize down when the longest line
exceeds the container. Fallback: reduce to 88px for lines > 22 chars. This is a
primitive-level fix that protects all future headlines.

## Defect 3: "$40.0T" formatting — H4 BEAT 1 (~330s) [MEDIUM]

**What:** The debt counter shows "$40.0T" — the ".0" is visual noise.

**Root cause:** `src/housing/H4Debt.tsx:47` — `${debt.toFixed(1)}T` where debt
animates 39.0 → 40.0. At exactly 40, it renders "40.0".

**Fix (1 line):** Conditional decimals:
`debt % 1 === 0 ? debt.toFixed(0) : debt.toFixed(1)` → "$40T" at rest, "$39.7T" mid-count.

## What looked GOOD (do not touch)

- H1 title card (~30s): clean hierarchy, good spacing
- H2 mortgage chart (~100s): line chart + dual stat cards, well composed
- H4 $320B card (~400s): clean single-stat layout
- H6 three-audience cards (~600s): balanced 2+1 grid, readable
- H4 debt counter entrance (~330s, aside from ".0"): strong hero number
- Overall: Light Premium Fintech identity is consistent; no dark leakage;
  typography is Plus Jakarta Sans throughout; left-align law holds.

## Upgrade plan (shortest safe path)

1. **Fix Defects 1–3** in source (3 small edits, all in `src/housing/`, none in primitives except the HeroTypography guard).
2. **Add a composition regression test**: render the 3 affected beats at low res
   (or screenshot via Remotion stills) and assert no text overlap / no clipping
   via bounding-box checks. This prevents recurrence.
3. **Hamza reviews** the fixed stills.
4. **Rerender Q004** ONLY on his explicit authorization (currently forbidden).

## Why not more

The 10 sampled frames show the visual system is fundamentally sound — the defects
are localized composition bugs, not systemic failures. A broad visual overhaul
would risk the consistency that's already working. Fix the 3 defects, add the
regression guard, and move on.
