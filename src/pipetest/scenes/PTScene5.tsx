import React from "react";
import { AbsoluteFill } from "remotion";
import {
  Camera,
  Card,
  INK,
  INDIGO,
  LightBackdrop,
  MUTED,
  PTCaption,
  PTKicker,
  RED,
  SpringIn,
} from "../shared";

// S5 (20-25s): proof. 6 stat cards stagger in silently during VO
// (local f21 + i*9). The fee card springs late at local f132 ->
// overshoot f143 -> snap @24.767s.

const STATS = [
  { top: "$100/mo", sub: "put aside" },
  { top: "$6,000", sub: "total in" },
  { top: "5 yrs", sub: "of patience" },
  { top: "$7,744", sub: "it becomes" },
  { top: "1 move", sub: "to start" },
];

const XS = [80, 680, 1280];
const YS = [400, 712];

export const PTScene5: React.FC = () => {
  return (
    <AbsoluteFill>
      <LightBackdrop />
      <Camera>
        <AbsoluteFill style={{ alignItems: "center" }}>
          <div style={{ height: 120 }} />
          <PTKicker>THE FEE DRAIN</PTKicker>
          {/* 5 stat cards: w560 h280, stagger f21+i*9 */}
          {STATS.map((s, i) => {
            const x = XS[i % 3];
            const y = YS[Math.floor(i / 3)];
            return (
              <div key={i} style={{ position: "absolute", top: y, left: x }}>
                <SpringIn startFrame={21 + i * 9}>
                  <Card style={{ width: 560, height: 280 }}>
                    <div
                      style={{
                        height: 280,
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        justifyContent: "center",
                        fontFamily: "'Plus Jakarta Sans', sans-serif",
                      }}
                    >
                      <div
                        style={{
                          fontSize: 76,
                          fontWeight: 800,
                          letterSpacing: -2,
                          color: INK,
                          fontVariantNumeric: "tabular-nums",
                        }}
                      >
                        {s.top}
                      </div>
                      <div style={{ fontSize: 30, fontWeight: 600, color: MUTED, marginTop: 16 }}>
                        {s.sub}
                      </div>
                    </div>
                  </Card>
                </SpringIn>
              </div>
            );
          })}
          {/* fee card: x1280 y712 w560 h280, springs at f132 -> snap */}
          <div style={{ position: "absolute", top: 712, left: 1280 }}>
            <SpringIn startFrame={132} y={24}>
              <Card
                style={{
                  width: 560,
                  height: 280,
                  border: `2px solid ${RED}`,
                  background: "#FFF5F5",
                }}
              >
                <div
                  style={{
                    height: 280,
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    fontFamily: "'Plus Jakarta Sans', sans-serif",
                  }}
                >
                  <div
                    style={{
                      fontSize: 76,
                      fontWeight: 800,
                      letterSpacing: -2,
                      color: RED,
                      fontVariantNumeric: "tabular-nums",
                    }}
                  >
                    −$719
                  </div>
                  <div style={{ fontSize: 30, fontWeight: 700, color: RED, marginTop: 16 }}>
                    eaten by a 1% fee
                  </div>
                </div>
              </Card>
            </SpringIn>
          </div>
        </AbsoluteFill>
      </Camera>
      <PTCaption
        text="A one percent fee alone eats seven hundred nineteen dollars."
        fromFrame={15}
        toFrame={132}
      />
    </AbsoluteFill>
  );
};
