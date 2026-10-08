import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { MeshBackground } from "../premium/components/MeshBackground";
import { GlassCard } from "../premium/components/GlassCard";
import { KineticHeadline, Toast } from "../premium/components/Type";
import { P } from "../premium/theme";

const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const expo = Easing.bezier(0.16, 1, 0.3, 1);

/**
 * H3 — The Autopsy (5448f / 180.6s).
 * Beats: $100-bond seesaw (0–40s) → 30yr 5.5% since 2004 (40–70s) →
 * three forces toasts (70–140s) → foreign demand + regime change (140–180s).
 */
export const H3Autopsy: React.FC = () => {
  const frame = useCurrentFrame();

  // seesaw: price $125 → $80, yield 4% → 6.25% over frames 60–900
  const sawP = interpolate(frame, [60, 900], [0, 1], { ...CLAMP, easing: expo });
  const price = 125 - 45 * sawP;
  const yld = 4 + 2.25 * sawP;
  const seesawOp = interpolate(frame, [30, 60], [0, 1], CLAMP);
  const seesawOut = interpolate(frame, [1050, 1100], [1, 0], CLAMP);

  // yield card 1200–2400
  const yOp = interpolate(frame, [1200, 1240], [0, 1], { ...CLAMP, easing: expo });
  const yOut = interpolate(frame, [2300, 2350], [1, 0], CLAMP);
  const yPulse = interpolate(frame, [1300, 1306, 1318], [1, 1.12, 1], CLAMP);

  // three forces 2500–4200
  const fOut = interpolate(frame, [4250, 4300], [1, 0], CLAMP);

  // regime change close 4350–end
  const rOp = interpolate(frame, [4350, 4390], [0, 1], { ...CLAMP, easing: expo });
  const rY = interpolate(rOp, [0, 1], [40, 0], CLAMP);

  const num = { fontVariantNumeric: "tabular-nums" } as const;

  return (
    <AbsoluteFill>
      <MeshBackground />

      {/* BEAT 1: bond seesaw */}
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: seesawOp * seesawOut }}>
        <GlassCard width={1200} delay={0}>
          <div style={{ fontFamily: P.font, fontWeight: 700, fontSize: 34, color: P.muted, marginBottom: 24, textAlign: "center" }}>
            The $100 bond · price vs yield
          </div>
          <div style={{ display: "flex", justifyContent: "space-around", fontFamily: P.font }}>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontWeight: 600, fontSize: 28, color: P.muted }}>PRICE</div>
              <div style={{ fontWeight: 800, fontSize: 88, color: P.neonBlue, ...num }}>${price.toFixed(0)}</div>
            </div>
            <div style={{ fontWeight: 800, fontSize: 72, color: P.muted, alignSelf: "center" }}>⚖</div>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontWeight: 600, fontSize: 28, color: P.muted }}>YIELD</div>
              <div style={{ fontWeight: 800, fontSize: 88, color: P.loss, ...num }}>{yld.toFixed(2)}%</div>
            </div>
          </div>
          <div style={{ fontFamily: P.font, fontWeight: 600, fontSize: 28, color: P.muted, textAlign: "center", marginTop: 24 }}>
            Price falls → yield jumps. Nothing about the bond changed.
          </div>
        </GlassCard>
      </AbsoluteFill>

      {/* BEAT 2: 30yr yield */}
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: yOp * yOut }}>
        <div style={{ textAlign: "center", transform: `scale(${yPulse})` }}>
          <KineticHeadline lines={["30-year Treasury:", "5.5%"]} accentWord="5.5%" delay={1210} fontSize={110} />
          <div style={{ fontFamily: P.font, fontWeight: 600, fontSize: 34, color: P.muted, marginTop: 24 }}>
            highest since 2004 · 10-year at 5.2%, highest since 2007
          </div>
        </div>
      </AbsoluteFill>

      {/* BEAT 3: three forces */}
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", gap: 28, opacity: fOut }}>
        <div style={{ marginBottom: 8, opacity: interpolate(frame, [2500, 2540], [0, 1], CLAMP) }}>
          <KineticHeadline lines={["Three forces hit at once"]} delay={2500} fontSize={72} />
        </div>
        <Toast delay={2600} tone="warn">Inflation: 65 months above 2%</Toast>
        <Toast delay={3150} tone="warn">Oil: $107 a barrel, +22% in a month</Toast>
        <Toast delay={3700} tone="warn">Fed: hiked to 3.75–4.00%</Toast>
      </AbsoluteFill>

      {/* BEAT 4: regime change */}
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: rOp }}>
        <div style={{ textAlign: "center", transform: `translateY(${rY}px)` }}>
          <KineticHeadline
            lines={["Foreign buyers are fading.", "This isn't a reaction —", "it's a regime change."]}
            delay={4360}
            fontSize={72}
          />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
