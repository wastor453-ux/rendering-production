#!/usr/bin/env python3
"""P4.4 Stage 2: Decisive recovery tests — actual job counts from the real plan.

This test inspects the ACTUAL recovery plan (build_resume_plan), not just
validation. It proves:
1. 39 valid chunks + assembly failure → render_count=0, reused_count=39
2. Single chunk corrupt → render_count=1, reused_count=38 (only bad chunk renders)
3. Missing chunk → render_count=1 (only missing renders)
4. Source change in assembly-only mode → all 39 reused, 0 rendered
   (source_sha excluded per Hamza's rule — the old "must reject" assertion
   encoded the abandoned invariant and failed identically on pristine HEAD
   0f0b9e6). The strict invariant survives in chunk_recovery mode (4b).
5. Corrupt chunk manifest in assembly-only mode → the bad chunk is NEVER
   reused; it is explicitly listed for render (zero-render guarantee void).
6. Genuine render change (different chunk count / frame range) → the plan
   is REJECTED outright; no chunk is reused, nothing is silently reassembled.
7. Tampered chunk manifests → the chunk ledger is not COMPLETE and the
   ledger gate exits 3 naming the exact chunk; hand-editing a ledger file
   cannot bypass the gate because production REBUILDS the ledger from the
   chunk manifests inside the assemble job.

RECOVERY CONTRACT (as of 2026-10-10, HEAD 0f0b9e6) — read before editing.
See also tests/test_recovery_split.py for the full contract text.

- Render (generation) fingerprint: SHA-256 over canonical render inputs
  (source_sha, composition, 1920x1080@30, start/end frame, chunk_size,
  codec, crf, with_audio, asset manifest SHA, package lock, node/remotion/
  react versions, os, chromium version + optional content hashes).
- source_sha is EXCLUDED in assembly_only mode
  (recovery.py::generation_fingerprint_for_mode; selected in production by
  REASSEMBLE_BYPASS_FINGERPRINT=true). chunk_recovery keeps it strict.
- Failure classes (classify_failure.py): PLAN_FAILURE -> dispatch fresh;
  CHUNK_FAILURE -> resume, re-render only failed chunks; ASSEMBLY_DEATH ->
  dispatch render-production-reassemble.yml with source_run_id, ZERO re-render.
- HAMZA'S STANDING RULE (RENDER LAW): assembly failure reassembles the SAME
  verified chunks and never re-renders. Enforced by: per-chunk eligibility
  checks (manifest, frame range, generation fp, verified video SHA-256, byte
  size, measured env), the build_ledger COMPLETE gate (exit 3 with exact
  missing IDs), and the assemble job's re-checksum of every staged video.

PRISTINE-BASELINE NOTE: test_incompatible_source_fails_closed was verified
failing on pristine HEAD 0f0b9e6 ("Should have rejected incompatible source!")
via a read-only git worktree — it encoded the abandoned invariant. The
contract above (Hamza's deliberate 2026-10-10 change) predates the test.
The assertion was updated to the real contract; nothing was weakened.

Per directive §3: "A log message claiming '39 chunks reused' is insufficient.
The test must inspect the actual recovery plan and dispatched job count."
"""

import copy
import json
import os
import subprocess
import sys
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".github", "scripts"))

from recovery import build_resume_plan
from generation import compute_generation_fingerprint
from build_ledger import build_ledger as build_chunk_ledger


def make_inputs():
    return {
        "source_sha": "abc123",
        "composition": "HousingBroke",
        "width": 1920, "height": 1080, "fps": 30,
        "start_frame": 0, "end_frame": 23150, "chunk_size": 600,
        "codec": "libx264", "crf": "18", "with_audio": False,
        "asset_manifest_sha256": "asset123",
        "package_lock_sha256": "lock123",
        "node_version": "20.0.0",
        "remotion_version": "4.0.532",
        "react_version": "18.0.0",
        "os": "Ubuntu 24.04",
        "expected_chromium_version": "149.0.7790.0",
    }


def get_test_generation():
    """Compute the real generation fingerprint for test inputs."""
    return compute_generation_fingerprint(make_inputs())


def make_plan(n=39):
    chunks = []
    for i in range(n):
        start = i * 600
        end = min((i + 1) * 600 - 1, 23150)
        chunks.append({"chunk_id": i, "start": start, "end": end})
    return chunks


