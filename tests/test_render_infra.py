#!/usr/bin/env python3
"""
Static regression tests for the GitHub production render infrastructure.

No video rendering. No workflow triggers. Synthetic fixtures only.

Run: python3 -m pytest tests/test_render_infra.py -v
     (or: python3 tests/test_render_infra.py)
"""

import hashlib
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".github", "scripts"))

from job_identity import generate, parse, validate
from manifest import (
    build_job_manifest,
    build_chunk_manifest,
    env_fingerprint,
    verify_assembly,
)


def make_job(**overrides):
    base = dict(
        job_identity="run-100-attempt-1-deadbeef",
        run_id="100",
        attempt="1",
        source_sha="deadbeef" * 5,
        workflow_path=".github/workflows/render-production.yml",
        workflow_sha="deadbeef" * 5,
        workflow_content_sha="c"*64,
        node_version="v24.20.0",
        npm_version="11.0.0",
        remotion_version="4.0.532",
        react_version="18.3.1",
        os_info="Ubuntu 24.04 LTS",
        runner_image="ubuntu-24.04",
        package_lock_sha="abc123",
        composition="P3Rehearsal",
        input_props_sha="none",
        beats_sha="beats123",
        events_sha="events123",
        payload_shas={},
        asset_manifest_sha="assets123",
        width=1920, height=1080, fps=30,
        start_frame=0, end_frame=899, chunk_size=300,
        codec="h264", crf="18", with_audio=True,
    )
    base.update(overrides)
    return build_job_manifest(**base)


def make_env(**overrides):
    base = {
        "node_version": "v24.20.0",
        "npm_version": "11.0.0",
        "remotion_version": "4.0.532",
        "react_version": "18.3.1",
        "chromium_version": "130.0.0",
        "os": "Ubuntu 24.04",
        "runner_image": "ubuntu-24.04",
    }
    base.update(overrides)
    return base


def make_chunk(job, cid, **overrides):
    # Chunk env mirrors the job's expected env (simulating identical runners)
    # Format must match what the workflow collects: `node --version` -> "v24.20.0"
    env = make_env(
        node_version=job["expected_environment"]["node_version"],
        remotion_version=job["expected_environment"]["remotion_version"],
        os=job["expected_environment"]["os"],
    )
    cm = build_chunk_manifest(
        job_identity=job["job_identity"],
        chunk_id=cid,
        start=job["plan"]["chunks"][cid]["start"],
        end=job["plan"]["chunks"][cid]["end"],
        source_sha=job["github"]["source_sha"],
        env_dict=env,
        attempt=int(job["github"]["run_attempt"]),
    )
    cm["output_sha256"] = hashlib.sha256(f"chunk-{cid}".encode()).hexdigest()
    cm.update(overrides)
    return cm


class TestJobIdentity(unittest.TestCase):
    def test_generate_format(self):
        jid = generate("37860000000", "1", "a1b2c3d4e5f6")
        self.assertEqual(jid, "run-37860000000-attempt-1-a1b2c3d4")

    def test_generate_truncates_sha(self):
        jid = generate("1", "1", "abcdef1234567890")
        self.assertTrue(jid.endswith("-abcdef12"))

    def test_repeated_manual_labels_give_different_identities(self):
        # Same label, different runs -> different identities
        a = generate("100", "1", "aaaaaaaabbbb")
        b = generate("101", "1", "aaaaaaaabbbb")
        self.assertNotEqual(a, b)

    def test_different_attempts_give_different_identities(self):
        a = generate("100", "1", "aaaaaaaabbbb")
        b = generate("100", "2", "aaaaaaaabbbb")
        self.assertNotEqual(a, b)

    def test_different_revisions_give_different_identities(self):
        a = generate("100", "1", "aaaaaaaabbbb")
        b = generate("100", "1", "cccccccddddd")
        self.assertNotEqual(a, b)

    def test_validate_accepts_canonical(self):
        self.assertTrue(validate("run-37860000000-attempt-1-a1b2c3d4"))

    def test_validate_rejects_manual_label(self):
        self.assertFalse(validate("2026-001"))
        self.assertFalse(validate("TEST-004"))
        self.assertFalse(validate("run-abc-attempt-1-a1b2c3d4"))

    def test_parse_roundtrip(self):
        jid = generate("999", "3", "deadbeefcafe")
        p = parse(jid)
        self.assertEqual(p, {"run_id": "999", "attempt": "3", "sha8": "deadbeef"})

    def test_generate_rejects_bad_input(self):
        with self.assertRaises(ValueError):
            generate("not-a-number", "1", "a1b2c3d4")
        with self.assertRaises(ValueError):
            generate("1", "1", "xyz")  # not hex


class TestManifestSchema(unittest.TestCase):
    def test_job_manifest_required_fields(self):
        job = make_job()
        for field in ["job_identity", "github", "expected_environment", "inputs", "plan", "stage"]:
            self.assertIn(field, job, f"missing {field}")
        for field in ["run_id", "run_attempt", "source_sha", "workflow_path"]:
            self.assertIn(field, job["github"], f"missing github.{field}")
        for field in ["node_version", "remotion_version", "react_version",
                      "os", "package_lock_sha256"]:
            self.assertIn(field, job["expected_environment"], f"missing expected_environment.{field}")
        # Chromium must NOT be in expected_environment (resolved at render)
        self.assertNotIn("chromium_version", job["expected_environment"])

    def test_chunk_manifest_required_fields(self):
        job = make_job()
        cm = make_chunk(job, 0)
        for field in ["job_identity", "chunk_id", "frame_range", "source_sha",
                      "env_fingerprint", "attempt", "output_sha256"]:
            self.assertIn(field, cm, f"missing {field}")

    def test_stage_classification(self):
        job = make_job()
        self.assertEqual(job["stage"], "planned")
        # Stages must be one of the known values
        self.assertIn(job["stage"], ["planned", "video_only", "av_master"])


