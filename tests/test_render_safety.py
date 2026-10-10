#!/usr/bin/env python3
"""Regression tests for the 2026-10-10 render-safety fixes (Hamza's rule).

Covers:
  C-14: reassembly is API-dispatchable (repository_dispatch trigger)
  Failure classifier: chunk failure vs assembly death vs plan failure
  Chunk ledger: durable ground truth gating assembly

Run: python3 -m unittest tests.test_render_safety -v
"""
import json
import os
import stat
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(REPO_ROOT, ".github", "scripts")
WORKFLOWS = os.path.join(REPO_ROOT, ".github", "workflows")
sys.path.insert(0, SCRIPTS)


def _read_workflow(name):
    with open(os.path.join(WORKFLOWS, name)) as f:
        return f.read()


class TestC14ApiDispatchable(unittest.TestCase):
    """C-14: one API call must be able to trigger reassembly."""

    def test_repository_dispatch_trigger_present(self):
        wf = _read_workflow("render-production-reassemble.yml")
        self.assertIn("repository_dispatch:", wf)
        self.assertIn("reassemble", wf)

    def test_inputs_resolve_from_client_payload(self):
        # Every inputs.* reference must fall back to client_payload
        # (repository_dispatch has no inputs context).
        wf = _read_workflow("render-production-reassemble.yml")
        import re
        bare = re.findall(r"\$\{\{\s*inputs\.\w+\s*\}\}", wf)
        self.assertEqual(bare, [], f"bare inputs.* refs without client_payload fallback: {bare}")

    def test_fail_fast_without_run_id(self):
        wf = _read_workflow("render-production-reassemble.yml")
        self.assertIn("no source_run_id", wf)

    def test_trigger_script_exists_and_executable(self):
        p = os.path.join(REPO_ROOT, "tools", "trigger_reassemble.sh")
        self.assertTrue(os.path.isfile(p), "trigger_reassemble.sh missing")
        self.assertTrue(os.stat(p).st_mode & stat.S_IXUSR, "not executable")
        with open(p) as f:
            content = f.read()
        self.assertIn("/dispatches", content)
        self.assertIn("event_type", content)
        self.assertIn("reassemble", content)
        self.assertIn("client_payload", content)


class TestFailureClassifier(unittest.TestCase):
    """The classifier must route each death to the right recovery."""

    def setUp(self):
        from classify_failure import classify
        self.classify = classify

    def test_assembly_death_routes_to_reassemble_only(self):
        jobs = [
            {"name": "plan", "conclusion": "success"},
            {"name": "render-chunk (0)", "conclusion": "success"},
            {"name": "render-chunk (1)", "conclusion": "success"},
            {"name": "assemble", "conclusion": "cancelled"},
        ]
        r = self.classify(jobs)
        self.assertEqual(r["classification"], "ASSEMBLY_DEATH")
        self.assertEqual(r["recovery"], "dispatch_reassemble_only")

    def test_assembly_timeout_is_death(self):
        jobs = [
            {"name": "plan", "conclusion": "success"},
            {"name": "render-chunk (0)", "conclusion": "success"},
            {"name": "assemble", "conclusion": "timed_out"},
        ]
        self.assertEqual(self.classify(jobs)["classification"], "ASSEMBLY_DEATH")

    def test_chunk_failure_routes_to_resume(self):
        jobs = [
            {"name": "plan", "conclusion": "success"},
            {"name": "render-chunk (0)", "conclusion": "success"},
            {"name": "render-chunk (1)", "conclusion": "failure"},
            {"name": "assemble", "conclusion": "skipped"},
        ]
        r = self.classify(jobs)
        self.assertEqual(r["classification"], "CHUNK_FAILURE")
        self.assertEqual(r["recovery"], "resume_render_failed_chunks")

    def test_plan_failure_routes_to_fix_inputs(self):
        r = self.classify([{"name": "plan", "conclusion": "failure"}])
        self.assertEqual(r["classification"], "PLAN_FAILURE")

    def test_success_needs_no_recovery(self):
        jobs = [
            {"name": "plan", "conclusion": "success"},
            {"name": "render-chunk (0)", "conclusion": "success"},
            {"name": "assemble", "conclusion": "success"},
        ]
        r = self.classify(jobs)
        self.assertEqual(r["classification"], "SUCCESS")
        self.assertEqual(r["recovery"], "none")

    def test_unknown_when_unclassifiable(self):
        jobs = [{"name": "plan", "conclusion": "success"},
                {"name": "render-chunk (0)", "conclusion": None}]
        self.assertEqual(self.classify(jobs)["classification"], "UNKNOWN")


