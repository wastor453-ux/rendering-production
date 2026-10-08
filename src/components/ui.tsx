import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme, fmt$ } from "../theme";

const CLAMP = {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
} as const;

/** Dark grid backdrop with vignette — the channel's base layer */
export const Backdrop: React.FC = () => {
  const frame = useCurrentFrame();
  const drift = interpolate(frame, [0, 900], [0, 60], {
    extrapolateLeft: "clamp",
    extrapolateRight: "extend",
    easing: Easing.linear,
  });
  return (
    <AbsoluteFill style={{ background: theme.bg }}>
      <AbsoluteFill
        style={{
          backgroundImage: `linear-gradient(${theme.grid} 1px, transparent 1px), linear-gradient(90deg, ${theme.grid} 1px, transparent 1px)`,
          backgroundSize: "64px 64px",
          backgroundPosition: `${-drift}px ${-drift / 2}px`,
          opacity: 0.9,
        }}
      />
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse 90% 70% at 50% 45%, transparent 40%, rgba(3,6,12,0.85) 100%)",
        }}
      />
      {/* top neon hairline */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: 4,
          background: `linear-gradient(90deg, ${theme.neon}, ${theme.cyan})`,
          opacity: 0.9,
        }}
      />
    </AbsoluteFill>
  );
};

export const Kicker: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const frame = useCurrentFrame();
  const op = interpolate(frame, [0, 15], [0, 1], {
    ...CLAMP,
    easing: Easing.out(Easing.quad),
  });
  const y = interpolate(frame, [0, 20], [24, 0], {
    ...CLAMP,
    easing: Easing.out(Easing.cubic),
  });
  return (
    <div
      style={{
        opacity: op,
        transform: `translateY(${y}px)`,
        fontFamily: theme.body,
        fontSize: 30,
        letterSpacing: 10,
        color: theme.cyan,
        fontWeight: 700,
      }}
    >
      {children}
    </div>
  );
};

/** Word-staggered kinetic headline */
export const StaggerHeadline: React.FC<{
  words: string[];
  startFrame?: number;
  fontSize?: number;
  color?: string;
  glow?: string;
  lineHeight?: number;
}> = ({
  words,
  startFrame = 0,
  fontSize = 120,
  color = theme.text,
  glow,
  lineHeight = 1.15,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div
      style={{
        fontFamily: theme.display,
        fontWeight: 800,
        fontSize,
        lineHeight,
        color,
        textAlign: "center",
        textShadow: glow ? `0 0 60px ${glow}, 0 0 140px ${glow}55` : undefined,
      }}
    >
      {words.map((w, i) => {
        const s = spring({
          frame: frame - startFrame - i * 5,
          fps,
          config: { damping: 14, stiffness: 220, mass: 0.9 },
        });
        const op = interpolate(frame - startFrame - i * 5, [0, 10], [0, 1], {
          ...CLAMP,
          easing: Easing.out(Easing.quad),
        });
        const y = interpolate(s, [0, 1], [60, 0], CLAMP);
        const scale = interpolate(s, [0, 1], [0.85, 1], CLAMP);
        return (
          <span
            key={i}
            style={{
              display: "inline-block",
              opacity: op,
              transform: `translateY(${y}px) scale(${scale})`,
              marginRight: fontSize * 0.28,
            }}
          >
            {w}
          </span>
        );
      })}
    </div>
  );
};

/** Frame-driven count-up. Never linear — eases out like a slot machine. */
export const CountUp: React.FC<{
  to: number;
  fromFrame: number;
  toFrame: number;
  fontSize?: number;
  color?: string;
  glow?: string;
  prefix?: string;
  suffix?: string;
}> = ({
  to,
  fromFrame,
  toFrame,
  fontSize = 110,
  color = theme.neon,
  glow,
  prefix = "$",
  suffix = "",
}) => {
  const frame = useCurrentFrame();
  const v = interpolate(frame, [fromFrame, toFrame], [0, to], {
    ...CLAMP,
    easing: Easing.out(Easing.exp),
  });
  return (
    <div
      style={{
        fontFamily: theme.display,
        fontWeight: 800,
        fontSize,
        color,
        textShadow: glow ? `0 0 50px ${glow}` : undefined,
        fontVariantNumeric: "tabular-nums",
      }}
    >
      {prefix}
      {Math.round(v).toLocaleString("en-US")}
      {suffix}
    </div>
  );
};

/** Comparison card with spring entrance */
export const CompareCard: React.FC<{
  title: string;
  value: number;
  sub: string;
  accent: string;
  delay?: number;
  align?: "left" | "right";
}> = ({ title, value, sub, accent, delay = 0, align = "left" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({
    frame: frame - delay,
    fps,
    config: { damping: 16, stiffness: 180 },
  });
  const op = interpolate(frame - delay, [0, 12], [0, 1], {
    ...CLAMP,
    easing: Easing.out(Easing.quad),
  });
  const x = interpolate(s, [0, 1], [align === "left" ? -120 : 120, 0], CLAMP);
  return (
    <div
      style={{
        opacity: op,
        transform: `translateX(${x}px)`,
        background: theme.panel,
        border: `2px solid ${theme.panelBorder}`,
        borderTop: `6px solid ${accent}`,
        borderRadius: 28,
        padding: "48px 56px",
        width: 700,
        boxShadow: `0 24px 80px rgba(0,0,0,0.55), 0 0 60px ${accent}22`,
      }}
    >
      <div
        style={{
          fontFamily: theme.body,
          fontSize: 30,
          letterSpacing: 8,
          color: theme.muted,
          fontWeight: 700,
          marginBottom: 18,
        }}
      >
        {title}
      </div>
      <div
        style={{
          fontFamily: theme.display,
          fontWeight: 800,
          fontSize: 96,
          color: accent,
          textShadow: `0 0 44px ${accent}66`,
          fontVariantNumeric: "tabular-nums",
        }}
      >
        {fmt$(value)}
      </div>
      <div
        style={{
          fontFamily: theme.body,
          fontSize: 32,
          color: theme.muted,
          marginTop: 16,
        }}
      >
        {sub}
      </div>
    </div>
  );
};
