import React from "react";
import { AbsoluteFill, Easing, interpolate, Sequence, useCurrentFrame } from "remotion";
import { LightCanvas, GlassCard, Label } from "../light/primitives";
import { HeroTypography } from "../light/editorial";
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
 * H3 — The Autopsy (5448f / 180.6s).
 * Beats: $100-bond seesaw (0–40s) → 30yr 5.5% since 2004 (40–70s) →
 * three forces toasts (70–140s) → foreign demand + regime change (140–180s).
 * LAYOUT: left-aligned flow (VISUAL_BRAIN §10/§11); seesaw stays a symmetric
 * comparison (ALIGN.comparison). Toasts at CARD_W.M tier.
 */
export const H3Autopsy: React.FC = () => {
  const frame = useCurrentFrame();

  // seesaw: price $125 → $80, yield 4% → 6.25% over frames 60–900
  const sawP = interpolate(frame, [60, 900], [0, 1], { ...CLAMP, easing: expo });
  const price = 125 - 45 * sawP;
  const yld = 4 + 2.25 * sawP;
  const seesawOp = interpolate(frame, [30, 60], [0, 1], CLAMP);
  const seesawOut = interpolate(frame, [1050, 1100], [1, 0], CLAMP);

  // yield card 1200–2400
  const yOp = interpolate(frame, [1200, 1240], [0, 1], { ...CLAMP, easing: expo });
  const yOut = interpolate(frame, [2300, 2350], [1, 0], CLAMP);
  const yPulse = interpolate(frame, [1300, 1306, 1318], [1, 1.12, 1], CLAMP);

  // three forces 2500–4200
  const fOut = interpolate(frame, [4250, 4300], [1, 0], CLAMP);

  // regime change close 4350–end
  const rOp = interpolate(frame, [4350, 4390], [0, 1], { ...CLAMP, easing: expo });
  const rY = interpolate(rOp, [0, 1], [40, 0], CLAMP);

  const num = { fontVariantNumeric: "tabular-nums" } as const;

  return (
    <LightCanvas>

      {/* BEAT 1: bond seesaw */}
      <AbsoluteFill style={{ justifyContent: "center", paddingLeft: PAGE.marginX, paddingRight: PAGE.marginX, opacity: seesawOp * seesawOut }}>
        <div style={{ maxWidth: CARD_W.L }}>
        <GlassCard width={CARD_W.L}>
          <div style={{ marginBottom: 24, textAlign: ALIGN.hero }}>
            <Label text="The $100 bond · price vs yield" />
          </div>
          <div style={{ display: "flex", justifyContent: "space-around", fontFamily: T.font }}>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontWeight: 600, fontSize: 28, color: T.inkMuted }}>PRICE</div>
              <div style={{ fontWeight: 800, fontSize: 88, color: T.primary, ...num }}>${price.toFixed(0)}</div>
            </div>
            <div style={{ fontWeight: 800, fontSize: 72, color: T.inkMuted, alignSelf: "center" }}>⚖</div>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontWeight: 600, fontSize: 28, color: T.inkMuted }}>YIELD</div>
              <div style={{ fontWeight: 800, fontSize: 88, color: T.negative, ...num }}>{yld.toFixed(2)}%</div>
            </div>
          </div>
          <div style={{ fontFamily: T.font, fontWeight: 600, fontSize: 28, color: T.inkMuted, textAlign: ALIGN.supporting, marginTop: 24 }}>
            Price falls → yield jumps. Nothing about the bond changed.
          </div>
        </GlassCard>
        </div>
      </AbsoluteFill>

      {/* BEAT 2: 30yr yield */}
      <AbsoluteFill style={{ justifyContent: "center", paddingLeft: PAGE.marginX, paddingRight: PAGE.marginX, opacity: yOp * yOut }}>
        <div style={{ maxWidth: CARD_W.L, textAlign: ALIGN.hero, transform: `scale(${yPulse})` }}>
          <Sequence from={1200}>
            {/* Q004 defect 2026-10-10: supporting line is now a HeroTypography
                prop — renders in-flow below the headline, fading in after the
                entrance settles. The standalone SupportingLine is removed. */}
            <HeroTypography
              kicker=""
              lines={["30-year Treasury:", "5.5%"]}
              accentLine={1}
              align="left"
              supporting="highest since 2004 · 10-year at 5.2%, highest since 2007"
              supportingDelay={34}
            />
          </Sequence>
        </div>
      </AbsoluteFill>

      {/* BEAT 3: three forces */}
      <AbsoluteFill style={{ justifyContent: "center", paddingLeft: PAGE.marginX, paddingRight: PAGE.marginX, opacity: fOut }}>
        <div style={{ maxWidth: CARD_W.L, display: "flex", flexDirection: "column", gap: PAGE.gapCard }}>
        <div style={{ marginBottom: 8, opacity: interpolate(frame, [2500, 2540], [0, 1], CLAMP) }}>
          <Sequence from={2500}>
            <HeroTypography kicker="" lines={["Three forces hit at once"]} align="left" />
          </Sequence>
        </div>
        <LightToast delay={2600}>Inflation: 65 months above 2%</LightToast>
        <LightToast delay={3150}>Oil: $107 a barrel, +22% in a month</LightToast>
        <LightToast delay={3700}>Fed: hiked to 3.75–4.00%</LightToast>
        </div>
      </AbsoluteFill>

      {/* BEAT 4: regime change */}
      <AbsoluteFill style={{ justifyContent: "center", paddingLeft: PAGE.marginX, paddingRight: PAGE.marginX, opacity: rOp }}>
        <div style={{ maxWidth: CARD_W.L, textAlign: ALIGN.hero, transform: `translateY(${rY}px)` }}>
          <Sequence from={4350}>
            <HeroTypography
              kicker=""
              lines={["Foreign buyers are fading.", "This isn't a reaction —", "it's a regime change."]}
              align="left"
            />
          </Sequence>
        </div>
      </AbsoluteFill>
    </LightCanvas>
  );
};
