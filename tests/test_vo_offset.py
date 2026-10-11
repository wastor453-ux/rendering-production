#!/usr/bin/env python3
"""
Q3 (2026-10-11): VO offset alignment tests.

The audio contract: vo_offset_seconds is the position in vo_file where the
rendered range's audio begins. The muxer seeks to VO_OFFSET (not to
start_frame/30). The duration guard checks VO_DUR - VO_OFFSET against
VIDEO_DUR.

Cases:
  - validate_vo_offset: accepts 0, positive floats; rejects negative, inf,
    nan, non-numeric
  - guard: H3 case (offset=0, vo=180.565s, video=181.6s) passes
  - guard: full render (offset=0, vo=772s, video=771.7s) passes
  - guard: partial render with full VO (offset=125.1, vo=772s,
    video=181.6s) passes
  - guard: offset >= VO duration fails
  - guard: available audio >30s short fails
  - guard: available audio slightly short warns (not fatal)
  - mux: ffmpeg command uses VO_OFFSET_SECONDS, not START_S
"""
import math
import os
import re
import sys
import unittest

REPO_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(REPO_ROOT, ".github", "scripts"))

import plan


def guard_check(video_dur, vo_dur, offset):
    """Mirror the workflow audio guard logic. Returns (exit_code, message)."""
    if not math.isfinite(offset) or offset < 0:
        return 1, "invalid offset"
    if offset >= vo_dur:
        return 1, "offset >= vo duration"
    available = vo_dur - offset
    gap = video_dur - available
    if gap > 30:
        return 1, f"FATAL: gap {gap:.1f}s"
    elif gap > 0:
        return 0, f"WARNING: gap {gap:.1f}s"
    return 0, "OK"


class TestValidateVoOffset(unittest.TestCase):
    def test_accepts_zero(self):
        self.assertEqual(plan.validate_vo_offset("0"), 0.0)

    def test_accepts_positive(self):
        self.assertEqual(plan.validate_vo_offset("125.1"), 125.1)
        self.assertEqual(plan.validate_vo_offset("0.5"), 0.5)

    def test_rejects_negative(self):
        with self.assertRaises(SystemExit):
            plan.validate_vo_offset("-1")

    def test_rejects_non_finite(self):
        for bad in ("inf", "-inf", "nan", "Infinity"):
            with self.assertRaises(SystemExit, msg=f"value={bad}"):
                plan.validate_vo_offset(bad)

    def test_rejects_non_numeric(self):
        for bad in ("", "abc", "12s", "None"):
            with self.assertRaises(SystemExit, msg=f"value={bad!r}"):
                plan.validate_vo_offset(bad)


class TestOffsetAwareGuard(unittest.TestCase):
    def test_h3_segment_vo_passes(self):
        # H3 demo: frames 3753-9200 (181.6s), hb_p3.wav (180.565s), offset=0.
        # Previously the mux would seek 125.1s into this file (wrong).
        code, msg = guard_check(181.6, 180.565, 0)
        self.assertEqual(code, 0, msg)
        self.assertIn("WARNING", msg)  # 1.0s gap -> warning, not fatal

    def test_full_render_full_vo_passes(self):
        # Q-004: 771.7s video, 772s VO, offset=0.
        code, msg = guard_check(771.7, 772.0, 0)
        self.assertEqual(code, 0, msg)

    def test_partial_render_full_vo_with_offset_passes(self):
        # H3 range with full-composition VO: offset=125.1 (=3753/30).
        code, msg = guard_check(181.6, 772.0, 125.1)
        self.assertEqual(code, 0, msg)

    def test_offset_beyond_vo_duration_fails(self):
        code, msg = guard_check(181.6, 180.565, 180.565)
        self.assertNotEqual(code, 0)

    def test_offset_leaves_too_little_audio_fails(self):
        # 100s offset into 180s VO leaves 80s for 181.6s video -> >30s gap.
        code, msg = guard_check(181.6, 180.0, 100.0)
        self.assertNotEqual(code, 0)
        self.assertIn("FATAL", msg)

    def test_short_vo_still_caught(self):
        # The original Q-004 failure mode: 83s VO vs 771s video.
        code, msg = guard_check(771.7, 83.0, 0)
        self.assertNotEqual(code, 0)


class TestMuxUsesOffset(unittest.TestCase):
    def test_workflow_mux_seeks_to_vo_offset(self):
        with open(os.path.join(
                REPO_ROOT, ".github/workflows/render-production.yml")) as f:
            wf = f.read()
        # The mux step must use VO_OFFSET_SECONDS, not START_S.
        mux_idx = wf.find("name: Mux canonical audio")
        self.assertNotEqual(mux_idx, -1)
        # Find the next step to bound the section
        next_step = wf.find("\n      - name:", mux_idx + 10)
        mux_section = wf[mux_idx:next_step]
        self.assertIn("-ss $VO_OFFSET_SECONDS", mux_section,
                      "mux must seek to VO_OFFSET_SECONDS")
        self.assertNotIn("-ss $START_S", mux_section,
                         "mux must NOT seek to START_S (the Q3 bug)")
        # VO_OFFSET_SECONDS must be in the step's env
        self.assertIn("VO_OFFSET_SECONDS:", mux_section)

    def test_guard_uses_offset(self):
        with open(os.path.join(
                REPO_ROOT, ".github/workflows/render-production.yml")) as f:
            wf = f.read()
        guard_idx = wf.find("name: P4.4 audio duration guard")
        self.assertNotEqual(guard_idx, -1)
        next_step = wf.find("\n      - name:", guard_idx + 10)
        guard_section = wf[guard_idx:next_step]
        self.assertIn("VO_OFFSET_SECONDS", guard_section,
                      "guard must be offset-aware")

    def test_workflow_input_exists(self):
        with open(os.path.join(
                REPO_ROOT, ".github/workflows/render-production.yml")) as f:
            wf = f.read()
        self.assertIn("vo_offset_seconds:", wf)


if __name__ == "__main__":
    unittest.main()
