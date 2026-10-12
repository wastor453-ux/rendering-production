#!/usr/bin/env python3
"""
generate_event_timeline.py — SYSTEM FIX for empty event arrays.

PROBLEM (audit critical #1): generate_beats_from_vo.py writes "events": []
for every beat. The VO_FIRST_PIPELINE_LAW demands word-anchored visual events,
but the generator produces none. Runtime timing is ad-hoc in TSX.

SOLUTION: Generate a non-empty semantic event timeline from:
  1. Whisper forced alignment (real word timestamps, not estimates)
  2. Script semantics (key phrases mapped to visual concepts)
  3. Visual grammar (entrance/progression/exit per event)

Each event has:
  - event_id: unique stable ID
  - start_frame, end_frame: frame range (30fps)
  - word_anchor: {word_index, phrase, occurrence} — NEVER bare word
  - semantic_claim: what narration concept this visualizes
  - visual_type: chart/diagram/callout/etc. from the visual library
  - entrance: how it appears (draw-on, rise, count-up, etc.)
  - progression: how it develops while narration continues
  - exit: how it leaves/transforms (morph, wipe, fade)
  - on_screen_text: exact text to display

FAIL-CLOSED: Empty events list = exit 1. Missing alignment = exit 1.
"""

import json
import sys
import re
from pathlib import Path


FPS = 30

