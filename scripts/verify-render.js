#!/usr/bin/env node
/*
 * verify-render.js — programmatic Quality Gate for CrackIt Finance videos.
 *
 * ⚠️  STATUS (P4.4 B-13): Legacy audio assumptions (drop pool, -4dB ducking).
 * NOT in active workflow routing. Current: event-driven SFX, 36-entry bench,
 * 18dB bed under VO. Preserved for reference. Active validation via Python tests.
 *
 * Audits the deterministic build BEFORE it ships:
 *   AUDIO (from audio_manifest.json + built files)
 *     1. Master exists, duration = manifest duration_sec ±0.05, true peak < 0 dBFS.
 *     2. Anti-fatigue: consecutive same-pool events never reuse one asset.
 *     3. Drop sync: every scene cut has a drop peaking exactly 1 frame before it.
 *     4. Density: max 5 one-shot gestures per 1s window (ripple groups count once).
 *     4b. Mandate laws (opt-in via manifest.laws): no-ticking (same-pool
 *         one-shots >= 0.25s apart), spring-overshoot anchor alignment,
 *         VO band exclusion, 8px grid multiples on declared layout values.
 *     5. VO ducking: ambient measures ≈ -4dB under VO vs. silence (3–5dB window).
 *     5b. Frequency separation: each one-shot's energy concentrated in its
 *         assigned band (catches dropped filter chains).
 *   VISUAL (from rendered stills)
 *     6. Stills are 1920×1080.
 *     7. Top hairline: 10px indigo→violet→indigo gradient present on every scene.
 *     8. Non-blank: ink pixels present (no empty renders).
 *     9. Pixel-clipping: 80px safe area free of ink on every test frame.
 *
 * Usage: node scripts/verify-render.js [--mode trial|production] [--comp NAME] [--manifest FILE]
 *          [--frames F1,F2,..] [--report FILE]
 *   Trial mode (default) keeps the old 30s TrialVideo frame set.
 *   Production mode audits frames across the FULL video (mid-scene frames,
 *   spread over the manifest duration) and streams the true-peak decode so
 *   long masters don't blow the 64MB exec buffer. Explicit --frames always
 *   wins and is range-checked against the video length.
 *   The stress test runs:
 *   node scripts/verify-render.js --comp StressTest \
 *     --manifest audio_manifest_stress.json \
 *     --frames 20,40,75,110,149 --report verify-report-stress.json
 * Exit 0 + PASS, or exit 1 + FAIL with violation coordinates.
 * Always writes the report JSON.
 */
const { execFileSync } = require("child_process");
const fs = require("fs");
const path = require("path");
const os = require("os");

function arg(name, def) {
  const i = process.argv.indexOf(name);
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : def;
}
const COMP = arg("--comp", "TrialVideo");
const MANIFEST_FILE = arg("--manifest", "audio_manifest.json");
const REPORT_FILE = arg("--report", "verify-report.json");
const MODE = arg("--mode", "trial");
const FRAMES_CLI = process.argv.indexOf("--frames") >= 0;
let FRAMES = null; // resolved after manifest load (production defaults span the full video)

const ROOT = path.resolve(__dirname, ".."); // demo-video/
const MANIFEST = path.join(ROOT, MANIFEST_FILE);
const PRODIR = path.join(ROOT, "public/audio/sfx/pro");
const SHAPED = path.join(ROOT, "public/audio/sfx/pro/shaped");
const REPORT = path.join(ROOT, REPORT_FILE);
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "verify-"));

const violations = [];
const notes = [];
const violate = (kind, where, detail) => violations.push({ kind, where, detail });
const note = (s) => notes.push(s);

