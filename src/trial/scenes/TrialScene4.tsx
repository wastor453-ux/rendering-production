import React from "react";
import { AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { Card, CLAMP, INK, INDIGO, LightBackdrop, LightHeadline, LightKicker, MUTED, VIOLET } from "../light";

// Scene 4 (0:24–0:30): call to action.
// Camera pulls back (scale 1.06 → 1), metrics slide out, logo card settles center.

const STATS = [
  { k: "$500/mo", v: "invested" },
  { k: "30 years", v: "of patience" },
  { k: "$1,000,000", v: "the result" },
];

export const TrialScene4: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const zoom = interpolate(frame, [0, 180], [1.06, 1], { ...CLAMP, easing: Easing.out(Easing.quad) });

  // stats slide out and fade, frames 25–60
  const outP = interpolate(frame, [25, 60], [0, 1], { ...CLAMP, easing: Easing.out(Easing.cubic) });

  // logo card springs in from frame 70
  const s = spring({ frame: frame - 70, fps, config: { mass: 1, tension: 180, friction: 12 } });
  const cardScale = interpolate(s, [0, 1], [0.7, 1], CLAMP);
  const cardOp = interpolate(frame, [70, 84], [0, 1], CLAMP);
  const cardY = interpolate(s, [0, 1], [60, 0], CLAMP);

  return (
    <AbsoluteFill style={{ transform: `scale(${zoom})` }}>
      <LightBackdrop />
      <AbsoluteFill style={{ alignItems: "center", paddingTop: 120 }}>
        <LightKicker>YOUR MOVE</LightKicker>
        <div style={{ height: 26 }} />
        <LightHeadline words={["Stop", "guessing.", "Automate", "today."]} fontSize={96} />

        {/* metrics row — slides out */}
        <div style={{
          display: "flex", gap: 32, marginTop: 70,
          opacity: 1 - outP, transform: `translateY(${-outP * 220}px)`,
        }}>
          {STATS.map((st) => (
            <Card key={st.k} style={{ padding: "36px 56px", textAlign: "center" }}>
              <div style={{ fontSize: 56, fontWeight: 800, color: INDIGO, fontVariantNumeric: "tabular-nums" }}>{st.k}</div>
              <div style={{ fontSize: 28, fontWeight: 600, color: MUTED, marginTop: 8 }}>{st.v}</div>
            </Card>
          ))}
        </div>

        {/* logo card — settles center */}
        <div style={{
          position: "absolute", top: 480, left: 0, right: 0, display: "flex", justifyContent: "center",
          opacity: cardOp, transform: `translateY(${cardY}px) scale(${cardScale})`,
        }}>
          <Card style={{ padding: "0 0 70px 0", textAlign: "center" }}>
            <div style={{ height: 12, background: INDIGO, marginBottom: 58 }} />
            <div style={{ padding: "0 120px" }}>
            <div style={{ fontSize: 34, fontWeight: 800, letterSpacing: 16, color: INDIGO, marginBottom: 18 }}>CRACKIT</div>
            <div style={{ fontSize: 88, fontWeight: 800, color: INK, letterSpacing: -2 }}>Finance</div>
            <div style={{ fontSize: 32, fontWeight: 600, color: MUTED, marginTop: 18 }}>Automate your wealth.</div>
            </div>
          </Card>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
