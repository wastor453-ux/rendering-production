# Visual System v2.0 — Production Rules

**Source:** Hamza's A-to-Z Visual Package (2026-10-12)
**Status:** MANDATORY for all new videos
**Replaces:** Old visual system (v1.0)

---

## THE CORE RULE

**The background should feel like light in a room, not a colored rectangle.**
Build it from soft gradients, large out-of-focus color blooms and translucent depth.
Keep charts, figures, and text crisp in the foreground.

---

## 1. COLOR TOKENS (LOCKED)

| Token | Hex | Role |
|-------|-----|------|
| Navy | `#102044` | Primary text, titles, axes |
| Primary Blue | `#3478F6` | Core data, emphasis, focus |
| Cyan | `#31B9F4` | Secondary data, highlights |
| Teal | `#18BFAE` | Positive / alternate series |
| Lavender | `#8C7BFF` | Secondary category, soft glow |
| Fog | `#EAF1FF` | Cool surface tint |
| White | `#FFFFFF` | Glass card face |
| Coral | `#F27D8C` | **Negative values ONLY, sparingly** |

### Color behavior rules:
- **Background:** mostly white/cool fog. Blue and lavender appear as soft light, not flat fills.
- **Primary data:** blue for main series/focal number; cyan and teal for comparisons.
- **Positive/negative:** teal = positive movement (when data supports it); coral = losses/costs ONLY.
- **No semantic guessing:** green ≠ "safe", upward arrows ≠ guaranteed returns. Label what colors mean.

---

## 2. ATMOSPHERIC BACKGROUND (5-LAYER RECIPE)

**NEVER use a flat, single-color background.**

| Layer | Build | Setting | Purpose |
|-------|-------|---------|---------|
| 01 — Base wash | Large multi-stop gradient | `#F8FBFF → #F1F6FF → #EFEDFF` (135°) | Luminous cool-white canvas |
| 02 — Blue bloom | Oversized feathered radial | Blur 100-180px, opacity 18-32% | Depth without blob look |
| 03 — Lavender bloom | Diffuse glow, opposing edge | Blur 120-220px, opacity 12-25% | Violet-blue finance echo |
| 04 — Cyan bloom | Lower edge, sparingly | Blur 100-180px, opacity 8-18% | Subtle accent |
| 05 — Foreground | Cards, charts, text | 0px blur, 100% crisp | Protects legibility |

### Background families (pick one per scene):
- **Cool Blue Fog:** Explainers, data, chapters
- **Lavender Horizon:** Investing, future planning, long-term growth
- **Glass Aurora:** Portfolio / growth / system diagrams
- **Soft Orb Depth:** Dashboard-style UI boards
- **Financial Data Atmosphere:** Graph atlas, analytics
- **Calm Executive:** Trust, security, recap, CTA

### Critical distinction:
**The whole frame is NOT blurry.** Background is soft; foreground typography, icons, numbers, charts, labels are SHARP.

---

## 3. GLASS PANELS

| Property | Spec | Rule |
|----------|------|------|
| Face | White at 86-94% opacity | Never let glow reduce readability |
| Corner radius | 18-28px (at 1920×1080) | One radius family, don't mix |
| Border | 1-1.5px `#D8E6FA` at 50-80% | Visible only on close inspection |
| Shadow | `0 10px 30px rgba(40,85,170,0.06-0.10)` | Soft, cool-tinted, NO dark drops |
| Backdrop blur | 16-28px | Only where background shows through |
| Padding | 20-32px for major cards | Give numbers breathing room |
| Elevation | Max 2-3 levels | Haze < canvas < cards |

### Composition rules:
- **16:9 canvas:** 1920×1080 default
- **Safe area:** key info inside 5-7% of each edge
- **Information grid:** 3×3 or 4×2 for dense; 5×2 for storyboards; 1 hero + 2-3 support for concepts
- **Single focal point:** one main number/chart/flow leads; secondary cards smaller/calmer
- **Space is design:** white/blurred space is NOT wasted; don't fill every corner

---

## 4. TYPOGRAPHY

**Font:** Inter (first choice), Manrope (acceptable alternate). Never mix families.

| Role | Size | Weight | Rule |
|------|------|--------|------|
| Main hook | 52-76px | Bold/700 | One thought, 1-3 short lines |
| Scene heading | 30-42px | Semibold/600 | Short, descriptive |
| Card title | 22-28px | Semibold/600 | Label the idea, not narration |
| Body | 18-22px | Regular/400 | Plain English, no dense paragraphs |
| Axis/legend | 16-18px min | Medium/500 | Don't shrink to fit crowded charts |

---

## 5. CHART LANGUAGE

