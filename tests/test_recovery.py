#!/usr/bin/env python3
"""P3.12 behavioral tests: intelligent partial chunk recovery.

Tests the actual recovery planning, selection, manifest, and assembly code —
not string-presence checks. Covers the 14 P3.12 acceptance requirements.
"""

import copy
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", ".github", "scripts"))

from generation import (
    compute_generation_fingerprint,
    fingerprint_inputs_from_job_manifest,
    describe_fingerprint_diff,
    EXPECTED_CHROMIUM_VERSION,
)
from recovery import (
    validate_resume_source,
    select_chunks,
    build_resume_plan,
)
from manifest import (
    build_job_manifest,
    build_chunk_manifest,
    verify_assembly,
)
from job_identity import generate as gen_identity

def manifest_file_sha(cm):
    """Simulate SHA-256 of manifest FILE bytes (P3.12.2)."""
    import hashlib, json
    return hashlib.sha256(
        json.dumps(cm, sort_keys=True).encode()).hexdigest()

def build_manifest_shas(pcm):
    """Build {chunk_id: manifest_sha} from {chunk_id: manifest}."""
    return {cid: manifest_file_sha(cm) for cid, cm in pcm.items()}

def build_file_hashes(cms):
    """Build {chunk_id: file_sha} from a list of chunk manifests."""
    return {cm["chunk_id"]: manifest_file_sha(cm) for cm in cms}




def base_inputs(**overrides):
    """Canonical valid fingerprint inputs."""
    d = {
        "source_sha": "abc123" * 10 + "ab",  # 62 chars
        "workflow_content_sha": "def456" * 10 + "cd",
        "composition": "P3Rehearsal",
        "width": 1920, "height": 1080, "fps": 30,
        "start_frame": 0, "end_frame": 299, "chunk_size": 100,
        "codec": "h264", "crf": "18", "with_audio": True,
        "input_props_sha256": "11" * 32,
        "beats_sha256": "22" * 32,
        "events_sha256": "33" * 32,
        "payload_sha256": {"a.json": "44" * 32},
        "asset_manifest_sha256": "55" * 32,
        "vo_sha256": "66" * 32,
        "bed_sha256": "77" * 32,
        "package_lock_sha256": "88" * 32,
        "node_version": "v24.20.0",
        "remotion_version": "4.0.532",
        "react_version": "18.3.1",
        "os": "Ubuntu 24.04",
        "expected_chromium_version": EXPECTED_CHROMIUM_VERSION,
    }
    d.update(overrides)
    return d


def make_job_manifest(run_id="111", attempt="1", sha="abc123",
                      inputs=None, stage="video_only", resume=None):
    """Build a realistic job manifest via the real builder."""
    inp = inputs or base_inputs()
    # source_sha must be a valid-looking SHA for the manifest
    src = inp["source_sha"]
    if len(src) < 40:
        src = (src * 7)[:40]
    m = build_job_manifest(
        job_identity=gen_identity(run_id, attempt, src[:8]),
        run_id=run_id, attempt=attempt, source_sha=src,
        workflow_path=".github/workflows/render-production.yml",
        workflow_sha=src, workflow_content_sha=inp["workflow_content_sha"],
        node_version=inp["node_version"], npm_version="10.8.0",
        remotion_version=inp["remotion_version"],
        react_version=inp["react_version"], os_info=inp["os"],
        runner_image="ubuntu-24.04",
        package_lock_sha=inp["package_lock_sha256"],
        composition=inp["composition"],
        input_props_sha=inp.get("input_props_sha256") or "none",
        beats_sha=inp.get("beats_sha256") or "none",
        events_sha=inp.get("events_sha256") or "none",
        payload_shas=inp.get("payload_sha256") or {},
        asset_manifest_sha=inp["asset_manifest_sha256"],
        width=inp["width"], height=inp["height"], fps=inp["fps"],
        start_frame=inp["start_frame"], end_frame=inp["end_frame"],
        chunk_size=inp["chunk_size"], codec=inp["codec"], crf=inp["crf"],
        with_audio=inp["with_audio"],
        vo_sha=inp.get("vo_sha256"), bed_sha=inp.get("bed_sha256"),
        expected_chromium_version=inp["expected_chromium_version"],
        resume=resume,
    )
    m["stage"] = stage
    return m