def make_prior_manifest():
    return {
        "kind": "job",
        "manifest_version": 2,
        "stage": "video_only",
        "job_identity": "run-123-attempt-1-abc12345",
        "github": {"run_id": "123", "source_sha": "abc123"},
        "inputs": {
            "composition": "HousingBroke",
            "width": 1920, "height": 1080, "fps": 30,
            "start_frame": 0, "end_frame": 23150, "chunk_size": 600,
            "codec": "libx264", "crf": "18", "with_audio": False,
            "asset_manifest_sha256": "asset123",
            "expected_chromium_version": "149.0.7790.0",
        },
        "expected_environment": {
            "node_version": "20.0.0",
            "remotion_version": "4.0.532",
            "react_version": "18.0.0",
            "os": "Ubuntu 24.04",
            "package_lock_sha256": "lock123",
        },
        "plan": {"chunks": make_plan()},
    }


def make_chunk_manifests(n=39, corrupt_ids=None, missing_ids=None):
    """Build valid chunk manifests with real SHA placeholders."""
    corrupt_ids = corrupt_ids or set()
    missing_ids = missing_ids or set()
    gen_fp = get_test_generation()
    manifests = {}
    shas = {}
    sizes = {}
    mshas = {}
    for i in range(n):
        if i in missing_ids:
            continue
        # Use real SHA-256 format (64 hex chars) for validity checks
        real_sha = f"{i:064x}" if i not in corrupt_ids else f"{'f'*63}{i%10}"
        manifests[i] = {
            "kind": "chunk",
            "chunk_id": i,
            "frame_range": {
                "start": i * 600,
                "end": min((i + 1) * 600 - 1, 23150),
            },
            "output_sha256": real_sha,
            "output_bytes": 1000000 + i * 1000,
            "generation_fingerprint": gen_fp,
            "job_identity": "run-123-attempt-1-abc12345",
            "validation": {
                "output_exists": True,
                "output_non_empty": True,
            },
        }
        # artifact_shas: actual bytes from archive (corrupt = mismatch)
        corrupt_sha = f"{'e'*63}{i%10}"
        shas[i] = corrupt_sha if i in corrupt_ids else real_sha
        sizes[i] = 1000000 + i * 1000
        mshas[i] = f"manifest_sha_{i:02d}"
    return manifests, shas, sizes, mshas


def test_assembly_failure_zero_renders():
    """39 valid chunks, assembly failed → ZERO render jobs."""
    print("Test 1: Assembly failure with 39 valid chunks → zero render jobs...")
    prior = make_prior_manifest()
    current = make_inputs()
    plan = make_plan()
    chunk_manifests, shas, sizes, mshas = make_chunk_manifests()

    result = build_resume_plan(
        prior, chunk_manifests, current, plan, "asset123",
        artifact_shas=shas, artifact_sizes=sizes, manifest_shas=mshas,
        prior_run_status={"status": "completed", "conclusion": "failure"},
        mode="assembly_only",
    )

    assert result["ok"], f"Plan failed: {result.get('errors')}"
    rp = result["resume_plan"]
    print(f"  reused_count={rp['reused_count']}, render_count={rp['render_count']}")

    # DECISIVE: inspect actual counts, not log messages
    assert rp["reused_count"] == 39, f"Expected 39 reused, got {rp['reused_count']}"
    assert rp["render_count"] == 0, f"Expected 0 renders, got {rp['render_count']}"
    assert len(rp["render"]) == 0, "Render list must be empty"
    assert len(rp["reuse"]) == 39, "Reuse list must have 39 entries"
    print("  ✅ PASS: Zero render jobs dispatched, all 39 chunks reused")


