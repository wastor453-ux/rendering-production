import React from "react";
import { Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { P } from "../theme";

const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const expo = Easing.bezier(0.16, 1, 0.3, 1);

/** Glassmorphism card — 85% white, 25px blur, 1px metallic border. */
export const GlassCard: React.FC<{
  children: React.ReactNode;
  style?: React.CSSProperties;
  delay?: number;
  width?: number;
}> = ({ children, style, delay = 0, width }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - delay, fps, config: { mass: 1, tension: 180, friction: 22 } });
  const clamped = Math.min(Math.max(s, 0), 1.03);
  const opacity = interpolate(frame, [delay, delay + 12], [0, 1], { ...CLAMP, easing: expo });
  const y = interpolate(clamped, [0, 1.03], [36, 0], CLAMP);

  return (
    <div
      style={{
        width,
        background: P.glassFill,
        backdropFilter: `blur(${P.glassBlur}px)`,
        WebkitBackdropFilter: `blur(${P.glassBlur}px)`,
        border: `1px solid ${P.glassBorder}`,
        borderRadius: P.glassRadius,
        boxShadow: "0 24px 64px rgba(15,13,36,0.25), inset 0 1px 0 rgba(255,255,255,0.6)",
        padding: 40,
        opacity,
        transform: `translateY(${y}px) scale(${0.96 + 0.04 * clamped})`,
        ...style,
      }}
    >
      {children}
    </div>
  );
};