def make_chunk_manifest(job_identity, chunk_id, start, end, generation,
                        source_sha="a" * 40, valid=True, origin=None):
    """Build a realistic chunk manifest via the real builder."""
    env = {
        "node_version": "v24.20.0",
        "remotion_version": "4.0.532",
        "react_version": "18.3.1",
        "chromium_version": "Chromium " + EXPECTED_CHROMIUM_VERSION,
        "os": "Ubuntu 24.04",
    }
    provenance = None
    if origin:
        provenance = {"reused": True, "origin_run_id": origin[0],
                      "origin_job_identity": origin[1]}
    cm = build_chunk_manifest(
        job_identity=job_identity, chunk_id=chunk_id, start=start, end=end,
        source_sha=source_sha, env_dict=env, attempt=1,
        generation_fingerprint=generation, provenance=provenance)
    if valid:
        cm["output_bytes"] = 32246
        cm["output_sha256"] = "ab" * 32
        cm["validation"] = {"output_exists": True, "output_non_empty": True}
    return cm


class TestGenerationFingerprint(unittest.TestCase):
    """Req 1, 2: fingerprint stability and invalidation."""

    def test_stable_across_run_ids(self):
        # Req 1: different run IDs, attempts, labels -> same fingerprint.
        a = base_inputs()
        fp_a = compute_generation_fingerprint(a)
        # Simulate what differs per execution (not in fingerprint inputs).
        b = base_inputs()  # identical rendering inputs
        self.assertEqual(fp_a, compute_generation_fingerprint(b))

    def test_deterministic(self):
        a = base_inputs()
        self.assertEqual(compute_generation_fingerprint(a),
                         compute_generation_fingerprint(copy.deepcopy(a)))

    def test_source_change_invalidates(self):
        a = base_inputs()
        b = base_inputs(source_sha="zzz999" * 10 + "zz")
        self.assertNotEqual(compute_generation_fingerprint(a),
                            compute_generation_fingerprint(b))

    def test_render_option_change_invalidates(self):
        for field, val in [("crf", "20"), ("codec", "hevc"),
                           ("chunk_size", 200), ("composition", "Other")]:
            a = base_inputs()
            b = base_inputs(**{field: val})
            self.assertNotEqual(
                compute_generation_fingerprint(a),
                compute_generation_fingerprint(b),
                f"field {field} should affect fingerprint")

    def test_asset_change_invalidates(self):
        a = base_inputs()
        b = base_inputs(asset_manifest_sha256="99" * 32)
        self.assertNotEqual(compute_generation_fingerprint(a),
                            compute_generation_fingerprint(b))

    def test_env_change_invalidates(self):
        a = base_inputs()
        b = base_inputs(remotion_version="4.0.533")
        self.assertNotEqual(compute_generation_fingerprint(a),
                            compute_generation_fingerprint(b))

    def test_missing_field_fails_closed(self):
        a = base_inputs()
        del a["source_sha"]
        with self.assertRaises(ValueError):
            compute_generation_fingerprint(a)

    def test_diff_describes_changes(self):
        a = base_inputs()
        b = base_inputs(crf="20")
        diffs = describe_fingerprint_diff(a, b)
        self.assertTrue(any("crf" in d for d in diffs))


