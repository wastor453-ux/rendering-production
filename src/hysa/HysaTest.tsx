import React from "react";
import {
  AbsoluteFill,
  Audio,
  Easing,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
} from "remotion";

export const HYSA_TOTAL = 300;
export const FPS = 30;
const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// Must stay identical to tools/layout_aabb_lib.js popIn() — the physics
// gate audited these exact boxes.
const popIn = (frame: number, startFrame: number) => {
  const f = frame - startFrame;
  const s = spring({ frame: f, fps: FPS, config: { mass: 1, tension: 180, friction: 12 } });
  const scale = interpolate(s, [0, 1], [0.6, 1], CLAMP);
  const y = interpolate(f, [0, 20], [40, 0], { ...CLAMP, easing: Easing.out(Easing.cubic) });
  const op = interpolate(f, [0, 10], [0, 1], { ...CLAMP, easing: Easing.out(Easing.quad) });
  return { transform: `translateY(${y}px) scale(${scale})`, opacity: op };
};

const Card: React.FC<{
  x: number; y: number; w: number; h: number;
  startFrame: number; title: string; value: string; valueColor: string;
}> = ({ x, y, w, h, startFrame, title, value, valueColor }) => {
  const frame = useCurrentFrame();
  const anim = popIn(frame, startFrame);
  return (
    <div
      style={{
        position: "absolute", left: x, top: y, width: w, height: h,
        background: "#FFFFFF", border: "1px solid #ECECF3", borderRadius: 28,
        padding: "48px 56px", ...anim,
      }}
    >
      <div style={{ fontSize: 30, letterSpacing: 4, color: "#8A8AA3", fontWeight: 700 }}>{title}</div>
      <div style={{ fontSize: 120, fontWeight: 800, color: valueColor, marginTop: 24 }}>{value}</div>
    </div>
  );
};

const ChartCard: React.FC = () => {
  const frame = useCurrentFrame();
  const x = 80, y = 768, w = 1760, h = 232;
  const op = interpolate(frame, [70, 90], [0, 1], { ...CLAMP, easing: Easing.out(Easing.quad) });
  const drawT = interpolate(frame, [90, 270], [0, 1], { ...CLAMP, easing: Easing.out(Easing.quad) });
  const labelOp = interpolate(frame, [270, 285], [0, 1], CLAMP);

  // Plot geometry: values [100, 99, 98.01, 97.03, 96.06, 95.10]
  const vals = [100, 99, 98.01, 97.03, 96.06, 95.1];
  const px0 = 40, px1 = w - 40, py0 = 36, py1 = h - 56;
  const X = (i: number) => px0 + ((px1 - px0) * i) / 5;
  const Y = (v: number) => py1 - ((py1 - py0) * (v - 94)) / 6;
  const d = vals.map((v, i) => `${i === 0 ? "M" : "L"} ${X(i).toFixed(1)} ${Y(v).toFixed(1)}`).join(" ");

  return (
    <div
      style={{
        position: "absolute", left: x, top: y, width: w, height: h,
        background: "#FFFFFF", border: "1px solid #ECECF3", borderRadius: 28, opacity: op,
      }}
    >
      <div style={{ position: "absolute", left: 40, top: 28, fontSize: 26, letterSpacing: 3, color: "#8A8AA3", fontWeight: 700 }}>
        REAL RETURN — 5 YEARS
      </div>
      <div style={{ position: "absolute", right: 48, top: 28, fontSize: 30, fontWeight: 800, color: "#E5484D", opacity: labelOp }}>
        −1% real return
      </div>
      <svg width={w} height={h} style={{ position: "absolute", left: 0, top: 0 }}>
        <path d={d} fill="none" stroke="#E5484D" strokeWidth={5} strokeLinecap="round"
          pathLength={1} strokeDasharray={1} strokeDashoffset={1 - drawT} />
        {vals.map((v, i) => (
          <circle key={i} cx={X(i)} cy={Y(v)} r={8} fill="#E5484D"
            opacity={drawT * 5 >= i ? 1 : 0} />
        ))}
        <text x={px0} y={py0 - 8} fontSize={22} fill="#8A8AA3" fontWeight={700}>100</text>
        <text x={px1 - 60} y={py1 + 30} fontSize={22} fill="#8A8AA3" fontWeight={700}>95.10</text>
      </svg>
    </div>
  );
};

export const HysaTest: React.FC = () => {
  const frame = useCurrentFrame();
  const kickerOp = interpolate(frame, [5, 15], [0, 1], { ...CLAMP, easing: Easing.out(Easing.quad) });
  return (
    <AbsoluteFill
      style={{
        background: "#FAFAF8",
        backgroundImage: "radial-gradient(#E0E0EE 1.3px, transparent 1.3px)",
        backgroundSize: "34px 34px",
        fontFamily: "'Plus Jakarta Sans', sans-serif",
      }}
    >
      <div style={{
        position: "absolute", top: 0, left: 0, right: 0, height: 10,
        background: "linear-gradient(90deg, #4F46E5, #8B5CF6, #4F46E5)",
      }} />
      <div style={{
        position: "absolute", left: 80, top: 150, opacity: kickerOp,
        fontSize: 40, letterSpacing: 10, fontWeight: 800, color: "#4F46E5",
      }}>
        THE HYSA TRAP
      </div>
      <Card x={80} y={320} w={856} h={400} startFrame={30}
        title="HYSA YIELD" value="+4%" valueColor="#1A1B25" />
      <Card x={984} y={320} w={856} h={400} startFrame={45}
        title="INFLATION RATE" value="−5%" valueColor="#E5484D" />
      <ChartCard />
      <Audio src={staticFile("audio/hysa/hysa-master.mp3")} />
    </AbsoluteFill>
  );
};
