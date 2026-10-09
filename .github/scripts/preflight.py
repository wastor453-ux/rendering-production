#!/usr/bin/env python3
"""
Dependency preflight: check what's already installed before apt-get.

Reports for each required component:
  - present/missing
  - version (if present)
  - path (if present)

Exit 0 if everything required is present.
Exit 1 with an actionable error if something required is missing.

This script does NOT install anything — it only reports.
The workflow decides whether to run apt-get based on this output.
"""

import json
import os
import shutil
import subprocess
import sys


def run(cmd: list) -> tuple:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return r.returncode, (r.stdout + r.stderr).strip()
    except Exception as e:
        return 127, str(e)


def check_ffmpeg() -> dict:
    path = shutil.which("ffmpeg")
    if not path:
        return {"present": False}
    _, out = run(["ffmpeg", "-version"])
    version = out.split("\n")[0] if out else "unknown"
    return {"present": True, "path": path, "version": version[:80]}


def check_ffprobe() -> dict:
    path = shutil.which("ffprobe")
    if not path:
        return {"present": False}
    _, out = run(["ffprobe", "-version"])
    version = out.split("\n")[0] if out else "unknown"
    return {"present": True, "path": path, "version": version[:80]}


def check_chromium_libs(browser_path: str = None) -> dict:
    """Check that Chromium's required system libraries are loadable.

    If browser_path is provided, uses `ldd` on the actual binary as the
    GROUND TRUTH: a library reported as `=> /path` is resolved; only
    `=> not found` is missing. No ldconfig cross-check — ldd already proves
    resolvability (it accounts for RUNPATH, LD_LIBRARY_PATH, etc.), and
    ldconfig can disagree (stale cache), causing false "missing" reports.

    Otherwise falls back to the known requirements for Remotion 4.0.532's
    chrome-headless-shell (149.0.7790.0) on Ubuntu 24.04, checked via ldconfig.

    FAIL-CLOSED: If ldd fails (non-ELF, missing file, ldd error), returns
    present=False. An empty inventory is NEVER treated as verified.

    R-024: Full versioned SONAMEs preserved. Absolute-path entries normalized
    to basename. System libs filtered on the normalized name.
    """
    if browser_path:
        if not os.path.isfile(browser_path):
            return {"present": False, "missing": [], "checked": [],
                    "error": f"browser binary not found: {browser_path}"}
        code, out = run(["ldd", browser_path])
        if code != 0:
            return {"present": False, "missing": [], "checked": [],
                    "error": f"ldd failed on {browser_path} (exit {code}): "
                             f"not a valid executable"}
        if "not a dynamic executable" in out:
            return {"present": False, "missing": [], "checked": [],
                    "error": f"{browser_path} is not a dynamic executable"}
        # P3.9: ldd is ground truth. Parse each line:
        #   "libfoo.so.1 => /lib/.../libfoo.so.1 (0x...)" → resolved
        #   "libfoo.so.1 => not found" → missing
        #   "/lib64/ld-linux-x86-64.so.2 (0x...)" → absolute, resolved
        #   "linux-vdso.so.1 (0x...)" → vdso, always present
        resolved = set()
        unresolved = []
        for line in out.split('\n'):
            stripped = line.strip()
            if not stripped or ".so" not in stripped:
                continue
            if "not found" in stripped:
                unresolved.append(stripped.split()[0])
                continue
            # Extract the SONAME (first token, or basename if absolute)
            first = stripped.split()[0]
            soname = os.path.basename(first) if os.path.isabs(first) else first
            if ".so" not in soname:
                continue
            # Filter system libs on normalized basename
            if any(soname.startswith(p) for p in
                   ("libc.so", "libm.so", "libgcc_s", "libexpat",
                    "ld-linux", "linux-vdso", "libpthread", "libdl.",
                    "libdl-", "librt.so", "libstdc++")):
                continue
            # If "=>" present with a real path, it's resolved.
            # (ldd only prints "=>" for resolved libs; vdso/abs have no "=>".)
            resolved.add(soname)
        if unresolved:
            return {"present": False, "missing": sorted(set(unresolved)),
                    "checked": sorted(resolved),
                    "error": f"ldd reports unresolved: {sorted(set(unresolved))}"}
        if not resolved:
            return {"present": False, "missing": [], "checked": [],
                    "error": "ldd found no non-system dependencies; "
                             "cannot verify browser requirements"}
        # All resolved per ldd ground truth — no ldconfig needed.
        return {"present": True, "missing": [],
                "checked": sorted(resolved)}
    else:
        # Fallback: static list checked via ldconfig (no binary to inspect).
        required = [
            "libnspr4.so",
            "libnss3.so",
            "libatk-bridge-2.0.so.0",
            "libcups.so.2",
            "libdrm.so.2",
            "libxkbcommon.so.0",
            "libgbm.so.1",
        ]
        code, out = run(["ldconfig", "-p"])
        if code != 0:
            return {"present": False, "missing": required, "checked": required,
                    "error": "ldconfig failed"}
        import re
        missing = []
        for lib in required:
            if lib not in out:
                base = re.escape(lib)
                if not re.search(base + r'(\.\d+)*', out):
                    missing.append(lib)
        return {"present": not missing, "missing": missing,
                "checked": required}