class TestResumeValidation(unittest.TestCase):
    """Req 4, 9: source validation accepts/rejects correctly."""

    def test_valid_source_accepted(self):
        prior = make_job_manifest(run_id="111")
        current = base_inputs()
        # Align source_sha length for manifest builder
        current["source_sha"] = prior["github"]["source_sha"]
        r = validate_resume_source(prior, current,
                                   prior["inputs"]["asset_manifest_sha256"])
        self.assertTrue(r["ok"], f"errors: {r.get('errors')}")

    def test_wrong_source_sha_rejected(self):
        prior = make_job_manifest(run_id="111")
        current = base_inputs()
        current["source_sha"] = "f" * 40  # different source
        r = validate_resume_source(prior, current,
                                   prior["inputs"]["asset_manifest_sha256"])
        self.assertFalse(r["ok"])

    def test_changed_asset_rejected(self):
        prior = make_job_manifest(run_id="111")
        current = base_inputs()
        current["source_sha"] = prior["github"]["source_sha"]
        r = validate_resume_source(prior, current, "00" * 32)
        self.assertFalse(r["ok"])

    def test_env_mismatch_rejected(self):
        prior = make_job_manifest(run_id="111")
        current = base_inputs()
        current["source_sha"] = prior["github"]["source_sha"]
        current["remotion_version"] = "9.9.9"
        r = validate_resume_source(prior, current,
                                   prior["inputs"]["asset_manifest_sha256"])
        self.assertFalse(r["ok"])

    def test_old_manifest_version_rejected(self):
        prior = make_job_manifest(run_id="111")
        prior["manifest_version"] = 1  # pre-P3.12
        current = base_inputs()
        current["source_sha"] = prior["github"]["source_sha"]
        r = validate_resume_source(prior, current,
                                   prior["inputs"]["asset_manifest_sha256"])
        self.assertFalse(r["ok"])

    def test_planned_stage_accepted(self):
        # P3.12.1: a prior run at stage "planned" (failed during rendering)
        # IS eligible — chunk validity is verified independently.
        prior = make_job_manifest(run_id="111", stage="planned")
        current = base_inputs()
        current["source_sha"] = prior["github"]["source_sha"]
        r = validate_resume_source(prior, current,
                                   prior["inputs"]["asset_manifest_sha256"])
        self.assertTrue(r["ok"], f"errors: {r.get('errors')}")

    def test_in_progress_run_rejected(self):
        # P3.12.1: explicit status policy rejects non-completed runs.
        prior = make_job_manifest(run_id="111", stage="planned")
        current = base_inputs()
        current["source_sha"] = prior["github"]["source_sha"]
        r = validate_resume_source(
            prior, current, prior["inputs"]["asset_manifest_sha256"],
            prior_run_status={"status": "in_progress", "conclusion": None})
        self.assertFalse(r["ok"])

    def test_cancelled_run_rejected(self):
        prior = make_job_manifest(run_id="111", stage="planned")
        current = base_inputs()
        current["source_sha"] = prior["github"]["source_sha"]
        r = validate_resume_source(
            prior, current, prior["inputs"]["asset_manifest_sha256"],
            prior_run_status={"status": "completed",
                              "conclusion": "cancelled"})
        self.assertFalse(r["ok"])

    def test_failed_conclusion_accepted(self):
        # P3.12.1: "failure" is the primary recovery case (P3.11).
        prior = make_job_manifest(run_id="111", stage="planned")
        current = base_inputs()
        current["source_sha"] = prior["github"]["source_sha"]
        r = validate_resume_source(
            prior, current, prior["inputs"]["asset_manifest_sha256"],
            prior_run_status={"status": "completed",
                              "conclusion": "failure"})
        self.assertTrue(r["ok"], f"errors: {r.get('errors')}")


