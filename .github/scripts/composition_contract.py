#!/usr/bin/env python3
"""
R-2: Universal composition contract (2026-10-10).

One registry declaring, for EVERY composition id in src/RemotionRoot.tsx:
  - role:       production | test | demo | calibration | fixture | rehearsal
  - brain:      required | exempt        (must the production brain govern it?)
  - timeline:   compiled_beats | fixed   (beat-compiled or hand-built timeline)
  - tokens:     design_tokens | legacy   (which visual-token source it uses)
  - audio:      embedded | none          (does the composition render <Audio>?)
  - qa:         verify_render | pytest | manual | none
  - exemption:  reason string, or None. Only allowed when role != "production".

Enforcement rules (used by validate_dispatch.py and plan.py):
  1. Unknown composition id -> dispatch/plan FAILS (fail closed). Previously a
     bad id passed format checks and died later inside the render matrix.
  2. role == "production" may NOT carry an exemption -> FAILS.
  3. brain == "exempt" requires a non-empty exemption reason -> FAILS.
  4. audio == "embedded" with with_audio=false -> FAILS. A master labeled
     video_only must never contain an audio stream (verified defect E1:
     HousingBroke.tsx and MoneyDying.tsx embed <Audio>).

This module has no dependencies beyond the standard library so it can be
imported by dispatch-time scripts and by CI consistency tests.
"""

import os
import re

# ---------------------------------------------------------------------------
# Registry — one entry per <Composition id="..."> in src/RemotionRoot.tsx.
# ---------------------------------------------------------------------------
COMPOSITIONS = {
    # --- legacy pipeline tests (pre-brain) ---------------------------------
    "TrialVideo":    dict(role="test", brain="exempt", timeline="fixed", tokens="legacy",
                          audio="embedded", qa="none",
                          exemption="Legacy 30s pipeline-test format; predates the brain"),
    "StressTest":    dict(role="test", brain="exempt", timeline="fixed", tokens="legacy",
                          audio="embedded", qa="none",
                          exemption="Retired stress-test format; predates the brain"),
    "PipeTestVideo": dict(role="test", brain="exempt", timeline="fixed", tokens="legacy",
                          audio="embedded", qa="none",
                          exemption="Pipeline smoke test"),
    "HysaTest":      dict(role="test", brain="exempt", timeline="fixed", tokens="legacy",
                          audio="embedded", qa="none",
                          exemption="Single-scenario test"),
    "BankTestVideo": dict(role="test", brain="exempt", timeline="fixed", tokens="legacy",
                          audio="embedded", qa="none",
                          exemption="Single-scenario test"),
    "RecutVideo":    dict(role="test", brain="exempt", timeline="fixed", tokens="legacy",
                          audio="embedded", qa="none",
                          exemption="Re-cut test"),
    # --- production ---------------------------------------------------------
    "MoneyDying":    dict(role="production", brain="required", timeline="fixed",
                          tokens="design_tokens", audio="embedded", qa="verify_render",
                          exemption=None),
    "HousingBroke":  dict(role="production", brain="required", timeline="fixed",
                          tokens="design_tokens", audio="embedded", qa="verify_render",
                          exemption=None),
    "ProductionBeats": dict(role="production", brain="required", timeline="compiled_beats",
                          tokens="design_tokens", audio="none", qa="verify_render",
                          exemption=None),
    # --- rehearsal ----------------------------------------------------------
    "P3Rehearsal":   dict(role="rehearsal", brain="required", timeline="compiled_beats",
                          tokens="design_tokens", audio="none", qa="verify_render",
                          exemption=None),
    # --- calibration --------------------------------------------------------
    "CalibrationV0": dict(role="calibration", brain="exempt", timeline="fixed",
                          tokens="design_tokens", audio="none", qa="manual",
                          exemption="Isolated visual calibration; pixel measurement only"),
    "CalibrationV1": dict(role="calibration", brain="exempt", timeline="fixed",
                          tokens="design_tokens", audio="none", qa="manual",
                          exemption="Isolated visual calibration; pixel measurement only"),
    "CalibrationV2": dict(role="calibration", brain="exempt", timeline="fixed",
                          tokens="design_tokens", audio="none", qa="manual",
                          exemption="Isolated visual calibration; pixel measurement only"),
    "CalibrationV3": dict(role="calibration", brain="exempt", timeline="fixed",
                          tokens="design_tokens", audio="none", qa="manual",
                          exemption="Isolated visual calibration; pixel measurement only"),
    "MaterialA":     dict(role="calibration", brain="exempt", timeline="fixed",
                          tokens="design_tokens", audio="none", qa="manual",
                          exemption="Material A/B comparison"),
    "MaterialB":     dict(role="calibration", brain="exempt", timeline="fixed",
                          tokens="design_tokens", audio="none", qa="manual",
                          exemption="Material A/B comparison"),
    # --- demo / fixtures ----------------------------------------------------
    "FinanceProof":  dict(role="demo", brain="exempt", timeline="fixed", tokens="legacy",
                          audio="none", qa="none",
                          exemption="Legacy manual fixture (kept until golden regression passes)"),
    "VisualShowcase": dict(role="demo", brain="exempt", timeline="fixed",
                          tokens="design_tokens", audio="none", qa="manual",
                          exemption="31-section visual showcase demo"),
    # --- test ---------------------------------------------------------------
    "B6A":           dict(role="test", brain="exempt", timeline="compiled_beats",
                          tokens="design_tokens", audio="none", qa="none",
                          exemption="Arbitration test pair; compiled beat data without selector authority"),
    "B6B":           dict(role="test", brain="exempt", timeline="compiled_beats",
                          tokens="design_tokens", audio="none", qa="none",
                          exemption="Arbitration test pair; compiled beat data without selector authority"),
    "ChainTest":     dict(role="test", brain="exempt", timeline="compiled_beats",
                          tokens="design_tokens", audio="none", qa="none",
                          exemption="Chain visualization test"),
    "CompositionA":  dict(role="test", brain="exempt", timeline="fixed",
                          tokens="design_tokens", audio="none", qa="manual",
                          exemption="Composition-scale test pair"),
    "CompositionB":  dict(role="test", brain="exempt", timeline="fixed",
                          tokens="design_tokens", audio="none", qa="manual",
                          exemption="Composition-scale test pair"),
    "ModeRegression": dict(role="test", brain="exempt", timeline="fixed",
                          tokens="design_tokens", audio="none", qa="pytest",
                          exemption="23-mode regression (tests/test_23_modes.py)"),
}