function sh(cmd, opts = {}) {
  return execFileSync("bash", ["-c", cmd], { maxBuffer: 64 * 1024 * 1024, ...opts })
    .toString();
}
function ffprobe(file, entries) {
  const out = sh(`ffprobe -v error -show_entries ${entries} -of csv=p=0 ${JSON.stringify(file)}`);
  return out.trim().split("\n").map((l) => l.trim());
}
function meanVolume(file, ss, t) {
  let out;
  try {
    out = sh(
      `ffmpeg -hide_banner -nostats -ss ${ss} -t ${t} -i ${JSON.stringify(file)} -af volumedetect -f null - 2>&1 | grep mean_volume`
    );
  } catch (e) {
    return null; // measurement window failed (e.g. beyond file duration) -> caller records a violation
  }
  const m = out.match(/mean_volume:\s*(-?[\d.]+)\s*dB/);
  return m ? parseFloat(m[1]) : null;
}

// ---- load manifest ----------------------------------------------------------
if (!fs.existsSync(MANIFEST)) {
  violate("manifest", MANIFEST, "audio_manifest.json missing — run tools/mix_master.py first");
  return finish();
}
const M = JSON.parse(fs.readFileSync(MANIFEST, "utf8"));
const FPS = M.fps || 30;
note(`manifest ${M.version}, ${M.events.length} events, ${Object.keys(M.pools).length} pools`);

// ---- resolve frames: production mode spans the full video ----------------------
const TOTAL_FRAMES = Math.floor((M.duration_sec || 0) * FPS);
if (FRAMES_CLI) {
  const given = arg("--frames", "").split(",").map(Number).filter(Number.isFinite);
  const bad = given.filter((f) => f < 0 || f >= TOTAL_FRAMES);
  if (bad.length)
    violate("visual", "frames", `${bad.length} --frames out of range (video is ${TOTAL_FRAMES} frames): ${bad.slice(0, 8).join(",")}`);
  FRAMES = given.filter((f) => f >= 0 && f < TOTAL_FRAMES);
  note(`explicit frames: ${FRAMES.length} passed range check`);
} else if (MODE === "production") {
  // mid-scene frame of up to 10 evenly-spread scenes; no scene cuts -> midpoint
  const cuts = (M.scene_cuts_sec || []).slice().sort((a, b) => a - b);
  const edges = [0, ...cuts, M.duration_sec || 0];
  const mids = edges.slice(1).map((e, i) => (edges[i] + e) / 2);
  const n = Math.min(10, mids.length) || 1;
  FRAMES = [];
  for (let i = 0; i < n; i++) {
    const t = mids.length > 1 ? mids[Math.round((i * (mids.length - 1)) / (n - 1))] : (M.duration_sec || 30) / 2;
    FRAMES.push(Math.min(TOTAL_FRAMES - 1, Math.floor(t * FPS)));
  }
  FRAMES = [...new Set(FRAMES)];
  note(`production mode: auditing ${FRAMES.length} frames across ${(M.duration_sec || 0).toFixed(1)}s`);
} else {
  FRAMES = [90, 179, 449, 585, 719, 899].filter((f) => f < TOTAL_FRAMES);
  note("trial mode: auditing first-30s frame set");
}

// ---- 1. master file ---------------------------------------------------------
const masterPath = path.join(ROOT, M.master.file);
if (!fs.existsSync(masterPath)) {
  violate("audio", "master", `missing ${M.master.file}`);
} else {
  const [dur] = ffprobe(masterPath, "format=duration");
  const d = parseFloat(dur);
  note(`master duration ${d.toFixed(3)}s, manifest peak ${M.master.true_peak_dbfs} dBFS`);
  if (Math.abs(d - M.duration_sec) > 0.05)
    violate("audio", "master.duration", `duration ${d.toFixed(3)}s != ${M.duration_sec}s`);
  // true peak: streamed volumedetect (raw f32le decode of a long master would
  // exceed the 64MB exec buffer and crash the gate — text stats stay tiny).
  // NOTE: no -v error here — volumedetect stats print at INFO level and would
  // be swallowed, leaving an empty match.
  const vd = sh(`ffmpeg -hide_banner -nostats -i ${JSON.stringify(masterPath)} ` +
    `-af "aresample=44100,volumedetect" -f null - 2>&1 | grep -E "max_volume|mean_volume" || true`);
  const mv = vd.match(/max_volume:\s*(-?[\d.]+|n\/a)\s*dB/);
  const peakDb = mv && mv[1] !== "n/a" ? parseFloat(mv[1]) : null;
  note(`measured true peak ${peakDb === null ? "n/a" : peakDb.toFixed(2) + " dBFS"}`);
  if (peakDb === null) {
    violate("audio", "master.true_peak", "volumedetect returned no peak — decode failed?");
  } else if (peakDb >= 0) {
    violate("audio", "master.true_peak", `true peak ${peakDb.toFixed(2)} dBFS >= 0`);
  }
}

