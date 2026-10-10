import React from "react";
import { AbsoluteFill, Easing, interpolate, Sequence, useCurrentFrame } from "remotion";
import { LightCanvas, GlassCard } from "../light/primitives";
import { HeroTypography } from "../light/editorial";
import { T } from "../light/tokens";
import { CARD_W, PAGE, ALIGN } from "../light/layout";

const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const expo = Easing.bezier(0.16, 1, 0.3, 1);

/**
 * H7 — Close (1155f / 37.5s). "Buy the math." + tagline.
 * LAYOUT: closing thesis stays centered per layout law (ALIGN.closing);
 * tagline card at CARD_W.M tier.
 */
export const H7Close: React.FC = () => {
  const frame = useCurrentFrame();
  const cardOp = interpolate(frame, [500, 530], [0, 1], { ...CLAMP, easing: expo });
  const cardY = interpolate(cardOp, [0, 1], [50, 0], CLAMP);
  const finalPulse = interpolate(frame, [950, 956, 972], [1, 1.08, 1], CLAMP);

  return (
    <LightCanvas>
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", gap: PAGE.gapSection }}>
        <div style={{ textAlign: ALIGN.closing }}>
          <Sequence from={10}>
            <HeroTypography
              kicker=""
              lines={["Don't buy the panic.", "Don't buy the dip.", "Buy the math."]}
              accentLine={2}
              align="center"
            />
          </Sequence>
        </div>
        <div style={{ opacity: cardOp, transform: `translateY(${cardY}px) scale(${finalPulse})` }}>
          <GlassCard width={CARD_W.M}>
            <div style={{ textAlign: ALIGN.closing, fontFamily: T.font }}>
              <div style={{ fontWeight: 800, fontSize: 54, color: T.ink, letterSpacing: -1 }}>
                Wealth is a legacy.
              </div>
              <div
                style={{
                  fontWeight: 800, fontSize: 54, letterSpacing: -1,
                  background: `linear-gradient(90deg, ${T.primary}, ${T.primaryDeep})`,
                  WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent",
                }}
              >
                Build yours.
              </div>
            </div>
          </GlassCard>
        </div>
      </AbsoluteFill>
    </LightCanvas>
  );
};
