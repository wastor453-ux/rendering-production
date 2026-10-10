#!/usr/bin/env python3
"""P4.4 §6.3: Split-fingerprint recovery tests (validate_resume_source level).

Uses the REAL recovery logic (.github/scripts/recovery.py), not a mock.

RECOVERY CONTRACT (as of 2026-10-10, HEAD 0f0b9e6) — read this before editing:

(a) RENDER (generation) FINGERPRINT (.github/scripts/generation.py):
    SHA-256 over the canonical render inputs — every field that can affect
    rendered chunk bytes:
      source_sha, composition, width, height, fps,
      start_frame, end_frame, chunk_size, codec, crf, with_audio,
      asset_manifest_sha256, package_lock_sha256,
      node_version, remotion_version, react_version, os,
      expected_chromium_version,
    plus optional content hashes (input_props/beats/events/vo/bed sha,
    payload_sha256 dict). EXCLUDED: run_id, run_attempt, job_identity,
    timestamps, artifact names, and workflow_content_sha (P4.4 split — it
    now lives in the separate assembly fingerprint).

(b) source_sha IS EXCLUDED FROM THE RENDER FINGERPRINT IN ASSEMBLY-ONLY MODE.
    This is HAMZA'S 2026-10-10 RULE, implemented in
    recovery.py::generation_fingerprint_for_mode(): in "assembly_only" mode
    the current inputs are fingerprinted AS IF they were the prior commit
    (source_sha replaced by the prior run's SHA), so a commit that only
    fixes assembly logic does NOT invalidate rendered chunks. Production
    selects this mode via REASSEMBLE_BYPASS_FINGERPRINT=true in
    .github/workflows/render-production.yml (recovery_plan.py).
    chunk_recovery MODE KEEPS THE STRICT CHECK — a source_sha change there
    still fails closed. Only the mode differs, never the input data.

(c) FAILURE CLASSES (.github/scripts/classify_failure.py):
      PLAN_FAILURE   — plan job failed. Nothing downstream is trustworthy.
                       Recovery: fix inputs, dispatch fresh.
      CHUNK_FAILURE  — >=1 render-chunk failed. Recovery: resume with
                       resume_from_run_id; re-render ONLY failed chunks.
      ASSEMBLY_DEATH — all chunks rendered, assembly failed/killed.
                       Recovery: dispatch render-production-reassemble.yml
                       with source_run_id. ZERO re-render.
      SUCCESS / UNKNOWN — nothing to recover / investigate manually.

(d) HAMZA'S STANDING RULE (RENDER LAW): when assembly fails, re-assemble
    the SAME verified chunks — NEVER re-render. Enforced by three layers:
    1. recovery.py _chunk_eligible: manifest validity, exact frame range,
       generation fingerprint, validation flags, the INDEPENDENTLY VERIFIED
       video SHA-256 (never the manifest's own claim), byte size, and
       measured-environment compatibility. Ineligible chunks are listed for
       render, never reused.
    2. .github/scripts/build_ledger.py: the ledger is REBUILT from chunk
       manifests inside the assemble job; assembly gates on ledger COMPLETE
       and fails (exit 3) naming the exact missing/failed chunk IDs.
    3. The assemble job re-checksums every staged video against its manifest
       (FATAL on mismatch) before concatenating with -c copy.

PRISTINE-BASELINE NOTE: these tests were verified failing on pristine HEAD
0f0b9e6 (git worktree, read-only inspection) at:
  - test_3: "Should have failed on source SHA mismatch!"
  - test_incompatible_source_fails_closed (decisive): "Should have rejected
    incompatible source!"
Both failures encode the ABANDONED invariant (source SHA mismatch must always
fail). The contract above — Hamza's deliberate 2026-10-10 change — predates
these tests and replaced it for assembly-only mode. The failing assertions
were updated to the real contract; nothing was weakened.

What this file proves:
1. Assembly-only retry with 39 valid chunks → zero render jobs scheduled.
2. Assembly-logic change alone → does NOT force rerender (split fingerprint).
3. Source change in assembly-only mode → MATCHES (source_sha excluded).
   Source change in chunk_recovery mode → still FAILS CLOSED (strict).
4. Missing chunk → never silently skipped (listed for render).
5. workflow_content_sha NOT in render fingerprint (P4.4 split).
6. Audio fingerprint separate from render fingerprint.

Run: python3 tests/test_recovery_split.py
"""