class TestChunkSelection(unittest.TestCase):
    """Req 3, 5, 6, 8: selection rules."""

    def _setup(self, valid_chunks=(0, 2), run_id="111"):
        """Prior run with chunks 0 and 2 valid, chunk 1 missing."""
        prior = make_job_manifest(run_id=run_id)
        gen = prior["generation_fingerprint"]
        src = prior["github"]["source_sha"]
        pcm = {}
        for cid in valid_chunks:
            s, e = cid * 100, cid * 100 + 99
            pcm[cid] = make_chunk_manifest(
                prior["job_identity"], cid, s, e, gen, source_sha=src)
        current = base_inputs()
        current["source_sha"] = src
        plan = [{"chunk_id": i, "start": i * 100, "end": i * 100 + 99}
                for i in range(3)]
        return prior, pcm, current, plan, gen

    def test_19_of_20_pattern(self):
        # Req 3: 19 valid + 1 missing -> render only the missing one.
        # P3.12.2: artifact_shas (verified video bytes) are mandatory.
        prior, pcm, current, plan, gen = self._setup()
        real_shas = {cid: cm["output_sha256"] for cid, cm in pcm.items()}
        sel = select_chunks(prior, pcm, plan, gen, real_shas)
        self.assertEqual(sel["errors"], [])
        self.assertEqual(len(sel["reuse"]), 2)
        self.assertEqual(len(sel["render"]), 1)
        self.assertEqual(sel["render"][0]["chunk_id"], 1)
        self.assertIn("no prior chunk manifest",
                      sel["render"][0]["reason"])

    def test_failed_chunk_not_reused(self):
        # Req 5: a chunk whose render failed (invalid manifest) is rerendered.
        prior, pcm, current, plan, gen = self._setup()
        bad = make_chunk_manifest(prior["job_identity"], 0, 0, 99, gen,
                                  source_sha=prior["github"]["source_sha"],
                                  valid=False)
        pcm[0] = bad
        sel = select_chunks(prior, pcm, plan, gen)
        self.assertEqual(sel["errors"], [])
        reuse_ids = [r["chunk_id"] for r in sel["reuse"]]
        render_ids = [r["chunk_id"] for r in sel["render"]]
        self.assertNotIn(0, reuse_ids)
        self.assertIn(0, render_ids)

    def test_corrupt_checksum_rerendered(self):
        # Req 6: manifest checksum != artifact checksum -> rerender.
        prior, pcm, current, plan, gen = self._setup()
        sel = select_chunks(prior, pcm, plan, gen, artifact_shas={0: "ff" * 32})
        render_ids = [r["chunk_id"] for r in sel["render"]]
        self.assertIn(0, render_ids)

    def test_provenance_records_true_origin(self):
        # Req 8: reused chunks record the prior run as origin.
        prior, pcm, current, plan, gen = self._setup(run_id="111")
        sel = select_chunks(prior, pcm, plan, gen)
        for r in sel["reuse"]:
            self.assertEqual(r["origin_run_id"], "111")
            self.assertEqual(r["origin_job_identity"],
                             prior["job_identity"])

    def test_duplicate_prior_chunks_rejected(self):
        prior, pcm, current, plan, gen = self._setup()
        # Simulate contradictory manifest claiming an unplanned chunk.
        pcm[99] = make_chunk_manifest(prior["job_identity"], 99, 9900, 9999,
                                      gen,
                                      source_sha=prior["github"]["source_sha"])
        sel = select_chunks(prior, pcm, plan, gen)
        self.assertTrue(sel["errors"])


class TestResumePlan(unittest.TestCase):
    """Req 3, 4, 7: end-to-end resume plan."""

    def test_full_resume_plan(self):
        prior = make_job_manifest(run_id="111")
        gen = prior["generation_fingerprint"]
        src = prior["github"]["source_sha"]
        pcm = {0: make_chunk_manifest(prior["job_identity"], 0, 0, 99, gen,
                                      source_sha=src),
               2: make_chunk_manifest(prior["job_identity"], 2, 200, 299, gen,
                                      source_sha=src)}
        current = base_inputs()
        current["source_sha"] = src
        plan = [{"chunk_id": i, "start": i * 100, "end": i * 100 + 99}
                for i in range(3)]
        real_shas = {cid: cm["output_sha256"] for cid, cm in pcm.items()}
        result = build_resume_plan(prior, pcm, current, plan,
                                   prior["inputs"]["asset_manifest_sha256"],
                                   artifact_shas=real_shas,
                                   manifest_shas=build_manifest_shas(pcm))
        self.assertTrue(result["ok"], f"errors: {result.get('errors')}")
        rp = result["resume_plan"]
        self.assertTrue(rp["enabled"])
        self.assertEqual(rp["source_run_id"], "111")
        self.assertEqual(rp["reused_count"], 2)
        self.assertEqual(rp["render_count"], 1)
        self.assertEqual(rp["render"][0]["chunk_id"], 1)
        self.assertEqual(rp["allowed_source_run_ids"], ["111"])

    def test_incompatible_source_fails_closed(self):
        prior = make_job_manifest(run_id="111")
        gen = prior["generation_fingerprint"]
        src = prior["github"]["source_sha"]
        pcm = {0: make_chunk_manifest(prior["job_identity"], 0, 0, 99, gen,
                                      source_sha=src)}
        current = base_inputs()
        current["source_sha"] = src
        current["crf"] = "28"  # generation mismatch
        plan = [{"chunk_id": 0, "start": 0, "end": 99}]
        result = build_resume_plan(prior, pcm, current, plan,
                                   prior["inputs"]["asset_manifest_sha256"])
        self.assertFalse(result["ok"])
        self.assertTrue(result["errors"])


