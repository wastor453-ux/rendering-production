# H-01: Creative Approval Criteria (DRAFT — needs Hamza's approval)

**Status:** APPROVED by Hamza 2026-10-11.
No redesign proposed until criteria are locked.

## Proposed measurable criteria for visual approval

### Layout (per scene, verified via stills)
1. No text overlap at entrance or settled state
2. No headline clipping at any breakpoint
3. Left-aligned text per `src/light/layout.ts` (no top/bottom jumping)
4. Card tiers match spec (640/960/1280)

### Typography
5. Hero headline size guard active (80/88/104px by character count)
6. Supporting text uses `HeroTypography` with correct delay props
7. Max 2 consecutive typography beats

### Motion
8. No linear easing (all motion uses expo/elastic springs)
9. Count-ups snap to exact target (no 999,023 freeze)
10. `interpolate` uses clamp on both ends (no negative opacity)

### Color & finish
11. Light Premium Fintech identity only (no dark/neon leakage)
12. Blur never on reading layer (background only)
13. 1920×1080, hairline gradient present, non-blank frames

### Audio-visual sync
14. SFX impact lands on exact visual frame (never after)
15. SFX never outlasts its visual
16. VO is spine; no visual beat without VO anchor

## Approval process (proposed)
- Hamza reviews rendered stills at beat boundaries
- Each criterion marked PASS/FAIL per scene
- One FAIL = scene rejected, not the whole video
- Three isolated fixes ≠ direction approval (standing rule)
