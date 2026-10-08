import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { LightBackdrop, LightKicker, LightHeadline, Card, INK, RED, INDIGO, CLAMP } from "../trial/light";

// S5 — FINE PRINT (123-180s): 7-day notice, $10k reports, structuring
export const BankScene5: React.FC = () => {
  const frame = useCurrentFrame();
  const docY = interpolate(frame, [40, 110], [120, 0], { ...CLAMP, easing: Easing.out(Easing.cubic) });
  const docOp = interpolate(frame, [40, 70], [0, 1], { ...CLAMP });
  const stampScale = interpolate(frame, [300, 360], [2.2, 1], { ...CLAMP, easing: Easing.out(Easing.back) });
  const stampOp = interpolate(frame, [300, 320], [0, 1], { ...CLAMP });
  const warnOp = interpolate(frame, [700, 740], [0, 1], { ...CLAMP });
  return (
    <AbsoluteFill>
      <LightBackdrop />
      <AbsoluteFill style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 34 }}>
        <LightKicker>The account agreement you never read</LightKicker>
        <div style={{ opacity: docOp, transform: `translateY(${docY}px)` }}>
          <Card>
            <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 58, color: INK, textAlign: "center" }}>
              7 days' written notice
            </div>
            <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontSize: 36, color: "#8A8AA3", textAlign: "center", marginTop: 10 }}>
              before you withdraw <span style={{ color: RED, fontWeight: 800 }}>your own money</span>
            </div>
          </Card>
        </div>
        <div style={{ opacity: stampOp, transform: `scale(${stampScale}) rotate(-8deg)`, border: `6px solid ${RED}`, borderRadius: 18, padding: "14px 44px", fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 800, fontSize: 64, color: RED }}>
          SIGNED BY YOU
        </div>
        <div style={{ opacity: warnOp }}>
          <LightHeadline words={["Withdraw", "$10,000+", "→", "reported.", "Dodge", "it", "→", "federal", "crime."]} startFrame={0} fontSize={64} color={INDIGO} />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
