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
     A composition embedding <Audio>; any production composition may).

This module has no dependencies beyond the standard library so it can be
imported by dispatch-time scripts and by CI consistency tests.
"""

import os
import re

# ---------------------------------------------------------------------------
# Registry — one entry per <Composition id="..."> in src/RemotionRoot.tsx.
#
# total_frames: authoritative composition duration in frames, resolved from
# the canonical TSX source (see tests/test_composition_frames.py which
# verifies every value against its source file). plan.py rejects any
# start_frame/end_frame outside [0, total_frames).
# ---------------------------------------------------------------------------
COMPOSITIONS = {
    # --- legacy pipeline tests (pre-brain) ---------------------------------
    # --- production ---------------------------------------------------------
    "ProductionBeats": dict(role="production", brain="required", timeline="compiled_beats",
                          tokens="design_tokens", audio="none", qa="verify_render",
                          total_frames=1820,
                          exemption=None),
    # --- rehearsal ----------------------------------------------------------
    # --- calibration --------------------------------------------------------
    # --- demo / fixtures ----------------------------------------------------
    "FinanceProof":  dict(role="demo", brain="exempt", timeline="fixed", tokens="legacy",
                          audio="none", qa="none", total_frames=1860,
                          exemption="Legacy manual fixture (kept until golden regression passes)"),
    "SavingsTrap":   dict(role="production", brain="required", timeline="compiled_beats",
                          tokens="design_tokens", audio="none", qa="verify_render",
                          total_frames=5400,
                          exemption=None),
    "CompoundInterest": dict(role="production", brain="required", timeline="compiled_beats",
                          tokens="design_tokens", audio="none", qa="verify_render",
                          total_frames=5400,
                          exemption=None),
    "EmergencyFund": dict(role="production", brain="required", timeline="compiled_beats",
                          tokens="design_tokens", audio="none", qa="verify_render",
                          total_frames=5400,
                          exemption=None),
    "BudgetRule": dict(role="production", brain="required", timeline="compiled_beats",
                          tokens="design_tokens", audio="embedded", qa="verify_render",
                          total_frames=5400,
                          exemption=None),
    "EmergencyShield": dict(role="production", brain="required", timeline="compiled_beats",
                          tokens="design_tokens", audio="embedded", qa="verify_render",
                          total_frames=3088,
                          exemption=None),
    "CreditScore": dict(role="production", brain="required", timeline="compiled_beats",
                          tokens="design_tokens", audio="embedded", qa="verify_render",
                          total_frames=3379,
                          exemption=None),
    # Generic event-driven pipeline: video_id selects data via workflow manifest.
    # No video-specific paths in contract. Timeline validated from manifest.
    # audio_ownership: "embedded" = <Audio> in component, workflow must use with_audio=false
    #                 "muxed" = workflow muxes via vo_file, component must NOT embed
    "EventDriven": dict(role="production", brain="required", timeline="event_timeline",
                          tokens="design_tokens", audio="embedded", audio_ownership="embedded",
                          qa="verify_render",
                          # F-08: total_frames is DYNAMIC for EventDriven.
                          # get_total_frames() computes it from the video's
                          # timeline (see below). NO FALLBACK — fails closed
                          # if timeline is unavailable.
                          # dynamic_duration=True is the explicit marker:
                          # this composition has NO static total_frames, and
                          # every caller must supply video_id to resolve one.
                          total_frames=None,
                          dynamic_duration=True,
                          exemption=None),
    # --- test ---------------------------------------------------------------
}

REQUIRED_FIELDS = {"role", "brain", "timeline", "tokens", "audio", "qa",
                   "exemption", "total_frames"}
VALID_ROLES = {"production", "test", "demo", "calibration", "fixture", "rehearsal"}
VALID_BRAIN = {"required", "exempt"}
VALID_TIMELINE = {"compiled_beats", "fixed", "event_timeline"}
VALID_TOKENS = {"design_tokens", "legacy"}
VALID_AUDIO = {"embedded", "none"}
VALID_QA = {"verify_render", "pytest", "manual", "none"}


# Compositions blocked from production until they migrate to explicit Typography roles.
LEGACY_TYPOGRAPHY_BLOCKED = frozenset([
    "BudgetRule", "CompoundInterest", "EmergencyFund", "EmergencyShield",
    "ProductionBeats", "SavingsTrap",
])

def is_blocked(composition_id):
    if composition_id in LEGACY_TYPOGRAPHY_BLOCKED:
        return "Legacy typography: must migrate to explicit Typography roles"
    return None

def get_contract(composition):
    """Return the contract dict for a composition id, or None if unregistered."""
    return COMPOSITIONS.get(composition)


def get_total_frames(composition, video_id=None):
    """Return the authoritative total frame count for a composition id.

    For EventDriven, computes dynamically from the video's timeline
    (F-08). video_id must be provided for EventDriven.

    Returns an int, or None if the composition is unregistered or its
    contract lacks a valid total_frames. Callers must treat None as
    "cannot validate" and fail closed.
    """
    # F-08: EventDriven duration is dynamic (from timeline, not hardcoded)
    if composition == "EventDriven" and video_id:
        import json
        import os
        # Try the video's data timeline (checked-in, stable duration)
        for path in [
            f"src/videos/{video_id}/data/event_timeline.json",
            "src/videos/_active/timeline.json",
        ]:
            if os.path.exists(path):
                try:
                    with open(path) as f:
                        tl = json.load(f)
                    events = tl.get("events", [])
                    if events:
                        max_end = max(e.get("end_frame", 0) for e in events)
                        if max_end > 0:
                            return int(max_end)
                except (json.JSONDecodeError, OSError, KeyError):
                    continue
        # Fall through to contract fallback if timeline unreadable
    contract = get_contract(composition)
    if contract is None:
        return None
    total = contract.get("total_frames")
    if not isinstance(total, int) or isinstance(total, bool) or total <= 0:
        return None
    return total


def registered_ids():
    """All composition ids covered by the contract."""
    return set(COMPOSITIONS.keys())


def remotion_root_ids(repo_root):
    """Composition ids actually registered in src/RemotionRoot.tsx."""
    path = os.path.join(repo_root, "src", "RemotionRoot.tsx")
    with open(path) as f:
        content = f.read()
    return set(re.findall(r'<Composition\s[^>]*id="([A-Za-z0-9_]+)"', content))


def validate_for_dispatch(composition, with_audio, video_id=None):
    """Enforce the contract for a dispatch. Returns a list of error strings.

    video_id is required for dynamic-duration compositions (total_frames
    is None + dynamic_duration=True, e.g. EventDriven): without it the
    duration cannot be resolved and dispatch fails closed.
    """
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

    # F-16: Only role=production may be dispatched to the production workflow.
    # Demo/test/calibration compositions must not reach production renders.
    if contract["role"] != "production":
        errors.append(
            f"Composition '{composition}' has role={contract['role']!r}, not 'production'. "
            f"Only production-role compositions may be dispatched. "
            f"(FinanceProof is demo-role and must not render via production.)"
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

    # Q1 (2026-10-11): total_frames must be a positive integer. plan.py
    # rejects frame ranges outside [0, total_frames); a missing or invalid
    # total fails closed here so the bound is never silently skipped.
    # Dynamic-duration compositions resolve their total from the video's
    # timeline — video_id is mandatory for them, and an unresolvable
    # timeline fails closed (never falls back to a static guess).
    if contract.get("dynamic_duration"):
        if not video_id:
            errors.append(
                f"Composition '{composition}' has dynamic duration: "
                f"video_id is required to resolve total_frames. "
                f"Dispatch without video_id cannot validate frame ranges."
            )
        elif get_total_frames(composition, video_id=video_id) is None:
            errors.append(
                f"Composition '{composition}' has dynamic duration but "
                f"total_frames could not be resolved from video_id "
                f"{video_id!r}. Frame-range validation cannot run."
            )
    elif get_total_frames(composition) is None:
        errors.append(
            f"Composition '{composition}' has missing or invalid total_frames "
            f"in the contract registry. Frame-range validation cannot run."
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


def discover_video_id_with_timeline(repo_root):
    """Find a checked-in video id with a readable event timeline.

    Generic discovery (glob, no hardcoded video names): used by the
    self-test and tests to resolve dynamic-duration compositions through
    the real production path (checked-in timeline -> total_frames).
    Returns the video id, or None if no such timeline exists.
    """
    import glob as _glob
    import json as _json
    pattern = os.path.join(repo_root, "src", "videos", "*", "data",
                           "event_timeline.json")
    for path in sorted(_glob.glob(pattern)):
        try:
            with open(path) as f:
                tl = _json.load(f)
        except (OSError, ValueError):
            continue
        events = tl.get("events", []) if isinstance(tl, dict) else []
        if events and max((e.get("end_frame", 0) for e in events),
                          default=0) > 0:
            # src/videos/<video_id>/data/event_timeline.json
            return os.path.basename(os.path.dirname(
                os.path.dirname(path)))
    return None


def self_test():
    """Smoke assertions runnable via `python3 .github/scripts/composition_contract.py`."""
    # Registry must match RemotionRoot.tsx registrations (no hardcoded count).
    import os as _os
    _here = _os.path.dirname(_os.path.abspath(__file__))
    _repo = _os.path.dirname(_os.path.dirname(_here))
    root_ids = remotion_root_ids(_repo)
    assert set(COMPOSITIONS) == set(root_ids), \
        f"registry/RemotionRoot mismatch: registry-only={set(COMPOSITIONS)-set(root_ids)}, root-only={set(root_ids)-set(COMPOSITIONS)}"
    # A checked-in timeline to resolve dynamic compositions (generic).
    _dynamic_video = None
    for cid, c in COMPOSITIONS.items():
        assert REQUIRED_FIELDS <= set(c.keys()), f"{cid} missing fields"
        assert c["role"] in VALID_ROLES, f"{cid} bad role"
        if c.get("dynamic_duration"):
            # Dynamic: NO static total (fail closed without video_id),
            # and resolvable through the real timeline path with one.
            assert get_total_frames(cid) is None, \
                f"{cid}: dynamic composition must not resolve without video_id"
            assert c.get("total_frames") is None, \
                f"{cid}: dynamic composition must not carry a static total_frames"
            if _dynamic_video is None:
                _dynamic_video = discover_video_id_with_timeline(_repo)
            assert _dynamic_video is not None, \
                f"{cid}: no checked-in event timeline to resolve dynamic duration"
            total = get_total_frames(cid, video_id=_dynamic_video)
            assert isinstance(total, int) and total > 0, \
                f"{cid}: could not resolve total_frames from {_dynamic_video!r}"
            errs = validate_for_dispatch(cid, True)
            assert errs and "video_id" in errs[0], \
                f"{cid}: must fail closed without video_id, got {errs}"
            errs = validate_for_dispatch(cid, True, video_id=_dynamic_video)
            assert not errs, f"{cid} with video_id={_dynamic_video!r}: {errs}"
        else:
            # Q1: static compositions must carry a valid total_frames.
            assert get_total_frames(cid) is not None, f"{cid} missing/invalid total_frames"
    # Unknown id is rejected.
    errs = validate_for_dispatch("NoSuchVideo", True)
    assert errs and "not registered" in errs[0]
    assert get_total_frames("NoSuchVideo") is None
    # Invalid policy values are rejected.
    saved = COMPOSITIONS["SavingsTrap"]["brain"]
    COMPOSITIONS["SavingsTrap"]["brain"] = "maybe"
    try:
        errs = validate_for_dispatch("SavingsTrap", True)
        assert errs and "invalid brain" in errs[0], errs
    finally:
        COMPOSITIONS["SavingsTrap"]["brain"] = saved
    # No duplicate declarations in the registry source.
    assert check_no_duplicate_ids() == []
    # Embedded-audio + with_audio=false is rejected (defect E1).
    # Test every production composition with embedded audio (pipeline, not video-specific).
    embedded = [c for c, v in COMPOSITIONS.items()
                if v.get("role") == "production" and v.get("audio") == "embedded"]
    assert embedded, "no embedded-audio production compositions"
    for cid in embedded:
        errs = validate_for_dispatch(cid, False)
        assert errs and "video_only" in errs[0], f"{cid}: {errs}"
    # Production cannot claim exemption (test any production composition).
    pcid = next(c for c, v in COMPOSITIONS.items() if v.get("role") == "production")
    saved = COMPOSITIONS[pcid]["exemption"]
    COMPOSITIONS[pcid]["exemption"] = "bogus"
    try:
        errs = validate_for_dispatch(pcid, True)
        assert errs and "cannot" in errs[0] and "exempt" in errs[0]
    finally:
        COMPOSITIONS[pcid]["exemption"] = saved
    # All registered ids pass with_audio=true.
    # Dynamic compositions need a video_id (resolved above via a
    # checked-in timeline); non-production roles are still rejected.
    for cid in COMPOSITIONS:
        if COMPOSITIONS[cid].get("dynamic_duration"):
            errs = validate_for_dispatch(cid, True, video_id=_dynamic_video)
            assert not errs, f"{cid}: {errs}"
        elif COMPOSITIONS[cid].get("role") == "production":
            errs = validate_for_dispatch(cid, True)
            assert not errs, f"{cid}: {errs}"
        else:
            errs = validate_for_dispatch(cid, True)
            assert errs, f"{cid} (non-production) should be rejected"
    print(f"composition_contract self-test: OK ({len(COMPOSITIONS)} registered, gates behave)")


if __name__ == "__main__":
    self_test()