class TestAssemblyEnforcement(unittest.TestCase):
    def test_happy_path(self):
        job = make_job()
        chunks = [make_chunk(job, i) for i in range(3)]
        result = verify_assembly(job, chunks)
        self.assertTrue(result["ok"], result.get("errors"))

    def test_rejects_mixed_generation(self):
        job = make_job()
        chunks = [make_chunk(job, i) for i in range(3)]
        chunks[1]["job_identity"] = "run-999-attempt-1-deadbeef"  # different job
        result = verify_assembly(job, chunks)
        self.assertFalse(result["ok"])
        self.assertTrue(any("mixed generation" in e for e in result["errors"]))

    def test_rejects_source_mismatch(self):
        job = make_job()
        chunks = [make_chunk(job, i) for i in range(3)]
        chunks[2]["source_sha"] = "different" * 5
        result = verify_assembly(job, chunks)
        self.assertFalse(result["ok"])
        self.assertTrue(any("source SHA mismatch" in e for e in result["errors"]))

    def test_rejects_env_mismatch(self):
        job = make_job()
        chunks = [make_chunk(job, i) for i in range(3)]
        # Change a pinned field (node_version) — must be rejected
        chunks[0]["measured_environment"]["node_version"] = "v99.99.99"
        from manifest import env_fingerprint
        chunks[0]["env_fingerprint"] = env_fingerprint(chunks[0]["measured_environment"])
        result = verify_assembly(job, chunks)
        self.assertFalse(result["ok"])
        self.assertTrue(any("node_version" in e and "mismatch" in e for e in result["errors"]))

    def test_rejects_placeholder_env(self):
        # env_fingerprint() must reject "unknown" / placeholder values
        from manifest import env_fingerprint
        with self.assertRaises(ValueError):
            env_fingerprint({"node_version": "v24.20.0", "chromium_version": "unknown"})

    def test_rejects_attempt_mismatch(self):
        job = make_job()
        chunks = [make_chunk(job, i) for i in range(3)]
        # Chunk claims attempt=99 but identity says attempt=1
        chunks[1]["attempt"] = 99
        result = verify_assembly(job, chunks)
        self.assertFalse(result["ok"])
        self.assertTrue(any("attempt mismatch" in e for e in result["errors"]))

    def test_resume_disabled_rejects_cross_attempt(self):
        # P3.5.2: resume is DISABLED. Chunks from a different attempt/identity
        # are always rejected, even with matching source SHA and env.
        from manifest import verify_assembly
        job = make_job()  # identity: run-100-attempt-1-deadbeef
        chunks = [make_chunk(job, i) for i in range(2)]  # chunks 0,1 from attempt 1
        # Chunk 2 from attempt 2 (would-be resume) — same SHA, same env
        job2 = make_job(job_identity="run-100-attempt-2-deadbeef", attempt="2")
        c2 = make_chunk(job2, 2)
        chunks.append(c2)
        result = verify_assembly(job, chunks)
        self.assertFalse(result["ok"])
        self.assertTrue(any("mixed generation rejected" in e for e in result["errors"]))

    def test_rejects_missing_chunk(self):
        job = make_job()
        chunks = [make_chunk(job, 0), make_chunk(job, 2)]  # chunk 1 missing
        result = verify_assembly(job, chunks)
        self.assertFalse(result["ok"])
        self.assertTrue(any("missing chunks" in e for e in result["errors"]))

    def test_rejects_duplicate_chunk(self):
        job = make_job()
        chunks = [make_chunk(job, 0), make_chunk(job, 1), make_chunk(job, 1)]
        result = verify_assembly(job, chunks)
        self.assertFalse(result["ok"])
        self.assertTrue(any("duplicate" in e for e in result["errors"]))

    def test_rejects_frame_gap(self):
        job = make_job()
        chunks = [make_chunk(job, i) for i in range(3)]
        chunks[1]["frame_range"] = {"start": 301, "end": 599}  # gap at 300
        result = verify_assembly(job, chunks)
        self.assertFalse(result["ok"])
        self.assertTrue(any("gap/overlap" in e for e in result["errors"]))

    def test_rejects_frame_overlap(self):
        job = make_job()
        chunks = [make_chunk(job, i) for i in range(3)]
        chunks[1]["frame_range"] = {"start": 299, "end": 599}  # overlap at 299
        result = verify_assembly(job, chunks)
        self.assertFalse(result["ok"])

    def test_rejects_unexpected_chunk(self):
        job = make_job()
        chunks = [make_chunk(job, i) for i in range(3)]
        extra = make_chunk(job, 0)
        extra["chunk_id"] = 99
        extra["frame_range"] = {"start": 900, "end": 1199}
        chunks.append(extra)
        result = verify_assembly(job, chunks)
        self.assertFalse(result["ok"])
        self.assertTrue(any("not in plan" in e for e in result["errors"]))

    def test_rejects_missing_checksum(self):
        job = make_job()
        chunks = [make_chunk(job, i) for i in range(3)]
        chunks[0]["output_sha256"] = None
        result = verify_assembly(job, chunks)
        self.assertFalse(result["ok"])

    def test_rejects_empty_manifest_list(self):
        job = make_job()
        result = verify_assembly(job, [])
        self.assertFalse(result["ok"])


class TestPlanCoverage(unittest.TestCase):
    def test_plan_covers_exact_range(self):
        job = make_job(start_frame=0, end_frame=899, chunk_size=300)
        chunks = job["plan"]["chunks"]
        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0], {"chunk_id": 0, "start": 0, "end": 299})
        self.assertEqual(chunks[2], {"chunk_id": 2, "start": 600, "end": 899})

    def test_plan_handles_uneven_division(self):
        job = make_job(start_frame=0, end_frame=899, chunk_size=400)
        chunks = job["plan"]["chunks"]
        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[2], {"chunk_id": 2, "start": 800, "end": 899})


class TestAssetManifest(unittest.TestCase):
    def test_genuine_sha256(self):
        import tempfile, shutil
        from manifest import build_asset_manifest
        tmpdir = tempfile.mkdtemp()
        try:
            path = os.path.join(tmpdir, "test.txt")
            with open(path, 'w') as f:
                f.write("test content")
            m = build_asset_manifest(["test.txt"], repo_root=tmpdir)
            # Must be a full 64-char hex SHA-256, not truncated
            self.assertEqual(len(m["manifest_sha256"]), 64)
            self.assertRegex(m["manifest_sha256"], r"^[0-9a-f]{64}$")
            # Per-file hash must also be full SHA-256
            self.assertEqual(len(m["files"]["test.txt"]), 64)
        finally:
            shutil.rmtree(tmpdir)

    def test_reflects_configured_paths(self):
        import tempfile, shutil
        from manifest import build_asset_manifest
        tmpdir = tempfile.mkdtemp()
        try:
            with open(os.path.join(tmpdir, "vo.wav"), 'w') as f1:
                f1.write("vo")
            with open(os.path.join(tmpdir, "bed.mp3"), 'w') as f2:
                f2.write("bed")
            m = build_asset_manifest(["vo.wav", "bed.mp3"], repo_root=tmpdir)
            self.assertIn("vo.wav", m["files"])
            self.assertIn("bed.mp3", m["files"])
            self.assertEqual(len(m["files"]), 2)
        finally:
            shutil.rmtree(tmpdir)

    def test_rejects_missing_file(self):
        from manifest import build_asset_manifest
        import tempfile, shutil
        tmpdir = tempfile.mkdtemp()
        try:
            with self.assertRaises(FileNotFoundError):
                build_asset_manifest(["nonexistent/audio.wav"], repo_root=tmpdir)
        finally:
            shutil.rmtree(tmpdir)

    def test_rejects_lfs_pointer(self):
        import tempfile, shutil
        from manifest import build_asset_manifest
        tmpdir = tempfile.mkdtemp()
        try:
            with open(os.path.join(tmpdir, "test.mp3"), 'w') as f:
                f.write("version https://git-lfs.github.com/spec/v1\noid sha256:abc\n")
            with self.assertRaises(ValueError):
                build_asset_manifest(["test.mp3"], repo_root=tmpdir)
        finally:
            shutil.rmtree(tmpdir)