class TestChunkLedger(unittest.TestCase):
    """The ledger must be complete-only and name missing chunks."""

    def setUp(self):
        from build_ledger import build_ledger
        self.build_ledger = build_ledger

    def _job(self, n):
        # Real job manifest structure: plan.chunks as [{"chunk_id","start","end"}]
        return {"job_identity": "test-job",
                "plan": {"chunks": [{"chunk_id": i, "start": i*100,
                                     "end": i*100+99} for i in range(n)]}}

    def _chunk(self, cid, ok=True, reused=False):
        return {
            "chunk_id": cid,
            "frame_range": {"start": cid * 100, "end": cid * 100 + 99},
            "output_sha256": "ab" * 32,
            "output_bytes": 12345,
            "attempt": 1,
            "generation_fingerprint": "fp",
            "provenance": {"reused": reused, "origin_run_id": "1",
                           "origin_job_identity": "test-job"},
            "validation": {"output_exists": ok, "output_non_empty": ok},
        }

    def test_complete_ledger(self):
        job = self._job(3)
        chunks = {i: self._chunk(i) for i in range(3)}
        ledger = self.build_ledger(job, chunks)
        self.assertTrue(ledger["complete"])
        self.assertEqual(ledger["ok_chunks"], 3)

    def test_incomplete_names_missing(self):
        job = self._job(3)
        chunks = {0: self._chunk(0), 2: self._chunk(2)}  # chunk 1 missing
        ledger = self.build_ledger(job, chunks)
        self.assertFalse(ledger["complete"])
        missing = [e["chunk_id"] for e in ledger["entries"]
                   if e["status"] == "missing"]
        self.assertEqual(missing, [1])

    def test_failed_chunk_blocks(self):
        job = self._job(2)
        chunks = {0: self._chunk(0), 1: self._chunk(1, ok=False)}
        ledger = self.build_ledger(job, chunks)
        self.assertFalse(ledger["complete"])

    def test_reused_marked(self):
        job = self._job(1)
        chunks = {0: self._chunk(0, reused=True)}
        ledger = self.build_ledger(job, chunks)
        self.assertTrue(ledger["complete"])
        self.assertEqual(ledger["entries"][0]["status"], "reused_ok")

    def test_ledger_gates_both_workflows(self):
        for wf_name in ("render-production.yml",
                        "render-production-reassemble.yml"):
            wf = _read_workflow(wf_name)
            self.assertIn("build_ledger.py", wf,
                           f"{wf_name} missing ledger gate")
            self.assertIn("chunk ledger", wf.lower(),
                           f"{wf_name} missing ledger step")


if __name__ == "__main__":
    unittest.main()


