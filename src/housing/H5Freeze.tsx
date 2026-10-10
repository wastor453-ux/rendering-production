import React from "react";
import { AbsoluteFill, Easing, interpolate, Sequence, useCurrentFrame } from "remotion";
import { LightCanvas, GlassCard, Label } from "../light/primitives";
import { HeroTypography } from "../light/editorial";
import { BarChart } from "../light/charts";
import { T } from "../light/tokens";
import { CARD_W, PAGE, ALIGN } from "../light/layout";

const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const expo = Easing.bezier(0.16, 1, 0.3, 1);

/** Light toast notification (replaces premium Toast). */
const LightToast: React.FC<{ delay: number; children: React.ReactNode }> = ({ delay, children }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [delay, delay + 18], [0, 1], { ...CLAMP, easing: expo });
  return (
    <div style={{
      opacity: p,
      transform: `translateY(${interpolate(p, [0, 1], [30, 0], CLAMP)}px)`,
      background: T.glassFill,
      border: `1px solid ${T.glassBorder}`,
      borderRadius: T.radiusL,
      padding: "20px 40px",
      fontFamily: T.font, fontWeight: 700, fontSize: 36, color: T.ink,
      maxWidth: CARD_W.M, textAlign: ALIGN.supporting,
    }}>
      {children}
    </div>
  );
};

/**
 * H5 — The Freeze (3618f / 119.6s).
 * Beats: "sales fall first" (0–25s) → 58% seller surplus (25–55s) →
 * −14% / −$62K card (55–85s) → golden cage close (85–119s).
 * LAYOUT: left-aligned flow (VISUAL_BRAIN §10/§11), chart card at CARD_W.L,
 * affordability card at CARD_W.M.
 */
export const H5Freeze: React.FC = () => {
  const frame = useCurrentFrame();

  const sOp = interpolate(frame, [10, 40], [0, 1], CLAMP);
  const sOut = interpolate(frame, [700, 750], [1, 0], CLAMP);

  // seller surplus bar 800–1600
  const bOp = interpolate(frame, [800, 840], [0, 1], CLAMP);
  const bOut = interpolate(frame, [1650, 1700], [1, 0], CLAMP);
  const barW = interpolate(frame, [900, 1300], [0, 1], { ...CLAMP, easing: expo });

  // −14% card 1750–2600
  const cOp = interpolate(frame, [1750, 1790], [0, 1], CLAMP);
  const cOut = interpolate(frame, [2650, 2700], [1, 0], CLAMP);
  const cPulse = interpolate(frame, [1850, 1856, 1868], [1, 1.1, 1], CLAMP);

  // golden cage 2750–end
  const gOp = interpolate(frame, [2750, 2790], [0, 1], CLAMP);

  return (
    <LightCanvas>

      {/* BEAT 1: sequencing */}
      <AbsoluteFill style={{ justifyContent: "center", paddingLeft: PAGE.marginX, paddingRight: PAGE.marginX, opacity: sOp * sOut }}>
        <div style={{ maxWidth: CARD_W.L, textAlign: ALIGN.hero }}>
          <Sequence from={10}>
            <HeroTypography
              kicker=""
              lines={["When rates rise fast,", "sales fall first.", "Not prices."]}
              accentLine={1}
              align="left"
            />
          </Sequence>
        </div>
      </AbsoluteFill>

      {/* BEAT 2: seller surplus */}
      <AbsoluteFill style={{ justifyContent: "center", paddingLeft: PAGE.marginX, paddingRight: PAGE.marginX, opacity: bOp * bOut }}>
        <div style={{ maxWidth: CARD_W.L }}>
        <GlassCard width={CARD_W.L}>
          <div style={{ fontFamily: T.font, padding: "12px 20px" }}>
            <div style={{ marginBottom: 20, textAlign: ALIGN.hero }}>
              <Label text="Sellers vs buyers · Redfin" />
            </div>
            <BarChart
              data={[
                { label: "Sellers", value: 100 },
                { label: "Buyers", value: 63 },
              ]}
              color={T.negative}
              highlight={0}
            />
            <div style={{ fontWeight: 800, fontSize: 44, color: T.negative, textAlign: ALIGN.hero, marginTop: 24 }}>
              +58% more sellers — strongest buyer's market ever recorded
            </div>
          </div>
        </GlassCard>
        </div>
      </AbsoluteFill>

      {/* BEAT 3: affordability gap */}
      <AbsoluteFill style={{ justifyContent: "center", paddingLeft: PAGE.marginX, paddingRight: PAGE.marginX, opacity: cOp * cOut }}>
        <div style={{ maxWidth: CARD_W.M, transform: `scale(${cPulse})` }}>
          <GlassCard width={CARD_W.M}>
            <div style={{ fontFamily: T.font, textAlign: ALIGN.hero, padding: "12px 20px" }}>
              <div style={{ fontWeight: 800, fontSize: 84, color: T.negative }}>−14%</div>
              <div style={{ fontWeight: 700, fontSize: 36, color: T.ink, marginTop: 8 }}>
                ≈ $62,000 off the median home
              </div>
              <div style={{ fontWeight: 600, fontSize: 28, color: T.inkMuted, marginTop: 8 }}>
                just to restore the payment buyers had earlier this year
              </div>
            </div>
          </GlassCard>
        </div>
      </AbsoluteFill>

      {/* BEAT 4: golden cage */}
      <AbsoluteFill style={{ justifyContent: "center", paddingLeft: PAGE.marginX, paddingRight: PAGE.marginX, opacity: gOp }}>
        <div style={{ maxWidth: CARD_W.L, display: "flex", flexDirection: "column", gap: PAGE.gapCard }}>
        <LightToast delay={2760}>Record equity · 3% fixed mortgage</LightToast>
        <div style={{ textAlign: ALIGN.hero }}>
          <Sequence from={2890}>
            <HeroTypography
              kicker=""
              lines={["The golden cage:", "they can't afford to sell."]}
              accentLine={0}
              align="left"
            />
          </Sequence>
        </div>
        </div>
      </AbsoluteFill>
    </LightCanvas>
  );
};
