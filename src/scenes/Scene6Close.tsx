import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { Backdrop, StaggerHeadline } from "../components/ui";
import { theme } from "../theme";

export const Scene6Close: React.FC = () => {
  const frame = useCurrentFrame();
  const op1 = interpolate(frame, [10, 40], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });
  const brandOp = interpolate(frame, [110, 150], [0, 1], {
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
          gap: 36,
        }}
      >
        <div
          style={{
            opacity: op1,
            fontFamily: theme.body,
            fontSize: 52,
            color: theme.muted,
            fontWeight: 600,
          }}
        >
          The best time to start was ten years ago.
        </div>
        <StaggerHeadline
          words={["The", "second", "best", "time", "is"]}
          startFrame={35}
          fontSize={80}
        />
        <StaggerHeadline
          words={["TODAY."]}
          startFrame={80}
          fontSize={220}
          color={theme.neon}
          glow={theme.neon}
        />
        <div
          style={{
            opacity: brandOp,
            fontFamily: theme.body,
            fontSize: 30,
            letterSpacing: 12,
            color: theme.cyan,
            fontWeight: 700,
            marginTop: 30,
          }}
        >
          CRACKIT FINANCE
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
