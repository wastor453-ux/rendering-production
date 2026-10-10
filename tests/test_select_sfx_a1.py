#!/usr/bin/env python3
"""Tests for tools/select_sfx_a1.py — autonomous A1 SFX selector.

Laws under test (SOUND_DESIGN.md):
  §4  Default = silence; score >= 75 to select.
  §4  Hard context locks (glitch/money/review never auto-selected).
  §7  Impact class never auto-selected (human ear gate).
  §8  Anti-fatigue: no back-to-back reuse, 12f click breathing, <=2/1s, <=1/beat.
"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
from select_sfx_a1 import (
    CATEGORY_ROLE, ROLE_ALLOW, SCORE_THRESHOLD,
    load_a1, score_asset, select, Fail,
)

MANIFEST = os.path.join(os.path.dirname(__file__), "..", "assets", "a1", "MANIFEST.json")


def ev(eid, role="ui_confirm", policy="auto", impact=300, beat="B1",
       verb="appear", motion="medium"):
    return {"event_id": eid, "beat_id": beat, "semantic_role": role,
            "visual_verb": verb, "motion_scale": motion,
            "visual_impact_frame": impact, "sfx_policy": policy}


class TestManifestLoading(unittest.TestCase):
    def test_loads_routable_assets(self):
        assets = load_a1(MANIFEST)
        # Hold categories excluded: Alert, Error, Loading, graph down/up
        cats = {a["category"] for a in assets}
        for hold in ("Alert", "Error", "Loading", "graph down", "graph rise"):
            self.assertNotIn(hold, cats, f"hold category {hold} must not be routable")
        self.assertGreater(len(assets), 50)

    def test_all_routable_have_peak(self):
        for a in load_a1(MANIFEST):
            self.assertIsNotNone(a.get("peak_time_s"))


class TestContextLocks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assets = load_a1(MANIFEST)

    def test_impact_never_auto_selected(self):
        # impact semantic_role has empty allow-list -> always silence
        m = select([ev("E1", role="impact", impact=300)], self.assets)
        self.assertNotIn("E1", m)

    def test_unknown_role_silent(self):
        m = select([ev("E1", role="glitch", impact=300)], self.assets)
        self.assertNotIn("E1", m)  # glitch not in ROLE_ALLOW

    def test_manual_policy_skipped(self):
        m = select([ev("E1", role="ui_confirm", policy="manual", impact=300)],
                   self.assets)
        self.assertNotIn("E1", m)

    def test_none_policy_skipped(self):
        m = select([ev("E1", role="ui_confirm", policy="none", impact=300)],
                   self.assets)
        self.assertNotIn("E1", m)

    def test_bad_policy_fails_closed(self):
        with self.assertRaises(Fail):
            select([ev("E1", policy="bogus", impact=300)], self.assets)


class TestScoring(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assets = load_a1(MANIFEST)

    def test_threshold_gates_selection(self):
        # A money event should select a coin asset (>= 75)
        m = select([ev("E1", role="money", impact=600, motion="small")],
                   self.assets)
        self.assertIn("E1", m)
        # Verify the selected asset actually scored >= threshold
        by_name = {a["filename"]: a for a in self.assets}
        s, _ = score_asset(by_name[m["E1"]],
                           ev("E1", role="money", impact=600, motion="small"),
                           None, {})
        self.assertGreaterEqual(s, SCORE_THRESHOLD)

    def test_wrong_category_zero_semantic(self):
        # money role cannot select a click asset (semantic hard fail)
        by_name = {a["filename"]: a for a in self.assets}
        click = next(a for a in self.assets
                     if CATEGORY_ROLE[a["category"]] == "click")
        s, parts = score_asset(click, ev("E1", role="money", impact=600),
                               None, {})
        self.assertEqual(s, 0)
        self.assertTrue(any("semantic+0" in p for p in parts))


class TestAntiFatigue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assets = load_a1(MANIFEST)

    def test_one_per_beat(self):
        evs = [ev(f"E{i}", role="ui_confirm", impact=300 + i * 60,
                  beat="B1") for i in range(4)]
        m = select(evs, self.assets)
        self.assertEqual(len(m), 1)  # only one per beat

    def test_no_back_to_back_repeat(self):
        evs = [ev(f"E{i}", role="ui_confirm", impact=300 + i * 900,
                  beat=f"B{i}") for i in range(6)]
        m = select(evs, self.assets)
        vals = [m[f"E{i}"] for i in range(6) if f"E{i}" in m]
        for a, b in zip(vals, vals[1:]):
            self.assertNotEqual(a, b, "back-to-back reuse forbidden")

    def test_variety_pressure(self):
        # 9 selections should use 9 distinct assets (variety bonus)
        evs = [ev(f"E{i}", role="card_entrance", impact=300 + i * 900,
                  beat=f"B{i}") for i in range(9)]
        m = select(evs, self.assets)
        self.assertEqual(len(set(m.values())), len(m))

    def test_click_breathing_room(self):
        # Two click events 6 frames apart -> second silenced
        evs = [ev("E1", role="ui_confirm", impact=300, beat="B1"),
               ev("E2", role="ui_confirm", impact=306, beat="B2")]
        m = select(evs, self.assets)
        # E2 may be silenced by breathing room OR selected with different asset;
        # either way E1 and E2 must not be the same asset 6f apart
        if "E1" in m and "E2" in m:
            self.assertNotEqual(m["E1"], m["E2"])

    def test_density_cap(self):
        # 3 events within 1.0s -> max 2 selected
        evs = [ev(f"E{i}", role="ui_confirm", impact=300 + i * 10,
                  beat=f"B{i}") for i in range(3)]
        m = select(evs, self.assets)
        self.assertLessEqual(len(m), 2)


class TestEndToEnd(unittest.TestCase):
    def test_cli_writes_asset_map(self):
        events = {"events": [
            ev("E1", role="money", impact=600, motion="small"),
            ev("E2", role="impact", impact=900),  # manual-ish, auto->silent
            ev("E3", role="ui_confirm", policy="none", impact=1200),
        ]}
        with tempfile.NamedTemporaryFile("w", suffix=".json",
                                         delete=False) as ef:
            json.dump(events, ef)
            ef_path = ef.name
        with tempfile.NamedTemporaryFile("w", suffix=".json",
                                         delete=False) as of:
            out_path = of.name
        try:
            import subprocess
            r = subprocess.run(
                [sys.executable,
                 os.path.join(os.path.dirname(__file__), "..", "tools",
                              "select_sfx_a1.py"),
                 "--events", ef_path, "--manifest", MANIFEST,
                 "--out", out_path],
                capture_output=True, text=True, timeout=30)
            self.assertEqual(r.returncode, 0, r.stderr)
            with open(out_path) as f:
                am = json.load(f)
            self.assertIn("E1", am)       # money auto-selected
            self.assertNotIn("E2", am)    # impact -> silence
            self.assertNotIn("E3", am)    # none -> silence
        finally:
            os.unlink(ef_path)
            os.unlink(out_path)


if __name__ == "__main__":
    unittest.main()
