#!/usr/bin/env python3
"""Intelligent partial chunk recovery (P3.12).

Validates a prior run as a resume source and selects which chunks can be
reused vs which must be rendered.

Safety contract:
- Reuse requires: generation fingerprint match (recomputed, not trusted) +
  asset digest match + plan match + environment compatibility.
- Every reused chunk must have a valid manifest, matching checksum, exact
  frame range, and successful validation. Failed/incomplete/corrupt chunks
  are rerendered, never reused.
- Generation-wide mismatch, contradictory manifests, ambiguous sources, or
  untrustworthy provenance fail CLOSED: resume is rejected, operator must
  run clean.
- Never silently render everything while claiming resume succeeded: the
  resume plan explicitly lists reused vs rendered chunks, and assembly
  verifies the plan was honored.

Provenance: prior-run artifacts keep their original names and manifests.
They are downloaded to a separate directory and never overwritten or
relabeled. Each reused chunk's manifest records its true origin run.
"""

from generation import (
    compute_generation_fingerprint,
    fingerprint_inputs_from_job_manifest,
    describe_fingerprint_diff,
    EXPECTED_CHROMIUM_VERSION,
)

# Pinned environment fields that must match between the prior run's
# measurements and the current run's expectations for reuse.
PINNED_ENV_FIELDS = ["node_version", "remotion_version", "react_version", "os"]

# Maps PINNED_ENV_FIELDS to the generation-input key holding the current
# expected value.
_ENV_INPUT_KEYS = {
    "node_version": "node_version",
    "remotion_version": "remotion_version",
    "react_version": "react_version",
    "os": "os",
}


def _err(errors, msg):
    errors.append(msg)


def generation_fingerprint_for_mode(inputs: dict, mode: str,
                                    prior_source_sha: str = None) -> str:
    """Compute the generation fingerprint for a resume mode.

    2026-10-10 (Hamza's rule): in assembly_only mode, source_sha (the git
    commit hash) must not invalidate chunks. Every commit changes source_sha,
    which used to force a full re-render after any fix. Assembly-only
    concatenates existing chunks (bytes verified per-chunk); what matters is
    the render inputs match, not the commit hash. chunk_recovery keeps the
    strict check.

    In assembly_only mode the current inputs are fingerprinted AS IF they
    were the prior commit (prior_source_sha). This makes the fingerprint
    exactly match the generation_fingerprint stored in the prior chunks'
    manifests, so per-chunk eligibility passes. For job-level
    prior-vs-current comparison, pass prior_source_sha=None and both sides
    normalize to the same constant.
    """
    inputs = dict(inputs)
    if mode == "assembly_only":
        inputs["source_sha"] = prior_source_sha or "assembly-only"
    return compute_generation_fingerprint(inputs)


