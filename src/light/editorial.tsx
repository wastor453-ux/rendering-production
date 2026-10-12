// editorial.tsx v2.0 — Rebuilt from Story System image (exact styles)
// 6 editorial modes matching reference specifications

import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import { T, CLAMP, EXPO } from "./tokens";
import { GlassCard, entry } from "./primitives";
import { LightCanvas } from "./primitives";

const expo = Easing.bezier(...EXPO);

// === 1. HeroTypography — Hook & Promise (Story System #1) ===
export const HeroTypography: React.FC<{
  question: string; highlight?: string; subtext?: string;
}> = ({ question, highlight, subtext }) => {
  const frame = useCurrentFrame();
  const { opacity, y } = entry(frame, 0, 18);

  // Split question to highlight part
  const parts = highlight ? question.split(highlight) : [question];

  return (
    <LightCanvas variant="coolBlue">
      <div style={{
        position: "absolute", inset: 0, display: "flex",
        alignItems: "center", justifyContent: "center",
        opacity, transform: `translateY(${y}px)`,
      }}>
        <div style={{ maxWidth: 1100, textAlign: "center", padding: "0 80px" }}>
          <div style={{
            fontFamily: T.font, fontSize: 76, fontWeight: 800,
            color: T.ink, lineHeight: 1.15, letterSpacing: -1,
          }}>
            {parts.map((p, i) => (
              <React.Fragment key={i}>
                {p}
                {i < parts.length - 1 && (
                  <span style={{ color: T.primary }}>{highlight}</span>
                )}
              </React.Fragment>
            ))}
          </div>
          {subtext && (
            <div style={{
              fontFamily: T.font, fontSize: 28, fontWeight: 400,
              color: T.inkMuted, marginTop: 24, lineHeight: 1.4,
            }}>
              {subtext}
            </div>
          )}
        </div>
      </div>
    </LightCanvas>
  );
};

// === 2. HeroNumber — KPI Hero (Motion Grammar #28) ===
export const HeroNumber: React.FC<{
  label: string; value: string; delta?: number; context?: string;
}> = ({ label, value, delta, context }) => {
  const frame = useCurrentFrame();
  const { opacity, y } = entry(frame, 0, 18);

  return (
    <LightCanvas variant="lavenderHorizon">
      <div style={{
        position: "absolute", inset: 0, display: "flex",
        alignItems: "center", justifyContent: "center",
        opacity, transform: `translateY(${y}px)`,
      }}>
        <GlassCard width={700} padding={56} style={{ textAlign: "center" }}>
          <div style={{ fontFamily: T.font, fontSize: 24, fontWeight: 600, color: T.inkMuted }}>
            {label}
          </div>
          <div style={{
            fontFamily: T.font, fontSize: 96, fontWeight: 800,
            color: T.ink, marginTop: 16, letterSpacing: -2,
          }}>
            {value}
          </div>
          {delta !== undefined && (
            <div style={{
              display: "inline-block", fontFamily: T.font, fontSize: 26, fontWeight: 700,
              color: delta >= 0 ? T.successDeep : T.negativeDeep,
              background: delta >= 0 ? T.successTint : T.negativeTint,
              borderRadius: 999, padding: "10px 24px", marginTop: 20,
            }}>
              {delta >= 0 ? "▲" : "▼"} {Math.abs(delta).toFixed(1)}%
            </div>
          )}
          {context && (
            <div style={{
              fontFamily: T.font, fontSize: 20, color: T.inkMuted, marginTop: 20,
            }}>
              {context}
            </div>
          )}
        </GlassCard>
      </div>
    </LightCanvas>
  );
};

// === 3. ThesisComposition — Concept Definition (Story System #3) ===
export const ThesisComposition: React.FC<{
  claim: string; value: string; delta?: string; steps?: { icon: string; label: string }[];
}> = ({ claim, value, delta, steps = [] }) => {
  const frame = useCurrentFrame();
  const { opacity } = entry(frame, 0, 18);

  return (
    <LightCanvas variant="glassAurora">
      <div style={{
        position: "absolute", inset: 0, display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center", opacity, padding: "0 80px",
      }}>
        <div style={{
          fontFamily: T.font, fontSize: 42, fontWeight: 800,
          color: T.ink, textAlign: "center", maxWidth: 900,
        }}>
          {claim}
        </div>
        <div style={{
          fontFamily: T.font, fontSize: 72, fontWeight: 800,
          color: T.primary, marginTop: 16,
        }}>
          {value}
        </div>
        {delta && (
          <div style={{ fontFamily: T.font, fontSize: 24, color: T.inkMuted, marginTop: 8 }}>
            {delta}
          </div>
        )}
        {steps.length > 0 && (
          <div style={{ display: "flex", gap: 24, marginTop: 48, alignItems: "center" }}>
            {steps.map((s, i) => (
              <React.Fragment key={i}>
                <GlassCard width={200} padding={24} style={{ textAlign: "center" }}>
                  <div style={{ fontSize: 48 }}>{s.icon}</div>
                  <div style={{
                    fontFamily: T.font, fontSize: 20, fontWeight: 700,
                    color: T.ink, marginTop: 12,
                  }}>
                    {s.label}
                  </div>
                </GlassCard>
                {i < steps.length - 1 && (
                  <div style={{ fontSize: 36, color: T.primary }}>→</div>
                )}
              </React.Fragment>
            ))}
          </div>
        )}
      </div>
    </LightCanvas>
  );
};

