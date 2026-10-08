import React from "react";
import { AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
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
  VIOLET,
} from "../shared";

// S4 (15-20s): the mechanism. 6 bars (yearly market balance) grow as springs,
// staggered 12f, silent during VO. Total strip springs at local f132 ->
// overshoot f143 -> snap @19.767s.
//
// Card-local coordinates: card is 1760x560, inner area x48-1712 / y48-512.
// Baseline y=464, bars grow upward (max 320px).

const VALUES = [10000, 11000, 12100, 13310, 14641, 16105];
const MAXV = 16105;
const BAR_W = 248;
const BAR_GAP = 32;
const BAR_X0 = 56; // 48 + (1664 - (6*248 + 5*32)) / 2
const BAR_STEP = BAR_W + BAR_GAP; // 280
const BASE_Y = 464;
const BAR_MAX_H = 320;

const Bar: React.FC<{ value: number; index: number; highlight?: boolean }> = ({
  value,
  index,
  highlight,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const start = 21 + index * 12;
  const s = spring({ frame: frame - start, fps, config: { mass: 1, tension: 180, friction: 12 } });
  const op = interpolate(frame, [start, start + 8], [0, 1], {
    ...CLAMP,
    easing: Easing.out(Easing.quad),
  });
  const h = Math.max(8, (value / MAXV) * BAR_MAX_H * Math.max(0, s));
  return (
    <div
      style={{
        position: "absolute",
        left: BAR_X0 + index * BAR_STEP,
        bottom: 560 - BASE_Y, // 96
        width: BAR_W,
        height: h,
        borderRadius: 16,
        background: highlight ? VIOLET : INDIGO,
        opacity: op,
      }}
    />
  );
};

export const PTScene4: React.FC = () => {
  return (
    <AbsoluteFill>
      <LightBackdrop />
      <Camera fromScale={1} toScale={1.04}>
        <AbsoluteFill style={{ alignItems: "center" }}>
          <div style={{ height: 120 }} />
          <PTKicker>COMPOUNDING</PTKicker>
          <div style={{ height: 32 }} />
          {/* bar card: x80 y280 w1760 h560 */}
          <div style={{ position: "absolute", top: 280, left: 80 }}>
            <Card style={{ width: 1760, height: 560 }}>
              <div style={{ position: "relative", width: 1760, height: 560 }}>
                <div
                  style={{
                    position: "absolute",
                    top: 48,
                    left: 48,
                    fontFamily: "'Plus Jakarta Sans', sans-serif",
                    fontSize: 28,
                    fontWeight: 800,
                    letterSpacing: 6,
                    color: MUTED,
                  }}
                >
                  BALANCE EACH YEAR · 10%
                </div>
                <div
                  style={{
                    position: "absolute",
                    left: 48,
                    right: 48,
                    top: BASE_Y - 2,
                    height: 4,
                    background: "#ECECF3",
                    borderRadius: 2,
                  }}
                />
                {VALUES.map((v, i) => (
                  <Bar key={i} value={v} index={i} highlight={i === 5} />
                ))}
                {VALUES.map((_, i) => (
                  <div
                    key={i}
                    style={{
                      position: "absolute",
                      left: BAR_X0 + i * BAR_STEP,
                      width: BAR_W,
                      top: BASE_Y + 24,
                      textAlign: "center",
                      fontFamily: "'Plus Jakarta Sans', sans-serif",
                      fontSize: 26,
                      fontWeight: 700,
                      color: MUTED,
                      fontVariantNumeric: "tabular-nums",
                    }}
                  >
                    Y{i}
                  </div>
                ))}
                <div
                  style={{
                    position: "absolute",
                    left: BAR_X0,
                    width: BAR_W,
                    top: BASE_Y - BAR_MAX_H - 56,
                    textAlign: "center",
                    fontFamily: "'Plus Jakarta Sans', sans-serif",
                    fontSize: 30,
                    fontWeight: 800,
                    color: INK,
                    fontVariantNumeric: "tabular-nums",
                  }}
                >
                  $10k
                </div>
                <div
                  style={{
                    position: "absolute",
                    left: BAR_X0 + 5 * BAR_STEP,
                    width: BAR_W,
                    top: BASE_Y - BAR_MAX_H - 56,
                    textAlign: "center",
                    fontFamily: "'Plus Jakarta Sans', sans-serif",
                    fontSize: 30,
                    fontWeight: 800,
                    color: VIOLET,
                    fontVariantNumeric: "tabular-nums",
                  }}
                >
                  $16.1k
                </div>
              </div>
            </Card>
          </div>
          {/* total strip: x80 y872 w1760 h128, springs at f132 */}
          <div style={{ position: "absolute", top: 872, left: 80 }}>
            <SpringIn startFrame={132} y={24}>
              <Card style={{ width: 1760, height: 128 }}>
                <div
                  style={{
                    height: 128,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontFamily: "'Plus Jakarta Sans', sans-serif",
                    fontSize: 44,
                    fontWeight: 800,
                    color: INK,
                  }}
                >
                  Gains earning their own gains
                  <span style={{ color: INDIGO, fontWeight: 800, marginLeft: 16 }}>
                    — that&apos;s the engine
                  </span>
                </div>
              </Card>
            </SpringIn>
          </div>
        </AbsoluteFill>
      </Camera>
      <PTCaption
        text="The difference is compounding. Your gains earn their own gains."
        fromFrame={15}
        toFrame={130}
      />
    </AbsoluteFill>
  );
};
