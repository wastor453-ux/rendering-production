import React from "react";
import {
  AbsoluteFill,
  Audio,
  Easing,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Card, CLAMP, INK, INDIGO, LightBackdrop, MUTED } from "../trial/light";

export const STRESS_FPS = 30;
export const STRESS_TOTAL = 150; // 5 seconds

// 8px grid: margins 80, gap 48, card 856x480, inner padding 48, card top 296 —
// every value a strict multiple of 8.
const CARD_W = 856;
const CARD_H = 480;
const CARD_Y = 296;
const CARD1_X = 80;
const CARD2_X = 984;
const CARD_PAD = 48;

/**
 * Typography boundary math (pillar 4): measure the rendered text width and
 * step the font size down in 8px decrements until it fits inside maxWidth.
 * Deterministic for identical inputs (pure function of text + font).
 */
const fitText = (text: string, maxWidth: number, baseSize: number, weight = 800): number => {
  if (typeof document === "undefined") return baseSize;
  const ctx = document.createElement("canvas").getContext("2d");
  if (!ctx) return baseSize;
  let size = baseSize;
  ctx.font = `${weight} ${size}px 'Plus Jakarta Sans', sans-serif`;
  while (ctx.measureText(text).width > maxWidth && size > 24) {
    size -= 8;
    ctx.font = `${weight} ${size}px 'Plus Jakarta Sans', sans-serif`;
  }
  return size;
};

const popIn = (frame: number, startFrame: number, fps: number) => {
  const f = frame - startFrame;
  const s = spring({ frame: f, fps, config: { mass: 1, tension: 180, friction: 12 } });
  const scale = interpolate(s, [0, 1], [0.6, 1], CLAMP);
  const op = interpolate(f, [0, 10], [0, 1], { ...CLAMP, easing: Easing.out(Easing.quad) });
  const y = interpolate(f, [0, 20], [40, 0], { ...CLAMP, easing: Easing.out(Easing.cubic) });
  return { transform: `translateY(${y}px) scale(${scale})`, opacity: op };
};

const PersonCard: React.FC<{
  x: number;
  startFrame: number;
  name: string;
  startAge: string;
  invested: string;
}> = ({ x, startFrame, name, startAge, invested }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const anim = popIn(frame, startFrame, fps);
  const textMax = CARD_W - CARD_PAD * 2;
  const amountSize = fitText(`$${invested}`, textMax, 72);
  const startSize = fitText(`Starts at ${startAge}`, textMax, 56);
  return (
    <div style={{ position: "absolute", left: x, top: CARD_Y, width: CARD_W, ...anim }}>
      <Card style={{ width: CARD_W, height: CARD_H, padding: CARD_PAD }}>
        <div style={{ fontSize: 32, fontWeight: 800, letterSpacing: 14, color: INDIGO }}>
          {name}
        </div>
        <div style={{ fontSize: startSize, fontWeight: 800, color: INK, marginTop: 24 }}>
          Starts at {startAge}
        </div>
        <div style={{ height: 1, background: "#ECECF3", margin: "32px 0" }} />
        <div style={{ fontSize: 28, fontWeight: 600, color: MUTED }}>Total Invested</div>
        <div
          style={{
            fontSize: amountSize,
            fontWeight: 800,
            color: INK,
            marginTop: 8,
            fontVariantNumeric: "tabular-nums",
          }}
        >
          ${invested}
        </div>
      </Card>
    </div>
  );
};

export const StressTest: React.FC = () => {
  return (
    <AbsoluteFill style={{ background: "#FAFAF8", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
      <LightBackdrop />
      {/* Card 1 pops at frame 15, Card 2 at frame 25 — staggered per spec */}
      <PersonCard x={CARD1_X} startFrame={15} name="ALEX" startAge="25" invested="60,000" />
      <PersonCard x={CARD2_X} startFrame={25} name="BEN" startAge="35" invested="150,000" />
      <Audio src={staticFile("audio/stress-master.mp3")} />
    </AbsoluteFill>
  );
};
