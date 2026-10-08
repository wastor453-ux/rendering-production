import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";

// ─── DECISION_BRAIN §0: unified preset family ──────────────────────────────
// One easing, one timing unit, one stagger. Everything reuses these.
// Calm-sharp premium fintech: ease-out decelerate, soft landings, ≤3% overshoot.

export const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
export const EASE_OUT = Easing.bezier(0.16, 1, 0.3, 1); // easeOutExpo
export const EASE_SMOOTH = Easing.bezier(0.4, 0, 0.2, 1);

export const INK = "#1A1B25";
export const MUTED = "#8A8AA3";
export const INDIGO = "#4F46E5";
export const AMBER = "#F59E0B"; // the ONE keyword accent per scene
export const RED = "#E5484D"; // danger/loss ONLY
export const PAPER = "#FAFAF8";
export const FONT = "'Plus Jakarta Sans', sans-serif";

/** pop: the universal entrance. opacity + scale 0.96→1, 9 frames, easeOut. */
export const pop = (frame: number, start: number, dur = 9) => {
  const t = interpolate(frame, [start, start + dur], [0, 1], { ...CLAMP, easing: EASE_OUT });
  return { opacity: t, transform: `scale(${0.96 + 0.04 * t})` };
};

/** stagger delay: 60ms ≈ 2 frames @30fps */
export const stag = (i: number, per = 2) => i * per;

/** MaskUp: industry-standard headline reveal — slides up behind a hard mask. */
export const MaskUp: React.FC<{ text: string; startFrame: number; fontSize?: number; color?: string; fontWeight?: number; delay?: number }> = ({
  text, startFrame, fontSize = 88, color = INK, fontWeight = 800, delay = 0,
}) => {
  const frame = useCurrentFrame();
  const t = interpolate(frame, [startFrame + delay, startFrame + delay + 15], [0, 1], { ...CLAMP, easing: EASE_OUT });
  return (
    <div style={{ overflow: "hidden", paddingBottom: 12 }}>
      <div style={{
        fontFamily: FONT, fontWeight, fontSize, color, lineHeight: 1.12,
        letterSpacing: -2, textAlign: "center",
        transform: `translateY(${(1 - t) * 110}%)`, opacity: t,
      }}>{text}</div>
    </div>
  );
};

/** WordStagger: words cascade up with fade, 2-frame stagger. */
export const WordStagger: React.FC<{ words: string[]; startFrame: number; fontSize?: number; accentWord?: string; color?: string }> = ({
  words, startFrame, fontSize = 72, accentWord, color = INK,
}) => {
  const frame = useCurrentFrame();
  return (
    <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: fontSize * 0.28, maxWidth: 1500 }}>
      {words.map((w, i) => {
        const t = interpolate(frame, [startFrame + stag(i), startFrame + stag(i) + 12], [0, 1], { ...CLAMP, easing: EASE_OUT });
        const isAccent = accentWord === w;
        return (
          <div key={i} style={{ overflow: "hidden", paddingBottom: 8 }}>
            <div style={{
              fontFamily: FONT, fontWeight: 800, fontSize, lineHeight: 1.15,
              letterSpacing: -1.5, color: isAccent ? AMBER : color,
              transform: `translateY(${(1 - t) * 100}%)`, opacity: t,
            }}>{w}</div>
          </div>
        );
      })}
    </div>
  );
};

/** CountUp: fast travel + LONG eased landing. Tabular numerals, commas. */
export const CountUp: React.FC<{ to: number; startFrame: number; durFrames?: number; fontSize?: number; prefix?: string; color?: string }> = ({
  to, startFrame, durFrames = 60, fontSize = 150, prefix = "", color = INK,
}) => {
  const frame = useCurrentFrame();
  const k = interpolate(frame, [startFrame, startFrame + durFrames], [0, 1], { ...CLAMP, easing: (x) => 1 - Math.pow(1 - x, 4) });
  const val = Math.round(to * k).toLocaleString("en-US");
  return (
    <div style={{
      fontFamily: FONT, fontWeight: 800, fontSize, color,
      fontVariantNumeric: "tabular-nums", letterSpacing: -3, textAlign: "center",
    }}>{prefix}{val}</div>
  );
};