class TestAssemblyOnlySourceSha(unittest.TestCase):
    """2026-10-10: assembly_only mode must not invalidate chunks when the
    commit hash changes (e.g. after fixing assembly code). chunk_recovery
    keeps the strict check."""

    def setUp(self):
        sys.path.insert(0, os.path.join(REPO_ROOT, "tests"))
        from test_recovery import base_inputs, make_job_manifest
        from recovery import validate_resume_source
        self.base_inputs = base_inputs
        self.make_job_manifest = make_job_manifest
        self.validate = validate_resume_source

    def test_assembly_only_ignores_source_sha_change(self):
        prior = self.make_job_manifest(
            run_id="111", sha="a" * 40, inputs=self.base_inputs())
        current = self.base_inputs(source_sha="b" * 40)
        current["_plan_chunks"] = [
            {"chunk_id": c["chunk_id"], "start": c["start"], "end": c["end"]}
            for c in prior["plan"]["chunks"]
        ]
        r = self.validate(
            prior, current, current["asset_manifest_sha256"],
            prior_run_status={"status": "completed", "conclusion": "failure"},
            mode="assembly_only")
        self.assertTrue(r["ok"], f"assembly_only rejected: {r.get('errors', [])[:3]}")

    def test_chunk_recovery_still_strict_on_source_sha(self):
        prior = self.make_job_manifest(
            run_id="111", sha="a" * 40, inputs=self.base_inputs())
        current = self.base_inputs(source_sha="b" * 40)
        current["_plan_chunks"] = [
            {"chunk_id": c["chunk_id"], "start": c["start"], "end": c["end"]}
            for c in prior["plan"]["chunks"]
        ]
        r = self.validate(
            prior, current, current["asset_manifest_sha256"],
            prior_run_status={"status": "completed", "conclusion": "failure"},
            mode="chunk_recovery")
        self.assertFalse(r["ok"], "chunk_recovery should stay strict")

    def test_assembly_only_still_rejects_render_changes(self):
        prior = self.make_job_manifest(
            run_id="111", sha="a" * 40, inputs=self.base_inputs())
        # Different codec = genuinely different render, must be rejected
        current = self.base_inputs(source_sha="b" * 40, codec="vp9")
        current["_plan_chunks"] = [
            {"chunk_id": c["chunk_id"], "start": c["start"], "end": c["end"]}
            for c in prior["plan"]["chunks"]
        ]
        r = self.validate(
            prior, current, current["asset_manifest_sha256"],
            prior_run_status={"status": "completed", "conclusion": "failure"},
            mode="assembly_only")
        self.assertFalse(r["ok"], "real render changes must still be rejected")


class TestAssemblyOnlyResumePlan(unittest.TestCase):
    """2026-10-10: build_resume_plan in assembly_only mode must produce a
    zero-render plan (all chunks reusable) even when source_sha changed.
    This is the exact production bug from run 37987633411."""

    def test_assembly_only_zero_render_on_sha_change(self):
        import sys as _sys, os as _os
        _sys.path.insert(0, _os.path.join(REPO_ROOT, "tests"))
        from test_recovery import (base_inputs, make_job_manifest,
                                   make_chunk_manifest, build_manifest_shas)
        from recovery import build_resume_plan

        prior = make_job_manifest(run_id="111", sha="a" * 40,
                                  inputs=base_inputs())
        gen = prior["generation_fingerprint"]
        src = prior["github"]["source_sha"]
        pcm = {i: make_chunk_manifest(prior["job_identity"], i,
                                      i * 100, i * 100 + 99, gen,
                                      source_sha=src)
               for i in range(3)}
        # Current run at a DIFFERENT commit, identical render inputs
        current = base_inputs(source_sha="b" * 40)
        plan = [{"chunk_id": i, "start": i * 100, "end": i * 100 + 99}
                for i in range(3)]
        real_shas = {cid: cm["output_sha256"] for cid, cm in pcm.items()}
        result = build_resume_plan(
            prior, pcm, current, plan,
            prior["inputs"]["asset_manifest_sha256"],
            artifact_shas=real_shas,
            manifest_shas=build_manifest_shas(pcm),
            prior_run_status={"status": "completed", "conclusion": "failure"},
            mode="assembly_only")
        self.assertTrue(result["ok"], f"errors: {result.get('errors')}")
        rp = result["resume_plan"]
        self.assertEqual(rp["render_count"], 0,
                         f"expected zero render, got: {rp['render']}")
        self.assertEqual(rp["reused_count"], 3)


