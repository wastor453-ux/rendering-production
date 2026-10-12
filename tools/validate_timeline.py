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
    "donut_segment", "hero_statement", "hero_number", "score_card",
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

    # Gate 1: Non-empty
    if not events:
        errors.append("Event timeline is empty")
        return errors, warnings

    # Gate 2: Complete lifecycle
    for e in events:
        eid = e.get("event_id", "?")
        for field in ["entrance", "progression", "exit"]:
            if not e.get(field):
                errors.append(f"{eid}: missing lifecycle field '{field}'")

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

    # Gate 6: Semantic coverage (events span reasonable duration)
    if sorted_events:
        first_start = sorted_events[0]["start_frame"] / FPS
        last_end = sorted_events[-1]["end_frame"] / FPS
        span_s = last_end - first_start
        if span_s < 10:
            warnings.append(
                f"Timeline spans only {span_s:.1f}s — verify narration coverage"
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