def verify_browser_for_render(browser_path: str) -> dict:
    """Three-outcome contract for browser dependency verification.

    Inspects the ACTUAL browser executable (from `remotion browser ensure`)
    and classifies the result into exactly one outcome:

    - "verified": executable is valid and all required dynamic libraries
      are resolved. Safe to proceed to version recording and rendering.
    - "repairable": executable is valid, dependency inspection succeeded,
      but one or more required system libraries are missing. The caller
      should install packages and call this function again.
    - "unrepairable": executable is invalid or absent, dependency inspection
      itself failed (ldd error, ldconfig error), or the problem is not a
      missing-package problem. Caller must fail closed WITHOUT attempting
      package repair.

    This distinction matters: unresolved shared libraries reported by ldd
    are REPAIRABLE (install the package). A non-ELF binary or ldd failure
    is UNREPAIRABLE (apt-get cannot fix a corrupt binary).

    Returns dict with "outcome" key plus details:
      verified: {"outcome": "verified", "checked": [...], "binary": path}
      repairable: {"outcome": "repairable", "missing": [...], "checked": [...],
                   "binary": path}
      unrepairable: {"outcome": "unrepairable", "reason": "...", "binary": path}
    """
    if not browser_path or not isinstance(browser_path, str):
        return {"outcome": "unrepairable",
                "reason": f"invalid browser path: {browser_path!r}",
                "binary": browser_path}
    result = check_chromium_libs(browser_path)
    # Unrepairable: inspection itself failed
    # (missing binary, non-ELF, ldd error, ldconfig error, not dynamic)
    if "error" in result:
        err = result["error"]
        # Unresolved libraries are REPAIRABLE, not an inspection failure.
        # check_chromium_libs puts them in both "missing" and "error".
        # Reclassify: if there are missing libs and the binary was inspected,
        # it's repairable.
        if result.get("missing") and "unresolved" in err.lower():
            return {"outcome": "repairable",
                    "missing": result["missing"],
                    "checked": result.get("checked", []),
                    "binary": browser_path,
                    "detail": err}
        return {"outcome": "unrepairable",
                "reason": err,
                "binary": browser_path}
    # No error: inspection succeeded. Missing libs = repairable.
    if result.get("missing"):
        return {"outcome": "repairable",
                "missing": result["missing"],
                "checked": result.get("checked", []),
                "binary": browser_path}
    return {"outcome": "verified",
            "checked": result.get("checked", []),
            "binary": browser_path}


# R-021 (P3.8): ONE coherent validated package set for Ubuntu 24.04 (Noble).
# Used by both the initial preflight install and the browser-specific repair.
# Covers: NSS/NSPR (from real binary ldd), ATK, ATK-bridge, CUPS, DRM, XKB,
# X11 (composite/damage/fixes/randr), GBM, ALSA audio.
# All names verified against https://packages.ubuntu.com/noble/ (t64 transition).
# This is the single source of truth; the workflow must not define its own list.
BROWSER_PACKAGES = [
    "libnss3",
    "libnspr4",
    "libatk1.0-0t64",
    "libatk-bridge2.0-0t64",
    "libcups2t64",
    "libdrm2",
    "libxkbcommon0",
    "libxcomposite1",
    "libxdamage1",
    "libxfixes3",
    "libxrandr2",
    "libgbm1",
    "libasound2t64",
]


def check_node(expected: str) -> dict:
    path = shutil.which("node")
    if not path:
        return {"present": False}
    code, out = run(["node", "--version"])
    version = out.strip()
    return {
        "present": True,
        "path": path,
        "version": version,
        "matches_expected": version == f"v{expected}",
    }


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("node_version", nargs="?", default="24.20.0")
    parser.add_argument("--for", dest="role", choices=["render", "assemble"],
                        default="render",
                        help="render needs chromium libs; assemble needs ffmpeg")
    args = parser.parse_args()

    report = {
        "ffmpeg": check_ffmpeg(),
        "ffprobe": check_ffprobe(),
        "chromium_libs": check_chromium_libs(),
        "node": check_node(args.node_version),
    }
    print(json.dumps(report, indent=2))

    # Role-specific requirements:
    # - render: chromium system libs (node handled by setup-node)
    # - assemble: ffmpeg + ffprobe (no chromium needed)
    missing = []
    if args.role == "render":
        if not report["chromium_libs"]["present"]:
            missing.append(f"chromium libs: {report['chromium_libs']['missing']}")
    elif args.role == "assemble":
        if not report["ffmpeg"]["present"]:
            missing.append("ffmpeg")
        if not report["ffprobe"]["present"]:
            missing.append("ffprobe")

    if missing:
        print(f"\nPREFLIGHT FAIL: missing {missing}", file=sys.stderr)
        print("Action: run apt-get install for the missing components.", file=sys.stderr)
        return 1
    print("PREFLIGHT OK: all required components present.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
