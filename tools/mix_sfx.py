#!/usr/bin/env python3
"""
mix_sfx.py — A1 SFX mix for Astor Legacy (LOCAL ONLY).

Consumes:
  --triggers    sfx_triggers.json (from tools/compile_sfx_triggers_a1.py;
                schema "astor-legacy-sfx-triggers-v1")
  --a1-manifest assets/a1/MANIFEST.json   (A1 membership = the ONLY allowed source)
  --a1-dir      assets/a1                 (filenames resolved via recursive index)
  --vo          VO wav (master anchor; NEVER ducked, NEVER moved)
  --bed         music bed mp3
  --video       optional master mp4 (muxes mixed audio under it, -c:v copy)

Sound laws (SOUND_DESIGN.md + standing rules):
  - VO is the master anchor: never ducked, never shifted.
  - SFX whose body overlaps active VO: -4dB (isolated ducking envelope).
  - Priority VO > Impact > Whoosh > Pop > Click > Data > Ambient.
    Overlapping SFX: the lower-priority hit takes -3dB.
  - Anti-fatigue: >=12 frames between repetitive clicks; <=2 one-shots
    per 1.0s window. Violations FAIL CLOSED (never silently dropped).
  - Bed: 16dB below VO RMS (midpoint of the 14-18dB law), looped.
  - Master targets: -14 LUFS +/-1, true peak <= -1 dBTP (loudnorm).
  - A1 ONLY. Legacy pools (pro/Sonniss/drop/subhit/pluck/snap/bell/wheel/
    ambient/cinematic) are forbidden — enforced by manifest membership.

Modes:
  --dry-run        validate everything, print the ffmpeg filter graph,
                   write NO audio.
  --test-seconds N render only the first N seconds (chain validation).

Fail-closed: missing triggers/assets, schema violations, timing violations,
unresolvable A1 assets, or ffmpeg errors all exit nonzero with no output.

LOCAL ONLY: not referenced by any active workflow path.
"""

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

FPS = 30
VO_DUCK_DB = -4.0          # SFX duck under active VO
PRIORITY_DUCK_DB = -3.0    # lower-priority SFX when overlapping a higher one
CLICK_BREATHING_FRAMES = 12
MAX_ONESHOTS_PER_SEC = 2
BED_BELOW_VO_DB = 16.0     # midpoint of the 14-18dB law
SILENCE_DB = -40.0
SILENCE_MIN_S = 0.3

# priority: lower number = higher priority (VO is 0, never ducked)
PRIORITY = {"Impact": 1, "Whoosh": 2, "Pop": 3, "Click": 4, "Data": 5, "Ambient": 6}

# base gain per role family, dB (from SOUND_DESIGN.md family table;
# Impact = redesigned restraint hits, staged at Money level)
ROLE_GAIN_DB = {
    "Impact": -12.0,
    "Whoosh": -14.0,
    "Pop": -14.0,
    "Click": -20.0,
    "Data": -12.0,
    "Ambient": -20.0,
}

# approved_role -> priority class
ROLE_CLASS = {
    "deep boom": "Impact", "low boom": "Impact", "deep hit": "Impact",
    "impact hit": "Impact", "low thud": "Impact", "warm hit": "Impact",
    "soft whoosh": "Whoosh",
    "UI click": "Click", "soft final tick": "Click",
    "money sound": "Data", "money tick": "Data", "data tick": "Data",
}

CLICK_ROLES = {"Click"}


class Fail(Exception):
    pass


def run(cmd, **kw):
    p = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if p.returncode != 0:
        raise Fail(f"command failed ({p.returncode}): {' '.join(cmd[:4])}\n{p.stderr[-2000:]}")
    return p


def check_ffmpeg():
    if not shutil.which("ffmpeg"):
        raise Fail("ffmpeg not found on PATH")


def load_json(path, what):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise Fail(f"cannot load {what} {path}: {e}")


