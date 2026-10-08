import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { LightBackdrop, LightKicker, LightHeadline, INK, INDIGO, PALE, CLAMP } from "../trial/light";

// S3 — FRACTIONAL RESERVE (55-81s): the bank lends most of it out
export const BankScene3: React.FC = () => {
  const frame = useCurrentFrame();
  // the split bar: lent portion grows, kept portion stays thin
  const lentW = interpolate(frame, [120, 260], [0, 1180], { ...CLAMP, easing: Easing.out(Easing.cubic) });
  const keptW = interpolate(frame, [200, 300], [0, 220], { ...CLAMP, easing: Easing.out(Easing.cubic) });
  const labelOp = interpolate(frame, [300, 330], [0, 1], { ...CLAMP });
  return (
    <AbsoluteFill>
      <LightBackdrop />
      <AbsoluteFill style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 36 }}>
        <LightKicker>Fractional reserve banking</LightKicker>
        <LightHeadline words={["The", "bank", "lends", "most", "of", "it", "out"]} startFrame={10} fontSize={92} />
        <div style={{ width: 1400, marginTop: 30 }}>
          <div style={{ display: "flex", height: 110, borderRadius: 24, overflow: "hidden", background: PALE, boxShadow: "0 18px 50px rgba(79,70,229,0.18)" }}>
            <div style={{ width: lentW, background: `linear-gradient(90deg, ${INDIGO}, #8B5CF6)` }} />
            <div style={{ width: keptW, background: "#1A1B25" }} />
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 18, opacity: labelOp, fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, fontSize: 38 }}>
            <span style={{ color: INDIGO }}>Lent out — mortgages, credit cards, loans</span>
            <span style={{ color: INK }}>Kept: a fraction</span>
          </div>
        </div>
        <LightHeadline words={["Your", "balance", "is", "an", "IOU."]} startFrame={420} fontSize={104} color={INK} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