class TestConcatParity(unittest.TestCase):
    """BATCH 1: both assemble paths must concat identically — `-c copy`
    (stream copy, NO re-encode). Proven by run 37942159718: re-encode
    concat made ffmpeg report `dup=14` -> 23,165 frames vs 23,151 expected
    -> the frame-count gate failed. See .github/scripts/assembly_contract.py.
    """

    def _concat_lines(self, wf_name):
        wf = _read_workflow(wf_name)
        return [l.strip() for l in wf.splitlines()
                if "ffmpeg" in l and "-f concat" in l
                and "concat.txt" in l and "vo_concat" not in l]

    def test_main_workflow_concat_is_stream_copy(self):
        lines = self._concat_lines("render-production.yml")
        self.assertEqual(len(lines), 1, f"expected 1 video concat cmd, got {lines}")
        self.assertIn("-c copy", lines[0])

    def test_reassemble_workflow_concat_is_stream_copy(self):
        lines = self._concat_lines("render-production-reassemble.yml")
        self.assertEqual(len(lines), 1, f"expected 1 video concat cmd, got {lines}")
        self.assertIn("-c copy", lines[0])

    def test_neither_path_reencodes_during_concat(self):
        from assembly_contract import FORBIDDEN_CONCAT_CODECS
        for wf_name in ("render-production.yml",
                        "render-production-reassemble.yml"):
            for line in self._concat_lines(wf_name):
                for codec in FORBIDDEN_CONCAT_CODECS:
                    self.assertNotIn(codec, line,
                                     f"{wf_name} concat re-encodes with {codec}: {line}")

    def test_concat_commands_identical_across_paths(self):
        main = self._concat_lines("render-production.yml")
        reasm = self._concat_lines("render-production-reassemble.yml")
        # Compare the ffmpeg invocation itself (strip YAML indentation).
        norm = lambda s: " ".join(s.split())
        self.assertEqual(norm(main[0]), norm(reasm[0]),
                         "assemble-path concat commands diverged")

    def test_contract_module_defines_canonical_spec(self):
        from assembly_contract import (CONCAT_DEMUXER_FLAGS, CONCAT_VIDEO_CODEC,
                                       FORBIDDEN_CONCAT_CODECS)
        self.assertEqual(CONCAT_DEMUXER_FLAGS, ["-f", "concat", "-safe", "0"])
        self.assertEqual(CONCAT_VIDEO_CODEC, ["-c", "copy"])
        self.assertIn("libx264", FORBIDDEN_CONCAT_CODECS)


class TestSeamContract(unittest.TestCase):
    """Contract rule 1: chunk ranges must tile exactly; sum(chunk frames)
    == master frames. Pure-python, ffmpeg-free (assembly_contract)."""

    def setUp(self):
        from assembly_contract import (check_frame_ranges,
                                       check_master_frame_count)
        self.check_ranges = check_frame_ranges
        self.check_master = check_master_frame_count

    def _chunks(self, ranges):
        return [{"chunk_id": i, "start": s, "end": e}
                for i, (s, e) in enumerate(ranges)]

    def test_exact_tiling_passes(self):
        chunks = self._chunks([(0, 599), (600, 1199), (1200, 1799)])
        r = self.check_master(chunks, 1800)
        self.assertTrue(r["ok"], r["errors"])
        self.assertEqual(r["expected"], 1800)

    def test_seam_gap_detected_as_missing_frames(self):
        # Chunk 1 lost its last frame: 600..1198 instead of 600..1199,
        # and chunk 2 still starts at 1200 -> frame 1199 is missing.
        chunks = self._chunks([(0, 599), (600, 1198), (1200, 1799)])
        r = self.check_ranges(chunks)
        self.assertFalse(r["ok"])
        self.assertTrue(any("gap" in e for e in r["errors"]),
                        r["errors"])
        m = self.check_master(chunks, 1800)
        self.assertFalse(m["ok"])  # sum is 1799, not 1800

    def test_seam_overlap_detected_as_duplicate_frames(self):
        # Chunk boundary rendered twice: chunk 1 starts at 599, not 600.
        chunks = self._chunks([(0, 599), (599, 1199), (1200, 1799)])
        r = self.check_ranges(chunks)
        self.assertFalse(r["ok"])
        self.assertTrue(any("overlap" in e for e in r["errors"]),
                        r["errors"])

    def test_master_mismatch_detected(self):
        # The historical failure mode: master 23,165 vs expected 23,151.
        chunks = self._chunks([(i * 600, i * 600 + 599) for i in range(38)]
                              + [(22800, 23150)])
        r = self.check_master(chunks, 23165)
        self.assertFalse(r["ok"])
        self.assertIn("23151", str(r["errors"]))
        self.assertIn("23165", str(r["errors"]))

    def test_out_of_order_chunk_ids_tiled_by_id(self):
        chunks = self._chunks([(600, 1199), (0, 599), (1200, 1799)])
        # chunk_ids assigned 0,1,2 by position — reorder by id explicitly:
        chunks[0]["chunk_id"], chunks[1]["chunk_id"] = 1, 0
        r = self.check_master(chunks, 1800)
        self.assertTrue(r["ok"], r["errors"])

    def test_empty_plan_rejected(self):
        r = self.check_master([], 0)
        self.assertFalse(r["ok"])

    def test_single_chunk(self):
        r = self.check_master(self._chunks([(0, 23150)]), 23151)
        self.assertTrue(r["ok"], r["errors"])


