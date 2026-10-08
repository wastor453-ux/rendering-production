import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import {
  Camera,
  Card,
  CLAMP,
  INK,
  INDIGO,
  LightBackdrop,
  MUTED,
  PTCaption,
  PTKicker,
  SpringIn,
} from "../shared";

// S6 (25-30s): CTA. Camera settles (1.04 -> 1.0). Headline during VO.
// Logo card springs at local f78 -> overshoot f89 -> snap @27.967s.
// CrackIt badge springs at local f108 -> overshoot f119 -> bell @28.967s.

const WORDS = ["Stop", "letting", "your", "money", "sit", "still."];

export const PTScene6: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill>
      <LightBackdrop />
      <Camera fromScale={1.04} toScale={1.0}>
        <AbsoluteFill style={{ alignItems: "center" }}>
          <div style={{ height: 120 }} />
          <PTKicker>THE MOVE</PTKicker>
          <div style={{ height: 32 }} />
          <div
            style={{
              fontFamily: "'Plus Jakarta Sans', sans-serif",
              fontWeight: 800,
              fontSize: 88,
              lineHeight: 1.15,
              letterSpacing: -2,
              color: INK,
              textAlign: "center",
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
                    marginRight: 23,
                  }}
                >
                  {w}
                </span>
              );
            })}
          </div>
          {/* logo card: x560 y360 w800 h360, springs at f78 */}
          <div style={{ position: "absolute", top: 400, left: 560 }}>
            <SpringIn startFrame={78}>
              <Card style={{ width: 800, height: 360 }}>
                <div
                  style={{
                    height: 360,
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    fontFamily: "'Plus Jakarta Sans', sans-serif",
                  }}
                >
                  <div
                    style={{
                      fontSize: 120,
                      fontWeight: 800,
                      letterSpacing: -4,
                      color: INK,
                    }}
                  >
                    Crack<span style={{ color: INDIGO }}>It</span>
                  </div>
                  <div
                    style={{
                      fontSize: 34,
                      fontWeight: 600,
                      color: MUTED,
                      marginTop: 24,
                      letterSpacing: 2,
                    }}
                  >
                    FINANCE, DECODED
                  </div>
                </div>
              </Card>
            </SpringIn>
          </div>
          {/* badge: centered w480 h120 at y=800, springs at f108 */}
          <div style={{ position: "absolute", top: 800, left: 720 }}>
            <SpringIn startFrame={108} y={24}>
              <div
                style={{
                  width: 480,
                  height: 120,
                  borderRadius: 28,
                  background: INDIGO,
                  color: "#fff",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontFamily: "'Plus Jakarta Sans', sans-serif",
                  fontWeight: 800,
                  fontSize: 56,
                  letterSpacing: 4,
                  boxShadow: "0 14px 44px rgba(26,27,37,.12)",
                }}
              >
                START TODAY
              </div>
            </SpringIn>
          </div>
        </AbsoluteFill>
      </Camera>
      <PTCaption text="Stop letting your money sit still." fromFrame={15} toFrame={69} />
    </AbsoluteFill>
  );
};
