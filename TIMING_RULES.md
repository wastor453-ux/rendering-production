# Animation Timing & Retention Rules v2.0

**Source:** Hamza's reference images + retention research (MrBeast, YouTube analytics)
**Date:** 2026-10-12
**Purpose:** No animation stays on screen too long. Keep viewers engaged.

---

## THE RETENTION PROBLEM

**Research findings:**
- Human attention span: **8.25 seconds** (Microsoft, 2015)
- Boredom threshold: **5-7 seconds** of static visual = viewer drops off
- MrBeast rule: Visual change every **2-4 seconds**
- Top creators: Average shot length **1.77 seconds** (first 30s)
- Hollywood trend: 12s → 2.5s average shot length
- Facebook: First 3 seconds determine if viewer stays for 30s

**Our problem:** 36-second static beats kill retention. Each beat needs internal visual progression.

---

## TIMING RULES (MANDATORY)

### RULE 1: MAX HOLD TIME

| Content Type | Max Static Hold | Action Required |
|--------------|-----------------|-----------------|
| Any visual | **4 seconds** | MUST change/add/remove something |
| Chart | **6 seconds** | Add annotation, highlight, or transition |
| Text card | **3 seconds** | Animate in next element or transition |
| Full beat (36s) | **NEVER static** | Minimum 9 visual changes per beat |

**Formula:** `visual_changes_per_beat = beat_duration / 4` (minimum)

For 36-second beat: 36 / 4 = **9 minimum visual developments**

### RULE 2: ANIMATION DURATIONS (from reference images)

| Animation | Duration | Easing | Max Hold After |
|-----------|----------|--------|----------------|
| Line draw-on | 0.5-1.0s (15-30f) | Ease-out | 3s then next action |
| Bar rise | 0.5-0.8s (15-24f) | Ease-out | 3s then next action |
| Count-up | 0.6-1.0s (18-30f) | Ease-out + snap | 2s then next action |
| Donut reveal | 0.6-1.0s (18-30f) | Ease-in-out | 3s then next action |
| Card reveal | 0.4-0.8s (12-24f) | Ease-out | 2s then next action |
| Scene transition | 0.3-0.8s (9-24f) | Fade/slide | Immediate next scene |

**Critical:** After animation completes, hold MAX 2-4 seconds, then:
- Reveal next data point, OR
- Highlight key insight, OR  
- Transition to next visual

### RULE 3: BEAT INTERNAL STRUCTURE (36s beat)

**OLD (kills retention):**
```
[0s] Show chart
[36s] Static for 36 seconds ❌
```

**NEW (keeps engagement):**
```
[0s]  Title + context appears (0.5s)
[2s]  Chart draws in (1.0s)
[5s]  First data point highlighted (0.5s)
[8s]  Annotation callout appears (0.5s)
[11s] Second data point highlighted (0.5s)
[14s] Key number counts up (1.0s)
[17s] Trust strip fades in (0.5s)
[20s] Comparison element appears (0.5s)
[23s] Takeaway checklist builds (1.0s)
[27s] Final highlight pulse (0.5s)
[30s] Hold for reading (3s)
[33s] Transition out (0.8s)
```

**Minimum 9 visual events per 36s beat.**

### RULE 4: WHICH ANIMATION WHERE (from images)

| Scene Type | Primary Animation | Secondary | Timing |
|------------|-------------------|-----------|--------|
| Hook (0-20s) | Hero typography fade | Number count-up | Fast: 0.5s each |
| Problem | Cards stagger in | Highlight pulse | 0.4s stagger |
| Concept | Icon flow (→) | Label fade | 0.6s per step |
| Mechanism | Flow diagram build | Arrow animation | 0.8s per node |
| Example | Calculator inputs | Result reveal | 0.5s per field |
| Data chart | Line draw / Bar rise | Endpoint highlight | 1.0s draw, 0.5s highlight |
| Compare | A/B cards slide | "Better" badge pop | 0.6s cards, 0.3s badge |
| Risks | Grid stagger | Icon pulse | 0.4s stagger |
| Actions | Checklist build | Number pop | 0.5s per item |
| Close | Takeaway fade | CTA button | 0.8s, hold 3s |

### RULE 5: ATTENTION RESET TRIGGERS

Every **2-4 seconds**, trigger ONE of:
- [ ] New element appears (card, label, icon)
- [ ] Existing element animates (highlight, pulse, move)
- [ ] Data point emphasized (dot, callout, zoom)
- [ ] Camera moves (subtle zoom, pan)
- [ ] Text updates (count-up, label change)

**NEVER** go 5+ seconds without a visual change.

### RULE 6: READING TIME CALCULATOR

How long to hold a visual for reading:

```
reading_time = (word_count / 3) + 1 second
```

- 6 words: (6/3) + 1 = **3 seconds**
- 12 words: (12/3) + 1 = **5 seconds** (too long! split it)
- Chart with 5 labels: **4 seconds** max

**If reading time > 4s:** Split into multiple visual steps.

### RULE 7: FIRST 30 SECONDS (CRITICAL)

From research: First 30s determines retention.

| Time | Requirement |
|------|-------------|
| 0-3s | Hook visible, ONE clear promise |
| 3-10s | 4-5 visual changes (every 1.5s) |
| 10-20s | Problem introduced, 5 visual changes |
| 20-30s | Concept teased, viewer committed |

**Shot changes:** Every **1.77s average** in first 30s (19 shots).

### RULE 8: BOREDOM DETECTION

**Warning signs (fix immediately):**
- [ ] Same visual for >4 seconds with no change
- [ ] Text on screen >5 seconds without animation
- [ ] Chart fully drawn but no highlight for >3 seconds
- [ ] No new information for >4 seconds

**Fix:** Add highlight, annotation, zoom, or transition.

---

## IMPLEMENTATION CHECKLIST

For each 36-second beat, verify:

- [ ] Minimum 9 visual events scheduled
- [ ] No gap >4 seconds without visual change
- [ ] Animations use correct durations (0.4-1.2s)
- [ ] Hold times calculated via reading formula
- [ ] End on stable frame (hold 2-3s for reading)
- [ ] Transition to next beat (0.3-0.8s)

---

## QUICK REFERENCE CARD

```
MAX STATIC: 4 seconds
MIN CHANGES per 36s beat: 9
FIRST 30s shot length: 1.77s avg
ANIMATION durations: 0.4-1.2s
HOLD after animation: 2-4s max
READING formula: (words/3) + 1s
BOREDOM threshold: 5-7s (NEVER reach)
```

---

*Based on: Hamza's reference images + MrBeast retention architecture + YouTube analytics research*
*Version 2.0 • 2026-10-12*