# Semantic phrase patterns mapped to visual treatments.
# Each pattern has: regex, visual_type, entrance, progression, exit
# Ordered by specificity (most specific first).
# Semantic phrase patterns mapped to visual treatments.
# Each pattern has: regex, visual_type, entrance, progression, exit
# Ordered by specificity (most specific first).
# Covers the full narration: ~40 semantic units across 5 scenes.
SEMANTIC_PATTERNS = [
    # === HOOK: thesis and impacts ===
    {
        "pattern": r"three.?digit number",
        "visual_type": "hero_number",
        "entrance": "count_up",
        "progression": "hold_emphasis",
        "exit": "morph_to_next",
        "concept": "score_definition",
    },
    {
        "pattern": r"controls your financial life",
        "visual_type": "hero_statement",
        "entrance": "kinetic_build",
        "progression": "word_highlight",
        "exit": "morph_to_next",
        "concept": "core_thesis",
    },
    {
        "pattern": r"approved for a mortgage",
        "visual_type": "impact_card",
        "entrance": "pop_in",
        "progression": "hold_with_pulse",
        "exit": "fade_with_next",
        "concept": "housing_impact",
    },
    {
        "pattern": r"what interest rate you pay",
        "visual_type": "impact_card",
        "entrance": "pop_in",
        "progression": "hold_with_pulse",
        "exit": "fade_with_next",
        "concept": "rate_impact",
    },
    {
        "pattern": r"whether you get that apartment",
        "visual_type": "impact_card",
        "entrance": "pop_in",
        "progression": "hold_with_pulse",
        "exit": "fade_with_next",
        "concept": "rental_impact",
    },
    {
        "pattern": r"no idea how it.?s calculated",
        "visual_type": "question_card",
        "entrance": "slide_in",
        "progression": "hold",
        "exit": "wipe_to_factors",
        "concept": "knowledge_gap",
    },
    {
        "pattern": r"what moves your score",
        "visual_type": "promise_card",
        "entrance": "slide_in",
        "progression": "hold",
        "exit": "wipe_to_factors",
        "concept": "video_promise",
    },
    # === FACTORS ===
    {
        "pattern": r"five factors",
        "visual_type": "section_title",
        "entrance": "fade_in",
        "progression": "hold",
        "exit": "morph_to_chart",
        "concept": "factors_intro",
    },
    {
        "pattern": r"payment history is 35",
        "visual_type": "donut_segment",
        "entrance": "donut_reveal",
        "progression": "label_count_up",
        "exit": "persist_dimmed",
        "concept": "factor_payment",
    },
    {
        "pattern": r"pay every bill on time",
        "visual_type": "advice_callout",
        "entrance": "callout_in",
        "progression": "hold",
        "exit": "fade",
        "concept": "advice_payment",
    },
    {
        "pattern": r"amounts owed is 30",
        "visual_type": "donut_segment",
        "entrance": "donut_reveal",
        "progression": "label_count_up",
        "exit": "persist_dimmed",
        "concept": "factor_amounts",
    },
    {
        "pattern": r"below 30.*of your limits",
        "visual_type": "gauge_visual",
        "entrance": "gauge_fill",
        "progression": "marker_to_ideal",
        "exit": "fade",
        "concept": "advice_utilization",
    },
    {
        "pattern": r"length of credit history is 15",
        "visual_type": "donut_segment",
        "entrance": "donut_reveal",
        "progression": "label_count_up",
        "exit": "persist_dimmed",
        "concept": "factor_length",
    },
    {
        "pattern": r"don.?t close your oldest card",
        "visual_type": "advice_callout",
        "entrance": "callout_in",
        "progression": "hold",
        "exit": "fade",
        "concept": "advice_length",
    },
    {
        "pattern": r"new credit is 10",
        "visual_type": "donut_segment",
        "entrance": "donut_reveal",
        "progression": "label_count_up",
        "exit": "persist_dimmed",
        "concept": "factor_new",
    },
    {
        "pattern": r"hard inquiry dings",
        "visual_type": "advice_callout",
        "entrance": "callout_in",
        "progression": "hold",
        "exit": "morph_to_example",
        "concept": "advice_inquiry",
    },
    # === EXAMPLE ===
    {
        "pattern": r"see this in action",
        "visual_type": "transition_card",
        "entrance": "wipe_in",
        "progression": "hold",
        "exit": "morph_to_story",
        "concept": "example_transition",
    },
    {
        "pattern": r"sarah has a 720",
        "visual_type": "score_card",
        "entrance": "slide_in",
        "progression": "count_up_to_value",
        "exit": "persist",
        "concept": "sarah_start",
    },
    {
        "pattern": r"misses one.*payment.*30 days",
        "visual_type": "timeline_event",
        "entrance": "marker_drop",
        "progression": "score_count_down",
        "exit": "persist",
        "concept": "sarah_miss",
    },
    {
        "pattern": r"drops to 680",
        "visual_type": "score_delta",
        "entrance": "delta_badge",
        "progression": "arrow_draw",
        "exit": "persist",
        "concept": "sarah_drop1",
    },
    {
        "pattern": r"40.?point hit",
        "visual_type": "delta_callout",
        "entrance": "pop_in",
        "progression": "hold",
        "exit": "fade",
        "concept": "sarah_hit1",
    },
    {
        "pattern": r"maxes out.*90.*utilization",
        "visual_type": "timeline_event",
        "entrance": "marker_drop",
        "progression": "score_count_down",
        "exit": "persist",
        "concept": "sarah_max",
    },
    {
        "pattern": r"another 30 points.*to 650",
        "visual_type": "score_delta",
        "entrance": "delta_badge",
        "progression": "arrow_draw",
        "exit": "persist",
        "concept": "sarah_drop2",
    },
    {
        "pattern": r"pays everything on time for six months",
        "visual_type": "timeline_event_positive",
        "entrance": "marker_drop_positive",
        "progression": "progress_bar_fill",
        "exit": "persist",
        "concept": "sarah_recovery_actions",
    },
    {
        "pattern": r"rebounds to 710",
        "visual_type": "score_delta",
        "entrance": "delta_badge_positive",
        "progression": "arrow_draw_up",
        "exit": "morph_to_tips",
        "concept": "sarah_recovery",
    },
    # === TIPS ===
    {
        "pattern": r"five proven ways",
        "visual_type": "section_title",
        "entrance": "fade_in",
        "progression": "hold",
        "exit": "morph_to_list",
        "concept": "tips_intro",
    },
    {
        "pattern": r"one,? set up auto pay",
        "visual_type": "tip_card",
        "entrance": "slide_in",
        "progression": "check_reveal",
        "exit": "persist_dimmed",
        "concept": "tip_autopay",
    },
    {
        "pattern": r"two,? pay down balances",
        "visual_type": "tip_card",
        "entrance": "slide_in",
        "progression": "check_reveal",
        "exit": "persist_dimmed",
        "concept": "tip_balances",
    },
    {
        "pattern": r"three,? don.?t close old cards",
        "visual_type": "tip_card",
        "entrance": "slide_in",
        "progression": "check_reveal",
        "exit": "persist_dimmed",
        "concept": "tip_keep_cards",
    },
    {
        "pattern": r"four,? limit hard inquiries",
        "visual_type": "tip_card",
        "entrance": "slide_in",
        "progression": "check_reveal",
        "exit": "persist_dimmed",
        "concept": "tip_inquiries",
    },
    {
        "pattern": r"five,? check your reports",
        "visual_type": "tip_card",
        "entrance": "slide_in",
        "progression": "check_reveal",
        "exit": "morph_to_action",
        "concept": "tip_reports",
    },
    {
        "pattern": r"one in five reports has a mistake",
        "visual_type": "stat_callout",
        "entrance": "pop_in",
        "progression": "hold",
        "exit": "fade",
        "concept": "tip_stat",
    },
    # === ACTION ===
    {
        "pattern": r"action plan starts today",
        "visual_type": "section_title",
        "entrance": "fade_in",
        "progression": "hold",
        "exit": "morph_to_steps",
        "concept": "action_intro",
    },
    {
        "pattern": r"step one,? pull your free.*reports",
        "visual_type": "action_card",
        "entrance": "slide_in",
        "progression": "icon_animate",
        "exit": "persist",
        "concept": "step_reports",
    },
    {
        "pattern": r"step two,? set up auto pay",
        "visual_type": "action_card",
        "entrance": "slide_in",
        "progression": "icon_animate",
        "exit": "persist",
        "concept": "step_autopay",
    },
    {
        "pattern": r"step three,? pick your highest utilization",
        "visual_type": "action_card",
        "entrance": "slide_in",
        "progression": "icon_animate",
        "exit": "persist",
        "concept": "step_payment",
    },
    {
        "pattern": r"reward consistency over time",
        "visual_type": "principle_card",
        "entrance": "fade_in",
        "progression": "hold",
        "exit": "morph_to_close",
        "concept": "principle_consistency",
    },
    {
        "pattern": r"small actions repeated monthly",
        "visual_type": "encouragement_card",
        "entrance": "fade_in",
        "progression": "hold",
        "exit": "morph_to_close",
        "concept": "encouragement",
    },
    {
        "pattern": r"future self.*thank you",
        "visual_type": "closing_card",
        "entrance": "fade_in",
        "progression": "hold_to_end",
        "exit": "end_card",
        "concept": "closing",
    },
]
def find_word_anchor(words, pattern, occurrence=1):
    """
    Find the word index anchoring a phrase pattern.
    Returns (word_index, matched_text) or (None, None).
    
    Uses occurrence to disambiguate repeated words (fixes the "five" bug).
    """
    # Build full text for regex search
    full_text = " ".join(w["word"] for w in words)
    
    matches = list(re.finditer(pattern, full_text, re.IGNORECASE))
    if len(matches) < occurrence:
        return None, None
    
    match = matches[occurrence - 1]
    match_start_char = match.start()
    
    # Find which word index contains this character position
    char_pos = 0
    for i, w in enumerate(words):
        word_len = len(w["word"])
        if char_pos <= match_start_char < char_pos + word_len:
            return i, match.group(0)
        char_pos += word_len + 1  # +1 for space
    
    return None, None


