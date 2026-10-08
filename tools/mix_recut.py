#!/usr/bin/env python3
"""180s re-cut master-audio builder.
VO_3MIN.mp3 (master anchor) + deterministic SFX event bed + ambient bed
(-22dB vs VO, -8dB duck under speech per SOUND_DESIGN.md section 12) -> one master.
Same mix laws as mix_master.py, parameterized for 180s.
"""
import json, subprocess, os, sys, math
import numpy as np

ROOT = os.path.expanduser("~/workspace/crackit")
PRO = os.path.join(ROOT, "demo-video/public/audio/sfx/pro")
SHAPED = os.path.join(PRO, "shaped")
AUD = os.path.join(ROOT, "demo-video/public/audio")
VO = f"{AUD}/VO_3MIN.mp3"
MASTER = f"{AUD}/recut-master.mp3"
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

def first_transient(path, thresh=0.15, backoff=0.005):
    data = run_bin(["ffmpeg","-v","error","-i",path,"-af","aresample=44100,aformat=channel_layouts=mono","-f","f32le","-"])
    a = np.frombuffer(data, dtype=np.float32)
    idx = np.where(np.abs(a) > thresh)[0]
    return max(0.0, float(idx[0])/44100 - backoff) if len(idx) else 0.0

def peak_pos(path):
    data = run_bin(["ffmpeg","-v","error","-i",path,"-af","aresample=44100,aformat=channel_layouts=mono","-f","f32le","-"])
    a = np.frombuffer(data, dtype=np.float32)
    return float(np.argmax(np.abs(a))) / 44100 if len(a) else 0.0

# ---- 0. VO duration -----------------------------------------------------------
r = run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",VO])
VO_DUR = float(r.stdout.strip())
print(f"VO duration: {VO_DUR:.3f}s")

# ---- 1. shape one-shots -------------------------------------------------------
print("== shaping one-shots")
specs = {
    "drop":   (f"{PRO}/pro-drop.wav", 1.5, 2.0, "afade=t=in:st=0:d=0.3,lowpass=f=800,loudnorm=I=-10:TP=-1.5:LRA=11"),
    "subhit": (f"{PRO}/pro-subhit.wav", 0.8, 1.3, "afade=t=in:st=0:d=0.2,lowpass=f=120,loudnorm=I=-8:TP=-1.5:LRA=11"),
    "pluck":  (f"{PRO}/pro-pluck.wav", None, None, "highpass=f=2000,loudnorm=I=-14:TP=-1.5:LRA=11"),
    "pluck_alt": (f"{PRO}/pro-pluck-alt.wav", None, None, "highpass=f=2000,loudnorm=I=-14:TP=-1.5:LRA=11"),
    "snap":   (f"{PRO}/pro-snap.wav", None, None, "highpass=f=2000,loudnorm=I=-14:TP=-1.5:LRA=11"),
    "bell":   (f"{PRO}/pro-bell-alt.wav", 1.5, 2.5, "highpass=f=400,loudnorm=I=-12:TP=-1.5:LRA=11"),
    "bell_alt": (f"{PRO}/pro-bell.wav", 1.5, 2.5, "highpass=f=400,loudnorm=I=-12:TP=-1.5:LRA=11"),
    "wheel":  (f"{PRO}/pro-wheel.wav", None, None, "loudnorm=I=-16:TP=-1.5:LRA=11"),
}
peaks = {}
for name, (src, ts, td, fc) in specs.items():
    if ts is None:
        ts = first_transient(src)
    trim = f"atrim=start={ts}" + (f":end={ts+td}" if td else "") + ",asetpts=PTS-STARTPTS"
    out = f"{SHAPED}/recut_{name}.wav"
    run(["ffmpeg","-y","-v","error","-i",src,"-af",f"{trim},{fc},aresample=44100,aformat=channel_layouts=stereo",out])
    peaks[name] = peak_pos(out)
print("  shaped:", list(specs))

# ---- 2. VO (master anchor) ----------------------------------------------------
print("== VO")
run(["ffmpeg","-y","-v","error","-i",VO,"-af",
     "aresample=44100,loudnorm=I=-16:TP=-1:LRA=11,aformat=channel_layouts=stereo",
     f"{SHAPED}/recut_vo.wav"])

# ---- 3. SFX event bed ---------------------------------------------------------
print("== SFX events")
POOLS = {"pluck": ["pluck","pluck_alt"], "bell": ["bell","bell_alt"],
         "drop": ["drop"], "snap": ["snap"], "subhit": ["subhit"], "wheel": ["wheel"]}
_pool_idx = {k: 0 for k in POOLS}
def draw(pool):
    i = _pool_idx[pool] % len(POOLS[pool]); _pool_idx[pool] += 1
    return POOLS[pool][i]

