#!/usr/bin/env python3
"""Regression tests for the R-2 universal composition contract (2026-10-10).

The contract (.github/scripts/composition_contract.py) declares every
composition registered in src/RemotionRoot.tsx with its role, brain/timeline/
token/audio/QA policies, and any allowed exemption. validate_dispatch.py and
plan.py enforce it at the production dispatch gates.

Run: python3 -m unittest tests.test_composition_contract -v
"""
import os
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(REPO_ROOT, ".github", "scripts")
sys.path.insert(0, SCRIPTS)

from composition_contract import (
    COMPOSITIONS,
    REQUIRED_FIELDS,
    VALID_ROLES,
    get_contract,
    registered_ids,
    remotion_root_ids,
    validate_for_dispatch,
    check_registry_consistency,
    check_no_duplicate_ids,
    find_duplicate_ids,
)

SCRIPTS_DIR = SCRIPTS
import contextlib as _contextlib
import io as _io
import json as _json
import shutil as _shutil
import tempfile as _tempfile


class TestBeatContractGate(unittest.TestCase):
    """The dispatch beat gate (validate_dispatch.check_beat_contract) proves
    checked-in beats honor the canonical EDITORIAL_BEAT_SCHEMA at dispatch."""

    def _beat_gate(self):
        sys.path.insert(0, SCRIPTS)
        from validate_dispatch import check_beat_contract
        return check_beat_contract

    def test_production_beats_satisfy_schema(self):
        check_beat_contract = self._beat_gate()
        errs = check_beat_contract("ProductionBeats", REPO_ROOT)
        self.assertEqual(errs, [], f"real beats should satisfy schema: {errs}")

    def test_production_beat_files_clean(self):
        # The production beat path must be fully schema-clean.
        check_beat_contract = self._beat_gate()
        for cid in ("ProductionBeats", "B6A", "B6B", "ChainTest"):
            errs = check_beat_contract(cid, REPO_ROOT)
            self.assertEqual(errs, [], f"{cid}: {errs}")

    def test_known_beat_violations_documented(self):
        # KNOWN DEBT (not invented, not hidden): one checked-in beat file is
        # stale relative to the canonical schema. P3Rehearsal is stopped by
        # Hamza's order. Regenerating it is R-5 work (beat compiler is not in
        # the pipeline). This test pins the exact known violation set so any
        # change — fix or new violation — fails loudly instead of drifting
        # silently. (ChainTest's t3 was repaired 2026-10-10 from the
        # arbitration record and is now clean.)
        check_beat_contract = self._beat_gate()
        p3 = check_beat_contract("P3Rehearsal", REPO_ROOT)
        # 2026-10-10: schema includes 'allocation'/'emphasize' and the 6
        # music_intensity values are authored (Hamza's consolidation order).
        # P3Rehearsal is fully schema-clean; the pin now guards against drift.
        self.assertEqual(len(p3), 0, f"P3Rehearsal violations changed: {p3}")

    def test_fixed_timeline_composition_skips(self):
        check_beat_contract = self._beat_gate()
        self.assertEqual(check_beat_contract("HousingBroke", REPO_ROOT), [])

    def test_tampered_beat_fails_closed(self):
        check_beat_contract = self._beat_gate()
        tmp = _tempfile.mkdtemp()
        try:
            repo = os.path.join(tmp, "demo-video")
            os.makedirs(os.path.join(repo, "src", "compiled"))
            _shutil.copy(os.path.join(REPO_ROOT, "..", "EDITORIAL_BEAT_SCHEMA.json"),
                         os.path.join(tmp, "EDITORIAL_BEAT_SCHEMA.json"))
            bad = {"beats": [{"beat_id": "bad1", "semantic_role": "trend"}]}
            with open(os.path.join(repo, "src", "compiled",
                                   "beat_timeline.json"), "w") as f:
                _json.dump(bad, f)
            errs = check_beat_contract("ProductionBeats", repo)
            self.assertTrue(errs, "tampered beat was accepted")
            self.assertTrue(any("missing required field" in e for e in errs))
        finally:
            _shutil.rmtree(tmp, ignore_errors=True)

    def test_missing_beat_file_fails(self):
        check_beat_contract = self._beat_gate()
        tmp = _tempfile.mkdtemp()
        try:
            repo = os.path.join(tmp, "demo-video")
            os.makedirs(os.path.join(repo, "src"))
            _shutil.copy(os.path.join(REPO_ROOT, "..", "EDITORIAL_BEAT_SCHEMA.json"),
                         os.path.join(tmp, "EDITORIAL_BEAT_SCHEMA.json"))
            errs = check_beat_contract("ProductionBeats", repo)
            self.assertTrue(errs)
            self.assertIn("Beat file missing", errs[0])
        finally:
            _shutil.rmtree(tmp, ignore_errors=True)

    def test_provenance_recorded_for_production_beats(self):
        # The gate result must carry the provenance record for a valid
        # beat-driven composition, identifying which artifact was validated.
        check_beat_contract = self._beat_gate()
        res = check_beat_contract("ProductionBeats", REPO_ROOT)
        prov = res.provenance
        self.assertIsNotNone(prov, "provenance missing from gate result")
        self.assertEqual(prov["file"], "src/compiled/beat_timeline.json")
        self.assertEqual(prov["provenance"], "checked-in")
        self.assertIn("beat_compiler.py", prov["generator"])

    def test_known_artifacts_are_checked_in(self):
        # Provenance fact (2026-10-10): beat_compiler.py is disconnected with
        # zero production callers and every checked-in beat file predates it,
        # so all three distinct beat artifacts are hand-authored "checked-in".
        check_beat_contract = self._beat_gate()
        for cid, rel in (("ProductionBeats", "src/compiled/beat_timeline.json"),
                         ("P3Rehearsal", "src/compiled_p3/beat_timeline.json"),
                         ("ChainTest", "src/chaintest/beat_timeline.json")):
            prov = check_beat_contract(cid, REPO_ROOT).provenance
            self.assertIsNotNone(prov, cid)
            self.assertEqual(prov["file"], rel, cid)
            self.assertEqual(prov["provenance"], "checked-in", cid)

    def test_provenance_line_printed_and_p3_pin_unchanged(self):
        # The provenance line must reach the dispatch log, and recording it
        # is metadata-only: the pinned P3Rehearsal 8-violation set must be
        # byte-identical to before the provenance addition.
        check_beat_contract = self._beat_gate()
        buf = _io.StringIO()
        with _contextlib.redirect_stdout(buf):
            p3 = check_beat_contract("P3Rehearsal", REPO_ROOT)
        self.assertIn("Provenance: src/compiled_p3/beat_timeline.json "
                      "[checked-in]", buf.getvalue())
        self.assertEqual(len(p3), 0, f"P3Rehearsal violations changed: {p3}")
        self.assertEqual(p3.provenance["provenance"], "checked-in")