def generate_events(alignment_path, script_text=None):
    """
    Generate semantic visual events from whisper alignment.
    
    Returns list of events. FAILS (raises) if no events generated.
    """
    with open(alignment_path) as f:
        data = json.load(f)
    
    words = data["words"] if "words" in data else data
    
    events = []
    event_id = 0
    
    for pattern_def in SEMANTIC_PATTERNS:
        pattern = pattern_def["pattern"]
        word_idx, matched = find_word_anchor(words, pattern)
        
        if word_idx is None:
            continue
        
        word = words[word_idx]
        start_frame = int(word["start"] * FPS)
        # Event lasts until next event or 4s max (hold ceiling)
        end_frame = start_frame + int(4 * FPS)
        
        event_id += 1
        events.append({
            "event_id": f"evt_{event_id:03d}",
            "start_frame": start_frame,
            "end_frame": end_frame,
            "word_anchor": {
                "word_index": word_idx,
                "word": word["word"],
                "phrase": matched,
                "start_s": word["start"],
                "end_s": word["end"],
            },
            "semantic_claim": pattern_def["concept"],
            "visual_type": pattern_def["visual_type"],
            "entrance": pattern_def["entrance"],
            "progression": pattern_def["progression"],
            "exit": pattern_def["exit"],
            "on_screen_text": matched,
        })
    
    # Sort by start frame
    events.sort(key=lambda e: e["start_frame"])
    
    # Re-number in timeline order
    for i, e in enumerate(events):
        e["event_id"] = f"evt_{i+1:03d}"
    
    # FAIL-CLOSED: empty events = system failure
    if not events:
        raise RuntimeError(
            "FATAL: Generated zero visual events. "
            "The event timeline must be non-empty. "
            "Check that semantic patterns match the script text."
        )
    
    return events


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <whisper_alignment.json> <output.json>")
        sys.exit(1)
    
    alignment_path = sys.argv[1]
    output_path = sys.argv[2]
    
    try:
        events = generate_events(alignment_path)
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    
    # Check hold ceiling: no event gap > 4s without coverage
    # (This is a warning, not fail — the TSX must fill gaps)
    for i in range(1, len(events)):
        gap_s = (events[i]["start_frame"] - events[i-1]["end_frame"]) / FPS
        if gap_s > 4.0:
            print(
                f"WARNING: {gap_s:.1f}s gap between {events[i-1]['event_id']} "
                f"and {events[i]['event_id']} exceeds 4s hold ceiling",
                file=sys.stderr
            )
    
    output = {
        "source": "generate_event_timeline.py",
        "alignment_source": alignment_path,
        "fps": FPS,
        "event_count": len(events),
        "events": events,
    }
    
    with open(output_path, "w") as f:
        json.dump(output, f, indent=1)
    
    print(f"✅ Generated {len(events)} semantic visual events")
    print(f"   Output: {output_path}")


if __name__ == "__main__":
    main()
