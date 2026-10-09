"""
P4.4 §4.4: Visual identity regression guard.

Prevents new production compositions from importing the retired dark theme.
Distinguishes active production imports from historical/test references.

Run: python3 -m unittest tests.test_visual_identity
"""

import os
import re
import unittest

REPO_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

# Directories that are allowed to reference the old theme
# (historical docs, retired components, test fixtures)
ALLOWED_REFERENCES = [
    "src/premium/",  # the old theme itself (until deleted)
    "tests/",  # test fixtures may reference it
    "docs/",  # historical documentation
]

# Import patterns that indicate active use of the retired dark brain
RETIRED_PATTERNS = [
    r'from\s+["\']\.\./premium/',
    r'from\s+["\']\./premium/',
    r'from\s+["\']\.\./\.\./premium/',
    r'import\s+.*\s+from\s+["\'].*premium/theme["\']',
    r'["\']#0F0D24["\']',  # dark background hex
]

# Production directories that must NOT use the retired theme
PRODUCTION_DIRS = [
    "src/housing/",
    "src/compositions/",
]


def is_allowed(path):
    """Check if a path is allowed to reference the old theme."""
    rel = os.path.relpath(path, REPO_ROOT)
    return any(rel.startswith(a) for a in ALLOWED_REFERENCES)


def find_retired_imports():
    """Find all files with retired theme imports, grouped by allowed/blocked."""
    blocked = []
    allowed = []
    for prod_dir in PRODUCTION_DIRS:
        full_dir = os.path.join(REPO_ROOT, prod_dir)
        if not os.path.isdir(full_dir):
            continue
        for root, _, files in os.walk(full_dir):
            for f in files:
                if not f.endswith((".tsx", ".ts")):
                    continue
                path = os.path.join(root, f)
                with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                    content = fh.read()
                for pattern in RETIRED_PATTERNS:
                    if re.search(pattern, content):
                        if is_allowed(path):
                            allowed.append((path, pattern))
                        else:
                            blocked.append((path, pattern))
                        break
    return blocked, allowed


class TestVisualIdentity(unittest.TestCase):
    def test_no_retired_theme_in_production(self):
        """Production scenes must not import the retired dark theme."""
        blocked, allowed = find_retired_imports()
        msg = (
            f"Found {len(blocked)} production files importing retired dark theme:\n"
            + "\n".join(f"  {p}: {pat}" for p, pat in blocked)
            + "\nMigrate to src/light/ or remove the import."
        )
        self.assertEqual(blocked, [], msg)

    def test_light_brain_used_by_housing(self):
        """All HousingBroke scenes must import from src/light/."""
        housing_dir = os.path.join(REPO_ROOT, "src", "housing")
        scenes = [
            "H1Hook.tsx", "H2Spike.tsx", "H3Autopsy.tsx",
            "H4Debt.tsx", "H5Freeze.tsx", "H6Escape.tsx", "H7Close.tsx",
        ]
        for scene in scenes:
            path = os.path.join(housing_dir, scene)
            self.assertTrue(os.path.isfile(path), f"Missing: {scene}")
            with open(path, "r") as fh:
                content = fh.read()
            self.assertIn(
                "../light/", content,
                f"{scene} does not import from src/light/"
            )


if __name__ == "__main__":
    unittest.main()
