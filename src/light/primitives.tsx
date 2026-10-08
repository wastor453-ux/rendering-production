// Light primitives: canvas background, glass card, kickers, labels, metrics.
// Blur is NEVER applied to the reading layer — only to background blobs.
import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { T, CLAMP, EXPO } from "./tokens";

const expo = Easing.bezier(...EXPO);

export const entry = (local: number, delay = 0, span = 18) => {
  const p = interpolate(local, [delay, delay + span], [0, 1], { ...CLAMP, easing: expo });
  return { p, opacity: p, y: interpolate(p, [0, 1], [36, 0], CLAMP) };
};

/** Light canvas: bright base + soft blurred atmosphere blobs (background only). */
import { AbsoluteFill } from "remotion";
import { T } from "./tokens";
import { useMaterial } from "./materialTheme";

/** Light canvas with atmospheric background blobs. Material-aware (A/B test). */
export const LightCanvas: React.FC<{ children?: React.ReactNode }> = ({ children }) => {
  const M = useMaterial();
  return (
  <AbsoluteFill style={{ background: M.canvas, overflow: "hidden" }}>
    <div style={{ position: "absolute", inset: 0, filter: "blur(90px)", opacity: M.blobOpacity }}>
      <div style={{ position: "absolute", width: 900, height: 900, borderRadius: "50%", background: T.lavender, opacity: M.blobLavenderOpacity, top: -260, left: -180 }} />
      <div style={{ position: "absolute", width: 760, height: 760, borderRadius: "50%", background: T.blueTint, opacity: M.blobBlueOpacity, bottom: -240, right: -140 }} />
      <div style={{ position: "absolute", width: 420, height: 420, borderRadius: "50%", background: T.accentPeach, opacity: M.blobPeachOpacity, top: "38%", left: "58%" }} />
    </div>
    {children}
  </AbsoluteFill>
  );
};

/** Premium light glass card. No blur on children — the card itself is translucent. Material-aware. */
export const GlassCard: React.FC<{
  width?: number; padding?: number; radius?: number; children: React.ReactNode; style?: React.CSSProperties;
}> = ({ width = 640, padding = 36, radius = T.radiusL, children, style }) => {
  const M = useMaterial();
  return (
  <div style={{
    width, padding, borderRadius: radius,
    background: M.glassFill,
    border: `${M.glassBorderWidth}px solid ${M.glassBorder}`,
    boxShadow: M.glassShadow,
    backdropFilter: "blur(20px)", WebkitBackdropFilter: "blur(20px)",
    ...style,
  }}>
    {children}
  </div>
  );
};

/** Small caps section kicker. */
export const Kicker: React.FC<{ text: string; color?: string }> = ({ text, color = T.primary }) => (
  <div style={{ fontFamily: T.font, fontWeight: 700, fontSize: 22, letterSpacing: 6, color, textTransform: "uppercase" }}>
    {text}
  </div>
);

/** Muted label line. */
export const Label: React.FC<{ text: string; size?: number }> = ({ text, size = 26 }) => (
  <div style={{ fontFamily: T.font, fontWeight: 600, fontSize: size, color: T.inkMuted }}>
    {text}
  </div>
);

/** Animated number with exact snap on the final frame. */
export const CountUp: React.FC<{
  value: number; prefix?: string; suffix?: string; decimals?: number;
  fontSize?: number; color?: string; weight?: number; duration?: number;
}> = ({ value, prefix = "", suffix = "", decimals = 0, fontSize = 120, color = T.ink, weight = 800, duration = 45 }) => {
  const frame = useCurrentFrame();
  const done = frame >= duration;
  const v = done ? value : value * Easing.out(Easing.exp)(interpolate(frame, [0, duration], [0, 1], CLAMP));
  const text = prefix + v.toLocaleString("en-US", { minimumFractionDigits: decimals, maximumFractionDigits: decimals }) + suffix;
  return (
    <div style={{ fontFamily: T.font, fontWeight: weight, fontSize, color, letterSpacing: -2, fontVariantNumeric: "tabular-nums", lineHeight: 1.05 }}>
      {text}
    </div>
  );
};

/** Small delta pill (+12.4% / −3.1%). */
export const Delta: React.FC<{ value: number; suffix?: string }> = ({ value, suffix = "%" }) => {
  const up = value >= 0;
  const bg = up ? T.successTint : T.negativeTint;
  const fg = up ? "#1E7F5C" : "#B44A4A";
  return (
    <span style={{
      display: "inline-block", fontFamily: T.font, fontWeight: 700, fontSize: 26,
      color: fg, background: bg, borderRadius: 999, padding: "8px 18px",
    }}>
      {up ? "▲" : "▼"} {Math.abs(value).toFixed(1)}{suffix}
    </span>
  );
};

/** Showcase section header: index + mode name. */
export const SectionHead: React.FC<{ index: string; title: string; local: number }> = ({ index, title, local }) => {
  const { opacity, y } = entry(local, 0, 14);
  return (
    <div style={{ position: "absolute", top: 54, left: 80, opacity, transform: `translateY(${y}px)` }}>
      <div style={{ fontFamily: T.font, fontWeight: 700, fontSize: 20, letterSpacing: 5, color: T.inkMuted }}>{index}</div>
      <div style={{ fontFamily: T.font, fontWeight: 800, fontSize: 34, color: T.ink, marginTop: 4 }}>{title}</div>
    </div>
  );
};
