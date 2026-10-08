import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { MeshBackground } from "../premium/components/MeshBackground";
import { GlassCard } from "../premium/components/GlassCard";
import { KineticHeadline, Toast } from "../premium/components/Type";
import { P } from "../premium/theme";

const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const expo = Easing.bezier(0.16, 1, 0.3, 1);

/**
 * H5 — The Freeze (3618f / 119.6s).
 * Beats: "sales fall first" (0–25s) → 58% seller surplus (25–55s) →
 * −14% / −$62K card (55–85s) → golden cage close (85–119s).
 */
export const H5Freeze: React.FC = () => {
  const frame = useCurrentFrame();

  const sOp = interpolate(frame, [10, 40], [0, 1], CLAMP);
  const sOut = interpolate(frame, [700, 750], [1, 0], CLAMP);

  // seller surplus bar 800–1600
  const bOp = interpolate(frame, [800, 840], [0, 1], CLAMP);
  const bOut = interpolate(frame, [1650, 1700], [1, 0], CLAMP);
  const barW = interpolate(frame, [900, 1300], [0, 1], { ...CLAMP, easing: expo });

  // −14% card 1750–2600
  const cOp = interpolate(frame, [1750, 1790], [0, 1], CLAMP);
  const cOut = interpolate(frame, [2650, 2700], [1, 0], CLAMP);
  const cPulse = interpolate(frame, [1850, 1856, 1868], [1, 1.1, 1], CLAMP);

  // golden cage 2750–end
  const gOp = interpolate(frame, [2750, 2790], [0, 1], CLAMP);

  return (
    <AbsoluteFill>
      <MeshBackground />

      {/* BEAT 1: sequencing */}
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: sOp * sOut }}>
        <div style={{ textAlign: "center" }}>
          <KineticHeadline
            lines={["When rates rise fast,", "sales fall first.", "Not prices."]}
            accentWord="sales"
            delay={20}
            fontSize={96}
          />
        </div>
      </AbsoluteFill>

      {/* BEAT 2: seller surplus */}
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: bOp * bOut }}>
        <GlassCard width={1200} delay={0}>
          <div style={{ fontFamily: P.font, padding: "12px 20px" }}>
            <div style={{ fontWeight: 700, fontSize: 34, color: P.muted, marginBottom: 20, textAlign: "center" }}>
              Sellers vs buyers · Redfin
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
              <div style={{ fontWeight: 800, fontSize: 40, color: P.ink, width: 220 }}>Sellers</div>
              <div style={{ flex: 1, height: 56, background: "rgba(229,72,77,0.15)", borderRadius: 16 }}>
                <div style={{ width: `${barW * 100}%`, height: "100%", background: P.loss, borderRadius: 16 }} />
              </div>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 20, marginTop: 16 }}>
              <div style={{ fontWeight: 800, fontSize: 40, color: P.ink, width: 220 }}>Buyers</div>
              <div style={{ flex: 1, height: 56, background: "rgba(56,189,248,0.15)", borderRadius: 16 }}>
                <div style={{ width: `${barW * 63}%`, height: "100%", background: P.neonBlue, borderRadius: 16 }} />
              </div>
            </div>
            <div style={{ fontWeight: 800, fontSize: 44, color: P.loss, textAlign: "center", marginTop: 24 }}>
              +58% more sellers — strongest buyer's market ever recorded
            </div>
          </div>
        </GlassCard>
      </AbsoluteFill>

      {/* BEAT 3: affordability gap */}
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: cOp * cOut }}>
        <div style={{ transform: `scale(${cPulse})` }}>
          <GlassCard width={1050} delay={0}>
            <div style={{ fontFamily: P.font, textAlign: "center", padding: "12px 20px" }}>
              <div style={{ fontWeight: 800, fontSize: 84, color: P.loss }}>−14%</div>
              <div style={{ fontWeight: 700, fontSize: 36, color: P.ink, marginTop: 8 }}>
                ≈ $62,000 off the median home
              </div>
              <div style={{ fontWeight: 600, fontSize: 28, color: P.muted, marginTop: 8 }}>
                just to restore the payment buyers had earlier this year
              </div>
            </div>
          </GlassCard>
        </div>
      </AbsoluteFill>

      {/* BEAT 4: golden cage */}
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", gap: 32, opacity: gOp }}>
        <Toast delay={2760} tone="info">Record equity · 3% fixed mortgage</Toast>
        <div style={{ textAlign: "center" }}>
          <KineticHeadline
            lines={["The golden cage:", "they can't afford to sell."]}
            delay={2900}
            fontSize={76}
          />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
