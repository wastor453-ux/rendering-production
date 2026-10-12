# Visual Essentials Catalog v2.0

**Source:** All 4 reference images from Hamza's A-to-Z Visual Package
**Date:** 2026-10-12
**Total unique essentials catalogued:** 47

---

## IMAGE 1: Finance Graph Atlas — 9 Charts

| # | Essential | Type | Key Features |
|---|-----------|------|--------------|
| 1 | Portfolio Value Over Time | Dual-line chart | 2 series (blue primary, teal secondary), time x-axis, USD y-axis, endpoint labels |
| 2 | Monthly Spending | Bar chart | 5 categories, blue→gray gradient bars, value labels on top |
| 3 | Budget Allocation | Donut chart | 5 segments, center total, right-side legend with % |
| 4 | Cash-Flow Waterfall | Waterfall chart | Income → deductions → savings → ending balance, +/- labels |
| 5 | Compound Interest | Area/line chart | 2 series (with interest vs principal only), 30-year x-axis, shaded areas |
| 6 | Mortgage Payment Breakdown | Stacked bar | 7 time periods, 4 components (P/I/T/I), value labels |
| 7 | Debt Payoff | Dual-line chart | Avalanche vs Snowball, months x-axis, balance y-axis |
| 8 | Inflation & Purchasing Power | Line chart | Declining index, year x-axis, "Illustrative" label |
| 9 | Scenario Comparison | Bar chart | 3 scenarios (Conservative/Base/Optimistic), hypothetical disclaimer |

---

## IMAGE 2: Money Mechanics Diagram Library — 8 Diagrams

| # | Essential | Type | Key Features |
|---|-----------|------|--------------|
| 10 | Paycheck → Cash Flow | Flow/split diagram | Income node → 4 expense branches with icons, % labels |
| 11 | Compound Growth | Area chart + legend | Contributions vs Growth stacked, example callout box |
| 12 | Debt Payoff Strategies | VS comparison | Avalanche (3 steps) vs Snowball (3 steps), "Best for" checkmarks |
| 13 | Mortgage Payment Stack | Horizontal stacked bar | 5 components with % ranges, bracket label |
| 14 | Rent vs Buy | Factor grid + VS | 4 key factors on top, Rent vs Buy cards below |
| 15 | Inflation Timeline | 3-stage timeline | $100 → fewer items over 10/20 years, arrow connectors |
| 16 | Diversification Donut | Donut + legend | 5 asset classes, % labels, right-side legend |
| 17 | Emergency Fund Ladder | Stepped progression | 5 tiers (Starter→Long-term), rising arrow, month labels |

*Note: #11 overlaps with #5 (Compound Interest) — same concept, different layout*

---

## IMAGE 3: Finance Video Story System — 10 Story Stages

| # | Essential | Type | Key Features |
|---|-----------|------|--------------|
| 18 | Hook & Promise | Hero card | Large question headline, phone mockup visual, supporting text |
| 19 | Real-World Problem | Photo + cards | Person photo, floating bill/statement cards with amounts |
| 20 | Concept Definition | 3-step icon flow | Icon → arrow → icon → arrow → icon, labels below |
| 21 | Mechanism Flow | 3-node diagram | Circular nodes (You → Platform → Goals), curved return arrow |
| 22 | Worked Example | Calculator card | Input fields (deposit, monthly, rate, years), Calculate button, results panel |
| 23 | Data & Chart | Chart + source | Line chart, legend, source attribution below |
| 24 | Scenario Compare | A/B cards | Two option cards, same assumptions header, final values |
| 25 | Risks Grid | 2×2 warning cards | Icon + title + description per risk (Fees, Rates, Taxes, Inflation) |
| 26 | Action Checklist | Numbered steps | 1-2-3 with icons, titles, descriptions |
| 27 | Recap End Card | Takeaway + CTA | Key message, logo, subscribe button, chart visual |

---

## IMAGE 4: Finance Motion Grammar

### Section A: Reusable On-Screen Components — 9

| # | Essential | Type | Key Features |
|---|-----------|------|--------------|
| 28 | KPI Card | Metric card | Large number ($12,480.00), delta pill (+12.4%), sparkline chart |
| 29 | Source + Date Label | Info pill | Calendar icon, "Source: BLS", "As of: Mar 2025" |
| 30 | Chart Legend | Legend list | Color dots (blue/teal/lavender), labels, % values |
| 31 | Annotation Callout | Info box | Info icon, text, pointer line to chart point |
| 32 | Compare A/B Cards | Option cards | Two cards, "Better" badge on winner, metric + label |
| 33 | Assumption Tag | Pill tag | "Assumes 7% annual return" with info icon |
| 34 | Section Title | Lower third | Bold heading, subtitle, accent underline bar |
| 35 | Takeaway Checklist | Check list | Green checkmarks, 4 items |
| 36 | Disclaimer Strip | Full-width bar | Info icon, legal text, light background |

