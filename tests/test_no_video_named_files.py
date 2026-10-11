#!/usr/bin/env python3
"""
Pipeline-generic guard (2026-10-11, Hamza's law).

Fails CI if anyone reintroduces video-specific files or hardcoded video names.
The pipeline must work for any video without per-video files.

Guards:
1. assets/sfx/ must not contain video-named event files (*_events.json, *_assetmap.json)
2. Workflow must not derive file paths from video names (SFX_SLUG pattern)
3. No src/{videoname}/ directories for retired test videos
4. Tests must not hardcode retired video names

Run: python3 -m pytest tests/test_no_video_named_files.py -v
"""
import os
import re
import unittest

REPO_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

# Retired video names that must never reappear as files/folders/identifiers.
# (Not a production dependency — this is a guard allowlist.)
RETIRED_VIDEOS = [
    "housingbroke",
    "hb_p1", "hb_p2", "hb_p3", "hb_p4", "hb_p5", "hb_p6", "hb_p7",
]

# Video-name derivation patterns that indicate per-video file logic.
FORBIDDEN_PATTERNS = [
    r'SFX_SLUG',                          # old video-name derivation
    r'\$\{SFX_SLUG\}',                  # variable usage
    r'tr\s+[\'"]\[:upper:\][\'"]',    # case-conversion for slug derivation
]


class TestNoVideoNamedFiles(unittest.TestCase):
    def test_no_video_event_files_in_sfx(self):
        """assets/sfx/ must not contain video-named event files."""
        sfx_dir = os.path.join(REPO_ROOT, "assets", "sfx")
        if not os.path.isdir(sfx_dir):
            return  # dir gone entirely is fine
        bad = []
        for f in os.listdir(sfx_dir):
            if f.endswith("_events.json") or f.endswith("_assetmap.json"):
                bad.append(f)
        self.assertEqual(bad, [],
                         f"Video-named SFX files found (use pipeline input instead): {bad}")

    def test_no_video_name_derivation_in_workflow(self):
        """Workflow must not derive file paths from video names."""
        wf_path = os.path.join(REPO_ROOT, ".github", "workflows", "render-production.yml")
        if not os.path.isfile(wf_path):
            self.skipTest("workflow not present")
        with open(wf_path) as f:
            content = f.read()
        violations = []
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, content):
                violations.append(pattern)
        self.assertEqual(violations, [],
                         f"Video-name derivation patterns in workflow: {violations}")

    def test_no_retired_video_directories(self):
        """No src/ subdirectories named after retired test videos."""
        src_dir = os.path.join(REPO_ROOT, "src")
        if not os.path.isdir(src_dir):
            self.skipTest("src/ not present")
        bad = []
        for entry in os.listdir(src_dir):
            full = os.path.join(src_dir, entry)
            if os.path.isdir(full) and entry.lower() in RETIRED_VIDEOS:
                bad.append(entry)
        self.assertEqual(bad, [],
                         f"Retired video directories found: {bad}")

    def test_no_retired_video_in_workflow(self):
        """Workflow must not reference retired video names."""
        wf_path = os.path.join(REPO_ROOT, ".github", "workflows", "render-production.yml")
        if not os.path.isfile(wf_path):
            self.skipTest("workflow not present")
        with open(wf_path) as f:
            content = f.read().lower()
        bad = [v for v in RETIRED_VIDEOS if v in content]
        self.assertEqual(bad, [],
                         f"Retired video names in workflow: {bad}")

    def test_sfx_mix_uses_input_not_convention(self):
        """sfx-mix job must take events as input, not derive from name."""
        wf_path = os.path.join(REPO_ROOT, ".github", "workflows", "render-production.yml")
        if not os.path.isfile(wf_path):
            self.skipTest("workflow not present")
        with open(wf_path) as f:
            content = f.read()
        # The input must exist
        self.assertIn("sfx_events_file", content,
                      "sfx-mix must accept sfx_events_file as pipeline input")


if __name__ == "__main__":
    unittest.main()
