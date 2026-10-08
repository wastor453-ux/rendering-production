#!/usr/bin/env python3
"""Premium master-audio builder for CrackIt Finance videos.
Reads audio_timeline.json, shapes pro SFX per the Vox/MagnatesMedia schematic,
ducks ambience under VO (-4dB, 12-frame ease-in-out ramps), and masters one file.
Deterministic: same manifest -> same master, every time.
"""
import json, subprocess, os, sys, math
import numpy as np

ROOT = os.path.expanduser("~/workspace/crackit")
PRO = os.path.join(ROOT, "demo-video/public/audio/sfx/pro")
SHAPED = os.path.join(PRO, "shaped")
AUD = os.path.join(ROOT, "demo-video/public/audio")
MANIFEST = os.path.join(ROOT, "audio_timeline.json")
os.makedirs(SHAPED, exist_ok=True)

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

def peak_pos(path):
    """Position (sec) of max |amplitude| in a mono 44.1k file."""
    data = run_bin(["ffmpeg","-v","error","-i",path,"-af","aresample=44100,aformat=channel_layouts=mono","-f","f32le","-"])
    a = np.frombuffer(data, dtype=np.float32)
    return float(np.argmax(np.abs(a))) / 44100 if len(a) else 0.0

def first_transient(path, thresh=0.15, backoff=0.005):
    data = run_bin(["ffmpeg","-v","error","-i",path,"-af","aresample=44100,aformat=channel_layouts=mono","-f","f32le","-"])
    a = np.frombuffer(data, dtype=np.float32)
    idx = np.where(np.abs(a) > thresh)[0]
    return max(0.0, float(idx[0])/44100 - backoff) if len(idx) else 0.0

# ---- 1. shape one-shots -------------------------------------------------------
print("== shaping one-shots")
specs = {
    # name: (src, trim_start, trim_dur, filter_chain)
    "drop":   (f"{PRO}/pro-drop.wav", 1.5, 2.0, "afade=t=in:st=0:d=0.3,lowpass=f=800,loudnorm=I=-10:TP=-1.5:LRA=11"),
    "subhit": (f"{PRO}/pro-subhit.wav", 0.8, 1.3, "afade=t=in:st=0:d=0.2,lowpass=f=120,loudnorm=I=-8:TP=-1.5:LRA=11"),
    "pluck":  (f"{PRO}/pro-pluck.wav", None, None, "highpass=f=2000,loudnorm=I=-14:TP=-1.5:LRA=11"),
    "pluck_alt": (f"{PRO}/pro-pluck-alt.wav", None, None, "highpass=f=2000,loudnorm=I=-14:TP=-1.5:LRA=11"),
    "snap":   (f"{PRO}/pro-snap.wav", None, None, "highpass=f=2000,loudnorm=I=-14:TP=-1.5:LRA=11"),
    "bell":   (f"{PRO}/pro-bell-alt.wav", 1.5, 2.5, "highpass=f=400,loudnorm=I=-12:TP=-1.5:LRA=11"),
    "bell_alt": (f"{PRO}/pro-bell.wav", 1.5, 2.5, "highpass=f=400,loudnorm=I=-12:TP=-1.5:LRA=11"),
}
peaks = {}
for name, (src, ts, td, fc) in specs.items():
    if ts is None:  # auto head-trim to first transient
        ts = first_transient(src)
        print(f"  {name}: head trimmed {ts:.3f}s")
    trim = f"atrim=start={ts}" + (f":end={ts+td}" if td else "") + ",asetpts=PTS-STARTPTS"
    out = f"{SHAPED}/{name}.wav"
    run(["ffmpeg","-y","-v","error","-i",src,"-af",f"{trim},{fc},aresample=44100,aformat=channel_layouts=stereo",out])
    peaks[name] = peak_pos(out)
    print(f"  {name}: shaped, peak at {peaks[name]:.3f}s")

# snap_alt: pitch-varied sibling (+5%) so the snap pool never repeats back-to-back
run(["ffmpeg","-y","-v","error","-i",f"{SHAPED}/snap.wav","-af",
     "asetrate=44100*1.05,aresample=44100,aformat=channel_layouts=stereo", f"{SHAPED}/snap_alt.wav"])
