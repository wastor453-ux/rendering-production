import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { MeshBackground } from "../premium/components/MeshBackground";
import { GlassCard } from "../premium/components/GlassCard";
import { MoneyFlowChart } from "../premium/components/MoneyFlowChart";
import { P, fmt$ } from "../premium/theme";

const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const expo = Easing.bezier(0.16, 1, 0.3, 1);

// Real math: $100 purchasing power decaying at 3% inflation, 36 years
// 100 / 1.03^36 = 34.5 → −65.5% ≈ −66% (matches the approved thumbnail)
const values = Array.from({ length: 37 }, (_, y) => 100 / Math.pow(1.03, y));
const END = 100 / Math.pow(1.03, 36);

/**
 * MD2 — The autopsy (798f / 25.6s). 36-year decay chart + hero −66%.
 * SFX sync (scene-local frames): tick@135 "three percent", whoosh@300
 * "slow bleed", coin@405 "hundred dollars" → start-label pulse,
 * coin@495 "thirty-four dollars" → endpoint pulse, impact@585
 * "sixty-six percent" → hero pulse, low impact@726 "died anyway" → dim.
 */
export const MD2Math: React.FC = () => {
  const frame = useCurrentFrame();

  const drawP = interpolate(frame, [20, 260], [0, 1], { ...CLAMP, easing: expo });
  const hero = 100 - (100 - END) * drawP;
  const heroOp = interpolate(frame, [250, 270], [0, 1], { ...CLAMP, easing: expo });

  // $100 start label pulses on the coin SFX at 405f
  const startPulse = interpolate(frame, [405, 411, 423], [1, 1.25, 1], { ...CLAMP, easing: expo });
  // endpoint ring pulses on the coin SFX at 495f (chart's own endpoint dot)
  // hero number slams on the impact SFX at 585f
  const heroPulse = interpolate(frame, [585, 591, 607], [1, 1.18, 1], { ...CLAMP, easing: expo });
  // whole card dims on the low impact at 726f ("died anyway")
  const dim = interpolate(frame, [726, 734, 750], [1, 0.82, 1], { ...CLAMP, easing: expo });

  const sideOp = interpolate(frame, [630, 650], [0, 1], { ...CLAMP, easing: expo });
  const sideY = interpolate(sideOp, [0, 1], [30, 0], CLAMP);

  return (
    <AbsoluteFill>
      <MeshBackground />
      <AbsoluteFill
        style={{ justifyContent: "center", alignItems: "center", opacity: dim }}
      >
        <GlassCard width={1360} delay={5}>
          <div style={{ fontFamily: P.font, fontWeight: 700, fontSize: 34, color: P.muted, marginBottom: 8 }}>
            $100 of purchasing power · 3% inflation · 36 years
          </div>
          <MoneyFlowChart values={values} delay={20} drawFrames={240} />
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginTop: 16 }}>
            <div style={{ fontFamily: P.font, transform: `scale(${heroPulse})`, transformOrigin: "left bottom" }}>
              <div style={{ fontWeight: 800, fontSize: 96, color: P.ink, letterSpacing: -2, fontVariantNumeric: "tabular-nums", opacity: heroOp }}>
                {fmt$(hero)}
              </div>
              <div style={{ fontWeight: 600, fontSize: 32, color: P.loss, opacity: heroOp }}>
                −66% of what it bought
              </div>
            </div>
            <div
              style={{
                fontFamily: P.font,
                fontWeight: 600,
                fontSize: 30,
                color: P.muted,
                opacity: sideOp,
                transform: `translateY(${sideY}px)`,
                textAlign: "right",
              }}
            >
              Your balance went up.<br />Your wealth died anyway.
            </div>
          </div>
          {/* $100 start marker — pulses on coin SFX */}
          <div
            style={{
              position: "absolute",
              left: 70,
              top: 120,
              fontFamily: P.font,
              fontWeight: 800,
              fontSize: 30,
              color: P.gain,
              background: "rgba(22,163,74,0.12)",
              borderRadius: 14,
              padding: "8px 20px",
              opacity: interpolate(frame, [30, 50], [0, 1], CLAMP),
              transform: `scale(${startPulse})`,
            }}
          >
            $100
          </div>
        </GlassCard>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