class TestBeatSchemaFailClosed(unittest.TestCase):
    """The beat gate must fail closed — never silently skip — when the
    schema is missing or malformed. A silent skip on a GitHub runner (where
    the canonical schema file is absent from the checkout) would let
    unvalidated beats reach dispatch."""

    def _beat_gate(self):
        sys.path.insert(0, SCRIPTS)
        from validate_dispatch import check_beat_contract
        return check_beat_contract

    def _fake_repo(self, tmp, schema_mode="vendored", beat_mode="valid"):
        """Build a minimal fake repo_root.

        schema_mode: "vendored" (repo copy present), "legacy" (canonical
        parent-dir copy present), "missing" (neither), "malformed"
        (vendored copy is not JSON).
        beat_mode: "valid" (one schema-clean beat), "malformed" (not JSON).
        """
        repo = os.path.join(tmp, "demo-video")
        os.makedirs(os.path.join(repo, "src", "compiled"))
        if schema_mode in ("vendored", "malformed"):
            sdir = os.path.join(repo, ".github", "schemas")
            os.makedirs(sdir)
            spath = os.path.join(sdir, "EDITORIAL_BEAT_SCHEMA.json")
            if schema_mode == "vendored":
                _shutil.copy(
                    os.path.join(REPO_ROOT, ".github", "schemas",
                                 "EDITORIAL_BEAT_SCHEMA.json"), spath)
            else:
                with open(spath, "w") as f:
                    f.write("{not valid json,,,")
        elif schema_mode == "legacy":
            _shutil.copy(
                os.path.join(REPO_ROOT, ".github", "schemas",
                             "EDITORIAL_BEAT_SCHEMA.json"),
                os.path.join(tmp, "EDITORIAL_BEAT_SCHEMA.json"))
        bpath = os.path.join(repo, "src", "compiled", "beat_timeline.json")
        if beat_mode == "valid":
            beat = {
                "beat_id": "ok1", "start_time": 0, "end_time": 1,
                "start_word": "a", "end_word": "b",
                "semantic_role": "trend", "claim": "c",
                "visual_verb": "reveal", "focal_object": "chart",
                "duration_class": "normal", "intensity": 1,
                "music_intensity": 1, "sfx_policy": "none",
                "events": [], "visual_mode": "comparison_bars",
                "visual_reason": "r",
            }
            with open(bpath, "w") as f:
                _json.dump({"beats": [beat]}, f)
        elif beat_mode == "malformed":
            with open(bpath, "w") as f:
                f.write("{broken,,,")
        return repo

    def test_missing_schema_fails_closed(self):
        check_beat_contract = self._beat_gate()
        tmp = _tempfile.mkdtemp()
        try:
            repo = self._fake_repo(tmp, schema_mode="missing")
            errs = check_beat_contract("ProductionBeats", repo)
            self.assertTrue(errs, "missing schema silently passed")
            self.assertTrue(any("fail-closed" in e and "schema" in e.lower()
                                for e in errs),
                            f"no fail-closed schema error: {errs}")
        finally:
            _shutil.rmtree(tmp, ignore_errors=True)

    def test_malformed_schema_fails_closed(self):
        check_beat_contract = self._beat_gate()
        tmp = _tempfile.mkdtemp()
        try:
            repo = self._fake_repo(tmp, schema_mode="malformed")
            errs = check_beat_contract("ProductionBeats", repo)
            self.assertTrue(errs, "malformed schema silently passed")
            self.assertTrue(any("fail-closed" in e for e in errs),
                            f"no fail-closed error: {errs}")
        finally:
            _shutil.rmtree(tmp, ignore_errors=True)

    def test_malformed_beat_file_fails_closed(self):
        check_beat_contract = self._beat_gate()
        tmp = _tempfile.mkdtemp()
        try:
            repo = self._fake_repo(tmp, schema_mode="vendored",
                                    beat_mode="malformed")
            errs = check_beat_contract("ProductionBeats", repo)
            self.assertTrue(errs, "malformed beat file silently passed")
            self.assertTrue(any("unreadable" in e for e in errs),
                            f"no unreadable-beat error: {errs}")
        finally:
            _shutil.rmtree(tmp, ignore_errors=True)

    def test_vendored_schema_validates_clean_beat(self):
        check_beat_contract = self._beat_gate()
        tmp = _tempfile.mkdtemp()
        try:
            repo = self._fake_repo(tmp, schema_mode="vendored")
            errs = check_beat_contract("ProductionBeats", repo)
            self.assertEqual(errs, [], f"clean beat rejected: {errs}")
        finally:
            _shutil.rmtree(tmp, ignore_errors=True)

    def test_legacy_canonical_path_still_works(self):
        check_beat_contract = self._beat_gate()
        tmp = _tempfile.mkdtemp()
        try:
            repo = self._fake_repo(tmp, schema_mode="legacy")
            errs = check_beat_contract("ProductionBeats", repo)
            self.assertEqual(errs, [], f"legacy schema path broke: {errs}")
        finally:
            _shutil.rmtree(tmp, ignore_errors=True)


