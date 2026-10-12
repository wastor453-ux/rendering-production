#!/usr/bin/env python3
"""
Word-Level Timestamp Estimation - ROOT FIX for visual/narration sync.

PROBLEM: Beats are scene-level (18-24s each). When VO says "payment history
is thirty-five percent," nothing happens on screen at that exact moment.
Visuals don't react to words.

SOLUTION: Estimate word-level timestamps from known script + measured voice duration.
- Uses the EXACT script text that generated the VO
- Distributes time proportionally by character length (longer words = more time)
- Adds pause time for punctuation (commas, periods, etc.)
- Anchors to measured voice_start and voice_end from voice_activity.py

This is not millisecond-perfect forced alignment, but it's structurally
better than scene-level beats. Visuals can now react to specific words.

For true forced alignment, install openai-whisper when disk space allows.
"""

import json
import sys
import re


def estimate_word_timestamps(script_text, voice_start, voice_end):
    """
    Estimate word-level timestamps from script text and voice bounds.
    
    Returns: [{"word": str, "start": float, "end": float}, ...]
    """
    # Split into words, keeping punctuation info
    # We need to account for pauses after punctuation
    tokens = re.findall(r"\S+", script_text)
    
    # Calculate weight for each token
    # Base weight = character count (longer words take longer)
    # Punctuation adds pause time
    weights = []
    for token in tokens:
        # Base: character count (alphanumeric only)
        clean = re.sub(r"[^a-zA-Z0-9]", "", token)
        weight = max(len(clean), 1)  # Minimum 1 for punctuation-only tokens
        
        # Punctuation pauses (in weight units)
        if token.endswith(".") or token.endswith("!") or token.endswith("?"):
            weight += 8  # Sentence end = longer pause
        elif token.endswith(",") or token.endswith(";") or token.endswith(":"):
            weight += 4  # Clause pause
        elif token.endswith("...") or "—" in token:
            weight += 6  # Dramatic pause
        
        weights.append(weight)
    
    total_weight = sum(weights)
    voice_duration = voice_end - voice_start
    
    # Distribute time proportionally
    words = []
    current_time = voice_start
    
    for token, weight in zip(tokens, weights):
        duration = (weight / total_weight) * voice_duration
        words.append({
            "word": token,
            "start": round(current_time, 3),
            "end": round(current_time + duration, 3),
        })
        current_time += duration
    
    return words


def generate_for_scenes(script_path, voice_bounds_path, output_path):
    """
    Generate word timestamps for all scenes.
    
    script_path: JSON with scenes [{scene_id, text}, ...]
    voice_bounds_path: JSON with per-scene voice bounds
    output_path: where to write word_timestamps.json
    """
    with open(script_path) as f:
        script_data = json.load(f)
    
    with open(voice_bounds_path) as f:
        bounds_data = json.load(f)
    
    scenes = script_data.get("scenes", script_data if isinstance(script_data, list) else [])
    
    result = {
        "scenes": [],
        "all_words": [],
    }
    
    for scene in scenes:
        scene_id = scene.get("scene_id", scene.get("id", "unknown"))
        text = scene.get("text", scene.get("script", ""))
        
        # Get voice bounds for this scene
        bounds = bounds_data.get(scene_id, bounds_data.get("scenes", {}).get(scene_id, {}))
        if not bounds:
            # Fallback: use sequential allocation
            print(f"Warning: No bounds for scene {scene_id}, skipping", file=sys.stderr)
            continue
        
        voice_start = bounds.get("voice_start", 0)
        voice_end = bounds.get("voice_end", 0)
        
        words = estimate_word_timestamps(text, voice_start, voice_end)
        
        result["scenes"].append({
            "scene_id": scene_id,
            "voice_start": voice_start,
            "voice_end": voice_end,
            "words": words,
        })
        result["all_words"].extend([
            {**w, "scene_id": scene_id} for w in words
        ])
    
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"Generated {len(result['all_words'])} word timestamps")
    print(f"Wrote to {output_path}")
    return result


def main():
    if len(sys.argv) == 4:
        # Batch mode: script.json bounds.json output.json
        generate_for_scenes(sys.argv[1], sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 2:
        # Single text mode: estimate from stdin text with 0-10s bounds
        text = open(sys.argv[1]).read()
        words = estimate_word_timestamps(text, 0, 10)
        print(json.dumps(words, indent=2))
    else:
        print("Usage:")
        print("  word_timestamps.py <script.json> <bounds.json> <output.json>")
        print("  word_timestamps.py <textfile>  (demo with 0-10s bounds)")
        sys.exit(1)


if __name__ == "__main__":
    main()
