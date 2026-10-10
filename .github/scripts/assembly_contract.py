#!/usr/bin/env python3
"""Assembly/concat contract (BATCH 1, 2026-10-10).

THE CONTRACT (both assemble paths — render-production.yml AND
render-production-reassemble.yml — must obey it identically):

  1. EXACT FRAME-COUNT EQUALITY: sum(chunk frames) == master frames.
     The master frame-count gate (`[ "$FRAMES" = "$EXPECTED" ]`, measured
     with `ffprobe -count_frames`) is the end-to-end proof. Chunk frame
     ranges must tile [start_frame, end_frame] with no gaps and no overlaps.

  2. ENCODING METHOD, BOTH PATHS: `ffmpeg -f concat -safe 0 -i concat.txt
     -c copy` — stream copy, NEVER re-encode during concat.
     PROVEN (GitHub run 37942159718, assemble log): the re-encode variant
     (`-c:v libx264 -crf 18 -preset veryfast -pix_fmt yuv420p`) made ffmpeg
     report `dup=14` -> master had 23,165 frames vs 23,151 expected -> the
     frame-count gate failed and assembly died.
     Mechanism: Remotion chunk MP4s carry AAC audio with a 2048-sample
     priming edit list (see Remotion's `aac-priming.js`;
     2048/48000 = 0.042667s — the failing run's concat input line showed
     `start: -0.042667`). The audio track's media duration exceeds the video
     track's, so the concat demuxer offsets each segment by the audio-driven
     format duration, opening PTS gaps at chunk seams; with `-vsync cfr`
     (ffmpeg 7.x default on the runners) the encoder duplicates frames to
     fill the gaps. `-c copy` copies packets verbatim (no decode, no vsync),
     so the count is provably exact.
     Precondition (enforced by manifest.verify_assembly): every chunk's
     generation_fingerprint (codec + crf + remotion version) must match the
     job's, so all chunks are identically-encoded H.264 and stream copy is
     safe. Under `-c copy` the master gate verifies the TRUE end-to-end
     count; under re-encode, dups could even mask a short chunk.

  3. AUDIO CONTINUITY RULE: chunk audio streams are carried through concat
     (`-c copy` copies all streams) but are DROPPED at the mux step — both
     workflows map `-map 0:v -map "[aout]"`. The master audio is EXCLUSIVELY
     the canonical VO+bed mix. There is deliberately NO audio-continuity
     requirement across chunk seams; do not "fix" seam audio.

This module is the testable specification of that contract: pure functions,
no ffmpeg, no I/O. The workflows enforce it in bash; the tests in
tests/test_render_safety.py assert both.
"""

# Canonical concat command shared by both assemble paths.
CONCAT_DEMUXER_FLAGS = ["-f", "concat", "-safe", "0"]
CONCAT_VIDEO_CODEC = ["-c", "copy"]  # stream copy; NEVER libx264 here
FORBIDDEN_CONCAT_CODECS = ("libx264", "libx265", "mpeg4")

# Mux-step mapping: only the concatenated video + the canonical mix.
MUX_VIDEO_MAP = "0:v"
MUX_AUDIO_MAP = "[aout]"


def check_frame_ranges(chunks):
    """Verify chunk frame ranges tile exactly: sorted, contiguous, no
    gaps, no overlaps.

    chunks: iterable of {"chunk_id": int, "start": int, "end": int}
            (inclusive frame ranges, as in plan.chunks).
    Returns {"ok": bool, "errors": [str], "total_frames": int}.
    """
    errors = []
    items = sorted(chunks, key=lambda c: c["chunk_id"])
    if not items:
        return {"ok": False, "errors": ["no chunks"], "total_frames": 0}
    total = 0
    prev_end = None
    prev_id = None
    for c in items:
        cid, s, e = c["chunk_id"], c["start"], c["end"]
        if not isinstance(s, int) or not isinstance(e, int) or e < s:
            errors.append(f"chunk {cid}: invalid range [{s}, {e}]")
            continue
        if prev_end is not None:
            if s != prev_end + 1:
                if s <= prev_end:
                    errors.append(
                        f"chunk {cid}: overlaps chunk {prev_id} "
                        f"(starts {s}, previous ends {prev_end})")
                else:
                    errors.append(
                        f"chunk {cid}: gap after chunk {prev_id} "
                        f"(starts {s}, previous ends {prev_end}; "
                        f"missing frames {prev_end + 1}..{s - 1})")
        total += e - s + 1
        prev_end, prev_id = e, cid
    return {"ok": not errors, "errors": errors, "total_frames": total}


def check_master_frame_count(chunks, master_frames):
    """Verify sum(chunk frames) == master_frames (contract rule 1).

    Returns {"ok": bool, "errors": [str], "expected": int, "actual": int}.
    Deterministic: identical inputs always produce the identical verdict.
    """
    ranges = check_frame_ranges(chunks)
    expected = ranges["total_frames"]
    errors = list(ranges["errors"])
    if master_frames != expected:
        errors.append(
            f"frame count mismatch: sum(chunks)={expected} != "
            f"master={master_frames}")
    return {"ok": not errors, "errors": errors,
            "expected": expected, "actual": master_frames}