def validate_resume_source(prior_manifest: dict, current_inputs: dict,
                           current_asset_digest: str,
                           prior_run_status: dict = None,
                           mode: str = "chunk_recovery") -> dict:
    """Validate a prior run's job manifest as a resume source.

    prior_manifest: the prior run's job_manifest.json (dict).
    current_inputs: fingerprint inputs for the CURRENT run (dict, as accepted
        by generation.compute_generation_fingerprint).
    current_asset_digest: SHA-256 digest of the current asset manifest.
    prior_run_status: optional {"status", "conclusion"} from the GitHub API.
        When provided, in-progress/cancelled runs are rejected explicitly.
    mode: "chunk_recovery" (default) or "assembly_only".
        - chunk_recovery: render missing/invalid chunks. Render fingerprint
          must match strictly.
        - assembly_only: re-run assembly with zero render jobs. Render
          fingerprint must match (chunks are valid). Assembly fingerprint
          MAY differ (that's the point — assembly logic changed).

    P4.4 SPLIT (§6.1): The render fingerprint no longer includes
    workflow_content_sha. Assembly-only logic changes do NOT invalidate
    rendered chunks. The old bypass_generation_check is removed — it was
    a blunt instrument that skipped all validation. The split fingerprint
    is the proper fix.

    Returns {"ok": True, ...} or {"ok": False, "errors": [...]}. Fail closed.
    """
    errors = []

    if mode not in ("chunk_recovery", "assembly_only"):
        return {"ok": False, "errors": [f"invalid mode: {mode!r}"]}

    if not isinstance(prior_manifest, dict):
        return {"ok": False, "errors": ["prior manifest is not a dict"]}
    if prior_manifest.get("kind") != "job":
        _err(errors, f"prior manifest kind is {prior_manifest.get('kind')!r}, "
                      "expected 'job'")
    # P3.12 contract begins at manifest_version 2 (generation_fingerprint +
    # provenance). Older manifests cannot be resume sources.
    if prior_manifest.get("manifest_version", 0) < 2:
        _err(errors, f"prior manifest version "
                      f"{prior_manifest.get('manifest_version')!r} predates the "
                      "P3.12 recovery contract (v2); cannot be a resume source")

    # P3.12.1: explicit run-status policy. A run that never finished cannot
    # be a source; cancelled runs are disallowed. "failure" IS allowed —
    # that is the primary recovery case (P3.11).
    if prior_run_status is not None:
        status = prior_run_status.get("status")
        conclusion = prior_run_status.get("conclusion")
        if status != "completed":
            _err(errors, f"prior run status is {status!r}: only completed "
                          "runs can be resume sources")
        elif conclusion not in ("success", "failure"):
            _err(errors, f"prior run conclusion is {conclusion!r}: only "
                          "'success' or 'failure' runs can be resume sources")

    prior_gh = prior_manifest.get("github", {})
    if not prior_gh.get("run_id"):
        _err(errors, "prior manifest missing github.run_id")
    if not prior_gh.get("source_sha"):
        _err(errors, "prior manifest missing github.source_sha")

    prior_identity = prior_manifest.get("job_identity", "unknown")

    # 1. Recompute (not trust) the prior generation fingerprint.
    try:
        prior_inputs = fingerprint_inputs_from_job_manifest(prior_manifest)
        prior_gen = compute_generation_fingerprint(prior_inputs)
    except ValueError as e:
        _err(errors, f"cannot reconstruct prior generation inputs: {e}")
        return {"ok": False, "errors": errors}

    # 2. Compute current generation fingerprint.
    try:
        current_gen = compute_generation_fingerprint(current_inputs)
    except ValueError as e:
        _err(errors, f"current generation inputs invalid: {e}")
        return {"ok": False, "errors": errors}

    # 3. Generation fingerprints must match exactly.
    # P4.4 SPLIT: The render fingerprint no longer includes workflow_content_sha.
    # 2026-10-10 FIX (Hamza's rule): generation_fingerprint_for_mode()
    # excludes source_sha in assembly_only mode (see helper above).
    # chunk_recovery mode keeps the strict check.
    prior_gen_cmp = generation_fingerprint_for_mode(prior_inputs, mode)
    curr_gen_cmp = generation_fingerprint_for_mode(current_inputs, mode)
    if prior_gen_cmp != curr_gen_cmp:
        if mode == "assembly_only":
            _err(errors, "generation fingerprint mismatch (excl. source_sha): "
                          "prior run produced a different render generation")
        else:
            _err(errors, "generation fingerprint mismatch: prior run produced a "
                          "different render generation")
        for d in describe_fingerprint_diff(current_inputs, prior_inputs):
            _err(errors, f"  diff: {d}")
    elif mode == "assembly_only":
        print("P4.4: assembly-only mode — render fingerprint MATCHES "
              "(source_sha excluded), zero render jobs will be scheduled")

    # 4. Asset manifest digest must match (defense in depth; also in fingerprint).
    # P4.4: This check is NOT bypassed. Different assets mean different
    # chunks. The split fingerprint already excludes workflow changes, so
    # a legitimate reassembly will pass this check.
    prior_asset_digest = prior_manifest.get("inputs", {}).get(
        "asset_manifest_sha256")
    if prior_asset_digest != current_asset_digest:
        _err(errors, f"asset manifest digest mismatch: prior="
                      f"{str(prior_asset_digest)[:12]} current="
                      f"{str(current_asset_digest)[:12]}")

    # 5. Plan must be identical (same chunk count and ranges).
    prior_plan = prior_manifest.get("plan", {}).get("chunks", [])
    current_plan = current_inputs.get("_plan_chunks")
    if current_plan is not None:
        if len(prior_plan) != len(current_plan):
            _err(errors, f"chunk plan mismatch: prior has {len(prior_plan)} "
                          f"chunks, current has {len(current_plan)}")
        else:
            for pc, cc in zip(prior_plan, current_plan):
                if (pc.get("chunk_id") != cc.get("chunk_id")
                        or pc.get("start") != cc.get("start")
                        or pc.get("end") != cc.get("end")):
                    _err(errors, f"chunk plan mismatch at chunk "
                                  f"{cc.get('chunk_id')}: prior={pc} "
                                  f"current={cc}")
                    break

    # 6. Environment compatibility: prior run's EXPECTED pinned fields must
    #    match current expectations, and prior chunks' MEASURED chromium
    #    versions must match the expected chromium version.
    prior_env = prior_manifest.get("expected_environment", {})
    for field in PINNED_ENV_FIELDS:
        expected = current_inputs.get(_ENV_INPUT_KEYS[field])
        prior_val = prior_env.get(field)
        if expected is None:
            _err(errors, f"current inputs missing env field for {field}")
        elif prior_val != expected:
            _err(errors, f"environment mismatch on {field}: prior="
                          f"{prior_val!r} current={expected!r}")

    prior_chromium = prior_manifest.get("inputs", {}).get(
        "expected_chromium_version", EXPECTED_CHROMIUM_VERSION)
    current_chromium = current_inputs.get("expected_chromium_version",
                                         EXPECTED_CHROMIUM_VERSION)
    if prior_chromium != current_chromium:
        _err(errors, f"chromium version mismatch: prior={prior_chromium} "
                      f"current={current_chromium}")

    # 7. P3.12.1: prior run stage. A manifest at "planned" (render failed
    #    before assembly, the P3.11 case) is eligible — chunk validity is
    #    verified independently per chunk. Only unknown/bogus stages reject.
    prior_stage = prior_manifest.get("stage")
    if prior_stage not in ("planned", "video_only", "av_intermediate",
                           "av_master"):
        _err(errors, f"prior run stage is {prior_stage!r}: not a recognized "
                      "completed stage")

    if errors:
        return {"ok": False, "errors": errors}
    return {"ok": True, "prior_identity": prior_identity,
            "prior_generation": prior_gen,
            "prior_run_id": str(prior_gh.get("run_id"))}


