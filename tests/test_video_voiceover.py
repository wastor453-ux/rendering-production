"""Enforce per-video voiceover isolation (Hamza 2026-10-12).

Each production video MUST have its own voiceover at:
  src/videos/{name}/audio/vo.wav

This prevents:
- Videos rendering without voiceover
- Videos sharing/reusing another video's voiceover
- Voiceover files accumulating in public/audio/

Exemptions: Videos in LEGACY_NO_VO_EXEMPT (pre-rule videos).
"""
import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEOS_DIR = os.path.join(REPO_ROOT, "src", "videos")

# Videos created before the voiceover rule (2026-10-12)
LEGACY_NO_VO_EXEMPT = {
    "moneydying",
    "finance-proof",
    "production-beats",
    "fromscratch",
    "fromscratch-light",
    "savings-trap",
    "compound-interest",  # Pipeline testing - VO to be added
}

class TestVideoVoiceover(unittest.TestCase):
    def test_each_video_has_own_voiceover(self):
        """Every non-exempt video must have src/videos/{name}/audio/vo.wav"""
        violations = []
        if not os.path.isdir(VIDEOS_DIR):
            self.skipTest("no videos directory")
        for name in sorted(os.listdir(VIDEOS_DIR)):
            video_dir = os.path.join(VIDEOS_DIR, name)
            if not os.path.isdir(video_dir):
                continue
            if name.startswith("_"):
                continue
            if name in LEGACY_NO_VO_EXEMPT:
                continue
            vo_path = os.path.join(video_dir, "audio", "vo.wav")
            if not os.path.isfile(vo_path):
                violations.append(
                    f"{name}: missing src/videos/{name}/audio/vo.wav - "
                    f"each video must have its own voiceover"
                )
        self.assertEqual(violations, [], "\n".join(violations))

    def test_no_shared_voiceover_in_public(self):
        """Videos must not reference public/audio/ voiceovers"""
        violations = []
        if not os.path.isdir(VIDEOS_DIR):
            self.skipTest("no videos directory")
        for name in sorted(os.listdir(VIDEOS_DIR)):
            video_dir = os.path.join(VIDEOS_DIR, name)
            if not os.path.isdir(video_dir) or name.startswith("_"):
                continue
            if name in LEGACY_NO_VO_EXEMPT:
                continue
            for root, dirs, files in os.walk(video_dir):
                for fn in files:
                    if fn.endswith((".tsx", ".ts", ".json")):
                        path = os.path.join(root, fn)
                        with open(path) as f:
                            content = f.read()
                        if "public/audio/" in content:
                            violations.append(
                                f"{path}: references public/audio/ - "
                                f"use video-local audio/ instead"
                            )
        self.assertEqual(violations, [], "\n".join(violations))

if __name__ == "__main__":
    unittest.main()
