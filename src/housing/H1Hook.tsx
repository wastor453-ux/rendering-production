import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { LightCanvas, GlassCard, Kicker } from "../light/primitives";
import { HeroTypography } from "../light/editorial";
import { T } from "../light/tokens";

const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const expo = Easing.bezier(0.16, 1, 0.3, 1);

/**
 * H1 — Hook (2127f / 69.9s). "The Housing Market Just Broke."
 * Binary fork card: rates collapse — or home prices do.
 * MIGRATED 2026-10-09: Light Premium Fintech (was dark premium/theme).
 */
export const H1Hook: React.FC = () => {
  const frame = useCurrentFrame();
  const forkOp = interpolate(frame, [150, 175], [0, 1], { ...CLAMP, easing: expo });
  const forkY = interpolate(forkOp, [0, 1], [40, 0], CLAMP);
  // fork card pulses on key beats through the scene
  const pulse = interpolate(frame, [150, 156, 168, 900, 906, 918, 1700, 1706, 1718], [1, 1.08, 1, 1, 1.08, 1, 1, 1.08, 1], CLAMP);
  const kickerOp = interpolate(frame, [5, 20], [0, 1], CLAMP);

  return (
    <LightCanvas>
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", gap: 40 }}>
        <div style={{ opacity: kickerOp }}>
          <Kicker text="THE RATE SHOCK" />
        </div>
        <HeroTypography
          kicker=""
          lines={["The Housing Market", "Just Broke"]}
          accentLine={1}
        />
        <div style={{ opacity: forkOp, transform: `translateY(${forkY}px) scale(${pulse})` }}>
          <GlassCard width={1100}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontFamily: T.font, padding: "8px 16px" }}>
              <div style={{ textAlign: "center", flex: 1 }}>
                <div style={{ fontWeight: 800, fontSize: 44, color: T.success }}>Rates collapse</div>
                <div style={{ fontWeight: 600, fontSize: 26, color: T.inkMuted }}>or</div>
              </div>
              <div style={{ fontWeight: 800, fontSize: 60, color: T.inkMuted, padding: "0 24px" }}>?</div>
              <div style={{ textAlign: "center", flex: 1 }}>
                <div style={{ fontWeight: 800, fontSize: 44, color: T.negative }}>Home prices do</div>
                <div style={{ fontWeight: 600, fontSize: 26, color: T.inkMuted }}>one has to give</div>
              </div>
            </div>
          </GlassCard>
        </div>
      </AbsoluteFill>
    </LightCanvas>
  );
};