def index_a1(a1_dir):
    """Recursive {filename: abspath} index of WAVs under a1_dir."""
    idx = {}
    for root, _, files in os.walk(a1_dir):
        for f in files:
            if f.lower().endswith(".wav"):
                if f in idx:
                    raise Fail(f"duplicate A1 filename: {f}")
                idx[f] = os.path.join(root, f)
    if not idx:
        raise Fail(f"no WAVs found under {a1_dir}")
    return idx


def validate_triggers(doc):
    if doc.get("schema") != "astor-legacy-sfx-triggers-v1":
        raise Fail(f"unexpected triggers schema: {doc.get('schema')!r}")
    trigs = doc.get("triggers")
    if not isinstance(trigs, list) or not trigs:
        raise Fail("triggers list is empty or missing")
    required = {"event_id", "asset", "trigger_s", "trigger_frame",
                "visual_impact_frame", "peak_time_s"}
    for t in trigs:
        missing = required - set(t.keys())
        if missing:
            raise Fail(f"trigger {t.get('event_id', '?')}: missing {sorted(missing)}")
        if not isinstance(t["trigger_s"], (int, float)) or t["trigger_s"] < 0:
            raise Fail(f"trigger {t['event_id']}: bad trigger_s {t['trigger_s']!r}")
    return trigs


def resolve_assets(trigs, a1_manifest, a1_idx):
    """Every trigger asset must exist in the A1 manifest AND on disk. A1-only."""
    by_name = {a["filename"]: a for a in a1_manifest["assets"]}
    resolved = []
    for t in trigs:
        fn = t["asset"]
        a = by_name.get(fn)
        if a is None:
            raise Fail(f"trigger {t['event_id']}: asset {fn!r} NOT in A1 manifest "
                       f"(A1-only; legacy pools forbidden)")
        path = a1_idx.get(fn)
        if path is None:
            raise Fail(f"trigger {t['event_id']}: asset {fn!r} not found under a1 dir")
        resolved.append((t, a, path))
    return resolved


def check_antifatigue(trigs, role_of):
    """12-frame click breathing room; <=2 one-shots per 1.0s window. Fail closed."""
    ordered = sorted(trigs, key=lambda t: t["trigger_s"])
    # click breathing room
    last_click = None
    for t in ordered:
        if role_of(t) in CLICK_ROLES:
            if last_click is not None:
                gap_f = round((t["trigger_s"] - last_click) * FPS)
                if gap_f < CLICK_BREATHING_FRAMES:
                    raise Fail(
                        f"anti-fatigue: clicks {gap_f}f apart (< {CLICK_BREATHING_FRAMES}f): "
                        f"{t['event_id']}")
            last_click = t["trigger_s"]
    # density cap
    for i, t in enumerate(ordered):
        n = sum(1 for u in ordered if 0 <= u["trigger_s"] - t["trigger_s"] < 1.0)
        if n > MAX_ONESHOTS_PER_SEC:
            raise Fail(f"anti-fatigue: {n} one-shots in 1.0s window at "
                       f"{t['trigger_s']}s (max {MAX_ONESHOTS_PER_SEC})")


def vo_active_intervals(vo_path):
    """Active (non-silent) VO intervals via silencedetect. Returns [(start, end)]."""
    p = run(["ffmpeg", "-hide_banner", "-i", vo_path,
             "-af", f"silencedetect=noise={SILENCE_DB}dB:d={SILENCE_MIN_S}",
             "-f", "null", "-"])
    silences = []
    cur_start = None
    for line in p.stderr.splitlines():
        m = re.search(r"silence_start: ([\d.]+)", line)
        if m:
            cur_start = float(m.group(1))
        m = re.search(r"silence_end: ([\d.]+)", line)
        if m and cur_start is not None:
            silences.append((cur_start, float(m.group(1))))
            cur_start = None
    dur = media_duration(vo_path)
    active, pos = [], 0.0
    for s, e in sorted(silences):
        if s > pos:
            active.append((pos, s))
        pos = max(pos, e)
    if pos < dur:
        active.append((pos, dur))
    return active