### Section B: Animation Behaviors — 8

| # | Essential | Animation | Timing |
|---|-----------|-----------|--------|
| 37 | Line Draw-On | Line draws left→right | 0.5-1.0s, ease-out |
| 38 | Bar Rise | Bars grow from baseline | 0.5-0.8s, ease-out |
| 39 | Count-Up Number | Number increments | 0.6-1.0s, ease-out, snap exact |
| 40 | Donut Segment Reveal | Segments appear in sequence | 0.6-1.0s, ease-in-out |
| 41 | Cash-Flow Arrows | Arrows flow between nodes | 0.8-1.2s, ease-in-out |
| 42 | Debt Balance Progress | Bar shrinks / number decreases | 0.8-1.2s, ease-out |
| 43 | Timeline Marker Travel | Dot moves along timeline | 0.6-1.0s, linear |
| 44 | Highlight Reveal | Spotlight on key element | 0.4-0.8s, ease-out |

### Section C: Transitions — 5

| # | Essential | Type | Timing |
|---|-----------|------|--------|
| 45 | Diagram Morph | Shape transforms | 0.5-1.0s, ease-in-out |
| 46 | Clean Wipe | Slide transition | 0.3-0.8s, ease-out |
| 47 | Card → Chart Zoom | Zoom into detail | 0.6-1.2s, ease-out |

*Note: #48-49 (Parallax, Shape Mask) are background/transition effects, not standalone components*

---

## DEDUPLICATED COUNT

After removing overlaps:
- **9** unique charts (Graph Atlas)
- **7** unique diagrams (Money Mechanics, minus 1 overlap)
- **10** story stages (Story System)
- **9** UI components (Motion Grammar A)
- **8** animation behaviors (Motion Grammar B)
- **3** transitions (Motion Grammar C, minus 2 effects)
- **5** trust rules (already in VISUAL_SYSTEM.md)

**Total: 46 unique visual essentials** (+ 5 trust rules = 51)

---

## IMPLEMENTATION STATUS

### ✅ Already in code (via tokens/primitives):
- Color tokens (all 8 colors)
- 5-layer atmospheric background
- GlassCard specs
- TrustStrip component
- IllustrativeLabel component
- CountUp animation (#39)
- Basic charts (Line, Bar, Donut via charts.tsx)

### 🔄 Needs update (old styling):
- charts.tsx: 10 chart components need v2.0 colors + trust strips
- editorial.tsx: 6 components need v2.0 styling
- explain.tsx: 6 components need v2.0 styling  
- ui.tsx: 7 components need v2.0 styling

### ❌ Missing (not in code yet):
- KPI Card with sparkline (#28)
- Source + Date Label pill (#29)
- Chart Legend component (#30)
- Annotation Callout with pointer (#31)
- Compare A/B Cards with badge (#32)
- Assumption Tag pill (#33)
- Section Title / Lower Third (#34)
- Takeaway Checklist (#35)
- Disclaimer Strip (#36)
- Cash-Flow Arrows animation (#41)
- Debt Balance Progress (#42)
- Timeline Marker Travel (#43)
- Highlight Reveal (#44)
- Calculator Card (#22)
- Risks Grid 2×2 (#25)
- Action Checklist numbered (#26)
- Emergency Fund Ladder (#17)
- Rent vs Buy comparison (#14)
- Inflation Timeline 3-stage (#15)
- Paycheck Flow diagram (#10)
- Mortgage Payment Stack (#13)

**Missing count: 21 components need to be built**

---

## RELATED FILES (v2.0 — all cross-linked)

- **VISUAL_INDEX.md** — Master index of all rules files
- **VISUAL_SYSTEM.md** — Production rules (colors, backgrounds, panels, motion)
- **VISUAL_ESSENTIALS.md** — 46-item component catalog from 4 images
- **TIMING_RULES.md** — Retention timing (max 4s static, 9 changes per beat)
- **REPLACEMENT_RULES.md** — Step-by-step rebuild specifications

*All files reference v2.0 only. No old visual styles.*