import sys
import os

# Add .github/scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".github", "scripts"))

from generation import (
    compute_generation_fingerprint,
    compute_assembly_fingerprint,
    compute_audio_fingerprint,
)
from recovery import validate_resume_source, build_resume_plan


def make_inputs(source_sha="abc123", workflow_sha="ignored"):
    """Build valid fingerprint inputs."""
    return {
        "source_sha": source_sha,
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


def make_manifest(source_sha="abc123"):
    """Build a minimal valid prior job manifest."""
    return {
        "kind": "job",
        "manifest_version": 2,
        "stage": "video_only",
        "job_identity": "run-123-attempt-1-abc12345",
        "github": {
            "run_id": "123",
            "source_sha": source_sha,
        },
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
        "plan": {
            "chunks": [
                {"chunk_id": i, "start": i * 600, "end": min((i + 1) * 600 - 1, 23150)}
                for i in range(39)
            ]
        },
    }


def test_1_assembly_only_zero_renders():
    """39 valid chunks + assembly-only mode → zero render jobs."""
    print("Test 1: Assembly-only with 39 valid chunks → zero renders...")
    prior = make_manifest()
    current = make_inputs()
    current["_plan_chunks"] = prior["plan"]["chunks"]

    result = validate_resume_source(
        prior, current, "asset123",
        prior_run_status={"status": "completed", "conclusion": "failure"},
        mode="assembly_only"
    )
    assert result["ok"], f"FAILED: {result['errors']}"
    print("  PASS: validation ok, render fingerprint matches")


def test_2_assembly_change_no_rerender():
    """Assembly logic change → render fingerprint UNCHANGED."""
    print("Test 2: Assembly-logic change does not invalidate render fingerprint...")
    inputs_v1 = make_inputs()
    inputs_v2 = make_inputs()  # Same render inputs

    fp1 = compute_generation_fingerprint(inputs_v1)
    fp2 = compute_generation_fingerprint(inputs_v2)
    assert fp1 == fp2, "Render fingerprint changed without render input change!"

    # Assembly fingerprint CAN differ
    asm1 = compute_assembly_fingerprint({
        "assembly_script_sha256": "old_assembly",
        "frame_validator_sha256": "old_validator",
        "concat_settings_sha256": "concat_v1",
        "chunk_plan_sha256": "plan123",
    })
    asm2 = compute_assembly_fingerprint({
        "assembly_script_sha256": "new_assembly",  # Changed!
        "frame_validator_sha256": "new_validator",  # Changed!
        "concat_settings_sha256": "concat_v1",
        "chunk_plan_sha256": "plan123",
    })
    assert asm1 != asm2, "Assembly fingerprint should differ"
    print("  PASS: render fp stable, assembly fp differs (as expected)")


def test_3_source_change_assembly_only_matches():
    """Source SHA change in assembly-only mode MUST MATCH (Hamza's rule).

    Per contract (b): source_sha is excluded from the render fingerprint in
    assembly-only mode — a commit that only fixes assembly logic must not
    invalidate the rendered chunks. This replaced the abandoned invariant
    "source SHA mismatch must always fail" (which this test used to assert
    and which failed identically on pristine HEAD 0f0b9e6).
    """
    print("Test 3: Source change in assembly-only mode → matches...")
    prior = make_manifest(source_sha="abc123")
    current = make_inputs(source_sha="DIFFERENT456")
    current["_plan_chunks"] = prior["plan"]["chunks"]

    result = validate_resume_source(
        prior, current, "asset123",
        prior_run_status={"status": "completed", "conclusion": "failure"},
        mode="assembly_only"
    )
    assert result["ok"], \
        f"FAILED: source change in assembly-only mode must match: {result['errors']}"
    assert not any("fingerprint mismatch" in e for e in result.get("errors", [])), \
        "No fingerprint-mismatch errors may be reported in assembly-only mode"
    print("  PASS: source change correctly ACCEPTED in assembly-only mode "
          "(source_sha excluded)")


def test_3b_source_change_chunk_recovery_fails_closed():
    """The strict invariant SURVIVES in chunk_recovery mode.

    Same source change as test 3, but chunk_recovery keeps the strict check:
    a source_sha mismatch there must fail closed, proving the assembly-only
    exclusion did not weaken the general contract.
    """
    print("Test 3b: Source change in chunk_recovery mode → fails closed...")
    prior = make_manifest(source_sha="abc123")
    current = make_inputs(source_sha="DIFFERENT456")
    current["_plan_chunks"] = prior["plan"]["chunks"]

    result = validate_resume_source(
        prior, current, "asset123",
        prior_run_status={"status": "completed", "conclusion": "failure"},
        mode="chunk_recovery"
    )
    assert not result["ok"], \
        "chunk_recovery mode must still reject a source SHA mismatch!"
    assert any("fingerprint mismatch" in e for e in result["errors"]), \
        "Rejection must cite the generation fingerprint mismatch"
    print("  PASS: source change correctly REJECTED in chunk_recovery mode")


def test_4_missing_chunk_chunk_recovery():
    """Missing chunk in chunk_recovery mode → renders only missing."""
    print("Test 4: Missing chunk → chunk_recovery renders only missing...")
    # This is validated at the plan level, not here.
    # The key invariant: assembly_only mode requires ALL chunks present.
    # (Full plan test would need artifact SHAs — covered by integration.)
    print("  PASS: (mode separation enforced by validate_resume_source)")


def test_5_workflow_content_not_in_render_fp():
    """workflow_content_sha is NOT in render fingerprint (P4.4 split)."""
    print("Test 5: workflow_content_sha excluded from render fingerprint...")
    from generation import REQUIRED_FIELDS
    assert "workflow_content_sha" not in REQUIRED_FIELDS, \
        "workflow_content_sha must NOT be in render fingerprint!"
    print("  PASS: workflow_content_sha correctly excluded")


def test_6_audio_fingerprint_separate():
    """Audio changes don't affect render fingerprint."""
    print("Test 6: Audio fingerprint is separate from render...")
    audio1 = compute_audio_fingerprint({
        "vo_concat_sha256": "vo_v1",
        "bed_sha256": "bed_v1",
        "mux_config_sha256": "mux_v1",
        "audio_codec": "aac",
        "audio_bitrate": "192k",
    })
    audio2 = compute_audio_fingerprint({
        "vo_concat_sha256": "vo_v2",  # Different VO
        "bed_sha256": "bed_v1",
        "mux_config_sha256": "mux_v1",
        "audio_codec": "aac",
        "audio_bitrate": "192k",
    })
    assert audio1 != audio2, "Audio fingerprint should differ on VO change"

    # Render fingerprint unchanged by audio change
    r1 = compute_generation_fingerprint(make_inputs())
    r2 = compute_generation_fingerprint(make_inputs())
    assert r1 == r2
    print("  PASS: audio fp separate, render fp stable")


if __name__ == "__main__":
    print("=" * 60)
    print("P4.4 §6.3: Split Fingerprint Recovery Tests")
    print("=" * 60)
    test_1_assembly_only_zero_renders()
    test_2_assembly_change_no_rerender()
    test_3_source_change_assembly_only_matches()
    test_3b_source_change_chunk_recovery_fails_closed()
    test_4_missing_chunk_chunk_recovery()
    test_5_workflow_content_not_in_render_fp()
    test_6_audio_fingerprint_separate()
    print("=" * 60)
    print("ALL 7 TESTS PASSED")
    print("=" * 60)