class TestAudioContinuityContract(unittest.TestCase):
    """Contract rule 3: chunk audio is dropped at mux; the master audio is
    exclusively the canonical VO+bed mix. No audio-continuity requirement
    exists across chunk seams — by design, not by omission."""

    def _mux_block(self, wf_name):
        wf = _read_workflow(wf_name)
        idx = wf.find("Mux canonical audio")
        self.assertNotEqual(idx, -1, f"{wf_name}: mux step not found")
        return wf[idx:idx + 4000]

    def test_both_paths_drop_chunk_audio_at_mux(self):
        for wf_name in ("render-production.yml",
                        "render-production-reassemble.yml"):
            mux = self._mux_block(wf_name)
            self.assertIn('-map 0:v', mux,
                          f"{wf_name}: mux must map only concatenated video")
            self.assertIn('-map "[aout]"', mux,
                          f"{wf_name}: mux must map only the canonical mix")
            self.assertNotIn("-map 0:a", mux,
                             f"{wf_name}: chunk audio must not be mapped")

    def test_both_paths_stream_copy_video_at_mux(self):
        for wf_name in ("render-production.yml",
                        "render-production-reassemble.yml"):
            mux = self._mux_block(wf_name)
            self.assertIn("-c:v copy", mux,
                          f"{wf_name}: mux must not re-encode video")


class TestVerificationDeterminism(unittest.TestCase):
    """Same inputs -> same verdict; a tampered chunk changes the verdict."""

    def setUp(self):
        from assembly_contract import check_master_frame_count
        from build_ledger import build_ledger
        self.check_master = check_master_frame_count
        self.build_ledger = build_ledger

    def _chunks(self):
        return [{"chunk_id": i, "start": i * 600, "end": i * 600 + 599}
                for i in range(3)]

    def test_same_inputs_same_verdict(self):
        r1 = self.check_master(self._chunks(), 1800)
        r2 = self.check_master(self._chunks(), 1800)
        self.assertEqual(r1, r2)
        self.assertTrue(r1["ok"])

    def test_tampered_chunk_range_changes_verdict(self):
        chunks = self._chunks()
        ok_before = self.check_master(chunks, 1800)["ok"]
        # Tamper: chunk 1 silently gains a duplicated frame at the seam.
        chunks[1]["start"] = 599
        verdict = self.check_master(chunks, 1800)
        self.assertTrue(ok_before)
        self.assertFalse(verdict["ok"], "tampered seam must fail")

    def test_tampered_master_count_changes_verdict(self):
        chunks = self._chunks()
        self.assertTrue(self.check_master(chunks, 1800)["ok"])
        # The dup=14 failure mode: master inflated by re-encode dups.
        self.assertFalse(self.check_master(chunks, 1814)["ok"])

    def test_ledger_verdict_deterministic(self):
        job = {"job_identity": "det-job",
               "plan": {"chunks": [{"chunk_id": i, "start": i * 600,
                                    "end": i * 600 + 599}
                                   for i in range(3)]}}

        def chunk(cid):
            return {"chunk_id": cid,
                    "frame_range": {"start": cid * 600, "end": cid * 600 + 599},
                    "output_sha256": "ab" * 32, "output_bytes": 999,
                    "attempt": 1, "generation_fingerprint": "fp",
                    "provenance": {"reused": False},
                    "validation": {"output_exists": True,
                                   "output_non_empty": True}}

        l1 = self.build_ledger(job, {i: chunk(i) for i in range(3)})
        l2 = self.build_ledger(job, {i: chunk(i) for i in range(3)})
        self.assertEqual(l1, l2)
        self.assertTrue(l1["complete"])


