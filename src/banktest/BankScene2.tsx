import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { LightBackdrop, LightKicker, LightHeadline, Card, INK, RED, INDIGO, CLAMP } from "../trial/light";

// S2 — LENDING (30-55s): you are not storing it, you are lending it
export const BankScene2: React.FC = () => {
  const frame = useCurrentFrame();
  const cardX = interpolate(frame, [60, 110], [-560, 0], { ...CLAMP, easing: Easing.out(Easing.cubic) });
  const cardOp = interpolate(frame, [60, 80], [0, 1], { ...CLAMP });
  return (
    <AbsoluteFill>
      <LightBackdrop />
      <AbsoluteFill style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 40 }}>
        <LightKicker>The first thing nobody told you</LightKicker>
        <LightHeadline words={["You", "are", "NOT", "storing", "it."]} startFrame={10} fontSize={104} />
        <LightHeadline words={["You", "are", "LENDING", "it."]} startFrame={130} fontSize={120} color={INDIGO} />
        <div style={{ opacity: cardOp, transform: `translateX(${cardX}px)`, marginTop: 24 }}>
          <Card>
            <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 54, color: INK, textAlign: "center" }}>
              You → <span style={{ color: RED }}>unsecured creditor</span>
            </div>
            <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontSize: 34, color: "#8A8AA3", textAlign: "center", marginTop: 12 }}>
              standing in line, hoping to get paid back
            </div>
          </Card>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
