#!/usr/bin/env python3
"""P4.4 Stage 2: Decisive recovery test — actual job counts from real plan.

This test inspects the ACTUAL recovery plan (build_resume_plan), not just
validation. It proves:
1. 39 valid chunks + assembly failure → render_count=0, reused_count=39
2. Single chunk corrupt → render_count=1, reused_count=38 (only bad chunk renders)
3. Missing chunk → render_count=1 (only missing renders)
4. Source incompatible → plan rejected (fail closed)

Per directive §3: "A log message claiming '39 chunks reused' is insufficient.
The test must inspect the actual recovery plan and dispatched job count."
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".github", "scripts"))

from recovery import build_resume_plan
from generation import compute_generation_fingerprint


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


def test_incompatible_source_fails_closed():
    """Source SHA changed → plan rejected (fail closed)."""
    print("Test 4: Incompatible source → plan rejected...")
    prior = make_prior_manifest()
    current = make_inputs()
    current["source_sha"] = "DIFFERENT999"  # Changed source
    plan = make_plan()
    chunk_manifests, shas, sizes, mshas = make_chunk_manifests()

    result = build_resume_plan(
        prior, chunk_manifests, current, plan, "asset123",
        artifact_shas=shas, artifact_sizes=sizes, manifest_shas=mshas,
        prior_run_status={"status": "completed", "conclusion": "failure"},
        mode="assembly_only",  # Even in assembly-only, source must match
    )

    assert not result["ok"], "Should have rejected incompatible source!"
    assert any("fingerprint mismatch" in e for e in result["errors"])
    print("  ✅ PASS: Correctly rejected (fail closed)")


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
    test_incompatible_source_fails_closed()
    print("=" * 70)
    print("ALL 4 DECISIVE TESTS PASSED")
    print("Assembly-only recovery law: PROVEN with actual job counts")
    print("=" * 70)
