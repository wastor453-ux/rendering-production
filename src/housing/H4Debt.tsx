import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { MeshBackground } from "../premium/components/MeshBackground";
import { GlassCard } from "../premium/components/GlassCard";
import { KineticHeadline } from "../premium/components/Type";
import { P } from "../premium/theme";

const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const expo = Easing.bezier(0.16, 1, 0.3, 1);

/**
 * H4 — The Debt Spiral (3603f / 119.1s).
 * Beats: $40T counter (0–30s) → $3B/day interest (30–60s) →
 * $320B per point (60–90s) → spiral loop close (90–119s).
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
    <AbsoluteFill>
      <MeshBackground />

      {/* BEAT 1: debt counter */}
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: dOut }}>
        <div style={{ textAlign: "center" }}>
          <div style={{ fontFamily: P.font, fontWeight: 800, fontSize: 30, letterSpacing: 12, color: P.neonBlue, marginBottom: 16 }}>
            US NATIONAL DEBT
          </div>
          <div style={{ fontFamily: P.font, fontWeight: 800, fontSize: 150, color: P.loss, letterSpacing: -4, ...num }}>
            ${debt.toFixed(1)}T
          </div>
          <div style={{ fontFamily: P.font, fontWeight: 600, fontSize: 32, color: P.muted, marginTop: 16 }}>
            $39T → $40T in under six months
          </div>
        </div>
      </AbsoluteFill>

      {/* BEAT 2: interest per day */}
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: iOp * iOut }}>
        <div style={{ textAlign: "center", transform: `scale(${iPulse})` }}>
          <KineticHeadline lines={["Interest alone:", "$3 billion. Per day."]} accentWord="$3" delay={1060} fontSize={96} />
          <div style={{ fontFamily: P.font, fontWeight: 600, fontSize: 32, color: P.muted, marginTop: 24 }}>
            more than Medicare · more than the military · up 12% this year
          </div>
        </div>
      </AbsoluteFill>

      {/* BEAT 3: per-point cost */}
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: pOp * pOut }}>
        <GlassCard width={1150} delay={0}>
          <div style={{ fontFamily: P.font, textAlign: "center", padding: "12px 20px" }}>
            <div style={{ fontWeight: 800, fontSize: 72, color: P.ink, ...num }}>
              +1% yield = +$320B<span style={{ fontSize: 36, color: P.muted }}>/year</span>
            </div>
            <div style={{ fontWeight: 600, fontSize: 30, color: P.muted, marginTop: 8 }}>
              on $32 trillion owed to the public
            </div>
          </div>
        </GlassCard>
      </AbsoluteFill>

      {/* BEAT 4: spiral */}
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: sOp }}>
        <div style={{ textAlign: "center" }}>
          <div style={{
            fontFamily: P.font, fontWeight: 800, fontSize: 90, color: P.loss,
            display: "inline-block", transform: `rotate(${spin}deg)`,
          }}>
            ⟳
          </div>
          <KineticHeadline
            lines={["Higher rates → bigger deficit →", "more bonds → higher rates."]}
            delay={3080}
            fontSize={64}
          />
          <div style={{ fontFamily: P.font, fontWeight: 700, fontSize: 34, color: P.gold, marginTop: 24 }}>
            The spiral has no exit.
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
