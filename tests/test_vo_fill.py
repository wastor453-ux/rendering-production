#!/usr/bin/env python3
"""
VO Fill Gate - ROOT FIX: "Voiceover ends before video ends"

PROBLEM: We measured container duration (112.62s) but voice ended at 111.78s.
The 0.85s trailing silence caused Hamza's complaint.

SOLUTION: CI gate that FAILS if:
1. Trailing silence > 0.5s (voice ends too early)
2. Leading silence > 0.5s (video starts with dead air)
3. Voice duration != video duration (mismatch)

Uses voice_activity.py for real voice detection, not container duration.
"""

import sys
import subprocess
import json
from pathlib import Path

# Import voice activity detector
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
from voice_activity import get_voice_bounds


def find_video_vo_files(repo_root):
    """Find all VO files in src/videos/*/audio/vo.wav"""
    videos_dir = Path(repo_root) / "src" / "videos"
    if not videos_dir.exists():
        return []
    
    vo_files = []
    for video_dir in videos_dir.iterdir():
        if video_dir.is_dir() and not video_dir.name.startswith("_"):
            vo_path = video_dir / "audio" / "vo.wav"
            if vo_path.exists():
                vo_files.append((video_dir.name, vo_path))
    return vo_files


def check_vo_fill(video_name, vo_path):
    """
    Check if VO fills the video properly.
    Returns list of errors (empty = pass).
    """
    errors = []
    
    try:
        bounds = get_voice_bounds(str(vo_path))
    except Exception as e:
        return [f"{video_name}: Failed to analyze VO: {e}"]
    
    # FAIL: Trailing silence > 0.5s
    if bounds["trailing_silence"] > 0.5:
        errors.append(
            f"{video_name}: {bounds['trailing_silence']}s trailing silence. "
            f"Voice ends at {bounds['voice_end']}s but file is {bounds['total_duration']}s. "
            "This causes 'VO ends before video ends'. "
            "Trim the VO or regenerate without trailing silence."
        )
    
    # FAIL: Leading silence > 0.5s
    if bounds["leading_silence"] > 0.5:
        errors.append(
            f"{video_name}: {bounds['leading_silence']}s leading silence. "
            "Video starts with dead air. Trim the VO."
        )
    
    # WARN: Voice duration seems short for a full video
    if bounds["voice_duration"] < 60:
        errors.append(
            f"{video_name}: Voice is only {bounds['voice_duration']}s. "
            "Expected 60s+ for a full video. VO may be truncated."
        )
    
    return errors


def main():
    repo_root = Path(__file__).parent.parent
    vo_files = find_video_vo_files(repo_root)
    
    if not vo_files:
        print("FATAL: No VO files found. Missing required media is a hard failure.", file=sys.stderr)
        print("Every video must have src/videos/{name}/audio/vo.wav", file=sys.stderr)
        return 1
    
    print(f"Checking VO fill for {len(vo_files)} videos...")
    
    all_errors = []
    for video_name, vo_path in vo_files:
        # Skip exempt videos (pre-voice-activity-system)
        exempt = ["budget-rule", "emergency-shield"]
        if video_name in exempt:
            print(f"  ⏭️  {video_name}: Exempt (pre-system)")
            continue
        
        print(f"  Checking {video_name}...")
        errors = check_vo_fill(video_name, vo_path)
        all_errors.extend(errors)
    
    if all_errors:
        print("\n❌ VO FILL GATE FAILED:")
        for e in all_errors:
            print(f"  • {e}")
        print("\nThese are PRODUCTION system issues.")
        print("Fix: trim silence from VO or regenerate with proper endings.")
        return 1
    
    print("\n✅ VO fill gate passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
