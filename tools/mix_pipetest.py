#!/usr/bin/env python3
"""Master-audio builder for the PipeTest pipeline stress video.
New-bench pools (curated Sonniss 2026) + deterministic variation engine.
Reads ~/workspace/crackit/audio_timeline_pipetest.json.
"""
import json, subprocess, os, sys, math
import numpy as np

ROOT = os.path.expanduser("~/workspace/crackit")
PRO = os.path.join(ROOT, "demo-video/public/audio/sfx/pro")
SHAPED = os.path.join(PRO, "shaped")
AUD = os.path.join(ROOT, "demo-video/public/audio")
MANIFEST = os.path.join(ROOT, "audio_timeline_pipetest.json")
sys.path.insert(0, os.path.join(ROOT, "demo-video/tools"))
from audio_variance import event_filter

def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        print("FAILED:", " ".join(cmd[:6]), r.stderr[:400]); sys.exit(1)
    return r

def run_bin(cmd):
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        print("FAILED:", " ".join(cmd[:6]), r.stderr[:200]); sys.exit(1)
    return r.stdout

def first_transient(path, thresh=0.15, backoff=0.005):
    data = run_bin(["ffmpeg","-v","error","-i",path,"-af",
                    "aresample=44100,aformat=channel_layouts=mono","-f","f32le","-"])
    a = np.frombuffer(data, dtype=np.float32)
    idx = np.where(np.abs(a) > thresh)[0]
    return max(0.0, float(idx[0])/44100 - backoff) if len(idx) else 0.0

def peak_pos_rel(path):
    """Peak position (sec) relative to file start."""
    data = run_bin(["ffmpeg","-v","error","-i",path,"-af",
                    "aresample=44100,aformat=channel_layouts=mono","-f","f32le","-"])
    a = np.frombuffer(data, dtype=np.float32)
    return float(np.argmax(np.abs(a))) / 44100 if len(a) else 0.0

# ---- 1. shape new-bench one-shots ---------------------------------------------
print("== shaping new-bench one-shots")
specs = {
    # plucks: high-pass 2kHz, -14dB (VO owns 150Hz-4kHz)
    "ppluck1": (f"{PRO}/plucks/pluck-01-soft-pop.wav",  "highpass=f=2000,loudnorm=I=-14:TP=-1.5:LRA=11"),
    "ppluck2": (f"{PRO}/plucks/pluck-02-ui-click.wav", "highpass=f=2000,loudnorm=I=-14:TP=-1.5:LRA=11"),
    "ppluck3": (f"{PRO}/plucks/pluck-04-button-blip.wav", "highpass=f=2000,loudnorm=I=-14:TP=-1.5:LRA=11"),
    # snaps: high-pass 2kHz, -14dB
    "psnap1": (f"{PRO}/snaps/snap-01-glassy.wav",      "highpass=f=2000,loudnorm=I=-14:TP=-1.5:LRA=11"),
    "psnap2": (f"{PRO}/snaps/snap-02-percussion.wav",  "highpass=f=2000,loudnorm=I=-14:TP=-1.5:LRA=11"),
    "psnap3": (f"{PRO}/snaps/snap-07-light-switch.wav","highpass=f=2000,loudnorm=I=-14:TP=-1.5:LRA=11"),
    "psnap4": (f"{PRO}/snaps/snap-09-card-flip.wav",   "highpass=f=2000,loudnorm=I=-14:TP=-1.5:LRA=11"),
}
peaks = {}
for name, (src, fc) in specs.items():
    ts = first_transient(src)
    trim = f"atrim=start={ts},asetpts=PTS-STARTPTS"
    out = f"{SHAPED}/{name}.wav"
    run(["ffmpeg","-y","-v","error","-i",src,"-af",
         f"{trim},{fc},aresample=44100,aformat=channel_layouts=stereo",out])
    peaks[name] = peak_pos_rel(out)
    print(f"  {name}: head-trimmed {ts:.3f}s, peak at {peaks[name]:.3f}s")

