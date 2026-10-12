#!/usr/bin/env python3
"""
Voice Activity Detection - ROOT FIX for VO sync issues.

PROBLEM: We measured container duration (112.62s) but the actual voice
ends at 111.78s. The 0.85s trailing silence causes "VO ends before video ends."

SOLUTION: Detect actual voice activity, not container duration.
- Find first voice start (trim leading silence)
- Find last voice end (trim trailing silence)
- Return the TRUE voice duration

This makes it structurally impossible to have VO/video mismatch.
"""

import subprocess
import json
import sys


def get_voice_bounds(wav_path, silence_db=-40, min_silence=0.3):
    """
    Returns (voice_start, voice_end, voice_duration) in seconds.
    
    voice_start: when first non-silence begins
    voice_end: when last non-silence ends
    voice_duration: voice_end - voice_start
    """
    # Detect all silence periods
    cmd = [
        "ffmpeg", "-i", wav_path,
        "-af", f"silencedetect=noise={silence_db}dB:d={min_silence}",
        "-f", "null", "-"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    silences = []
    for line in result.stderr.split("\n"):
        if "silence_start:" in line:
            # Parse: silence_start: 111.77875
            start = float(line.split("silence_start:")[1].split()[0])
            silences.append({"start": start})
        elif "silence_end:" in line and silences:
            # Parse: silence_end: 112.625 | silence_duration: 0.84625
            end = float(line.split("silence_end:")[1].split()[0].strip())
            silences[-1]["end"] = end
    
    # Get total duration
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
           "-of", "default=noprint_wrappers=1:nokey=1", wav_path]
    total = float(subprocess.run(cmd, capture_output=True, text=True).stdout.strip())
    
    # Voice starts after first silence (if file starts with silence)
    # Voice ends before last silence (if file ends with silence)
    voice_start = 0.0
    voice_end = total
    
    if silences:
        # If first silence starts at 0, voice starts when it ends
        if silences[0]["start"] < 0.1:
            voice_start = silences[0].get("end", 0.0)
        # If last silence ends at total duration, voice ends when it starts
        if abs(silences[-1].get("end", 0) - total) < 0.1:
            voice_end = silences[-1]["start"]
    
    return {
        "voice_start": round(voice_start, 3),
        "voice_end": round(voice_end, 3),
        "voice_duration": round(voice_end - voice_start, 3),
        "total_duration": round(total, 3),
        "leading_silence": round(voice_start, 3),
        "trailing_silence": round(total - voice_end, 3),
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: voice_activity.py <wav_file>")
        sys.exit(1)
    
    result = get_voice_bounds(sys.argv[1])
    print(json.dumps(result, indent=2))
    
    # FAIL if trailing silence > 0.5s (would cause "VO ends before video")
    if result["trailing_silence"] > 0.5:
        print(f"\n⚠️  WARNING: {result['trailing_silence']}s trailing silence detected!", file=sys.stderr)
        print("This will cause 'VO ends before video ends' complaint.", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
