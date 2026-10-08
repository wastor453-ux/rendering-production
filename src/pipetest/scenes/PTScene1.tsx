import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import {
  Camera,
  CLAMP,
  INK,
  INDIGO,
  LightBackdrop,
  MUTED,
  PTCaption,
  PTKicker,
  RED,
  SpringIn,
} from "../shared";

// S1 (0-5s): Hook. Camera push-in. Kicker + staggered headline,
// red 2% badge springs at local f90 -> overshoot f101 -> bell @3.367s.

const WORDS = ["Your", "savings", "account", "is", "lying", "to", "you."];

export const PTScene1: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill>
      <LightBackdrop />
      <Camera fromScale={1} toScale={1.05}>
        <AbsoluteFill style={{ alignItems: "center" }}>
          <div style={{ height: 120 }} />
          <PTKicker>THE LIE IN YOUR BANK APP</PTKicker>
          <div style={{ height: 40 }} />
          <div
            style={{
              fontFamily: "'Plus Jakarta Sans', sans-serif",
              fontWeight: 800,
              fontSize: 104,
              lineHeight: 1.15,
              letterSpacing: -2,
              color: INK,
              textAlign: "center",
              maxWidth: 1600,
            }}
          >
            {WORDS.map((w, i) => {
              const f = frame - 10 - i * 3;
              const op = interpolate(f, [0, 10], [0, 1], {
                ...CLAMP,
                easing: Easing.out(Easing.quad),
              });
              const y = interpolate(f, [0, 18], [28, 0], {
                ...CLAMP,
                easing: Easing.out(Easing.cubic),
              });
              return (
                <span
                  key={i}
                  style={{
                    display: "inline-block",
                    opacity: op,
                    transform: `translateY(${y}px)`,
                    marginRight: 27,
                  }}
                >
                  {w}
                </span>
              );
            })}
          </div>
          <div style={{ height: 56 }} />
          {/* badge: x centered, w520 h160 -> x=700 y=640 */}
          <div style={{ position: "absolute", top: 640, left: 700 }}>
            <SpringIn startFrame={90}>
              <div
                style={{
                  width: 520,
                  height: 160,
                  borderRadius: 28,
                  background: RED,
                  color: "#fff",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontFamily: "'Plus Jakarta Sans', sans-serif",
                  fontWeight: 800,
                  fontSize: 88,
                  fontVariantNumeric: "tabular-nums",
                  boxShadow: "0 14px 44px rgba(26,27,37,.12)",
                }}
              >
                2%
              </div>
            </SpringIn>
          </div>
          <div
            style={{
              position: "absolute",
              top: 824,
              fontFamily: "'Plus Jakarta Sans', sans-serif",
              fontSize: 30,
              fontWeight: 700,
              color: MUTED,
              opacity: interpolate(frame, [100, 115], [0, 1], CLAMP),
            }}
          >
            interest on $10,000
          </div>
        </AbsoluteFill>
      </Camera>
      <PTCaption text="Your savings account is lying to you." fromFrame={15} toFrame={82} />
    </AbsoluteFill>
  );
};
