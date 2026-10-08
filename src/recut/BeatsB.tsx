import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { CLAMP, EASE_OUT, INK, MUTED, INDIGO, AMBER, RED, FONT, pop, stag, MaskUp, WordStagger, GlassCard, MeshGradient, Kicker, MutedLine } from "./presets";

// ─── BEAT 4 (f924-1170): VALUE — three promise cards ───
export const Beat4: React.FC = () => {
  const frame = useCurrentFrame();
  const cards = [
    { n: "1", t: "HOW IT WORKS" },
    { n: "2", t: "THE FINE PRINT" },
    { n: "3", t: "WHAT I DO" },
  ];
  return (
    <AbsoluteFill>
      <MeshGradient hue="mint" />
      <AbsoluteFill style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 48 }}>
        <Kicker startFrame={4}>IN THE NEXT FEW MINUTES</Kicker>
        <div style={{ display: "flex", gap: 36 }}>
          {cards.map((c, i) => {
            const s = pop(frame, 12 + stag(i, 4));
            return (
              <div key={c.n} style={{
                width: 380, padding: "52px 40px", background: "rgba(255,255,255,0.96)",
                borderRadius: 28, boxShadow: "0 24px 64px rgba(20,20,60,0.12)",
                textAlign: "center", ...s,
              }}>
                <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 64, color: INDIGO }}>{c.n}</div>
                <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 34, color: INK, marginTop: 16, letterSpacing: 1 }}>{c.t}</div>
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ─── BEAT 5 (f1170-1788): THE LENDING TRUTH ───
const LoanArrow: React.FC<{ startFrame: number }> = ({ startFrame }) => {
  const frame = useCurrentFrame();
  const draw = interpolate(frame, [startFrame, startFrame + 30], [0, 940], { ...CLAMP, easing: EASE_OUT });
  return (
    <svg width="1100" height="200">
      <defs>
        <marker id="ahead" markerWidth="14" markerHeight="14" refX="10" refY="7" orient="auto">
          <path d="M0,0 L14,7 L0,14" fill="none" stroke={INDIGO} strokeWidth="3" />
        </marker>
      </defs>
      <line x1="80" y1="100" x2={80 + draw} y2="100" stroke={INDIGO} strokeWidth="10"
        strokeLinecap="round" markerEnd="url(#ahead)" />
      <text x="560" y="70" textAnchor="middle" fontFamily={FONT} fontWeight={800} fontSize={40}
        fill={INDIGO} opacity={draw / 940}>LOAN</text>
    </svg>
  );
};

export const Beat5: React.FC = () => {
  const frame = useCurrentFrame();
  // STORING ✗ → LENDING ✓ swap at local f110
  const swap = interpolate(frame, [110, 130], [0, 1], { ...CLAMP, easing: EASE_OUT });
  return (
    <AbsoluteFill>
      <MeshGradient hue="blue" />
      <AbsoluteFill style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 40 }}>
        <Kicker startFrame={4}>THE FIRST THING NOBODY TOLD YOU</Kicker>
        {/* state A: YOU → BANK loan diagram */}
        <div style={{ display: "flex", alignItems: "center", gap: 30 }}>
          {["YOU", "BANK"].map((w, i) => {
            const s = pop(frame, 10 + stag(i, 10));
            return (
              <div key={w} style={{
                fontFamily: FONT, fontWeight: 800, fontSize: 72, color: i === 0 ? INK : "#fff",
                background: i === 0 ? "rgba(255,255,255,0.96)" : INDIGO,
                padding: "36px 64px", borderRadius: 28,
                boxShadow: "0 24px 64px rgba(20,20,60,0.12)", ...s,
              }}>{w}</div>
            );
          })}
        </div>
        <LoanArrow startFrame={40} />
        {/* state B: storing/lending swap */}
        <div style={{ height: 130, display: "flex", alignItems: "center" }}>
          <div style={{ position: "relative", height: 110, width: 900, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <div style={{ position: "absolute", fontFamily: FONT, fontWeight: 800, fontSize: 76, color: MUTED, opacity: 1 - swap, textDecoration: "line-through" }}>STORING</div>
            <div style={{ position: "absolute", fontFamily: FONT, fontWeight: 800, fontSize: 76, color: INDIGO, opacity: swap }}>LENDING ✓</div>
          </div>
        </div>
        {/* state C: definition card */}
        <GlassCard startFrame={200} width={1150} padding={52}>
          <div style={{ textAlign: "center" }}>
            <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 58, color: RED, letterSpacing: 4 }}>UNSECURED CREDITOR</div>
            <MutedLine startFrame={212} fontSize={40}>someone standing in line, hoping to get paid back</MutedLine>
          </div>
        </GlassCard>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ─── BEAT 6 (f1788-2436): FRACTIONAL FLOW ───
export const Beat6: React.FC = () => {
  const frame = useCurrentFrame();
  const barLent = interpolate(frame, [130, 175], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const barKept = interpolate(frame, [145, 190], [0, 1], { ...CLAMP, easing: EASE_OUT });
  return (
    <AbsoluteFill>
      <MeshGradient hue="peach" />
      <AbsoluteFill style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 36 }}>
        {/* state A: $100 deposit */}
        <div style={{ height: 190, display: "flex", alignItems: "center" }}>
          <GlassCard startFrame={6} width={760} padding={44}>
            <div style={{ textAlign: "center", fontFamily: FONT, fontWeight: 800, fontSize: 88, color: INK, fontVariantNumeric: "tabular-nums" }}>$100 <span style={{ fontSize: 40, color: MUTED, fontWeight: 600 }}>DEPOSIT</span></div>
          </GlassCard>
        </div>
        {/* state B: bars grow from baseline */}
        <div style={{ display: "flex", alignItems: "flex-end", gap: 60, height: 320, marginTop: 56 }}>
          {[
            { label: "LENT OUT", val: "$90", h: 260, c: INDIGO, t: barLent },
            { label: "KEPT", val: "$10", h: 90, c: AMBER, t: barKept },
          ].map((b) => (
            <div key={b.label} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 16 }}>
              <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 54, color: INK, opacity: b.t, fontVariantNumeric: "tabular-nums" }}>{b.val}</div>
              <div style={{
                width: 170, height: b.h * b.t, background: b.c, borderRadius: "20px 20px 8px 8px",
                transformOrigin: "bottom",
              }} />
              <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 30, color: MUTED, letterSpacing: 3, opacity: b.t }}>{b.label}</div>
            </div>
          ))}
        </div>
        {/* state C: term label */}
        <div style={{ height: 100 }}>
          <MutedLine startFrame={230} fontSize={44}>called <span style={{ color: INDIGO, fontWeight: 800 }}>fractional reserve banking</span></MutedLine>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
