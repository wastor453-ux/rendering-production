#!/usr/bin/env python3
"""
Test: No dangling composition references (2026-10-12)

ROOT CAUSE FIX: When a composition is deleted from the contract,
all references in tests, scripts, and workflows must also be removed.
This test fails if any deleted composition ID appears in:
- tests/
- .github/scripts/
- .github/workflows/

This prevents the "again and again" issues where deletions leave
dangling references that break CI later.
"""

import os
import re
import sys

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(REPO_ROOT, ".github", "scripts"))

from composition_contract import COMPOSITIONS

# Compositions that were deleted and must not be referenced anywhere
# Updated when a composition is deleted: add its ID here
DELETED_COMPOSITIONS = {
    "B6A", "B6B", "P3Rehearsal", "RecutVideo", "StressTest", "TrialVideo",
    "PipeTestVideo", "HysaTest", "BankTestVideo", "CalibrationV0", "CalibrationV1",
    "CalibrationV2", "CalibrationV3", "ModeRegression", "VisualShowcase",
    "VisualCalibration", "H1Hook", "HousingBroke", "ChainTest",
    # Test videos removed 2026-10-13 (Hamza: diagnostic fixtures, not production)
    "FromScratch", "FromScratchLight", "MoneyDying",
}

def test_no_dangling_composition_references():
    """Fail if any deleted composition ID is referenced in code."""
    violations = []
    
    # Directories to scan
    scan_dirs = [
        os.path.join(REPO_ROOT, "tests"),
        os.path.join(REPO_ROOT, ".github", "scripts"),
        os.path.join(REPO_ROOT, ".github", "workflows"),
    ]
    
    for scan_dir in scan_dirs:
        if not os.path.isdir(scan_dir):
            continue
        for root, dirs, files in os.walk(scan_dir):
            # Skip __pycache__
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for fname in files:
                if not fname.endswith((".py", ".yml", ".yaml")):
                    continue
                fpath = os.path.join(root, fname)
                rel = os.path.relpath(fpath, REPO_ROOT)
                # Skip this guard file itself (it lists deleted IDs intentionally)
                if "test_no_dangling" in fname:
                    continue
                try:
                    with open(fpath) as f:
                        content = f.read()
                except:
                    continue
                for comp_id in DELETED_COMPOSITIONS:
                    # Look for quoted references (not in comments explaining deletion)
                    pattern = rf'["\']{comp_id}["\']'
                    for i, line in enumerate(content.split("\n"), 1):
                        if re.search(pattern, line):
                            # Skip lines that mention "deleted" (documenting the deletion)
                            if "deleted" in line.lower():
                                continue
                            violations.append(f"{rel}:{i} references deleted '{comp_id}'")
    
    # Also verify deleted IDs are not in the contract
    for comp_id in DELETED_COMPOSITIONS:
        if comp_id in COMPOSITIONS:
            violations.append(f"composition_contract.py: '{comp_id}' still in COMPOSITIONS (should be deleted)")
    
    assert not violations, (
        f"Found {len(violations)} dangling references to deleted compositions:\n" +
        "\n".join(violations[:20]) +
        ("\n... and more" if len(violations) > 20 else "") +
        "\n\nROOT CAUSE: When deleting a composition, ALL references must be removed. "
        "Add the ID to DELETED_COMPOSITIONS in this file."
    )

if __name__ == "__main__":
    test_no_dangling_composition_references()
    print("PASS: No dangling composition references")
