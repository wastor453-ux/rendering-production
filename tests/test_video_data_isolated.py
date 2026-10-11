"""
test_video_data_isolated.py — Ensure videos use their own data, not another video's.

Prevents the "same cheap style" bug: a video that doesn't generate its own
data files must FAIL, not silently fall back to another video's data.
"""
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEOS_DIR = os.path.join(REPO_ROOT, "src", "videos")


def test_video_data_isolated():
    """Videos must not import data files from outside their own folder."""
    violations = []

    if not os.path.isdir(VIDEOS_DIR):
        return

    json_import_re = re.compile(r"""from\s+["']([^"']*\.json)["']""")

    for video_name in os.listdir(VIDEOS_DIR):
        if video_name.startswith("_"):
            continue
        video_dir = os.path.join(VIDEOS_DIR, video_name)
        if not os.path.isdir(video_dir):
            continue

        for root, dirs, files in os.walk(video_dir):
            for fname in files:
                if not fname.endswith((".tsx", ".ts")):
                    continue
                fpath = os.path.join(root, fname)
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                for m in json_import_re.finditer(content):
                    imp = m.group(1)
                    imp_dir = os.path.dirname(fpath)
                    resolved = os.path.normpath(os.path.join(imp_dir, imp))
                    video_abs = os.path.abspath(video_dir)
                    resolved_abs = os.path.abspath(resolved)

                    if not resolved_abs.startswith(video_abs):
                        if "schema" not in imp.lower():
                            rel = os.path.relpath(fpath, VIDEOS_DIR)
                            violations.append(rel + " imports data from outside: " + imp)

    assert not violations, (
        "Videos must use their own data files:\n"
        + "\n".join("  " + v for v in violations)
        + "\nEach video must generate its own data via the rule pipeline."
    )


if __name__ == "__main__":
    test_video_data_isolated()
    print("OK - All videos use isolated data")