def mean_volume(path):
    p = run(["ffmpeg", "-hide_banner", "-i", path,
             "-af", "volumedetect", "-f", "null", "-"])
    m = re.search(r"mean_volume: ([-\d.]+) dB", p.stderr)
    if not m:
        raise Fail(f"could not measure mean_volume of {path}")
    return float(m.group(1))


def media_duration(path):
    p = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", path])
    return float(p.stdout.strip())


def overlaps(a0, a1, b0, b1):
    return a0 < b1 and b0 < a1


def compute_gains(trigs, role_of, active_vo, durations):
    """Per-SFX final gain in dB: base role gain, -4dB under VO, -3dB priority."""
    gains = {}
    for t in trigs:
        role = role_of(t)
        g = ROLE_GAIN_DB[role]
        t0, t1 = t["trigger_s"], t["trigger_s"] + durations[t["event_id"]]
        # VO duck: peak moment inside active VO -> -4dB
        peak_s = t["trigger_s"] + t["peak_time_s"]
        if any(s <= peak_s < e for s, e in active_vo):
            g += VO_DUCK_DB
        # priority duck vs overlapping SFX
        my_prio = PRIORITY[role]
        for u in trigs:
            if u["event_id"] == t["event_id"]:
                continue
            u0, u1 = u["trigger_s"], u["trigger_s"] + durations[u["event_id"]]
            if overlaps(t0, t1, u0, u1) and PRIORITY[role_of(u)] < my_prio:
                g += PRIORITY_DUCK_DB
                break
        gains[t["event_id"]] = round(g, 2)
    return gains


def build_filtergraph(n_sfx, bed_gain_db, gains_db, triggers, durations, mix_dur):
    """Deterministic ffmpeg filter graph. Returns (filter_complex, map_label)."""
    parts = ["[0:a]aresample=48000,asetnsamples=n=1024:p=0[vo]"]
    parts.append(
        f"[1:a]aresample=48000,aloop=loop=-1:size=2147483647,"
        f"atrim=0:{mix_dur:.3f},volume={bed_gain_db:.2f}dB[bed]")
    sfx_labels = []
    for i, t in enumerate(triggers):
        ms = int(round(t["trigger_s"] * 1000))
        g = gains_db[t["event_id"]]
        lbl = f"sfx{i}"
        parts.append(
            f"[{i + 2}:a]aresample=48000,atrim=0:{durations[t['event_id']]:.3f},"
            f"adelay={ms}|{ms},volume={g:.2f}dB[{lbl}]")
        sfx_labels.append(f"[{lbl}]")
    ins = "[vo][bed]" + "".join(sfx_labels)
    parts.append(
        f"{ins}amix=inputs={2 + n_sfx}:duration=first:normalize=0[mix]")
    parts.append("[mix]loudnorm=I=-14:TP=-1.0:LRA=11:print_format=none,aresample=48000[out]")
    return ";".join(parts), "[out]"


