import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
} from "remotion";
import { Backdrop, Kicker } from "../components/ui";
import { theme, fmt$ } from "../theme";
import { balanceAt, PMT, RATE } from "../lib/finance";

const W = 1920;
const H = 1080;
const CX = 170; // chart left
const CY = 250; // chart top
const CW = 1580; // chart width
const CH = 640; // chart height
const MAXV = 745180; // 8% 30yr — computed, not guessed

function path(m0: number, m1: number, fn: (m: number) => number): string {
  const pts: string[] = [];
  for (let m = m0; m <= m1; m += 6) {
    const x = CX + (m / 360) * CW;
    const y = CY + CH - (fn(m) / MAXV) * CH;
    pts.push(`${m === m0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`);
  }
  return pts.join(" ");
}

const MILESTONES = [
  { year: 10, m: 120 },
  { year: 20, m: 240 },
  { year: 30, m: 360 },
];

export const Scene3Curve: React.FC = () => {
  const frame = useCurrentFrame();
  const DUR = 622;
  const p = interpolate(frame, [40, DUR - 90], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });
  const currentM = p * 360;
  const currentV = balanceAt(PMT, RATE, currentM);
  const curve = path(0, 360, (m) => balanceAt(PMT, RATE, m));
  const contrib = path(0, 360, (m) => PMT * m);

  return (
    <AbsoluteFill>
      <Backdrop />
      <div
        style={{
          position: "absolute",
          top: 70,
          left: 0,
          right: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 8,
        }}
      >
        <Kicker>COMPOUNDING</Kicker>
        <div
          style={{
            fontFamily: theme.display,
            fontWeight: 800,
            fontSize: 120,
            color: theme.neon,
            textShadow: `0 0 60px ${theme.neon}88`,
            fontVariantNumeric: "tabular-nums",
          }}
        >
          {fmt$(currentV)}
        </div>
        <div style={{ fontFamily: theme.body, fontSize: 34, color: theme.muted }}>
          from {fmt$(PMT * currentM)} of your own contributions
        </div>
      </div>

      <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
        {/* gridlines */}
        {[0, 250000, 500000, 750000].map((v) => {
          const y = CY + CH - (v / MAXV) * CH;
          return (
            <g key={v}>
              <line x1={CX} y1={y} x2={CX + CW} y2={y} stroke={theme.panelBorder} strokeWidth={2} />
              <text x={CX - 24} y={y + 12} textAnchor="end" fill={theme.dim} fontSize={30} fontFamily={theme.body}>
                {v === 0 ? "$0" : `$${v / 1000}K`}
              </text>
            </g>
          );
        })}
        {/* x labels */}
        {[0, 10, 20, 30].map((yr) => {
          const x = CX + (yr / 30) * CW;
          return (
            <text key={yr} x={x} y={CY + CH + 56} textAnchor="middle" fill={theme.dim} fontSize={32} fontFamily={theme.body}>
              {yr === 0 ? "START" : `${yr} YRS`}
            </text>
          );
        })}
        {/* contributions baseline (dashed gray) */}
        <path
          d={contrib}
          fill="none"
          stroke={theme.dim}
          strokeWidth={4}
          strokeDasharray="14 12"
          pathLength={1000}
          strokeDashoffset={1000 - 1000 * p}
          opacity={0.8}
        />
        {/* neon growth curve */}
        <path
          d={curve}
          fill="none"
          stroke={theme.neon}
          strokeWidth={10}
          strokeLinecap="round"
          pathLength={1000}
          strokeDasharray={1000}
          strokeDashoffset={1000 - 1000 * p}
          style={{ filter: `drop-shadow(0 0 18px ${theme.neon})` }}
        />
        {/* area fill under curve */}
        <path
          d={`${curve} L${CX + CW},${CY + CH} L${CX},${CY + CH} Z`}
          fill={theme.neon}
          opacity={0.1 * p}
        />
        {/* milestones */}
        {MILESTONES.map(({ year, m }) => {
          const v = balanceAt(PMT, RATE, m);
          const x = CX + (m / 360) * CW;
          const y = CY + CH - (v / MAXV) * CH;
          const shown = currentM >= m;
          return (
            <g key={year} opacity={shown ? 1 : 0}>
              <circle cx={x} cy={y} r={14} fill={theme.bg} stroke={theme.cyan} strokeWidth={6} />
              <circle cx={x} cy={y} r={6} fill={theme.cyan} />
              <text
                x={x}
                y={y - 44}
                textAnchor="middle"
                fill={theme.text}
                fontSize={36}
                fontWeight={800}
                fontFamily={theme.display}
              >
                {fmt$(v)}
              </text>
              <text
                x={x}
                y={y - 88}
                textAnchor="middle"
                fill={theme.cyan}
                fontSize={28}
                fontWeight={700}
                fontFamily={theme.body}
              >
                YEAR {year}
              </text>
            </g>
          );
        })}
        {/* legend */}
        <g opacity={interpolate(frame, [20, 60], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}>
          <line x1={CX + CW - 560} y1={CY + CH + 120} x2={CX + CW - 480} y2={CY + CH + 120} stroke={theme.neon} strokeWidth={8} strokeLinecap="round" />
          <text x={CX + CW - 460} y={CY + CH + 132} fill={theme.muted} fontSize={30} fontFamily={theme.body}>Your balance</text>
          <line x1={CX + CW - 200} y1={CY + CH + 120} x2={CX + CW - 120} y2={CY + CH + 120} stroke={theme.dim} strokeWidth={6} strokeDasharray="12 10" />
          <text x={CX + CW - 100} y={CY + CH + 132} fill={theme.muted} fontSize={30} fontFamily={theme.body}>Contributions</text>
        </g>
      </svg>
    </AbsoluteFill>
  );
};
