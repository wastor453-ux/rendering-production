# Generic Pipeline Rule-to-Enforcement Matrix

**Created:** 2026-10-12
**Purpose:** Every mandatory rule for the generic video production pipeline, its enforcement, and its test.
**Principle:** One generic pipeline for all videos. No video-specific code, rules, or exceptions.

---

## 1. Pipeline Generality Rules

| Rule | Definition | Enforcement | Stage | Test | Status |
|------|------------|-------------|-------|------|--------|
| No video names in shared code | Shared tools/components must not contain video titles, names, or channel names | `tests/test_no_video_named_files.py` (CI) | Pre-commit | test_no_video_named_files.py | ✅ |
| No hardcoded narration phrases | Tools must not contain phrases from any video's script | Manual audit + code review | Development | N/A (audit) | ✅ |
| No per-video branches | No `if video == X` logic in shared code | Code review | Development | N/A | ✅ |
| Patterns are video data | Semantic patterns come from video's `data/semantic_patterns.json`, not pipeline code | `generate_event_timeline.py` requires patterns file input | Event generation | Fail-closed on missing/empty | ✅ |
| Explicit input paths | Tools accept explicit paths, don't infer from filenames | CLI args validated | All stages | Missing arg → exit 1 | ✅ |

## 2. Event Generation Rules

| Rule | Definition | Enforcement | Stage | Test | Status |
|------|------------|-------------|-------|------|--------|
| Non-empty events | Event timeline must contain ≥1 event | `generate_event_timeline.py` exits 1 on empty | Event generation | Empty alignment → exit 1 | ✅ |
| Valid word anchors | Each event has phrase + occurrence, never bare word | Generator uses phrase matching | Event generation | N/A | ✅ |
| Supported visual types | visual_type must be in renderer's supported set | `EventDrivenVideo` throws on unsupported | Render | All 37 events validated | ✅ |
| Complete lifecycle | Each event has entrance, progression, exit | `tools/validate_timeline.py` | Event generation | Fail-closed test | ✅ |
| Deterministic output | Same inputs → same events | No randomness in generator | Event generation | N/A | ✅ |

## 3. Renderer Rules

| Rule | Definition | Enforcement | Stage | Test | Status |
|------|------------|-------------|-------|------|--------|
| Consume timeline directly | Renderer reads event_timeline.json, not hardcoded scenes | `EventDrivenVideo` component | Render | N/A | ✅ |
| Correct visual selection | donut → DonutChart, not bars | Semantic router in `EventVisual` | Render | Visual type validation | ✅ |
| Fail on unsupported types | Unknown visual_type throws, never substitutes | `throw new Error()` in router | Render | N/A | ✅ |
| Frame-driven animation | No CSS transitions, all animations use frame numbers | `useEntrance`/`useExit` hooks | Render | N/A | ✅ |
| 4s hold ceiling | No unexplained static >4s | `tools/validate_timeline.py` | Validation | Gap detection, exit 1 | ✅ |

## 4. Audio & Timing Rules

| Rule | Definition | Enforcement | Stage | Test | Status |
|------|------------|-------------|-------|------|--------|
| VO must exist | Video fails without voiceover file | `tests/test_vo_fill.py` exits 1 | Pre-render | Missing VO → exit 1 | ✅ |
| Real alignment | Word timestamps from faster-whisper, not estimates | `tools/align_vo.py` (pipeline stage) | Alignment | Fail-closed on empty | ✅ |
| A/V endpoint match | VO duration ≈ video duration (±500ms) | `tests/test_vo_visual_sync.py` | CI | Mismatch → fail | ✅ |

## 5. Visual Quality Rules

| Rule | Definition | Enforcement | Stage | Test | Status |
|------|------------|-------------|-------|------|--------|
| Light premium fintech | Colors, glass, blur per VISUAL_SYSTEM.md | Component library | Render | N/A | ✅ |
| Blurred background | Atmosphere blurred, foreground crisp | `LightCanvas` component | Render | N/A | ✅ |
| Readable typography | Minimum sizes per TIMING_RULES.md | Component defaults | Render | N/A | 🟡 |
| No watermarks | No channel/video branding unless contracted | Code review | Render | N/A | ✅ |

---

## Enforcement Gaps (🟡)

1. **Readable typography** - Component defaults exist but not validated

## Recently Closed
- ✅ Complete lifecycle validation → `tools/validate_timeline.py`
- ✅ 4s hold ceiling → integrated into `tools/run_pipeline.py`
- ✅ Real alignment automation → `tools/align_vo.py` as pipeline stage

## Next Actions

- [ ] Wire `validateTimeline()` into canonical pipeline entry point
- [ ] Automate faster-whisper alignment as pipeline stage
- [ ] Add CI test for event lifecycle completeness
- [ ] Add visual regression tests for typography