REQUIRED_FIELDS = {"role", "brain", "timeline", "tokens", "audio", "qa", "exemption"}
VALID_ROLES = {"production", "test", "demo", "calibration", "fixture", "rehearsal"}
VALID_BRAIN = {"required", "exempt"}
VALID_TIMELINE = {"compiled_beats", "fixed"}
VALID_TOKENS = {"design_tokens", "legacy"}
VALID_AUDIO = {"embedded", "none"}
VALID_QA = {"verify_render", "pytest", "manual", "none"}


def get_contract(composition):
    """Return the contract dict for a composition id, or None if unregistered."""
    return COMPOSITIONS.get(composition)


def registered_ids():
    """All composition ids covered by the contract."""
    return set(COMPOSITIONS.keys())


def remotion_root_ids(repo_root):
    """Composition ids actually registered in src/RemotionRoot.tsx."""
    path = os.path.join(repo_root, "src", "RemotionRoot.tsx")
    with open(path) as f:
        content = f.read()
    return set(re.findall(r'<Composition\s[^>]*id="([A-Za-z0-9_]+)"', content))


def validate_for_dispatch(composition, with_audio):
    """Enforce the contract for a dispatch. Returns a list of error strings."""
    errors = []
    contract = get_contract(composition)
    if contract is None:
        errors.append(
            f"Composition '{composition}' is not registered in the composition "
            f"contract (.github/scripts/composition_contract.py). Unregistered "
            f"compositions cannot be dispatched."
        )
        return errors

    missing = REQUIRED_FIELDS - set(contract.keys())
    if missing:
        errors.append(
            f"Composition '{composition}' contract is missing fields: {sorted(missing)}"
        )
        return errors

    if contract["role"] not in VALID_ROLES:
        errors.append(
            f"Composition '{composition}' has invalid role {contract['role']!r} "
            f"(must be one of {sorted(VALID_ROLES)})"
        )

    # Every policy field must hold a known value — a typo'd policy must never
    # silently pass as a weaker requirement.
    for field, valid in (("brain", VALID_BRAIN), ("timeline", VALID_TIMELINE),
                         ("tokens", VALID_TOKENS), ("audio", VALID_AUDIO),
                         ("qa", VALID_QA)):
        if contract.get(field) not in valid:
            errors.append(
                f"Composition '{composition}' has invalid {field} "
                f"{contract.get(field)!r} (must be one of {sorted(valid)})"
            )

    # Production compositions cannot self-exempt from the brain.
    if contract["role"] == "production" and contract.get("exemption"):
        errors.append(
            f"Composition '{composition}' is role=production but claims a brain "
            f"exemption: {contract['exemption']!r}. Production compositions cannot "
            f"be exempt."
        )

    # An exemption claim requires a documented reason.
    if contract["brain"] == "exempt" and not contract.get("exemption"):
        errors.append(
            f"Composition '{composition}' claims brain=exempt without a documented "
            f"exemption reason."
        )

    # Audio honesty (verified defect E1): embedded <Audio> + with_audio=false
    # would produce a master labeled video_only that contains an audio stream.
    if contract["audio"] == "embedded" and not with_audio:
        errors.append(
            f"Composition '{composition}' embeds <Audio> (audio_policy=embedded) "
            f"but with_audio=false: the master would be labeled video_only while "
            f"containing an audio stream. Dispatch with with_audio=true, or fix "
            f"the composition's audio policy."
        )
    return errors


