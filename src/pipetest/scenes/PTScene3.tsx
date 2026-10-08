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
  SpringIn,
  VIOLET,
} from "../shared";

// S3 (10-15s): comparison. Two cards spring in silently during VO
// (local f21 / f27); ratio badge springs at local f132 ->
// overshoot f143 -> bell @14.767s.

const CompareCard: React.FC<{
  label: string;
  rate: string;
  value: string;
  sub: string;
  accent?: boolean;
}> = ({ label, rate, value, sub, accent }) => (
  <Card style={{ width: 856, height: 440 }}>
    <div style={{ padding: 48, height: 440, display: "flex", flexDirection: "column" }}>
      <div
        style={{
          fontFamily: "'Plus Jakarta Sans', sans-serif",
          fontSize: 28,
          fontWeight: 800,
          letterSpacing: 6,
          color: MUTED,
        }}
      >
        {label}
      </div>
      <div
        style={{
          fontFamily: "'Plus Jakarta Sans', sans-serif",
          fontSize: 40,
          fontWeight: 800,
          color: accent ? VIOLET : INDIGO,
          marginTop: 16,
        }}
      >
        {rate}
      </div>
      <div
        style={{
          fontFamily: "'Plus Jakarta Sans', sans-serif",
          fontSize: 110,
          fontWeight: 800,
          letterSpacing: -2,
          color: INK,
          fontVariantNumeric: "tabular-nums",
          marginTop: 24,
        }}
      >
        {value}
      </div>
      <div
        style={{
          fontFamily: "'Plus Jakarta Sans', sans-serif",
          fontSize: 30,
          fontWeight: 600,
          color: MUTED,
          marginTop: 16,
        }}
      >
        {sub}
      </div>
    </div>
  </Card>
);

export const PTScene3: React.FC = () => {
  return (
    <AbsoluteFill>
      <LightBackdrop />
      <Camera fromScale={1} toScale={1.03}>
        <AbsoluteFill style={{ alignItems: "center" }}>
          <div style={{ height: 120 }} />
          <PTKicker>SAVINGS VS MARKET</PTKicker>
          <div style={{ height: 48 }} />
          {/* card-save: x80 y320 w856 h440 */}
          <div style={{ position: "absolute", top: 320, left: 80 }}>
            <SpringIn startFrame={21}>
              <CompareCard
                label="SAVINGS"
                rate="2% APY"
                value="$11,041"
                sub="Five years of waiting"
              />
            </SpringIn>
          </div>
          {/* card-market: x984 y320 w856 h440 */}
          <div style={{ position: "absolute", top: 320, left: 984 }}>
            <SpringIn startFrame={27}>
              <CompareCard
                label="MARKET"
                rate="10% AVG"
                value="$16,105"
                sub="Same money, same years"
                accent
              />
            </SpringIn>
          </div>
          {/* badge: x720 y800 w480 h144, springs at f132 */}
          <div style={{ position: "absolute", top: 800, left: 720 }}>
            <SpringIn startFrame={132} y={24}>
              <div
                style={{
                  width: 480,
                  height: 144,
                  borderRadius: 28,
                  background: INDIGO,
                  color: "#fff",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontFamily: "'Plus Jakarta Sans', sans-serif",
                  fontWeight: 800,
                  fontSize: 80,
                  fontVariantNumeric: "tabular-nums",
                  letterSpacing: -1,
                  boxShadow: "0 14px 44px rgba(26,27,37,.12)",
                }}
              >
                1.46× MORE
              </div>
            </SpringIn>
          </div>
        </AbsoluteFill>
      </Camera>
      <PTCaption
        text="The market average? Sixteen thousand. Same five years."
        fromFrame={15}
        toFrame={136}
      />
    </AbsoluteFill>
  );
};