| Question | Best visual | Motion | Must show |
|----------|-------------|--------|-----------|
| "How did value change?" | Line/area chart | Draw left→right, endpoint last | Period, unit, source, legend |
| "Where does money go?" | Cash-flow/waterfall | Reveal inflow, then outflows | Amounts reconcile |
| "How is this split?" | Donut/stacked bar | Segments in sequence | Sum to 100% |
| "How do options differ?" | A/B cards/bars | One option, then other | Same assumptions |
| "Why compounding?" | Contributions vs growth | Contributions first, growth second | Schedule, rate, term, caveats |
| "What's in a payment?" | Stacked breakdown | Build from baseline | All components |
| "How fast debt falls?" | Two payoff lines | Animate downward calmly | APR, rules, assumptions |
| "What did inflation change?" | Purchasing-power/indexed | Hold nominal, reveal real | Base year, measure |
| "What should I do?" | Decision tree/checklist | One step at a time | Actions, boundaries |

### Chart styling:
- **Axes:** thin light-blue grid, clear units, minimal ticks
- **Series:** blue=primary, cyan/teal=secondary, lavender=third, navy/gray=context
- **Avoid:** 3D pies, perspective bars, decorative points, unlabelled arrows, chopped axes
- **Trust strip:** Source, As-of date, Units, Assumptions — ALWAYS on data scenes
- **Truth rule:** Placeholder data labeled "Illustrative example"; replace with verified before publishing

---

## 6. MOTION GRAMMAR

| Behavior | Timing | Easing | Use for |
|----------|--------|--------|---------|
| Line draw-on | 0.5-1.0s | Ease-out | Trends, curves |
| Bar rise | 0.5-0.8s | Ease-out | Comparisons |
| Number count-up | 0.6-1.0s | Ease-out, end exact | One primary KPI |
| Donut reveal | 0.6-1.0s | Ease-in-out | Allocations |
| Cash-flow arrows | 0.8-1.2s | Ease-in-out | Income→expenses→savings |
| Card reveal | 0.4-0.8s | Ease-out | Emphasis panels |
| Scene transition | 0.3-0.8s | Fade/slide/wipe | Next idea |

### Motion rules:
- **One major movement at a time** — don't animate everything simultaneously
- **End on stable frame** — hold complete chart long enough to read
- **Data motion preserves meaning** — lines map to data order, bars from proper baseline
- **Background stays nearly invisible** — slow drift OK, no moving blobs behind labels
- **No bounce, elastic, whip-pan, or flashy transitions**

---

## 7. SCENE GRAMMAR (9 STAGES)

| Stage | Question | Visual | Motion |
|-------|----------|--------|--------|
| 01 — Hook | Why care? | Strong headline, one number | Headline appears, element settles |
| 02 — Problem | What's difficult? | Bills, debt, cost stack | Reveal one by one |
| 03 — Explain | What does it mean? | Concept card, diagram | Reading order reveal |
| 04 — Mechanism | How does it work? | Flow diagram, timeline | Highlight cause/effect |
| 05 — Example | Can I see math? | Calculator card | Inputs → calc → result |
| 06 — Evidence | Is it supported? | Historical chart | Draw chart, reveal source |
| 07 — Trade-offs | What might change? | A/B scenario, caveats | Side-by-side, assumptions visible |
| 08 — Action | What can I do? | Checklist, next steps | One action at a time |
| 09 — Close | What to remember? | Takeaway, logo, CTA | Minimal, no confetti |

---

## 8. QUALITY CHECKLIST (BEFORE RENDER)

- [ ] Background is atmospheric (not flat)
- [ ] Foreground is sharp (0px blur on text/charts)
- [ ] One clear focal point; safe margins respected
- [ ] Visual matches narration (chart answers the question)
- [ ] Data trustworthy (calculated, units/dates visible, assumptions stated)
- [ ] Colors consistent (roles locked, coral only for negative)
- [ ] Motion calm (no simultaneous movement, no bounce)
- [ ] Reads on mobile (labels legible at 1080p)
- [ ] No generation artifacts (fix misspelled text, distorted icons)
- [ ] Brand locked (type hierarchy, panels, motion rhythm match system)

---

## 9. WHAT'S LOCKED vs FLEXIBLE

**LOCKED (every video):**
- Color tokens and semantic roles
- Type family, size hierarchy
- Glass treatment, borders, shadows
- Chart behavior, source labels, trust rules
- Motion timing family
- Background principle (atmospheric, never flat)

**FLEXIBLE (per topic):**
- Which charts/diagrams are needed
- Background bloom placement and family
- Number of cards/panels
- Scene pacing and complexity
- Topic-specific icons
- Accent emphasis

---

*Version 2.0 • 2026-10-12 • From Hamza's A-to-Z Visual Package*
*Visual DNA only — no HousingBroke texts, names, or branding*
