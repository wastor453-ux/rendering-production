"""Regression tests for R-008 (Ubuntu snapshot package reproducibility).

Verifies:
1. No direct `apt-get install` in the workflow (all go through install_snapshot.sh).
2. install_snapshot.sh fails closed when UBUNTU_SNAPSHOT is unset.
3. install_snapshot.sh fails closed on empty package list.
4. The script logs snapshot timestamp and validates sources.
"""
import os
import re
import subprocess
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOW = os.path.join(REPO_ROOT, ".github", "workflows", "render-production.yml")
SCRIPT = os.path.join(REPO_ROOT, ".github", "scripts", "install_snapshot.sh")


class TestR008NoBypass(unittest.TestCase):
    def test_no_direct_apt_get_install_in_workflow(self):
        """Every apt-get install must go through install_snapshot.sh."""
        with open(WORKFLOW) as f:
            content = f.read()
        # Find all apt-get install occurrences outside the script reference
        for i, line in enumerate(content.split("\n"), 1):
            if "apt-get install" in line and "install_snapshot.sh" not in line:
                self.fail(f"Line {i}: direct apt-get install bypasses R-008: {line.strip()[:80]}")

    def test_no_rolling_apt_update_in_workflow(self):
        """No bare `apt-get update` that could hit rolling sources."""
        with open(WORKFLOW) as f:
            content = f.read()
        for i, line in enumerate(content.split("\n"), 1):
            stripped = line.strip()
            # Allow apt-get update only inside install_snapshot.sh logic comments
            if stripped.startswith("sudo apt-get update") or stripped == "apt-get update -qq":
                self.fail(f"Line {i}: bare apt-get update bypasses R-008: {stripped[:80]}")

    def test_all_jobs_use_snapshot_script(self):
        """Each job that needs packages references install_snapshot.sh."""
        with open(WORKFLOW) as f:
            content = f.read()
        # Count usages — should cover render, assemble, sfx-mix, sfx-chain-test
        uses = content.count("install_snapshot.sh")
        self.assertGreaterEqual(uses, 4,
                                f"Expected >=4 install_snapshot.sh usages, found {uses}")

    def test_snapshot_script_exists_and_executable(self):
        self.assertTrue(os.path.isfile(SCRIPT), f"Missing {SCRIPT}")
        self.assertTrue(os.access(SCRIPT, os.X_OK), f"Not executable: {SCRIPT}")


class TestR008FailClosed(unittest.TestCase):
    def run_script(self, *args, env_extra=None):
        env = dict(os.environ)
        env.pop("UBUNTU_SNAPSHOT", None)  # ensure clean unless set below
        if env_extra:
            env.update(env_extra)
        return subprocess.run(["bash", SCRIPT] + list(args),
                              capture_output=True, text=True, env=env, timeout=30)

    def test_fails_without_snapshot_var(self):
        """Empty/unset UBUNTU_SNAPSHOT must fail closed, not fall back to rolling."""
        r = self.run_script("ffmpeg")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("UBUNTU_SNAPSHOT", r.stderr)
        self.assertIn("refusing", r.stderr.lower())

    def test_fails_with_empty_package_list(self):
        r = self.run_script(env_extra={"UBUNTU_SNAPSHOT": "20260820T000000Z"})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("no packages", r.stderr.lower())

    def test_script_validates_snapshot_url_format(self):
        """Script must reference snapshot.ubuntu.com (not archive.ubuntu.com)."""
        with open(SCRIPT) as f:
            content = f.read()
        self.assertIn("snapshot.ubuntu.com", content)
        # Must not contain a fallback to the rolling archive
        self.assertNotIn("archive.ubuntu.com", content)

    def test_script_checks_for_rolling_sources(self):
        """Script must detect and reject non-snapshot sources."""
        with open(SCRIPT) as f:
            content = f.read()
        self.assertIn("rolling", content.lower())
        self.assertIn("refusing install", content.lower() or content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
