import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { MeshBackground } from "../premium/components/MeshBackground";
import { GlassCard } from "../premium/components/GlassCard";
import { KineticHeadline, Toast } from "../premium/components/Type";
import { P } from "../premium/theme";

const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const expo = Easing.bezier(0.16, 1, 0.3, 1);

/**
 * MD4 — The fix (579f / 18.3s). "Money that moves survives."
 * SFX sync (scene-local): ticks@90/150/195 on "high-yield savings / T-bills /
 * index funds" → pills pop; coin@270 "three percent" → chip pulse;
 * whoosh@345 "survives" → headline rise; impact@435 "buried" → toast slam;
 * final hit@495 "Build yours." → tagline pulse.
 */
const PILLS = ["High-yield savings", "T-bills", "Index funds"];
const PILL_AT = [90, 150, 195];

export const MD4Takeaway: React.FC = () => {
  const frame = useCurrentFrame();

  const rise = interpolate(frame, [345, 365], [0, -18], { ...CLAMP, easing: expo });
  const slam = interpolate(frame, [435, 441, 453], [1, 1.08, 1], { ...CLAMP, easing: expo });
  const finalPulse = interpolate(frame, [495, 501, 517], [1, 1.1, 1], { ...CLAMP, easing: expo });
  const chipPulse = interpolate(frame, [270, 276, 288], [1, 1.2, 1], { ...CLAMP, easing: expo });

  return (
    <AbsoluteFill>
      <MeshBackground />
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
          <KineticHeadline
            lines={["Money that moves,", "survives"]}
            accentWord="survives"
            delay={8}
            fontSize={104}
          />
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
                  background: P.glassFill,
                  border: `1px solid ${P.glassBorder}`,
                  borderRadius: 18,
                  padding: "14px 30px",
                  fontFamily: P.font,
                  fontWeight: 700,
                  fontSize: 32,
                  color: P.gain,
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
            fontFamily: P.font,
            fontWeight: 800,
            fontSize: 30,
            letterSpacing: 6,
            color: P.neonBlue,
          }}
        >
          OUTRUN 3%
        </div>

        {/* buried toast — slams on the impact SFX at 435f */}
        <div style={{ transform: `scale(${slam})` }}>
          <Toast delay={380} tone="warn">Money that sleeps gets buried</Toast>
        </div>

        <div style={{ transform: `scale(${finalPulse})` }}>
          <GlassCard delay={420} width={900}>
            <div style={{ textAlign: "center", fontFamily: P.font }}>
              <div style={{ fontWeight: 800, fontSize: 54, color: P.ink, letterSpacing: -1 }}>
                Wealth is a legacy.
              </div>
              <div
                style={{
                  fontWeight: 800,
                  fontSize: 54,
                  letterSpacing: -1,
                  background: `linear-gradient(90deg, ${P.purple}, ${P.magenta})`,
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
    </AbsoluteFill>
  );
};
