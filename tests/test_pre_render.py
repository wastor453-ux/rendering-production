"""
Regression tests for pre-render enforcement gate.
Every bypass attempt must fail closed.
"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import pre_render_check as prc

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUTH_DIR = os.path.join(REPO, ".production-state", "authorizations")


def _write_auth(name, data):
    os.makedirs(AUTH_DIR, exist_ok=True)
    path = os.path.join(AUTH_DIR, name + ".json")
    with open(path, "w") as f:
        json.dump(data, f)
    return path


def _clear_auth(name):
    path = os.path.join(AUTH_DIR, name + ".json")
    if os.path.exists(path):
        os.remove(path)


class TestBypassAttempts(unittest.TestCase):
    def setUp(self):
        for n in ("sfx_mix", "creative", "production_dispatch"):
            _clear_auth(n)

    def tearDown(self):
        for n in ("sfx_mix", "creative", "production_dispatch"):
            _clear_auth(n)

    def test_sfx_mix_without_auth_rejected(self):
        ok, msg = prc.check_sfx_mix_flag({"with_sfx_mix": True})
        self.assertFalse(ok, "sfx mix without auth must be rejected")

    def test_sfx_mix_with_auth_allowed(self):
        _write_auth("sfx_mix", {"authorized": True, "by": "Hamza"})
        ok, msg = prc.check_sfx_mix_flag({"with_sfx_mix": True})
        self.assertTrue(ok)

    def test_sfx_mix_false_always_ok(self):
        ok, msg = prc.check_sfx_mix_flag({"with_sfx_mix": False})
        self.assertTrue(ok)

    def test_creative_rejected_blocks(self):
        _write_auth("creative", {"approved": False, "rejected": True})
        ok, msg = prc.check_creative_approval()
        self.assertFalse(ok, "rejected creative must block")

    def test_creative_missing_blocks(self):
        ok, msg = prc.check_creative_approval()
        self.assertFalse(ok, "missing creative approval must block")

    def test_creative_approved_passes(self):
        _write_auth("creative", {"approved": True, "note": "Direction A"})
        ok, msg = prc.check_creative_approval()
        self.assertTrue(ok)

    def test_unauthorized_dispatch_blocked(self):
        ok, msg = prc.check_authorization()
        self.assertFalse(ok, "unauthorized dispatch must be blocked")

    def test_authorized_dispatch_passes(self):
        _write_auth("production_dispatch", {"authorized": True})
        ok, msg = prc.check_authorization()
        self.assertTrue(ok)

    def test_typography_run_rejected(self):
        beats = {"beats": [
            {"beat_id": f"B{i}", "visual_mode": "hero_typography"}
            for i in range(3)
        ]}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(beats, f)
            path = f.name
        try:
            ok, msg = prc.check_variety(path)
            self.assertFalse(ok, "3 typography beats in a row must be rejected")
        finally:
            os.unlink(path)

    def test_variety_ok(self):
        beats = {"beats": [
            {"beat_id": "B1", "visual_mode": "hero_typography"},
            {"beat_id": "B2", "visual_mode": "hero_typography"},
            {"beat_id": "B3", "visual_mode": "line_chart"},
            {"beat_id": "B4", "visual_mode": "hero_typography"},
        ]}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(beats, f)
            path = f.name
        try:
            ok, msg = prc.check_variety(path)
            self.assertTrue(ok)
        finally:
            os.unlink(path)

    def test_recovery_tools_present(self):
        ok, msg = prc.check_recovery_tools()
        self.assertTrue(ok, f"recovery tools should exist: {msg}")


if __name__ == "__main__":
    unittest.main()
