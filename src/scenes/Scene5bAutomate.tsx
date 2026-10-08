import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Backdrop, Kicker } from "../components/ui";
import { theme } from "../theme";

const Strike: React.FC<{ text: string; delay: number; fontSize?: number }> = ({
  text,
  delay,
  fontSize = 110,
}) => {
  const frame = useCurrentFrame();
  const op = interpolate(frame - delay, [0, 14], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });
  const strikeAt = delay + 45;
  const sx = interpolate(frame - strikeAt, [0, 22], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.exp),
  });
  return (
    <div style={{ position: "relative", opacity: op }}>
      <div
        style={{
          fontFamily: theme.display,
          fontWeight: 800,
          fontSize,
          color: theme.muted,
          textDecoration: "none",
        }}
      >
        {text}
      </div>
      <div
        style={{
          position: "absolute",
          top: "52%",
          left: "-4%",
          width: "108%",
          height: 14,
          borderRadius: 7,
          background: theme.red,
          boxShadow: `0 0 30px ${theme.red}`,
          transform: `scaleX(${sx}) rotate(-2deg)`,
          transformOrigin: "left center",
        }}
      />
    </div>
  );
};

export const Scene5bAutomate: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({
    frame: frame - 220,
    fps,
    config: { damping: 12, stiffness: 200 },
  });
  const op = interpolate(frame - 220, [0, 12], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });
  const scale = interpolate(s, [0, 1], [0.6, 1]);
  const subOp = interpolate(frame, [300, 350], [0, 1], {
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
          gap: 48,
        }}
      >
        <Kicker>THE RULE</Kicker>
        <Strike text="BUY HIGH." delay={30} />
        <Strike text="SELL LOW." delay={110} />
        <div
          style={{
            opacity: op,
            transform: `scale(${scale})`,
            fontFamily: theme.display,
            fontWeight: 800,
            fontSize: 190,
            color: theme.neon,
            textShadow: `0 0 80px ${theme.neon}, 0 0 180px ${theme.neon}55`,
            marginTop: 20,
          }}
        >
          AUTOMATE.
        </div>
        <div
          style={{
            opacity: subOp,
            fontFamily: theme.body,
            fontSize: 42,
            color: theme.muted,
          }}
        >
          Set it. Forget it. Let compounding do the heavy lifting.
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
