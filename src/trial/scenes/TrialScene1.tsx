import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { CLAMP, INK, INDIGO, LightBackdrop, LightHeadline, LightKicker, MUTED, RED } from "../light";

// Scene 1 (0:00–0:06): the problem — timing the market.
// Volatile zigzag line drawn across the grid, ending in a sharp red drop.

function mulberry(seed: number) {
  let s = seed >>> 0;
  return () => {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const W = 1920, H = 1080;
const CHART = { x0: 160, x1: 1760, yBase: 830, amp: 110 };

function buildPath(): { main: string; drop: string } {
  const rnd = mulberry(42);
  const n = 30;
  const pts: [number, number][] = [];
  for (let i = 0; i < n; i++) {
    const x = CHART.x0 + (i * (CHART.x1 - CHART.x0)) / (n - 1);
    const y = CHART.yBase - 120 + (rnd() - 0.5) * 2 * CHART.amp - i * 4;
    pts.push([x, y]);
  }
  // sharp drop: last 3 points plunge
  const last = pts[pts.length - 1];
  pts.push([last[0] + 40, last[1] + 260]);
  pts.push([last[0] + 80, last[1] + 300]);
  const d = (p: [number, number][]) => "M" + p.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(" L");
  const main = d(pts.slice(0, n));
  const drop = d([pts[n - 1], ...pts.slice(n)]);
  return { main, drop };
}

const { main, drop } = buildPath();

export const TrialScene1: React.FC = () => {
  const frame = useCurrentFrame();
  const drawMain = interpolate(frame, [20, 135], [0, 1], { ...CLAMP, easing: Easing.out(Easing.quad) });
  const drawDrop = interpolate(frame, [130, 160], [0, 1], { ...CLAMP, easing: Easing.out(Easing.exp) });
  const dropOp = interpolate(frame, [128, 136], [0, 1], CLAMP);
  const labelOp = interpolate(frame, [150, 165], [0, 1], CLAMP);

  return (
    <AbsoluteFill>
      <LightBackdrop />
      <AbsoluteFill style={{ alignItems: "center", paddingTop: 120 }}>
        <LightKicker>THE TRAP</LightKicker>
        <div style={{ height: 30 }} />
        <LightHeadline words={["Most", "people", "fail", "at", "investing"]} fontSize={96} />
        <LightHeadline words={["because", "they", "try", "to", "time", "the", "market."]} fontSize={96} startFrame={26} />
      </AbsoluteFill>

      {/* chart layer */}
      <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
        <path d={main} fill="none" stroke={INDIGO} strokeWidth={10} strokeLinecap="round" strokeLinejoin="round"
          pathLength={1} strokeDasharray={1} strokeDashoffset={1 - drawMain} />
        <path d={drop} fill="none" stroke={RED} strokeWidth={14} strokeLinecap="round" strokeLinejoin="round"
          pathLength={1} strokeDasharray={1} strokeDashoffset={1 - drawDrop} opacity={dropOp} />
      </svg>
      <div style={{
        position: "absolute", right: 120, bottom: 120, opacity: labelOp,
        background: RED, color: "#fff", fontWeight: 800, fontSize: 40,
        padding: "16px 40px", borderRadius: 20,
      }}>
        The crash always comes
      </div>
      <div style={{ position: "absolute", left: 160, bottom: 120, opacity: labelOp, color: MUTED, fontSize: 30, fontWeight: 600 }}>
        One bad guess erases years of gains
      </div>
    </AbsoluteFill>
  );
};