class TestConcatFrameExactnessFfmpeg(unittest.TestCase):
    """End-to-end (needs ffmpeg; skipped gracefully when absent): build
    tiny Remotion-style chunks — H.264 with B-frames + AAC audio carrying
    the 2048-sample priming edit list (`-itsoffset -42667us`, exactly as
    Remotion's aac-priming.js does) — then concat with the workflow's
    `-c copy` command and assert exact frame-count preservation."""

    FFMPEG = "ffmpeg"
    FFPROBE = "ffprobe"

    @classmethod
    def setUpClass(cls):
        import shutil
        if shutil.which(cls.FFMPEG) is None or shutil.which(cls.FFPROBE) is None:
            raise unittest.SkipTest("ffmpeg/ffprobe not available")

    def _run(self, *args):
        import subprocess
        p = subprocess.run(args, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
        self.assertEqual(p.returncode, 0,
                         f"{args[0]} failed: {p.stderr.decode()[-500:]}")

    def _count_frames(self, path):
        import subprocess
        p = subprocess.run(
            [self.FFPROBE, "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=nb_read_frames",
             "-of", "default=noprint_wrappers=1:nokey=1",
             "-count_frames", path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(p.returncode, 0)
        return int(p.stdout.decode().strip())

    def test_stream_copy_concat_preserves_exact_frame_count(self):
        import os
        import tempfile
        work = tempfile.mkdtemp(prefix="concat-parity-")
        n_chunks, frames_per_chunk = 3, 30  # tiny: fast, still exercises seams
        chunk_files = []
        for i in range(n_chunks):
            v = os.path.join(work, f"v_{i}.mp4")
            a = os.path.join(work, f"a_{i}.m4a")
            c = os.path.join(work, f"chunk_{i}.mp4")
            # Video: H.264 with B-frames (x264 defaults, like Remotion).
            self._run(self.FFMPEG, "-y", "-v", "error",
                      "-f", "lavfi",
                      "-i", f"testsrc=size=64x64:rate=30:duration=1",
                      "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", v)
            # Audio: AAC, then muxed with Remotion's priming shift so the
            # chunk carries the 2048-sample edit list (the real-world hazard).
            self._run(self.FFMPEG, "-y", "-v", "error",
                      "-f", "lavfi", "-i", "sine=frequency=440:duration=1",
                      "-c:a", "aac", "-b:a", "64k", a)
            self._run(self.FFMPEG, "-y", "-v", "error",
                      "-itsoffset", "-42667us", "-i", a, "-i", v,
                      "-c", "copy", "-map", "0:a", "-map", "1:v", c)
            chunk_files.append(c)

        per_chunk = [self._count_frames(c) for c in chunk_files]
        self.assertTrue(all(n == frames_per_chunk for n in per_chunk),
                        f"chunk frame counts: {per_chunk}")

        concat_list = os.path.join(work, "concat.txt")
        with open(concat_list, "w") as f:
            for c in chunk_files:
                f.write(f"file '{c}'\n")
        master = os.path.join(work, "master.mp4")
        # The EXACT command from both workflows' assemble paths.
        self._run(self.FFMPEG, "-y", "-v", "error",
                  "-f", "concat", "-safe", "0", "-i", concat_list,
                  "-c", "copy", master)
        expected = sum(per_chunk)
        actual = self._count_frames(master)
        self.assertEqual(actual, expected,
                         f"stream-copy concat changed frame count: "
                         f"{actual} != sum(chunks)={expected}")
