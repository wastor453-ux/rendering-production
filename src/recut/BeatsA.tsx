import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { CLAMP, EASE_OUT, INK, MUTED, INDIGO, AMBER, RED, FONT, pop, stag, MaskUp, WordStagger, CountUp, Stamp, GlassCard, MeshGradient, Kicker, MutedLine } from "./presets";

// ─── BEAT 1 (f0-195): HOOK SPARK ───
export const Beat1: React.FC = () => {
  return (
    <AbsoluteFill>
      <MeshGradient hue="peach" />
      <AbsoluteFill style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 40 }}>
        <Kicker startFrame={6}>LAST WEEK</Kicker>
        <GlassCard startFrame={10} width={1450}>
          <MaskUp text="YOUR BANK" startFrame={14} fontSize={110} />
          <MaskUp text="HAS NO MONEY." startFrame={22} fontSize={110} color={INDIGO} />
        </GlassCard>
        <div style={{ height: 130, display: "flex", alignItems: "center" }}>
          <Stamp text="DECLINED" startFrame={96} />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ─── BEAT 2 (f195-453): SCALE ───
export const Beat2: React.FC = () => {
  const frame = useCurrentFrame();
  const f = frame; // local frame within beat (parent offsets via Sequence)
  return (
    <AbsoluteFill>
      <MeshGradient hue="blue" />
      <AbsoluteFill style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 36 }}>
        <Kicker startFrame={4}>WATCHED IT HAPPEN</Kicker>
        <CountUp to={6700000} startFrame={10} durFrames={64} fontSize={170} />
        <MutedLine startFrame={80} fontSize={46}>people watched — and asked one question</MutedLine>
        <div style={{ marginTop: 8 }}>
          <WordStagger words={["how", "is", "that", "legal?"]} startFrame={120} fontSize={92} accentWord="legal?" />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ─── BEAT 3 (f453-924): TWIST ───
const FlowPipes: React.FC<{ startFrame: number }> = ({ startFrame }) => {
  const frame = useCurrentFrame();
  const t = interpolate(frame, [startFrame, startFrame + 90], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const dash = interpolate(frame, [startFrame, startFrame + 400], [0, -400], { ...CLAMP });
  const labels = ["mortgages", "credit cards", "business loans"];
  return (
    <div style={{ position: "relative", width: 1100, height: 340 }}>
      <svg width="1100" height="340" style={{ position: "absolute" }}>
        {/* vault node */}
        <rect x="40" y="130" width="180" height="90" rx="20" fill={INDIGO} opacity={t} />
        {/* three pipes */}
        {[0, 1, 2].map((i) => {
          const y = 80 + i * 90;
          const draw = interpolate(frame, [startFrame + i * 12, startFrame + 40 + i * 12], [0, 1], { ...CLAMP, easing: EASE_OUT });
          return (
            <line key={i} x1="220" y1="175" x2={220 + 700 * draw} y2={y}
              stroke={INDIGO} strokeWidth="10" strokeLinecap="round"
              strokeDasharray="26 18" strokeDashoffset={dash} opacity={0.85} />
          );
        })}
      </svg>
      {labels.map((l, i) => {
        const s = pop(frame, startFrame + 30 + stag(i, 6));
        return (
          <div key={l} style={{
            position: "absolute", left: 950, top: 58 + i * 90, fontFamily: FONT,
            fontWeight: 700, fontSize: 34, color: INK,
            background: "rgba(255,255,255,0.96)", padding: "14px 28px", borderRadius: 16,
            boxShadow: "0 12px 32px rgba(20,20,60,0.10)", whiteSpace: "nowrap", ...s,
          }}>{l}</div>
        );
      })}
      <div style={{ position: "absolute", left: 40, top: 235, fontFamily: FONT, fontWeight: 800, fontSize: 30, color: "#fff", opacity: t }}>YOUR BANK</div>
    </div>
  );
};

export const Beat3: React.FC = () => {
  const frame = useCurrentFrame();
  // balance → IOU morph at local f10
  const morph = interpolate(frame, [10, 34], [0, 1], { ...CLAMP, easing: EASE_OUT });
  return (
    <AbsoluteFill>
      <MeshGradient hue="lavender" />
      <AbsoluteFill style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 44 }}>
        {/* state A: balance morphs to IOU */}
        <div style={{ height: 210, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <GlassCard startFrame={6} width={900} padding={48}>
            <div style={{ position: "relative", height: 110, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <div style={{ position: "absolute", fontFamily: FONT, fontWeight: 800, fontSize: 84, color: INK, opacity: 1 - morph, fontVariantNumeric: "tabular-nums" }}>$48,210.00</div>
              <div style={{ position: "absolute", fontFamily: FONT, fontWeight: 800, fontSize: 84, color: AMBER, opacity: morph, letterSpacing: 8 }}>IOU</div>
            </div>
          </GlassCard>
        </div>
        {/* state B: money flow */}
        <FlowPipes startFrame={150} />
        {/* state C: kinetic phrase */}
        <div style={{ height: 120 }}>
          <WordStagger words={["not", "a", "pile", "of", "cash.", "An", "IOU."]} startFrame={300} fontSize={64} accentWord="IOU." />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
