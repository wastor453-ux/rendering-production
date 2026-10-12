// ui.tsx v2.0 — Rebuilt from Motion Grammar Section A (exact styles)
// 7 UI modes matching reference specifications

import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import { T, CLAMP, EXPO } from "./tokens";
import { GlassCard, entry } from "./primitives";
import { LightCanvas } from "./primitives";
import { KPICard } from "./components_v2";

const expo = Easing.bezier(...EXPO);

// === 1. MetricGrid — KPI Cards Grid (Motion Grammar #28) ===
export const MetricGrid: React.FC<{
  metrics: { label: string; value: string; delta?: number }[];
  title?: string;
}> = ({ metrics, title }) => {
  const frame = useCurrentFrame();

  return (
    <LightCanvas variant="softOrb">
      <div style={{
        position: "absolute", inset: 0, display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center", gap: 32, padding: "0 60px",
      }}>
        {title && (
          <div style={{ fontFamily: T.font, fontSize: 36, fontWeight: 800, color: T.ink }}>
            {title}
          </div>
        )}
        <div style={{
          display: "grid", gridTemplateColumns: `repeat(${Math.min(3, metrics.length)}, 1fr)`,
          gap: 24,
        }}>
          {metrics.map((m, i) => {
            const { opacity, y } = entry(frame, i * 10, 16);
            return (
              <div key={i} style={{ opacity, transform: `translateY(${y}px)` }}>
                <KPICard label={m.label} value={m.value} delta={m.delta} width={360} />
              </div>
            );
          })}
        </div>
      </div>
    </LightCanvas>
  );
};

// === 2. Dashboard — Dashboard Layout ===
export const Dashboard: React.FC<{
  title: string; kpis: { label: string; value: string }[];
  chart?: React.ReactNode;
}> = ({ title, kpis, chart }) => {
  const frame = useCurrentFrame();
  const { opacity } = entry(frame, 0, 18);

  return (
    <LightCanvas variant="softOrb">
      <div style={{ position: "absolute", inset: 40, opacity }}>
        <div style={{ fontFamily: T.font, fontSize: 36, fontWeight: 800, color: T.ink, marginBottom: 24 }}>
          {title}
        </div>
        <div style={{ display: "flex", gap: 20, marginBottom: 24 }}>
          {kpis.map((k, i) => (
            <GlassCard key={i} width={260} padding={24} style={{ flex: 1 }}>
              <div style={{ fontFamily: T.font, fontSize: 18, color: T.inkMuted, fontWeight: 600 }}>
                {k.label}
              </div>
              <div style={{ fontFamily: T.font, fontSize: 36, fontWeight: 800, color: T.ink, marginTop: 8 }}>
                {k.value}
              </div>
            </GlassCard>
          ))}
        </div>
        {chart && (
          <GlassCard width={1200} padding={32}>
            {chart}
          </GlassCard>
        )}
      </div>
    </LightCanvas>
  );
};

// === 3. PortfolioCardStack ===
export const PortfolioCardStack: React.FC<{
  cards: { name: string; value: string; change?: number }[];
}> = ({ cards }) => {
  const frame = useCurrentFrame();

  return (
    <LightCanvas variant="coolBlue">
      <div style={{
        position: "absolute", inset: 0, display: "flex",
        alignItems: "center", justifyContent: "center", gap: 20,
      }}>
        {cards.map((c, i) => {
          const { opacity, y } = entry(frame, i * 12, 16);
          const offset = (i - (cards.length - 1) / 2) * 12;
          return (
            <GlassCard key={i} width={300} padding={28}
              style={{
                opacity, transform: `translateY(${y + offset}px)`,
                zIndex: cards.length - i,
              }}>
              <div style={{ fontFamily: T.font, fontSize: 22, fontWeight: 700, color: T.ink }}>
                {c.name}
              </div>
              <div style={{
                fontFamily: T.font, fontSize: 40, fontWeight: 800,
                color: T.ink, marginTop: 12,
              }}>
                {c.value}
              </div>
              {c.change !== undefined && (
                <div style={{
                  fontFamily: T.font, fontSize: 20, fontWeight: 700, marginTop: 8,
                  color: c.change >= 0 ? T.successDeep : T.negativeDeep,
                }}>
                  {c.change >= 0 ? "▲" : "▼"} {Math.abs(c.change).toFixed(1)}%
                </div>
              )}
            </GlassCard>
          );
        })}
      </div>
    </LightCanvas>
  );
};

// === 4. RankedTable ===
export const RankedTable: React.FC<{
  title: string; rows: { name: string; value: string; rank: number }[];
}> = ({ title, rows }) => {
  const frame = useCurrentFrame();
  const { opacity } = entry(frame, 0, 18);

  return (
    <LightCanvas variant="dataAtmosphere">
      <div style={{
        position: "absolute", inset: 0, display: "flex",
        alignItems: "center", justifyContent: "center", opacity,
      }}>
        <GlassCard width={700} padding={36}>
          <div style={{
            fontFamily: T.font, fontSize: 28, fontWeight: 800,
            color: T.ink, marginBottom: 24,
          }}>
            {title}
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            {rows.map((r, i) => {
              const { opacity: rop } = entry(frame, 10 + i * 8, 12);
              const medal = r.rank === 1 ? "🥇" : r.rank === 2 ? "🥈" : r.rank === 3 ? "🥉" : `${r.rank}.`;
              return (
                <div key={i} style={{
                  display: "flex", alignItems: "center", gap: 16,
                  padding: "16px 20px", borderRadius: 12,
                  background: i % 2 === 0 ? "rgba(234,241,255,0.40)" : "transparent",
                  opacity: rop,
                }}>
                  <span style={{ fontSize: 24, minWidth: 40 }}>{medal}</span>
                  <span style={{ fontFamily: T.font, fontSize: 20, fontWeight: 600, color: T.ink, flex: 1 }}>
                    {r.name}
                  </span>
                  <span style={{ fontFamily: T.font, fontSize: 22, fontWeight: 800, color: T.primary }}>
                    {r.value}
                  </span>
                </div>
              );
            })}
          </div>
        </GlassCard>
      </div>
    </LightCanvas>
  );
};

