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
        """Each job that needs packages references install_snapshot.sh.

        Job map (5 install sites):
          render-chunk  — Install system deps (BROWSER_PACKAGES) + browser repair
          assemble      — Install ffmpeg (minimal)
          sfx-mix       — Install ffmpeg (minimal)
          sfx-chain-test— Build synthetic VO + bed inputs (ffmpeg)
        """
        with open(WORKFLOW) as f:
            content = f.read()
        lines = content.split("\n")
        # Actual invocations only (exclude comments mentioning the script)
        invocations = [
            i for i, line in enumerate(lines, 1)
            if "bash .github/scripts/install_snapshot.sh" in line
            and not line.strip().startswith("#")
        ]
        # 5 production sites + 3 install-verify sites
        self.assertEqual(len(invocations), 8,
                         f"Expected exactly 8 install sites, found {len(invocations)}")

        # Map each invocation to its workflow job
        job_headers = [(i, line.strip().rstrip(":"))
                       for i, line in enumerate(lines, 1)
                       if line.startswith("  ") and line.strip().endswith(":")
                       and not line.strip().startswith(("if", "with", "run", "env", "steps", "outputs"))]
        expected = {
            "render-chunk": 2,   # main install + browser repair
            "assemble": 1,       # ffmpeg
            "sfx-mix": 1,        # ffmpeg
            "sfx-chain-test": 1, # ffmpeg
            "install-verify": 3, # render-chunk path + assemble path + sfx-mix path
        }
        found = {job: 0 for job in expected}
        for lineno in invocations:
            job = "unknown"
            for hline, hname in job_headers:
                if hline < lineno and hname in expected:
                    job = hname
            if job in found:
                found[job] += 1
        self.assertEqual(found, expected,
                         f"Per-job install-site map mismatch: {found}")

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


class TestInstallVerifyJob(unittest.TestCase):
    """R-008: the install-verify job must exist and be the ONLY job that runs
    in install_verify mode. All production jobs must be gated off."""

    def _jobs(self):
        import yaml
        with open(WORKFLOW) as f:
            return yaml.safe_load(f)["jobs"]

    def test_install_verify_job_exists(self):
        jobs = self._jobs()
        self.assertIn("install-verify", jobs)
        iv = jobs["install-verify"]
        self.assertIn("inputs.install_verify == true", iv.get("if", ""))
        step_names = [s.get("name", "") for s in iv["steps"]]
        self.assertIn("R-008 render-chunk install path (BROWSER_PACKAGES)", step_names)
        self.assertIn("R-008 assemble install path (ffmpeg)", step_names)
        self.assertIn("R-008 sfx-mix install path (ffmpeg)", step_names)

    def test_all_other_jobs_gated_off(self):
        jobs = self._jobs()
        for name, job in jobs.items():
            if name == "install-verify":
                continue
            cond = str(job.get("if", ""))
            self.assertIn("install_verify != true", cond,
                          f"Job {name} is NOT gated off install_verify mode: {cond}")

    def test_install_verify_steps_use_snapshot_script(self):
        """Every install-verify step must route through install_snapshot.sh."""
        import yaml
        with open(WORKFLOW) as f:
            jobs = yaml.safe_load(f)["jobs"]
        for step in jobs["install-verify"]["steps"]:
            run = step.get("run", "")
            if "apt" in run.lower() or "install" in run.lower():
                self.assertIn("install_snapshot.sh", run,
                              f"Step '{step.get('name')}' bypasses install_snapshot.sh")

    def test_with_sfx_mix_still_default_false(self):
        """Guardrail: with_sfx_mix must remain default false (no full mix)."""
        import yaml
        with open(WORKFLOW) as f:
            # YAML 1.1 parses `on:` as boolean True
            inputs = yaml.safe_load(f)[True]["workflow_dispatch"]["inputs"]
        self.assertEqual(inputs["with_sfx_mix"]["default"], False)
        self.assertEqual(inputs["install_verify"]["default"], False)
        self.assertEqual(inputs["sfx_chain_test"]["default"], False)


class TestBrowserRepairPath(unittest.TestCase):
    """R-008: the render-chunk browser-repair path must use the snapshot
    installer and cannot fall back to rolling apt sources."""

    def _repair_block(self):
        with open(WORKFLOW) as f:
            content = f.read()
        start = content.index('elif [ "$OUTCOME" = "repairable" ]')
        # Repair block ends at the next elif/fi at the same level
        end = content.index('echo "Rechecking after repair..."', start)
        return content[start:end].split("\n")

    def test_repair_uses_snapshot_installer(self):
        block = self._repair_block()
        invocations = [l for l in block
                       if "bash .github/scripts/install_snapshot.sh" in l
                       and not l.strip().startswith("#")]
        self.assertEqual(len(invocations), 1,
                         "Repair path must invoke install_snapshot.sh exactly once")

    def test_repair_has_no_rolling_fallback(self):
        block = "\n".join(self._repair_block())
        self.assertNotIn("apt-get install", block,
                         "Repair path must not call apt-get install directly")
        self.assertNotIn("archive.ubuntu.com", block,
                         "Repair path must not reference the rolling archive")

    def test_repair_uses_unified_package_set(self):
        """Repair must install BROWSER_PACKAGES (R-021), not a separate list."""
        block = "\n".join(self._repair_block())
        self.assertIn("from preflight import BROWSER_PACKAGES", block)

    def test_repair_is_gated_on_repairable(self):
        """Repair only runs when the browser check says 'repairable'."""
        with open(WORKFLOW) as f:
            content = f.read()
        self.assertIn('elif [ "$OUTCOME" = "repairable" ]', content)
