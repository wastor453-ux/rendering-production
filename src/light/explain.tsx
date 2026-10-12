// explain.tsx v2.0 — Rebuilt from Money Mechanics + Motion Grammar images
// 6 explanation modes with exact reference styles

import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import { T, CLAMP, EXPO } from "./tokens";
import { GlassCard, entry } from "./primitives";
import { LightCanvas } from "./primitives";

const expo = Easing.bezier(...EXPO);

// === 1. BeforeAfter ===
export const BeforeAfter: React.FC<{
  before: { label: string; value: string };
  after: { label: string; value: string };
  title?: string;
}> = ({ before, after, title }) => {
  const frame = useCurrentFrame();
  const { opacity } = entry(frame, 0, 18);

  return (
    <LightCanvas variant="coolBlue">
      <div style={{
        position: "absolute", inset: 0, display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center", opacity, gap: 32,
      }}>
        {title && (
          <div style={{ fontFamily: T.font, fontSize: 36, fontWeight: 800, color: T.ink }}>
            {title}
          </div>
        )}
        <div style={{ display: "flex", gap: 32, alignItems: "center" }}>
          <GlassCard width={320} padding={36} style={{ textAlign: "center", opacity: 0.7 }}>
            <div style={{ fontFamily: T.font, fontSize: 20, fontWeight: 600, color: T.inkMuted }}>
              {before.label}
            </div>
            <div style={{ fontFamily: T.font, fontSize: 48, fontWeight: 800, color: T.inkMuted, marginTop: 12 }}>
              {before.value}
            </div>
          </GlassCard>
          <div style={{ fontSize: 48, color: T.primary }}>→</div>
          <GlassCard width={320} padding={36} style={{ textAlign: "center", border: `2px solid ${T.primary}` }}>
            <div style={{ fontFamily: T.font, fontSize: 20, fontWeight: 600, color: T.primary }}>
              {after.label}
            </div>
            <div style={{ fontFamily: T.font, fontSize: 48, fontWeight: 800, color: T.primary, marginTop: 12 }}>
              {after.value}
            </div>
          </GlassCard>
        </div>
      </div>
    </LightCanvas>
  );
};

