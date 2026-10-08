import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import { P } from "../theme";

const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const expo = Easing.bezier(0.16, 1, 0.3, 1);

const W = 1100;
const H = 420;
const PAD = 60;

/** Glowing money-flow line chart — draw-on + glow particles traveling the path. */
export const MoneyFlowChart: React.FC<{
  values: number[];
  delay?: number;
  drawFrames?: number;
  color1?: string;
  color2?: string;
}> = ({ values, delay = 0, drawFrames = 90, color1 = P.neonBlue, color2 = P.magenta }) => {
  const frame = useCurrentFrame();
  const n = values.length;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const px = (i: number) => PAD + (i / (n - 1)) * (W - PAD * 2);
  const py = (v: number) => PAD + (1 - (v - min) / (max - min || 1)) * (H - PAD * 2);

  const d = values.map((v, i) => `${i === 0 ? "M" : "L"}${px(i).toFixed(1)},${py(v).toFixed(1)}`).join(" ");
  // Approximate path length for dash draw-on
  const approxLen = n * ((W - PAD * 2) / (n - 1)) * 1.15;

  const drawP = interpolate(frame, [delay, delay + drawFrames], [0, 1], { ...CLAMP, easing: expo });
  const dashOffset = approxLen * (1 - drawP);

  // Endpoint dot + value label
  const endP = interpolate(frame, [delay + drawFrames - 6, delay + drawFrames + 6], [0, 1], { ...CLAMP, easing: expo });

  // Glow particles: 5 dots traveling along the x-range, y follows the curve
  const particles = [0, 1, 2, 3, 4].map((k) => {
    const cycle = 150;
    const t = ((frame - delay - k * 30) % cycle) / cycle;
    if (t < 0 || t > 1 || drawP < 0.05) return null;
    const fi = t * (n - 1);
    const i0 = Math.floor(fi);
    const i1 = Math.min(i0 + 1, n - 1);
    const fr = fi - i0;
    const cx = px(i0) + (px(i1) - px(i0)) * fr;
    const cy = py(values[i0]) + (py(values[i1]) - py(values[i0])) * fr;
    const op = interpolate(t, [0, 0.15, 0.85, 1], [0, 1, 1, 0], CLAMP);
    return <circle key={k} cx={cx} cy={cy} r={7} fill="#fff" opacity={op * 0.95} />;
  });

  const lastV = values[n - 1];

  return (
    <svg width={W} height={H} style={{ overflow: "visible" }}>
      <defs>
        <linearGradient id="flowline" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor={color1} />
          <stop offset="100%" stopColor={color2} />
        </linearGradient>
        <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
          <feGaussianBlur stdDeviation="10" result="b" />
          <feMerge>
            <feMergeNode in="b" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
        {/* micro-dashed vector path underneath */}
        <pattern id="dashpat" width="14" height="6" patternUnits="userSpaceOnUse">
          <line x1="0" y1="3" x2="8" y2="3" stroke="rgba(255,255,255,0.35)" strokeWidth="2" strokeDasharray="4 4" />
        </pattern>
      </defs>
      {/* dashed guide path */}
      <path d={d} fill="none" stroke="url(#dashpat)" strokeWidth="3"
        strokeDasharray={`${approxLen} ${approxLen}`} strokeDashoffset={dashOffset} opacity={0.5} />
      {/* glowing main line */}
      <g filter="url(#glow)">
        <path d={d} fill="none" stroke="url(#flowline)" strokeWidth="7" strokeLinecap="round"
          strokeDasharray={`${approxLen} ${approxLen}`} strokeDashoffset={dashOffset} />
      </g>
      {particles}
      {/* endpoint */}
      {endP > 0 && (
        <g opacity={endP}>
          <circle cx={px(n - 1)} cy={py(lastV)} r={12} fill="#fff" />
          <circle cx={px(n - 1)} cy={py(lastV)} r={20} fill="none" stroke="#fff" strokeWidth={2} opacity={0.5} />
        </g>
      )}
    </svg>
  );
};