# drops: tight 2s cinematic hits, peak 0.3s in (low-pass 120Hz, -8dB per schematic)
drop_srcs = [
    f"{PRO}/sub_drops/sub-01-fast-drop.wav",
    f"{PRO}/sub_drops/sub-04-fast-drop-2.wav",
    f"{PRO}/sub_drops/sub-07-jump-drop.wav",
    f"{PRO}/sub_drops/sub-09-trailer-boom-a.wav",
    f"{PRO}/sub_drops/sub-12-metal-thud.wav",
]
for i, src in enumerate(drop_srcs, 1):
    name = f"pdrop{i}"
    # find absolute peak, cut a 2s window with peak 0.3s in
    data = run_bin(["ffmpeg","-v","error","-i",src,"-af",
                    "aresample=44100,aformat=channel_layouts=mono","-f","f32le","-"])
    a = np.frombuffer(data, dtype=np.float32)
    pk = float(np.argmax(np.abs(a))) / 44100
    ts = max(0.0, pk - 0.3)
    out = f"{SHAPED}/{name}.wav"
    run(["ffmpeg","-y","-v","error","-i",src,"-af",
         f"atrim=start={ts}:end={ts+2.0},asetpts=PTS-STARTPTS,"
         f"afade=t=in:st=0:d=0.05,lowpass=f=120,loudnorm=I=-8:TP=-1.5:LRA=11,"
         f"aresample=44100,aformat=channel_layouts=stereo",out])
    peaks[name] = 0.3
    print(f"  {name}: window [{ts:.2f},{ts+2.0:.2f}]s, peak at 0.300s")

# reuse proven shaped assets for bell + wheel
for b in ["bell", "bell_alt", "wheel"]:
    assert os.path.exists(f"{SHAPED}/{b}.wav"), f"missing shaped/{b}.wav"

POOLS = {
    "pluck": ["ppluck1", "ppluck2", "ppluck3"],
    "snap":  ["psnap1", "psnap2", "psnap3", "psnap4"],
    "bell":  ["bell", "bell_alt"],
    "drop":  ["pdrop1", "pdrop2", "pdrop3", "pdrop4", "pdrop5"],
    "wheel": ["wheel"],
}
_pool_idx = {k: 0 for k in POOLS}
def draw(pool):
    assets = POOLS[pool]
    a = assets[_pool_idx[pool] % len(assets)]
    _pool_idx[pool] += 1
    return a

# ---- 2. VO timeline ------------------------------------------------------------
man = json.load(open(MANIFEST))
CUTS = man["scene_cuts_sec"]
VO_FILES = man["vo_files"]
VO_OFF = man["vo_offsets"]
VO_SEGS = man["vo_segments"]
print("== VO timeline")
fc, inputs, n = [], [], 0
for f, t in zip(VO_FILES, VO_OFF):
    inputs += ["-i", f"{AUD}/pt/{f}"]
    fc.append(f"[{n}]aresample=44100,adelay={int(t*1000)}|{int(t*1000)}[v{n}]"); n += 1
fc.append("".join(f"[v{i}]" for i in range(n)) +
         f"amix=inputs={n}:normalize=0,loudnorm=I=-16:TP=-1:LRA=11,"
         f"aresample=44100,aformat=channel_layouts=stereo,apad,atrim=0:30[vo]")
run(["ffmpeg","-y","-v","error"]+inputs+["-filter_complex",";".join(fc),
     "-map","[vo]",f"{SHAPED}/vo_pt.wav"])

# ---- 3. SFX event bed -----------------------------------------------------------
print("== SFX events")
ev = [dict(e) for e in man["events"]]
# re-time cut drops: peak exactly 1 frame before the cut
drop_events = [e for e in ev if e["sfx"] == "drop" and "cut" in e]
assert len(drop_events) == len(CUTS), "drop/cut count mismatch"
for e, cut in zip(drop_events, CUTS):
    e["t"] = cut - 1/30 - 0.3
    print(f"  drop re-timed to {e['t']:.4f}s (peak {cut-1/30:.4f}s, 1f before {cut}s cut)")

