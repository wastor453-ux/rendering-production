import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { LightBackdrop, LightKicker, LightHeadline, Badge, INK, RED, INDIGO, CLAMP } from "../trial/light";

// S1 — HOOK (0-30s): the millionaire story
export const BankScene1: React.FC = () => {
  const frame = useCurrentFrame();
  const zoom = interpolate(frame, [0, 870], [1, 1.05], {
    ...CLAMP, easing: Easing.inOut(Easing.cubic),
  });
  return (
    <AbsoluteFill>
      <LightBackdrop />
      <AbsoluteFill style={{ transform: `scale(${zoom})`, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 44 }}>
        <LightKicker>Last week</LightKicker>
        <LightHeadline words={["A", "millionaire", "walked", "into", "his", "bank..."]} startFrame={27} fontSize={92} />
        <LightHeadline words={["and", "the", "bank", "said", "NO."]} startFrame={87} fontSize={120} color={RED} />
        <div style={{ marginTop: 20 }}>
          <Badge fontSize={64}>6.7M views</Badge>
        </div>
        <LightHeadline words={["How", "is", "that", "legal?"]} startFrame={300} fontSize={88} color={INDIGO} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