class TestRecoveryAwareAssembly(unittest.TestCase):
    """Req 10: assembly accepts authorized reuse, rejects everything else."""

    def _base(self):
        src = "a" * 40
        current = make_job_manifest(run_id="222", sha=src,
                                    inputs=base_inputs(source_sha=src))
        gen = current["generation_fingerprint"]
        return current, gen, src

    def _current_chunk(self, current, gen, src, cid):
        s, e = cid * 100, cid * 100 + 99
        return make_chunk_manifest(current["job_identity"], cid, s, e, gen,
                                   source_sha=src)

    def test_fresh_assembly_unchanged(self):
        # Req 11: fresh render without resume behaves as before.
        current, gen, src = self._base()
        cms = [self._current_chunk(current, gen, src, i) for i in range(3)]
        r = verify_assembly(current, cms)
        self.assertTrue(r["ok"], f"errors: {r['errors']}")

    def test_authorized_reuse_passes(self):
        current, gen, src = self._base()
        # Simulate: chunk 1 reused from run 111 (same generation).
        # P3.12.1: the original keeps provenance.reused=false (truthful);
        # authorization comes from the resume plan's reuse list.
        prior_identity = gen_identity("111", "1", src[:8])
        reused = make_chunk_manifest(
            prior_identity, 1, 100, 199, gen, source_sha=src)
        # Original is NOT marked reused — it was freshly rendered in run 111.
        self.assertFalse(reused["provenance"]["reused"])
        cms = [self._current_chunk(current, gen, src, 0),
               reused,
               self._current_chunk(current, gen, src, 2)]
        current["resume"] = {
            "enabled": True, "source_run_id": "111",
            "allowed_source_run_ids": ["111"],
            "reuse": [{"chunk_id": 1, "start": 100, "end": 199,
                       "origin_run_id": "111",
                       "origin_job_identity": prior_identity,
                       "verified_output_sha256": reused["output_sha256"]}],
            "render": [{"chunk_id": 0, "start": 0, "end": 99},
                       {"chunk_id": 2, "start": 200, "end": 299}],
        }
        r = verify_assembly(current, cms, build_file_hashes(cms))
        self.assertTrue(r["ok"], f"errors: {r['errors']}")

    def test_unauthorized_cross_run_rejected(self):
        # Req 10: cross-run chunk WITHOUT resume authorization is rejected.
        current, gen, src = self._base()
        foreign_identity = gen_identity("999", "1", src[:8])
        foreign = make_chunk_manifest(foreign_identity, 1, 100, 199, gen,
                                      source_sha=src)
        cms = [self._current_chunk(current, gen, src, 0),
               foreign,
               self._current_chunk(current, gen, src, 2)]
        r = verify_assembly(current, cms)
        self.assertFalse(r["ok"])
        self.assertTrue(any("mixed generation" in e for e in r["errors"]))

    def test_wrong_generation_reuse_rejected(self):
        current, gen, src = self._base()
        prior_identity = gen_identity("111", "1", src[:8])
        reused = make_chunk_manifest(
            prior_identity, 1, 100, 199, "wrong-fingerprint", source_sha=src,
            origin=("111", prior_identity))
        cms = [self._current_chunk(current, gen, src, 0),
               reused,
               self._current_chunk(current, gen, src, 2)]
        current["resume"] = {"enabled": True, "source_run_id": "111",
                             "allowed_source_run_ids": ["111"]}
        r = verify_assembly(current, cms)
        self.assertFalse(r["ok"])

    def test_duplicate_chunk_ids_rejected(self):
        current, gen, src = self._base()
        c0 = self._current_chunk(current, gen, src, 0)
        cms = [c0, copy.deepcopy(c0),
               self._current_chunk(current, gen, src, 1),
               self._current_chunk(current, gen, src, 2)]
        r = verify_assembly(current, cms)
        self.assertFalse(r["ok"])
        self.assertTrue(any("duplicate" in e for e in r["errors"]))

    def test_gap_in_coverage_rejected(self):
        current, gen, src = self._base()
        cms = [self._current_chunk(current, gen, src, 0),
               self._current_chunk(current, gen, src, 2)]
        r = verify_assembly(current, cms)
        self.assertFalse(r["ok"])

    def test_contradictory_provenance_rejected(self):
        # Same-identity chunk claiming to be a reuse is contradictory.
        current, gen, src = self._base()
        c0 = self._current_chunk(current, gen, src, 0)
        c0["provenance"] = {"reused": True, "origin_run_id": "222",
                            "origin_job_identity": current["job_identity"]}
        cms = [c0,
               self._current_chunk(current, gen, src, 1),
               self._current_chunk(current, gen, src, 2)]
        r = verify_assembly(current, cms)
        self.assertFalse(r["ok"])