// ---- 2. anti-fatigue pools ----------------------------------------------------
const ev = [...M.events].sort((x, y) => x.t - y.t);
for (let i = 1; i < ev.length; i++) {
  const p = ev[i], q = ev[i - 1];
  if (p.pool === q.pool && M.pools[p.pool].length > 1 && p.asset === q.asset) {
    violate("audio", `t=${p.t}s`, `anti-fatigue: pool "${p.pool}" fired "${p.asset}" twice in a row (prev t=${q.t}s)`);
  }
}
note("anti-fatigue pool rotation checked");

// ---- 3. drop sync: peak exactly 1 frame before each cut ------------------------
for (const cut of M.scene_cuts_sec) {
  const drops = ev.filter((e) => e.pool === "drop");
  const ok = drops.some((e) => {
    const peakAt = M.shaped_peaks[e.asset];
    return Math.abs(e.t + peakAt - (cut - 1 / FPS)) <= 0.002;
  });
  if (!ok) violate("audio", `cut=${cut}s`, "no drop peaks exactly 1 frame before this cut");
}
note(`drop sync checked for cuts [${M.scene_cuts_sec.join(", ")}]`);

// ---- 4. density: max 5 one-shot gestures per 1s window --------------------------
const gestures = []; // ripple groups collapse to one gesture
for (const e of ev) {
  if (e.pool === "wheel") continue; // beds, not one-shots
  const last = gestures[gestures.length - 1];
  if (e.ripple && last && last.ripple && e.t - last.t <= 0.15) continue;
  gestures.push(e);
}
for (let i = 0; i < gestures.length; i++) {
  const w0 = gestures[i].t;
  const n = gestures.filter((g) => g.t >= w0 && g.t < w0 + 1.0).length;
  if (n > 5) {
    violate("audio", `window ${w0.toFixed(2)}–${(w0 + 1).toFixed(2)}s`, `density: ${n} one-shot gestures in 1s (cap 5)`);
    break;
  }
}
note(`density checked over ${gestures.length} one-shot gestures`);

// ---- 4b–4e. re-training mandate laws (opt-in per manifest) ----------------------
const LAWS = M.laws || {};
if (LAWS.no_ticking) {
  // Pillar 1: no two one-shots from the same pool within 0.25s (ticker ban)
  for (let i = 1; i < ev.length; i++) {
    const p = ev[i], q = ev[i - 1];
    if (p.pool === q.pool && p.pool !== "wheel" && p.t - q.t < 0.25) {
      violate("audio", `t=${p.t}s`, `no-ticking law: pool "${p.pool}" fired twice within 0.25s (${(p.t - q.t).toFixed(3)}s apart)`);
    }
  }
  note("no-ticking law checked");
}
if (LAWS.overshoot_alignment) {
  // Pillar 2: spring-overshoot anchors must hit (start_frame + 11) / fps
  for (const e of ev) {
    const a = e.anchor;
    if (a && a.type === "spring-overshoot") {
      const want = (a.spring_start_frame + 11) / FPS;
      if (Math.abs(e.t - want) > 0.002) {
        violate("audio", `t=${e.t}s`, `overshoot alignment: want t=${want.toFixed(4)}s (frame ${a.spring_start_frame}+11), got ${e.t}s`);
      }
    }
  }
  note("spring-overshoot alignment checked");
}
if (LAWS.vo_band_exclusion) {
  // Pillar 3, layer 2: no one-shot inside VO-active segments (±0.1s)
  for (const e of ev) {
    if (e.pool === "wheel") continue;
    for (const [a, b] of M.vo_segments) {
      if (e.t > a - 0.1 && e.t < b + 0.1) {
        violate("audio", `t=${e.t}s`, `VO band exclusion: one-shot inside VO segment [${a}, ${b}]`);
      }
    }
  }
  note("VO band exclusion checked");
}
if (LAWS.grid_8px && M.layout) {
  // Pillar 4: every declared layout value a strict multiple of 8
  const vals = { grid: M.layout.grid, margins: M.layout.margins };
  (M.layout.cards || []).forEach((c, i) => {
    vals[`card${i}.x`] = c.x; vals[`card${i}.y`] = c.y;
    vals[`card${i}.w`] = c.w; vals[`card${i}.h`] = c.h; vals[`card${i}.pad`] = c.pad;
  });
  for (const [k, v] of Object.entries(vals)) {
    if (typeof v !== "number" || v % 8 !== 0) {
      violate("visual", `layout.${k}`, `8px grid law: ${k}=${v} is not a multiple of 8`);
    }
  }
  note(`8px grid checked over ${Object.keys(vals).length} layout values`);
}

