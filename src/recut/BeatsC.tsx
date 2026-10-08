import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { CLAMP, EASE_OUT, INK, MUTED, INDIGO, AMBER, RED, FONT, pop, stag, MaskUp, WordStagger, Stamp, GlassCard, MeshGradient, Kicker, MutedLine } from "./presets";

// ─── BEAT 7 (f2436-3102): THE UNCOMFORTABLE PART — bank run ───
const DOTS = 24;
const BankRun: React.FC<{ startFrame: number }> = ({ startFrame }) => {
  const frame = useCurrentFrame();
  // dots converge with easeInOut (NOT linear) toward the vault, synced to VO
  const t = interpolate(frame, [startFrame, startFrame + 110], [0, 1], { ...CLAMP, easing: Easing.inOut(Easing.cubic) });
  return (
    <div style={{ position: "relative", width: 1200, height: 480 }}>
      {/* vault */}
      <div style={{
        position: "absolute", left: 500, top: 150, width: 200, height: 180,
        background: INDIGO, borderRadius: 28, display: "flex", alignItems: "center",
        justifyContent: "center", fontFamily: FONT, fontWeight: 800, fontSize: 34, color: "#fff",
        boxShadow: "0 24px 64px rgba(79,70,229,0.35)",
      }}>VAULT</div>
      {Array.from({ length: DOTS }).map((_, i) => {
        const angle = (i / DOTS) * Math.PI * 2;
        const r0 = 480;
        const x0 = 600 + Math.cos(angle) * r0, y0 = 240 + Math.sin(angle) * r0 * 0.55;
        const x1 = 600 + Math.cos(angle) * 150, y1 = 240 + Math.sin(angle) * 90;
        const x = x0 + (x1 - x0) * t, y = y0 + (y1 - y0) * t;
        const op = interpolate(frame, [startFrame, startFrame + 20], [0, 1], { ...CLAMP });
        return (
          <div key={i} style={{
            position: "absolute", left: x - 16, top: y - 16, width: 32, height: 32,
            borderRadius: "50%", background: "#fff",
            border: `3px solid ${INDIGO}`, opacity: op,
            boxShadow: "0 8px 20px rgba(20,20,60,0.15)",
          }} />
        );
      })}
    </div>
  );
};

export const Beat7: React.FC = () => {
  return (
    <AbsoluteFill>
      <MeshGradient hue="lavender" />
      <AbsoluteFill style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 30 }}>
        <Kicker startFrame={4}>IF EVERYONE SHOWED UP AT ONCE</Kicker>
        <BankRun startFrame={20} />
        <div style={{ height: 150, display: "flex", alignItems: "center" }}>
          <Stamp text="COULD NOT PAY" startFrame={150} fontSize={88} />
        </div>
        <div style={{ height: 90 }}>
          <MutedLine startFrame={210} fontSize={42}>your balance is an IOU — already spent</MutedLine>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ─── BEAT 8 (f3102-3216): SECTION CARD ───
export const Beat8: React.FC = () => {
  return (
    <AbsoluteFill>
      <MeshGradient hue="blue" />
      <AbsoluteFill style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 30 }}>
        <GlassCard startFrame={6} width={1250} padding={72}>
          <MaskUp text="THE WITHDRAWAL" startFrame={10} fontSize={96} />
          <MaskUp text="RULES" startFrame={18} fontSize={96} color={INDIGO} />
        </GlassCard>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ─── BEAT 9 (f3216-3894): SEVEN DAYS ───
const Calendar: React.FC<{ startFrame: number }> = ({ startFrame }) => {
  const frame = useCurrentFrame();
  return (
    <div style={{ display: "flex", gap: 14 }}>
      {["M", "T", "W", "T", "F", "S", "S"].map((d, i) => {
        const s = pop(frame, startFrame + stag(i, 5), 8);
        return (
          <div key={i} style={{
            width: 96, height: 120, background: "rgba(255,255,255,0.96)", borderRadius: 20,
            display: "flex", alignItems: "center", justifyContent: "center",
            fontFamily: FONT, fontWeight: 800, fontSize: 44, color: i === 6 ? RED : INK,
            boxShadow: "0 16px 40px rgba(20,20,60,0.10)", ...s,
          }}>{d}</div>
        );
      })}
    </div>
  );
};

export const Beat9: React.FC = () => {
  const frame = useCurrentFrame();
  // highlight sweep across the document at local f40
  const sweep = interpolate(frame, [40, 90], [-100, 1100], { ...CLAMP, easing: EASE_OUT });
  return (
    <AbsoluteFill>
      <MeshGradient hue="peach" />
      <AbsoluteFill style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 40 }}>
        {/* state A: the agreement document */}
        <div style={{ height: 300, display: "flex", alignItems: "center" }}>
          <GlassCard startFrame={6} width={1050} padding={56}>
            <div style={{ position: "relative", overflow: "hidden" }}>
              <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 40, color: INK, letterSpacing: 3, marginBottom: 20 }}>ACCOUNT AGREEMENT</div>
              {[0, 1, 2].map((i) => (
                <div key={i} style={{ height: 18, background: "#ECECF3", borderRadius: 9, marginBottom: 14, width: `${92 - i * 12}%` }} />
              ))}
              <div style={{
                position: "absolute", top: 64, left: sweep, width: 260, height: 76,
                background: "rgba(245,158,11,0.35)", borderRadius: 12,
              }} />
              <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 34, color: INK, marginTop: 8 }}>
                "...may require up to <span style={{ color: RED, fontWeight: 800 }}>seven days' written notice</span>..."
              </div>
            </div>
          </GlassCard>
        </div>
        {/* state B: 7-day calendar tear-off */}
        <Calendar startFrame={130} />
        <div style={{ height: 110 }}>
          <WordStagger words={["Seven", "days.", "For", "your", "own", "money."]} startFrame={200} fontSize={68} accentWord="money." />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
