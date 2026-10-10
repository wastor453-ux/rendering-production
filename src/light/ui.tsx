// Financial UI modes: dashboard, card stack, ranked table, notification,
// feature icons, metric grid.
import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import { T, CLAMP, EXPO } from "./tokens";
import { GlassCard, Kicker, Label, Delta, CountUp, entry } from "./primitives";
import { LineChart } from "./charts";

const expo = Easing.bezier(...EXPO);

export const MetricGrid: React.FC<{ metrics: { label: string; value: string; delta?: number }[] }> = ({ metrics }) => {
  const frame = useCurrentFrame();
  return (
    <div style={{ display: "flex", gap: 24 }}>
      {metrics.map((m, i) => {
        const { opacity, y } = entry(frame, 8 + i * 10, 16);
        return (
          <div key={m.label} style={{ opacity, transform: `translateY(${y}px)` }}>
            <GlassCard width={300} padding={28}>
              <Label text={m.label} size={22} />
              <div style={{ fontFamily: T.font, fontWeight: 800, fontSize: 44, color: T.ink, margin: "10px 0 12px", fontVariantNumeric: "tabular-nums" }}>{m.value}</div>
              {m.delta !== undefined && <Delta value={m.delta} />}
            </GlassCard>
          </div>
        );
      })}
    </div>
  );
};

export const Dashboard: React.FC<{
  portfolioLabel?: string;
  portfolioValue?: number;
  portfolioDelta?: number;
  accounts?: { label: string; value: string; delta: number }[];
  growthLabel?: string;
  growthData?: number[];
}> = ({
  portfolioLabel = "Portfolio",
  portfolioValue = 48250.32,
  portfolioDelta = 12.4,
  accounts = [
    { label: "Investments", value: "$32,480", delta: 8.2 },
    { label: "Cash", value: "$12,340", delta: 14.6 },
  ],
  growthLabel = "Growth",
  growthData = [12, 14, 13, 18, 22, 21, 28, 34, 33, 41, 48, 55],
}) => {
  const frame = useCurrentFrame();
  const { opacity, y } = entry(frame, 0, 16);
  return (
    <div style={{ opacity, transform: `translateY(${y}px)`, display: "flex", gap: 28, alignItems: "stretch" }}>
      <GlassCard width={560} padding={40}>
        <Kicker text={portfolioLabel} />
        <div style={{ marginTop: 14 }}>
          <CountUp value={portfolioValue} prefix="$" decimals={2} fontSize={72} duration={50} />
        </div>
        <div style={{ marginTop: 12 }}><Delta value={portfolioDelta} /></div>
        <div style={{ display: "flex", gap: 16, marginTop: 28 }}>
          {accounts.map((a) => (
            <div key={a.label} style={{ flex: 1, background: T.canvasAlt, borderRadius: T.radiusM, padding: 20 }}>
              <Label text={a.label} size={20} />
              <div style={{ fontFamily: T.font, fontWeight: 800, fontSize: 32, color: T.ink, margin: "6px 0" }}>{a.value}</div>
              <Delta value={a.delta} />
            </div>
          ))}
        </div>
      </GlassCard>
      <GlassCard width={640} padding={40}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <Kicker text={growthLabel} />
          <Label text="Last 12 months" size={20} />
        </div>
        <div style={{ marginTop: 8, transform: "scale(0.72)", transformOrigin: "top left", width: 1250 }}>
          <LineChart data={growthData} />
        </div>
      </GlassCard>
    </div>
  );
};

export const PortfolioCardStack: React.FC<{ cards: { name: string; value: string; delta: number }[] }> = ({ cards }) => {
  const frame = useCurrentFrame();
  return (
    <div style={{ display: "flex", gap: 8 }}>
      {cards.map((c, i) => {
        const p = interpolate(frame, [6 + i * 12, 24 + i * 12], [0, 1], { ...CLAMP, easing: expo });
        return (
          <div key={c.name} style={{
            opacity: p,
            transform: `translateY(${interpolate(p, [0, 1], [60, 0], CLAMP)}px) rotate(${interpolate(p, [0, 1], [-4, 0], CLAMP)}deg)`,
            marginLeft: i === 0 ? 0 : -70, zIndex: i,
          }}>
            <GlassCard width={330} padding={30}>
              <div style={{ width: 54, height: 54, borderRadius: 16, background: T.blueTint, marginBottom: 18 }} />
              <div style={{ fontFamily: T.font, fontWeight: 700, fontSize: 28, color: T.ink }}>{c.name}</div>
              <div style={{ fontFamily: T.font, fontWeight: 800, fontSize: 36, color: T.ink, margin: "8px 0 12px" }}>{c.value}</div>
              <Delta value={c.delta} />
            </GlassCard>
          </div>
        );
      })}
    </div>
  );
};