// ---- 5. VO ducking: isolate the envelope --------------------------------------
// The roomtone source has its own dynamics (~8dB across 30s), so comparing
// absolute levels across segments conflates source with ducking. Honest method:
// render an unducked reference (identical chain, no envelope) and compare
// the manifest's ducked amb stem vs reference at IDENTICAL timestamps.
const amb = path.join(ROOT, (M.stems && M.stems.amb) || "public/audio/sfx/pro/shaped/amb.wav");
const DURM = M.duration_sec, RAMP = M.ducking.ramp_sec;
if (!fs.existsSync(amb)) {
  violate("audio", "amb stem", `ducked ambient stem missing: ${amb}`);
} else {
  const ref = path.join(tmp, "amb-ref.wav");
  sh(`ffmpeg -y -v error -i ${JSON.stringify(path.join(PRODIR, "pro-ambient.wav"))} ` +
     `-af "atrim=0:${DURM},asetpts=PTS-STARTPTS,aresample=44100,lowpass=f=400,volume=0.08,` +
     `aformat=channel_layouts=stereo" ${JSON.stringify(ref)}`);
  const depthAt = (ss, t) => {
    const a = meanVolume(amb, ss, t), b = meanVolume(ref, ss, t);
    return a === null || b === null ? null : a - b;
  };
  const segs = M.vo_segments;
  // fully-ducked flat: first VO segment long enough, inset past the ramps
  const dseg = segs.find(([a, b]) => b - a >= RAMP * 2 + 1.5);
  const dDucked = dseg ? depthAt(dseg[0] + RAMP + 0.1, 1.5) : null;
  // fully-open flat: widest gap outside VO ± ramps
  const bounds = [0, ...segs.flatMap(([a, b]) => [a - RAMP, b + RAMP]), DURM];
  let gap = null;
  for (let i = 0; i < bounds.length; i += 2) {
    const [g0, g1] = [Math.max(0, bounds[i]), Math.min(DURM, bounds[i + 1])];
    if (g1 - g0 >= 0.8 && (!gap || g1 - g0 > gap[1] - gap[0])) gap = [g0, g1];
  }
  const dOpen = gap ? depthAt(gap[0] + 0.1, Math.min(1.5, gap[1] - gap[0] - 0.2)) : null;
  // ramp midpoint: first segment whose ramp-up completes inside the video
  const rseg = segs.find(([a, b]) => b + RAMP < DURM - 0.1);
  const dRamp = rseg ? depthAt(rseg[1] + RAMP / 2, 0.15) : "skipped";
  if (dDucked === null || dOpen === null || dRamp === null) {
    violate("audio", "ducking", "could not measure ambient envelope");
  } else {
    // smoothstep(0.5) = 0.5 → ramp-mid target = depth_db/2 (depth_db is negative)
    const rampTarget = M.ducking.depth_db / 2;
    note(`envelope isolated: ducked ${dDucked.toFixed(2)}dB (target ${M.ducking.depth_db}dB), ` +
         `open ${dOpen.toFixed(2)}dB (target 0)` +
         (dRamp === "skipped" ? ", ramp: skipped (VO runs to end)" : `, ramp-mid ${dRamp.toFixed(2)}dB (target ${rampTarget.toFixed(2)}dB)`));
    if (dDucked < M.ducking.depth_db - 1 || dDucked > M.ducking.depth_db + 1)
      violate("audio", "ducking.depth", `ducked depth ${dDucked.toFixed(2)}dB outside target ±1dB`);
    if (Math.abs(dOpen) > 1)
      violate("audio", "ducking.open", `open gain ${dOpen.toFixed(2)}dB outside ±1dB`);
    if (dRamp !== "skipped" && (dRamp < rampTarget - 0.9 || dRamp > rampTarget + 0.9))
      violate("audio", "ducking.ramp", `ramp midpoint ${dRamp.toFixed(2)}dB outside ${rampTarget.toFixed(2)}±0.9dB (ease-in-out broken?)`);
  }
}

