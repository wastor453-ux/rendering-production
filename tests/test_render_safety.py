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
            "validation": {"passed": ok},
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
