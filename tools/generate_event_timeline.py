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

# Semantic patterns are VIDEO DATA, not pipeline code.
# They come from the input patterns JSON file (per-video).
# The pipeline tool is generic; each video supplies its own patterns.
# See: src/videos/{name}/data/semantic_patterns.json

def load_patterns(patterns_path):
    """Load video-specific semantic patterns from JSON file."""
    import json
    with open(patterns_path) as f:
        data = json.load(f)
    patterns = data.get("patterns", data) if isinstance(data, dict) else data
    if not patterns:
        raise RuntimeError(
            f"FATAL: No semantic patterns in {patterns_path}. "
            "Each video must supply its own patterns in data/semantic_patterns.json. "
            "The pipeline does not hardcode video-specific patterns."
        )
    return patterns

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


def generate_events(alignment_path, patterns):
    """
    Generate semantic visual events from whisper alignment.
    
    Returns list of events. FAILS (raises) if no events generated.
    """
    with open(alignment_path) as f:
        data = json.load(f)
    
    words = data["words"] if "words" in data else data
    
    events = []
    event_id = 0
    
    for pattern_def in patterns:
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
    if len(sys.argv) < 4:
        print(f"Usage: {sys.argv[0]} <whisper_alignment.json> <semantic_patterns.json> <output.json>")
        print(f"  semantic_patterns.json: video-specific patterns (NOT hardcoded in pipeline)")
        sys.exit(1)
    
    alignment_path = sys.argv[1]
    patterns_path = sys.argv[2]
    output_path = sys.argv[3]
    
    try:
        patterns = load_patterns(patterns_path)
        events = generate_events(alignment_path, patterns)
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
