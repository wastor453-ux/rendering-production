import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { P } from "../theme";

const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** Ambient 4-point mesh gradient — slow continuous drift, never static. */
export const MeshBackground: React.FC = () => {
  const frame = useCurrentFrame();
  // Two slow drift cycles (60s and 90s) so the loop point is invisible
  const t1 = interpolate(frame, [0, 1800], [0, Math.PI * 2], {
    ...CLAMP,
    easing: Easing.linear,
  });
  const t2 = interpolate(frame, [0, 2700], [0, Math.PI * 2], {
    ...CLAMP,
    easing: Easing.linear,
  });
  const x1 = 30 + 12 * Math.sin(t1);
  const y1 = 30 + 10 * Math.cos(t1 * 0.7);
  const x2 = 70 + 12 * Math.cos(t2 * 0.8);
  const y2 = 65 + 10 * Math.sin(t2);
  const x3 = 50 + 15 * Math.sin(t2 * 0.5 + 1);
  const y3 = 50 + 12 * Math.cos(t1 * 0.6 + 2);

  return (
    <AbsoluteFill
      style={{
        background: `
          radial-gradient(ellipse 55% 45% at ${x1}% ${y1}%, ${P.indigo} 0%, transparent 70%),
          radial-gradient(ellipse 50% 45% at ${x2}% ${y2}%, ${P.purple} 0%, transparent 70%),
          radial-gradient(ellipse 45% 40% at ${x3}% ${y3}%, ${P.neonBlue} 0%, transparent 70%),
          radial-gradient(ellipse 40% 35% at ${100 - x1}% ${100 - y1}%, ${P.magenta} 0%, transparent 70%),
          ${P.deepBg}
        `,
      }}
    />
  );
};