def find_duplicate_ids(content):
    """Return {id: count} for registry keys declared more than once."""
    seen = {}
    for m in re.finditer(r'^    "([A-Za-z0-9_]+)":\s*dict\(', content, re.M):
        cid = m.group(1)
        seen[cid] = seen.get(cid, 0) + 1
    return {cid: n for cid, n in seen.items() if n > 1}


def check_no_duplicate_ids():
    """A Python dict collapses duplicate keys silently, so check the source.

    Each composition id must appear exactly once as a top-level registry key.
    Returns a list of error strings (empty = clean).
    """
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "composition_contract.py")
    with open(path) as f:
        content = f.read()
    return [
        f"Composition '{cid}' is declared {count} times in the "
        f"contract registry (must appear exactly once)"
        for cid, count in sorted(find_duplicate_ids(content).items())
    ]


def check_registry_consistency(repo_root):
    """The contract must cover exactly the compositions RemotionRoot registers."""
    errors = []
    root_ids = remotion_root_ids(repo_root)
    contract_ids = registered_ids()
    for cid in sorted(root_ids - contract_ids):
        errors.append(
            f"Composition '{cid}' is registered in RemotionRoot.tsx but has no "
            f"contract entry."
        )
    for cid in sorted(contract_ids - root_ids):
        errors.append(
            f"Composition '{cid}' has a contract entry but is not registered in "
            f"RemotionRoot.tsx (stale entry)."
        )
    return errors


def self_test():
    """Smoke assertions runnable via `python3 .github/scripts/composition_contract.py`."""
    assert len(COMPOSITIONS) == 24, f"expected 24 compositions, got {len(COMPOSITIONS)}"
    for cid, c in COMPOSITIONS.items():
        assert REQUIRED_FIELDS <= set(c.keys()), f"{cid} missing fields"
        assert c["role"] in VALID_ROLES, f"{cid} bad role"
    # Unknown id is rejected.
    errs = validate_for_dispatch("NoSuchVideo", True)
    assert errs and "not registered" in errs[0]
    # Invalid policy values are rejected.
    saved = COMPOSITIONS["B6A"]["brain"]
    COMPOSITIONS["B6A"]["brain"] = "maybe"
    try:
        errs = validate_for_dispatch("B6A", True)
        assert errs and "invalid brain" in errs[0], errs
    finally:
        COMPOSITIONS["B6A"]["brain"] = saved
    # No duplicate declarations in the registry source.
    assert check_no_duplicate_ids() == []
    # Embedded-audio + with_audio=false is rejected (defect E1).
    errs = validate_for_dispatch("HousingBroke", False)
    assert errs and "video_only" in errs[0]
    # Production cannot claim exemption.
    saved = COMPOSITIONS["HousingBroke"]["exemption"]
    COMPOSITIONS["HousingBroke"]["exemption"] = "bogus"
    try:
        errs = validate_for_dispatch("HousingBroke", True)
        assert errs and "cannot" in errs[0] and "exempt" in errs[0]
    finally:
        COMPOSITIONS["HousingBroke"]["exemption"] = saved
    # All registered ids pass with_audio=true.
    for cid in COMPOSITIONS:
        errs = validate_for_dispatch(cid, True)
        assert not errs, f"{cid}: {errs}"
    print("composition_contract self-test: OK (24 registered, gates behave)")


if __name__ == "__main__":
    self_test()
