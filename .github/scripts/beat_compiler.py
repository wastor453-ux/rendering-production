#!/usr/bin/env python3
"""P4.4 P0-2: Minimal executable beat compiler.

Takes narration with word-level timings and produces semantic beats
per EDITORIAL_BRAIN.md rules. This is the missing link between narration
meaning and the visual selector.

Input: List of {word, start, end} dicts (from whisper alignment).
Output: List of beats with semantic evidence for selectVisualMode().

Beat rules (from EDITORIAL_BRAIN.md):
- Max 2.5s focal hold per beat
- Pauses group beats (pause > 0.8s = beat boundary)
- Each beat gets semantic_role, visual_verb, focal_object
- event_id is the join key across narration/visuals/sound/QA

Usage:
    from beat_compiler import compile_beats
    beats = compile_beats(word_timings, narration_text)
"""

import re
from typing import List, Dict, Any


# Semantic role keywords (from VISUAL_BRAIN §2)
ROLE_KEYWORDS = {
    "number": ["percent", "%", "dollar", "$", "million", "billion", "thousand",
               "increased", "decreased", "rose", "fell", "dropped", "grew"],
    "comparison": ["versus", "vs", "compared", "than", "while", "whereas",
                   "on the other hand"],
    "trend": ["over time", "since", "from", "to", "growing", "shrinking",
              "trend", "trajectory"],
    "mechanism": ["because", "causes", "leads to", "results in", "drives",
                  "mechanism", "how"],
    "consequence": ["therefore", "so", "thus", "consequence", "result",
                    "impact", "effect"],
    "thesis": ["believe", "think", "argue", "thesis", "point is", "key is"],
}


def detect_semantic_role(text: str) -> str:
    """Detect the semantic role of a text segment."""
    text_lower = text.lower()
    for role, keywords in ROLE_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return role
    # Default: claim (a statement of fact or argument)
    return "claim"


def detect_visual_verb(text: str, role: str) -> str:
    """Detect the visual verb (what the visual should DO)."""
    text_lower = text.lower()
    if role == "number":
        if any(w in text_lower for w in ["rose", "grew", "increased", "up"]):
            return "rise"
        if any(w in text_lower for w in ["fell", "dropped", "decreased", "down"]):
            return "fall"
        return "reveal"
    if role == "comparison":
        return "contrast"
    if role == "trend":
        return "trace"
    if role == "mechanism":
        return "explain"
    if role == "consequence":
        return "impact"
    if role == "thesis":
        return "assert"
    return "present"


def compile_beats(word_timings: List[Dict[str, Any]],
                  narration_text: str = "") -> List[Dict[str, Any]]:
    """Compile word timings into semantic beats.

    Args:
        word_timings: List of {word, start, end} (seconds).
        narration_text: Full narration text (for context).

    Returns:
        List of beat dicts with:
        - id: beat_001, beat_002, ...
        - start, end: seconds
        - start_frame, end_frame: at 30fps
        - text: the words in this beat
        - semantic_role: claim|number|comparison|trend|mechanism|etc.
        - visual_verb: rise|fall|contrast|trace|explain|etc.
        - focal_object: key noun phrase (simple extraction)
        - event_id: evt_beat_001, ...
        - visual_impact_frame: frame of the key word (for SFX sync)
    """
    if not word_timings:
        return []

    beats = []
    current_words = []
    current_start = word_timings[0]["start"]
    beat_id = 1

    PAUSE_THRESHOLD = 0.8  # seconds — pause groups beats
    MAX_BEAT_DURATION = 2.5  # seconds — max focal hold

    for i, wt in enumerate(word_timings):
        current_words.append(wt)

        # Check if this is a beat boundary
        is_last = (i == len(word_timings) - 1)
        pause_after = 0
        if not is_last:
            pause_after = word_timings[i + 1]["start"] - wt["end"]

        duration = wt["end"] - current_start
        boundary = (
            is_last or
            pause_after > PAUSE_THRESHOLD or
            duration >= MAX_BEAT_DURATION
        )

        if boundary:
            # Finalize this beat
            text = " ".join(w["word"] for w in current_words)
            role = detect_semantic_role(text)
            verb = detect_visual_verb(text, role)

            # Focal object: longest noun-like word (simple heuristic)
            words = [w["word"].strip(".,!?;:") for w in current_words]
            focal = max(words, key=len) if words else ""

            # Visual impact frame: middle of the beat (key moment)
            # For numbers, use the frame of the number word
            impact_word_idx = len(current_words) // 2
            if role == "number":
                for idx, w in enumerate(current_words):
                    if any(c.isdigit() for c in w["word"]):
                        impact_word_idx = idx
                        break
            impact_time = current_words[impact_word_idx]["start"]
            impact_frame = int(impact_time * 30)

            beat = {
                "id": f"beat_{beat_id:03d}",
                "event_id": f"evt_beat_{beat_id:03d}",
                "start": round(current_start, 3),
                "end": round(wt["end"], 3),
                "start_frame": int(current_start * 30),
                "end_frame": int(wt["end"] * 30),
                "text": text,
                "semantic_role": role,
                "visual_verb": verb,
                "focal_object": focal,
                "visual_impact_frame": impact_frame,
            }
            beats.append(beat)

            # Reset for next beat
            beat_id += 1
            current_words = []
            if not is_last:
                current_start = word_timings[i + 1]["start"]

    return beats


def beats_to_selector_evidence(beats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert beats to SemanticEvidence for selectVisualMode().

    Maps beat fields to the selector's expected input format.
    """
    evidence = []
    for beat in beats:
        ev = {
            "semantic_role": beat["semantic_role"],
            "claim": beat["text"],
            "visual_verb": beat["visual_verb"],
            "focal_object": beat["focal_object"],
            # Heuristics for selector
            "number_presence": beat["semantic_role"] == "number",
            "comparison_state": "A_vs_B" if beat["semantic_role"] == "comparison" else "none",
            "trend_presence": "up" if beat["visual_verb"] == "rise" else (
                "down" if beat["visual_verb"] == "fall" else "none"
            ),
            "narrative_intensity": 3,  # Default; refined by human or LLM
            "information_density": 2,  # Default
        }
        evidence.append(ev)
    return evidence


if __name__ == "__main__":
    # Self-test with sample data
    sample = [
        {"word": "Your", "start": 0.0, "end": 0.3},
        {"word": "money", "start": 0.3, "end": 0.6},
        {"word": "is", "start": 0.6, "end": 0.8},
        {"word": "dying", "start": 0.8, "end": 1.2},
        # Pause > 0.8s = beat boundary
        {"word": "while", "start": 2.5, "end": 2.8},
        {"word": "you", "start": 2.8, "end": 3.0},
        {"word": "sleep.", "start": 3.0, "end": 3.5},
    ]
    beats = compile_beats(sample)
    print(f"Compiled {len(beats)} beats:")
    for b in beats:
        print(f"  {b['id']}: [{b['start']:.1f}s-{b['end']:.1f}s] "
              f"role={b['semantic_role']} verb={b['visual_verb']} "
              f"impact_frame={b['visual_impact_frame']}")
        print(f"    text: {b['text'][:60]}...")
