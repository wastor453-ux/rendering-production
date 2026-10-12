# Visual Replacement Rules v2.0

**MANDATORY for rebuilding all 29 visual modes**
**Source:** Hamza's 4 reference images
**Date:** 2026-10-12

---

## RULE 1: BACKGROUND (EVERY COMPONENT)

Every visual mode MUST be wrapped in the 5-layer atmospheric background:
1. Base: `linear-gradient(135deg, #F8FBFF 0%, #F1F6FF 48%, #EFEDFF 100%)`
2. Blue bloom: radial at 9%/9%, #5393FF @ 24%, blur 140px
3. Lavender bloom: radial at 92%/24%, #8C7BFF @ 16%, blur 170px
4. Cyan bloom: radial at 66%/100%, #31B9F4 @ 12%, blur 140px
5. Content: crisp, 0px blur

**NEVER:** Flat solid background. **ALWAYS:** Atmospheric.

---

## RULE 2: CARD STRUCTURE (EVERY CHART/DIAGRAM)

From Graph Atlas image analysis:
- Card: white @ 90%, radius 24px, border 1px #D8E6FA @ 70%
- Shadow: `0 10px 30px rgba(40,85,170,0.08)`
- Padding: 32px
- Title: 28px, weight 800, color #102044, left-aligned
- Subtitle: 20px, weight 400, color #5E6B82, below title
- Chart area: minimum 400px height
- Trust strip: 16px, #5E6B82, bottom of card

---

## RULE 3: CHART SPECIFICS (FROM GRAPH ATLAS)