peaks["snap_alt"] = peak_pos(f"{SHAPED}/snap_alt.wav")
print(f"  snap_alt: derived, peak at {peaks['snap_alt']:.3f}s")

# wheel: keep raw 0.5s, looped at mix time
run(["ffmpeg","-y","-v","error","-i",f"{PRO}/pro-wheel.wav","-af",
     "atrim=0:0.5,asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=44100,aformat=channel_layouts=stereo", f"{SHAPED}/wheel.wav"])

# ---- anti-fatigue pools: localized, sequential draw, no back-to-back repeats --
POOLS = {
    "pluck":  ["pluck", "pluck_alt"],  # text entrances, card ripples
    "bell":   ["bell", "bell_alt"],    # badge springs
    "drop":   ["drop"],                # scene transitions (9s apart)
    "snap":   ["snap", "snap_alt"],    # UI confirmations (+5% pitch sibling)
    "wheel":  ["wheel"],
    "subhit": ["subhit"],
}
_pool_idx = {k: 0 for k in POOLS}
def draw(pool):
    assets = POOLS[pool]
    a = assets[_pool_idx[pool] % len(assets)]
    _pool_idx[pool] += 1
    return a

# ---- 2. VO timeline (master anchor, untouched by ducking) --------------------
print("== VO timeline")
vo = [("trial1.mp3",0.0),("trial2.mp3",6.0),("trial3.mp3",15.0),("trial4.mp3",24.0)]
fc, inputs, n = [], [], 0
for f, t in vo:
    inputs += ["-i", f"{AUD}/{f}"]
    fc.append(f"[{n}]aresample=44100,adelay={int(t*1000)}|{int(t*1000)}[v{n}]"); n += 1
fc.append("".join(f"[v{i}]" for i in range(n)) + f"amix=inputs={n}:normalize=0,loudnorm=I=-16:TP=-1:LRA=11,aresample=44100,aformat=channel_layouts=stereo,apad,atrim=0:30[vo]")
run(["ffmpeg","-y","-v","error"]+inputs+["-filter_complex",";".join(fc),"-map","[vo]",f"{SHAPED}/vo.wav"])

# VO-active intervals (measured durations)
VO_SEGS = [(0.0,3.528),(6.0,11.088),(15.0,19.608),(24.0,26.352)]

# ---- 3. SFX event bed from manifest ------------------------------------------
print("== SFX events")
man = json.load(open(MANIFEST))
CUTS = man["scene_cuts_sec"]
ev = []
for e in man["events"]:
    if "ripple" in e:  # expand card ripple (marked for density grouping)
        for i in range(e["ripple"]["count"]):
            ev.append({"t": e["t"]+i*e["ripple"]["step"], "sfx": e["sfx"], "ripple": True})
    else:
        ev.append(e)
# re-time drops: peak exactly 1 frame before each cut
drop_events = [e for e in ev if e["sfx"]=="drop"]
for e, cut in zip(drop_events, CUTS):
    e["t"] = cut - 1/30 - peaks["drop"]
    print(f"  drop re-timed to {e['t']:.4f}s (peak {cut-1/30:.4f}s, 1f before {cut}s cut)")

fc, inputs, n, labels = [], [], 0, []
for e in ev:
    pool, t = e["sfx"], e["t"]
    asset = draw(pool)          # anti-fatigue: sequential pool rotation
    e["asset"] = asset         # recorded into the manifest for verification
    if pool == "wheel":
        dur = e["dur"]
        vel = e.get("vel", "quad-out")
        # Velocity-following swell (Disney motion-derived signal): gain tracks the
        # data line's normalized velocity analytically. All trial draws use
        # Easing.out(Easing.quad) -> velocity decays linearly 1 -> 0, so
        # gain(t) = 0.35 + 0.65*(1 - t/dur): strong attack, breathing decay.
        # 80ms attack fade (de-click loop start), 30ms de-click at exact stop.
        loops = math.ceil(dur/0.5)
        env = (f"min(t/0.08,1)*(0.35+0.65*max(0,1-(t-0.08)/({dur}-0.11)))"
               if vel == "quad-out" else f"min(t/0.08,1)*(0.35+0.65*pow(2,-10*(t-0.08)/({dur}-0.11)))")
        inputs += ["-i", f"{SHAPED}/wheel.wav"]
        fc.append(f"[{n}]aloop=loop={loops}:size=22050,atrim=0:{dur},asetpts=PTS-STARTPTS,"
                  f"volume='{env}':eval=frame,"
                  f"afade=t=out:st={dur-0.03}:d=0.03,"
                  f"adelay={int(t*1000)}|{int(t*1000)}[s{n}]")
    else:
        inputs += ["-i", f"{SHAPED}/{asset}.wav"]
        fc.append(f"[{n}]adelay={int(t*1000)}|{int(t*1000)}[s{n}]")
    labels.append(f"[s{n}]"); n += 1
