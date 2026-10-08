import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { MeshBackground } from "../premium/components/MeshBackground";
import { KineticHeadline } from "../premium/components/Type";
import { P } from "../premium/theme";

const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const expo = Easing.bezier(0.16, 1, 0.3, 1);

/**
 * MD1 — Hook (450f / 14.0s). "Your money is DYING while you sleep."
 * SFX sync: tick@"dying" (42f) → accent pulse; coin@"savings account" (300f)
 * → chip pulse; impact@"obituary" (402f) → headline thump.
 */
export const MD1Hook: React.FC = () => {
  const frame = useCurrentFrame();

  // "dying" accent pulse synced to the tick SFX at 42f
  const dyingPulse = interpolate(frame, [42, 48, 60], [1, 1.12, 1], { ...CLAMP, easing: expo });

  // savings chip slides in, pulses on the coin SFX at 300f
  const chipP = interpolate(frame, [270, 288], [0, 1], { ...CLAMP, easing: expo });
  const chipPulse = interpolate(frame, [300, 306, 318], [1, 1.15, 1], { ...CLAMP, easing: expo });
  const chipX = interpolate(chipP, [0, 1], [60, 0], CLAMP);

  // headline thump synced to the impact SFX at 402f
  const thump = interpolate(frame, [402, 408, 422], [1, 0.96, 1], { ...CLAMP, easing: expo });

  return (
    <AbsoluteFill>
      <MeshBackground />
      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: "center",
          flexDirection: "column",
          gap: 32,
          transform: `scale(${thump * dyingPulse})`,
        }}
      >
        <div
          style={{
            fontFamily: P.font,
            fontWeight: 800,
            fontSize: 30,
            letterSpacing: 14,
            color: P.neonBlue,
            opacity: interpolate(frame, [5, 20], [0, 1], CLAMP),
          }}
        >
          THE SLOW LEAK
        </div>
        <div style={{ textAlign: "center" }}>
          <KineticHeadline
            lines={["Your money is dying", "while you sleep"]}
            accentWord="dying"
            delay={10}
            fontSize={110}
          />
        </div>
        {/* savings chip — visual anchor for the coin SFX */}
        <div
          style={{
            opacity: chipP,
            transform: `translateX(${chipX}px) scale(${chipPulse})`,
            background: P.glassFill,
            border: `1px solid ${P.glassBorder}`,
            borderRadius: 20,
            padding: "16px 36px",
            fontFamily: P.font,
            fontWeight: 700,
            fontSize: 34,
            color: P.ink,
            letterSpacing: 4,
          }}
        >
          SAVINGS ACCOUNT · 0.5%
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
