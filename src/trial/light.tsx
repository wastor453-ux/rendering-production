import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

/**
 * Style A (Pastel Fintech) light component library — Hamza's pick.
 * NOTE: Remotion's Easing has no cubic-bezier(x1,y1,x2,y2) API in this
 * version, so the spec's `cubic-bezier(0.215,0.610,0.355,1)` (ease-out
 * cubic) is implemented as Easing.out(Easing.cubic) — the same curve family.
 */

export const PAPER = "#FAFAF8";
export const INK = "#1A1B25";
export const MUTED = "#8A8AA3";
export const INDIGO = "#4F46E5";
export const VIOLET = "#8B5CF6";
export const PALE = "#EEEDFE";
export const RED = "#E5484D";

export const CLAMP = {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
} as const;

const EASE_OUT_CUBIC = Easing.out(Easing.cubic); // spec: cubic-bezier(0.215,0.610,0.355,1)
const EASE_FADE = Easing.out(Easing.quad);

const FONT = "'Plus Jakarta Sans', sans-serif";

export const LightBackdrop: React.FC = () => {
  const frame = useCurrentFrame();
  const op = interpolate(frame, [0, 12], [0, 1], { ...CLAMP, easing: EASE_FADE });
  return (
    <AbsoluteFill
      style={{
        background: PAPER,
        opacity: op,
        backgroundImage: "radial-gradient(#E0E0EE 1.3px, transparent 1.3px)",
        backgroundSize: "34px 34px",
        fontFamily: FONT,
      }}
    >
      <div
        style={{
          position: "absolute", top: 0, left: 0, right: 0, height: 10,
          background: `linear-gradient(90deg, ${INDIGO}, ${VIOLET}, ${INDIGO})`,
        }}
      />
    </AbsoluteFill>
  );
};

export const LightKicker: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const frame = useCurrentFrame();
  const op = interpolate(frame, [6, 18], [0, 1], { ...CLAMP, easing: EASE_FADE });
  const y = interpolate(frame, [6, 26], [24, 0], { ...CLAMP, easing: EASE_OUT_CUBIC });
  return (
    <div style={{ fontFamily: FONT, opacity: op, transform: `translateY(${y}px)`, fontSize: 30, fontWeight: 800, letterSpacing: 14, color: INDIGO }}>
      {children}
    </div>
  );
};

/** Word-staggered headline. Fade + rise only — no overshoot on large elements. */
export const LightHeadline: React.FC<{
  words: string[];
  startFrame?: number;
  fontSize?: number;
  color?: string;
  stagger?: number;
}> = ({ words, startFrame = 12, fontSize = 104, color = INK, stagger = 2.4 }) => {
  const frame = useCurrentFrame();
  return (
    <div style={{ fontFamily: FONT, fontWeight: 800, fontSize, lineHeight: 1.15, color, textAlign: "center", letterSpacing: -2 }}>
      {words.map((w, i) => {
        const f = frame - startFrame - i * stagger;
        const op = interpolate(f, [0, 10], [0, 1], { ...CLAMP, easing: EASE_FADE });
        const y = interpolate(f, [0, 18], [28, 0], { ...CLAMP, easing: EASE_OUT_CUBIC });
        return (
          <span key={i} style={{ display: "inline-block", opacity: op, transform: `translateY(${y}px)`, marginRight: fontSize * 0.26 }}>
            {w}
          </span>
        );
      })}
    </div>
  );
};

/** Count-up, eases out like a slot machine. */
export const LightCountUp: React.FC<{
  to: number;
  fromFrame: number;
  toFrame: number;
  fontSize?: number;
  color?: string;
}> = ({ to, fromFrame, toFrame, fontSize = 96, color = INK }) => {
  const frame = useCurrentFrame();
  // Snap to exact value at/past the end: Easing.out(Easing.exp) asymptotes at
  // 1 - 2^-10 = 0.999023 and NEVER reaches 1, so without the snap the counter
  // would freeze at $999,023 instead of $1,000,000.
  const v = frame >= toFrame
    ? to
    : interpolate(frame, [fromFrame, toFrame], [0, to], { ...CLAMP, easing: Easing.out(Easing.exp) });
  return (
    <div style={{ fontFamily: FONT, fontWeight: 800, fontSize, color, fontVariantNumeric: "tabular-nums" }}>
      ${Math.round(v).toLocaleString("en-US")}
    </div>
  );
};

/** Indigo badge with white text — hero numbers. */
export const Badge: React.FC<{ children: React.ReactNode; fontSize?: number }> = ({ children, fontSize = 84 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - 6, fps, config: { mass: 1, tension: 180, friction: 12 } });
  const scale = interpolate(s, [0, 1], [0.6, 1], CLAMP);
  const op = interpolate(frame, [0, 10], [0, 1], { ...CLAMP, easing: EASE_FADE });
  return (
    <div style={{
      fontFamily: FONT,
      opacity: op, transform: `scale(${scale})`, background: INDIGO, color: "#fff",
      fontWeight: 800, fontSize, padding: "22px 64px", borderRadius: 28,
      fontVariantNumeric: "tabular-nums", letterSpacing: -1,
    }}>
      {children}
    </div>
  );
};

export const Card: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div style={{
    fontFamily: FONT,
    background: "#FFFFFF", borderRadius: 28, border: "1px solid #ECECF3",
    boxShadow: "0 14px 44px rgba(26,27,37,.08)", overflow: "hidden", ...style,
  }}>
    {children}
  </div>
);