def _is_valid_sha256(s) -> bool:
    """Strict SHA-256 format check: 64 hex characters."""
    if not isinstance(s, str) or len(s) != 64:
        return False
    try:
        int(s, 16)
        return True
    except ValueError:
        return False


def _chunk_eligible(chunk_manifest: dict, expected: dict,
                    expected_env: dict = None) -> tuple:
    """Check a single prior chunk manifest for reuse eligibility.

    expected: {"chunk_id", "start", "end", "generation", "artifact_sha256",
        "artifact_bytes"}. artifact_sha256 MUST be the independently verified
        SHA-256 of the actual video bytes (P3.12.2: absence is NOT success).
    expected_env: {"node_version", "remotion_version", "react_version", "os",
        "chromium_version"} — the current run's compatibility requirements.
        When provided, the candidate's MEASURED environment must satisfy it.

    P3.12.1: the original chunk manifest keeps provenance.reused=false
    (truthful — it was freshly rendered in its own run). Authorization
    comes from the NEW run's resume plan, not from mutating the original.
    Returns (eligible: bool, reason: str).
    """
    if not isinstance(chunk_manifest, dict):
        return False, "manifest is not a dict"
    if chunk_manifest.get("kind") != "chunk":
        return False, f"kind is {chunk_manifest.get('kind')!r}"
    if chunk_manifest.get("chunk_id") != expected["chunk_id"]:
        return False, "chunk_id mismatch"
    fr = chunk_manifest.get("frame_range", {})
    if fr.get("start") != expected["start"] or fr.get("end") != expected["end"]:
        return False, (f"frame range mismatch: manifest={fr} "
                        f"expected={expected['start']}-{expected['end']}")
    if chunk_manifest.get("generation_fingerprint") != expected["generation"]:
        return False, "generation fingerprint mismatch"
    val = chunk_manifest.get("validation") or {}
    if not val.get("output_exists") or not val.get("output_non_empty"):
        return False, "validation did not confirm successful output"
    # P3.12.2: the verified actual-video hash is MANDATORY. A missing,
    # malformed, or unverified hash is ineligible — never treat absence
    # as a successful comparison.
    verified_sha = expected.get("artifact_sha256")
    if not _is_valid_sha256(verified_sha):
        return False, ("no independently verified video SHA-256 "
                        "(missing/empty/corrupt video in archive)")
    recorded_sha = chunk_manifest.get("output_sha256")
    if not _is_valid_sha256(recorded_sha):
        return False, "manifest has missing or malformed output_sha256"
    if recorded_sha != verified_sha:
        return False, ("checksum mismatch: manifest-recorded hash != "
                        "actual video bytes")
    # P3.12.2: validate actual byte size against the manifest.
    verified_bytes = expected.get("artifact_bytes")
    recorded_bytes = chunk_manifest.get("output_bytes")
    if not isinstance(recorded_bytes, int) or recorded_bytes <= 0:
        return False, f"invalid output_bytes: {recorded_bytes!r}"
    if verified_bytes is not None:
        if not isinstance(verified_bytes, int) or verified_bytes <= 0:
            return False, "invalid verified byte size"
        if verified_bytes != recorded_bytes:
            return False, (f"byte size mismatch: manifest={recorded_bytes} "
                            f"actual={verified_bytes}")
    # Measured-environment compatibility. A matching generation fingerprint
    # must not override a real environment mismatch.
    if expected_env is not None:
        measured = chunk_manifest.get("measured_environment") or {}
        for field in ("node_version", "remotion_version", "react_version",
                      "os"):
            want = expected_env.get(field)
            got = measured.get(field)
            if want is not None and got != want:
                return False, (f"measured environment mismatch on {field}: "
                                f"candidate={got!r} required={want!r}")
        # Chromium: the candidate's measured version must contain the
        # required version string.
        want_chrome = expected_env.get("chromium_version")
        got_chrome = measured.get("chromium_version", "")
        if want_chrome and want_chrome not in str(got_chrome):
            return False, (f"measured chromium mismatch: candidate="
                            f"{got_chrome!r} required to contain "
                            f"{want_chrome!r}")
    return True, "eligible"


