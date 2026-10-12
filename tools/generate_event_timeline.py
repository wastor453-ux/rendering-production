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

import hashlib
import json
import sys
import re
from pathlib import Path
import os


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
        occurrence = pattern_def.get("occurrence", 1)
        word_idx, matched = find_word_anchor(words, pattern, occurrence)
        
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
    
    # F-06: Clip event durations to prevent overlap.
    # Each event ends at min(start + 4s ceiling, next event start).
    # This makes the "until next event or 4s max" comment actual behavior.
    MAX_HOLD_FRAMES = int(4 * FPS)
    for i in range(len(events)):
        start = events[i]["start_frame"]
        ceiling_end = start + MAX_HOLD_FRAMES
        if i + 1 < len(events):
            next_start = events[i + 1]["start_frame"]
            events[i]["end_frame"] = min(ceiling_end, next_start)
        else:
            events[i]["end_frame"] = ceiling_end
        # Fail closed: zero/negative duration means patterns are too dense
        if events[i]["end_frame"] <= events[i]["start_frame"]:
            raise RuntimeError(
                f"FATAL: Event {events[i]['event_id']} has zero/negative duration "
                f"(start={events[i]['start_frame']}, end={events[i]['end_frame']}). "
                f"Semantic patterns are too dense — events must not overlap."
            )
    
    # F-06: First event must cover from frame 0 (leading silence).
    # ONLY extend if the first event is a safe opening type (hero/title/hook).
    # Data types (gauge, delta, charts) must NOT be shown before their narration
    # anchor — extending them would place semantic content on screen early.
    # If the first event is a data type with a late anchor, the validator will
    # fail (leading gap), which is correct — the patterns need a proper opening.
    SAFE_OPENING_TYPES = {"hero_statement", "title_card", "hook", "opening", "kpi_card"}
    if events and events[0]["start_frame"] > 0:
        first_type = events[0].get("visual_type", "")
        if first_type in SAFE_OPENING_TYPES:
            events[0]["start_frame"] = 0
            events[0]["end_frame"] = min(events[0]["end_frame"], MAX_HOLD_FRAMES)
        # else: leave the gap; validator will fail closed (correct behavior)
    
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
    
    # Provenance: record hashes of both inputs
    def _sha256(path):
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    
    # Narration duration from alignment (last word end time)
    with open(alignment_path) as af:
        alignment_data = json.load(af)
    words = alignment_data.get("words", [])
    narration_duration_s = max((w.get("end", 0) for w in words), default=0)
    narration_end_frame = int(narration_duration_s * FPS)
    
    # Clip last event to narration duration (cannot extend beyond audio)
    if events:
        last = events[-1]
        if last["end_frame"] > narration_end_frame:
            last["end_frame"] = narration_end_frame
            # Ensure positive duration
            if last["end_frame"] <= last["start_frame"]:
                last["end_frame"] = last["start_frame"] + 1
    
    # F-15: Record VO hash for direct binding (not just via alignment)
    # Must match run_pipeline.py's preference: data/vo.wav first, then audio/vo.wav
    _video_dir = os.path.dirname(os.path.dirname(alignment_path))
    vo_path = None
    for _p in [os.path.join(_video_dir, "data", "vo.wav"),
               os.path.join(_video_dir, "audio", "vo.wav")]:
        if os.path.exists(_p):
            vo_path = _p
            break
    vo_sha = _sha256(vo_path) if vo_path else None
    output = {
        "source": "generate_event_timeline.py",
        "provenance": {
            "alignment_source": alignment_path,
            "alignment_sha256": _sha256(alignment_path),
            "patterns_source": patterns_path,
            "patterns_sha256": _sha256(patterns_path),
            "vo_sha256": vo_sha,
            "generator": "tools/generate_event_timeline.py",
        },
        "narration_duration_s": narration_duration_s,
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