export const RankedTable: React.FC<{ title: string; rows: { name: string; value: string; delta: number }[] }> = ({ title, rows }) => {
  const frame = useCurrentFrame();
  const { opacity, y } = entry(frame, 0, 14);
  return (
    <div style={{ opacity, transform: `translateY(${y}px)` }}>
      <GlassCard width={900} padding={40}>
        <div style={{ fontFamily: T.font, fontWeight: 800, fontSize: 36, color: T.ink, marginBottom: 8 }}>{title}</div>
        <div style={{ display: "flex", fontFamily: T.font, fontWeight: 700, fontSize: 20, color: T.inkMuted, padding: "14px 0", borderBottom: `1px solid ${T.glassBorder}` }}>
          <div style={{ flex: 2 }}>Asset</div><div style={{ flex: 1, textAlign: "right" }}>Value</div><div style={{ flex: 1, textAlign: "right" }}>Change</div>
        </div>
        {rows.map((r, i) => {
          const p = interpolate(frame, [10 + i * 9, 22 + i * 9], [0, 1], { ...CLAMP, easing: expo });
          return (
            <div key={r.name} style={{ display: "flex", alignItems: "center", padding: "16px 0", borderBottom: `1px solid ${T.glassBorder}`,
              opacity: p, transform: `translateX(${interpolate(p, [0, 1], [-24, 0], CLAMP)}px)` }}>
              <div style={{ flex: 2, display: "flex", alignItems: "center", gap: 16 }}>
                <div style={{ width: 40, height: 40, borderRadius: 12, background: T.blueTint, display: "flex", alignItems: "center", justifyContent: "center",
                  fontFamily: T.font, fontWeight: 800, fontSize: 20, color: T.primaryDeep }}>{i + 1}</div>
                <div style={{ fontFamily: T.font, fontWeight: 700, fontSize: 27, color: T.ink }}>{r.name}</div>
              </div>
              <div style={{ flex: 1, textAlign: "right", fontFamily: T.font, fontWeight: 700, fontSize: 27, color: T.ink, fontVariantNumeric: "tabular-nums" }}>{r.value}</div>
              <div style={{ flex: 1, textAlign: "right" }}><Delta value={r.delta} /></div>
            </div>
          );
        })}
      </GlassCard>
    </div>
  );
};

export const GlassNotification: React.FC<{ title: string; body: string }> = ({ title, body }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [6, 24], [0, 1], { ...CLAMP, easing: expo });
  return (
    <div style={{ opacity: p, transform: `translateY(${interpolate(p, [0, 1], [-40, 0], CLAMP)}px) scale(${interpolate(p, [0, 1], [0.94, 1], CLAMP)})` }}>
      <GlassCard width={620} padding={30}>
        <div style={{ display: "flex", gap: 22, alignItems: "center" }}>
          <div style={{ width: 64, height: 64, borderRadius: "50%", background: T.successTint, display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 30, color: T.successDeep, fontWeight: 800 }}>✓</div>
          <div style={{ flex: 1 }}>
            <div style={{ fontFamily: T.font, fontWeight: 800, fontSize: 30, color: T.ink }}>{title}</div>
            <div style={{ fontFamily: T.font, fontWeight: 500, fontSize: 24, color: T.inkMuted, marginTop: 4 }}>{body}</div>
          </div>
          <div style={{ fontFamily: T.font, fontSize: 26, color: T.inkMuted }}>✕</div>
        </div>
      </GlassCard>
    </div>
  );
};