def select_chunks(prior_manifest: dict, prior_chunk_manifests: dict,
                  current_plan: list, generation: str,
                  artifact_shas: dict = None,
                  artifact_sizes: dict = None,
                  expected_env: dict = None) -> dict:
    """Select reusable vs must-render chunks.

    prior_chunk_manifests: {chunk_id: chunk_manifest_dict} from the prior run.
    current_plan: [{"chunk_id", "start", "end"}, ...] for the current run.
    generation: the validated generation fingerprint.
    artifact_shas: {chunk_id: sha256} of ACTUAL video bytes hashed from
        inside the downloaded prior artifact archives. MANDATORY for reuse —
        a missing entry means the video was not verified and the chunk is
        rerendered. Never pass manifest-recorded hashes here.
    artifact_sizes: {chunk_id: bytes} of actual video sizes.
    expected_env: measured-environment compatibility policy.

    Returns {"reuse": [...], "render": [...], "errors": [...]}.
    Deterministic: same inputs -> same selection.
    """
    errors = []
    reuse = []
    render = []
    seen_ids = set()
    artifact_shas = artifact_shas or {}
    artifact_sizes = artifact_sizes or {}

    prior_run_id = str(prior_manifest.get("github", {}).get("run_id",
                                                            "unknown"))
    prior_identity = prior_manifest.get("job_identity", "unknown")

    for chunk in current_plan:
        cid = chunk["chunk_id"]
        if cid in seen_ids:
            errors.append(f"duplicate chunk_id {cid} in current plan")
            continue
        seen_ids.add(cid)
        expected = {"chunk_id": cid, "start": chunk["start"],
                    "end": chunk["end"], "generation": generation,
                    "artifact_sha256": artifact_shas.get(cid),
                    "artifact_bytes": artifact_sizes.get(cid)}
        pm = prior_chunk_manifests.get(cid)
        if pm is None:
            render.append({"chunk_id": cid, "start": chunk["start"],
                           "end": chunk["end"],
                           "reason": "no prior chunk manifest"})
            continue
        eligible, reason = _chunk_eligible(pm, expected, expected_env)
        if eligible:
            reuse.append({
                "chunk_id": cid, "start": chunk["start"], "end": chunk["end"],
                "origin_run_id": prior_run_id,
                "origin_job_identity": prior_identity,
                "origin_artifact_sha256": pm.get("output_sha256"),
                "origin_manifest": pm,
            })
        else:
            render.append({"chunk_id": cid, "start": chunk["start"],
                           "end": chunk["end"],
                           "reason": f"prior chunk ineligible: {reason}"})

    # Detect unplanned prior chunks (informational; they are simply ignored,
    # but a contradictory manifest that claims them as planned is an error).
    planned_ids = {c["chunk_id"] for c in current_plan}
    for cid in prior_chunk_manifests:
        if cid not in planned_ids:
            errors.append(f"prior run has unplanned chunk_id {cid}; "
                          "refusing resume due to contradictory plan")

    if errors:
        return {"reuse": [], "render": [], "errors": errors}
    return {"reuse": reuse, "render": render, "errors": []}


