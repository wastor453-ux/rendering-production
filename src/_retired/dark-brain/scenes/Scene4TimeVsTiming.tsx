import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Backdrop, Kicker, CompareCard } from "../components/ui";
import { theme, fmt$ } from "../theme";

const EARLY = 1745504; // $500/mo, 8%, 40yr — start at 25
const LATE = 745180; // $500/mo, 8%, 30yr — start at 35
const COST = EARLY - LATE; // 1,000,324

export const Scene4TimeVsTiming: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const bannerIn = 300;
  const s = spring({
    frame: frame - bannerIn,
    fps,
    config: { damping: 13, stiffness: 200 },
  });
  const bOp = interpolate(frame - bannerIn, [0, 14], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });
  const bScale = interpolate(s, [0, 1], [0.7, 1]);
  return (
    <AbsoluteFill>
      <Backdrop />
      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: 64,
        }}
      >
        <Kicker>TIME BEATS TIMING</Kicker>
        <div style={{ display: "flex", gap: 60 }}>
          <CompareCard
            title="START AT 25"
            value={EARLY}
            sub="40 years · $500/mo · 8%"
            accent={theme.neon}
            delay={40}
            align="left"
          />
          <CompareCard
            title="START AT 35"
            value={LATE}
            sub="30 years · $500/mo · 8%"
            accent={theme.cyan}
            delay={130}
            align="right"
          />
        </div>
        <div
          style={{
            opacity: bOp,
            transform: `scale(${bScale})`,
            background: "rgba(255,77,94,0.12)",
            border: `3px solid ${theme.red}`,
            borderRadius: 24,
            padding: "36px 72px",
            boxShadow: `0 0 70px ${theme.red}44`,
            textAlign: "center",
          }}
        >
          <div
            style={{
              fontFamily: theme.body,
              fontSize: 32,
              letterSpacing: 6,
              color: theme.red,
              fontWeight: 700,
              marginBottom: 10,
            }}
          >
            10 YEARS OF WAITING COST
          </div>
          <div
            style={{
              fontFamily: theme.display,
              fontWeight: 800,
              fontSize: 110,
              color: theme.red,
              textShadow: `0 0 50px ${theme.red}88`,
              fontVariantNumeric: "tabular-nums",
            }}
          >
            {fmt$(COST)}
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