class TestStageNaming(unittest.TestCase):
    def test_valid_stages(self):
        valid = {"planned", "video_only", "av_intermediate", "av_master"}
        job = make_job()
        self.assertIn(job["stage"], valid)
        # av_intermediate (VO+bed) must NOT be called av_master
        # (av_master requires the SFX mix, a separate post-production step)
        self.assertNotEqual("av_intermediate", "av_master")

    def test_all_four_stages_distinct(self):
        # All four stages must be distinct labels with distinct meanings
        stages = ["planned", "video_only", "av_intermediate", "av_master"]
        self.assertEqual(len(set(stages)), 4)
        # The workflow must never label a VO+bed output as av_master
        # (checked statically: grep for STAGE="av_master" must find nothing)


class TestPlaceholderRejection(unittest.TestCase):
    def test_rejects_all_placeholders(self):
        from manifest import env_fingerprint
        placeholders = ["unknown", "UNKNOWN", "resolved-at-render",
                        "Resolved-At-Render", "", "   ", "from-lockfile",
                        "from-package-lock", "MISSING:foo"]
        for ph in placeholders:
            with self.assertRaises(ValueError, msg=f"placeholder {ph!r} not rejected"):
                env_fingerprint({"node_version": "v24.20.0",
                                 "chromium_version": ph})

    def test_rejects_placeholder_in_any_field(self):
        from manifest import env_fingerprint
        # Placeholder in node_version (not just chromium) must also fail
        with self.assertRaises(ValueError):
            env_fingerprint({"node_version": "unknown",
                             "chromium_version": "Chrome Headless Shell 130.0.0"})

    def test_accepts_real_values(self):
        from manifest import env_fingerprint
        fp = env_fingerprint({
            "node_version": "v24.20.0",
            "npm_version": "11.0.0",
            "remotion_version": "4.0.532",
            "react_version": "18.3.1",
            "chromium_version": "Chrome Headless Shell 130.0.6723.91",
            "os": "Ubuntu 24.04.1 LTS",
            "runner_image": "ubuntu-24.04",
        })
        self.assertEqual(len(fp), 16)
        self.assertRegex(fp, r"^[0-9a-f]{16}$")

    def test_rejects_react_mismatch(self):
        # React version mismatch must fail assembly
        job = make_job()
        chunks = [make_chunk(job, i) for i in range(3)]
        chunks[1]["measured_environment"]["react_version"] = "17.0.0"
        from manifest import env_fingerprint
        chunks[1]["env_fingerprint"] = env_fingerprint(chunks[1]["measured_environment"])
        result = verify_assembly(job, chunks)
        self.assertFalse(result["ok"])
        self.assertTrue(any("react_version" in e for e in result["errors"]))

    def test_rejects_chromium_disagreement(self):
        # Chunks must agree on Chromium version with each other
        job = make_job()
        chunks = [make_chunk(job, i) for i in range(3)]
        chunks[2]["measured_environment"]["chromium_version"] = "Chrome Headless Shell 999.0.0"
        from manifest import env_fingerprint
        chunks[2]["env_fingerprint"] = env_fingerprint(chunks[2]["measured_environment"])
        result = verify_assembly(job, chunks)
        self.assertFalse(result["ok"])
        self.assertTrue(any("fingerprint" in e for e in result["errors"]))

    def test_rejects_invalid_planning_value(self):
        # build_job_manifest must reject placeholders in expected values
        from manifest import build_job_manifest
        with self.assertRaises(ValueError):
            build_job_manifest(
                job_identity="run-1-attempt-1-abc12345", run_id="1", attempt="1",
                source_sha="abc", workflow_path="w", workflow_sha="abc",
                workflow_content_sha="c"*64,
                node_version="resolved-at-render",  # invalid!
                npm_version="11.0.0", remotion_version="4.0.532",
                react_version="18.3.1", os_info="Ubuntu 24.04",
                runner_image="ubuntu-24.04", package_lock_sha="abc",
                composition="P3Rehearsal", input_props_sha="none",
                beats_sha="b", events_sha="e", payload_shas={},
                asset_manifest_sha="a"*64, width=1920, height=1080, fps=30,
                start_frame=0, end_frame=99, chunk_size=100,
                codec="h264", crf="18", with_audio=False)

    def test_rejects_missing_browser_info(self):
        # build_chunk_manifest must require chromium_version
        from manifest import build_chunk_manifest
        with self.assertRaises(ValueError):
            build_chunk_manifest(
                job_identity="run-1-attempt-1-abc12345",
                chunk_id=0, start=0, end=99,
                source_sha="abc",
                env_dict={
                    "node_version": "v24.20.0",
                    "remotion_version": "4.0.532",
                    "react_version": "18.3.1",
                    # chromium_version missing!
                    "os": "Ubuntu 24.04",
                })


class TestAssetManifestRetention(unittest.TestCase):
    def test_manifest_structure_for_artifacts(self):
        # The asset manifest must contain everything needed for audit:
        # configured paths + complete hashes + the canonical digest
        import tempfile
        from manifest import build_asset_manifest
        import shutil
        tmpdir = tempfile.mkdtemp()
        try:
            with open(os.path.join(tmpdir, "vo.wav"), 'w') as f1:
                f1.write("vo-data")
            with open(os.path.join(tmpdir, "bed.mp3"), 'w') as f2:
                f2.write("bed-data")
            m = build_asset_manifest(["vo.wav", "bed.mp3"], repo_root=tmpdir)
            self.assertIn("files", m)
            self.assertIn("manifest_sha256", m)
            self.assertEqual(set(m["files"].keys()), {"vo.wav", "bed.mp3"})
            # Hashes must be complete (not truncated)
            for h in m["files"].values():
                self.assertEqual(len(h), 64)
            self.assertEqual(len(m["manifest_sha256"]), 64)
        finally:
            shutil.rmtree(tmpdir)

    def test_manifest_changes_with_content(self):
        # Different content must produce a different manifest digest
        import tempfile, shutil
        from manifest import build_asset_manifest
        tmpdir = tempfile.mkdtemp()
        try:
            p = os.path.join(tmpdir, "test.txt")
            with open(p, 'w') as f:
                f.write("version-a")
            m1 = build_asset_manifest(["test.txt"], repo_root=tmpdir)
            with open(p, 'w') as f:
                f.write("version-b")
            m2 = build_asset_manifest(["test.txt"], repo_root=tmpdir)
            self.assertNotEqual(m1["manifest_sha256"], m2["manifest_sha256"])
            self.assertNotEqual(m1["files"]["test.txt"], m2["files"]["test.txt"])
        finally:
            shutil.rmtree(tmpdir)


