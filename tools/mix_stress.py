#!/usr/bin/env python3
"""5-second stress-test mixer. Same laws as mix_master.py, parameterized:
pools with sequential draw, -4dB VO ducking (12-frame ramps), -1dB pre-encode
trim, deterministic manifest for verify-render.js.
"""
import json, subprocess, os, sys
import numpy as np

from audio_variance import event_filter

ROOT = os.path.expanduser("~/workspace/crackit")
PRO = os.path.join(ROOT, "demo-video/public/audio/sfx/pro")
SHAPED = os.path.join(PRO, "shaped")
AUD = os.path.join(ROOT, "demo-video/public/audio")
MANIFEST = os.path.join(ROOT, "audio_timeline_stress.json")
DUR = 5.0

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAILED:", " ".join(cmd[:6]), r.stderr[:400]); sys.exit(1)
    return r

def run_bin(cmd):
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        print("FAILED:", " ".join(cmd[:6]), r.stderr[:200]); sys.exit(1)
    return r.stdout

man = json.load(open(MANIFEST))

# ---- pools: localized, sequential draw ---------------------------------------
POOLS = {
    "pluck":  ["pluck", "pluck_alt"],
    "bell":   ["bell", "bell_alt"],
    "drop":   ["drop"],
    "snap":   ["snap", "snap_alt"],
    "wheel":  ["wheel"],
    "subhit": ["subhit"],
}
_pool_idx = {k: 0 for k in POOLS}
def draw(pool):
    a = POOLS[pool][_pool_idx[pool] % len(POOLS[pool])]
    _pool_idx[pool] += 1
    return a

# ---- VO (real TTS, placed per timeline, faded at the 5s boundary) ------------
print("== VO")
vo_file, vo_t = man["vo"]["file"], man["vo"]["placed_at_sec"]
run(["ffmpeg","-y","-v","error","-i",os.path.join(ROOT, vo_file),"-af",
     f"aresample=44100,adelay={int(vo_t*1000)}|{int(vo_t*1000)},"
     f"loudnorm=I=-16:TP=-1:LRA=11,aresample=44100,aformat=channel_layouts=stereo,"
     f"afade=t=out:st={DUR-0.2}:d=0.2,apad,atrim=0:{DUR}", f"{SHAPED}/vo_stress.wav"])
VO_SEGS = [tuple(s) for s in man["vo_segments"]]

# ---- SFX events via pool draw --------------------------------------------------
print("== SFX events")
ev = sorted(man["events"], key=lambda e: e["t"])
fc, inputs, n, labels = [], [], 0, []
for e in ev:
    pool, t = e["sfx"], e["t"]
    asset = draw(pool)
    e["asset"] = asset
    e["seed"] = n  # variance engine seed: stable across re-mixes
    # intrinsic variation: deterministic per-event-instance filter chain
    # (excluded pools return "" — see audio_variance.EXCLUDED_POOLS)
    vf = event_filter(pool, asset, n, SHAPED)
    chain = (vf + "," if vf else "") + f"adelay={int(t*1000)}|{int(t*1000)}"
    print(f"  t={t:.4f}s pool={pool} -> {asset} (seed {n}{' +variance' if vf else ''})")
    inputs += ["-i", f"{SHAPED}/{asset}.wav"]
    fc.append(f"[{n}]{chain}[s{n}]")
    labels.append(f"[s{n}]"); n += 1
fc.append("".join(labels)+f"amix=inputs={n}:normalize=0,aresample=44100,aformat=channel_layouts=stereo[sfx]")
run(["ffmpeg","-y","-v","error"]+inputs+["-filter_complex",";".join(fc),
     "-map","[sfx]",f"{SHAPED}/sfx_stress.wav"])

# ---- ambient with deterministic -4dB ducking -----------------------------------
print("== ambient + ducking")
R, DEPTH = 0.4, 1-10**(-4/20)
def ss(e0,e1):
    x = f"min(max((t-({e0}))/({e1}-({e0})),0),1)"
    return f"(({x})*({x})*(3-2*({x})))"
dips = []
for a,b in VO_SEGS:
    up, dn = ss(a-R,a), ss(b,b+R)
    dips.append(f"({up}*(1-{dn}))")
expr = f"1-{DEPTH}*({'+'.join(dips)})"
run(["ffmpeg","-y","-v","error","-i",f"{PRO}/pro-ambient.wav","-af",
     f"atrim=0:{DUR},asetpts=PTS-STARTPTS,aresample=44100,lowpass=f=400,volume=0.08,"
     f"aformat=channel_layouts=stereo,volume='{expr}':eval=frame", f"{SHAPED}/amb_stress.wav"])

# ---- master ----------------------------------------------------------------------
print("== master")
run(["ffmpeg","-y","-v","error","-i",f"{SHAPED}/vo_stress.wav","-i",f"{SHAPED}/sfx_stress.wav",
     "-i",f"{SHAPED}/amb_stress.wav","-filter_complex",
     "[0][1][2]amix=inputs=3:normalize=0,alimiter=limit=0.95,volume=0.891,"
     f"apad,atrim=0:{DUR}[m]","-map","[m]",f"{AUD}/stress-master.mp3"])
r = run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"{AUD}/stress-master.mp3"])
dur = float(r.stdout.strip())
raw = run_bin(["ffmpeg","-v","error","-i",f"{AUD}/stress-master.mp3","-af","aresample=44100","-f","f32le","-"])
a = np.frombuffer(raw, dtype=np.float32)
true_peak = float(20*np.log10(np.max(np.abs(a)))) if len(a) else 0.0
print(f"master duration: {dur}, true peak: {true_peak:.2f} dBFS")

manifest = {
    "version": "stress-v3",  # 2026-10-05: deterministic variation engine wired
    "video": "StressTest",
    "fps": 30,
    "duration_sec": DUR,
    "pools": POOLS,
    "scene_cuts_sec": man["scene_cuts_sec"],
    "vo_segments": VO_SEGS,
    "ducking": {"depth_db": -4, "ramp_frames": 12, "ramp_sec": 0.4},
    "stems": {"amb": "public/audio/sfx/pro/shaped/amb_stress.wav"},
    "laws": man.get("laws", {}),
    "layout": man.get("layout"),
    "events": [
        {"t": round(e["t"],4), "pool": e["sfx"], "asset": e["asset"],
         "seed": e.get("seed"),
         "anchor": e.get("anchor"), "why": e.get("why","")}
        for e in ev
    ],
    "master": {"file": "public/audio/stress-master.mp3",
               "duration_sec": dur, "true_peak_dbfs": round(true_peak,2)},
}
mpath = os.path.join(ROOT, "demo-video/audio_manifest_stress.json")
json.dump(manifest, open(mpath, "w"), indent=1)
print("manifest:", mpath)
print("DONE")
