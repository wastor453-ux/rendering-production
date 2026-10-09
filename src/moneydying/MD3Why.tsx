import React from "react";
import { AbsoluteFill, Easing, interpolate, Sequence, useCurrentFrame } from "remotion";
import { LightCanvas } from "../light/primitives";
import { HeroTypography } from "../light/editorial";
import { T } from "../light/tokens";

/**
 * MD3 — Why it works (495f / 15.5s). Three toasts, then the punchline.
 * SFX sync (scene-local): tick@105 "seven percent", tick@219 "no headlines",
 * whoosh@324 "invisible" → punchline drift, impact@435 "why it works" → thump.
 * MIGRATED 2026-10-09: Light Premium Fintech (was dark premium/theme).
 */
const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const expo = Easing.bezier(0.16, 1, 0.3, 1);

/** Light toast (replaces premium Toast). */
const LightToast: React.FC<{ delay: number; tone: "info" | "warn"; children: React.ReactNode }> = ({ delay, tone, children }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [delay, delay + 18], [0, 1], { ...CLAMP, easing: expo });
  const bg = tone === "warn" ? T.warningTint : T.blueTint;
  const border = tone === "warn" ? T.warning : T.primary;
  return (
    <div style={{
      opacity: p,
      transform: `translateY(${interpolate(p, [0, 1], [30, 0], CLAMP)}px)`,
      background: bg,
      border: `2px solid ${border}`,
      borderRadius: T.radiusM,
      padding: "20px 40px",
      fontFamily: T.font, fontWeight: 700, fontSize: 36, color: T.ink,
      maxWidth: 700, textAlign: "center",
    }}>
      {children}
    </div>
  );
};

export const MD3Why: React.FC = () => {
  const frame = useCurrentFrame();

  // punchline drifts on the whoosh SFX at 324f, thumps on impact at 435f
  const drift = interpolate(frame, [324, 360], [0, -14], { ...CLAMP, easing: expo });
  const thump = interpolate(frame, [435, 441, 455], [1, 0.95, 1], { ...CLAMP, easing: expo });

  return (
    <LightCanvas>
      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: "center",
          flexDirection: "column",
          gap: 28,
          transform: `translateY(${drift}px) scale(${thump})`,
        }}
      >
        <LightToast delay={60} tone="info">No crash</LightToast>
        <LightToast delay={140} tone="info">No warning</LightToast>
        <LightToast delay={219} tone="warn">No headlines</LightToast>
        <div style={{ marginTop: 40, textAlign: "center" }}>
          <Sequence from={300}>
            <HeroTypography
              kicker=""
              lines={["A death this slow is invisible —", "which is exactly why it works"]}
            />
          </Sequence>
        </div>
      </AbsoluteFill>
    </LightCanvas>
  );
};
