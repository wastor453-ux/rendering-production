#!/usr/bin/env python3
"""P4.4 §6.5: Frame-count correctness test — concat must not duplicate frames.

Proves that the assembly concat (stream copy) preserves exact frame counts
across chunk boundaries, including the shorter last chunk.

This test creates small synthetic H.264 chunks with ffmpeg, concatenates
them using the SAME command as the workflow, and verifies the decoded
frame count matches the sum of inputs.

Run: python3 tests/test_frame_count.py
Requires: ffmpeg, ffprobe in PATH
"""

import subprocess
import os
import tempfile
import sys


def run(cmd, **kwargs):
    result = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
    if result.returncode != 0:
        print(f"CMD FAILED: {' '.join(cmd)}", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    return result


def count_frames(video_path):
    """Count actual decoded frames using ffprobe (same as workflow)."""
    result = run([
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=nb_read_frames",
        "-of", "default=noprint_wrappers=1:nokey=1",
        "-count_frames", video_path
    ])
    return int(result.stdout.strip())


def make_test_chunk(path, frames, width=320, height=240, fps=30):
    """Create a synthetic H.264 chunk with exact frame count."""
    # Use testsrc2 for deterministic content
    run([
        "ffmpeg", "-y", "-v", "error",
        "-f", "lavfi", "-i", f"testsrc2=size={width}x{height}:rate={fps}:duration={frames/fps}",
        "-frames:v", str(frames),
        "-c:v", "libx264", "-crf", "18", "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        "-r", str(fps),
        path
    ])
    actual = count_frames(path)
    assert actual == frames, f"Chunk {path}: expected {frames}, got {actual}"
    return actual


def test_concat_preserves_frames():
    """Concat 5 chunks (including short last) → exact total, no duplicates."""
    print("Test: concat 5 chunks with stream copy → exact frame count...")
    with tempfile.TemporaryDirectory() as tmp:
        # 4 full chunks + 1 short last chunk (like the 39-chunk plan)
        chunk_frames = [60, 60, 60, 60, 23]  # Last is short
        expected_total = sum(chunk_frames)

        chunk_paths = []
        for i, nf in enumerate(chunk_frames):
            p = os.path.join(tmp, f"chunk_{i}.mp4")
            make_test_chunk(p, nf)
            chunk_paths.append(p)

        # Write concat list (same format as workflow)
        concat_list = os.path.join(tmp, "concat.txt")
        with open(concat_list, "w") as f:
            for i in range(len(chunk_paths)):
                f.write(f"file 'chunk_{i}.mp4'\n")

        # Concat with stream copy (P4.4 §6.5 fix)
        output = os.path.join(tmp, "master.mp4")
        run([
            "ffmpeg", "-y", "-v", "error",
            "-f", "concat", "-safe", "0", "-i", concat_list,
            "-c", "copy",
            output
        ])

        actual_total = count_frames(output)
        print(f"  Expected: {expected_total}, Actual: {actual_total}")
        assert actual_total == expected_total, \
            f"FRAME COUNT MISMATCH: expected {expected_total}, got {actual_total} " \
            f"({actual_total - expected_total} duplicates!)"

        print("  PASS: no duplicate frames, short last chunk handled correctly")


def test_concat_old_method_duplicates():
    """Demonstrate that re-encode CAN duplicate (documents the bug)."""
    print("Test: re-encode concat may duplicate (documents old bug)...")
    with tempfile.TemporaryDirectory() as tmp:
        chunk_frames = [60, 60, 60]
        expected_total = sum(chunk_frames)

        for i, nf in enumerate(chunk_frames):
            p = os.path.join(tmp, f"chunk_{i}.mp4")
            make_test_chunk(p, nf)

        concat_list = os.path.join(tmp, "concat.txt")
        with open(concat_list, "w") as f:
            for i in range(len(chunk_frames)):
                f.write(f"file 'chunk_{i}.mp4'\n")

        # OLD (buggy) method: re-encode during concat
        output = os.path.join(tmp, "master_old.mp4")
        run([
            "ffmpeg", "-y", "-v", "error",
            "-f", "concat", "-safe", "0", "-i", concat_list,
            "-c:v", "libx264", "-crf", "18", "-preset", "ultrafast",
            "-pix_fmt", "yuv420p",
            output
        ])

        actual_total = count_frames(output)
        print(f"  Expected: {expected_total}, Actual (re-encode): {actual_total}")
        # We don't assert failure here — just document the behavior.
        # On some ffmpeg versions this duplicates, on others it doesn't.
        if actual_total != expected_total:
            print(f"  INFO: re-encode duplicated {actual_total - expected_total} frames (confirms bug)")
        else:
            print("  INFO: re-encode did not duplicate on this ffmpeg version")
        print("  PASS: (informational)")


if __name__ == "__main__":
    print("=" * 60)
    print("P4.4 §6.5: Frame-Count Correctness Tests")
    print("=" * 60)
    try:
        test_concat_preserves_frames()
        test_concat_old_method_duplicates()
    except FileNotFoundError as e:
        print(f"SKIP: ffmpeg/ffprobe not in PATH ({e})")
        sys.exit(0)
    print("=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)
