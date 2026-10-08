import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { MeshBackground } from "../components/MeshBackground";
import { GlassCard } from "../components/GlassCard";
import { MoneyFlowChart } from "../components/MoneyFlowChart";
import { P, fmt$ } from "../theme";

const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const expo = Easing.bezier(0.16, 1, 0.3, 1);

// Real math: $100 purchasing power decaying at 3% inflation, 10 years
const values = Array.from({ length: 11 }, (_, y) => 100 / Math.pow(1.03, y));

/** S2 — The math. Glass card + glowing decay chart + hero stat. */
export const S2Math: React.FC = () => {
  const frame = useCurrentFrame();
  // Count the hero number down as the chart draws: 100 → 74
  const drawP = interpolate(frame, [20, 110], [0, 1], { ...CLAMP, easing: expo });
  const hero = 100 - (100 - 74.4) * drawP;
  const heroOp = interpolate(frame, [100, 115], [0, 1], { ...CLAMP, easing: expo });

  return (
    <AbsoluteFill>
      <MeshBackground />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <GlassCard width={1280} delay={5}>
          <div style={{ fontFamily: P.font, fontWeight: 700, fontSize: 34, color: P.muted, marginBottom: 8 }}>
            $100 of purchasing power · 3% inflation · 10 years
          </div>
          <MoneyFlowChart values={values} delay={20} drawFrames={90} />
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginTop: 16 }}>
            <div style={{ fontFamily: P.font }}>
              <div style={{ fontWeight: 800, fontSize: 88, color: P.ink, letterSpacing: -2, fontVariantNumeric: "tabular-nums" }}>
                {fmt$(hero)}
              </div>
              <div style={{ fontWeight: 600, fontSize: 30, color: P.loss }}>
                −26% of what it bought
              </div>
            </div>
            <div style={{ fontFamily: P.font, fontWeight: 600, fontSize: 28, color: P.muted, opacity: heroOp, textAlign: "right" }}>
              Your balance went up.<br />Your power went down.
            </div>
          </div>
        </GlassCard>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