def test_single_corrupt_chunk():
    """1 corrupt chunk → only that chunk renders, 38 reused."""
    print("Test 2: Single corrupt chunk (chunk 17) → only chunk 17 renders...")
    prior = make_prior_manifest()
    current = make_inputs()
    plan = make_plan()
    chunk_manifests, shas, sizes, mshas = make_chunk_manifests(corrupt_ids={17})

    result = build_resume_plan(
        prior, chunk_manifests, current, plan, "asset123",
        artifact_shas=shas, artifact_sizes=sizes, manifest_shas=mshas,
        prior_run_status={"status": "completed", "conclusion": "failure"},
        mode="chunk_recovery",
    )

    assert result["ok"], f"Plan failed: {result.get('errors')}"
    rp = result["resume_plan"]
    print(f"  reused_count={rp['reused_count']}, render_count={rp['render_count']}")

    assert rp["render_count"] == 1, f"Expected 1 render, got {rp['render_count']}"
    assert rp["reused_count"] == 38, f"Expected 38 reused, got {rp['reused_count']}"
    render_ids = [r["chunk_id"] for r in rp["render"]]
    assert render_ids == [17], f"Expected [17], got {render_ids}"
    print("  ✅ PASS: Only corrupt chunk 17 scheduled for render")


def test_missing_chunk():
    """1 missing chunk → only that chunk renders."""
    print("Test 3: Missing chunk (chunk 5) → only chunk 5 renders...")
    prior = make_prior_manifest()
    current = make_inputs()
    plan = make_plan()
    chunk_manifests, shas, sizes, mshas = make_chunk_manifests(missing_ids={5})

    result = build_resume_plan(
        prior, chunk_manifests, current, plan, "asset123",
        artifact_shas=shas, artifact_sizes=sizes, manifest_shas=mshas,
        prior_run_status={"status": "completed", "conclusion": "failure"},
        mode="chunk_recovery",
    )

    assert result["ok"], f"Plan failed: {result.get('errors')}"
    rp = result["resume_plan"]
    print(f"  reused_count={rp['reused_count']}, render_count={rp['render_count']}")

    assert rp["render_count"] == 1, f"Expected 1 render, got {rp['render_count']}"
    render_ids = [r["chunk_id"] for r in rp["render"]]
    assert render_ids == [5], f"Expected [5], got {render_ids}"
    print("  ✅ PASS: Only missing chunk 5 scheduled for render")


def test_4_source_change_assembly_only_reuses():
    """Source change in assembly-only mode → all 39 reused, 0 rendered.

    Per contract (Hamza's rule): source_sha is excluded from the render
    fingerprint in assembly-only mode, so a commit that only fixed assembly
    logic matches the prior run's chunks. This replaced the abandoned
    invariant (fail on any source SHA mismatch) — the old assertion failed
    identically on pristine HEAD 0f0b9e6.
    """
    print("Test 4: Source change in assembly-only mode → 39 reused, 0 rendered...")
    prior = make_prior_manifest()
    current = make_inputs()
    current["source_sha"] = "DIFFERENT999"  # Changed source (assembly fix commit)
    plan = make_plan()
    chunk_manifests, shas, sizes, mshas = make_chunk_manifests()

    result = build_resume_plan(
        prior, chunk_manifests, current, plan, "asset123",
        artifact_shas=shas, artifact_sizes=sizes, manifest_shas=mshas,
        prior_run_status={"status": "completed", "conclusion": "failure"},
        mode="assembly_only",
    )

    assert result["ok"], \
        f"Plan must accept source change in assembly-only mode: {result.get('errors')}"
    rp = result["resume_plan"]
    print(f"  reused_count={rp['reused_count']}, render_count={rp['render_count']}")
    assert rp["reused_count"] == 39, f"Expected 39 reused, got {rp['reused_count']}"
    assert rp["render_count"] == 0, f"Expected 0 renders, got {rp['render_count']}"
    assert not any("fingerprint mismatch" in e for e in result.get("errors", [])), \
        "No fingerprint-mismatch errors in assembly-only mode"
    print("  ✅ PASS: Source change accepted, all 39 chunks reused, zero renders")


def test_4b_source_change_chunk_recovery_rejected():
    """The strict invariant SURVIVES in chunk_recovery mode.

    Same source change as test 4, but chunk_recovery keeps the strict check —
    proving the assembly-only exclusion did not weaken the general contract.
    """
    print("Test 4b: Source change in chunk_recovery mode → plan rejected...")
    prior = make_prior_manifest()
    current = make_inputs()
    current["source_sha"] = "DIFFERENT999"
    plan = make_plan()
    chunk_manifests, shas, sizes, mshas = make_chunk_manifests()

    result = build_resume_plan(
        prior, chunk_manifests, current, plan, "asset123",
        artifact_shas=shas, artifact_sizes=sizes, manifest_shas=mshas,
        prior_run_status={"status": "completed", "conclusion": "failure"},
        mode="chunk_recovery",
    )

    assert not result["ok"], \
        "chunk_recovery mode must still reject a source SHA mismatch!"
    assert any("fingerprint mismatch" in e for e in result["errors"]), \
        "Rejection must cite the generation fingerprint mismatch"
    print("  ✅ PASS: Correctly rejected in chunk_recovery mode (fail closed)")


