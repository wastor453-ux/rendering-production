#!/usr/bin/env python3
"""
align_vo.py — Canonical VO alignment stage for the generic production pipeline.

Uses faster-whisper (locked to .venv) with the local pinned model to generate
word-level timestamps from a video's own voiceover audio.

This is a PIPELINE STAGE, not a manual experiment. It takes explicit paths,
validates inputs, and produces a durable alignment JSON in the video's data
directory.

Usage:
    python3 tools/align_vo.py <vo.wav> <output_alignment.json> [--model base]

Inputs:
    vo.wav: Path to the video's voiceover audio (WAV format)
    output_alignment.json: Destination for word-level alignment

Output schema:
    {
        "source_audio": "<path>",
        "source_sha256": "<hash>",
        "model": "faster-whisper-base (local)",
        "words": [
            {"word": "...", "start": 0.0, "end": 0.5, "probability": 0.95},
            ...
        ],
        "word_count": 348,
        "duration_s": 112.6
    }

FAIL-CLOSED:
    - Missing audio file → exit 1
    - Empty audio → exit 1
    - Zero words transcribed → exit 1
    - Model not available → exit 1
"""

import json
import sys
import hashlib
from pathlib import Path


def sha256_file(path):
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <vo.wav> <output_alignment.json> [--model base]")
        print(f"  Aligns a video's voiceover using faster-whisper (pipeline stage)")
        sys.exit(1)

    vo_path = sys.argv[1]
    output_path = sys.argv[2]

    # Validate input
    vo_file = Path(vo_path)
    if not vo_file.exists():
        print(f"FATAL: VO audio not found: {vo_path}", file=sys.stderr)
        print(f"  Each video must supply its own voiceover.", file=sys.stderr)
        sys.exit(1)

    if vo_file.stat().st_size == 0:
        print(f"FATAL: VO audio is empty: {vo_path}", file=sys.stderr)
        sys.exit(1)

    # Compute source hash for provenance
    print(f"Computing SHA-256 of {vo_path}...", file=sys.stderr)
    audio_hash = sha256_file(vo_path)
    print(f"  SHA-256: {audio_hash[:16]}...", file=sys.stderr)

    # Load faster-whisper
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print(f"FATAL: faster-whisper not available.", file=sys.stderr)
        print(f"  Use the locked pipeline venv: ~/workspace/crackit/demo-video/.venv", file=sys.stderr)
        sys.exit(1)

    # Use local pinned model (no download)
    import os
    model_path = os.path.expanduser(
        "~/.cache/huggingface/hub/models--Systran--faster-whisper-base"
        "/snapshots/ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66"
    )
    if not os.path.exists(model_path):
        print(f"FATAL: Local whisper model not found: {model_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading faster-whisper model...", file=sys.stderr)
    # Monkeypatch for PyAV compatibility (workspace quirk)
    import av
    _orig_open = av.open
    def _patched_open(*args, **kwargs):
        kwargs.pop("metadata_errors", None)
        return _orig_open(*args, **kwargs)
    av.open = _patched_open

    model = WhisperModel(model_path, device="cpu", compute_type="int8")

    print(f"Transcribing {vo_path}...", file=sys.stderr)
    segments, info = model.transcribe(str(vo_file), word_timestamps=True)

    words = []
    for segment in segments:
        for w in segment.words:
            words.append({
                "word": w.word.strip(),
                "start": round(w.start, 3),
                "end": round(w.end, 3),
                "probability": round(w.probability, 3),
            })

    # Fail-closed: zero words
    if not words:
        print(f"FATAL: Transcription produced zero words.", file=sys.stderr)
        print(f"  Check that the audio contains speech.", file=sys.stderr)
        sys.exit(1)

    # Build output
    duration = max(w["end"] for w in words) if words else 0
    output = {
        "source_audio": str(vo_path),
        "source_sha256": audio_hash,
        "model": "faster-whisper-base (local pinned)",
        "words": words,
        "word_count": len(words),
        "duration_s": round(duration, 3),
    }

    # Write output
    with open(output_path, "w") as f:
        json.dump(output, f, indent=1)

    mean_prob = sum(w["probability"] for w in words) / len(words)
    print(f"✅ Aligned {len(words)} words (mean confidence: {mean_prob:.3f})", file=sys.stderr)
    print(f"   Duration: {duration:.1f}s", file=sys.stderr)
    print(f"   Output: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
