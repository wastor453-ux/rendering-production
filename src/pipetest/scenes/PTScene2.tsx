import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import {
  Camera,
  Card,
  CLAMP,
  INK,
  INDIGO,
  LightBackdrop,
  MUTED,
  PALE,
  PTCaption,
  PTKicker,
  SpringIn,
} from "../shared";

// S2 (5-10s): the problem. SVG line chart draws 2% curve (quad-out easing,
// matched to the wheel velocity profile), count-up $10k -> $11,041,
// total strip springs at local f132 -> overshoot f143 -> snap @9.767s.

const YEARS = [10000, 10200, 10404, 10612, 10824, 11041];
const PX0 = 200;
const PXX = 296; // per-year step (1480 / 5), 8px-divisible
const PY0 = 540;
const PY1 = 740;
const VMIN = 9800;
const VMAX = 11200;

const px = (i: number) => PX0 + i * PXX;
const py = (v: number) => PY1 - ((v - VMIN) / (VMAX - VMIN)) * (PY1 - PY0);

const linePath = YEARS.map((v, i) => `${i === 0 ? "M" : "L"}${px(i)},${py(v).toFixed(1)}`).join(" ");
const areaPath = `${linePath} L${px(5)},${PY1} L${px(0)},${PY1} Z`;

/** Count-up from a base value (the chart story is $10k -> $11,041, not 0). */
const CountFrom: React.FC<{ from: number; to: number; fromFrame: number; toFrame: number }> = ({
  from,
  to,
  fromFrame,
  toFrame,
}) => {
  const frame = useCurrentFrame();
  // Snap to exact target at/past the end: Easing.out(Easing.exp) asymptotes at
  // 1 - 2^-10 = 0.999023 and NEVER reaches 1.
  const v =
    frame >= toFrame
      ? to
      : interpolate(frame, [fromFrame, toFrame], [from, to], {
          ...CLAMP,
          easing: Easing.out(Easing.exp),
        });
  return (
    <div
      style={{
        fontFamily: "'Plus Jakarta Sans', sans-serif",
        fontWeight: 800,
        fontSize: 120,
        color: INK,
        fontVariantNumeric: "tabular-nums",
      }}
    >
      ${Math.round(v).toLocaleString("en-US")}
    </div>
  );
};

const kLabel = (g: number) => `$${(g / 1000).toFixed(1).replace(/\.0$/, "")}k`;

export const PTScene2: React.FC = () => {
  const frame = useCurrentFrame();
  // quad-out matches the wheel swell velocity profile in the mix
  const prog = interpolate(frame, [21, 132], [0, 1], {
    ...CLAMP,
    easing: Easing.out(Easing.quad),
  });
  const endOp = interpolate(prog, [0.97, 1], [0, 1], CLAMP);

  return (
    <AbsoluteFill>
      <LightBackdrop />
      <Camera fromX={0} toX={-48}>
        <AbsoluteFill style={{ alignItems: "center" }}>
          <div style={{ height: 120 }} />
          <PTKicker>2% INTEREST · 5 YEARS</PTKicker>
          <div style={{ height: 32 }} />
          {/* chart card: x80 y280 w1760 h560 */}
          <div style={{ position: "absolute", top: 280, left: 80 }}>
            <Card style={{ width: 1760, height: 560 }}>
              <div style={{ padding: 48 }}>
                <div
                  style={{
                    fontFamily: "'Plus Jakarta Sans', sans-serif",
                    fontSize: 28,
                    fontWeight: 800,
                    letterSpacing: 6,
                    color: MUTED,
                  }}
                >
                  $10,000 GROWS TO
                </div>
                <CountFrom from={10000} to={11041} fromFrame={21} toFrame={132} />
                <svg width={1664} height={240} viewBox="48 500 1664 240" style={{ marginTop: 8 }}>
                  <defs>
                    <clipPath id="areaClip">
                      <rect x={48} y={500} width={48 + prog * 1664 - 48} height={240} />
                    </clipPath>
                  </defs>
                  {[10000, 10500, 11000].map((g) => (
                    <g key={g}>
                      <line
                        x1={PX0}
                        x2={PX0 + 5 * PXX}
                        y1={py(g)}
                        y2={py(g)}
                        stroke="#ECECF3"
                        strokeWidth={2}
                      />
                      <text
                        x={PX0 - 16}
                        y={py(g) + 10}
                        textAnchor="end"
                        fontSize={24}
                        fill={MUTED}
                        fontWeight={700}
                        fontFamily="'Plus Jakarta Sans', sans-serif"
                      >
                        {kLabel(g)}
                      </text>                    </g>
                  ))}
                  <path d={areaPath} fill={PALE} opacity={prog * 0.9} clipPath="url(#areaClip)" />
                  <path
                    d={linePath}
                    fill="none"
                    stroke={INDIGO}
                    strokeWidth={8}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    pathLength={1}
                    strokeDasharray={1}
                    strokeDashoffset={1 - prog}
                  />
                  <circle cx={px(5)} cy={py(11041)} r={14} fill={INDIGO} opacity={endOp} />
                </svg>
              </div>
            </Card>
          </div>
          {/* total strip: x80 y872 w1760 h128, springs at f132 */}
          <div style={{ position: "absolute", top: 872, left: 80 }}>
            <SpringIn startFrame={132} y={24}>
              <Card style={{ width: 1760, height: 128 }}>
                <div
                  style={{
                    height: 128,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontFamily: "'Plus Jakarta Sans', sans-serif",
                    fontSize: 44,
                    fontWeight: 800,
                    color: INK,
                    fontVariantNumeric: "tabular-nums",
                  }}
                >
                  Only $1,041 of growth
                  <span style={{ color: MUTED, fontWeight: 600, marginLeft: 16 }}>
                    in five years
                  </span>
                </div>
              </Card>
            </SpringIn>
          </div>
        </AbsoluteFill>
      </Camera>
      <PTCaption
        text="At two percent, ten thousand becomes eleven thousand in five years."
        fromFrame={15}
        toFrame={136}
      />
    </AbsoluteFill>
  );
};
