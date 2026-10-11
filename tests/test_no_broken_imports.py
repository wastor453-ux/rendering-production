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
