import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { MeshBackground } from "../premium/components/MeshBackground";
import { KineticHeadline } from "../premium/components/Type";
import { GlassCard } from "../premium/components/GlassCard";
import { P } from "../premium/theme";

const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const expo = Easing.bezier(0.16, 1, 0.3, 1);

/**
 * H1 — Hook (2127f / 69.9s). "The Housing Market Just Broke."
 * Binary fork card: rates collapse — or home prices do.
 */
export const H1Hook: React.FC = () => {
  const frame = useCurrentFrame();
  const forkOp = interpolate(frame, [150, 175], [0, 1], { ...CLAMP, easing: expo });
  const forkY = interpolate(forkOp, [0, 1], [40, 0], CLAMP);
  // fork card pulses on key beats through the scene
  const pulse = interpolate(frame, [150, 156, 168, 900, 906, 918, 1700, 1706, 1718], [1, 1.08, 1, 1, 1.08, 1, 1, 1.08, 1], CLAMP);

  return (
    <AbsoluteFill>
      <MeshBackground />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", gap: 40 }}>
        <div style={{
          fontFamily: P.font, fontWeight: 800, fontSize: 30, letterSpacing: 14,
          color: P.neonBlue, opacity: interpolate(frame, [5, 20], [0, 1], CLAMP),
        }}>
          THE RATE SHOCK
        </div>
        <div style={{ textAlign: "center" }}>
          <KineticHeadline
            lines={["The Housing Market", "Just Broke"]}
            accentWord="Broke"
            delay={10}
            fontSize={120}
          />
        </div>
        <div style={{ opacity: forkOp, transform: `translateY(${forkY}px) scale(${pulse})` }}>
          <GlassCard width={1100} delay={0}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontFamily: P.font, padding: "8px 16px" }}>
              <div style={{ textAlign: "center", flex: 1 }}>
                <div style={{ fontWeight: 800, fontSize: 44, color: P.gain }}>Rates collapse</div>
                <div style={{ fontWeight: 600, fontSize: 26, color: P.muted }}>or</div>
              </div>
              <div style={{ fontWeight: 800, fontSize: 60, color: P.muted, padding: "0 24px" }}>?</div>
              <div style={{ textAlign: "center", flex: 1 }}>
                <div style={{ fontWeight: 800, fontSize: 44, color: P.loss }}>Home prices do</div>
                <div style={{ fontWeight: 600, fontSize: 26, color: P.muted }}>one has to give</div>
              </div>
            </div>
          </GlassCard>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
