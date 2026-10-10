"""Regression tests for validate_verify_report.py (stale-report fail-closed).

The Q-004 run uploaded a stale verify-report (2026-10-06, 180s master, FAIL
grade). These tests lock the binding contract: a report without a matching
master identity must never be uploaded.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO_ROOT, ".github", "scripts", "validate_verify_report.py")


def make_master(path, frames=300, duration=10.0):
    """Minimal valid MP4 via ffmpeg (testsrc, exact frame count)."""
    r = subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
         f"testsrc=duration={duration}:size=64x64:rate=30",
         "-frames:v", str(frames), "-pix_fmt", "yuv420p", path],
        capture_output=True, text=True)
    assert r.returncode == 0, f"ffmpeg failed: {r.stderr}"


class TestVerifyReportBinding(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.master = os.path.join(self.tmp, "master.mp4")
        make_master(self.master)
        self.report = os.path.join(self.tmp, "verify-report.json")

    def run_script(self, *args):
        return subprocess.run([sys.executable, SCRIPT] + list(args),
                              capture_output=True, text=True)

    def test_stamp_then_validate_passes(self):
        with open(self.report, "w") as f:
            json.dump({"grade": "PASS"}, f)
        r = self.run_script("stamp", "--report", self.report,
                            "--run-id", "123", "--master", self.master)
        self.assertEqual(r.returncode, 0, r.stderr)
        r = self.run_script("validate", "--report", self.report,
                            "--run-id", "123", "--master", self.master,
                            "--expected-frames", "300")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("bound OK", r.stdout)

    def test_unstamped_report_rejected(self):
        """A report with no master_identity stamp must fail closed."""
        with open(self.report, "w") as f:
            json.dump({"grade": "PASS"}, f)  # no stamp
        r = self.run_script("validate", "--report", self.report,
                            "--run-id", "123", "--master", self.master)
        self.assertEqual(r.returncode, 1)
        self.assertIn("no master_identity", r.stderr)

    def test_wrong_run_id_rejected(self):
        """Report stamped for a different run => stale, fail closed."""
        with open(self.report, "w") as f:
            json.dump({"grade": "PASS"}, f)
        self.run_script("stamp", "--report", self.report,
                        "--run-id", "999", "--master", self.master)
        r = self.run_script("validate", "--report", self.report,
                            "--run-id", "123", "--master", self.master)
        self.assertEqual(r.returncode, 1)
        self.assertIn("stale report", r.stderr)

    def test_tampered_master_rejected(self):
        """Report stamped, then master replaced => sha mismatch, fail closed."""
        with open(self.report, "w") as f:
            json.dump({"grade": "PASS"}, f)
        self.run_script("stamp", "--report", self.report,
                        "--run-id", "123", "--master", self.master)
        other = os.path.join(self.tmp, "other.mp4")
        # Different visual content => different bytes (same frame count).
        r = subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
             "testsrc=duration=10.0:size=64x64:rate=30",
             "-frames:v", "300", "-pix_fmt", "yuv420p",
             "-vf", "negate", other],
            capture_output=True, text=True)
        assert r.returncode == 0
        r = self.run_script("validate", "--report", self.report,
                            "--run-id", "123", "--master", other)
        self.assertEqual(r.returncode, 1)
        self.assertIn("sha256 does not match", r.stderr)

    def test_frame_count_mismatch_rejected(self):
        r = self.run_script("validate", "--report", self.report,
                            "--run-id", "123", "--master", self.master,
                            "--expected-frames", "999")
        # No report file at all here -> exit 2 (skip, not failure).
        # Write a stamped one first, then check expected-frames mismatch.
        with open(self.report, "w") as f:
            json.dump({"grade": "PASS"}, f)
        self.run_script("stamp", "--report", self.report,
                        "--run-id", "123", "--master", self.master)
        r = self.run_script("validate", "--report", self.report,
                            "--run-id", "123", "--master", self.master,
                            "--expected-frames", "999")
        self.assertEqual(r.returncode, 1)
        self.assertIn("!= expected", r.stderr)

    def test_missing_report_skips_not_fails(self):
        """Absent report => exit 2 (caller skips upload, not a failure)."""
        r = self.run_script("validate", "--report",
                            os.path.join(self.tmp, "nope.json"),
                            "--run-id", "123", "--master", self.master)
        self.assertEqual(r.returncode, 2)
        self.assertIn("skipping upload", r.stdout)

    def test_corrupt_report_rejected(self):
        with open(self.report, "w") as f:
            f.write("{not json")
        r = self.run_script("validate", "--report", self.report,
                            "--run-id", "123", "--master", self.master)
        self.assertEqual(r.returncode, 1)
        self.assertIn("not valid JSON", r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
