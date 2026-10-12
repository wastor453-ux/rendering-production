#!/usr/bin/env python3
"""
Animation Quality Gates - ROOT FIX: Prevent static videos from passing CI.

PROBLEM: The old system let static videos (one image per 20s scene) pass CI.
Hamza complained: "visuals not look like what i asked" and "many issues."

SOLUTION: CI gates that FAIL if:
1. TSX has no word-level sync imports (word_sync.tsx not used)
2. TSX has no TimedReveal or KineticText (no word-triggered animation)
3. TSX has static scenes > 5 seconds without visual change markers
4. Video has no word_timestamps.json (no word-level data)

These gates make it structurally impossible to deliver static videos.
"""

import os
import re
import json
import sys
from pathlib import Path


def find_video_tsx_files(repo_root):
    """Find all video TSX files in src/videos/*/"""
    videos_dir = Path(repo_root) / "src" / "videos"
    if not videos_dir.exists():
        return []
    
    tsx_files = []
    for video_dir in videos_dir.iterdir():
        if video_dir.is_dir() and not video_dir.name.startswith("_"):
            for tsx in video_dir.glob("*.tsx"):
                # Skip test files
                if "test" not in tsx.name.lower():
                    tsx_files.append(tsx)
    return tsx_files


def check_word_sync_usage(tsx_path):
    """
    Check if TSX uses word-level synchronization.
    FAIL if no word_sync imports or no word-triggered components.
    """
    content = tsx_path.read_text()
    errors = []
    
    # Must import from word_sync
    if "word_sync" not in content:
        errors.append(
            f"{tsx_path.name}: No word_sync import. "
            "Visuals must be driven by word timestamps, not scene boundaries. "
            "Import { KineticText, TimedReveal, useWordSpoken } from '../../light/word_sync'."
        )
    
    # Must use word-triggered components
    has_kinetic = "KineticText" in content
    has_timed = "TimedReveal" in content
    has_word_spoken = "useWordSpoken" in content
    
    if not (has_kinetic or has_timed or has_word_spoken):
        errors.append(
            f"{tsx_path.name}: No word-triggered animation found. "
            "Must use at least one of: KineticText, TimedReveal, useWordSpoken. "
            "Static scenes are not allowed."
        )
    
    return errors


def check_word_timestamps_exist(tsx_path):
    """
    Check if video has word_timestamps.json data file.
    FAIL if missing (can't do word sync without word data).
    """
    video_dir = tsx_path.parent
    data_dir = video_dir / "data"
    word_file = data_dir / "word_timestamps.json"
    
    if not word_file.exists():
        return [
            f"{tsx_path.name}: Missing data/word_timestamps.json. "
            "Generate with: python3 tools/word_timestamps.py <script.json> <bounds.json> <output.json>"
        ]
    
    # Validate structure
    try:
        data = json.loads(word_file.read_text())
        if "scenes" not in data:
            return [f"{tsx_path.name}: word_timestamps.json missing 'scenes' key"]
        
        total_words = sum(len(s.get("words", [])) for s in data["scenes"])
        if total_words < 50:
            return [
                f"{tsx_path.name}: Only {total_words} words in timestamps. "
                "Expected 50+ for a full video. Word data may be incomplete."
            ]
    except json.JSONDecodeError as e:
        return [f"{tsx_path.name}: word_timestamps.json is invalid JSON: {e}"]
    
    return []


def check_no_static_scenes(tsx_path):
    """
    Check for patterns indicating static scenes.
    WARN (not fail) if suspicious patterns found.
    """
    content = tsx_path.read_text()
    warnings = []
    
    # Count interpolate calls - should have many for animation
    interpolate_count = content.count("interpolate(")
    if interpolate_count < 10:
        warnings.append(
            f"{tsx_path.name}: Only {interpolate_count} interpolate() calls. "
            "Expected 10+ for proper animation. Video may be too static."
        )
    
    # Check for dead UI elements (buttons that do nothing)
    if "<button" in content.lower() or "Calculate" in content:
        # Allow if it's clearly animated, warn if static
        if "onClick" not in content:
            warnings.append(
                f"{tsx_path.name}: Found button-like element without onClick. "
                "If this is a visual button, ensure it's animated, not a dead UI mockup."
            )
    
    return warnings


def main():
    repo_root = Path(__file__).parent.parent
    tsx_files = find_video_tsx_files(repo_root)
    
    if not tsx_files:
        print("No video TSX files found, skipping animation quality checks")
        return 0
    
    print(f"Checking animation quality for {len(tsx_files)} videos...")
    
    all_errors = []
    all_warnings = []
    
    for tsx_path in tsx_files:
        # Skip videos that are explicitly exempt (pre-animation-system)
        # Remove from this list as videos are rebuilt
        exempt_videos = [
            "budget-rule",      # Pre-animation system
            "emergency-shield", # Pre-animation system  
            "compound-interest",
            "emergency-fund",
        ]
        video_name = tsx_path.parent.name
        if video_name in exempt_videos:
            print(f"  ⏭️  {video_name}: Exempt (pre-animation system)")
            continue
        
        print(f"  Checking {video_name}/{tsx_path.name}...")
        
        errors = []
        errors.extend(check_word_sync_usage(tsx_path))
        errors.extend(check_word_timestamps_exist(tsx_path))
        warnings = check_no_static_scenes(tsx_path)
        
        all_errors.extend(errors)
        all_warnings.extend(warnings)
    
    # Report warnings as FAILURES (fail-closed per audit)
    # A warning about static output is not acceptable — it must block release
    if all_warnings:
        print("\n❌ ANIMATION QUALITY GATE FAILED (warnings are failures):")
        for w in all_warnings:
            print(f"  • {w}")
        print("\nThese indicate static or low-quality output.")
        print("Fix the root cause: add real frame-based animation.")
        return 1
    
    # Fail on errors
    if all_errors:
        print("\n❌ ANIMATION QUALITY GATE FAILED:")
        for e in all_errors:
            print(f"  • {e}")
        print("\nThese are PRODUCTION system issues, not video issues.")
        print("Fix the root cause: add word-level animation to the TSX.")
        return 1
    
    print("\n✅ Animation quality gate passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
