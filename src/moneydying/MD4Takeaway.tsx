import React from "react";
import { AbsoluteFill, Easing, interpolate, Sequence, useCurrentFrame } from "remotion";
import { LightCanvas, GlassCard } from "../light/primitives";
import { HeroTypography } from "../light/editorial";
import { T } from "../light/tokens";

const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const expo = Easing.bezier(0.16, 1, 0.3, 1);

/**
 * MD4 — The fix (579f / 18.3s). "Money that moves survives."
 * SFX sync (scene-local): ticks@90/150/195 on "high-yield savings / T-bills /
 * index funds" → pills pop; coin@270 "three percent" → chip pulse;
 * whoosh@345 "survives" → headline rise; impact@435 "buried" → toast slam;
 * final hit@495 "Build yours." → tagline pulse.
 * MIGRATED 2026-10-09: Light Premium Fintech (was dark premium/theme).
 */
const PILLS = ["High-yield savings", "T-bills", "Index funds"];
const PILL_AT = [90, 150, 195];

/** Light toast (replaces premium Toast). */
const LightToast: React.FC<{ delay: number; tone: "warn"; children: React.ReactNode }> = ({ delay, children }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [delay, delay + 18], [0, 1], { ...CLAMP, easing: expo });
  return (
    <div style={{
      opacity: p,
      transform: `translateY(${interpolate(p, [0, 1], [30, 0], CLAMP)}px)`,
      background: T.warningTint,
      border: `2px solid ${T.warning}`,
      borderRadius: T.radiusM,
      padding: "20px 40px",
      fontFamily: T.font, fontWeight: 700, fontSize: 36, color: T.ink,
      maxWidth: 700, textAlign: "center",
    }}>
      {children}
    </div>
  );
};

export const MD4Takeaway: React.FC = () => {
  const frame = useCurrentFrame();

  const rise = interpolate(frame, [345, 365], [0, -18], { ...CLAMP, easing: expo });
  const slam = interpolate(frame, [435, 441, 453], [1, 1.08, 1], { ...CLAMP, easing: expo });
  const finalPulse = interpolate(frame, [495, 501, 517], [1, 1.1, 1], { ...CLAMP, easing: expo });
  const chipPulse = interpolate(frame, [270, 276, 288], [1, 1.2, 1], { ...CLAMP, easing: expo });

  return (
    <LightCanvas>
      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: "center",
          flexDirection: "column",
          gap: 36,
          transform: `translateY(${rise}px)`,
        }}
      >
        <div style={{ textAlign: "center" }}>
          <Sequence from={8}>
            <HeroTypography
              kicker=""
              lines={["Money that moves,", "survives"]}
              accentLine={1}
            />
          </Sequence>
        </div>

        {/* alternative pills — pop on the tick SFX */}
        <div style={{ display: "flex", gap: 20 }}>
          {PILLS.map((label, i) => {
            const p = interpolate(frame, [PILL_AT[i], PILL_AT[i] + 16], [0, 1], { ...CLAMP, easing: expo });
            const y = interpolate(p, [0, 1], [40, 0], CLAMP);
            return (
              <div
                key={label}
                style={{
                  opacity: p,
                  transform: `translateY(${y}px)`,
                  background: T.glassFill,
                  border: `1px solid ${T.glassBorder}`,
                  borderRadius: 18,
                  padding: "14px 30px",
                  fontFamily: T.font,
                  fontWeight: 700,
                  fontSize: 32,
                  color: T.success,
                }}
              >
                {label}
              </div>
            );
          })}
        </div>

        {/* +3% chip — pulses on the coin SFX at 270f */}
        <div
          style={{
            opacity: interpolate(frame, [240, 256], [0, 1], CLAMP),
            transform: `scale(${chipPulse})`,
            fontFamily: T.font,
            fontWeight: 800,
            fontSize: 30,
            letterSpacing: 6,
            color: T.primary,
          }}
        >
          OUTRUN 3%
        </div>

        {/* buried toast — slams on the impact SFX at 435f */}
        <div style={{ transform: `scale(${slam})` }}>
          <LightToast delay={380} tone="warn">Money that sleeps gets buried</LightToast>
        </div>

        <div style={{ transform: `scale(${finalPulse})` }}>
          <GlassCard width={900}>
            <div style={{ textAlign: "center", fontFamily: T.font }}>
              <div style={{ fontWeight: 800, fontSize: 54, color: T.ink, letterSpacing: -1 }}>
                Wealth is a legacy.
              </div>
              <div
                style={{
                  fontWeight: 800,
                  fontSize: 54,
                  letterSpacing: -1,
                  background: `linear-gradient(90deg, ${T.primary}, ${T.primaryDeep})`,
                  WebkitBackgroundClip: "text",
                  backgroundClip: "text",
                  color: "transparent",
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