F = 1/30
# (frame, pool, opts) — cut frames get drop re-timed to peak 1f before the cut
CUTS = {195, 453, 924, 1170, 1788, 2436, 3102, 3216, 3894, 4728, 4983}
raw_events = [
    (60,  "pluck", {}),            # beat1 headline
    (96,  "subhit", {}),           # DECLINED stamp
    (150, "drop", {"cut": 195}),   # morph whoosh -> beat2 (peak 1f before cut)
    (260, "pluck", {}),            # 6.7M kicker
    (425, "snap", {}),             # count-up settle
    (453, "drop", {"cut": 453}),
    (500, "pluck", {}),            # balance morph
    (603, "pluck", {"ripple": 3, "step": 4}),  # pipe labels
    (693, "snap", {}),             # IOU stamp
    (924, "drop", {"cut": 924}),
    (936, "pluck", {"ripple": 3, "step": 5}),  # 3 value cards
    (1170, "drop", {"cut": 1170}),
    (1182, "snap", {}),            # STORING -> LENDING swap
    (1788, "drop", {"cut": 1788}),
    (1838, "bell", {}),            # $100 deposit bars
    (2436, "drop", {"cut": 2436}),
    (2496, "subhit", {}),          # COULD NOT PAY
    (3102, "drop", {"cut": 3102}),
    (3216, "drop", {"cut": 3216}),
    (3276, "pluck", {"ripple": 4, "step": 8}),  # calendar days (audio accents every other day; visual staggers at 4f)
    (3516, "snap", {}),            # "money." punch
    (3894, "drop", {"cut": 3894}),
    (3908, "pluck", {"ripple": 4, "step": 5}),  # limit icons
    (4034, "wheel", {"dur": 1.6}), # threshold meter fill
    (4089, "subhit", {}),          # REPORT FILED
    (4354, "bell", {}),            # STRUCTURING stamp
    (4728, "drop", {"cut": 4728}),
    (4798, "pluck", {"ripple": 2, "step": 6}),  # privilege/property cards
    (4983, "drop", {"cut": 4983}),
    (5113, "bell", {}),            # gold coin
]
ev = []
for fr, pool, opts in raw_events:
    if "ripple" in opts:
        for i in range(opts["ripple"]):
            ev.append({"t": (fr + i*opts["step"])*F, "sfx": pool})
    elif pool == "wheel":
        ev.append({"t": fr*F, "sfx": pool, "dur": opts["dur"]})
    elif "cut" in opts:
        cut = opts["cut"]*F
        ev.append({"t": cut - F - peaks["drop"], "sfx": pool, "cut": cut})
    else:
        ev.append({"t": fr*F, "sfx": pool})

fc, inputs, n, labels = [], [], 0, []
for e in ev:
    pool, t = e["sfx"], e["t"]
    asset = draw(pool)
    e["asset"] = asset
    if pool == "wheel":
        dur = e["dur"]
        env = f"min(t/0.08,1)*(0.35+0.65*max(0,1-(t-0.08)/({dur}-0.11)))"
        loops = math.ceil(dur/0.5)
        inputs += ["-i", f"{SHAPED}/recut_{asset}.wav"]
        fc.append(f"[{n}]aloop=loop={loops}:size=22050,atrim=0:{dur},asetpts=PTS-STARTPTS,"
                  f"volume='{env}':eval=frame,afade=t=out:st={dur-0.03}:d=0.03,"
                  f"adelay={int(t*1000)}|{int(t*1000)}[s{n}]")
    else:
        inputs += ["-i", f"{SHAPED}/recut_{asset}.wav"]
        fc.append(f"[{n}]adelay={int(t*1000)}|{int(t*1000)}[s{n}]")
    labels.append(f"[s{n}]"); n += 1
fc.append("".join(labels)+f"amix=inputs={n}:normalize=0,aresample=44100,aformat=channel_layouts=stereo[sfx]")
run(["ffmpeg","-y","-v","error"]+inputs+["-filter_complex",";".join(fc),"-map","[sfx]",f"{SHAPED}/recut_sfx.wav"])
print(f"  {n} events mixed")

# ---- 4. ambient bed, -22dB vs VO, -8dB duck under speech ----------------------
print("== ambient + ducking")
R, DEPTH = 0.4, 1-10**(-8/20)  # 12-frame ramps, -8dB = x0.39811
def ss(e0,e1):
    x = f"min(max((t-({e0}))/({e1}-({e0})),0),1)"
    return f"(({x})*({x})*(3-2*({x})))"
a, b = 0.0, VO_DUR
up, dn = ss(a-R,a), ss(b,b+R)
expr = f"1-{DEPTH}*(({up}*(1-{dn})))"
run(["ffmpeg","-y","-v","error","-i",f"{PRO}/pro-ambient.wav","-af",
     f"aresample=44100,lowpass=f=400,volume=0.08,aformat=channel_layouts=stereo,"
     f"volume='{expr}':eval=frame,apad,atrim=0:{VO_DUR:.3f}", f"{SHAPED}/recut_amb.wav"])

# ---- 5. final master -----------------------------------------------------------
print("== final master")
run(["ffmpeg","-y","-v","error","-i",f"{SHAPED}/recut_vo.wav","-i",f"{SHAPED}/recut_sfx.wav","-i",f"{SHAPED}/recut_amb.wav",
     "-filter_complex",f"[0][1][2]amix=inputs=3:normalize=0,alimiter=limit=0.95,volume=0.891,atrim=0:{VO_DUR:.3f}[m]",
     "-map","[m]",MASTER])
r = run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",MASTER])
print("master duration:", r.stdout.strip())
raw = run_bin(["ffmpeg","-v","error","-i",MASTER,"-af","aresample=44100","-f","f32le","-"])
a = np.frombuffer(raw, dtype=np.float32)
print(f"true peak: {20*np.log10(np.max(np.abs(a))):.2f} dBFS")

# ---- 6. manifest ----------------------------------------------------------------
manifest = {"comp": "RecutVideo", "duration_sec": VO_DUR, "vo": "VO_3MIN.mp3",
            "scene_cuts_sec": sorted(c*F for c in CUTS),
            "events": [{"t": round(e["t"],4), "sfx": e["sfx"], "asset": e["asset"]} for e in ev]}
mpath = os.path.join(ROOT, "demo-video/recut_audio_manifest.json")
json.dump(manifest, open(mpath, "w"), indent=1)
print("manifest:", mpath)
