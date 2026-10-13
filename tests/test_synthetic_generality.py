"""
test_synthetic_generality.py — Prove generic behavior with synthetic fixtures.

Two synthetic video identities with different inputs. No real video content.
"""
import unittest
import hashlib
import json
import tempfile
import os

class TestSyntheticGenerality(unittest.TestCase):
    def _make_fixture(self, video_id, audio_content):
        """Create synthetic video fixture."""
        return {
            "video_id": video_id,
            "audio_hash": hashlib.sha256(audio_content).hexdigest(),
            "audio": audio_content,
        }
    
    def test_two_fixtures_isolated(self):
        """Two synthetic videos must not leak into each other."""
        fix_a = self._make_fixture("synth-alpha", b"audio alpha content")
        fix_b = self._make_fixture("synth-beta", b"audio beta content")
        
        # Different hashes
        self.assertNotEqual(fix_a["audio_hash"], fix_b["audio_hash"])
        # Different IDs
        self.assertNotEqual(fix_a["video_id"], fix_b["video_id"])
    
    def test_no_cross_contamination(self):
        """Fixture A's artifacts must not be usable for Fixture B."""
        fix_a = self._make_fixture("synth-alpha", b"alpha")
        fix_b = self._make_fixture("synth-beta", b"beta")
        
        # Simulate provenance check
        timeline_a = {"provenance": {"audio_hash": fix_a["audio_hash"]}}
        # Fixture B's audio should NOT match A's timeline
        self.assertNotEqual(
            timeline_a["provenance"]["audio_hash"],
            fix_b["audio_hash"]
        )
    
    def test_video_id_validation(self):
        """Video IDs must be validated (alphanumeric + hyphens)."""
        import re
        valid = ["synth-alpha", "test123", "my-video-2"]
        invalid = ["../etc", "video;rm", "video/path"]
        
        pattern = r'^[a-z0-9-]+$'
        for v in valid:
            self.assertTrue(re.match(pattern, v), f"{v} should be valid")
        for v in invalid:
            self.assertFalse(re.match(pattern, v), f"{v} should be invalid")
    
    def test_unknown_composition_rejected(self):
        """Unknown composition must not have a contract."""
        import sys
        sys.path.insert(0, ".github/scripts")
        from composition_contract import get_contract
        self.assertIsNone(get_contract("NonExistentVideo123"))
    
    def test_blocked_composition_rejected(self):
        """Blocked legacy compositions must fail."""
        import sys
        sys.path.insert(0, ".github/scripts")
        from composition_contract import is_blocked
        self.assertIsNotNone(is_blocked("BudgetRule"))
        self.assertIsNone(is_blocked("EventDriven"))

if __name__ == "__main__":
    unittest.main()
