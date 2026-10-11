#!/usr/bin/env python3
"""
Test: No hardcoded scenes in production compositions (2026-10-11)

This test FAILS if any production composition hardcodes scenes instead of
using the visual_mode routing system from VISUAL_BRAIN.md.

The HousingBroke bypass pattern (hardcoded H1-H7 scenes) must never recur.
Every production composition must route through the semantic visual selector.
"""

import os
import re
import sys

def test_no_hardcoded_scenes():
    src_dir = os.path.join(os.path.dirname(__file__), "..", "src")
    violations = []

    # Production compositions that must use visual_mode routing
    production_comps = ["FromScratchLight"]

    for comp in production_comps:
        path = os.path.join(src_dir, f"{comp}.tsx")
        if not os.path.exists(path):
            continue

        with open(path, 'r') as f:
            content = f.read()

        # Check 1: Must import from ./light/
        if "from "./light/" not in content and "from './light/" not in content:
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
        sys.exit(1)

    print("PASS: No hardcoded scenes in production compositions")
    sys.exit(0)

if __name__ == "__main__":
    test_no_hardcoded_scenes()
