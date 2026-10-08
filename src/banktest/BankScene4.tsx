import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { LightBackdrop, LightKicker, LightHeadline, RED, INK, INDIGO, CLAMP } from "../trial/light";

// S4 — THE BANK RUN (81-123s): what if everyone showed up at once
export const BankScene4: React.FC = () => {
  const frame = useCurrentFrame();
  // crowd dots converge on the bank doors
  const converge = interpolate(frame, [80, 320], [0, 1], { ...CLAMP, easing: Easing.inOut(Easing.cubic) });
  const shake = interpolate(frame, [340, 700], [0, 1], { ...CLAMP });
  const shakeX = shake * Math.sin(frame * 0.9) * 6;
  const dots = Array.from({ length: 24 }, (_, i) => {
    const angle = (i / 24) * Math.PI * 2;
    const r0 = 620, r1 = 150;
    const r = r0 + (r1 - r0) * converge;
    return { x: Math.cos(angle) * r, y: Math.sin(angle) * r * 0.45 };
  });
  return (
    <AbsoluteFill>
      <LightBackdrop />
      <AbsoluteFill style={{ transform: `translateX(${shakeX}px)`, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 30 }}>
        <LightKicker>But here's the uncomfortable part</LightKicker>
        <LightHeadline words={["What", "if", "everyone", "showed", "up", "at", "once?"]} startFrame={10} fontSize={88} />
        <div style={{ position: "relative", width: 900, height: 320, marginTop: 10 }}>
          {/* bank doors */}
          <div style={{ position: "absolute", left: "50%", top: "50%", transform: "translate(-50%,-50%)", width: 190, height: 240, background: "#1A1B25", borderRadius: 22, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 44, color: "#fff" }}>
            BANK
          </div>
          {dots.map((d, i) => (
            <div key={i} style={{ position: "absolute", left: `calc(50% + ${d.x}px)`, top: `calc(50% + ${d.y}px)`, width: 34, height: 34, borderRadius: "50%", background: i % 4 === 0 ? RED : INDIGO, transform: "translate(-50%,-50%)", opacity: 0.85 }} />
          ))}
        </div>
        <LightHeadline words={["The", "bank", "could", "NOT", "pay", "them."]} startFrame={380} fontSize={110} color={RED} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