// === 2. TwoSidedComparison — A/B Cards (Money Mechanics #3, #5) ===
export const TwoSidedComparison: React.FC<{
  left: { title: string; points: string[]; icon?: string };
  right: { title: string; points: string[]; icon?: string };
  vsLabel?: string;
}> = ({ left, right, vsLabel = "VS" }) => {
  const frame = useCurrentFrame();
  const { opacity: opL, y: yL } = entry(frame, 0, 16);
  const { opacity: opR, y: yR } = entry(frame, 10, 16);

  const Card = ({ data, opacity, y, accent }: any) => (
    <GlassCard width={380} padding={32} style={{ opacity, transform: `translateY(${y}px)` }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        {data.icon && <span style={{ fontSize: 36 }}>{data.icon}</span>}
        <div style={{ fontFamily: T.font, fontSize: 26, fontWeight: 800, color: T.ink }}>
          {data.title}
        </div>
      </div>
      <div style={{ marginTop: 20, display: "flex", flexDirection: "column", gap: 12 }}>
        {data.points.map((p: string, i: number) => (
          <div key={i} style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
            <span style={{ color: accent, fontWeight: 700, fontSize: 20 }}>✓</span>
            <span style={{ fontFamily: T.font, fontSize: 19, color: T.ink }}>{p}</span>
          </div>
        ))}
      </div>
    </GlassCard>
  );

  return (
    <LightCanvas variant="lavenderHorizon">
      <div style={{
        position: "absolute", inset: 0, display: "flex",
        alignItems: "center", justifyContent: "center", gap: 24,
      }}>
        <Card data={left} opacity={opL} y={yL} accent={T.primary} />
        <div style={{
          width: 64, height: 64, borderRadius: "50%", background: T.fog,
          display: "flex", alignItems: "center", justifyContent: "center",
          fontFamily: T.font, fontWeight: 800, fontSize: 20, color: T.primary,
          flexShrink: 0,
        }}>
          {vsLabel}
        </div>
        <Card data={right} opacity={opR} y={yR} accent={T.teal} />
      </div>
    </LightCanvas>
  );
};

// === 3. CausalDiagram — Step Flow (Story System #4) ===
export const CausalDiagram: React.FC<{
  steps: { label: string; sub: string; icon?: string }[];
  title?: string;
}> = ({ steps, title }) => {
  const frame = useCurrentFrame();

  return (
    <LightCanvas variant="glassAurora">
      <div style={{
        position: "absolute", inset: 0, display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center", gap: 40, padding: "0 60px",
      }}>
        {title && (
          <div style={{ fontFamily: T.font, fontSize: 36, fontWeight: 800, color: T.ink }}>
            {title}
          </div>
        )}
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          {steps.map((s, i) => {
            const { opacity, y } = entry(frame, i * 12, 16);
            return (
              <React.Fragment key={i}>
                <GlassCard width={240} padding={28}
                  style={{ textAlign: "center", opacity, transform: `translateY(${y}px)` }}>
                  {s.icon && <div style={{ fontSize: 48 }}>{s.icon}</div>}
                  <div style={{
                    fontFamily: T.font, fontSize: 22, fontWeight: 700,
                    color: T.ink, marginTop: 12,
                  }}>
                    {s.label}
                  </div>
                  <div style={{
                    fontFamily: T.font, fontSize: 17, color: T.inkMuted, marginTop: 6,
                  }}>
                    {s.sub}
                  </div>
                </GlassCard>
                {i < steps.length - 1 && (
                  <div style={{ fontSize: 36, color: T.primary, flexShrink: 0 }}>→</div>
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>
    </LightCanvas>
  );
};

// === 4. CausalLoop — Circular Flow ===
export const CausalLoop: React.FC<{
  steps: { label: string; sub: string }[];
}> = ({ steps }) => {
  const frame = useCurrentFrame();
  const { opacity } = entry(frame, 0, 20);

  const R = 200; const CX = 400; const CY = 220;

  return (
    <LightCanvas variant="softOrb">
      <div style={{
        position: "absolute", inset: 0, display: "flex",
        alignItems: "center", justifyContent: "center", opacity,
      }}>
        <svg width={800} height={440} viewBox="0 0 800 440">
          {/* Circular arrow */}
          <path
            d={`M${CX + R},${CY} A${R},${R} 0 1,1 ${CX + R - 1},${CY - 1}`}
            fill="none" stroke={T.primary} strokeWidth={4}
            strokeDasharray="12 8" opacity={0.4}
          />
          {steps.map((s, i) => {
            const angle = (i / steps.length) * 360 - 90;
            const x = CX + R * Math.cos((angle * Math.PI) / 180);
            const y = CY + R * Math.sin((angle * Math.PI) / 180);
            const { opacity: op } = entry(frame, i * 10, 14);
            return (
              <g key={i} opacity={op}>
                <circle cx={x} cy={y} r={52} fill="white"
                  stroke={T.primary} strokeWidth={3} />
                <text x={x} y={y - 6} textAnchor="middle"
                  fontFamily={T.font} fontSize={17} fontWeight={700} fill={T.ink}>
                  {s.label}
                </text>
                <text x={x} y={y + 18} textAnchor="middle"
                  fontFamily={T.font} fontSize={14} fill={T.inkMuted}>
                  {s.sub}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </LightCanvas>
  );
};

// === 5. Timeline — Horizontal Timeline (Motion Grammar #43) ===
export const Timeline: React.FC<{
  events: { year: string; label: string }[];
  title?: string;
}> = ({ events, title }) => {
  const frame = useCurrentFrame();

  return (
    <LightCanvas variant="coolBlue">
      <div style={{
        position: "absolute", inset: 0, display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center", gap: 48, padding: "0 100px",
      }}>
        {title && (
          <div style={{ fontFamily: T.font, fontSize: 36, fontWeight: 800, color: T.ink }}>
            {title}
          </div>
        )}
        <div style={{ display: "flex", alignItems: "flex-start", width: "100%" }}>
          {events.map((e, i) => {
            const active = frame > 20 + i * 15;
            const { opacity } = entry(frame, i * 15, 14);
            return (
              <React.Fragment key={i}>
                <div style={{
                  display: "flex", flexDirection: "column", alignItems: "center",
                  gap: 12, opacity, minWidth: 140,
                }}>
                  <div style={{
                    width: active ? 40 : 28, height: active ? 40 : 28,
                    borderRadius: "50%", background: active ? T.primary : T.blueTint,
                    border: active ? `4px solid ${T.cyan}` : "none",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    color: "white", fontFamily: T.font, fontWeight: 700,
                  }}>
                    {active ? "✓" : ""}
                  </div>
                  <div style={{
                    fontFamily: T.font, fontSize: 20, fontWeight: 700,
                    color: active ? T.ink : T.inkMuted,
                  }}>
                    {e.year}
                  </div>
                  <div style={{
                    fontFamily: T.font, fontSize: 17, color: T.inkMuted,
                    textAlign: "center",
                  }}>
                    {e.label}
                  </div>
                </div>
                {i < events.length - 1 && (
                  <div style={{
                    flex: 1, height: 4, borderRadius: 2, marginTop: 18,
                    background: frame > 20 + i * 15 ? T.primary : T.blueTint,
                  }} />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>
    </LightCanvas>
  );
};

// === 6. FlowDiagram — Node Flow ===
export const FlowDiagram: React.FC<{
  nodes: string[]; title?: string;
}> = ({ nodes, title }) => {
  const frame = useCurrentFrame();

  return (
    <LightCanvas variant="dataAtmosphere">
      <div style={{
        position: "absolute", inset: 0, display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center", gap: 40,
      }}>
        {title && (
          <div style={{ fontFamily: T.font, fontSize: 36, fontWeight: 800, color: T.ink }}>
            {title}
          </div>
        )}
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          {nodes.map((n, i) => {
            const { opacity, y } = entry(frame, i * 10, 14);
            const colors = [T.primary, T.cyan, T.teal, T.lavender];
            return (
              <React.Fragment key={i}>
                <div style={{
                  background: colors[i % colors.length], borderRadius: 16,
                  padding: "20px 32px", fontFamily: T.font, fontSize: 22,
                  fontWeight: 700, color: "white",
                  opacity, transform: `translateY(${y}px)`,
                }}>
                  {n}
                </div>
                {i < nodes.length - 1 && (
                  <div style={{ fontSize: 32, color: T.primary }}>→</div>
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>
    </LightCanvas>
  );
};