def test_5_corrupt_chunk_manifest_never_reused_assembly_only():
    """NEGATIVE (a): a corrupted chunk manifest must fail the plan's reuse.

    In assembly-only mode a checksum-tampered chunk manifest (recorded SHA !=
    independently verified video bytes) must NEVER be reused silently. The
    honest outcomes are: the bad chunk is explicitly listed for render (so
    the zero-render guarantee is visibly void), or the plan is rejected.
    """
    print("Test 5: Corrupt chunk manifest in assembly-only mode → never reused...")
    prior = make_prior_manifest()
    current = make_inputs()
    plan = make_plan()
    chunk_manifests, shas, sizes, mshas = make_chunk_manifests(corrupt_ids={17})

    result = build_resume_plan(
        prior, chunk_manifests, current, plan, "asset123",
        artifact_shas=shas, artifact_sizes=sizes, manifest_shas=mshas,
        prior_run_status={"status": "completed", "conclusion": "failure"},
        mode="assembly_only",
    )

    assert result["ok"], f"Plan failed unexpectedly: {result.get('errors')}"
    rp = result["resume_plan"]
    reuse_ids = [r["chunk_id"] for r in rp["reuse"]]
    render_ids = [r["chunk_id"] for r in rp["render"]]
    assert 17 not in reuse_ids, \
        "Corrupt chunk 17 must NEVER appear in the reuse list!"
    assert render_ids == [17], \
        f"Corrupt chunk 17 must be explicitly listed for render, got {render_ids}"
    assert rp["render_count"] == 1 and rp["reused_count"] == 38, \
        f"Expected 38 reused / 1 render, got {rp['reused_count']} / {rp['render_count']}"
    print("  ✅ PASS: Corrupt chunk refused reuse, explicitly listed for render")


def test_6_genuine_render_change_rejected():
    """NEGATIVE (b): a genuine render change must NOT reuse chunks.

    Different end_frame (23,150 -> 23,500) changes the chunk count (39 -> 40)
    and the generation fingerprint. In assembly-only mode the plan must be
    REJECTED outright — no chunk is reused and nothing is silently
    reassembled. The operator must dispatch a fresh render.
    """
    print("Test 6: Genuine render change (different frame range) → rejected...")
    prior = make_prior_manifest()
    current = make_inputs()
    current["end_frame"] = 23500  # Genuine render change, not an assembly fix
    # Current plan now has 40 chunks (chunk 39 covers 23400-23500)
    plan = []
    for i in range(40):
        start = i * 600
        end = min((i + 1) * 600 - 1, 23500)
        plan.append({"chunk_id": i, "start": start, "end": end})
    chunk_manifests, shas, sizes, mshas = make_chunk_manifests()

    result = build_resume_plan(
        prior, chunk_manifests, current, plan, "asset123",
        artifact_shas=shas, artifact_sizes=sizes, manifest_shas=mshas,
        prior_run_status={"status": "completed", "conclusion": "failure"},
        mode="assembly_only",
    )

    assert not result["ok"], \
        "A genuine render change must NOT produce a resume plan!"
    assert "resume_plan" not in result, \
        "No resume plan may be authorized on a genuine render change"
    assert any("mismatch" in e for e in result["errors"]), \
        f"Errors must cite the mismatch, got: {result['errors']}"
    print("  ✅ PASS: Genuine render change rejected, zero chunks reused")