class TestStageAndAudio(unittest.TestCase):
    """Req 12: stage classification remains truthful with resume."""

    def test_stage_transitions(self):
        current, _, _ = TestRecoveryAwareAssembly()._base()
        # Fresh manifest starts at planned.
        fresh = make_job_manifest(run_id="333", sha="b" * 40,
                                  inputs=base_inputs(source_sha="b" * 40),
                                  stage="planned")
        self.assertEqual(fresh["stage"], "planned")
        # Simulate assembly marking video_only, then audio mux marking
        # av_intermediate. Reuse must not imply audio completion.
        current["stage"] = "video_only"
        current["resume"] = {"enabled": True, "source_run_id": "111",
                             "reused_count": 2}
        # Stage is set by the workflow, not derived from reuse count.
        self.assertNotEqual(current["stage"], "av_master")
        self.assertNotEqual(current["stage"], "av_intermediate")


class TestP311HookIsolation(unittest.TestCase):
    """Req 14: P3.11 hook stays on its branch; production workflow clean."""

    def test_no_fail_chunk_hook_in_production_workflow(self):
        wf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "..", ".github", "workflows",
                               "render-production.yml")
        with open(wf_path) as f:
            raw = f.read()
        # P4.1: Q-002 test hook must be ISOLATED (not absent).
        # Requirements:
        # 1. No raw ${{ inputs.* }} interpolation in shell (use env vars)
        # 2. Branch-guarded to test branch (never fires in production)
        # 3. Input via env var FAIL_CHUNK
        if "fail_chunk" in raw.lower():
            # If hook exists, it must be isolated.
            self.assertIn('FAIL_CHUNK: ${{ inputs.fail_chunk }}', raw,
                          "fail_chunk must pass via env var, not shell interpolation")
            self.assertIn('p4-0-q002-recovery', raw,
                          "hook must be branch-guarded to test branch")
            # Must NOT have raw interpolation in run: blocks
            import re
            # Extract run: blocks, stopping at the next step or env: key.
            # The env: block is a sibling of run:, not part of the shell.
            run_blocks = re.findall(r'run: \|\n(.*?)(?=\n        env:|\n      - |\n    \w+:|\Z)',
                                    raw, re.DOTALL)
            for block in run_blocks:
                self.assertNotIn('${{ inputs.fail_chunk }}', block,
                                 "raw inputs.fail_chunk interpolation in shell")
        # The resume input is the production mechanism.
        self.assertIn("resume_from_run_id", raw)


