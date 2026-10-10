import React from "react";
import { AbsoluteFill, Easing, interpolate, Sequence, useCurrentFrame } from "remotion";
import { LightCanvas, GlassCard, Kicker } from "../light/primitives";
import { HeroTypography } from "../light/editorial";
import { T } from "../light/tokens";
import { CARD_W, PAGE, ALIGN } from "../light/layout";

const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const expo = Easing.bezier(0.16, 1, 0.3, 1);

const CARDS = [
  { who: "BUYERS", what: "Waiting is a strategy now", sub: "inventory builds · sellers get desperate" },
  { who: "OWNERS", what: "Your 3% mortgage is armor", sub: "never trade it for 7.45%" },
  { who: "INVESTORS", what: "$500K → $26K risk-free", sub: "vs $24K rental with all the headaches" },
  { who: "RENTERS", what: "You're not losing", sub: "optionality while owners argue with arithmetic" },
];

/**
 * H6 — The Escape (5574f / 184.8s).
 * Beats: 4 audience cards (0–90s) → landlord math (90–130s) →
 * bull/bear scenarios (130–165s) → dashboard close (165–184s).
 * LAYOUT: left-aligned flow (VISUAL_BRAIN §10/§11); audience/scenario cards at
 * CARD_W.S tier; landlord math and scenarios stay symmetric comparisons
 * (ALIGN.comparison) inside left-placed cards.
 */
export const H6Escape: React.FC = () => {
  const frame = useCurrentFrame();

  const mOp = interpolate(frame, [2700, 2740], [0, 1], CLAMP);
  const mOut = interpolate(frame, [3900, 3950], [1, 0], CLAMP);
  const mPulse = interpolate(frame, [2850, 2856, 2868], [1, 1.08, 1], CLAMP);

  const sOp = interpolate(frame, [4000, 4040], [0, 1], CLAMP);
  const sOut = interpolate(frame, [5000, 5050], [1, 0], CLAMP);

  const dOp = interpolate(frame, [5100, 5140], [0, 1], CLAMP);

  return (
    <LightCanvas>

      {/* BEAT 1: audience cards */}
      <AbsoluteFill style={{ justifyContent: "center", paddingLeft: PAGE.marginX, paddingRight: PAGE.marginX }}>
        <div style={{ maxWidth: CARD_W.L, display: "grid", gridTemplateColumns: "1fr 1fr", gap: PAGE.gapCard }}>
          {CARDS.map((c, i) => {
            const d = 60 + i * 700;
            const p = interpolate(frame, [d, d + 24], [0, 1], { ...CLAMP, easing: expo });
            const y = interpolate(p, [0, 1], [50, 0], CLAMP);
            const out = interpolate(frame, [2400, 2450], [1, 0], CLAMP);
            return (
              <div key={c.who} style={{ opacity: p * out, transform: `translateY(${y}px)` }}>
                <GlassCard width={CARD_W.S}>
                  <div style={{ fontFamily: T.font, padding: "16px 24px" }}>
                    <div style={{ fontWeight: 800, fontSize: 26, letterSpacing: 6, color: T.primary }}>{c.who}</div>
                    <div style={{ fontWeight: 800, fontSize: 38, color: T.ink, marginTop: 8 }}>{c.what}</div>
                    <div style={{ fontWeight: 600, fontSize: 26, color: T.inkMuted, marginTop: 6 }}>{c.sub}</div>
                  </div>
                </GlassCard>
              </div>
            );
          })}
        </div>
      </AbsoluteFill>

      {/* BEAT 2: landlord math — symmetric comparison, centered inside left-placed card */}
      <AbsoluteFill style={{ justifyContent: "center", paddingLeft: PAGE.marginX, paddingRight: PAGE.marginX, opacity: mOp * mOut }}>
        <div style={{ maxWidth: CARD_W.L, transform: `scale(${mPulse})` }}>
          <GlassCard width={CARD_W.L}>
            <div style={{ fontFamily: T.font, padding: "16px 28px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", textAlign: ALIGN.comparison }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 800, fontSize: 64, color: T.success }}>$26K</div>
                  <div style={{ fontWeight: 600, fontSize: 26, color: T.inkMuted }}>Treasuries · guaranteed<br />no tenants, no toilets</div>
                </div>
                <div style={{ fontWeight: 800, fontSize: 56, color: T.inkMuted, alignSelf: "center" }}>vs</div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 800, fontSize: 64, color: T.negative }}>$24K</div>
                  <div style={{ fontWeight: 600, fontSize: 26, color: T.inkMuted }}>Rental · all the headaches<br />on the same $500K</div>
                </div>
              </div>
            </div>
          </GlassCard>
        </div>
      </AbsoluteFill>

      {/* BEAT 3: scenarios — symmetric comparison pair, centered inside left-placed cards */}
      <AbsoluteFill style={{ justifyContent: "center", paddingLeft: PAGE.marginX, paddingRight: PAGE.marginX, opacity: sOp * sOut }}>
        <div style={{ display: "flex", gap: PAGE.gapCard }}>
          <GlassCard width={CARD_W.S}>
            <div style={{ fontFamily: T.font, padding: "16px 28px", textAlign: ALIGN.comparison }}>
              <div style={{ fontWeight: 800, fontSize: 40, color: T.success }}>BULL CASE</div>
              <div style={{ fontWeight: 600, fontSize: 28, color: T.ink, marginTop: 12 }}>
                Oil under $80 · inflation cools<br />Fed holds · ice thaws slowly
              </div>
            </div>
          </GlassCard>
          <GlassCard width={CARD_W.S}>
            <div style={{ fontFamily: T.font, padding: "16px 28px", textAlign: ALIGN.comparison }}>
              <div style={{ fontWeight: 800, fontSize: 40, color: T.negative }}>BEAR CASE</div>
              <div style={{ fontWeight: 600, fontSize: 28, color: T.ink, marginTop: 12 }}>
                Oil above $100 · Fed hikes again<br />mortgages touch 8%
              </div>
            </div>
          </GlassCard>
        </div>
      </AbsoluteFill>

      {/* BEAT 4: dashboard */}
      <AbsoluteFill style={{ justifyContent: "center", paddingLeft: PAGE.marginX, paddingRight: PAGE.marginX, opacity: dOp }}>
        <div style={{ maxWidth: CARD_W.L, textAlign: ALIGN.hero }}>
          <Sequence from={5100}>
            <HeroTypography
              kicker=""
              lines={["Watch Brent crude", "and the 10-year yield.", "That's your dashboard."]}
              align="left"
            />
          </Sequence>
        </div>
      </AbsoluteFill>
    </LightCanvas>
  );
};
