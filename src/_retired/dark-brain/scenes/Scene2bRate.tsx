import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
} from "remotion";
import { Backdrop, Kicker, CountUp } from "../components/ui";
import { theme } from "../theme";

export const Scene2bRate: React.FC = () => {
  const frame = useCurrentFrame();
  const DUR = 547;
  // pulsing ring behind the hero number
  const pulse = interpolate(frame, [0, 60], [0.9, 1.08], {
    extrapolateRight: "extend",
    easing: Easing.inOut(Easing.sin),
  });
  const pulseOp = interpolate(frame % 60, [0, 60], [0.5, 0], {
    easing: Easing.out(Easing.quad),
  });
  const discOp = interpolate(frame, [DUR - 90, DUR - 30], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });
  return (
    <AbsoluteFill>
      <Backdrop />
      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: 30,
        }}
      >
        <Kicker>THE ENGINE</Kicker>
        <div style={{ position: "relative", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <div
            style={{
              position: "absolute",
              width: 620,
              height: 620,
              borderRadius: "50%",
              border: `3px solid ${theme.cyan}`,
              opacity: pulseOp * 0.8,
              transform: `scale(${pulse})`,
            }}
          />
          <CountUp
            to={8}
            fromFrame={30}
            toFrame={200}
            fontSize={330}
            color={theme.cyan}
            glow={theme.cyan}
            prefix=""
            suffix="%"
          />
        </div>
        <div
          style={{
            fontFamily: theme.display,
            fontWeight: 700,
            fontSize: 64,
            color: theme.text,
            opacity: interpolate(frame, [120, 170], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.out(Easing.quad),
            }),
          }}
        >
          average annual return
        </div>
        <div
          style={{
            fontFamily: theme.body,
            fontSize: 40,
            color: theme.muted,
            opacity: interpolate(frame, [200, 260], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.out(Easing.quad),
            }),
          }}
        >
          U.S. stock market · 100+ years of history · inflation-adjusted, conservative
        </div>
        <div
          style={{
            fontFamily: theme.body,
            fontSize: 30,
            color: theme.dim,
            opacity: discOp,
            marginTop: 20,
          }}
        >
          Past performance does not guarantee future results.
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