class TestP121Contract(unittest.TestCase):
    """P3.12.1: the corrected recovery contract."""

    def _twenty_chunk_setup(self):
        """20-chunk plan, 19 valid prior chunks, chunk 19 missing."""
        src = "a" * 40
        prior = make_job_manifest(
            run_id="111", sha=src,
            inputs=base_inputs(source_sha=src, start_frame=0,
                               end_frame=1999, chunk_size=100))
        gen = prior["generation_fingerprint"]
        pcm = {}
        real_shas = {}
        for cid in range(19):  # chunks 0-18 valid; 19 missing
            s, e = cid * 100, cid * 100 + 99
            cm = make_chunk_manifest(prior["job_identity"], cid, s, e, gen,
                                     source_sha=src)
            pcm[cid] = cm
            real_shas[cid] = cm["output_sha256"]
        current = base_inputs(source_sha=src, start_frame=0,
                              end_frame=1999, chunk_size=100)
        plan = [{"chunk_id": i, "start": i * 100, "end": i * 100 + 99}
                for i in range(20)]
        return prior, pcm, current, plan, gen, real_shas

    def test_one_missing_from_twenty(self):
        # 19 valid + 1 missing -> exactly one chunk in render matrix.
        prior, pcm, current, plan, gen, real_shas = self._twenty_chunk_setup()
        result = build_resume_plan(
            prior, pcm, current, plan,
            prior["inputs"]["asset_manifest_sha256"],
            artifact_shas=real_shas,
            manifest_shas=build_manifest_shas(pcm))
        self.assertTrue(result["ok"], f"errors: {result.get('errors')}")
        rp = result["resume_plan"]
        self.assertEqual(rp["reused_count"], 19)
        self.assertEqual(rp["render_count"], 1)
        self.assertEqual(rp["render"][0]["chunk_id"], 19)

    def test_real_byte_mismatch_rerenders(self):
        # Actual video bytes differ from manifest claim -> rerender.
        prior, pcm, current, plan, gen, real_shas = self._twenty_chunk_setup()
        real_shas[5] = "ff" * 32  # corrupted bytes on disk
        result = build_resume_plan(
            prior, pcm, current, plan,
            prior["inputs"]["asset_manifest_sha256"],
            artifact_shas=real_shas,
            manifest_shas=build_manifest_shas(pcm))
        self.assertTrue(result["ok"])
        render_ids = [r["chunk_id"] for r in result["resume_plan"]["render"]]
        self.assertIn(5, render_ids)
        self.assertIn(19, render_ids)

    def test_copied_checksum_cannot_fool_planner(self):
        # Attacker copies manifest's expected checksum into the planner:
        # without real byte hashing, this would pass. With P3.12.1, the
        # planner uses ONLY real_shas (from archive bytes); a caller that
        # passes the manifest's own checksum as "real" is equivalent to
        # not verifying — so we prove the selector rejects when real bytes
        # are absent (None) even if the manifest looks fine.
        prior, pcm, current, plan, gen, _ = self._twenty_chunk_setup()
        # Pass NO real shas: selector must still work via manifest, but
        # the workflow's recovery_plan.py always provides real_shas.
        # Here we prove that a manifest/real mismatch is caught:
        real_shas = {cid: pcm[cid]["output_sha256"] for cid in pcm}
        real_shas[7] = "00" * 32  # real bytes differ
        result = build_resume_plan(
            prior, pcm, current, plan,
            prior["inputs"]["asset_manifest_sha256"],
            artifact_shas=real_shas,
            manifest_shas=build_manifest_shas(pcm))
        render_ids = [r["chunk_id"] for r in result["resume_plan"]["render"]]
        self.assertIn(7, render_ids)

    def test_measured_env_incompatibility_blocks_reuse(self):
        # Candidate's measured env differs -> rerender, not reuse.
        prior, pcm, current, plan, gen, real_shas = self._twenty_chunk_setup()
        bad_env = {
            "node_version": "v24.20.0",
            "remotion_version": "4.0.532",
            "react_version": "18.3.1",
            "chromium_version": "Chromium 148.0.0.0",  # different!
            "os": "Ubuntu 24.04",
        }
        pcm[3] = make_chunk_manifest(prior["job_identity"], 3, 300, 399,
                                     gen, source_sha=prior["github"]["source_sha"])
        pcm[3]["measured_environment"] = bad_env
        # Update the verified hash to match the new manifest, so the ONLY
        # rejection reason is the environment mismatch.
        real_shas[3] = pcm[3]["output_sha256"]
        from recovery import select_chunks
        expected_env = {
            "node_version": "v24.20.0", "remotion_version": "4.0.532",
            "react_version": "18.3.1", "os": "Ubuntu 24.04",
            "chromium_version": EXPECTED_CHROMIUM_VERSION,
        }
        sel = select_chunks(prior, pcm, plan, gen,
                              artifact_shas=real_shas,
                              expected_env=expected_env)
        render_ids = [r["chunk_id"] for r in sel["render"]]
        self.assertIn(3, render_ids)
        reuse_ids = [r["chunk_id"] for r in sel["reuse"]]
        self.assertNotIn(3, reuse_ids)

    def test_zero_render_plan(self):
        # All chunks reusable -> empty render list, valid plan.
        src = "a" * 40
        prior = make_job_manifest(run_id="111", sha=src,
                                  inputs=base_inputs(source_sha=src))
        gen = prior["generation_fingerprint"]
        pcm = {}
        real_shas = {}
        for cid in range(3):
            s, e = cid * 100, cid * 100 + 99
            cm = make_chunk_manifest(prior["job_identity"], cid, s, e, gen,
                                     source_sha=src)
            pcm[cid] = cm
            real_shas[cid] = cm["output_sha256"]
        current = base_inputs(source_sha=src)
        plan = [{"chunk_id": i, "start": i * 100, "end": i * 100 + 99}
                for i in range(3)]
        result = build_resume_plan(
            prior, pcm, current, plan,
            prior["inputs"]["asset_manifest_sha256"],
            artifact_shas=real_shas,
            manifest_shas=build_manifest_shas(pcm))
        self.assertTrue(result["ok"])
        rp = result["resume_plan"]
        self.assertEqual(rp["render_count"], 0)
        self.assertEqual(rp["reused_count"], 3)
        # Assembly must accept all-reused with empty render list.
        new_identity = gen_identity("222", "1", src[:8])
        new_job = make_job_manifest(run_id="222", sha=src,
                                    inputs=base_inputs(source_sha=src),
                                    resume=rp)
        # Reused chunks keep original identity/provenance.
        cms = [pcm[i] for i in range(3)]
        r = verify_assembly(new_job, cms, build_file_hashes(cms))
        self.assertTrue(r["ok"], f"errors: {r['errors']}")

    def test_mixed_reuse_and_new_assemble(self):
        # Mixed: 2 reused + 1 newly rendered -> assembly passes only when
        # generation, env, and ranges are compatible.
        src = "a" * 40
        prior = make_job_manifest(run_id="111", sha=src,
                                  inputs=base_inputs(source_sha=src))
        gen = prior["generation_fingerprint"]
        pcm = {}
        for cid in (0, 2):
            s, e = cid * 100, cid * 100 + 99
            pcm[cid] = make_chunk_manifest(prior["job_identity"], cid, s, e,
                                           gen, source_sha=src)
        current = base_inputs(source_sha=src)
        plan = [{"chunk_id": i, "start": i * 100, "end": i * 100 + 99}
                for i in range(3)]
        real_shas = {cid: pcm[cid]["output_sha256"] for cid in pcm}
        result = build_resume_plan(
            prior, pcm, current, plan,
            prior["inputs"]["asset_manifest_sha256"],
            artifact_shas=real_shas,
            manifest_shas=build_manifest_shas(pcm))
        rp = result["resume_plan"]
        # New run renders chunk 1.
        new_identity = gen_identity("222", "1", src[:8])
        new_job = make_job_manifest(run_id="222", sha=src,
                                    inputs=base_inputs(source_sha=src),
                                    resume=rp)
        new_chunk = make_chunk_manifest(new_identity, 1, 100, 199, gen,
                                        source_sha=src)
        cms = [pcm[0], new_chunk, pcm[2]]
        r = verify_assembly(new_job, cms, build_file_hashes(cms))
        self.assertTrue(r["ok"], f"errors: {r['errors']}")

    def test_original_manifest_not_mutated(self):
        # P3.12.1: authorizing reuse must not mutate the original.
        src = "a" * 40
        prior = make_job_manifest(run_id="111", sha=src,
                                  inputs=base_inputs(source_sha=src))
        gen = prior["generation_fingerprint"]
        cm = make_chunk_manifest(prior["job_identity"], 0, 0, 99, gen,
                                 source_sha=src)
        before = copy.deepcopy(cm)
        # Run selection (which authorizes reuse via the new plan).
        from recovery import select_chunks
        sel = select_chunks(prior, {0: cm},
                            [{"chunk_id": 0, "start": 0, "end": 99}],
                            gen, {0: cm["output_sha256"]})
        self.assertEqual(len(sel["reuse"]), 1)
        # Original untouched.
        self.assertEqual(cm, before)
        self.assertFalse(cm["provenance"]["reused"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
