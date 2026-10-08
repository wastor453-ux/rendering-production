import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
} from "remotion";
import { Backdrop, Kicker } from "../components/ui";
import { theme, fmt$ } from "../theme";

const FULL = 1745504; // 8% 40yr
const DRAG = 1312407; // 7% 40yr (1% fee)
const LOST = FULL - DRAG; // 433,097

const Bar: React.FC<{
  label: string;
  value: number;
  max: number;
  color: string;
  delay: number;
  width: number;
}> = ({ label, value, max, color, delay, width }) => {
  const frame = useCurrentFrame();
  const w = interpolate(frame - delay, [0, 70], [0, (value / max) * width], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.exp),
  });
  const op = interpolate(frame - delay, [0, 12], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <div style={{ opacity: op, width: width + 420 }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "baseline",
          marginBottom: 14,
        }}
      >
        <span style={{ fontFamily: theme.body, fontSize: 38, fontWeight: 700, color: theme.text }}>
          {label}
        </span>
        <span
          style={{
            fontFamily: theme.display,
            fontWeight: 800,
            fontSize: 64,
            color,
            textShadow: `0 0 40px ${color}66`,
            fontVariantNumeric: "tabular-nums",
          }}
        >
          {fmt$(value)}
        </span>
      </div>
      <div
        style={{
          width,
          height: 64,
          borderRadius: 32,
          background: theme.panel,
          border: `2px solid ${theme.panelBorder}`,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            width: w,
            height: "100%",
            borderRadius: 32,
            background: `linear-gradient(90deg, ${color}88, ${color})`,
            boxShadow: `0 0 40px ${color}66`,
          }}
        />
      </div>
    </div>
  );
};

export const Scene5Fees: React.FC = () => {
  const frame = useCurrentFrame();
  const calloutOp = interpolate(frame, [200, 240], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.back),
  });
  const calloutY = interpolate(frame, [200, 250], [40, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
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
          gap: 72,
        }}
      >
        <Kicker>THE FEE TRAP</Kicker>
        <Bar label="0.1% annual fee" value={FULL} max={FULL} color={theme.neon} delay={40} width={1100} />
        <Bar label="1.0% annual fee" value={DRAG} max={FULL} color={theme.red} delay={110} width={1100} />
        <div
          style={{
            opacity: calloutOp,
            transform: `translateY(${calloutY}px)`,
            fontFamily: theme.display,
            fontWeight: 800,
            fontSize: 72,
            color: theme.red,
            textShadow: `0 0 44px ${theme.red}88`,
          }}
        >
          That "tiny" fee cost {fmt$(LOST)}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
