"""
test_no_broken_imports.py — CI guard against dangling imports.

Prevents the H1Hook-class bug: a deleted file leaves a dangling import,
which breaks the entire Remotion webpack bundle and kills ALL renders.

This test scans every .tsx/.ts file in src/ for relative imports and
verifies each target exists. Fails CI if any import is broken.
"""
import os
import re

SRC_DIR = os.path.join(os.path.dirname(__file__), "..", "src")


def resolve_import(source_file, import_path):
    """Resolve a relative import to an actual file. Returns True if OK."""
    if not import_path.startswith("."):
        return True  # node_modules etc — skip

    source_dir = os.path.dirname(source_file)
    target_base = os.path.normpath(os.path.join(source_dir, import_path))

    for ext in [".tsx", ".ts", ".jsx", ".js"]:
        if os.path.isfile(target_base + ext):
            return True
    for ext in [".tsx", ".ts"]:
        if os.path.isfile(os.path.join(target_base, "index" + ext)):
            return True
    if os.path.isfile(target_base):
        return True
    return False


def test_no_broken_imports():
    broken = []
    import_re = re.compile(r'''from\s+["'](\.[^"']+)["']''')

    for root, dirs, files in os.walk(SRC_DIR):
        dirs[:] = [d for d in dirs if d != "node_modules"]
        for fname in files:
            if not fname.endswith((".tsx", ".ts")):
                continue
            fpath = os.path.join(root, fname)
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            for m in import_re.finditer(content):
                imp = m.group(1)
                if not resolve_import(fpath, imp):
                    rel = os.path.relpath(fpath, SRC_DIR)
                    broken.append(rel + " -> " + imp)

    assert not broken, (
        "Found %d broken import(s) that would kill the Remotion bundle:\n" % len(broken)
        + "\n".join("  " + b for b in broken)
        + "\nFix or remove these imports before merging."
    )


if __name__ == "__main__":
    test_no_broken_imports()
    print("OK - No broken imports found")


# --- Runtime-generated import contract -------------------------------------
# EventDriven statically imports files the render workflow generates
# (src/videos/_active/*). Those files do NOT exist as real data in Git,
# so a naive "file must exist" rule would fail every clean checkout
# (the test.yml python-tests failure). The structural contract is:
#   1. Checked-in STUBS make every static import resolve in any
#      checkout (bundle never dies on a missing file).
#   2. Stubs are visibly placeholders (never real video data), so a
#      render that forgets to generate fails closed downstream
#      (empty timeline -> validate_timeline + verify_provenance fail;
#      EventDrivenVideo reports "Timeline has zero events").
#   3. The render workflow generates (overwrites) every stub before
#      any bundling step.
# This test proves all three — it does not exempt the imports.

import json as _json
import wave as _wave

ACTIVE_DIR = os.path.join(SRC_DIR, "videos", "_active")
RUNTIME_GENERATED = {
    # import path (as written in EventDriven.tsx) -> stub file
    "./videos/_active/manifest.json": "manifest.json",
    "./videos/_active/timeline.json": "timeline.json",
    "./videos/_active/vo.wav": "vo.wav",
}
RENDER_WORKFLOW = os.path.join(
    os.path.dirname(__file__), "..", ".github", "workflows",
    "render-production.yml")


def test_runtime_generated_stubs_are_placeholders():
    """_active stubs exist, are placeholders, and the workflow generates them."""
    # 1. Stubs exist (so test_no_broken_imports can pass honestly).
    for _imp, _stub in RUNTIME_GENERATED.items():
        _p = os.path.join(ACTIVE_DIR, _stub)
        assert os.path.isfile(_p), (
            f"Missing runtime-generated stub: src/videos/_active/{_stub}. "
            f"Without it the Remotion bundle dies on a clean checkout.")
    # 2a. Manifest stub carries the placeholder marker, never real video data.
    with open(os.path.join(ACTIVE_DIR, "manifest.json")) as f:
        manifest = _json.load(f)
    assert manifest.get("videoId") == "__STUB__", (
        f"_active/manifest.json must be the __STUB__ placeholder, got "
        f"{manifest!r}. Real video data must never be committed here.")
    # 2b. Timeline stub has zero events (renders fail closed, never silently
    # use placeholder visuals).
    with open(os.path.join(ACTIVE_DIR, "timeline.json")) as f:
        timeline = _json.load(f)
    assert timeline.get("events") == [], (
        f"_active/timeline.json stub must have zero events, got "
        f"{len(timeline.get('events', []))} events.")
    # 2c. VO stub is a valid WAV but only a fraction of a second of silence
    # (a real VO committed here would be video-specific data in a generic path).
    with open(os.path.join(ACTIVE_DIR, "vo.wav"), "rb") as f:
        wav = _wave.open(f)
        try:
            duration = wav.getnframes() / wav.getframerate()
        finally:
            wav.close()
    assert 0 < duration < 1.0, (
        f"_active/vo.wav stub must be <1s of silence, got {duration:.2f}s.")
    # 3. The render workflow overwrites every stub before bundling
    # (both the plan-job prepare step and the per-worker prepare step).
    with open(RENDER_WORKFLOW) as f:
        workflow = f.read()
    for _imp, stub in RUNTIME_GENERATED.items():
        target = f"src/videos/_active/{stub}"
        assert target in workflow, (
            f"render-production.yml never generates {target}; "
            f"the stub would ship as real render data.")
