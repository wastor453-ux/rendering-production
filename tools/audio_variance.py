#!/usr/bin/env python3
"""Deterministic audio variation engine for CrackIt Finance videos.

Every playback instance of a base asset gets subtle, seeded variations so
sequential elements never sound identical — no auditory fatigue, fully
reproducible (same seed -> same variant, every time).

Variations (all subtle, broadcast-safe):
  - Pitch shift:        -3% .. +3%  (asetrate, resampled back to 44.1k)
  - Low-pass ceiling:   16kHz .. 20kHz micro-adjust on the high end
  - Tail termination:   fade-out start shifted by up to ±10% of duration

Usage:
    from audio_variance import variance_filter, variance_params
    f = variance_filter(seed=7, dur=0.22)
    # -> "asetrate=44100*1.014,aresample=44100,lowpass=f=17832,afade=t=out:st=0.19:d=0.03"
    # apply inside an ffmpeg -af chain (before adelay positioning).

Seeds: use the event index within the timeline (stable across re-mixes).
"""
import hashlib
import random
import subprocess

_V1 = "audio-variance-v1"


def variance_params(seed: int) -> dict:
    """Deterministic per-seed variation parameters."""
    h = hashlib.sha256(f"{_V1}:{int(seed)}".encode()).digest()
    rng = random.Random(h)
    return {
        "pitch": 1.0 + rng.uniform(-0.03, 0.03),   # -3% .. +3%
        "lpf": rng.uniform(16000, 20000),           # Hz ceiling micro-adjust
        "tail": rng.uniform(-0.10, 0.10),          # ±10% tail shift (fraction)
    }


def probe_duration(path: str) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path],
        capture_output=True, text=True)
    return float(out.stdout.strip())


def variance_filter(seed: int, dur: float | None = None,
                    base_path: str | None = None) -> str:
    """ffmpeg -af fragment applying the seeded variation.

    Provide dur directly, or base_path to probe it.
    """
    p = variance_params(seed)
    if dur is None:
        if base_path is None:
            raise ValueError("need dur or base_path")
        dur = probe_duration(base_path)
    # tail: shift where the final fade begins by ±10% of duration
    fade_d = max(0.015, dur * 0.12)
    fade_st = max(0.0, dur * (0.88 + p["tail"]) - fade_d)
    parts = [
        f"asetrate=44100*{p['pitch']:.4f}",
        "aresample=44100",
        f"lowpass=f={p['lpf']:.0f}",
        f"afade=t=out:st={fade_st:.3f}:d={fade_d:.3f}",
    ]
    return ",".join(parts)


# Pools excluded from per-instance variance:
#  - drop/subhit: peak-timing critical (1-frame-before-cut law measures peaks
#    on the shaped file; pitch variance would shift peaks by ms).
#  - wheel: loop-size critical (aloop=size assumes exactly 0.5s; asetrate
#    would break seamless looping).
# These pools are already structurally unique (drops 9s apart, single beds).
EXCLUDED_POOLS = frozenset({"drop", "subhit", "wheel"})


def event_filter(pool: str, asset: str, seed: int, shaped_dir: str) -> str:
    """ffmpeg -af fragment for one event instance.

    Returns "" for excluded pools. Otherwise a deterministic per-seed
    variation chain to prepend before adelay positioning.
    Seed with the event index: stable across re-mixes.
    """
    if pool in EXCLUDED_POOLS:
        return ""
    import os
    base = os.path.join(shaped_dir, f"{asset}.wav")
    return variance_filter(seed, base_path=base)


if __name__ == "__main__":
    # self-test: determinism + bounds
    a = variance_params(7)
    b = variance_params(7)
    assert a == b, "not deterministic!"
    c = variance_params(8)
    assert a != c, "seeds collide!"
    assert 0.97 <= a["pitch"] <= 1.03
    assert 16000 <= a["lpf"] <= 20000
    assert -0.10 <= a["tail"] <= 0.10
    print("seed 7 ->", a)
    print("seed 8 ->", c)
    print("filter(seed=7, dur=0.22):", variance_filter(7, dur=0.22))
    print("SELF-TEST PASS")
