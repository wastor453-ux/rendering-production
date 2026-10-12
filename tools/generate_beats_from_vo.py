#!/usr/bin/env python3
"""
generate_beats_from_vo.py — TRUE ROOT FIX for VO/visual mismatch.

PROBLEM: Human types beat timings by hand. Human makes mistakes.
  "start_time": 0, "end_time": 36  <- I typed this. Wrong.

TRUE FIX: Beats are GENERATED from VO measurements. No human types durations.
  1. VO wav file exists (generated first per VO-FIRST law)
  2. Script measures each scene with ffprobe (millisecond precision)
  3. Script outputs beat_timeline.json with MEASURED timings
  4. Impossible to mismatch — numbers come from measurement, not typing.

Usage:
    python3 generate_beats_from_vo.py <video-name> <script.json>

    script.json format:
    {
      "scenes": [
        {"id": "hook", "text": "What if I told you..."},
        {"id": "rule", "text": "The fifty thirty twenty rule..."}
      ]
    }

    Expects VO parts at: src/videos/{name}/audio/{scene_id}.wav
    Outputs: src/videos/{name}/data/beat_timeline.json
"""
import json
import os
import subprocess
import sys

def measure_wav(path):
    """Measure WAV duration in seconds with ffprobe (ms precision)."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed for {path}: {result.stderr}")
    return float(result.stdout.strip())

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <video-name> <script.json>")
        sys.exit(1)

    video_name = sys.argv[1]
    script_path = sys.argv[2]

    video_dir = os.path.join("src", "videos", video_name)
    audio_dir = os.path.join(video_dir, "audio")
    data_dir = os.path.join(video_dir, "data")

    with open(script_path) as f:
        script = json.load(f)

    beats = []
    current_time = 0.0

    for i, scene in enumerate(script["scenes"]):
        scene_id = scene["id"]
        wav_path = os.path.join(audio_dir, f"{scene_id}.wav")

        if not os.path.isfile(wav_path):
            print(f"FATAL: Missing VO file: {wav_path}")
            print(f"Generate VO first per VO-FIRST law. Cannot invent timings.")
            sys.exit(1)

        # MEASURE — not estimate, not type by hand
        duration = measure_wav(wav_path)
        start_time = current_time
        end_time = current_time + duration

        # Word count for reading-time validation
        word_count = len(scene["text"].split())

        beat = {
            "beat_id": f"{video_name}_{scene_id}",
            "start_time": round(start_time, 3),
            "end_time": round(end_time, 3),
            "start_word": scene["text"].split()[0] if word_count > 0 else "",
            "end_word": scene["text"].split()[-1] if word_count > 0 else "",
            "semantic_role": scene.get("role", "body"),
            "claim": scene["text"][:200],
            "visual_verb": scene.get("visual_verb", "show"),
            "focal_object": scene.get("focal_object", ""),
            "duration_class": "long" if duration > 20 else "medium" if duration > 10 else "short",
            "intensity": scene.get("intensity", "medium"),
            "music_intensity": scene.get("music_intensity", "low"),
            "sfx_policy": "minimal",
            "events": [],
            "visual_mode": scene.get("visual_mode", "data_atmosphere"),
            "visual_reason": f"Auto-generated from measured VO ({duration:.1f}s)",
        }
        beats.append(beat)
        current_time = end_time

        print(f"  {scene_id}: {duration:.2f}s ({start_time:.2f} → {end_time:.2f})")

    os.makedirs(data_dir, exist_ok=True)
    output_path = os.path.join(data_dir, "beat_timeline.json")
    with open(output_path, "w") as f:
        json.dump(beats, f, indent=2)

    total = current_time
    print(f"\n✅ Generated {len(beats)} beats, total {total:.2f}s")
    print(f"   Output: {output_path}")
    print(f"   All timings MEASURED from VO. Mismatch impossible.")

if __name__ == "__main__":
    main()