// === 4. ClosingComposition — Recap End Card (Story System #10) ===
export const ClosingComposition: React.FC<{
  line1: string; line2: string; cta?: string;
}> = ({ line1, line2, cta = "Subscribe" }) => {
  const frame = useCurrentFrame();
  const { opacity, y } = entry(frame, 0, 20);

  return (
    <LightCanvas variant="calmExecutive">
      <div style={{
        position: "absolute", inset: 0, display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center",
        opacity, transform: `translateY(${y}px)`,
      }}>
        <div style={{
          fontFamily: T.font, fontSize: 24, fontWeight: 700,
          color: T.inkMuted, letterSpacing: 4, textTransform: "uppercase",
        }}>
          Key Takeaway
        </div>
        <div style={{
          fontFamily: T.font, fontSize: 48, fontWeight: 800,
          color: T.ink, textAlign: "center", maxWidth: 800,
          marginTop: 20, lineHeight: 1.3,
        }}>
          {line1}<br />{line2}
        </div>
        <div style={{
          marginTop: 40, background: T.primary, color: "white",
          fontFamily: T.font, fontSize: 22, fontWeight: 700,
          padding: "16px 48px", borderRadius: 999,
        }}>
          {cta}
        </div>
      </div>
    </LightCanvas>
  );
};

// === 5. ImageryGlassOverlay ===
export const ImageryGlassOverlay: React.FC<{
  title: string; metric: string; delta?: string; imageUrl?: string;
}> = ({ title, metric, delta, imageUrl }) => {
  const frame = useCurrentFrame();
  const { opacity } = entry(frame, 0, 18);

  return (
    <LightCanvas variant="softOrb">
      {imageUrl && (
        <div style={{
          position: "absolute", inset: 0,
          backgroundImage: `url(${imageUrl})`, backgroundSize: "cover",
          backgroundPosition: "center", opacity: 0.3,
        }} />
      )}
      <div style={{
        position: "absolute", inset: 0, display: "flex",
        alignItems: "center", justifyContent: "center", opacity,
      }}>
        <GlassCard width={600} padding={48} style={{ textAlign: "center" }}>
          <div style={{ fontFamily: T.font, fontSize: 28, fontWeight: 700, color: T.ink }}>
            {title}
          </div>
          <div style={{
            fontFamily: T.font, fontSize: 64, fontWeight: 800,
            color: T.primary, marginTop: 16,
          }}>
            {metric}
          </div>
          {delta && (
            <div style={{ fontFamily: T.font, fontSize: 22, color: T.inkMuted, marginTop: 12 }}>
              {delta}
            </div>
          )}
        </GlassCard>
      </div>
    </LightCanvas>
  );
};

// === 6. RealWorldImagery ===
export const RealWorldImagery: React.FC<{
  headline: string; cards?: { label: string; amount: string }[];
}> = ({ headline, cards = [] }) => {
  const frame = useCurrentFrame();
  const { opacity } = entry(frame, 0, 18);

  return (
    <LightCanvas variant="coolBlue">
      <div style={{
        position: "absolute", inset: 0, display: "flex",
        alignItems: "center", justifyContent: "center",
        gap: 48, opacity, padding: "0 80px",
      }}>
        <div style={{ flex: 1 }}>
          <div style={{
            fontFamily: T.font, fontSize: 52, fontWeight: 800,
            color: T.ink, lineHeight: 1.2,
          }}>
            {headline}
          </div>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {cards.map((c, i) => {
            const { opacity: cop, y } = entry(frame, 10 + i * 8, 14);
            return (
              <GlassCard key={i} width={320} padding={24}
                style={{ opacity: cop, transform: `translateY(${y}px)` }}>
                <div style={{ fontFamily: T.font, fontSize: 18, color: T.inkMuted }}>
                  {c.label}
                </div>
                <div style={{
                  fontFamily: T.font, fontSize: 32, fontWeight: 800,
                  color: T.ink, marginTop: 4,
                }}>
                  {c.amount}
                </div>
              </GlassCard>
            );
          })}
        </div>
      </div>
    </LightCanvas>
  );
};
