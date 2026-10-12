#!/usr/bin/env python3
"""
validate_typography.py — Typography and readability gates.

Enforces role-appropriate text sizes from canonical design tokens.
These are UNIVERSAL rules for all videos.

Canonical source: src/light/tokens.ts TYPE scale (1920x1080)
  hook:      52-76px, weight 700  (main headlines)
  heading:   30-42px, weight 600  (section titles)
  cardTitle: 22-28px, weight 600  (card titles)
  body:      18-22px, weight 400  (body text)
  axis:      16-18px, weight 500  (chart labels)

Absolute minimum: 14px (captions/footnotes only, use sparingly)

This validates the GENERIC RENDERER (EventDrivenVideo.tsx) with
fail-closed mandatory ranges. Other components are checked for
absolute minimum only.

Usage:
    python3 tools/validate_typography.py [--strict]

FAIL-CLOSED: violations → exit 1 (in --strict mode)
"""

import re
import sys
from pathlib import Path


# Canonical TYPE scale from src/light/tokens.ts (1920x1080)
TYPE_SCALE = {
    "hook":      {"min": 52, "max": 76},
    "heading":   {"min": 30, "max": 42},
    "cardTitle": {"min": 22, "max": 28},
    "body":      {"min": 18, "max": 22},
    "axis":      {"min": 16, "max": 18},
}

# Absolute minimum for any text
ABSOLUTE_MIN = 14


def check_generic_renderer(tsx_path):
    """
    Check EventDrivenVideo.tsx with fail-closed mandatory ranges.
    
    This is the generic renderer — all roles must be within spec.
    Prefers TYPE token usage over hardcoded numbers for explicit roles.
    """
    violations = []
    
    with open(tsx_path) as f:
        content = f.read()
    
    # Find all fontSize declarations with fontWeight context
    # Pattern matches: fontSize: NN ... fontWeight: WW (within 200 chars)
    pattern = r'fontSize:\s*(\d+)(.{0,200}?)fontWeight:\s*(\d+)'
    
    for m in re.finditer(pattern, content, re.DOTALL):
        size = int(m.group(1))
        weight = int(m.group(3))
        
        # Get line for reporting
        line_start = content.rfind('\n', 0, m.start()) + 1
        line_end = content.find('\n', m.end())
        line = content[line_start:line_end].strip()[:80]
        
        # Absolute minimum (fail-closed)
        if size < ABSOLUTE_MIN:
            violations.append(
                f"Font size {size}px below absolute minimum ({ABSOLUTE_MIN}px): {line}"
            )
            continue
        
        # Determine valid roles by weight, then check if size fits ANY
        valid_roles = []
        if weight >= 700:
            valid_roles = ["hook"]
        elif weight >= 600:
            valid_roles = ["heading", "cardTitle"]
        elif weight <= 500:
            valid_roles = ["body", "axis"]
        
        # Check if size fits at least one valid role (fail-closed)
        fits = False
        for role in valid_roles:
            spec = TYPE_SCALE[role]
            if spec["min"] <= size <= spec["max"]:
                fits = True
                break
        
        if valid_roles and not fits:
            ranges = ", ".join([f"{r} {TYPE_SCALE[r]['min']}-{TYPE_SCALE[r]['max']}px" for r in valid_roles])
            violations.append(
                f"Text at {size}px (weight {weight}) fits no valid role "
                f"({ranges}): {line}"
            )
    
    return violations


def check_absolute_minimum(tsx_path):
    """Check any TSX file for absolute minimum (fail-closed)."""
    violations = []
    
    with open(tsx_path) as f:
        content = f.read()
    
    pattern = r'fontSize:\s*(\d+)'
    for m in re.finditer(pattern, content):
        size = int(m.group(1))
        if size < ABSOLUTE_MIN:
            line_start = content.rfind('\n', 0, m.start()) + 1
            line_end = content.find('\n', m.end())
            line = content[line_start:line_end].strip()[:80]
            violations.append(
                f"{tsx_path.name}: Font size {size}px below absolute minimum: {line}"
            )
    
    return violations


def check_explicit_roles():
    """Verify EventDrivenVideo uses explicit role components, not weight inference."""
    with open("src/light/EventDrivenVideo.tsx") as f:
        content = f.read()
    # Must import from Typography
    if "from \"./Typography\"" not in content and "from './Typography'" not in content:
        print("FATAL: EventDrivenVideo must import explicit role components from ./Typography", file=sys.stderr)
        sys.exit(1)
    # Must use Hook, CardTitle, etc. (not just TYPE tokens)
    roles_used = []
    for role in ["Hook", "Heading", "CardTitle", "Body", "Axis"]:
        if f"<{role}" in content:
            roles_used.append(role)
    if not roles_used:
        print("FATAL: EventDrivenVideo uses no explicit role components", file=sys.stderr)
        sys.exit(1)
    print(f"✅ Explicit roles used: {', '.join(roles_used)}")

def main():
    check_explicit_roles()
    strict = "--strict" in sys.argv
    
    light_dir = Path(__file__).parent.parent / "src" / "light"
    generic_renderer = light_dir / "EventDrivenVideo.tsx"
    
    if not generic_renderer.exists():
        print(f"FATAL: {generic_renderer} not found", file=sys.stderr)
        sys.exit(1)
    
    # 1. Generic renderer: fail-closed mandatory ranges
    print("Checking generic renderer (EventDrivenVideo.tsx)...", file=sys.stderr)
    violations = check_generic_renderer(generic_renderer)
    
    # 2. All components: absolute minimum only
    print("Checking absolute minimum across all components...", file=sys.stderr)
    for tsx_path in sorted(light_dir.glob("*.tsx")):
        if tsx_path == generic_renderer:
            continue  # Already checked above
        violations.extend(check_absolute_minimum(tsx_path))
    
    if violations:
        print(f"❌ TYPOGRAPHY VIOLATIONS ({len(violations)}):", file=sys.stderr)
        for v in violations:
            print(f"   • {v}", file=sys.stderr)
        if strict:
            sys.exit(1)
    else:
        print(f"✅ Typography check passed", file=sys.stderr)


if __name__ == "__main__":
    main()
