import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { MeshBackground } from "../premium/components/MeshBackground";
import { GlassCard } from "../premium/components/GlassCard";
import { MoneyFlowChart } from "../premium/components/MoneyFlowChart";
import { P } from "../premium/theme";

const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const expo = Easing.bezier(0.16, 1, 0.3, 1);

// Mortgage rate climb: Feb 5.99 → Aug 6.77 → mid-Sep 7.12 → Sep 24 7.45
const rates = [5.99, 6.15, 6.3, 6.5, 6.77, 6.95, 7.12, 7.3, 7.45];

/**
 * H2 — The Spike (1626f / 53.2s). Rate chart 5.99 → 7.45 + payment shock card.
 */
export const H2Spike: React.FC = () => {
  const frame = useCurrentFrame();
  const drawP = interpolate(frame, [20, 320], [0, 1], { ...CLAMP, easing: expo });
  const hero = 5.99 + (7.45 - 5.99) * drawP;
  const heroOp = interpolate(frame, [300, 320], [0, 1], { ...CLAMP, easing: expo });
  // spike slam near the end of the draw (the "jump" moment)
  const slam = interpolate(frame, [300, 306, 322], [1, 1.15, 1], { ...CLAMP, easing: expo });
  const cardOp = interpolate(frame, [700, 730], [0, 1], { ...CLAMP, easing: expo });
  const cardY = interpolate(cardOp, [0, 1], [40, 0], CLAMP);

  return (
    <AbsoluteFill>
      <MeshBackground />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", gap: 32 }}>
        <GlassCard width={1360} delay={5}>
          <div style={{ fontFamily: P.font, fontWeight: 700, fontSize: 34, color: P.muted, marginBottom: 8 }}>
            30-year fixed mortgage · Feb → Sep 2026
          </div>
          <MoneyFlowChart values={rates} delay={20} drawFrames={300} color1={P.gold} color2={P.loss} />
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginTop: 16 }}>
            <div style={{ fontFamily: P.font, transform: `scale(${slam})`, transformOrigin: "left bottom", opacity: heroOp }}>
              <div style={{ fontWeight: 800, fontSize: 96, color: P.loss, letterSpacing: -2, fontVariantNumeric: "tabular-nums" }}>
                {hero.toFixed(2)}%
              </div>
              <div style={{ fontWeight: 600, fontSize: 30, color: P.muted }}>
                +19 bps in a single day
              </div>
            </div>
            <div style={{ fontFamily: P.font, fontWeight: 600, fontSize: 28, color: P.muted, opacity: heroOp, textAlign: "right" }}>
              5.99% in February.<br />7.45% by September.
            </div>
          </div>
        </GlassCard>
        <div style={{ opacity: cardOp, transform: `translateY(${cardY}px)` }}>
          <GlassCard width={1100} delay={0}>
            <div style={{ fontFamily: P.font, textAlign: "center", padding: "8px 16px" }}>
              <div style={{ fontWeight: 800, fontSize: 52, color: P.ink }}>
                +$380<span style={{ fontSize: 32, color: P.muted }}>/month</span>
              </div>
              <div style={{ fontWeight: 600, fontSize: 28, color: P.muted }}>
                on a $400K loan · 6% → 7.45% · $4,500 a year for 30 years
              </div>
            </div>
          </GlassCard>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