### Line Chart (Portfolio Value Over Time)
- SVG: 900×420, padding 56
- Grid: light blue (#DCE6FF), horizontal only, 5 lines
- Primary line: #3478F6, width 3, no fill
- Secondary line: #18BFAE, width 2.5, no fill
- X labels: 16px #5E6B82, every Nth point
- Y labels: 16px #5E6B82, formatted ($, %, etc.)
- Endpoint: dot + label box (white, border, 18px bold)
- Animation: draw-on 0.5-1.0s ease-out, left→right

### Bar Chart (Monthly Spending)
- Bars: rounded top (8px), gradient blue→lighter
- Bar width: 60px, gap 32px
- Value labels: 20px bold #102044, above each bar
- Category labels: 18px #5E6B82, below
- Y axis: light grid, 16px labels
- Animation: rise 0.5-0.8s ease-out, staggered 0.1s

### Donut Chart (Budget Allocation)
- Outer radius: 140, inner radius: 90 (donut thickness 50)
- Segments: #3478F6, #31B9F4, #8C7BFF, #18BFAE, #DCE6FF
- Center: total value (32px bold) + label (18px muted)
- Legend: right side, color dot 20px + label + % (right-aligned)
- Animation: segments reveal 0.6-1.0s ease-in-out, sequential

### Waterfall Chart (Cash-Flow)
- Bars: income (blue), deductions (coral/lavender), savings (teal), ending (navy)
- Connectors: dashed gray lines between bars
- Labels: +/- values on each bar, 18px bold
- X labels: category names below
- Math: MUST reconcile (income - deductions + savings = ending)

### Area Chart (Compound Interest)
- Two stacked areas: contributions (#31B9F4 @ 30%) + growth (#3478F6 @ 20%)
- Lines on top: 3px solid matching colors
- X: years (0, 5, 10...), Y: USD
- Legend: top-right, color dots + labels
- Example box: right side, white card with inputs/outputs

### Stacked Bar (Mortgage Breakdown)
- 7 groups (Year 1, 5, 10...), each stacked: P (blue), I (lavender), T (teal), Ins (light)
- Value labels: on top of each stack, 18px bold
- Legend: top, horizontal, color squares + labels
- Y: USD, light grid

---

## RULE 4: MATH/PHYSICS VERIFICATION

### Every chart MUST:
1. **Scale correctly:** `y = H - PAD - ((value - min) / (max - min)) * (H - PAD*2)`
2. **Handle edge cases:** empty data, single point, all same value, negative values
3. **Reconcile:** waterfall sums, donut = 100%, stacked bars sum correctly
4. **Format numbers:** USD with commas, % with 1 decimal, no floating point errors
5. **Snap animations:** count-up MUST end on exact value (not 0.999...)

### Physics (motion):
- Easing: `Easing.bezier(0.16, 1, 0.3, 1)` (EXPO from tokens)
- Clamp: ALWAYS use `extrapolateLeft: "clamp", extrapolateRight: "clamp"`
- Count-up: `Easing.out(Easing.exp)` NEVER reaches 1 — snap when `frame >= duration`

---

## RULE 5: TYPOGRAPHY HIERARCHY

| Element | Size | Weight | Color | Example |
|---------|------|--------|-------|---------|
| Card title | 28px | 800 | #102044 | "Portfolio Value Over Time" |
| Card subtitle | 20px | 400 | #5E6B82 | "Track how investments grow" |
| Axis label | 16px | 500 | #5E6B82 | "Jan 2020", "$50,000" |
| Data label | 18px | 700 | #102044 | "$178,420" |
| Legend | 18px | 500 | #102044 | "Total Portfolio Value" |
| Trust strip | 16px | 500 | #5E6B82 | "Source: BLS | As of: 2024" |

Font: Inter. NEVER mix fonts.

---

## RULE 6: COLOR SEMANTICS (LOCKED)

- **#3478F6 (Blue):** Primary data series, focal numbers, main actions
- **#31B9F4 (Cyan):** Secondary series, highlights
- **#18BFAE (Teal):** Positive values, alternate series, "better" indicators
- **#8C7BFF (Lavender):** Third category, soft accents
- **#F27D8C (Coral):** NEGATIVE ONLY (losses, costs, debt)
- **#102044 (Navy):** Text, titles, axes
- **#5E6B82 (Muted):** Secondary text, axis labels

**NEVER:** Use coral for positive. Use green for "safe". Use red for emphasis.

---

## RULE 7: LAYOUT GRIDS

### Chart card (from Graph Atlas):
```
┌─────────────────────────────────────────┐
│ Title (28px bold)          Legend       │
│ Subtitle (20px muted)                   │
│ ┌─────────────────────────────────────┐ │
│ │                                     │ │
│ │         CHART AREA (SVG)            │ │
│ │         900×420 min                 │ │
│ │                                     │ │
│ └─────────────────────────────────────┘ │
│ Source: X | As of: Y | Units: Z        │
└─────────────────────────────────────────┘
```

### Comparison (from Money Mechanics):
```
┌──────────────┐  ┌──────────────┐
│   Option A   │  │   Option B   │
│   6.5%       │  │   8.2% ✓Better│
│   Annual     │  │   Annual     │
└──────────────┘  └──────────────┘
```

---

## RULE 8: ANIMATION TIMING

| Animation | Duration | Easing | Stagger |
|-----------|----------|--------|---------|
| Line draw | 15-30f | ease-out | — |
| Bar rise | 15-24f | ease-out | 3f per bar |
| Count up | 18-30f | exp-out + snap | — |
| Donut reveal | 18-30f | ease-in-out | 6f per segment |
| Card entry | 12-18f | expo | 4f per card |

**RULE:** One major animation at a time. End on stable frame (hold 30f minimum).

---

## CHECKLIST (BEFORE COMMIT)

- [ ] Background: 5-layer atmospheric (not flat)
- [ ] Card: white 90%, 24px radius, 1px #D8E6FA border
- [ ] Title: 28px/800/#102044, subtitle 20px/#5E6B82
- [ ] Colors: only from locked palette, correct semantics
- [ ] Typography: Inter only, correct hierarchy
- [ ] Math: scales correct, reconciles, snaps exact
- [ ] Animation: correct timing, easing, clamp, one at a time
- [ ] Trust strip: source/date/units on data visuals
- [ ] Mobile: readable at 1080p, 16px minimum
- [ ] No hardcoded old colors (#5368F7, peach, etc.)

---

## RELATED FILES (v2.0 — all cross-linked)

- **VISUAL_INDEX.md** — Master index of all rules files
- **VISUAL_SYSTEM.md** — Production rules (colors, backgrounds, panels, motion)
- **VISUAL_ESSENTIALS.md** — 46-item component catalog from 4 images
- **TIMING_RULES.md** — Retention timing (max 4s static, 9 changes per beat)
- **REPLACEMENT_RULES.md** — Step-by-step rebuild specifications

*All files reference v2.0 only. No old visual styles.*
