#!/usr/bin/env python3
"""
Unified pre-render enforcement gate.
Derived from canonical sources — no new laws.

Each check maps to PRE_RENDER_CHECKLIST.md with:
  source, enforcer, consumer, test, evidence.

Exit 0 = all pass. Exit non-zero = FAIL, do not dispatch.
"""
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# Authorization state (in production, this comes from Hamza's explicit order).
# For local verification, these files must exist with valid content.
# ---------------------------------------------------------------------------
AUTH_DIR = os.path.join(REPO, ".production-state", "authorizations")


def _read_auth(name):
    path = os.path.join(AUTH_DIR, name + ".json")
    if not os.path.exists(path):
        return None
    try:
        return json.load(open(path))
    except Exception:
        return None


def check_visual_identity():
    """VISUAL_BRAIN §0: Light Premium Fintech only."""
    tokens_path = os.path.join(REPO, "..", "design_tokens.json")
    # Fallback: check the demo-video copy if canonical not reachable
    if not os.path.exists(tokens_path):
        tokens_path = os.path.join(REPO, "src", "light", "tokens.ts")
    if not os.path.exists(tokens_path):
        return False, "design tokens not found"
    content = open(tokens_path).read()
    # Dark identity markers that must NOT appear in the default path
    dark_markers = ["#0F0D24", "neon", "Premium SaaS"]
    for m in dark_markers:
        if m in content:
            return False, f"dark identity marker found: {m}"
    return True, "light identity confirmed"


def check_sfx_mix_flag(workflow_inputs):
    """Hamza's order: with_sfx_mix must be false without explicit auth."""
    if workflow_inputs.get("with_sfx_mix") is True:
        auth = _read_auth("sfx_mix")
        if not auth or not auth.get("authorized"):
            return False, "with_sfx_mix=true without authorization"
    return True, "sfx mix flag OK"


def check_creative_approval():
    """Q004 rejected 2026-10-10: visual direction needs explicit approval."""
    auth = _read_auth("creative")
    if not auth or not auth.get("approved"):
        return False, "no creative approval on file (Q004 direction rejected)"
    if auth.get("rejected"):
        return False, "creative direction explicitly rejected"
    return True, f"creative approved: {auth.get('note', '')}"


def check_authorization():
    """No production dispatch without Hamza's explicit authorization."""
    auth = _read_auth("production_dispatch")
    if not auth or not auth.get("authorized"):
        return False, "no production dispatch authorization"
    return True, "dispatch authorized"


def check_recovery_tools():
    """AGENTS.md render recovery law: tools must exist."""
    required = [
        ".github/scripts/classify_failure.py",
        ".github/scripts/build_ledger.py",
        "tools/trigger_reassemble.sh",
    ]
    missing = [t for t in required if not os.path.exists(os.path.join(REPO, t))]
    if missing:
        return False, f"recovery tools missing: {missing}"
    return True, "recovery tools present"


def check_variety(beat_timeline_path):
    """VISUAL_BRAIN §6: ≤2 typography-led beats in a row."""
    if not beat_timeline_path or not os.path.exists(beat_timeline_path):
        return True, "no beat timeline (skip)"
    beats = json.load(open(beat_timeline_path)).get("beats", [])
    run = 0
    for b in beats:
        mode = b.get("visual_mode", "")
        if mode in ("headline", "hero_typography", "hero_number"):
            run += 1
            if run > 2:
                return False, f"typography run of {run} at beat {b.get('beat_id')}"
        else:
            run = 0
    return True, "variety law satisfied"


def run_all(workflow_inputs=None, beat_timeline=None):
    workflow_inputs = workflow_inputs or {}
    checks = [
        ("visual_identity", check_visual_identity()),
        ("sfx_mix_flag", check_sfx_mix_flag(workflow_inputs)),
        ("creative_approval", check_creative_approval()),
        ("authorization", check_authorization()),
        ("recovery_tools", check_recovery_tools()),
        ("variety", check_variety(beat_timeline)),
    ]
    failed = [(n, msg) for n, (ok, msg) in checks if not ok]
    return checks, failed


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--inputs", help="JSON workflow inputs")
    p.add_argument("--beats", help="beat timeline JSON path")
    args = p.parse_args()

    inputs = json.load(open(args.inputs)) if args.inputs else {}
    checks, failed = run_all(inputs, args.beats)

    for name, (ok, msg) in checks:
        print(f"{'PASS' if ok else 'FAIL'} [{name}] {msg}")

    if failed:
        print(f"\n{len(failed)} check(s) FAILED — do not dispatch.")
        sys.exit(1)
    print("\nAll pre-render checks passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