class TestBeatSchemaSync(unittest.TestCase):
    """The repo-vendored schema replica must be byte-identical to the
    canonical source. The replica exists only so GitHub runners (whose
    checkouts lack crackit/) can enforce the beat gate; the canonical file
    remains the single source of truth."""

    def test_vendored_matches_canonical(self):
        import hashlib
        canonical = os.path.join(os.path.dirname(REPO_ROOT),
                                 "EDITORIAL_BEAT_SCHEMA.json")
        if not os.path.exists(canonical):
            self.skipTest("canonical schema absent (e.g. runner checkout)")
        vendored = os.path.join(REPO_ROOT, ".github", "schemas",
                                "EDITORIAL_BEAT_SCHEMA.json")
        self.assertTrue(os.path.exists(vendored), "vendored replica missing")
        ch = hashlib.sha256(open(canonical, "rb").read()).hexdigest()
        vh = hashlib.sha256(open(vendored, "rb").read()).hexdigest()
        self.assertEqual(vh, ch,
                         "vendored schema drifted from canonical source")


class TestRegistryCompleteness(unittest.TestCase):
    """The contract must cover exactly the 24 compositions RemotionRoot registers."""

    def test_24_registered(self):
        self.assertEqual(len(COMPOSITIONS), 24)

    def test_matches_remotion_root(self):
        root_ids = remotion_root_ids(REPO_ROOT)
        self.assertEqual(root_ids, registered_ids(),
                         f"contract/root mismatch: "
                         f"missing={sorted(root_ids - registered_ids())} "
                         f"stale={sorted(registered_ids() - root_ids)}")

    def test_consistency_check_clean(self):
        self.assertEqual(check_registry_consistency(REPO_ROOT), [])

    def test_no_duplicate_ids_in_registry(self):
        self.assertEqual(check_no_duplicate_ids(), [])

    def test_duplicate_id_detected(self):
        dup_src = (
            'COMPOSITIONS = {\n'
            '    "HousingBroke": dict(role="production"),\n'
            '    "HousingBroke": dict(role="test"),\n'
            '}\n'
        )
        dups = find_duplicate_ids(dup_src)
        self.assertEqual(dups, {"HousingBroke": 2})

    def test_each_id_declared_once(self):
        # The real registry file: every id exactly once.
        path = os.path.join(SCRIPTS, "composition_contract.py")
        with open(path) as f:
            content = f.read()
        self.assertEqual(find_duplicate_ids(content), {})


