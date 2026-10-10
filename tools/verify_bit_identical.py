#!/usr/bin/env python3
"""
B-20: Bit-identical render verification.
Compares two render outputs frame-by-frame.

Usage: python3 tools/verify_bit_identical.py <render1.mp4> <render2.mp4>

Exit 0 = identical. Exit 1 = differences found (with details).
"""
import subprocess
import sys
import hashlib


def frame_hashes(video_path):
    """Extract per-frame MD5 hashes using ffmpeg."""
    cmd = [
        "ffmpeg", "-v", "error",
        "-i", video_path,
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-"
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    # Get dimensions
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,nb_frames",
         "-of", "csv=p=0", video_path],
        capture_output=True, text=True
    )
    w, h, n = map(int, probe.stdout.strip().split(","))
    frame_size = w * h * 3

    hashes = []
    while True:
        data = proc.stdout.read(frame_size)
        if len(data) < frame_size:
            break
        hashes.append(hashlib.md5(data).hexdigest())
    proc.wait()
    return hashes


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <render1.mp4> <render2.mp4>")
        sys.exit(2)

    h1 = frame_hashes(sys.argv[1])
    h2 = frame_hashes(sys.argv[2])

    print(f"Render 1: {len(h1)} frames")
    print(f"Render 2: {len(h2)} frames")

    if len(h1) != len(h2):
        print(f"FAIL: frame count mismatch ({len(h1)} vs {len(h2)})")
        sys.exit(1)

    diffs = [i for i, (a, b) in enumerate(zip(h1, h2)) if a != b]
    if diffs:
        print(f"FAIL: {len(diffs)} frames differ. First 10: {diffs[:10]}")
        sys.exit(1)

    print("PASS: renders are bit-identical")
    sys.exit(0)


if __name__ == "__main__":
    main()