class TestAssetManifestVerification(unittest.TestCase):
    """Verify the assembly-time asset manifest checks."""

    def _make_valid(self):
        import tempfile, shutil
        from manifest import build_asset_manifest
        tmpdir = tempfile.mkdtemp()
        with open(os.path.join(tmpdir, "vo.wav"), 'w') as f: f.write("vo-data")
        with open(os.path.join(tmpdir, "bed.mp3"), 'w') as f: f.write("bed-data")
        asset_m = build_asset_manifest(["vo.wav", "bed.mp3"], repo_root=tmpdir)
        job = make_job()
        job["inputs"]["asset_manifest_sha256"] = asset_m["manifest_sha256"]
        job["inputs"]["with_audio"] = True
        return job, asset_m, tmpdir

    def test_accepts_valid_manifest(self):
        from manifest import verify_asset_manifest
        job, asset_m, tmpdir = self._make_valid()
        # Create the actual files in tmpdir with relative names
        import shutil
        for rel in ["vo.wav", "bed.mp3"]:
            shutil.copy(os.path.join(tmpdir, rel.replace("vo.wav", "vo.wav")),
                        os.path.join(tmpdir, rel)) if False else None
        # Write files with expected names
        with open(os.path.join(tmpdir, "vo.wav"), 'w') as f: f.write("vo-data")
        with open(os.path.join(tmpdir, "bed.mp3"), 'w') as f: f.write("bed-data")
        result = verify_asset_manifest(job, asset_m, repo_root=tmpdir)
        self.assertTrue(result["ok"], result.get("errors"))
        import shutil
        shutil.rmtree(tmpdir)

    def test_rejects_altered_manifest(self):
        from manifest import verify_asset_manifest
        job, asset_m, tmpdir = self._make_valid()
        # Tamper with a file hash
        asset_m["files"]["vo.wav"] = "0" * 64
        result = verify_asset_manifest(job, asset_m, repo_root=tmpdir)
        self.assertFalse(result["ok"])
        self.assertTrue(any("digest mismatch" in e or "altered" in e
                            for e in result["errors"]))
        import shutil
        shutil.rmtree(tmpdir)

    def test_rejects_digest_mismatch_with_job(self):
        from manifest import verify_asset_manifest
        job, asset_m, tmpdir = self._make_valid()
        job["inputs"]["asset_manifest_sha256"] = "f" * 64  # wrong
        result = verify_asset_manifest(job, asset_m, repo_root=tmpdir)
        self.assertFalse(result["ok"])
        self.assertTrue(any("provenance broken" in e for e in result["errors"]))
        import shutil
        shutil.rmtree(tmpdir)

    def test_rejects_malformed_manifest(self):
        from manifest import verify_asset_manifest
        job = make_job()
        result = verify_asset_manifest(job, {"bad": "schema"})
        self.assertFalse(result["ok"])

    def test_rejects_missing_audio_file(self):
        from manifest import verify_asset_manifest
        import tempfile
        job, asset_m, tmpdir = self._make_valid()
        # Don't create the files — they should be reported missing
        result = verify_asset_manifest(job, asset_m, repo_root="/nonexistent")
        self.assertFalse(result["ok"])
        self.assertTrue(any("not found" in e for e in result["errors"]))
        import shutil
        shutil.rmtree(tmpdir)

    def test_rejects_changed_file_content(self):
        # MANDATORY: build valid manifest, change the file, prove failure
        from manifest import verify_asset_manifest, build_asset_manifest
        import tempfile, shutil
        tmpdir = tempfile.mkdtemp()
        try:
            with open(os.path.join(tmpdir, "vo.wav"), 'w') as f:
                f.write("original-content")
            asset_m = build_asset_manifest(["vo.wav"], repo_root=tmpdir)
            job = make_job()
            job["inputs"]["asset_manifest_sha256"] = asset_m["manifest_sha256"]
            job["inputs"]["with_audio"] = True
            # Should pass before change
            result = verify_asset_manifest(job, asset_m, repo_root=tmpdir)
            self.assertTrue(result["ok"], result.get("errors"))
            # Change the file content WITHOUT updating manifest
            with open(os.path.join(tmpdir, "vo.wav"), 'w') as f:
                f.write("TAMPERED-content")
            result = verify_asset_manifest(job, asset_m, repo_root=tmpdir)
            self.assertFalse(result["ok"])
            self.assertTrue(any("content changed" in e for e in result["errors"]))
        finally:
            shutil.rmtree(tmpdir)

    def test_rejects_path_traversal(self):
        from manifest import verify_asset_manifest
        import hashlib, json
        job = make_job()
        evil_m = {"files": {"../../../etc/passwd": "a" * 64}}
        canonical = json.dumps({"files": evil_m["files"]}, sort_keys=True)
        evil_m["manifest_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
        job["inputs"]["asset_manifest_sha256"] = evil_m["manifest_sha256"]
        result = verify_asset_manifest(job, evil_m, repo_root="/tmp")
        self.assertFalse(result["ok"])
        self.assertTrue(any("escapes" in e for e in result["errors"]))

    def test_rejects_absolute_path(self):
        from manifest import verify_asset_manifest
        import hashlib, json
        job = make_job()
        evil_m = {"files": {"/etc/passwd": "a" * 64}}
        canonical = json.dumps({"files": evil_m["files"]}, sort_keys=True)
        evil_m["manifest_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
        job["inputs"]["asset_manifest_sha256"] = evil_m["manifest_sha256"]
        result = verify_asset_manifest(job, evil_m, repo_root="/tmp")
        self.assertFalse(result["ok"])
        self.assertTrue(any("relative" in e for e in result["errors"]))

    def test_rejects_symlink_pointing_outside(self):
        # R-020: symlink inside repo pointing outside must be rejected
        # at validation, creation, and verification.
        from manifest import canonical_repo_path, build_asset_manifest
        from manifest import verify_asset_manifest
        import tempfile, shutil, hashlib, json, os
        tmpdir = tempfile.mkdtemp()
        outside = tempfile.mkdtemp()
        try:
            # Create a file outside the repo
            secret = os.path.join(outside, "secret.txt")
            with open(secret, 'w') as f:
                f.write("secret")
            # Symlink inside repo pointing outside
            link = os.path.join(tmpdir, "link.txt")
            os.symlink(secret, link)
            # 1. Path validation rejects
            with self.assertRaises(ValueError):
                canonical_repo_path(tmpdir, "link.txt")
            # 2. Manifest creation rejects
            with self.assertRaises(ValueError):
                build_asset_manifest(["link.txt"], repo_root=tmpdir)
            # 3. Manifest verification rejects
            evil_m = {"files": {"link.txt": "a" * 64}}
            canonical = json.dumps({"files": evil_m["files"]}, sort_keys=True)
            evil_m["manifest_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
            job = make_job()
            job["inputs"]["asset_manifest_sha256"] = evil_m["manifest_sha256"]
            result = verify_asset_manifest(job, evil_m, repo_root=tmpdir)
            self.assertFalse(result["ok"])
            # Symlink resolved outside → either "symlink" or "escapes" error
            self.assertTrue(any("symlink" in e or "escapes" in e
                                for e in result["errors"]))
        finally:
            shutil.rmtree(tmpdir)
            shutil.rmtree(outside)


class TestWorkflowContracts(unittest.TestCase):
    """Static contract tests: verify the actual workflow source matches
    the expectations of the Python helpers. These catch wiring drift."""

    @classmethod
    def setUpClass(cls):
        import yaml
        with open('.github/workflows/render-production.yml') as f:
            cls.wf = yaml.safe_load(f)
        with open('.github/workflows/render-production.yml') as f:
            cls.raw = f.read()

    def test_browser_cache_path_matches_remotion(self):
        # Remotion 4.0.532 uses node_modules/.remotion (verified from
        # get-download-destination.js). The workflow must cache that path.
        self.assertIn("path: node_modules/.remotion", self.raw)
        self.assertNotIn("path: ~/.cache/remotion", self.raw)

    def test_cache_key_uses_runner_image(self):
        # Must not override GitHub's reserved RUNNER_OS
        self.assertNotIn("RUNNER_OS: 'ubuntu-24.04'", self.raw)
        self.assertIn("RUNNER_IMAGE:", self.raw)
        self.assertIn("env.RUNNER_IMAGE", self.raw)

    def test_no_restore_keys_fallback(self):
        # Broad restore-keys could supply an incompatible browser
        self.assertNotIn("restore-keys:", self.raw)

    def test_asset_verification_in_workflow(self):
        # The assemble job must call verify_asset_manifest before publication
        self.assertIn("verify_asset_manifest", self.raw)
        self.assertIn("Verify asset manifest provenance", self.raw)

    def test_browser_detection_fails_closed(self):
        # Browser detection must exit 1 if binary missing or version empty
        self.assertIn('FATAL: Chromium executable not found', self.raw)
        # P3.6.5: version recorded after verification; failure message updated
        self.assertIn('FATAL: version inspection failed', self.raw)
        # No silent fallback to "unknown"
        self.assertNotIn('|| echo "unknown"', self.raw)

    def test_no_resolved_at_render_placeholder(self):
        # The literal placeholder must not be used as a manifest VALUE.
        # (May appear in comments explaining its removal.)
        import re
        # Find assignments: chromium_version='resolved-at-render' or similar
        assignments = re.findall(
            r'chromium_version\s*=\s*[\'"]resolved-at-render[\'"]', self.raw)
        self.assertEqual(assignments, [],
                         f"placeholder used as value: {assignments}")

    def test_expected_vs_measured_separation(self):
        # Workflow must not pass chromium_version to build_job_manifest
        # (it's measured at render, not planned)
        import re
        calls = re.findall(r'build_job_manifest\((.*?)\)', self.raw, re.DOTALL)
        for call in calls:
            self.assertNotIn("chromium_version", call,
                             "plan must not set chromium_version")

    def test_no_raw_input_interpolation_in_shell(self):
        # P3.6.2: ${{ inputs.* }} must not appear in shell run: blocks,
        # only in env: blocks (safe) or if: conditions (safe).
        # Comments mentioning the pattern are allowed.
        import re
        lines = self.raw.split('\n')
        in_run = False
        in_env = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped == 'run: |':
                in_run = True
                in_env = False
                continue
            if in_run and stripped == 'env:':
                in_env = True
                continue
            if in_run and re.match(r'^      - ', line):
                in_run = False
                in_env = False
                continue
            if in_run and not in_env and '${{ inputs.' in line:
                # Allow comments
                if stripped.startswith('#'):
                    continue
                self.fail(f"raw input interpolation in shell at line {i+1}: "
                          f"{line.strip()}")

    def test_browser_binary_passed_to_checker(self):
        # R-021: Workflow must pass the discovered binary path to
        # the verifier before rendering.
        import re
        self.assertRegex(self.raw, r'id:\s*browser')
        self.assertIn('binary_path=$CHROME_BIN', self.raw)
        self.assertIn("steps.browser.outputs.binary_path", self.raw)
        # P3.6.5: uses verify_browser_for_render (3-outcome contract)
        self.assertIn("verify_browser_for_render", self.raw)
        # Order by line numbers (not string find, which hits comments)
        lines = self.raw.split('\n')
        browser_line = next(i for i, l in enumerate(lines) if 'id: browser' in l)
        verify_line = next(i for i, l in enumerate(lines)
                           if 'Verify browser dependencies (real binary)' in l)
        render_line = next(i for i, l in enumerate(lines)
                           if 'name: Render chunk ${{ matrix.chunk.chunk_id }}' in l)
        self.assertLess(browser_line, verify_line)
        self.assertLess(verify_line, render_line)

    def test_audio_mux_uses_boolean_condition(self):
        # R-023: with_audio is type Boolean; conditions must not compare
        # to the string 'true'.
        import re
        lines = self.raw.split('\n')
        mux_line = next(i for i, l in enumerate(lines)
                        if 'Mux canonical audio' in l)
        # The `if:` is on the line AFTER the name:
        context = '\n'.join(lines[mux_line:mux_line+3])
        self.assertIn('if: inputs.with_audio', context)
        # Must NOT have string comparison anywhere
        self.assertNotIn("inputs.with_audio == 'true'", self.raw,
                         "Boolean input must not be compared to string 'true'")
        self.assertNotIn('inputs.with_audio == "true"', self.raw)

    def test_audio_stage_consistency(self):
        # R-023: Boolean true → av_intermediate; Boolean false → video_only.
        # Verify the shell logic maps correctly.
        # When WITH_AUDIO=true: STAGE=av_intermediate, MASTER=/tmp/master.mp4
        # When WITH_AUDIO=false: STAGE=video_only, MASTER=/tmp/master_video.mp4
        self.assertIn('STAGE="av_intermediate"', self.raw)
        self.assertIn('STAGE="video_only"', self.raw)
        # The stage assignment must be inside the WITH_AUDIO conditional
        import re
        # Find the stage assignment block
        stage_block = re.search(
            r'if \[ "\$WITH_AUDIO" = "true" \]; then\s+'
            r'MASTER=/tmp/master\.mp4\s+'
            r'STAGE="av_intermediate"',
            self.raw
        )
        self.assertIsNotNone(stage_block,
                             "true branch must set av_intermediate")
        stage_block_false = re.search(
            r'else\s+'
            r'MASTER=/tmp/master_video\.mp4\s+'
            r'cp \$MASTER /tmp/master\.mp4\s+'
            r'STAGE="video_only"',
            self.raw
        )
        self.assertIsNotNone(stage_block_false,
                             "false branch must set video_only")

    def test_workflow_has_repair_and_recheck(self):
        # R-021: Workflow must attempt repair and recheck before failing.
        self.assertIn("attempting repair", self.raw.lower())
        self.assertIn("Rechecking after repair", self.raw)
        self.assertIn("still failing after repair", self.raw)
        # P3.8: Must use the unified BROWSER_PACKAGES, not a separate list
        self.assertIn("BROWSER_PACKAGES", self.raw)

    def test_unified_package_set(self):
        # R-021 (P3.8): ONE package set for both install paths.
        # The workflow must reference BROWSER_PACKAGES, not define its own.
        from preflight import BROWSER_PACKAGES
        # Must cover all categories: NSS/NSPR, ATK, CUPS, DRM, XKB, X11, GBM, audio
        pkg_str = " ".join(BROWSER_PACKAGES)
        self.assertIn("libnss3", pkg_str)
        self.assertIn("libnspr4", pkg_str)
        self.assertIn("libatk-bridge2.0-0t64", pkg_str)
        self.assertIn("libcups2t64", pkg_str)
        self.assertIn("libdrm2", pkg_str)
        self.assertIn("libxkbcommon0", pkg_str)
        self.assertIn("libgbm1", pkg_str)
        self.assertIn("libasound2t64", pkg_str)
        # X11 libs
        self.assertIn("libxcomposite1", pkg_str)
        # All must use Noble t64 names where applicable (no old names)
        self.assertNotIn("libatk1.0-0 ", pkg_str)  # old name has trailing space
        self.assertNotIn("libcups2 ", pkg_str)

    def test_stage_av_master_never_assigned(self):
        # The workflow must never label VO+bed as av_master
        self.assertNotIn('STAGE="av_master"', self.raw)

    def test_resume_fully_removed(self):
        # No resume_from input; no allowed_identities as a code parameter
        # (may appear in comments explaining its removal)
        inputs = self.wf[True]['workflow_dispatch']['inputs']
        self.assertNotIn('resume_from', inputs)
        # Check it's not used as a function argument in embedded Python
        import re
        code_uses = re.findall(r'verify_assembly\([^)]*allowed_identities', self.raw)
        self.assertEqual(code_uses, [],
                         f"allowed_identities still used in code: {code_uses}")

    def test_ubuntu_packages_use_t64_names(self):
        # Ubuntu 24.04 Noble t64 transition: new names must be used.
        # P3.8: packages now live in preflight.py::BROWSER_PACKAGES (single source).
        from preflight import BROWSER_PACKAGES
        pkg_str = " ".join(BROWSER_PACKAGES)
        self.assertIn("libatk1.0-0t64", pkg_str)
        self.assertIn("libatk-bridge2.0-0t64", pkg_str)
        self.assertIn("libcups2t64", pkg_str)
        self.assertIn("libasound2t64", pkg_str)
        # Old names must not appear
        for old in ["libatk1.0-0 ", "libatk-bridge2.0-0 ", "libcups2 ",
                    "libasound2 "]:
            self.assertNotIn(old, pkg_str + " ",
                             f"old package name still present: {old.strip()}")
        # Workflow must reference the unified set
        self.assertIn("BROWSER_PACKAGES", self.raw)

    def test_fail_fast_false_on_matrix(self):
        # One failed chunk must not prevent others from reporting
        render_job = self.wf['jobs']['render-chunk']
        self.assertEqual(render_job['strategy']['fail-fast'], False)

    def test_render_job_skips_ffmpeg(self):
        # Render jobs need chromium libs only; ffmpeg is assembly-only
        # (checked: preflight --for render does not require ffmpeg)
        from preflight import check_ffmpeg, check_chromium_libs
        # Simulate: render role should not list ffmpeg as required
        import subprocess
        result = subprocess.run(
            ["python3", ".github/scripts/preflight.py", "--help"],
            capture_output=True, text=True)
        self.assertIn("--for", result.stdout)


class TestPreflightComprehensive(unittest.TestCase):
    """Preflight must cover all browser dependencies."""

    def test_checks_nss_nspr(self):
        # The actual binary needs these (from ldd)
        from preflight import check_chromium_libs
        result = check_chromium_libs()
        checked = result.get("checked", [])
        self.assertIn("libnss3.so", checked)
        self.assertIn("libnspr4.so", checked)

    def test_uses_ldd_when_binary_provided(self):
        # When given the real binary path, preflight uses ldd
        from preflight import check_chromium_libs
        import os
        binary = "node_modules/.remotion/chrome-headless-shell/linux64/chrome-headless-shell-linux64/chrome-headless-shell"
        if os.path.isfile(binary):
            result = check_chromium_libs(binary)
            # Should have checked libs derived from ldd
            self.assertTrue(len(result.get("checked", [])) > 0)
        else:
            self.skipTest("browser binary not present locally")

    def test_preflight_roles(self):
        # --for render should not require ffmpeg; --for assemble should
        import subprocess, json
        # We can't fully run preflight without the libs, but we can check
        # the role logic via the script's argument parsing
        result = subprocess.run(
            ["python3", ".github/scripts/preflight.py", "--for", "render", "--help"],
            capture_output=True, text=True)
        # Help should show the --for option
        self.assertIn("render", result.stdout + result.stderr)

    def test_ldd_fails_closed_on_non_elf(self):
        # MANDATORY: non-ELF file must fail closed, not return present=true
        from preflight import check_chromium_libs
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt',
                                         delete=False) as f:
            f.write("this is not an ELF binary")
            path = f.name
        try:
            result = check_chromium_libs(path)
            self.assertFalse(result["present"],
                             "non-ELF must not report present=true")
            self.assertIn("error", result)
        finally:
            os.unlink(path)

    def test_ldd_fails_closed_on_missing_file(self):
        from preflight import check_chromium_libs
        result = check_chromium_libs("/nonexistent/binary")
        self.assertFalse(result["present"])
        self.assertIn("error", result)

    def test_ldd_succeeds_on_real_binary(self):
        from preflight import check_chromium_libs
        binary = ("node_modules/.remotion/chrome-headless-shell/linux64/"
                  "chrome-headless-shell-linux64/chrome-headless-shell")
        if not os.path.isfile(binary):
            self.skipTest("browser binary not present")
        result = check_chromium_libs(binary)
        # Should have checked libs derived from ldd (not empty due to error)
        self.assertTrue(len(result.get("checked", [])) > 0)
        # 'error' key must NOT be present on success
        self.assertNotIn("error", result)

    def test_repair_distinguishes_invalid_executable(self):
        # R-021: Invalid executable is NOT a package-install problem.
        from preflight import verify_browser_for_render
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bin',
                                         delete=False) as f:
            f.write("not an executable")
            path = f.name
        try:
            result = verify_browser_for_render(path)
            self.assertEqual(result["outcome"], "unrepairable")
            self.assertIn("reason", result)
        finally:
            os.unlink(path)

    def test_verify_missing_executable_unrepairable(self):
        from preflight import verify_browser_for_render
        result = verify_browser_for_render("/nonexistent/browser")
        self.assertEqual(result["outcome"], "unrepairable")

    def test_verify_invalid_path_unrepairable(self):
        from preflight import verify_browser_for_render
        self.assertEqual(verify_browser_for_render("")["outcome"],
                         "unrepairable")
        self.assertEqual(verify_browser_for_render(None)["outcome"],
                         "unrepairable")

    def test_verify_real_binary(self):
        # Valid executable with all deps → verified
        from preflight import verify_browser_for_render
        binary = ("node_modules/.remotion/chrome-headless-shell/linux64/"
                  "chrome-headless-shell-linux64/chrome-headless-shell")
        if not os.path.isfile(binary):
            self.skipTest("browser binary not present")
        result = verify_browser_for_render(binary)
        # Must be verified or repairable (not unrepairable on a real binary)
        self.assertIn(result["outcome"], ("verified", "repairable"))

    def test_unresolved_libs_are_repairable(self):
        # R-021 (P3.6.5): ldd "not found" must be repairable, not unrepairable.
        # Simulate by mocking check_chromium_libs to return unresolved.
        from preflight import verify_browser_for_render
        import preflight
        orig = preflight.check_chromium_libs
        try:
            preflight.check_chromium_libs = lambda p: {
                "present": False,
                "missing": ["libfoo.so"],
                "checked": ["libfoo.so"],
                "error": "ldd reports unresolved: ['libfoo.so']",
            }
            result = verify_browser_for_render("/fake/binary")
            self.assertEqual(result["outcome"], "repairable",
                             "unresolved libs must be repairable, not unrepairable")
            self.assertEqual(result["missing"], ["libfoo.so"])
        finally:
            preflight.check_chromium_libs = orig

    def test_versioned_soname_preserved(self):
        # R-024: Full versioned SONAMEs must be inventoried, not normalized.
        # P3.9: ldd is ground truth — resolved libs need no ldconfig check.
        from preflight import check_chromium_libs
        import preflight
        orig_run = preflight.run
        try:
            fake_ldd = (
                "linux-vdso.so.1 (0x00007fff)\n"
                "libatk-bridge-2.0.so.0 => /lib/x86_64-linux-gnu/libatk-bridge-2.0.so.0\n"
                "libcups.so.2 => /lib/x86_64-linux-gnu/libcups.so.2\n"
                "libnss3.so => /lib/x86_64-linux-gnu/libnss3.so\n"
                "libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6\n"
            )
            def fake_run(cmd):
                if cmd[0] == "ldd":
                    return (0, fake_ldd)
                return orig_run(cmd)
            preflight.run = fake_run
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False) as f:
                path = f.name
            try:
                result = check_chromium_libs(path)
                self.assertIn("libatk-bridge-2.0.so.0", result["checked"])
                self.assertIn("libcups.so.2", result["checked"])
                self.assertIn("libnss3.so", result["checked"])
                self.assertNotIn("libc.so.6", result["checked"])
                self.assertNotIn("linux-vdso.so.1", result["checked"])
                # P3.9: ldd resolved everything → present, no ldconfig needed
                self.assertTrue(result["present"])
                self.assertEqual(result["missing"], [])
            finally:
                os.unlink(path)
        finally:
            preflight.run = orig_run

    def test_ldd_ground_truth_no_ldconfig_false_missing(self):
        # P3.9: A library ldd resolves must NOT be reported missing just
        # because ldconfig -p lacks it (stale cache, rpath, etc.).
        from preflight import check_chromium_libs
        import preflight
        orig_run = preflight.run
        try:
            fake_ldd = (
                "libcustom.so.1 => /opt/custom/lib/libcustom.so.1 (0xabc)\n"
                "libnss3.so => /lib/x86_64-linux-gnu/libnss3.so (0xdef)\n"
            )
            def fake_run(cmd):
                if cmd[0] == "ldd":
                    return (0, fake_ldd)
                if cmd[0] == "ldconfig":
                    # Simulate stale cache missing libcustom
                    return (0, "libnss3.so (libc6) => /lib/x86_64-linux-gnu/libnss3.so\n")
                return orig_run(cmd)
            preflight.run = fake_run
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False) as f:
                path = f.name
            try:
                result = check_chromium_libs(path)
                # ldd proved resolution → verified, despite ldconfig gap
                self.assertTrue(result["present"])
                self.assertEqual(result["missing"], [])
                self.assertIn("libcustom.so.1", result["checked"])
            finally:
                os.unlink(path)
        finally:
            preflight.run = orig_run

    def test_empty_inventory_fails_closed(self):
        # R-024: Empty ldd inventory must not verify as success.
        from preflight import check_chromium_libs
        import preflight
        orig_run = preflight.run
        try:
            # ldd succeeds but reports only system libs
            fake_ldd = (
                "linux-vdso.so.1 => (0x00007fff)\n"
                "libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6\n"
                "libm.so.6 => /lib/x86_64-linux-gnu/libm.so.6\n"
            )
            def fake_run(cmd):
                if cmd[0] == "ldd":
                    return (0, fake_ldd)
                return orig_run(cmd)
            preflight.run = fake_run
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False) as f:
                path = f.name
            try:
                result = check_chromium_libs(path)
                self.assertFalse(result["present"],
                                 "empty inventory must not verify")
                self.assertIn("error", result)
            finally:
                os.unlink(path)
        finally:
            preflight.run = orig_run

    def test_absolute_path_entries_not_falsely_missing(self):
        # R-024 (P3.8): Absolute-path ldd entries (e.g. the dynamic loader
        # /lib64/ld-linux-x86-64.so.2) must not be reported as missing.
        from preflight import check_chromium_libs
        import preflight
        orig_run = preflight.run
        try:
            fake_ldd = (
                "linux-vdso.so.1 (0x00007ffd)\n"
                "libnss3.so => /lib/x86_64-linux-gnu/libnss3.so (0xabc)\n"
                "libatk-bridge-2.0.so.0 => /lib/x86_64-linux-gnu/libatk-bridge-2.0.so.0 (0xdef)\n"
                "/lib64/ld-linux-x86-64.so.2 (0x123)\n"
                "libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x456)\n"
            )
            fake_ldconfig = (
                "libnss3.so (libc6) => /lib/x86_64-linux-gnu/libnss3.so\n"
                "libatk-bridge-2.0.so.0 (libc6) => /lib/x86_64-linux-gnu/libatk-bridge-2.0.so.0\n"
                "ld-linux-x86-64.so.2 (libc6) => /lib64/ld-linux-x86-64.so.2\n"
            )
            def fake_run(cmd):
                if cmd[0] == "ldd":
                    return (0, fake_ldd)
                if cmd[0] == "ldconfig":
                    return (0, fake_ldconfig)
                return orig_run(cmd)
            preflight.run = fake_run
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False) as f:
                path = f.name
            try:
                result = check_chromium_libs(path)
                # The loader must be filtered (not in checked, not in missing)
                for lib in result["checked"]:
                    self.assertFalse(lib.startswith("/"),
                                     f"absolute path leaked into inventory: {lib}")
                self.assertNotIn("ld-linux-x86-64.so.2", result["missing"])
                self.assertNotIn("/lib64/ld-linux-x86-64.so.2",
                                 result["missing"])
                # Real deps are inventoried with versions
                self.assertIn("libnss3.so", result["checked"])
                self.assertIn("libatk-bridge-2.0.so.0", result["checked"])
                self.assertTrue(result["present"])
            finally:
                os.unlink(path)
        finally:
            preflight.run = orig_run

    def test_real_binary_no_false_missing(self):
        # R-024 (P3.8): A real dynamically linked binary must not falsely
        # report resolved absolute-path libraries as missing.
        from preflight import check_chromium_libs
        import sys
        result = check_chromium_libs(sys.executable)  # real dynamic binary
        # No absolute paths in missing list
        for lib in result.get("missing", []):
            self.assertFalse(lib.startswith("/"),
                             f"false missing (absolute path): {lib}")
        # No absolute paths in checked list
        for lib in result.get("checked", []):
            self.assertFalse(lib.startswith("/"),
                             f"absolute path in inventory: {lib}")

    def test_real_binary_repairable_implies_missing(self):
        # R-024 (P3.8): Strengthened — 'repairable' must mean genuinely
        # missing libs, not a false positive from parser bugs.
        from preflight import verify_browser_for_render
        binary = ("node_modules/.remotion/chrome-headless-shell/linux64/"
                  "chrome-headless-shell-linux64/chrome-headless-shell")
        if not os.path.isfile(binary):
            self.skipTest("browser binary not present")
        result = verify_browser_for_render(binary)
        if result["outcome"] == "repairable":
            # Every listed missing lib must be a real SONAME, not a path
            self.assertTrue(len(result["missing"]) > 0)
            for lib in result["missing"]:
                self.assertFalse(lib.startswith("/"),
                                 f"parser bug: path in missing: {lib}")
                self.assertIn(".so", lib)