// ---- 5b. frequency separation: energy concentrated in the assigned band -------
// Guards against filter-chain regressions (a dropped highpass/lowpass would
// collapse separation to ~0-3dB). Baselines measured 2026-10-04 on shaped files.
const SEPARATION = [
  // [asset, rejected-band filter, min separation dB, measured baseline]
  ["subhit.wav", "highpass=f=300", 8, 34.6],  // sub-bass: nothing lives above 300Hz
  ["drop.wav", "highpass=f=1600", 8, 23.5],   // transition sub: nothing above 1.6kHz
  ["pluck.wav", "lowpass=f=1000", 8, 11.9],   // delicate highs: little below 1kHz
  ["snap.wav", "lowpass=f=1000", 8, 10.2],
  ["bell.wav", "lowpass=f=200", 8, 52.5],      // de-mudded: nothing below 200Hz
];
for (const [asset, rejFilter, minSep] of SEPARATION) {
  const p = path.join(SHAPED, asset);
  const full = meanVolume(p, 0, 99), rej = (() => {
    const out = sh(`ffmpeg -hide_banner -i ${JSON.stringify(p)} -af "${rejFilter},volumedetect" -vn -f null /dev/null 2>&1 | grep mean_volume`);
    const m = out.match(/mean_volume:\s*(-?[\d.]+)\s*dB/);
    return m ? parseFloat(m[1]) : null;
  })();
  if (full === null || rej === null) {
    violate("audio", `separation:${asset}`, "could not measure spectral separation");
  } else {
    const sep = full - rej;
    note(`separation ${asset}: ${sep.toFixed(1)}dB (min ${minSep}dB)`);
    if (sep < minSep)
      violate("audio", `separation:${asset}`, `only ${sep.toFixed(1)}dB separation (min ${minSep}dB) — filter chain broken?`);
  }
}
const INDIGO = [0x4f, 0x46, 0xe5], VIOLET = [0x8b, 0x5c, 0xf6];
const lerp = (a, b, t) => a.map((c, i) => Math.round(c + (b[i] - c) * t));
// RETIRED 2026-10-08: hairlineAt() belonged to the dark Premium SaaS identity.
// The light-premium check (7) replaced it. Kept as history, not executed.
const hairlineAt = (x) => {
  const t = x / 1919;
  return t <= 0.5 ? lerp(INDIGO, VIOLET, t * 2) : lerp(VIOLET, INDIGO, (t - 0.5) * 2);
};
for (const f of FRAMES) {
  const png = path.join(tmp, `f${f}.png`);
  try {
    sh(`cd ${JSON.stringify(ROOT)} && npx remotion still ${COMP} ${JSON.stringify(png)} --frame=${f} 2>&1 | tail -1`);
  } catch (e) {
    violate("visual", `frame ${f}`, `still render failed: ${String(e).slice(0, 160)}`);
    continue;
  }
  if (!fs.existsSync(png)) {
    violate("visual", `frame ${f}`, "still PNG missing after render attempt");
    continue;
  }
  // 6. dimensions
  const [wh] = ffprobe(png, "stream=width,height");
  const [w, h] = wh.split(",").map(Number);
  if (w !== 1920 || h !== 1080) violate("visual", `frame ${f}`, `dimensions ${w}x${h} != 1920x1080`);
  // 7. LIGHT PREMIUM FINTECH identity (replaces the retired dark hairline check,
  //    2026-10-08): bright canvas default + no dark/neon leakage. Sampled at
  //    quarter resolution for speed.
  const small = execFileSync("ffmpeg", ["-v", "error", "-i", png,
    "-vf", "scale=480:270", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
    { maxBuffer: 64 * 1024 * 1024 });
  let lumaSum = 0, darkPx = 0, neonPx = 0;
  const NP = small.length / 3;
  for (let i = 0; i < small.length; i += 3) {
    const r = small[i], g = small[i + 1], b = small[i + 2];
    const mx = Math.max(r, g, b), mn = Math.min(r, g, b);
    const luma = 0.299 * r + 0.587 * g + 0.114 * b;
    lumaSum += luma;
    if (luma < 50) darkPx++;
    // neon = bright AND highly saturated (brand blues are mid-luma, exempt)
    if (mx > 0 && (mx - mn) / mx > 0.65 && luma > 140) neonPx++;
  }
  const meanLuma = lumaSum / NP, darkFrac = darkPx / NP, neonFrac = neonPx / NP;
  if (meanLuma < 185)
    violate("visual", `frame ${f}`, `canvas too dark for light identity: mean luma ${meanLuma.toFixed(0)} (min 185)`);
  if (darkFrac > 0.04)
    violate("visual", `frame ${f}`, `dark leakage: ${(darkFrac * 100).toFixed(1)}% near-black pixels (max 4% — text only)`);
  if (neonFrac > 0.005)
    violate("visual", `frame ${f}`, `neon leakage: ${(neonFrac * 100).toFixed(2)}% bright-saturated pixels (max 0.5%)`);
  // 8. non-blank: content pixels in the content band. Threshold <180 (not <80)
  // because mid-transition frames legitimately render faded text — the check
  // must catch empty renders, not punish entrances. Light canvas is ~245.
  const band = execFileSync("ffmpeg", ["-v", "error", "-i", png,
    "-vf", "crop=1920:700:0:200", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
    { maxBuffer: 64 * 1024 * 1024 });
  let content = 0;
  for (let i = 0; i < band.length; i += 4) if (band[i] < 180) content++;
  if (content < 1500) violate("visual", `frame ${f}`, `blank frame suspected: only ${content} content pixels`);
  // 9. pixel-clipping: 80px safe area must be free of ink (baseline 0 on trial)
  let marginInk = 0;
  for (const vf of ["crop=1920:70:0:10", "crop=1920:80:0:1000", "crop=80:1080:0:0", "crop=80:1080:1840:0"]) {
    const m = execFileSync("ffmpeg", ["-v", "error", "-i", png,
      "-vf", vf, "-f", "rawvideo", "-pix_fmt", "gray", "-"],
      { maxBuffer: 64 * 1024 * 1024 });
    for (let i = 0; i < m.length; i++) if (m[i] < 80) marginInk++;
  }
  if (marginInk > 500)
    violate("visual", `frame ${f}`, `pixel-clipping: ${marginInk} ink pixels inside 80px safe area`);
  fs.unlinkSync(png);
  note(`frame ${f}: 1920x1080, light canvas ok (luma ${meanLuma.toFixed(0)}), no dark/neon leak, ink ok, safe-area ok`);
}

// ---- report ----------------------------------------------------------------------
function finish() {
  const pass = violations.length === 0;
  const report = {
    at: new Date().toISOString(),
    pass,
    grade: pass ? "PASS" : "FAIL",
    notes,
    violations,
  };
  fs.writeFileSync(REPORT, JSON.stringify(report, null, 1));
  console.log(`\n===== VERIFY-RENDER: ${report.grade} =====`);
  for (const n of notes) console.log("  ok:", n);
  for (const x of violations) console.log(`  FAIL [${x.kind}] ${x.where}: ${x.detail}`);
  console.log(`report: ${REPORT}\n`);
  process.exit(pass ? 0 : 1);
}
finish();
