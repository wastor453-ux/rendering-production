#!/usr/bin/env python3
"""
validate_timeline.py — Quality gates for event timelines.

Enforces mandatory rules on generated event timelines:
1. Complete lifecycle: every event has entrance, progression, exit
2. Static hold ceiling: no unexplained gap >4s between events
3. Valid visual types: all types in renderer's supported set
4. Timing validity: start < end, non-negative, ordered
5. Semantic coverage: events span the narration duration

This is a PIPELINE STAGE. Run after event generation, before render.
FAIL-CLOSED: any violation → exit 1.

Usage:
    python3 tools/validate_timeline.py <event_timeline.json> [--max-hold 4.0]
"""

import json
import sys
from pathlib import Path


# Supported visual types (must match EventDrivenVideo.tsx router)
SUPPORTED_TYPES = {
    "factor_card", "hero_statement", "hero_number", "score_card",
    "section_title", "impact_card", "tip_card", "action_card",
    "advice_callout", "question_card", "promise_card", "transition_card",
    "stat_callout", "principle_card", "encouragement_card", "closing_card",
    "timeline_event", "timeline_event_positive", "score_delta",
    "delta_callout", "gauge_visual",
}

FPS = 30
DEFAULT_MAX_HOLD_S = 4.0


def validate(timeline_path, max_hold_s=DEFAULT_MAX_HOLD_S):
    errors = []
    warnings = []

    with open(timeline_path) as f:
        timeline = json.load(f)

    events = timeline.get("events", [])

    # Gate 0: Provenance required
    # Timeline must record hashes of its alignment and patterns inputs.
    # This proves the timeline was generated from validated inputs,
    # not hand-crafted or copied from another video.
    prov = timeline.get("provenance", {})
    import re
    for field in ["alignment_sha256", "patterns_sha256"]:
        val = prov.get(field)
        if not val:
            errors.append(f"Missing provenance field '{field}' — timeline must record input hashes in provenance object")
        elif not re.fullmatch(r"[0-9a-f]{64}", str(val)):
            errors.append(f"Invalid provenance field '{field}': must be 64-char lowercase hex SHA-256, got '{val}'")
    # F-15: VO hash is optional (old timelines) but if present must be valid
    vo_sha = prov.get("vo_sha256")
    if vo_sha and not re.fullmatch(r"[0-9a-f]{64}", str(vo_sha)):
        errors.append(f"Invalid provenance field 'vo_sha256': must be 64-char hex, got '{vo_sha}'")
    
    # Gate 1: Non-empty
    if not events:
        errors.append("Event timeline is empty")
        return errors, warnings

    # Gate 2: Complete lifecycle with valid enum values (F-10)
    # The renderer defaults unknown values to generic/static behavior.
    # Fail closed here: reject unsupported enum values before render.
    SUPPORTED_ENTRANCES = {
        "kinetic_build", "fade_in", "pop_in", "slide_in", "donut_reveal",
        "count_up", "gauge_fill", "marker_drop", "marker_drop_positive",
        "wipe_in", "callout_in",
        "delta_badge", "delta_badge_positive",
    }
    SUPPORTED_PROGRESSIONS = {
        "hold", "hold_to_end", "hold_with_pulse", "word_highlight",
        "label_count_up", "count_up_to_value", "score_count_down",
        "progress_bar_fill", "arrow_draw", "arrow_draw_up",
        "marker_to_ideal", "check_reveal", "icon_animate",
    }
    SUPPORTED_EXITS = {
        "fade", "fade_with_next", "wipe_to_factors", "wipe_to_next",
        "morph_to_next", "morph_to_chart", "morph_to_example",
        "morph_to_tips", "morph_to_action", "morph_to_close",
        "morph_to_list", "morph_to_steps", "morph_to_story",
        "end_card", "persist", "persist_dimmed",
    }
    for e in events:
        eid = e.get("event_id", "?")
        for field, supported in [
            ("entrance", SUPPORTED_ENTRANCES),
            ("progression", SUPPORTED_PROGRESSIONS),
            ("exit", SUPPORTED_EXITS),
        ]:
            val = e.get(field)
            if not val:
                errors.append(f"{eid}: missing lifecycle field '{field}'")
            elif val not in supported:
                errors.append(
                    f"{eid}: unsupported {field} '{val}'. "
                    f"Supported: {sorted(supported)}"
                )

    # Gate 3: Valid visual types
    for e in events:
        eid = e.get("event_id", "?")
        vt = e.get("visual_type")
        if vt not in SUPPORTED_TYPES:
            errors.append(
                f"{eid}: unsupported visual_type '{vt}'. "
                f"Supported: {sorted(SUPPORTED_TYPES)}"
            )

    # Gate 4: Timing validity
    for e in events:
        eid = e.get("event_id", "?")
        sf = e.get("start_frame", -1)
        ef = e.get("end_frame", -1)
        if sf < 0:
            errors.append(f"{eid}: negative start_frame")
        if ef <= sf:
            errors.append(f"{eid}: end_frame ({ef}) <= start_frame ({sf})")

    # Gate 4b: No overlapping events (F-06)
    # Events are full-screen; overlap causes visual stacking/obscuring.
    sorted_by_start = sorted(events, key=lambda e: e["start_frame"])
    for i in range(1, len(sorted_by_start)):
        prev = sorted_by_start[i - 1]
        curr = sorted_by_start[i]
        if curr["start_frame"] < prev["end_frame"]:
            errors.append(
                f"Overlapping events: {curr['event_id']} starts at {curr['start_frame']} "
                f"but {prev['event_id']} ends at {prev['end_frame']}. "
                f"Events must not overlap (clip to next start)."
            )

    # Gate 5: Static hold ceiling
    sorted_events = sorted(events, key=lambda e: e["start_frame"])
    for i in range(1, len(sorted_events)):
        prev = sorted_events[i - 1]
        curr = sorted_events[i]
        gap_frames = curr["start_frame"] - prev["end_frame"]
        gap_s = gap_frames / FPS
        if gap_s > max_hold_s:
            errors.append(
                f"Static hold violation: {gap_s:.1f}s gap between "
                f"{prev['event_id']} (ends {prev['end_frame']}) and "
                f"{curr['event_id']} (starts {curr['start_frame']}). "
                f"Ceiling is {max_hold_s}s."
            )

    # Gate 6: Narration coverage (events must cover the voiceover)
    # The timeline must span from near-start to near-end of narration.
    # Leading gap >2s or trailing gap >2s fails (unless explicitly justified).
    narration_dur = timeline.get("narration_duration_s", 0)
    # F-15: narration_duration_s is required. Missing/zero must fail,
    # not silently skip the coverage gates.
    if not narration_dur or narration_dur <= 0:
        errors.append(
            "Missing or invalid 'narration_duration_s' — timeline must record "
            "narration duration for coverage validation"
        )
    if sorted_events:
        first_start = sorted_events[0]["start_frame"] / FPS
        last_end = sorted_events[-1]["end_frame"] / FPS
        span_s = last_end - first_start
        
        if span_s < 10:
            warnings.append(
                f"Timeline spans only {span_s:.1f}s — verify narration coverage"
            )
        
        if narration_dur > 0:
            # Leading gap check
            if first_start > 2.0:
                errors.append(
                    f"Leading gap too large: first event starts at {first_start:.1f}s "
                    f"(narration is {narration_dur:.1f}s). Events must start within 2s."
                )
            # Trailing gap check
            trailing_gap = narration_dur - last_end
            if trailing_gap > 2.0:
                errors.append(
                    f"Trailing gap too large: last event ends at {last_end:.1f}s "
                    f"but narration is {narration_dur:.1f}s (gap: {trailing_gap:.1f}s). "
                    f"Events must cover narration within 2s."
                )
            # Out-of-range check
            if last_end > narration_dur + 1.0:
                errors.append(
                    f"Event extends beyond narration: last end {last_end:.1f}s > "
                    f"narration {narration_dur:.1f}s + 1s tolerance"
                )

    # Gate 7: Word anchor validity
    for e in events:
        eid = e.get("event_id", "?")
        anchor = e.get("word_anchor", {})
        if not anchor.get("phrase"):
            errors.append(f"{eid}: word_anchor missing phrase")
        if anchor.get("word_index", -1) < 0:
            errors.append(f"{eid}: word_anchor has invalid word_index")

    return errors, warnings


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <event_timeline.json> [--max-hold 4.0]")
        sys.exit(1)

    timeline_path = sys.argv[1]
    max_hold = DEFAULT_MAX_HOLD_S
    if "--max-hold" in sys.argv:
        idx = sys.argv.index("--max-hold")
        max_hold = float(sys.argv[idx + 1])

    if not Path(timeline_path).exists():
        print(f"FATAL: Timeline not found: {timeline_path}", file=sys.stderr)
        sys.exit(1)

    errors, warnings = validate(timeline_path, max_hold)

    for w in warnings:
        print(f"⚠️  WARNING: {w}", file=sys.stderr)

    if errors:
        print(f"\n❌ TIMELINE VALIDATION FAILED ({len(errors)} errors):", file=sys.stderr)
        for e in errors:
            print(f"   • {e}", file=sys.stderr)
        sys.exit(1)

    print(f"✅ Timeline validation passed", file=sys.stderr)


if __name__ == "__main__":
    main()