def main():
    ap = argparse.ArgumentParser(description="A1 SFX mix (LOCAL ONLY)")
    ap.add_argument("--triggers", required=True)
    ap.add_argument("--a1-manifest", default="assets/a1/MANIFEST.json")
    ap.add_argument("--a1-dir", default="assets/a1")
    ap.add_argument("--vo", required=True)
    ap.add_argument("--bed", required=True)
    ap.add_argument("--video", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--fps", type=int, default=FPS)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--test-seconds", type=float, default=None)
    a = ap.parse_args()

    check_ffmpeg()
    if not a.dry_run and not a.out:
        raise Fail("--out is required unless --dry-run")

    doc = load_json(a.triggers, "triggers")
    trigs = validate_triggers(doc)
    manifest = load_json(a.a1_manifest, "A1 manifest")
    a1_idx = index_a1(a.a1_dir)
    resolved = resolve_assets(trigs, manifest, a1_idx)

    # role_of: staged approved_role if present in trigger doc, else classify
    # from asset category/filename (fail closed on unknown)
    def role_of(t):
        r = t.get("approved_role")
        if r and r in ROLE_CLASS:
            return ROLE_CLASS[r]
        # fallback: classify from A1 category
        by_name = {x["filename"]: x for x in manifest["assets"]}
        cat = (by_name[t["asset"]].get("category") or "").lower()
        for key, cls in (("impact", "Impact"), ("whoosh", "Whoosh"), ("swipe", "Whoosh"),
                         ("pop", "Pop"), ("click", "Click"), ("coin", "Data"), ("money", "Data"),
                         ("tick", "Click"), ("chime", "Pop"), ("notification", "Pop")):
            if key in cat or key in t["asset"].lower():
                return cls
        raise Fail(f"trigger {t['event_id']}: cannot classify role for "
                   f"asset {t['asset']!r} (category {cat!r})")

    for t, _, _ in resolved:
        role_of(t)  # fail closed on unclassifiable

    check_antifatigue(trigs, role_of)

    for pth, what in ((a.vo, "VO"), (a.bed, "bed")):
        if not os.path.isfile(pth):
            raise Fail(f"{what} not found: {pth}")
    if a.video and not os.path.isfile(a.video):
        raise Fail(f"video not found: {a.video}")

    durations = {}
    for t, _, path in resolved:
        durations[t["event_id"]] = media_duration(path)

    active_vo = vo_active_intervals(a.vo)
    vo_db = mean_volume(a.vo)
    bed_db = mean_volume(a.bed)
    bed_gain = round((vo_db - BED_BELOW_VO_DB) - bed_db, 2)

    gains = compute_gains([t for t, _, _ in resolved], role_of, active_vo, durations)

    mix_dur = media_duration(a.video) if a.video else media_duration(a.vo)
    if a.test_seconds:
        mix_dur = min(mix_dur, a.test_seconds)

    fc, out_lbl = build_filtergraph(len(trigs), bed_gain, gains,
                                    [t for t, _, _ in resolved], durations, mix_dur)

    print("=== MIX PLAN (A1-only, fail-closed) ===")
    print(f"triggers: {len(trigs)}  VO-active regions: {len(active_vo)}")
    print(f"VO mean {vo_db:.1f} dB | bed mean {bed_db:.1f} dB -> bed gain {bed_gain:+.2f} dB "
          f"(target {BED_BELOW_VO_DB:.0f}dB below VO)")
    for t, _, _ in resolved:
        duck = "VO-DUCK" if gains[t["event_id"]] < ROLE_GAIN_DB[role_of(t)] else "      "
        print(f"  {duck} {t['event_id']:12s} t={t['trigger_s']:7.3f}s "
              f"{t['asset']:40s} gain {gains[t['event_id']]:+.2f}dB [{role_of(t)}]")
    print("=== FILTER GRAPH ===")
    print(fc)

    if a.dry_run:
        print("DRY RUN: no audio written.")
        return 0

    cmd = ["ffmpeg", "-hide_banner", "-y", "-i", a.vo, "-i", a.bed]
    for _, _, path in resolved:
        cmd += ["-i", path]
    if a.video:
        cmd += ["-i", a.video]
        v_idx = 2 + len(resolved)
        cmd += ["-filter_complex", fc, "-map", f"{v_idx}:v", "-c:v", "copy",
                "-map", out_lbl, "-c:a", "aac", "-b:a", "192k"]
    else:
        cmd += ["-filter_complex", fc, "-map", out_lbl]
    if a.test_seconds:
        cmd += ["-t", str(a.test_seconds)]
    cmd += [a.out]
    print("=== RENDERING ===")
    run(cmd)
    print(f"WROTE {a.out}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Fail as e:
        print(f"MIX FAIL: {e}", file=sys.stderr)
        sys.exit(2)
