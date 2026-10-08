import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { Badge, Card, CLAMP, INK, INDIGO, LightBackdrop, LightCountUp, LightHeadline, LightKicker, MUTED, PALE } from "../light";
import { balanceAt } from "../../lib/finance";

// Scene 3 (0:15–0:24): the engine — $500/mo at 9.42% for 30 years → $1,000,000.
// Curve is plotted from the real future-value formula, month by month.

const RATE = 0.09422; // solved: $500/mo × 30yr → $1,000,000
const MONTHS_TOTAL = 360;

const BOX = { x0: 160, x1: 1760, y0: 760, y1: 240 }; // y0 = $0, y1 = $1M
const balances = Array.from({ length: MONTHS_TOTAL + 1 }, (_, m) => balanceAt(500, RATE, m));
const MAXV = 1_000_000;

function curvePath(upto: number): string {
  const pts: string[] = [];
  for (let m = 0; m <= upto; m++) {
    const x = BOX.x0 + (m / MONTHS_TOTAL) * (BOX.x1 - BOX.x0);
    const y = BOX.y0 - (Math.min(balances[m], MAXV) / MAXV) * (BOX.y0 - BOX.y1);
    pts.push(`${x.toFixed(1)},${y.toFixed(1)}`);
  }
  return "M" + pts.join(" L");
}

const FULL = curvePath(MONTHS_TOTAL);

export const TrialScene3: React.FC = () => {
  const frame = useCurrentFrame();
  const draw = interpolate(frame, [30, 200], [0, 1], { ...CLAMP, easing: Easing.out(Easing.quad) });
  const badgeIn = interpolate(frame, [205, 220], [0, 1], CLAMP);
  const capOp = interpolate(frame, [225, 240], [0, 1], CLAMP);

  // peak position for the badge
  const px = BOX.x1, py = BOX.y1;

  return (
    <AbsoluteFill>
      <LightBackdrop />
      <AbsoluteFill style={{ alignItems: "center", paddingTop: 110 }}>
        <LightKicker>THE ENGINE</LightKicker>
        <div style={{ height: 26 }} />
        <LightHeadline words={["Thirty", "years", "of", "showing", "up."]} fontSize={96} />
      </AbsoluteFill>

      {/* curve layer */}
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        {/* axis */}
        <line x1={BOX.x0} y1={BOX.y0} x2={BOX.x1} y2={BOX.y0} stroke="#D9D9E8" strokeWidth={3} />
        <path d={FULL} fill="none" stroke={INDIGO} strokeWidth={12} strokeLinecap="round"
          pathLength={1} strokeDasharray={1} strokeDashoffset={1 - draw} />
      </svg>

      {/* running total */}
      <div style={{ position: "absolute", left: 160, top: 470 }}>
        <div style={{ fontSize: 28, fontWeight: 700, letterSpacing: 8, color: MUTED, marginBottom: 10 }}>PORTFOLIO VALUE</div>
        <LightCountUp to={1000000} fromFrame={30} toFrame={200} fontSize={110} />
      </div>

      {/* badge under the peak */}
      <div style={{ position: "absolute", left: 1310, top: 560, opacity: badgeIn }}>
        <Badge fontSize={72}>$1,000,000</Badge>
      </div>

      <div style={{ position: "absolute", left: 160, bottom: 110, opacity: capOp, color: MUTED, fontSize: 30, fontWeight: 600 }}>
        $500/month · 9.42% avg. annual return · 30 years
      </div>
    </AbsoluteFill>
  );
};
