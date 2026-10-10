#!/usr/bin/env python3
"""
test_sfx_mix.py — A1 SFX mix chain regression tests.

Covers tools/mix_sfx.py (LOCAL ONLY):
- Trigger JSON schema validation (valid passes, malformed fails closed).
- Every staged-manifest event's asset resolves in the vendored A1 dir.
- Ducking/priority/breathing-room math on a synthetic timeline.
- --dry-run prints the filter graph and writes no audio.
- A1-only enforcement: non-A1 assets fail closed.
- Workflow sfx-mix job is inert unless with_sfx_mix=true.

Conventions: unittest, no network, synthetic fixtures only (no production audio).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MIX = os.path.join(REPO_ROOT, "tools", "mix_sfx.py")
A1_MANIFEST = os.path.join(REPO_ROOT, "assets", "a1", "MANIFEST.json")
A1_DIR = os.path.join(REPO_ROOT, "assets", "a1")
STAGED = os.path.join(os.path.expanduser("~"), "workspace", "crackit",
                      "weekly", "proof", "P4_4", "P4_4_SFX_STAGED_MANIFEST.json")
WORKFLOW = os.path.join(REPO_ROOT, ".github", "workflows", "render-production.yml")

sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import mix_sfx


def have_ffmpeg():
    return shutil.which("ffmpeg") is not None


def make_tone(path, seconds=2.0, freq=440):
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-y", "-f", "lavfi", "-i",
         f"sine=frequency={freq}:duration={seconds}:sample_rate=44100",
         "-c:a", "pcm_s16le", path],
        check=True, capture_output=True)


class TestTriggerSchema(unittest.TestCase):
    def good_doc(self):
        return {"schema": "astor-legacy-sfx-triggers-v1", "triggers": [
            {"event_id": "H1_01", "asset": "ui-swipe-45.wav", "trigger_s": 0.3,
             "trigger_frame": 9, "visual_impact_frame": 10, "peak_time_s": 0.045,
             "approved_role": "soft whoosh"}]}

    def test_valid_triggers_pass(self):
        trigs = mix_sfx.validate_triggers(self.good_doc())
        self.assertEqual(len(trigs), 1)

    def test_wrong_schema_fails(self):
        doc = self.good_doc()
        doc["schema"] = "something-else"
        with self.assertRaises(mix_sfx.Fail):
            mix_sfx.validate_triggers(doc)

    def test_missing_key_fails(self):
        doc = self.good_doc()
        del doc["triggers"][0]["trigger_s"]
        with self.assertRaises(mix_sfx.Fail):
            mix_sfx.validate_triggers(doc)

    def test_empty_triggers_fails(self):
        with self.assertRaises(mix_sfx.Fail):
            mix_sfx.validate_triggers(
                {"schema": "astor-legacy-sfx-triggers-v1", "triggers": []})

    def test_negative_trigger_s_fails(self):
        doc = self.good_doc()
        doc["triggers"][0]["trigger_s"] = -1.0
        with self.assertRaises(mix_sfx.Fail):
            mix_sfx.validate_triggers(doc)


class TestA1OnlyEnforcement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.load(open(A1_MANIFEST))
        cls.idx = mix_sfx.index_a1(A1_DIR)

    def test_all_180_assets_resolve(self):
        self.assertEqual(len(self.idx), 180)

    def test_all_33_staged_events_resolve(self):
        staged = json.load(open(STAGED))
        by_name = {a["filename"] for a in self.manifest["assets"]}
        bad = []
        for e in staged["events"]:
            fn = e["filename"]
            if fn not in by_name:
                bad.append((e["seq"], "not in manifest"))
            elif fn not in self.idx:
                bad.append((e["seq"], "not on disk"))
        self.assertEqual(bad, [], f"Unresolved staged assets: {bad}")

    def test_non_a1_asset_fails_closed(self):
        trigs = [{"event_id": "X_01", "asset": "pro-drop-01.wav",
                  "trigger_s": 1.0, "trigger_frame": 30,
                  "visual_impact_frame": 30, "peak_time_s": 0.01}]
        with self.assertRaises(mix_sfx.Fail):
            mix_sfx.resolve_assets(trigs, self.manifest, self.idx)

    def test_missing_file_fails_closed(self):
        trigs = [{"event_id": "X_01", "asset": "ui-swipe-45.wav",
                  "trigger_s": 1.0, "trigger_frame": 30,
                  "visual_impact_frame": 30, "peak_time_s": 0.01}]
        with self.assertRaises(mix_sfx.Fail):
            mix_sfx.resolve_assets(trigs, self.manifest, {})  # empty index


class TestDuckingMath(unittest.TestCase):
    """Pure gain-computation tests on a synthetic timeline (no ffmpeg)."""

    def mk(self, eid, role, trigger_s, peak=0.02, dur=0.5, asset="x.wav"):
        return {"event_id": eid, "asset": asset, "trigger_s": trigger_s,
                "trigger_frame": int(trigger_s * 30),
                "visual_impact_frame": int(trigger_s * 30),
                "peak_time_s": peak, "approved_role": role}

    def role_of(self, t):
        return mix_sfx.ROLE_CLASS[t["approved_role"]]

    def test_vo_overlap_ducks_4db(self):
        t = self.mk("A", "soft whoosh", 1.0)
        gains = mix_sfx.compute_gains(
            [t], self.role_of, [(0.5, 5.0)], {"A": 0.5})
        self.assertAlmostEqual(
            gains["A"], mix_sfx.ROLE_GAIN_DB["Whoosh"] + mix_sfx.VO_DUCK_DB)

    def test_no_vo_overlap_no_duck(self):
        t = self.mk("A", "soft whoosh", 10.0)
        gains = mix_sfx.compute_gains(
            [t], self.role_of, [(0.5, 5.0)], {"A": 0.5})
        self.assertAlmostEqual(gains["A"], mix_sfx.ROLE_GAIN_DB["Whoosh"])

    def test_vo_never_ducked(self):
        # VO gain is not computed here at all: the mix keeps VO at 0dB by
        # construction (first amix input, no volume filter). This pins the law.
        self.assertNotIn("VO", mix_sfx.PRIORITY)

    def test_priority_overlap_ducks_lower(self):
        hi = self.mk("H", "impact hit", 2.0)
        lo = self.mk("L", "UI click", 2.1)  # overlaps hi, lower priority
        durs = {"H": 0.5, "L": 0.5}
        gains = mix_sfx.compute_gains([hi, lo], self.role_of, [], durs)
        self.assertAlmostEqual(
            gains["L"],
            mix_sfx.ROLE_GAIN_DB["Click"] + mix_sfx.PRIORITY_DUCK_DB)
        self.assertAlmostEqual(gains["H"], mix_sfx.ROLE_GAIN_DB["Impact"])

    def test_click_breathing_room_fails(self):
        a = self.mk("A", "UI click", 1.0)
        b = self.mk("B", "UI click", 1.2)  # 6 frames apart < 12
        with self.assertRaises(mix_sfx.Fail):
            mix_sfx.check_antifatigue([a, b], self.role_of)

    def test_click_breathing_room_passes(self):
        a = self.mk("A", "UI click", 1.0)
        b = self.mk("B", "UI click", 1.5)  # 15 frames >= 12
        mix_sfx.check_antifatigue([a, b], self.role_of)  # no raise

    def test_density_cap_fails(self):
        ts = [self.mk(f"E{i}", "soft whoosh", 1.0 + i * 0.2) for i in range(3)]
        with self.assertRaises(mix_sfx.Fail):
            mix_sfx.check_antifatigue(ts, self.role_of)

    def test_density_cap_passes_at_two(self):
        ts = [self.mk(f"E{i}", "soft whoosh", 1.0 + i * 0.2) for i in range(2)]
        mix_sfx.check_antifatigue(ts, self.role_of)  # no raise


@unittest.skipUnless(have_ffmpeg(), "ffmpeg not available")
class TestDryRun(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="sfxmix_test_")
        cls.vo = os.path.join(cls.tmp, "vo.wav")
        cls.bed = os.path.join(cls.tmp, "bed.mp3")
        make_tone(cls.vo, seconds=3.0, freq=440)
        # bed as mp3 via wav intermediate
        bed_wav = os.path.join(cls.tmp, "bed.wav")
        make_tone(bed_wav, seconds=3.0, freq=220)
        subprocess.run(["ffmpeg", "-hide_banner", "-y", "-i", bed_wav,
                        "-c:a", "libmp3lame", cls.bed],
                       check=True, capture_output=True)
        cls.trig = os.path.join(cls.tmp, "triggers.json")
        json.dump({"schema": "astor-legacy-sfx-triggers-v1", "triggers": [
            {"event_id": "T_01", "asset": "ui-swipe-45.wav", "trigger_s": 0.5,
             "trigger_frame": 15, "visual_impact_frame": 16,
             "peak_time_s": 0.045, "approved_role": "soft whoosh"},
            {"event_id": "T_02", "asset": "ui-click-30.wav", "trigger_s": 2.0,
             "trigger_frame": 60, "visual_impact_frame": 61,
             "peak_time_s": 0.02, "approved_role": "UI click"},
        ]}, open(cls.trig, "w"))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_dry_run_prints_graph_writes_nothing(self):
        out = os.path.join(self.tmp, "should_not_exist.wav")
        p = subprocess.run(
            [sys.executable, MIX, "--triggers", self.trig,
             "--a1-manifest", A1_MANIFEST, "--a1-dir", A1_DIR,
             "--vo", self.vo, "--bed", self.bed,
             "--out", out, "--dry-run"],
            capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr[-2000:])
        self.assertIn("FILTER GRAPH", p.stdout)
        self.assertIn("amix", p.stdout)
        self.assertIn("loudnorm", p.stdout)
        self.assertIn("DRY RUN", p.stdout)
        self.assertFalse(os.path.exists(out),
                         "dry-run must not write audio")

    def test_test_seconds_renders_bounded_audio(self):
        out = os.path.join(self.tmp, "bounded.wav")
        p = subprocess.run(
            [sys.executable, MIX, "--triggers", self.trig,
             "--a1-manifest", A1_MANIFEST, "--a1-dir", A1_DIR,
             "--vo", self.vo, "--bed", self.bed,
             "--out", out, "--test-seconds", "2"],
            capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr[-2000:])
        self.assertTrue(os.path.isfile(out))
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "stream=sample_rate,duration", "-of", "csv=p=0", out],
            capture_output=True, text=True)
        sr, dur = probe.stdout.strip().split(",")[:2]
        self.assertEqual(sr, "48000")
        self.assertLessEqual(float(dur), 2.5)

    def test_missing_asset_fails_closed(self):
        bad = os.path.join(self.tmp, "bad.json")
        json.dump({"schema": "astor-legacy-sfx-triggers-v1", "triggers": [
            {"event_id": "B_01", "asset": "nope-not-a1.wav", "trigger_s": 0.5,
             "trigger_frame": 15, "visual_impact_frame": 16,
             "peak_time_s": 0.045, "approved_role": "soft whoosh"}]},
            open(bad, "w"))
        p = subprocess.run(
            [sys.executable, MIX, "--triggers", bad,
             "--a1-manifest", A1_MANIFEST, "--a1-dir", A1_DIR,
             "--vo", self.vo, "--bed", self.bed,
             "--out", os.path.join(self.tmp, "x.wav"), "--dry-run"],
            capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("MIX FAIL", p.stderr)


class TestWorkflowInert(unittest.TestCase):
    """The sfx-mix job must be fully gated off unless with_sfx_mix=true."""

    @classmethod
    def setUpClass(cls):
        import yaml
        with open(WORKFLOW) as f:
            cls.wf = yaml.safe_load(f)

    def test_with_sfx_mix_input_defaults_false(self):
        # yaml parses the `on:` key as boolean True
        sfx = self.wf[True]["workflow_dispatch"]["inputs"]["with_sfx_mix"]
        self.assertEqual(sfx["type"], "boolean")
        self.assertEqual(sfx["default"], False)

    def test_sfx_mix_job_requires_flag(self):
        job = self.wf["jobs"]["sfx-mix"]
        cond = job["if"]
        self.assertIn("inputs.with_sfx_mix", cond)
        self.assertIn("== true", cond)

    def test_sfx_mix_needs_assemble_success(self):
        job = self.wf["jobs"]["sfx-mix"]
        self.assertIn("assemble", job["needs"])
        self.assertIn("needs.assemble.result", job["if"])

    def test_existing_jobs_untouched_by_flag(self):
        # No existing job may reference with_sfx_mix or sfx-mix.
        for name in ("plan", "render-chunk", "assemble"):
            text = json.dumps(self.wf["jobs"][name])
            self.assertNotIn("with_sfx_mix", text, f"job {name} references flag")
            self.assertNotIn("sfx-mix", text, f"job {name} references sfx-mix")


if __name__ == "__main__":
    unittest.main(verbosity=2)
