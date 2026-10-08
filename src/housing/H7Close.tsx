import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { MeshBackground } from "../premium/components/MeshBackground";
import { GlassCard } from "../premium/components/GlassCard";
import { KineticHeadline } from "../premium/components/Type";
import { P } from "../premium/theme";

const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const expo = Easing.bezier(0.16, 1, 0.3, 1);

/**
 * H7 — Close (1155f / 37.5s). "Buy the math." + tagline.
 */
export const H7Close: React.FC = () => {
  const frame = useCurrentFrame();
  const cardOp = interpolate(frame, [500, 530], [0, 1], { ...CLAMP, easing: expo });
  const cardY = interpolate(cardOp, [0, 1], [50, 0], CLAMP);
  const finalPulse = interpolate(frame, [950, 956, 972], [1, 1.08, 1], CLAMP);

  return (
    <AbsoluteFill>
      <MeshBackground />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", gap: 48 }}>
        <div style={{ textAlign: "center" }}>
          <KineticHeadline
            lines={["Don't buy the panic.", "Don't buy the dip.", "Buy the math."]}
            accentWord="math."
            delay={10}
            fontSize={96}
          />
        </div>
        <div style={{ opacity: cardOp, transform: `translateY(${cardY}px) scale(${finalPulse})` }}>
          <GlassCard width={900} delay={0}>
            <div style={{ textAlign: "center", fontFamily: P.font }}>
              <div style={{ fontWeight: 800, fontSize: 54, color: P.ink, letterSpacing: -1 }}>
                Wealth is a legacy.
              </div>
              <div
                style={{
                  fontWeight: 800, fontSize: 54, letterSpacing: -1,
                  background: `linear-gradient(90deg, ${P.purple}, ${P.magenta})`,
                  WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent",
                }}
              >
                Build yours.
              </div>
            </div>
          </GlassCard>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
