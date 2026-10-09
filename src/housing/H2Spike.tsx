import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { LightCanvas, GlassCard, Label } from "../light/primitives";
import { LineChart } from "../light/charts";
import { T } from "../light/tokens";

const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const expo = Easing.bezier(0.16, 1, 0.3, 1);

// Mortgage rate climb: Feb 5.99 → Aug 6.77 → mid-Sep 7.12 → Sep 24 7.45
const rates = [5.99, 6.15, 6.3, 6.5, 6.77, 6.95, 7.12, 7.3, 7.45];

/**
 * H2 — The Spike (1626f / 53.2s). Rate chart 5.99 → 7.45 + payment shock card.
 * MIGRATED 2026-10-09: Light Premium Fintech (was dark premium/theme).
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
    <LightCanvas>
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", gap: 32 }}>
        <GlassCard width={1360}>
          <div style={{ marginBottom: 8 }}>
            <Label text="30-year fixed mortgage · Feb → Sep 2026" />
          </div>
          <LineChart data={rates} color={T.negative} highlightLast />
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginTop: 16 }}>
            <div style={{ fontFamily: T.font, transform: `scale(${slam})`, transformOrigin: "left bottom", opacity: heroOp }}>
              <div style={{ fontWeight: 800, fontSize: 96, color: T.negative, letterSpacing: -2, fontVariantNumeric: "tabular-nums" }}>
                {hero.toFixed(2)}%
              </div>
              <div style={{ fontWeight: 600, fontSize: 30, color: T.inkMuted }}>
                +19 bps in a single day
              </div>
            </div>
            <div style={{ fontFamily: T.font, fontWeight: 600, fontSize: 28, color: T.inkMuted, opacity: heroOp, textAlign: "right" }}>
              5.99% in February.<br />7.45% by September.
            </div>
          </div>
        </GlassCard>
        <div style={{ opacity: cardOp, transform: `translateY(${cardY}px)` }}>
          <GlassCard width={1100}>
            <div style={{ fontFamily: T.font, textAlign: "center", padding: "8px 16px" }}>
              <div style={{ fontWeight: 800, fontSize: 52, color: T.ink }}>
                +$380<span style={{ fontSize: 32, color: T.inkMuted }}>/month</span>
              </div>
              <div style={{ fontWeight: 600, fontSize: 28, color: T.inkMuted }}>
                on a $400K loan · 6% → 7.45% · $4,500 a year for 30 years
              </div>
            </div>
          </GlassCard>
        </div>
      </AbsoluteFill>
    </LightCanvas>
  );
};