class TestContractShape(unittest.TestCase):
    def test_all_fields_present(self):
        for cid, c in COMPOSITIONS.items():
            self.assertTrue(REQUIRED_FIELDS <= set(c.keys()), f"{cid} missing fields")

    def test_valid_roles(self):
        for cid, c in COMPOSITIONS.items():
            self.assertIn(c["role"], VALID_ROLES, cid)

    def test_production_has_no_exemption(self):
        for cid, c in COMPOSITIONS.items():
            if c["role"] == "production":
                self.assertIsNone(c["exemption"], f"{cid} must not be exempt")
                self.assertEqual(c["brain"], "required", cid)

    def test_exemption_requires_reason(self):
        for cid, c in COMPOSITIONS.items():
            if c["brain"] == "exempt":
                self.assertTrue(c.get("exemption"), f"{cid} exempt without reason")


class TestDispatchGates(unittest.TestCase):
    def test_unknown_composition_rejected(self):
        errs = validate_for_dispatch("NoSuchVideo", True)
        self.assertTrue(errs)
        self.assertIn("not registered", errs[0])

    def test_empty_id_rejected(self):
        errs = validate_for_dispatch("", True)
        self.assertTrue(errs)

    def test_production_cannot_claim_exemption(self):
        saved = COMPOSITIONS["HousingBroke"]["exemption"]
        COMPOSITIONS["HousingBroke"]["exemption"] = "bogus"
        try:
            errs = validate_for_dispatch("HousingBroke", True)
            self.assertTrue(errs)
            self.assertIn("cannot", errs[0])
        finally:
            COMPOSITIONS["HousingBroke"]["exemption"] = saved

    def test_embedded_audio_with_audio_false_rejected(self):
        # Verified defect E1: HousingBroke embeds <Audio>; a with_audio=false
        # master would be labeled video_only while containing an audio stream.
        errs = validate_for_dispatch("HousingBroke", False)
        self.assertTrue(errs)
        self.assertIn("video_only", errs[0])
        errs = validate_for_dispatch("MoneyDying", False)
        self.assertTrue(errs)

    def test_all_registered_pass_with_audio_true(self):
        for cid in COMPOSITIONS:
            errs = validate_for_dispatch(cid, True)
            self.assertEqual(errs, [], f"{cid}: {errs}")

    def test_exempt_test_compositions_pass(self):
        for cid in ("TrialVideo", "CalibrationV0", "ModeRegression", "ChainTest"):
            self.assertEqual(validate_for_dispatch(cid, True), [])

    def test_invalid_policy_values_rejected(self):
        for field, bad in (("brain", "maybe"), ("timeline", "sometimes"),
                           ("tokens", "css"), ("audio", "sometimes"),
                           ("qa", "vibes"), ("role", "blockbuster")):
            saved = COMPOSITIONS["B6A"][field]
            COMPOSITIONS["B6A"][field] = bad
            try:
                errs = validate_for_dispatch("B6A", True)
                self.assertTrue(errs, f"{field}={bad!r} was accepted")
                self.assertIn(f"invalid {field}", errs[0])
            finally:
                COMPOSITIONS["B6A"][field] = saved

    def test_valid_compositions_still_pass_after_hardening(self):
        for cid in COMPOSITIONS:
            self.assertEqual(validate_for_dispatch(cid, True), [], f"{cid}")


class TestPlanGate(unittest.TestCase):
    """plan.py's validate_composition must reject unregistered ids (fail closed)."""

    def test_plan_rejects_unknown(self):
        import plan
        with self.assertRaises(SystemExit):
            plan.validate_composition("NoSuchVideo")

    def test_plan_accepts_registered(self):
        import plan
        self.assertEqual(plan.validate_composition("HousingBroke"), "HousingBroke")
        self.assertEqual(plan.validate_composition("CalibrationV2"), "CalibrationV2")

    def test_plan_still_rejects_bad_format(self):
        import plan
        with self.assertRaises(SystemExit):
            plan.validate_composition("bad-id!")


if __name__ == "__main__":
    unittest.main()
