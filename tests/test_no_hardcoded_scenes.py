#!/usr/bin/env python3
"""
Test: No hardcoded scenes in production compositions (2026-10-11)

This test FAILS if any production composition hardcodes scenes instead of
using the visual_mode routing system from VISUAL_BRAIN.md.

Pipeline test (no hardcoded video): discovers every role="production"
composition from the registry and verifies each routes through the
semantic visual selector. Works for any current or future video.
"""

import os
import re
import sys

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(REPO_ROOT, ".github", "scripts"))
from composition_contract import COMPOSITIONS

# Legacy dark compositions exempt from light-system check.
# These predate the LIGHT PREMIUM FINTECH mandate and are not
# part of the current production visual system.
LEGACY_DARK_EXEMPT = {"FromScratch"}


def _production_tsx_files():
    """Map production composition IDs to their TSX source files."""
    # Convention: src/videos/<folder>/<CompId>.tsx (video isolation, D-028).
    result = []
    videos_dir = os.path.join(REPO_ROOT, "src", "videos")
    for cid, c in COMPOSITIONS.items():
        if c.get("role") != "production":
            continue
        # Search in src/videos/*/ for the composition file
        found = None
        if os.path.isdir(videos_dir):
            for folder in os.listdir(videos_dir):
                folder_path = os.path.join(videos_dir, folder)
                if not os.path.isdir(folder_path) or folder.startswith("_"):
                    continue
                path = os.path.join(folder_path, f"{cid}.tsx")
                if os.path.isfile(path):
                    found = path
                    break
        if found:
            result.append((cid, found))
    return result


def test_no_hardcoded_scenes():
    violations = []
    comps = _production_tsx_files()
    if not comps:
        print("SKIP: no production TSX files found")
        sys.exit(0)

    for comp, path in comps:
        if comp in LEGACY_DARK_EXEMPT:
            print(f"SKIP: {comp} (legacy dark, exempt)")
            continue
        with open(path, 'r') as f:
            content = f.read()

        # Check 1: Must import from ./light/
        if 'from "./light/' not in content and "from './light/" not in content:
            violations.append(f"{comp}: does not import from ./light/ components")

        # Check 2: Must reference visual_mode
        if "visual_mode" not in content:
            violations.append(f"{comp}: does not route by visual_mode")

        # Check 3: Must not hardcode dark backgrounds
        dark_patterns = ["#0a0e1a", "#000000", "backgroundColor.*#[0-3][0-9a-f]"]
        for pattern in dark_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(f"{comp}: contains hardcoded dark color ({pattern})")

        # Check 4: Must use LightCanvas (not custom dark container)
        if "LightCanvas" not in content:
            violations.append(f"{comp}: does not use LightCanvas")

    if violations:
        print("FAIL: Hardcoded scene violations found:")
        for v in violations:
            print(f"  - {v}")
        # Fail for both pytest and script mode
        raise AssertionError(f"{len(violations)} hardcoded scene violations")

    print(f"PASS: No hardcoded scenes in {len(comps)} production compositions")

if __name__ == "__main__":
    try:
        test_no_hardcoded_scenes()
    except AssertionError as e:
        print(e)
        sys.exit(1)