def build_resume_plan(prior_manifest: dict, prior_chunk_manifests: dict,
                      current_inputs: dict, current_plan: list,
                      current_asset_digest: str,
                      artifact_shas: dict = None,
                      artifact_sizes: dict = None,
                      manifest_shas: dict = None,
                      expected_env: dict = None,
                      prior_run_status: dict = None,
                      mode: str = "chunk_recovery") -> dict:
    """Build the complete resume plan. Fail closed.

    artifact_shas: {chunk_id: sha256} of ACTUAL video bytes from inside the
        prior artifact archives (P3.12.1). artifact_sizes: {chunk_id: bytes}.
    manifest_shas: {chunk_id: sha256} of the ORIGINAL manifest FILE bytes
        (P3.12.2). Recorded as origin_manifest_sha256 — never a copy of
        the video hash.
    expected_env: measured-environment compatibility policy.
    prior_run_status: {"status", "conclusion"} from the GitHub API.
    mode: "chunk_recovery" or "assembly_only" (see validate_resume_source).

    Returns {"ok": True, "resume_plan": {...}} or
    {"ok": False, "errors": [...]}.
    The resume plan is stored in the new job manifest and honored by assembly.
    It is the SINGLE authoritative selection: assembly must verify every
    reuse/render entry was honored.
    """
    # Attach the current plan for the plan-compatibility check in validation.
    current_inputs = dict(current_inputs)
    current_inputs["_plan_chunks"] = current_plan
    validation = validate_resume_source(prior_manifest, current_inputs,
                                        current_asset_digest,
                                        prior_run_status,
                                        mode=mode)
    if not validation["ok"]:
        return {"ok": False, "errors": validation["errors"]}

    try:
        # 2026-10-10: mode-aware — assembly_only fingerprints current inputs
        # as the prior commit, so per-chunk eligibility matches the stored
        # chunk fingerprints. See generation_fingerprint_for_mode().
        prior_sha = prior_manifest.get("github", {}).get("source_sha")
        generation = generation_fingerprint_for_mode(
            current_inputs, mode, prior_source_sha=prior_sha)
    except ValueError as e:
        return {"ok": False, "errors": [f"current inputs invalid: {e}"]}

    selection = select_chunks(prior_manifest, prior_chunk_manifests,
                              current_plan, generation, artifact_shas,
                              artifact_sizes, expected_env)
    if selection["errors"]:
        return {"ok": False, "errors": selection["errors"]}

    # Strip heavy nested manifests from the stored plan; assembly reloads
    # them from the downloaded artifacts. Record the verified output hash
    # and size from REAL archive inspection (not trusted manifest claims).
    # P3.12.2: origin_manifest_sha256 is the hash of the original manifest
    # FILE bytes — never a copy of the video hash.
    artifact_sizes = artifact_sizes or {}
    manifest_shas = manifest_shas or {}
    reuse_light = []
    for r in selection["reuse"]:
        cid = r["chunk_id"]
        if not manifest_shas.get(cid):
            return {"ok": False, "resume_plan": None,
                    "errors": [f"chunk {cid}: missing verified original "
                               f"manifest digest — cannot authorize reuse"]}
        # Prefer the independently measured byte size; fall back to the
        # manifest's validated positive size only if real measurement is
        # unavailable (workflow always provides it).
        real_bytes = artifact_sizes.get(cid)
        if real_bytes is None:
            real_bytes = (r.get("origin_manifest") or {}).get("output_bytes")
        reuse_light.append({
            "chunk_id": cid, "start": r["start"], "end": r["end"],
            "origin_run_id": r["origin_run_id"],
            "origin_job_identity": r["origin_job_identity"],
            # Verified from actual archive bytes (mandatory per Fix 1):
            "verified_output_sha256": artifact_shas[cid],
            "verified_output_bytes": real_bytes,
            "origin_manifest_sha256": manifest_shas[cid],
        })

    resume_plan = {
        "enabled": True,
        "source_run_id": validation["prior_run_id"],
        "source_job_identity": validation["prior_identity"],
        "source_generation": validation["prior_generation"],
        # Assembly authorizes ONLY these source runs for cross-run chunks.
        "allowed_source_run_ids": [validation["prior_run_id"]],
        "reuse": reuse_light,
        "render": selection["render"],
        "reused_count": len(reuse_light),
        "render_count": len(selection["render"]),
    }
    # Honesty: never claim resume while rendering everything.
    if resume_plan["render_count"] == len(current_plan):
        resume_plan["note"] = ("no chunks eligible for reuse; full render "
                               "required")
    return {"ok": True, "resume_plan": resume_plan}
