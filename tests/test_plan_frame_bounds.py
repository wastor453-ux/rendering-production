#!/usr/bin/env python3
"""
Q1 (2026-10-11): Frame upper-bound validation tests.

plan.validate_frame_range() must reject any frame range outside the
composition's authoritative [0, total_frames) before chunk generation.

Cases (using HousingBroke, total_frames=23151):
  - last valid frame (23150) passes
  - exactly one beyond (23151) fails
  - very large end frame (999999) fails
  - start beyond end of composition fails
  - end < start fails
  - unregistered composition fails closed
  - composition with missing/invalid total_frames fails closed
  - H3 demo range (3753-9200) passes
"""
import os
import sys
import unittest

REPO_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(REPO_ROOT, ".github", "scripts"))

import plan
from composition_contract import COMPOSITIONS


class TestValidateFrameRange(unittest.TestCase):
    def test_last_valid_frame_passes(self):
        # 23150 is the last valid frame of HousingBroke (0-indexed).
        total = plan.validate_frame_range("HousingBroke", 0, 23150)
        self.assertEqual(total, 23151)

    def test_one_beyond_end_fails(self):
        # 23151 is exactly one frame past the end.
        with self.assertRaises(SystemExit) as ctx:
            plan.validate_frame_range("HousingBroke", 0, 23151)
        self.assertNotEqual(ctx.exception.code, 0)

    def test_very_large_end_frame_fails(self):
        with self.assertRaises(SystemExit) as ctx:
            plan.validate_frame_range("HousingBroke", 0, 999999)
        self.assertNotEqual(ctx.exception.code, 0)

    def test_start_beyond_composition_fails(self):
        with self.assertRaises(SystemExit) as ctx:
            plan.validate_frame_range("HousingBroke", 23151, 23151)
        self.assertNotEqual(ctx.exception.code, 0)

    def test_end_before_start_fails(self):
        with self.assertRaises(SystemExit) as ctx:
            plan.validate_frame_range("HousingBroke", 9200, 3753)
        self.assertNotEqual(ctx.exception.code, 0)

    def test_unregistered_composition_fails_closed(self):
        with self.assertRaises(SystemExit) as ctx:
            plan.validate_frame_range("NoSuchVideo", 0, 100)
        self.assertNotEqual(ctx.exception.code, 0)

    def test_missing_total_frames_fails_closed(self):
        # Temporarily remove total_frames from a contract entry.
        saved = COMPOSITIONS["HousingBroke"].pop("total_frames")
        try:
            with self.assertRaises(SystemExit) as ctx:
                plan.validate_frame_range("HousingBroke", 0, 100)
            self.assertNotEqual(ctx.exception.code, 0)
        finally:
            COMPOSITIONS["HousingBroke"]["total_frames"] = saved

    def test_invalid_total_frames_fails_closed(self):
        # Zero, negative, and non-int totals must all fail closed.
        for bad in (0, -5, "23151", 23151.0, None):
            saved = COMPOSITIONS["HousingBroke"]["total_frames"]
            COMPOSITIONS["HousingBroke"]["total_frames"] = bad
            try:
                with self.assertRaises(SystemExit, msg=f"total={bad!r}"):
                    plan.validate_frame_range("HousingBroke", 0, 100)
            finally:
                COMPOSITIONS["HousingBroke"]["total_frames"] = saved

    def test_h3_demo_range_passes(self):
        # The proposed H3 demo: frames 3753-9200 of HousingBroke.
        total = plan.validate_frame_range("HousingBroke", 3753, 9200)
        self.assertEqual(total, 23151)

    def test_full_composition_range_passes(self):
        total = plan.validate_frame_range("HousingBroke", 0, 23150)
        self.assertEqual(total, 23151)

    def test_other_compositions_use_their_own_bounds(self):
        # MoneyDying has 2322 frames; 23151 would be out of range there.
        plan.validate_frame_range("MoneyDying", 0, 2321)
        with self.assertRaises(SystemExit):
            plan.validate_frame_range("MoneyDying", 0, 23151)


if __name__ == "__main__":
    unittest.main()