const ICONS = ["◈", "⬢", "⬣", "✦"];
export const FeatureIconSystem: React.FC<{ items: { title: string; sub: string }[] }> = ({ items }) => {
  const frame = useCurrentFrame();
  const tints = [T.blueTint, T.successTint, T.lavender, T.warningTint];
  return (
    <div style={{ display: "flex", gap: 40 }}>
      {items.map((it, i) => {
        const { opacity, y } = entry(frame, 8 + i * 12, 16);
        return (
          <div key={it.title} style={{ opacity, transform: `translateY(${y}px)`, textAlign: "center", width: 250 }}>
            <div style={{ width: 96, height: 96, borderRadius: 28, background: tints[i % tints.length], margin: "0 auto 20px",
              display: "flex", alignItems: "center", justifyContent: "center", fontSize: 40, color: T.primaryDeep }}>{ICONS[i % ICONS.length]}</div>
            <div style={{ fontFamily: T.font, fontWeight: 800, fontSize: 32, color: T.ink }}>{it.title}</div>
            <div style={{ fontFamily: T.font, fontWeight: 500, fontSize: 23, color: T.inkMuted, marginTop: 8, lineHeight: 1.4 }}>{it.sub}</div>
          </div>
        );
      })}
    </div>
  );
};

/** 8. RANKING MOVEMENT: rows reorder mid-scene; rank change is visually readable. */
export const RankingMovement: React.FC<{
  title: string;
  before: { name: string; value: string; delta: number }[];
  after: { name: string; value: string; delta: number }[];
  caption: string;
}> = ({ title, before, after, caption }) => {
  const frame = useCurrentFrame();
  const { opacity, y } = entry(frame, 0, 14);
  // phase 1: show before ranking; phase 2: reorder to after; phase 3: settle + caption
  const swap = interpolate(frame, [55, 95], [0, 1], { ...CLAMP, easing: Easing.bezier(...EXPO) });
  const cap = interpolate(frame, [100, 116], [0, 1], CLAMP);
  const ROW_H = 76;
  const order = (list: typeof before) => {
    // map each row to its target index in `after`
    return list.map((r) => {
      const from = before.findIndex((x) => x.name === r.name);
      const to = after.findIndex((x) => x.name === r.name);
      return { r, from, to };
    });
  };
  return (
    <div style={{ opacity, transform: `translateY(${y}px)` }}>
      <GlassCard width={900} padding={40}>
        <div style={{ fontFamily: T.font, fontWeight: 800, fontSize: 36, color: T.ink, marginBottom: 8 }}>{title}</div>
        <div style={{ display: "flex", fontFamily: T.font, fontWeight: 700, fontSize: 20, color: T.inkMuted, padding: "14px 0", borderBottom: `1px solid ${T.glassBorder}` }}>
          <div style={{ flex: 2 }}>Asset</div><div style={{ flex: 1, textAlign: "right" }}>Value</div><div style={{ flex: 1, textAlign: "right" }}>Change</div>
        </div>
        <div style={{ position: "relative", height: before.length * ROW_H }}>
          {order(before).map(({ r, from, to }, i) => {
            const p = interpolate(frame, [10 + i * 9, 22 + i * 9], [0, 1], { ...CLAMP, easing: Easing.bezier(...EXPO) });
            const yPos = interpolate(swap, [0, 1], [from * ROW_H, to * ROW_H], CLAMP);
            const moved = from !== to;
            return (
              <div key={r.name} style={{
                position: "absolute", left: 0, right: 0, top: 0,
                display: "flex", alignItems: "center", height: ROW_H,
                borderBottom: `1px solid ${T.glassBorder}`,
                opacity: p, transform: `translateY(${yPos}px)`,
                background: moved && swap > 0.5 ? T.blueTint : "transparent",
                borderRadius: 14, padding: "0 12px",
              }}>
                <div style={{ flex: 2, display: "flex", alignItems: "center", gap: 16 }}>
                  <div style={{ width: 40, height: 40, borderRadius: 12,
                    background: moved ? T.primary : T.blueTint,
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontFamily: T.font, fontWeight: 800, fontSize: 20,
                    color: moved ? "#fff" : T.primaryDeep }}>
                    {interpolate(swap, [0, 1], [from + 1, to + 1], CLAMP).toFixed(0)}
                  </div>
                  <div style={{ fontFamily: T.font, fontWeight: 700, fontSize: 27, color: T.ink }}>{r.name}</div>
                </div>
                <div style={{ flex: 1, textAlign: "right", fontFamily: T.font, fontWeight: 700, fontSize: 27, color: T.ink, fontVariantNumeric: "tabular-nums" }}>{r.value}</div>
                <div style={{ flex: 1, textAlign: "right" }}><Delta value={r.delta} /></div>
              </div>
            );
          })}
        </div>
        {cap > 0 && (
          <div style={{ marginTop: 18, fontFamily: T.font, fontWeight: 700, fontSize: 24, color: T.primaryDeep, opacity: cap }}>
            {caption}
          </div>
        )}
      </GlassCard>
    </div>
  );
};
