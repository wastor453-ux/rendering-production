import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { Backdrop, Kicker, StaggerHeadline } from "../components/ui";
import { theme } from "../theme";

export const Scene1Hook: React.FC = () => {
  const frame = useCurrentFrame();
  // slow push-in on the whole composition for cinematic depth
  const zoom = interpolate(frame, [0, 221], [1, 1.06], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });
  return (
    <AbsoluteFill>
      <Backdrop />
      <AbsoluteFill
        style={{
          transform: `scale(${zoom})`,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: 40,
        }}
      >
        <Kicker>THE MILLION-DOLLAR HABIT</Kicker>
        <StaggerHeadline
          words={["$500/month", "for", "30", "years"]}
          startFrame={25}
          fontSize={110}
        />
        <StaggerHeadline
          words={["becomes", "$1,000,000"]}
          startFrame={75}
          fontSize={150}
          color={theme.neon}
          glow={theme.neon}
        />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