fc, inputs, n, labels = [], [], 0, []
for idx, e in enumerate(ev):
    pool, t = e["sfx"], e["t"]
    asset = draw(pool)
    e["asset"] = asset
    e["seed"] = idx
    if pool == "wheel":
        dur = e["dur"]
        vel = e.get("vel", "quad-out")
        loops = math.ceil(dur/0.5)
        env = (f"min(t/0.08,1)*(0.35+0.65*max(0,1-(t-0.08)/({dur}-0.11)))"
               if vel == "quad-out" else f"min(t/0.08,1)*(0.35+0.65*pow(2,-10*(t-0.08)/({dur}-0.11)))")
        inputs += ["-i", f"{SHAPED}/wheel.wav"]
        fc.append(f"[{n}]aloop=loop={loops}:size=22050,atrim=0:{dur},asetpts=PTS-STARTPTS,"
                  f"volume='{env}':eval=frame,"
                  f"afade=t=out:st={dur-0.03}:d=0.03,"
                  f"adelay={int(t*1000)}|{int(t*1000)}[s{n}]")
    else:
        vf = event_filter(pool, asset, idx, SHAPED)  # deterministic variance
        chain = (vf + "," if vf else "") + f"adelay={int(t*1000)}|{int(t*1000)}"
        inputs += ["-i", f"{SHAPED}/{asset}.wav"]
        fc.append(f"[{n}]{chain}[s{n}]")
    labels.append(f"[s{n}]"); n += 1
    print(f"  t={t:.4f}s pool={pool:5s} -> {asset} (seed {idx}{' +variance' if pool not in ('drop','wheel') else ''})")
fc.append("".join(labels)+f"amix=inputs={n}:normalize=0,aresample=44100,aformat=channel_layouts=stereo[sfx]")
run(["ffmpeg","-y","-v","error"]+inputs+["-filter_complex",";".join(fc),
     "-map","[sfx]",f"{SHAPED}/sfx_pt.wav"])
print(f"  {n} events mixed")

# ---- 4. ambient bed with -4dB VO ducking -----------------------------------------
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
     f"atrim=0:30,asetpts=PTS-STARTPTS,aresample=44100,lowpass=f=400,volume=0.08,"
     f"aformat=channel_layouts=stereo,volume='{expr}':eval=frame", f"{SHAPED}/amb_pt.wav"])

# ---- 5. final master --------------------------------------------------------------
print("== final master")
run(["ffmpeg","-y","-v","error","-i",f"{SHAPED}/vo_pt.wav","-i",f"{SHAPED}/sfx_pt.wav",
     "-i",f"{SHAPED}/amb_pt.wav","-filter_complex",
     "[0][1][2]amix=inputs=3:normalize=0,alimiter=limit=0.95,volume=0.794,apad,atrim=0:30[m]",
     "-map","[m]",f"{AUD}/pipetest-master.mp3"])
r = run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",
         f"{AUD}/pipetest-master.mp3"])
dur = float(r.stdout.strip())
print("master duration:", dur)
raw = run_bin(["ffmpeg","-v","error","-i",f"{AUD}/pipetest-master.mp3",
               "-af","aresample=44100","-f","f32le","-"])
a = np.frombuffer(raw, dtype=np.float32)
true_peak = float(20*np.log10(np.max(np.abs(a)))) if len(a) else 0.0
print(f"true peak: {true_peak:.2f} dBFS")

# ---- 6. deterministic manifest ------------------------------------------------------
manifest = {
    "version": "pipetest-v1",
    "video": "PipeTestVideo",
    "fps": 30,
    "duration_sec": 30,
    "pools": POOLS,
    "shaped_peaks": peaks,
    "scene_cuts_sec": CUTS,
    "vo_segments": VO_SEGS,
    "ducking": {"depth_db": -4, "ramp_frames": 12, "ramp_sec": 0.4},
    "stems": {"amb": "public/audio/sfx/pro/shaped/amb_pt.wav"},
    "layout": man["layout"],
    "laws": man["laws"],
    "numbers": man["numbers"],
    "events": [
        {"t": round(e["t"], 4), "pool": e["sfx"], "asset": e["asset"], "seed": e["seed"],
         "dur": e.get("dur"), "vel": e.get("vel"), "why": e.get("why", ""),
         "anchor": e.get("anchor", "")}
        for e in sorted(ev, key=lambda x: x["t"])
    ],
    "master": {"file": "public/audio/pipetest-master.mp3",
               "duration_sec": dur, "true_peak_dbfs": round(true_peak, 2)},
}
mpath = os.path.join(ROOT, "demo-video/audio_manifest_pipetest.json")
json.dump(manifest, open(mpath, "w"), indent=1)
print("manifest:", mpath)
print("DONE")
