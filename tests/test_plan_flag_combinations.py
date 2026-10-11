#!/usr/bin/env python3
"""
Q2 (2026-10-11): Unsafe workflow flag combination tests.

plan.validate_flag_combinations() must reject incompatible inputs
fail-closed before any rendering or publication.

Combinations (with_sfx_mix, sfx_chain_test, install_verify, reassemble_bypass):
  - (True, False, False, True)  -> REJECT (sfx-mix on bypassed reassembly)
  - (True, False, False, False) -> ALLOW (normal sfx-mix path)
  - (False, False, False, True) -> ALLOW (legitimate recovery)
  - (False, False, False, False)-> ALLOW (normal render)
  - (False, True, False, False) -> ALLOW (chain test mode)
  - (False, False, True, False) -> ALLOW (install verify mode)
  - (True, True, False, False)  -> ALLOW (test mode wins; sfx-mix blocked by job condition)
  - invalid flag strings        -> REJECT (strict true/false)
"""
import os
import sys
import unittest

REPO_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(REPO_ROOT, ".github", "scripts"))

import plan


class TestValidateFlagCombinations(unittest.TestCase):
    def test_reassemble_bypass_with_sfx_mix_rejected(self):
        # The unsafe combination: mixing SFX into a reassembled master
        # with bypassed fingerprint verification.
        with self.assertRaises(SystemExit) as ctx:
            plan.validate_flag_combinations(
                with_sfx_mix=True, sfx_chain_test=False,
                install_verify=False, reassemble_bypass=True)
        self.assertNotEqual(ctx.exception.code, 0)

    def test_normal_sfx_mix_allowed(self):
        plan.validate_flag_combinations(
            with_sfx_mix=True, sfx_chain_test=False,
            install_verify=False, reassemble_bypass=False)

    def test_legitimate_recovery_allowed(self):
        # Reassembly without sfx-mix is the intended recovery path.
        plan.validate_flag_combinations(
            with_sfx_mix=False, sfx_chain_test=False,
            install_verify=False, reassemble_bypass=True)

    def test_normal_render_allowed(self):
        plan.validate_flag_combinations(
            with_sfx_mix=False, sfx_chain_test=False,
            install_verify=False, reassemble_bypass=False)

    def test_chain_test_mode_allowed(self):
        plan.validate_flag_combinations(
            with_sfx_mix=False, sfx_chain_test=True,
            install_verify=False, reassemble_bypass=False)

    def test_install_verify_mode_allowed(self):
        plan.validate_flag_combinations(
            with_sfx_mix=False, sfx_chain_test=False,
            install_verify=True, reassemble_bypass=False)

    def test_sfx_mix_with_chain_test_allowed(self):
        # Test mode wins deterministically (sfx-mix job condition blocks it).
        plan.validate_flag_combinations(
            with_sfx_mix=True, sfx_chain_test=True,
            install_verify=False, reassemble_bypass=False)

    def test_reassemble_bypass_with_chain_test_allowed(self):
        # Chain test mode doesn't touch reassembly.
        plan.validate_flag_combinations(
            with_sfx_mix=False, sfx_chain_test=True,
            install_verify=False, reassemble_bypass=True)


class TestValidateBoolFlag(unittest.TestCase):
    def test_accepts_true_false(self):
        self.assertTrue(plan.validate_bool_flag("TEST", "true"))
        self.assertTrue(plan.validate_bool_flag("TEST", "True"))
        self.assertTrue(plan.validate_bool_flag("TEST", " TRUE "))
        self.assertFalse(plan.validate_bool_flag("TEST", "false"))
        self.assertFalse(plan.validate_bool_flag("TEST", "False"))

    def test_rejects_invalid(self):
        for bad in ("yes", "1", "0", "", "Truee", "null"):
            with self.assertRaises(SystemExit, msg=f"value={bad!r}"):
                plan.validate_bool_flag("TEST", bad)


if __name__ == "__main__":
    unittest.main()
