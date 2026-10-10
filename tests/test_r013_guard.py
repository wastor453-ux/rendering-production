"""Regression tests for R-013 (stale-rerun guard logic).

The guard logic lives in .github/scripts/rerun_guard.sh. The workflow binds
github.run_attempt -> the script's argument. These tests prove the fail-closed
logic; the binding itself can only be proven by a hosted rerun, which is
deferred (no production workflow may be rerun).
"""
import os
import subprocess
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO_ROOT, ".github", "scripts", "rerun_guard.sh")
WORKFLOW = os.path.join(REPO_ROOT, ".github", "workflows", "render-production.yml")


class TestRerunGuard(unittest.TestCase):
    def run_guard(self, *args):
        return subprocess.run(["bash", SCRIPT] + list(args),
                              capture_output=True, text=True, timeout=10)

    def test_attempt_1_passes(self):
        r = self.run_guard("1")
        self.assertEqual(r.returncode, 0)
        self.assertIn("R-013 guard passed", r.stdout)

    def test_attempt_2_fails_closed(self):
        r = self.run_guard("2")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("FATAL", r.stderr)
        self.assertIn("rerun", r.stderr.lower())

    def test_attempt_5_fails_closed(self):
        r = self.run_guard("5")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("attempt 5", r.stderr)

    def test_invalid_attempt_fails_closed(self):
        for bad in ("", "abc"):
            r = self.run_guard(bad)
            self.assertNotEqual(r.returncode, 0, f"bad input {bad!r} must fail closed")

    def test_workflow_binds_run_attempt(self):
        """The plan job must pass github.run_attempt to the guard script."""
        with open(WORKFLOW) as f:
            content = f.read()
        self.assertIn("rerun_guard.sh \"${{ github.run_attempt }}\"", content,
                      "Workflow must bind github.run_attempt to rerun_guard.sh")

    def test_guard_is_first_plan_step(self):
        """The guard must run before any installation, rendering, or publication."""
        with open(WORKFLOW) as f:
            content = f.read()
        plan_start = content.index("  plan:")
        guard_pos = content.index("R-013 stale-rerun guard", plan_start)
        # No apt-get / render / publish steps before the guard within plan
        before = content[plan_start:guard_pos]
        self.assertNotIn("apt-get", before)
        self.assertNotIn("remotion", before.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