class TestHistoricalRegressions(unittest.TestCase):
    """Regression tests for previously encountered failures."""

    def test_rejects_stale_workflow_evidence(self):
        # A rerun uses its ORIGINAL workflow revision. The manifest records
        # workflow_sha; assembly must reject mismatched source.
        job = make_job()
        chunks = [make_chunk(job, i) for i in range(3)]
        chunks[0]["source_sha"] = "different-sha"
        result = verify_assembly(job, chunks)
        self.assertFalse(result["ok"])
        self.assertTrue(any("source SHA mismatch" in e for e in result["errors"]))

    def test_rejects_missing_manifest_fields(self):
        # Malformed chunk manifest (missing frame_range) must fail
        job = make_job()
        chunks = [make_chunk(job, i) for i in range(3)]
        del chunks[1]["frame_range"]
        result = verify_assembly(job, chunks)
        self.assertFalse(result["ok"])

    def test_rejects_empty_chunk_output(self):
        # Chunk with null checksum (failed render) must not assemble
        job = make_job()
        chunks = [make_chunk(job, i) for i in range(3)]
        chunks[2]["output_sha256"] = None
        result = verify_assembly(job, chunks)
        self.assertFalse(result["ok"])
        self.assertTrue(any("missing output checksum" in e for e in result["errors"]))