/** Stamp: SLAMS — scale 2→1 + shake + impact. For danger/authority moments. */
export const Stamp: React.FC<{ text: string; startFrame: number; fontSize?: number; color?: string }> = ({
  text, startFrame, fontSize = 96, color = RED,
}) => {
  const frame = useCurrentFrame();
  const t = interpolate(frame, [startFrame, startFrame + 8], [0, 1], { ...CLAMP, easing: Easing.out(Easing.cubic) });
  const scale = 2 - t; // 2 → 1
  const shake = t >= 1 && frame < startFrame + 14
    ? Math.sin((frame - startFrame - 8) * 2.2) * 5 * (1 - (frame - startFrame - 8) / 6)
    : 0;
  return (
    <div style={{
      opacity: frame >= startFrame ? 1 : 0,
      transform: `scale(${Math.max(scale, 1)}) translateX(${shake}px) rotate(-4deg)`,
      border: `6px solid ${color}`, borderRadius: 18, padding: "18px 48px",
      fontFamily: FONT, fontWeight: 800, fontSize, color, letterSpacing: 6,
    }}>{text}</div>
  );
};

/** GlassCard: white 96% + one soft shadow + radius 28. Contents clipped. */
export const GlassCard: React.FC<{ children: React.ReactNode; startFrame: number; width?: number; padding?: number; delay?: number }> = ({
  children, startFrame, width = 1200, padding = 64, delay = 0,
}) => {
  const frame = useCurrentFrame();
  const s = pop(frame, startFrame + delay);
  return (
    <div style={{
      width, padding, background: "rgba(255,255,255,0.96)", borderRadius: 28,
      boxShadow: "0 24px 64px rgba(20,20,60,0.12)", overflow: "hidden",
      ...s,
    }}>{children}</div>
  );
};

/** MeshGradient: luminous pastel backdrop, brightest behind subject + slow drift. */
export const MeshGradient: React.FC<{ hue?: "peach" | "blue" | "lavender" | "mint"; children?: React.ReactNode }> = ({ hue = "peach", children }) => {
  const frame = useCurrentFrame();
  const drift = Math.sin(frame / 90) * 60; // ambient loop ~3s cycle
  const palettes: Record<string, string> = {
    peach: `radial-gradient(1000px 700px at ${50 + drift / 20}% 42%, #FFE9D6 0%, #FAFAF8 55%, #EDE9FE 100%)`,
    blue: `radial-gradient(1000px 700px at ${50 + drift / 20}% 42%, #DBEAFE 0%, #FAFAF8 55%, #E0E7FF 100%)`,
    lavender: `radial-gradient(1000px 700px at ${50 - drift / 20}% 42%, #EDE9FE 0%, #FAFAF8 55%, #FCE7F3 100%)`,
    mint: `radial-gradient(1000px 700px at ${50 + drift / 20}% 42%, #D1FAE5 0%, #FAFAF8 55%, #DBEAFE 100%)`,
  };
  return (
    <AbsoluteFill style={{ background: palettes[hue] }}>
      <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse at center, transparent 40%, rgba(26,27,37,0.05) 100%)" }} />
      {children}
    </AbsoluteFill>
  );
};

/** Kicker: small caps section label. */
export const Kicker: React.FC<{ children: React.ReactNode; startFrame: number }> = ({ children, startFrame }) => {
  const frame = useCurrentFrame();
  const s = pop(frame, startFrame, 8);
  return (
    <div style={{
      fontFamily: FONT, fontWeight: 800, fontSize: 30, letterSpacing: 14,
      color: INDIGO, ...s,
    }}>{children}</div>
  );
};

/** MutedLine: quiet supporting text (calm-reading contrast). */
export const MutedLine: React.FC<{ children: React.ReactNode; startFrame: number; fontSize?: number }> = ({ children, startFrame, fontSize = 44 }) => {
  const frame = useCurrentFrame();
  const t = interpolate(frame, [startFrame, startFrame + 12], [0, 1], { ...CLAMP, easing: EASE_OUT });
  return (
    <div style={{
      fontFamily: FONT, fontWeight: 500, fontSize, color: MUTED, textAlign: "center",
      maxWidth: 1300, lineHeight: 1.5, opacity: t,
      transform: `translateY(${(1 - t) * 24}px)`,
    }}>{children}</div>
  );
};