fc.append("".join(labels)+f"amix=inputs={n}:normalize=0,aresample=44100,aformat=channel_layouts=stereo[sfx]")
run(["ffmpeg","-y","-v","error"]+inputs+["-filter_complex",";".join(fc),"-map","[sfx]",f"{SHAPED}/sfx.wav"])
print(f"  {n} events mixed")

# ---- 4. ambient bed with deterministic -4dB VO ducking ------------------------
print("== ambient + ducking")
R, DEPTH = 0.4, 1-10**(-4/20)  # 12-frame ramps, -4dB = x0.63096
def ss(e0,e1):
    x = f"min(max((t-({e0}))/({e1}-({e0})),0),1)"
    return f"(({x})*({x})*(3-2*({x})))"
dips = []
for a,b in VO_SEGS:
    up, dn = ss(a-R,a), ss(b,b+R)
    dips.append(f"({up}*(1-{dn}))")
expr = f"1-{DEPTH}*({'+'.join(dips)})"
run(["ffmpeg","-y","-v","error","-i",f"{PRO}/pro-ambient.wav","-af",
     f"atrim=0:30,asetpts=PTS-STARTPTS,aresample=44100,lowpass=f=400,volume=0.08,aformat=channel_layouts=stereo,"
     f"volume='{expr}':eval=frame", f"{SHAPED}/amb.wav"])

# ---- 5. final master -----------------------------------------------------------
print("== final master")
run(["ffmpeg","-y","-v","error","-i",f"{SHAPED}/vo.wav","-i",f"{SHAPED}/sfx.wav","-i",f"{SHAPED}/amb.wav",
     "-filter_complex","[0][1][2]amix=inputs=3:normalize=0,alimiter=limit=0.95,volume=0.891,apad,atrim=0:30[m]",
     "-map","[m]",f"{AUD}/trial-master.mp3"])
r = run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"{AUD}/trial-master.mp3"])
dur = float(r.stdout.strip())
print("master duration:", dur)

# true peak (MP3 encoder overshoots a bare limiter; verify < 0 dBFS)
raw = run_bin(["ffmpeg","-v","error","-i",f"{AUD}/trial-master.mp3",
               "-af","aresample=44100","-f","f32le","-"])
a = np.frombuffer(raw, dtype=np.float32)
true_peak = float(20*np.log10(np.max(np.abs(a)))) if len(a) else 0.0
print(f"true peak: {true_peak:.2f} dBFS")

# ---- 6. deterministic manifest for verify-render.js ---------------------------
manifest = {
    "version": "premium-v3",
    "video": "TrialVideo",
    "fps": 30,
    "duration_sec": 30,
    "pools": POOLS,
    "shaped_peaks": peaks,
    "scene_cuts_sec": CUTS,
    "vo_segments": VO_SEGS,
    "ducking": {"depth_db": -4, "ramp_frames": 12, "ramp_sec": 0.4},
    "stems": {"amb": "public/audio/sfx/pro/shaped/amb.wav"},
    "events": [
        {"t": round(e["t"], 4), "pool": e["sfx"], "asset": e["asset"],
         "dur": e.get("dur"), "ripple": bool(e.get("ripple", False)),
         "vel": e.get("vel"), "why": e.get("why", "")}
        for e in sorted(ev, key=lambda x: x["t"])
    ],
    "master": {"file": "public/audio/trial-master.mp3",
               "duration_sec": dur, "true_peak_dbfs": round(true_peak, 2)},
}
mpath = os.path.join(ROOT, "demo-video/audio_manifest.json")
json.dump(manifest, open(mpath, "w"), indent=1)
print("manifest:", mpath)
print("DONE")
