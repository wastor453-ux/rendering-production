import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import {
  CLAMP,
  INK,
  INDIGO,
  VIOLET,
  MUTED,
  PALE,
  RED,
  PAPER,
  LightBackdrop,
  LightCountUp,
  Card,
} from "../trial/light";

/** Spring-driven entrance. Overshoot peaks at local frame 11 for the
 *  standard config {mass:1, tension:180, friction:12} @30fps. */
export const SpringIn: React.FC<{
  startFrame: number;
  children: React.ReactNode;
  y?: number;
}> = ({ startFrame, children, y = 32 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({
    frame: frame - startFrame,
    fps,
    config: { mass: 1, tension: 180, friction: 12 },
  });
  const op = interpolate(frame, [startFrame, startFrame + 8], [0, 1], {
    ...CLAMP,
    easing: Easing.out(Easing.quad),
  });
  const scale = 0.85 + 0.15 * s;
  const dy = interpolate(s, [0, 1], [y, 0], CLAMP);
  return (
    <div
      style={{
        opacity: op,
        transform: `scale(${scale}) translateY(${dy}px)`,
      }}
    >
      {children}
    </div>
  );
};

/** Kicker with explicit fade start (pluck fires at frame 0 of the fade). */
export const PTKicker: React.FC<{ children: React.ReactNode; startFrame?: number }> = ({
  children,
  startFrame = 5,
}) => {
  const frame = useCurrentFrame();
  const op = interpolate(frame, [startFrame, startFrame + 12], [0, 1], {
    ...CLAMP,
    easing: Easing.out(Easing.quad),
  });
  const y = interpolate(frame, [startFrame, startFrame + 20], [24, 0], {
    ...CLAMP,
    easing: Easing.out(Easing.cubic),
  });
  return (
    <div
      style={{
        fontFamily: "'Plus Jakarta Sans', sans-serif",
        opacity: op,
        transform: `translateY(${y}px)`,
        fontSize: 30,
        fontWeight: 800,
        letterSpacing: 14,
        color: INDIGO,
      }}
    >
      {children}
    </div>
  );
};

/** Cinematic camera wrapper: scale + lateral drift, eased, clamped. */
export const Camera: React.FC<{
  children: React.ReactNode;
  fromScale?: number;
  toScale?: number;
  fromX?: number;
  toX?: number;
}> = ({ children, fromScale = 1, toScale = 1, fromX = 0, toX = 0 }) => {
  const frame = useCurrentFrame();
  const sc = interpolate(frame, [0, 150], [fromScale, toScale], {
    ...CLAMP,
    easing: Easing.out(Easing.quad),
  });
  const dx = interpolate(frame, [0, 150], [fromX, toX], {
    ...CLAMP,
    easing: Easing.out(Easing.cubic),
  });
  return (
    <AbsoluteFill
      style={{ transform: `scale(${sc}) translateX(${dx}px)`, transformOrigin: "50% 50%" }}
    >
      {children}
    </AbsoluteFill>
  );
};

/** Bottom caption pill — VO line, visible during the VO segment. */
export const PTCaption: React.FC<{ text: string; fromFrame: number; toFrame: number }> = ({
  text,
  fromFrame,
  toFrame,
}) => {
  const frame = useCurrentFrame();
  const op = interpolate(frame, [fromFrame, fromFrame + 8], [0, 1], {
    ...CLAMP,
    easing: Easing.out(Easing.quad),
  });
  const opOut = interpolate(frame, [toFrame - 8, toFrame], [1, 0], CLAMP);
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        top: 928,
        display: "flex",
        justifyContent: "center",
        opacity: Math.min(op, opOut),
        fontFamily: "'Plus Jakarta Sans', sans-serif",
      }}
    >
      <div
        style={{
          background: "#FFFFFF",
          border: "1px solid #ECECF3",
          borderRadius: 999,
          padding: "16px 48px",
          fontSize: 32,
          fontWeight: 700,
          color: INK,
          boxShadow: "0 8px 28px rgba(26,27,37,.08)",
        }}
      >
        {text}
      </div>
    </div>
  );
};

export { LightBackdrop, LightCountUp, Card, INK, INDIGO, VIOLET, MUTED, PALE, RED, PAPER, CLAMP };
