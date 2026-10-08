import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { CLAMP, EASE_OUT, INK, MUTED, INDIGO, AMBER, RED, FONT, pop, stag, MaskUp, WordStagger, Stamp, GlassCard, MeshGradient, Kicker, MutedLine } from "./presets";

// ─── BEAT 10 (f3894-4728): DAILY LIMITS ───
const LimitIcons: React.FC<{ startFrame: number }> = ({ startFrame }) => {
  const frame = useCurrentFrame();
  const icons = ["?", "▤", "◷", "👔"];
  const labels = ["questions", "forms", "delays", "the manager"];
  return (
    <div style={{ display: "flex", gap: 28 }}>
      {icons.map((ic, i) => {
        const s = pop(frame, startFrame + stag(i, 8), 9);
        return (
          <div key={i} style={{
            width: 200, padding: "36px 20px", background: "rgba(255,255,255,0.96)",
            borderRadius: 24, boxShadow: "0 16px 40px rgba(20,20,60,0.10)",
            textAlign: "center", ...s,
          }}>
            <div style={{ fontSize: 64 }}>{ic}</div>
            <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 28, color: MUTED, marginTop: 12 }}>{labels[i]}</div>
          </div>
        );
      })}
    </div>
  );
};

const ThresholdMeter: React.FC<{ startFrame: number }> = ({ startFrame }) => {
  const frame = useCurrentFrame();
  const t = interpolate(frame, [startFrame, startFrame + 50], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const badge = pop(frame, startFrame + 55, 9);
  return (
    <div style={{ width: 1100 }}>
      <div style={{ position: "relative", height: 46, background: "#ECECF3", borderRadius: 23, overflow: "hidden" }}>
        <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: `${t * 100}%`, background: `linear-gradient(90deg, ${INDIGO}, #8B5CF6)`, borderRadius: 23 }} />
        {/* $10k red line at 70% */}
        <div style={{ position: "absolute", left: "70%", top: -6, bottom: -6, width: 6, background: RED, borderRadius: 3 }} />
        <div style={{ position: "absolute", left: "70%", top: -52, transform: "translateX(-50%)", fontFamily: FONT, fontWeight: 800, fontSize: 32, color: RED, whiteSpace: "nowrap", fontVariantNumeric: "tabular-nums" }}>$10,000</div>
      </div>
      <div style={{ height: 110, display: "flex", justifyContent: "center", marginTop: 18 }}>
        <div style={{
          fontFamily: FONT, fontWeight: 800, fontSize: 44, color: "#fff", background: RED,
          padding: "20px 48px", borderRadius: 18, letterSpacing: 3, ...badge,
        }}>REPORT FILED</div>
      </div>
    </div>
  );
};

export const Beat10: React.FC = () => {
  const frame = useCurrentFrame();
  const show9999 = frame >= 420 ? 1 : 0;
  return (
    <AbsoluteFill>
      <MeshGradient hue="blue" />
      <AbsoluteFill style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 36 }}>
        <Kicker startFrame={4}>TRY WITHDRAWING CASH</Kicker>
        <LimitIcons startFrame={14} />
        <div style={{ height: 300, display: "flex", alignItems: "center" }}>
          <ThresholdMeter startFrame={140} />
        </div>
        <div style={{ height: 150, display: "flex", alignItems: "center", gap: 40 }}>
          <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 64, color: INK, fontVariantNumeric: "tabular-nums", opacity: show9999 }}>$9,999 <span style={{ fontSize: 36, color: MUTED }}>× repeated</span></div>
          <Stamp text="STRUCTURING" startFrame={470} fontSize={72} />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ─── BEAT 11 (f4728-4983): THE SHAPE — privilege vs property ───
export const Beat11: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill>
      <MeshGradient hue="lavender" />
      <AbsoluteFill style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 44 }}>
        <div style={{ height: 100 }}>
          <WordStagger words={["Do", "you", "see", "the", "shape", "of", "this?"]} startFrame={6} fontSize={72} />
        </div>
        <div style={{ display: "flex", gap: 36 }}>
          {[
            { t: "PRIVILEGE", s: "granted by the system", hot: true },
            { t: "PROPERTY", s: "yours by right", hot: false },
          ].map((c, i) => {
            const p = pop(frame, 70 + stag(i, 10));
            return (
              <div key={c.t} style={{
                width: 520, padding: "56px 48px", borderRadius: 28, textAlign: "center",
                background: c.hot ? INDIGO : "rgba(255,255,255,0.96)",
                boxShadow: "0 24px 64px rgba(20,20,60,0.12)",
                opacity: c.hot ? p.opacity : (p.opacity as number) * 0.55, transform: p.transform,
              }}>
                <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 54, color: c.hot ? "#fff" : MUTED, letterSpacing: 2 }}>{c.t}</div>
                <div style={{ fontFamily: FONT, fontWeight: 600, fontSize: 34, color: c.hot ? "rgba(255,255,255,0.85)" : MUTED, marginTop: 14 }}>{c.s}</div>
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ─── BEAT 12 (f4983-5400): REFRAME — collapse? no. ───
export const Beat12: React.FC = () => {
  const frame = useCurrentFrame();
  const coin = pop(frame, 130, 10);
  return (
    <AbsoluteFill>
      <MeshGradient hue="mint" />
      <AbsoluteFill style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 44 }}>
        <div style={{ height: 200, display: "flex", alignItems: "center" }}>
          <WordStagger words={["Banks", "collapsing?", "No."]} startFrame={6} fontSize={110} accentWord="No." />
        </div>
        <div style={{ height: 220, display: "flex", alignItems: "center", gap: 32 }}>
          <MutedLine startFrame={70} fontSize={46}>anyone who tells you that is selling you something —</MutedLine>
          <div style={{
            width: 130, height: 130, borderRadius: "50%",
            background: "radial-gradient(circle at 35% 30%, #FCD34D, #F59E0B)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontFamily: FONT, fontWeight: 800, fontSize: 56, color: "#fff",
            boxShadow: "0 16px 40px rgba(245,158,11,0.35)", ...coin,
          }}>$</div>
          <MutedLine startFrame={140} fontSize={46}>usually gold.</MutedLine>
        </div>
        {/* exhale: calm hold, ambient loop only */}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
