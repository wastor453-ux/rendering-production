import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { CLAMP, INK, INDIGO, LightBackdrop, LightHeadline, LightKicker, MUTED, PALE } from "../light";

// Scene 2 (0:06–0:15): the plan — $500 every month on autopilot.
// 12 month cards fill left-to-right as the progress bar sweeps.

const MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];

export const TrialScene2: React.FC = () => {
  const frame = useCurrentFrame();
  // sweep 0→1 across frames 50–230, eased
  const sweep = interpolate(frame, [50, 230], [0, 1], { ...CLAMP, easing: Easing.out(Easing.quad) });
  const barOp = interpolate(frame, [40, 55], [0, 1], CLAMP);
  const totalOp = interpolate(frame, [235, 250], [0, 1], CLAMP);

  return (
    <AbsoluteFill>
      <LightBackdrop />
      <AbsoluteFill style={{ alignItems: "center", paddingTop: 110 }}>
        <LightKicker>THE PLAN</LightKicker>
        <div style={{ height: 26 }} />
        <LightHeadline words={["$500", "every", "month.", "On", "autopilot."]} fontSize={96} />

        {/* 12 month cards: 6 × 2 */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(6, 1fr)", gap: 26, marginTop: 64, width: 1560 }}>
          {MONTHS.map((m, i) => {
            const filled = sweep * 12 > i + 0.5;
            const f = frame - 20 - i * 3;
            const op = interpolate(f, [0, 12], [0, 1], { ...CLAMP, easing: Easing.out(Easing.quad) });
            const y = interpolate(f, [0, 20], [28, 0], { ...CLAMP, easing: Easing.out(Easing.cubic) });
            return (
              <div key={m} style={{
                opacity: op, transform: `translateY(${y}px)`,
                background: filled ? INDIGO : PALE, borderRadius: 28,
                border: `1px solid ${filled ? INDIGO : "#DCDCF5"}`,
                boxShadow: filled ? "0 14px 44px rgba(26,27,37,.10)" : "none",
                padding: "30px 0", textAlign: "center",
              }}>
                <div style={{ fontSize: 30, fontWeight: 800, letterSpacing: 4, color: filled ? "#fff" : INDIGO }}>{m}</div>
                <div style={{ fontSize: 34, fontWeight: 800, color: filled ? "#fff" : INK, fontVariantNumeric: "tabular-nums", marginTop: 8 }}>
                  $500
                </div>
              </div>
            );
          })}
        </div>

        {/* progress bar */}
        <div style={{ opacity: barOp, marginTop: 54, width: 1560 }}>
          <div style={{ height: 20, borderRadius: 10, background: PALE, overflow: "hidden" }}>
            <div style={{ width: `${sweep * 100}%`, height: "100%", background: INDIGO, borderRadius: 10 }} />
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 14 }}>
            <span style={{ fontSize: 28, fontWeight: 700, color: MUTED }}>Month 1</span>
            <span style={{ fontSize: 28, fontWeight: 700, color: MUTED }}>Month 12</span>
          </div>
        </div>

        <div style={{ opacity: totalOp, marginTop: 40, fontSize: 52, fontWeight: 800, color: INK }}>
          $6,000 a year <span style={{ color: MUTED, fontWeight: 600 }}>— without thinking about it</span>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