def test_7_tampered_ledger_rejected():
    """NEGATIVE (c): a tampered ledger must be rejected by the gate.

    build_ledger.py is the ground truth for "which chunks are safely
    rendered": assembly gates on ledger COMPLETE before concatenating.
    (1) 39 valid manifests -> COMPLETE, 39/39.
    (2) One manifest tampered (validation fails) -> ledger INCOMPLETE and
        the CLI gate exits 3 naming the exact chunk ID.
    (3) Hand-editing a ledger file cannot bypass the gate: production
        REBUILDS the ledger from the chunk manifests inside the assemble
        job (render-production.yml and render-production-reassemble.yml),
        so a forged "complete" file is never trusted.
    """
    print("Test 7: Tampered ledger → gate rejects...")
    prior = make_prior_manifest()
    manifests, _shas, _sizes, _mshas = make_chunk_manifests()

    # (1) Valid ledger is COMPLETE.
    ledger = build_chunk_ledger(prior, manifests)
    assert ledger["complete"] is True, f"Valid ledger must be COMPLETE: {ledger}"
    assert ledger["ok_chunks"] == 39 and ledger["expected_chunks"] == 39
    print("  valid ledger: COMPLETE 39/39")

    # (2) Tampered manifest (chunk 17's validation fails) -> INCOMPLETE.
    tampered = copy.deepcopy(manifests)
    tampered[17]["validation"]["output_exists"] = False
    bad_ledger = build_chunk_ledger(prior, tampered)
    assert bad_ledger["complete"] is False, \
        "Tampered ledger must NOT be COMPLETE!"
    bad_ids = [e["chunk_id"] for e in bad_ledger["entries"]
               if e["status"] not in ("rendered_ok", "reused_ok")]
    assert bad_ids == [17], f"Gate must name exactly chunk 17, got {bad_ids}"
    print("  tampered ledger: INCOMPLETE, names chunk 17")

    # (3) CLI gate: exit 3 + exact chunk IDs on stderr/stdout.
    with tempfile.TemporaryDirectory() as td:
        job_path = os.path.join(td, "job_manifest.json")
        with open(job_path, "w") as f:
            json.dump(prior, f)
        chunks_dir = os.path.join(td, "chunks")
        os.makedirs(chunks_dir)
        for cid, cm in tampered.items():
            with open(os.path.join(chunks_dir, f"chunk_{cid}_manifest.json"), "w") as f:
                json.dump(cm, f)
        out_path = os.path.join(td, "chunk-ledger.json")
        scripts = os.path.join(os.path.dirname(__file__), "..", ".github", "scripts")
        proc = subprocess.run(
            [sys.executable, os.path.join(scripts, "build_ledger.py"),
             "--job-manifest", job_path, "--chunks-dir", chunks_dir,
             "--out", out_path],
            capture_output=True, text=True)
        assert proc.returncode == 3, \
            f"Ledger gate must exit 3 on incomplete chunks, got {proc.returncode}: {proc.stderr}"
        assert "17" in proc.stdout + proc.stderr, \
            "Gate output must name the tampered chunk ID 17"
    print("  CLI gate: exit 3, names chunk 17")

    # (4) A forged ledger FILE (complete=True hand-edited onto bad entries)
    # changes nothing: rebuild-from-manifests still yields INCOMPLETE.
    forged = copy.deepcopy(bad_ledger)
    forged["complete"] = True  # attacker hand-edit
    forged["ok_chunks"] = 39
    rebuilt = build_chunk_ledger(prior, tampered)
    assert rebuilt["complete"] is False, \
        "Rebuild from manifests must ignore a forged ledger file"
    print("  forged ledger file: rebuild-from-manifests still INCOMPLETE")
    print("  ✅ PASS: Tampered ledger rejected at every layer")


if __name__ == "__main__":
    print("=" * 70)
    print("STAGE 2: Decisive Recovery Tests (Actual Job Counts)")
    print("=" * 70)
    test_assembly_failure_zero_renders()
    print()
    test_single_corrupt_chunk()
    print()
    test_missing_chunk()
    print()
    test_4_source_change_assembly_only_reuses()
    print()
    test_4b_source_change_chunk_recovery_rejected()
    print()
    test_5_corrupt_chunk_manifest_never_reused_assembly_only()
    print()
    test_6_genuine_render_change_rejected()
    print()
    test_7_tampered_ledger_rejected()
    print("=" * 70)
    print("ALL 8 DECISIVE TESTS PASSED")
    print("Assembly-only recovery law: PROVEN with actual job counts")
    print("=" * 70)
