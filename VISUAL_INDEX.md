# Visual System Master Index v2.0

**All visual rules files are linked and communicate with each other.**
**No file references old visual styles. All point to v2.0.**

---

## RULE FILES (READ IN ORDER)

### 1. VISUAL_SYSTEM.md — Production Rules
**What:** Colors, backgrounds, panels, typography, charts, motion, scene grammar, QC checklist
**When to read:** Before building any visual component
**Links to:** VISUAL_ESSENTIALS.md (what to build), TIMING_RULES.md (how long), REPLACEMENT_RULES.md (how to rebuild)

### 2. VISUAL_ESSENTIALS.md — Component Catalog  
**What:** 46 unique essentials from all 4 reference images (9 charts, 8 diagrams, 10 stages, 9 UI, 8 animations, 3 transitions)
**When to read:** When choosing which visual to use for a beat
**Links to:** VISUAL_SYSTEM.md (style rules), TIMING_RULES.md (animation timing)

### 3. TIMING_RULES.md — Retention & Timing
**What:** Max 4s static, 9 changes per beat, MrBeast 2-4s rule, reading formula, first 30s rules
**When to read:** When planning beat internal structure
**Links to:** VISUAL_SYSTEM.md (motion specs), VISUAL_ESSENTIALS.md (which animations)

### 4. REPLACEMENT_RULES.md — Rebuild Specifications
**What:** Step-by-step rules for rebuilding 29 modes (backgrounds, cards, math, animations)
**When to read:** When rebuilding or creating new visual components
**Links to:** VISUAL_SYSTEM.md (design tokens), TIMING_RULES.md (timing), VISUAL_ESSENTIALS.md (components)

---

## CODE FILES (IMPLEMENTATION)

### src/light/tokens.ts
**Implements:** VISUAL_SYSTEM.md §1 (colors), §4 (typography)
**Status:** v2.0 ✅

### src/light/primitives.tsx
**Implements:** VISUAL_SYSTEM.md §2 (5-layer background), §3 (glass panels)
**Provides:** LightCanvas, GlassCard, TrustStrip, IllustrativeLabel
**Status:** v2.0 ✅

### src/light/components_v2.tsx
**Implements:** VISUAL_ESSENTIALS.md (21 new components)
**Status:** v2.0 ✅

### src/light/charts.tsx (10 modes)
**Implements:** VISUAL_ESSENTIALS.md (9 charts) + VISUAL_SYSTEM.md §5
**Status:** v2.0 rebuilt ✅

### src/light/editorial.tsx (6 modes)
**Implements:** VISUAL_ESSENTIALS.md (10 story stages)
**Status:** v2.0 rebuilt ✅

### src/light/explain.tsx (6 modes)
**Implements:** VISUAL_ESSENTIALS.md (8 diagrams)
**Status:** v2.0 rebuilt ✅

### src/light/ui.tsx (7 modes)
**Implements:** VISUAL_ESSENTIALS.md (9 UI components)
**Status:** v2.0 rebuilt ✅

---

## PIPELINE INTEGRATION

### New video checklist (D-030) now includes:
1. Create `src/videos/{name}/` with composition + data
2. Add import + `<Composition>` to `src/RemotionRoot.tsx`
3. Add entry to `.github/scripts/composition_contract.py`
4. Add beat file path to `BEAT_FILES` in `.github/scripts/validate_dispatch.py`
5. Beat file MUST match EDITORIAL_BEAT_SCHEMA.json
6. **Visuals MUST use v2.0 system** (see VISUAL_SYSTEM.md)
7. **Timing MUST follow TIMING_RULES.md** (max 4s static, 9 changes per beat)
8. CI must pass

### Validation scripts check:
- `.github/scripts/validate_new_video.py` — beat schema + no sideways imports
- CI guards — no broken imports, no data leaks, no dangling compositions

---

## OLD SYSTEM (REMOVED)

**Deleted/Replaced:**
- ❌ `visual-style-guide.md` (old dark brain) — deleted 2026-10-11
- ❌ `Plus Jakarta Sans` font — replaced with Inter
- ❌ `#5368F7` primary blue — replaced with `#3478F6`
- ❌ Peach blobs (`accentPeach`) — removed from palette
- ❌ Flat backgrounds — replaced with 5-layer atmospheric
- ❌ 36-second static beats — replaced with 9-change minimum

**No file in the repo references the old system.** All point to v2.0.

---

## QUICK START FOR NEW VIDEO

1. Read **VISUAL_SYSTEM.md** — understand colors, backgrounds, panels
2. Read **VISUAL_ESSENTIALS.md** — pick visuals for each beat
3. Read **TIMING_RULES.md** — plan 9+ changes per 36s beat
4. Use components from `src/light/` — they're all v2.0
5. Follow **REPLACEMENT_RULES.md** — if building custom visuals
6. Validate with `.github/scripts/validate_new_video.py`

---

*Version 2.0 • 2026-10-12 • All files cross-linked and communicating*
*No old visual styles referenced anywhere*
