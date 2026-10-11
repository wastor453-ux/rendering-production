#!/usr/bin/env python3
"""
Q1 (2026-10-11): Frame upper-bound validation tests.

plan.validate_frame_range() must reject any frame range outside the
composition's authoritative [0, total_frames) before chunk generation.

Pipeline tests (no hardcoded video): bounds are derived from whichever
production composition the registry provides. Works for any current or
future video without test changes.
"""
import os
import sys
import unittest

REPO_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(REPO_ROOT, ".github", "scripts"))

import plan
from composition_contract import COMPOSITIONS


def _production_composition():
    """Return (id, total_frames) for any production composition."""
    for cid, c in COMPOSITIONS.items():
        if c.get("role") == "production" and isinstance(c.get("total_frames"), int):
            return cid, c["total_frames"]
    raise AssertionError("no production composition with total_frames in registry")


class TestValidateFrameRange(unittest.TestCase):
    def test_last_valid_frame_passes(self):
        cid, total = _production_composition()
        result = plan.validate_frame_range(cid, 0, total - 1)
        self.assertEqual(result, total)

    def test_one_beyond_end_fails(self):
        cid, total = _production_composition()
        with self.assertRaises(SystemExit) as ctx:
            plan.validate_frame_range(cid, 0, total)
        self.assertNotEqual(ctx.exception.code, 0)

    def test_very_large_end_frame_fails(self):
        cid, _ = _production_composition()
        with self.assertRaises(SystemExit) as ctx:
            plan.validate_frame_range(cid, 0, 999999)
        self.assertNotEqual(ctx.exception.code, 0)

    def test_start_beyond_composition_fails(self):
        cid, total = _production_composition()
        with self.assertRaises(SystemExit) as ctx:
            plan.validate_frame_range(cid, total, total)
        self.assertNotEqual(ctx.exception.code, 0)

    def test_end_before_start_fails(self):
        cid, total = _production_composition()
        mid = total // 2
        with self.assertRaises(SystemExit) as ctx:
            plan.validate_frame_range(cid, mid + 10, mid)
        self.assertNotEqual(ctx.exception.code, 0)

    def test_unregistered_composition_fails_closed(self):
        with self.assertRaises(SystemExit) as ctx:
            plan.validate_frame_range("NoSuchVideo", 0, 100)
        self.assertNotEqual(ctx.exception.code, 0)

    def test_missing_total_frames_fails_closed(self):
        cid, _ = _production_composition()
        saved = COMPOSITIONS[cid].pop("total_frames")
        try:
            with self.assertRaises(SystemExit) as ctx:
                plan.validate_frame_range(cid, 0, 100)
            self.assertNotEqual(ctx.exception.code, 0)
        finally:
            COMPOSITIONS[cid]["total_frames"] = saved

    def test_invalid_total_frames_fails_closed(self):
        cid, total = _production_composition()
        for bad in (0, -5, str(total), float(total), None):
            saved = COMPOSITIONS[cid]["total_frames"]
            COMPOSITIONS[cid]["total_frames"] = bad
            try:
                with self.assertRaises(SystemExit, msg=f"total={bad!r}"):
                    plan.validate_frame_range(cid, 0, 100)
            finally:
                COMPOSITIONS[cid]["total_frames"] = saved

    def test_mid_range_passes(self):
        cid, total = _production_composition()
        lo, hi = total // 4, total // 2
        result = plan.validate_frame_range(cid, lo, hi)
        self.assertEqual(result, total)

    def test_full_composition_range_passes(self):
        cid, total = _production_composition()
        result = plan.validate_frame_range(cid, 0, total - 1)
        self.assertEqual(result, total)

    def test_other_compositions_use_their_own_bounds(self):
        prods = [(c, v["total_frames"]) for c, v in COMPOSITIONS.items()
                 if v.get("role") == "production"
                 and isinstance(v.get("total_frames"), int)]
        self.assertTrue(len(prods) >= 1)
        cid, total = prods[0]
        plan.validate_frame_range(cid, 0, total - 1)
        with self.assertRaises(SystemExit):
            plan.validate_frame_range(cid, 0, total)


if __name__ == "__main__":
    unittest.main()
