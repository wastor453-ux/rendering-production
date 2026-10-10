import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { LightCanvas, GlassCard, Kicker } from "../light/primitives";
import { HeroTypography } from "../light/editorial";
import { T } from "../light/tokens";
import { CARD_W, PAGE, ALIGN } from "../light/layout";

const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const expo = Easing.bezier(0.16, 1, 0.3, 1);

/**
 * H1 — Hook (2127f / 69.9s). "The Housing Market Just Broke."
 * Binary fork card: rates collapse — or home prices do.
 * LAYOUT: left-aligned hero (VISUAL_BRAIN §10), CARD_W.M tier, kicker → hero → supporting flow.
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
      <AbsoluteFill style={{ justifyContent: "center", paddingLeft: PAGE.marginX, paddingRight: PAGE.marginX }}>
        <div style={{ maxWidth: CARD_W.L }}>
          <div style={{ opacity: kickerOp, marginBottom: PAGE.gapTight, textAlign: ALIGN.hero }}>
            <Kicker text="THE RATE SHOCK" />
          </div>
          <HeroTypography
            kicker=""
            lines={["The Housing Market", "Just Broke"]}
            accentLine={1}
            align="left"
          />
          <div style={{ opacity: forkOp, transform: `translateY(${forkY}px) scale(${pulse})`, marginTop: PAGE.gapCard }}>
            <GlassCard width={CARD_W.M}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontFamily: T.font, padding: "8px 16px" }}>
                <div style={{ textAlign: "left", flex: 1 }}>
                  <div style={{ fontWeight: 800, fontSize: 44, color: T.successDeep }}>Rates collapse</div>
                  <div style={{ fontWeight: 600, fontSize: 26, color: T.inkMuted }}>or</div>
                </div>
                <div style={{ fontWeight: 800, fontSize: 60, color: T.inkMuted, padding: "0 24px" }}>?</div>
                <div style={{ textAlign: "left", flex: 1 }}>
                  <div style={{ fontWeight: 800, fontSize: 44, color: T.negativeDeep }}>Home prices do</div>
                  <div style={{ fontWeight: 600, fontSize: 26, color: T.inkMuted }}>one has to give</div>
                </div>
              </div>
            </GlassCard>
          </div>
        </div>
      </AbsoluteFill>
    </LightCanvas>
  );
};
