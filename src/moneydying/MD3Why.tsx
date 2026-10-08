import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { MeshBackground } from "../premium/components/MeshBackground";
import { KineticHeadline, Toast } from "../premium/components/Type";

/**
 * MD3 — Why it works (495f / 15.5s). Three toasts, then the punchline.
 * SFX sync (scene-local): tick@105 "seven percent", tick@219 "no headlines",
 * whoosh@324 "invisible" → punchline drift, impact@435 "why it works" → thump.
 */
const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const expo = Easing.bezier(0.16, 1, 0.3, 1);

export const MD3Why: React.FC = () => {
  const frame = useCurrentFrame();

  // punchline drifts on the whoosh SFX at 324f, thumps on impact at 435f
  const drift = interpolate(frame, [324, 360], [0, -14], { ...CLAMP, easing: expo });
  const thump = interpolate(frame, [435, 441, 455], [1, 0.95, 1], { ...CLAMP, easing: expo });

  return (
    <AbsoluteFill>
      <MeshBackground />
      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: "center",
          flexDirection: "column",
          gap: 28,
          transform: `translateY(${drift}px) scale(${thump})`,
        }}
      >
        <Toast delay={60} tone="info">No crash</Toast>
        <Toast delay={140} tone="info">No warning</Toast>
        <Toast delay={219} tone="warn">No headlines</Toast>
        <div style={{ marginTop: 40, textAlign: "center" }}>
          <KineticHeadline
            lines={["A death this slow is invisible —", "which is exactly why it works"]}
            delay={300}
            fontSize={68}
          />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
