"""
Regression tests for the P4.4 audio duration guard.

Tests the guard logic in isolation (without requiring a GitHub runner).
Each test simulates a guard scenario with mocked ffprobe/file state.

The guard must:
- WARN (not fatal) for 181.6s video vs 180.565s VO (1.0s gap)
- FATAL for gap > 30s
- FATAL for missing audio
- FATAL with clear diagnostic for ffprobe failure/empty output
- FATAL for invalid numeric duration
- FATAL for LFS pointer files
"""
import os
import subprocess
import sys
import tempfile
import unittest


def run_guard(video_dur, vo_dur_str, vo_exists=True, is_lfs=False):
    """
    Simulate the guard logic in isolation.

    Returns: (exit_code, stdout, stderr)
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        vo_path = os.path.join(tmpdir, "test_vo.wav")

        if vo_exists:
            if is_lfs:
                # Write LFS pointer content
                with open(vo_path, "w") as f:
                    f.write("version https://git-lfs.github.com/spec/v1\n")
            else:
                # Write minimal WAV header (not valid audio, but exists)
                with open(vo_path, "wb") as f:
                    f.write(b"RIFF\x00\x00\x00\x00WAVEfmt ")

        # Build the guard script (mirrors workflow logic)
        script = f"""
set -euo pipefail
VIDEO_DUR={video_dur}
VO_FILE="{vo_path}"
VO_DUR_MOCK="{vo_dur_str}"

if [ ! -f "$VO_FILE" ]; then
  echo "FATAL: VO file not found: $VO_FILE" >&2
  exit 1
fi
if head -c 100 "$VO_FILE" | grep -q "version https://git-lfs.github.com"; then
  echo "FATAL: VO is a Git LFS pointer, not real audio: $VO_FILE" >&2
  exit 1
fi
# Simulate ffprobe: use mock value (empty string = ffprobe failed)
VO_DUR="$VO_DUR_MOCK"
if [ -z "$VO_DUR" ]; then
  echo "FATAL: ffprobe failed to read duration from $VO_FILE" >&2
  exit 1
fi
if ! python3 -c "float('$VO_DUR')" 2>/dev/null; then
  echo "FATAL: ffprobe returned invalid duration '$VO_DUR' for $VO_FILE" >&2
  exit 1
fi
echo "VO duration: ${{VO_DUR}}s ($VO_FILE)"
VIDEO_DUR="$VIDEO_DUR" VO_DUR="$VO_DUR" python3 -c "
import os, sys
video_dur = float(os.environ['VIDEO_DUR'])
vo_dur = float(os.environ['VO_DUR'])
gap = video_dur - vo_dur
if gap > 30:
    print(f'FATAL: VO too short', file=sys.stderr)
    sys.exit(1)
elif gap > 0:
    print(f'WARNING: VO slightly shorter (gap {{gap:.1f}}s)')
else:
    print(f'VO duration OK')
"
"""
        result = subprocess.run(
            ["bash", "-c", script],
            capture_output=True, text=True
        )
        return result.returncode, result.stdout, result.stderr


class TestAudioGuard(unittest.TestCase):
    def test_warning_not_fatal_for_small_gap(self):
        # 181.6s video, 180.565s VO → 1.035s gap → WARNING, exit 0
        code, out, err = run_guard(181.6, "180.565")
        self.assertEqual(code, 0, f"Should warn, not fail. stderr: {err}")
        self.assertIn("WARNING", out)

    def test_fatal_for_large_gap(self):
        # 181.6s video, 100s VO → 81.6s gap → FATAL, exit 1
        code, out, err = run_guard(181.6, "100.0")
        self.assertEqual(code, 1, "Gap > 30s must be fatal")
        self.assertIn("FATAL", err)

    def test_fatal_for_missing_audio(self):
        # VO file doesn't exist → FATAL, exit 1
        code, out, err = run_guard(181.6, "180.565", vo_exists=False)
        self.assertEqual(code, 1, "Missing audio must be fatal")
        self.assertIn("FATAL", err)
        self.assertIn("not found", err)

    def test_fatal_for_ffprobe_failure(self):
        # ffprobe returns empty → FATAL with diagnostic, exit 1
        code, out, err = run_guard(181.6, "")
        self.assertEqual(code, 1, "Empty ffprobe output must be fatal")
        self.assertIn("FATAL", err)
        self.assertIn("ffprobe failed", err)

    def test_fatal_for_invalid_duration(self):
        # ffprobe returns non-numeric → FATAL, exit 1
        code, out, err = run_guard(181.6, "not_a_number")
        self.assertEqual(code, 1, "Invalid duration must be fatal")
        self.assertIn("FATAL", err)
        self.assertIn("invalid duration", err)

    def test_fatal_for_lfs_pointer(self):
        # LFS pointer file → FATAL, exit 1
        code, out, err = run_guard(181.6, "180.565", is_lfs=True)
        self.assertEqual(code, 1, "LFS pointer must be fatal")
        self.assertIn("FATAL", err)
        self.assertIn("LFS pointer", err)

    def test_ok_for_matching_durations(self):
        # VO longer than video → OK, exit 0
        code, out, err = run_guard(181.6, "185.0")
        self.assertEqual(code, 0, f"Should pass. stderr: {err}")
        self.assertIn("OK", out)


if __name__ == "__main__":
    unittest.main()
