import React from "react";
import { AbsoluteFill, Easing, interpolate, Sequence, useCurrentFrame } from "remotion";
import { LightCanvas, GlassCard, Kicker } from "../light/primitives";
import { HeroTypography } from "../light/editorial";
import { T } from "../light/tokens";
import { CARD_W, PAGE, ALIGN } from "../light/layout";

const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const expo = Easing.bezier(0.16, 1, 0.3, 1);

/**
 * H4 — The Debt Spiral (3603f / 119.1s).
 * Beats: $40T counter (0–30s) → $3B/day interest (30–60s) →
 * $320B per point (60–90s) → spiral loop close (90–119s).
 * LAYOUT: left-aligned flow (VISUAL_BRAIN §10/§11); BEAT 1 $40T stays centered
 * as a single hero number (ALIGN.heroNumber).
 */
export const H4Debt: React.FC = () => {
  const frame = useCurrentFrame();
  const num = { fontVariantNumeric: "tabular-nums" } as const;

  // $40T counter 30–700
  const debtP = interpolate(frame, [30, 700], [0, 1], { ...CLAMP, easing: expo });
  const debt = 39 + debtP;
  const dOut = interpolate(frame, [950, 1000], [1, 0], CLAMP);

  // $3B/day 1050–1900
  const iOp = interpolate(frame, [1050, 1090], [0, 1], CLAMP);
  const iOut = interpolate(frame, [1950, 2000], [1, 0], CLAMP);
  const iPulse = interpolate(frame, [1150, 1156, 1168], [1, 1.1, 1], CLAMP);

  // $320B per point 2050–2900
  const pOp = interpolate(frame, [2050, 2090], [0, 1], CLAMP);
  const pOut = interpolate(frame, [2950, 3000], [1, 0], CLAMP);

  // spiral close 3050–end
  const sOp = interpolate(frame, [3050, 3090], [0, 1], CLAMP);
  const spin = interpolate(frame, [3050, 3603], [0, 120], CLAMP);

  return (
    <LightCanvas>

      {/* BEAT 1: debt counter — single hero number, centered per layout law */}
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: dOut }}>
        <div style={{ textAlign: ALIGN.heroNumber }}>
          <Kicker text="US NATIONAL DEBT" />
          <div style={{ fontFamily: T.font, fontWeight: 800, fontSize: 150, color: T.negative, letterSpacing: -4, ...num, marginTop: 16 }}>
            ${debt.toFixed(1)}T
          </div>
          <div style={{ fontFamily: T.font, fontWeight: 600, fontSize: 32, color: T.inkMuted, marginTop: 16 }}>
            $39T → $40T in under six months
          </div>
        </div>
      </AbsoluteFill>

      {/* BEAT 2: interest per day */}
      <AbsoluteFill style={{ justifyContent: "center", paddingLeft: PAGE.marginX, paddingRight: PAGE.marginX, opacity: iOp * iOut }}>
        <div style={{ maxWidth: CARD_W.L, textAlign: ALIGN.hero, transform: `scale(${iPulse})` }}>
          <Sequence from={1050}>
            <HeroTypography kicker="" lines={["Interest alone:", "$3 billion. Per day."]} accentLine={1} align="left" />
          </Sequence>
          <div style={{ fontFamily: T.font, fontWeight: 600, fontSize: 32, color: T.inkMuted, marginTop: 24, textAlign: ALIGN.supporting }}>
            more than Medicare · more than the military · up 12% this year
          </div>
        </div>
      </AbsoluteFill>

      {/* BEAT 3: per-point cost */}
      <AbsoluteFill style={{ justifyContent: "center", paddingLeft: PAGE.marginX, paddingRight: PAGE.marginX, opacity: pOp * pOut }}>
        <div style={{ maxWidth: CARD_W.L }}>
        <GlassCard width={CARD_W.L}>
          <div style={{ fontFamily: T.font, textAlign: ALIGN.hero, padding: "12px 20px" }}>
            <div style={{ fontWeight: 800, fontSize: 72, color: T.ink, ...num }}>
              +1% yield = +$320B<span style={{ fontSize: 36, color: T.inkMuted }}>/year</span>
            </div>
            <div style={{ fontWeight: 600, fontSize: 30, color: T.inkMuted, marginTop: 8 }}>
              on $32 trillion owed to the public
            </div>
          </div>
        </GlassCard>
        </div>
      </AbsoluteFill>

      {/* BEAT 4: spiral */}
      <AbsoluteFill style={{ justifyContent: "center", paddingLeft: PAGE.marginX, paddingRight: PAGE.marginX, opacity: sOp }}>
        <div style={{ maxWidth: CARD_W.L, textAlign: ALIGN.hero }}>
          <div style={{
            fontFamily: T.font, fontWeight: 800, fontSize: 90, color: T.negative,
            display: "inline-block", transform: `rotate(${spin}deg)`,
          }}>
            ⟳
          </div>
          <Sequence from={3050}>
            <HeroTypography
              kicker=""
              lines={["Higher rates → bigger deficit →", "more bonds → higher rates."]}
              align="left"
            />
          </Sequence>
          <div style={{ fontFamily: T.font, fontWeight: 700, fontSize: 34, color: T.warning, marginTop: 24, textAlign: ALIGN.supporting }}>
            The spiral has no exit.
          </div>
        </div>
      </AbsoluteFill>
    </LightCanvas>
  );
};
