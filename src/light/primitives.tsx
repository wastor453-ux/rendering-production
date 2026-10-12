// Light primitives v2.0 — Visual System from Hamza's A-to-Z Package (2026-10-12)
// Blur is NEVER applied to the reading layer — only to background atmosphere.
import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { T, CLAMP, EXPO } from "./tokens";
import { useMaterial } from "./materialTheme";

const expo = Easing.bezier(...EXPO);

export const entry = (local: number, delay = 0, span = 18) => {
  const p = interpolate(local, [delay, delay + span], [0, 1], { ...CLAMP, easing: expo });
  return { p, opacity: p, y: interpolate(p, [0, 1], [36, 0], CLAMP) };
};

/**
 * LightCanvas v2.0 — 5-layer atmospheric background (from A-to-Z Visual System).
 *
 * Layer 01 — Base wash: linear 135° #F8FBFF → #F1F6FF → #EFEDFF (never flat)
 * Layer 02 — Blue bloom: radial at 9%/9%, #5393FF at 24%, blur 100-180px
 * Layer 03 — Lavender bloom: radial at 92%/24%, #8C7BFF at 16%, blur 120-220px
 * Layer 04 — Cyan bloom: radial at 66%/100%, #31B9F4 at 12%, blur 100-180px
 * Layer 05 — Foreground: crisp content (0px blur, 100% sharp)
 *
 * RULE: Background is soft and atmospheric; foreground stays sharp.
 * The whole frame is NOT blurry — only the background layers are.
 */
export const LightCanvas: React.FC<{
  children?: React.ReactNode;
  /** Background family: coolBlue | lavenderHorizon | glassAurora | softOrb | dataAtmosphere | calmExecutive */
  variant?: "coolBlue" | "lavenderHorizon" | "glassAurora" | "softOrb" | "dataAtmosphere" | "calmExecutive";
}> = ({ children, variant = "coolBlue" }) => {
  const M = useMaterial();

  // Variant-specific bloom positions (from ZIP background recipes)
  const blooms = {
    coolBlue: { blue: { top: "-15%", left: "-10%" }, lavender: { top: "-5%", right: "-8%" }, cyan: { bottom: "-12%", left: "55%" } },
    lavenderHorizon: { blue: { top: "-8%", right: "-10%" }, lavender: { top: "-12%", left: "-8%" }, cyan: { bottom: "-10%", left: "60%" } },
    glassAurora: { blue: { top: "-10%", left: "20%" }, lavender: { top: "30%", right: "-12%" }, cyan: { bottom: "-15%", left: "-5%" } },
    softOrb: { blue: { top: "10%", left: "-15%" }, lavender: { top: "40%", right: "-10%" }, cyan: { bottom: "20%", left: "70%" } },
    dataAtmosphere: { blue: { top: "-12%", left: "30%" }, lavender: { top: "-8%", right: "20%" }, cyan: { bottom: "-8%", left: "40%" } },
    calmExecutive: { blue: { top: "-5%", right: "-5%" }, lavender: { top: "80%", left: "-10%" }, cyan: { bottom: "-15%", right: "30%" } },
  }[variant];

  return (
  <AbsoluteFill style={{
    background: "linear-gradient(135deg, #F8FBFF 0%, #F1F6FF 48%, #EFEDFF 100%)",
    overflow: "hidden",
  }}>
    {/* Layer 02 — Blue bloom */}
    <div style={{
      position: "absolute", width: 1100, height: 1100, borderRadius: "50%",
      background: `radial-gradient(ellipse, ${T.bloomBlue} 0%, transparent 70%)`,
      opacity: T.bloomBlueOpacity, filter: "blur(140px)",
      ...blooms.blue,
    }} />
    {/* Layer 03 — Lavender bloom */}
    <div style={{
      position: "absolute", width: 1200, height: 1200, borderRadius: "50%",
      background: `radial-gradient(ellipse, ${T.lavender} 0%, transparent 70%)`,
      opacity: T.bloomLavenderOpacity, filter: "blur(170px)",
      ...blooms.lavender,
    }} />
    {/* Layer 04 — Cyan bloom */}
    <div style={{
      position: "absolute", width: 900, height: 900, borderRadius: "50%",
      background: `radial-gradient(ellipse, ${T.cyan} 0%, transparent 70%)`,
      opacity: T.bloomCyanOpacity, filter: "blur(140px)",
      ...blooms.cyan,
    }} />
    {/* Layer 05 — Foreground content (crisp) */}
    {children}
  </AbsoluteFill>
  );
};

/**
 * GlassCard v2.0 — from A-to-Z panel recipe.
 * Face: white at 90% | Radius: 18-28px | Border: 1px #D8E6FA at 70%
 * Shadow: 0 10px 30px rgba(40,85,170,0.08) | Backdrop blur: 20px
 */
export const GlassCard: React.FC<{
  width?: number; padding?: number; radius?: number; children: React.ReactNode; style?: React.CSSProperties;
}> = ({ width = 640, padding = 32, radius = T.radiusL, children, style }) => {
  const M = useMaterial();
  return (
  <div style={{
    width, padding, borderRadius: radius,
    background: M.glassFill,
    border: `1px solid ${M.glassBorder}`,
    boxShadow: M.glassShadow,
    backdropFilter: `blur(${T.glassBlur}px)`, WebkitBackdropFilter: `blur(${T.glassBlur}px)`,
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
  const fg = up ? T.successDeep : T.negativeDeep;
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

/**
 * TrustStrip — source, date, units, assumptions (from A-to-Z trust rules).
 * Every data-driven scene must show this.
 */
export const TrustStrip: React.FC<{
  source?: string; date?: string; units?: string; assumptions?: string;
}> = ({ source, date, units, assumptions }) => (
  <div style={{
    fontFamily: T.font, fontSize: 16, fontWeight: 500, color: T.inkMuted,
    display: "flex", gap: 24, marginTop: 16, flexWrap: "wrap",
  }}>
    {source && <span>Source: {source}</span>}
    {date && <span>As of: {date}</span>}
    {units && <span>Units: {units}</span>}
    {assumptions && <span>Assumes: {assumptions}</span>}
  </div>
);

/**
 * IllustrativeLabel — marks placeholder data (from A-to-Z data truth rule).
 * Replace with verified data before publishing.
 */
export const IllustrativeLabel: React.FC = () => (
  <div style={{
    fontFamily: T.font, fontSize: 14, fontWeight: 500, color: T.inkMuted,
    fontStyle: "italic", marginTop: 8,
  }}>
    Illustrative example
  </div>
);