// === 5. GlassNotification ===
export const GlassNotification: React.FC<{
  title: string; body: string; type?: "info" | "success" | "warning";
}> = ({ title, body, type = "info" }) => {
  const frame = useCurrentFrame();
  const { opacity, y } = entry(frame, 0, 16);

  const colors = {
    info: T.primary, success: T.teal, warning: T.warning,
  };
  const icons = { info: "ⓘ", success: "✓", warning: "⚠️" };

  return (
    <div style={{
      opacity, transform: `translateY(${y}px)`,
      display: "flex", gap: 16, alignItems: "flex-start",
      background: "rgba(255,255,255,0.92)",
      border: `1px solid ${T.glassBorder}`, borderLeft: `6px solid ${colors[type]}`,
      borderRadius: 16, padding: "20px 28px",
      boxShadow: "0 10px 30px rgba(40,85,170,0.10)",
      maxWidth: 600,
    }}>
      <span style={{
        width: 40, height: 40, borderRadius: "50%", background: colors[type],
        color: "white", display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 20, fontWeight: 700, flexShrink: 0,
      }}>
        {icons[type]}
      </span>
      <div>
        <div style={{ fontFamily: T.font, fontSize: 22, fontWeight: 700, color: T.ink }}>
          {title}
        </div>
        <div style={{ fontFamily: T.font, fontSize: 18, color: T.inkMuted, marginTop: 6 }}>
          {body}
        </div>
      </div>
    </div>
  );
};

// === 6. FeatureIconSystem ===
export const FeatureIconSystem: React.FC<{
  items: { title: string; sub: string; icon: string }[];
}> = ({ items }) => {
  const frame = useCurrentFrame();

  return (
    <LightCanvas variant="glassAurora">
      <div style={{
        position: "absolute", inset: 0, display: "flex",
        alignItems: "center", justifyContent: "center", gap: 24, padding: "0 60px",
      }}>
        {items.map((item, i) => {
          const { opacity, y } = entry(frame, i * 10, 16);
          return (
            <GlassCard key={i} width={260} padding={32}
              style={{ textAlign: "center", opacity, transform: `translateY(${y}px)` }}>
              <div style={{
                width: 72, height: 72, borderRadius: 20, margin: "0 auto",
                background: `linear-gradient(135deg, ${T.primary}20, ${T.cyan}20)`,
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 40,
              }}>
                {item.icon}
              </div>
              <div style={{
                fontFamily: T.font, fontSize: 22, fontWeight: 700,
                color: T.ink, marginTop: 16,
              }}>
                {item.title}
              </div>
              <div style={{
                fontFamily: T.font, fontSize: 17, color: T.inkMuted, marginTop: 8,
              }}>
                {item.sub}
              </div>
            </GlassCard>
          );
        })}
      </div>
    </LightCanvas>
  );
};

// === 7. RankingMovement — Animated Ranking ===
export const RankingMovement: React.FC<{
  items: { name: string; value: number }[];
}> = ({ items }) => {
  const frame = useCurrentFrame();

  // Sort by value (descending)
  const sorted = [...items].sort((a, b) => b.value - a.value);
  const max = Math.max(...items.map(i => i.value));

  return (
    <LightCanvas variant="coolBlue">
      <div style={{
        position: "absolute", inset: 0, display: "flex",
        alignItems: "center", justifyContent: "center",
      }}>
        <GlassCard width={700} padding={36}>
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {sorted.map((item, i) => {
              const p = interpolate(frame, [10 + i * 10, 40 + i * 10], [0, 1], { ...CLAMP, easing: expo });
              const w = (item.value / max) * 100;
              return (
                <div key={item.name}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                    <span style={{ fontFamily: T.font, fontSize: 20, fontWeight: 600, color: T.ink }}>
                      {i + 1}. {item.name}
                    </span>
                    <span style={{ fontFamily: T.font, fontSize: 20, fontWeight: 800, color: T.primary }}>
                      {item.value.toLocaleString()}
                    </span>
                  </div>
                  <div style={{ height: 20, borderRadius: 10, background: T.fog, overflow: "hidden" }}>
                    <div style={{
                      height: "100%", width: `${w * p}%`, borderRadius: 10,
                      background: i === 0
                        ? `linear-gradient(90deg, ${T.primary}, ${T.cyan})`
                        : T.blueTint,
                    }} />
                  </div>
                </div>
              );
            })}
          </div>
        </GlassCard>
      </div>
    </LightCanvas>
  );
};
