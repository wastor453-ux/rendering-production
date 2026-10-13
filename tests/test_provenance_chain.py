"""
test_provenance_chain.py — Provenance validation tests.

Calls the REAL tools/validate_timeline.py (not synthetic dict comparisons).
F-12 fix: was testing hand-chosen strings, not the production validator.
"""
import unittest
import json
import tempfile
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
from validate_timeline import validate


def _make_timeline(provenance=None, events=None):
    """Build a minimal timeline dict for testing."""
    tl = {
        "source": "test",
        "provenance": provenance if provenance is not None else {
            "alignment_sha256": "a" * 64,
            "patterns_sha256": "b" * 64,
            "generator": "test",
        },
        "narration_duration_s": 10.0,
        "fps": 30,
        "events": events if events is not None else [
            {
                "event_id": "evt_001",
                "start_frame": 0,
                "end_frame": 120,
                "visual_type": "tip_card",
                "entrance": "fade_in",
                "progression": "hold",
                "exit": "fade",
                "on_screen_text": "test",
                "semantic_claim": "test_claim",
            }
        ],
    }
    return tl


def _validate_dict(timeline_dict):
    """Write dict to temp file and run the real validator."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(timeline_dict, f)
        path = f.name
    try:
        errors, warnings = validate(path)
        return errors, warnings
    finally:
        os.unlink(path)


class TestProvenanceChain(unittest.TestCase):
    def test_missing_provenance_fails(self):
        """Timeline without provenance must fail the real validator."""
        tl = _make_timeline(provenance={})
        errors, _ = _validate_dict(tl)
        self.assertTrue(any("provenance" in e.lower() for e in errors),
                        f"Expected provenance error, got: {errors}")

    def test_missing_alignment_hash_fails(self):
        """Provenance without alignment_sha256 must fail."""
        tl = _make_timeline(provenance={"patterns_sha256": "bbb222"})
        errors, _ = _validate_dict(tl)
        self.assertTrue(any("alignment_sha256" in e for e in errors),
                        f"Expected alignment_sha256 error, got: {errors}")

    def test_valid_provenance_passes(self):
        """Complete provenance must pass Gate 0."""
        tl = _make_timeline()
        errors, _ = _validate_dict(tl)
        prov_errors = [e for e in errors if "provenance" in e.lower()]
        self.assertEqual(prov_errors, [],
                         f"Provenance should pass, got: {prov_errors}")

    def test_empty_timeline_fails(self):
        """Empty timeline must fail the real validator."""
        tl = _make_timeline(events=[])
        errors, _ = _validate_dict(tl)
        self.assertTrue(len(errors) > 0,
                        "Empty timeline should produce errors")

    def test_invalid_entrance_enum_fails(self):
        """Unknown entrance value must fail (F-10)."""
        tl = _make_timeline()
        tl["events"][0]["entrance"] = "bogus_entrance_xyz"
        errors, _ = _validate_dict(tl)
        self.assertTrue(any("bogus_entrance_xyz" in e for e in errors),
                        f"Expected enum error, got: {errors}")

    def test_overlapping_events_fail(self):
        """Overlapping events must fail (F-06)."""
        tl = _make_timeline(events=[
            {
                "event_id": "evt_001", "start_frame": 0, "end_frame": 120,
                "visual_type": "tip_card", "entrance": "fade_in",
                "progression": "hold", "exit": "fade",
                "on_screen_text": "a", "semantic_claim": "c1",
            },
            {
                "event_id": "evt_002", "start_frame": 60, "end_frame": 180,
                "visual_type": "tip_card", "entrance": "fade_in",
                "progression": "hold", "exit": "fade",
                "on_screen_text": "b", "semantic_claim": "c2",
            },
        ])
        errors, _ = _validate_dict(tl)
        self.assertTrue(any("overlap" in e.lower() for e in errors),
                        f"Expected overlap error, got: {errors}")


if __name__ == "__main__":
    unittest.main()