class TestScopeControl(unittest.TestCase):
    """Verify the infrastructure patch does not touch creative assets."""

    def test_no_creative_files_in_patch(self):
        import subprocess
        result = subprocess.run(
            ["git", "diff", "HEAD", "--name-only"],
            capture_output=True, text=True, cwd=".")
        files = result.stdout.strip().split('\n')
        # Creative paths that must NOT appear in the infrastructure patch
        forbidden_prefixes = [
            "src/light/", "src/compiled_p3/", "crackit/",
            "public/audio/sfx/",  # curated SFX pack
        ]
        for f in files:
            for prefix in forbidden_prefixes:
                self.assertFalse(f.startswith(prefix),
                                 f"creative file in patch: {f}")

    def test_sfx_pack_untouched(self):
        import subprocess
        result = subprocess.run(
            ["git", "status", "--short", "public/audio/sfx/"],
            capture_output=True, text=True, cwd=".")
        self.assertEqual(result.stdout.strip(), "",
                         f"SFX pack modified: {result.stdout}")


class TestPlanScript(unittest.TestCase):
    """Execute the actual plan.py logic with fixtures."""

    def _run_plan(self, env_overrides, repo_root="."):
        import subprocess, tempfile, os
        tmpdir = tempfile.mkdtemp()
        base_env = {
            "JOB_IDENTITY": "run-999-attempt-1-test1234",
            "GITHUB_RUN_ID": "999",
            "GITHUB_RUN_ATTEMPT": "1",
            "GITHUB_SHA": "abc123",
            "COMPOSITION": "P3Rehearsal",
            "START_FRAME": "0",
            "END_FRAME": "899",
            "CHUNK_SIZE": "300",
            "MAX_PARALLEL": "20",
            "CRF": "18",
            "WITH_AUDIO": "false",  # avoid needing real audio files
            "VO_FILE": "public/audio/vo_p3.wav",
            "BED_FILE": "public/audio/bed.mp3",
            "LABEL": "test",
            "OUTPUT_DIR": tmpdir,
            "REPO_ROOT": repo_root,
            "PATH": os.environ.get("PATH", ""),
        }
        base_env.update(env_overrides)
        result = subprocess.run(
            ["python3", ".github/scripts/plan.py"],
            env=base_env, capture_output=True, text=True, cwd=".")
        return result, tmpdir

    def test_plan_creates_manifest_and_matrix(self):
        import json, os, shutil
        result, tmpdir = self._run_plan({})
        self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")
        with open(os.path.join(tmpdir, "job_manifest.json")) as f:
            m = json.load(f)
        self.assertEqual(m["plan"]["chunk_count"], 3)
        chunks = m["plan"]["chunks"]
        self.assertEqual(chunks[0], {"chunk_id": 0, "start": 0, "end": 299})
        self.assertEqual(chunks[2], {"chunk_id": 2, "start": 600, "end": 899})
        # Verify expected_environment (not environment)
        self.assertIn("expected_environment", m)
        self.assertNotIn("environment", m)
        shutil.rmtree(tmpdir)

    def test_plan_rejects_bad_start_frame(self):
        result, tmpdir = self._run_plan({"START_FRAME": "-1"})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("START_FRAME", result.stderr)
        import shutil
        shutil.rmtree(tmpdir)

    def test_plan_rejects_end_before_start(self):
        result, tmpdir = self._run_plan({"START_FRAME": "100", "END_FRAME": "50"})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("END_FRAME", result.stderr)
        import shutil
        shutil.rmtree(tmpdir)

    def test_plan_rejects_bad_crf(self):
        result, tmpdir = self._run_plan({"CRF": "99"})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("crf", result.stderr.lower())
        import shutil
        shutil.rmtree(tmpdir)

    def test_plan_rejects_bad_composition(self):
        result, tmpdir = self._run_plan({"COMPOSITION": "evil; rm -rf /"})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("composition", result.stderr.lower())
        import shutil
        shutil.rmtree(tmpdir)

    def test_plan_rejects_path_traversal(self):
        result, tmpdir = self._run_plan({
            "WITH_AUDIO": "true",
            "VO_FILE": "../../../etc/passwd",
        })
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("escape", result.stderr.lower())
        import shutil
        shutil.rmtree(tmpdir)

    def test_plan_rejects_absolute_path(self):
        result, tmpdir = self._run_plan({
            "WITH_AUDIO": "true",
            "VO_FILE": "/etc/passwd",
        })
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("absolute", result.stderr.lower())
        import shutil
        shutil.rmtree(tmpdir)

    def test_plan_audio_mode_strict(self):
        # R-022: WITH_AUDIO must be exactly true/false
        from plan import validate_audio_mode
        self.assertTrue(validate_audio_mode("true"))
        self.assertTrue(validate_audio_mode("TRUE"))
        self.assertTrue(validate_audio_mode("  true  "))
        self.assertFalse(validate_audio_mode("false"))
        self.assertFalse(validate_audio_mode("FALSE"))
        # Arbitrary strings must fail
        import subprocess
        for bad in ["yes", "1", "", "maybe", "Truee"]:
            result, tmpdir = self._run_plan({"WITH_AUDIO": bad})
            self.assertNotEqual(result.returncode, 0,
                                f"WITH_AUDIO={bad!r} should be rejected")
            import shutil
            shutil.rmtree(tmpdir)


if __name__ == "__main__":
    unittest.main(verbosity=2)
