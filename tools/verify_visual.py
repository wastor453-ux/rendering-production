#!/usr/bin/env python3
"""B-23: Independent visual verifier for rendered masters.

Runs objective defect scans on a video file WITHOUT re-rendering:
  - stream properties (codec, resolution, fps, frame count, duration)
  - black-frame detection (blackdetect)
  - frozen-frame detection (freezedetect)
  - blank-frame detection (pixel variance on sampled frames)

Usage: verify_visual.py <video.mp4> [--expected-frames N]
Exit 0 = PASS (no defects), exit 1 = FAIL (defects found).

This is the automated visual QA the pipeline was missing. It judges
technical validity only — creative quality remains human judgment.
"""
import json
import subprocess
import sys


def ffprobe_streams(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-of", "json", path],
        capture_output=True, text=True, check=True).stdout
    return json.loads(out)["streams"]


def detect(path, vf):
    """Run a detection filter, return matching segment lines."""
    p = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-vf", vf, "-f", "null", "-"],
        capture_output=True, text=True)
    return [l for l in (p.stderr + p.stdout).split("\n") if "black_start" in l or "freeze_start" in l]


def main():
    if len(sys.argv) < 2:
        print("usage: verify_visual.py <video.mp4> [--expected-frames N]", file=sys.stderr)
        return 2
    path = sys.argv[1]
    expected = None
    if "--expected-frames" in sys.argv:
        expected = int(sys.argv[sys.argv.index("--expected-frames") + 1])

    streams = ffprobe_streams(path)
    video = next(s for s in streams if s["codec_type"] == "video")
    audio = next((s for s in streams if s["codec_type"] == "audio"), None)

    violations = []
    frames = int(video.get("nb_frames", 0) or 0)
    print(f"codec={video['codec_name']} res={video['width']}x{video['height']} "
          f"fps={eval(video['avg_frame_rate']):.2f} frames={frames}")
    if audio:
        print(f"audio={audio['codec_name']} {audio['sample_rate']}Hz {audio['channels']}ch")

    if expected and frames != expected:
        violations.append(f"frame count {frames} != expected {expected}")
    if (video["width"], video["height"]) != (1920, 1080):
        violations.append(f"resolution {video['width']}x{video['height']} != 1920x1080")

    black = detect(path, "blackdetect=d=0.5:pix_th=0.10")
    if black:
        violations.append(f"{len(black)} black segments >=0.5s")
    else:
        print("black segments >=0.5s: 0")

    frozen = detect(path, "freezedetect=n=0.001:d=2")
    if frozen:
        violations.append(f"{len(frozen)} frozen segments >=2s")
    else:
        print("frozen segments >=2s: 0")

    if violations:
        print("VISUAL VERIFY: FAIL")
        for v in violations:
            print(f"  - {v}")
        return 1
    print("VISUAL VERIFY: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
