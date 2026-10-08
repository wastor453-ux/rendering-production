// COMPOSITION ENGINE (2026-10-08 completion pass).
// Compositions, not isolated components. Each pattern combines modes into a
// semantically dense finance scene. White space allowed; empty information not.
import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { T, CLAMP } from "./tokens";
import { GlassCard, Kicker, CountUp, Delta, entry } from "./primitives";
import { LineChartStory, MultiSeriesChart, StackedBar, ChartToMetric } from "./charts";
import { CausalDiagram } from "./explain";
import { PortfolioCardStack } from "./ui";

/** A. HERO + DATA: statement + major number + supporting chart + annotation + KPI. */
export const HeroData: React.FC<{
  kicker: string; claim: string; value: number; prefix?: string; suffix?: string; decimals?: number;
  chartData: number[]; chartLabels?: string[]; annotation: string; kpi: string; kpiLabel: string;
}> = ({ kicker, claim, value, prefix = "", suffix = "", decimals = 0, chartData, chartLabels = [], annotation, kpi, kpiLabel }) => {
  const f = useCurrentFrame();
  const c = entry(f, 0, 16); const n = entry(f, 14, 16); const ch = entry(f, 30, 20); const a = entry(f, 52, 16);
  return (
    <div style={{ width: 1560, display: "flex", gap: 48, alignItems: "stretch" }}>
      <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center", opacity: c.opacity, transform: `translateY(${c.y}px)` }}>
        <Kicker text={kicker} />
        <div style={{ fontFamily: T.font, fontWeight: 800, fontSize: 64, color: T.ink, lineHeight: 1.15, margin: "18px 0 30px", letterSpacing: -1.5 }}>{claim}</div>
        <div style={{ opacity: n.opacity }}>
          <CountUp value={value} prefix={prefix} suffix={suffix} decimals={decimals} fontSize={96} />
        </div>
        <div style={{ display: "flex", gap: 16, marginTop: 26, opacity: a.opacity }}>
          <GlassCard width={300} padding={22}>
            <div style={{ fontFamily: T.font, fontWeight: 700, fontSize: 20, color: T.inkMuted }}>{kpiLabel}</div>
            <div style={{ fontFamily: T.font, fontWeight: 800, fontSize: 40, color: T.primaryDeep, fontVariantNumeric: "tabular-nums" }}>{kpi}</div>
          </GlassCard>
        </div>
      </div>
      <div style={{ flex: 1.15, opacity: ch.opacity, transform: `translateY(${ch.y}px)` }}>
        <GlassCard width={960} padding={36}>
          <LineChartStory data={chartData} labels={chartLabels} eventIndex={chartData.length - 3}
            eventLabel={annotation} metric={kpi} />
        </GlassCard>
      </div>
    </div>
  );
};

/** B. CHART + METRIC: chart owns the frame, key metric linked, inflection annotated. */
export const ChartMetric: React.FC<{
  kicker: string; data: number[]; labels?: string[];
  eventIndex: number; eventLabel: string; eventSub?: string;
  metric: string; metricLabel: string;
}> = ({ kicker, data, labels = [], eventIndex, eventLabel, eventSub, metric, metricLabel }) => {
  const f = useCurrentFrame();
  const k = entry(f, 0, 14); const ch = entry(f, 12, 20); const m = entry(f, 60, 16);
  return (
    <div style={{ width: 1240, opacity: k.opacity }}>
      <div style={{ textAlign: "center", marginBottom: 24 }}><Kicker text={kicker} /></div>
      <div style={{ display: "flex", gap: 40, alignItems: "flex-start" }}>
        <div style={{ flex: 2.2, opacity: ch.opacity, transform: `translateY(${ch.y}px)` }}>
          <GlassCard width={960} padding={36}>
            <LineChartStory data={data} labels={labels} eventIndex={eventIndex}
              eventLabel={eventLabel} eventSub={eventSub} />
          </GlassCard>
        </div>
        <div style={{ flex: 1, opacity: m.opacity, transform: `translateY(${m.y}px)` }}>
          <GlassCard width={380} padding={36}>
            <div style={{ fontFamily: T.font, fontWeight: 700, fontSize: 22, color: T.inkMuted, marginBottom: 10 }}>{metricLabel}</div>
            <div style={{ fontFamily: T.font, fontWeight: 800, fontSize: 72, color: T.ink, fontVariantNumeric: "tabular-nums", letterSpacing: -2 }}>{metric}</div>
            <div style={{ fontFamily: T.font, fontWeight: 600, fontSize: 22, color: T.inkMuted, marginTop: 12, lineHeight: 1.45 }}>{eventLabel}</div>
          </GlassCard>
        </div>
      </div>
    </div>
  );
};

/** C. DASHBOARD STORY: shell -> primary KPI -> secondary metrics -> chart -> state. */
export const DashboardStory: React.FC<{
  kicker: string; primary: { label: string; value: string; delta: number };
  secondary: { label: string; value: string; delta: number }[];
  chartData: number[]; state: string;
}> = ({ kicker, primary, secondary, chartData, state }) => {
  const f = useCurrentFrame();
  const k = entry(f, 0, 14);
  const p1 = entry(f, 12, 18); const p2 = entry(f, 30, 18); const p3 = entry(f, 48, 20); const p4 = entry(f, 70, 16);
  return (
    <div style={{ width: 1500, opacity: k.opacity }}>
      <div style={{ textAlign: "center", marginBottom: 28 }}><Kicker text={kicker} /></div>
      <div style={{ display: "flex", gap: 36 }}>
        <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 24 }}>
          <div style={{ opacity: p1.opacity, transform: `translateY(${p1.y}px)` }}>
            <GlassCard width={460} padding={36}>
              <div style={{ fontFamily: T.font, fontWeight: 700, fontSize: 22, color: T.inkMuted }}>{primary.label}</div>
              <div style={{ fontFamily: T.font, fontWeight: 800, fontSize: 76, color: T.ink, fontVariantNumeric: "tabular-nums", letterSpacing: -2, margin: "6px 0" }}>{primary.value}</div>
              <Delta value={primary.delta} />
            </GlassCard>
          </div>
          <div style={{ opacity: p2.opacity, transform: `translateY(${p2.y}px)`, display: "flex", gap: 20 }}>
            {secondary.map((s) => (
              <GlassCard key={s.label} width={220} padding={24}>
                <div style={{ fontFamily: T.font, fontWeight: 700, fontSize: 19, color: T.inkMuted }}>{s.label}</div>
                <div style={{ fontFamily: T.font, fontWeight: 800, fontSize: 38, color: T.ink, fontVariantNumeric: "tabular-nums" }}>{s.value}</div>
                <Delta value={s.delta} />
              </GlassCard>
            ))}
          </div>
          <div style={{ opacity: p4.opacity }}>
            <GlassCard width={460} padding={28}>
              <div style={{ fontFamily: T.font, fontWeight: 700, fontSize: 24, color: T.primaryDeep }}>{state}</div>
            </GlassCard>
          </div>
        </div>
        <div style={{ flex: 1.4, opacity: p3.opacity, transform: `translateY(${p3.y}px)` }}>
          <GlassCard width={980} padding={36}>
            <MultiSeriesChart series={[
              { label: "Portfolio", color: T.primary, data: chartData },
              { label: "S&P 500", color: T.inkMuted, data: chartData.map((v, i) => v * (0.82 + i * 0.012)) },
            ]} indexed />
          </GlassCard>
        </div>
      </div>
    </div>
  );
};

/** D. COMPARISON STORY: left/right, shared metric, animated difference, verdict. */
export const ComparisonStory: React.FC<{
  kicker: string;
  left: { title: string; value: string; rows: [string, string][] };
  right: { title: string; value: string; rows: [string, string][] };
  delta: string; verdict: string;
}> = ({ kicker, left, right, delta, verdict }) => {
  const f = useCurrentFrame();
  const k = entry(f, 0, 14);
  const l = entry(f, 12, 18); const r = entry(f, 26, 18);
  const d = interpolate(f, [48, 66], [0, 1], { ...CLAMP });
  const v = entry(f, 72, 16);
  const card = (s: typeof left, e: { opacity: number; y: number }, accent: string) => (
    <div style={{ flex: 1, opacity: e.opacity, transform: `translateY(${e.y}px)` }}>
      <GlassCard width={560} padding={40}>
        <div style={{ fontFamily: T.font, fontWeight: 800, fontSize: 34, color: T.ink, marginBottom: 6 }}>{s.title}</div>
        <div style={{ fontFamily: T.font, fontWeight: 800, fontSize: 58, color: accent, fontVariantNumeric: "tabular-nums", marginBottom: 18 }}>{s.value}</div>
        {s.rows.map(([a, b]) => (
          <div key={a} style={{ display: "flex", justifyContent: "space-between", padding: "10px 0",
            borderTop: `1px solid ${T.glassBorder}`, fontFamily: T.font, fontSize: 24 }}>
            <span style={{ fontWeight: 600, color: T.inkMuted }}>{a}</span>
            <span style={{ fontWeight: 800, color: T.ink, fontVariantNumeric: "tabular-nums" }}>{b}</span>
          </div>
        ))}
      </GlassCard>
    </div>
  );
  return (
    <div style={{ width: 1280, opacity: k.opacity }}>
      <div style={{ textAlign: "center", marginBottom: 30 }}><Kicker text={kicker} /></div>
      <div style={{ display: "flex", gap: 36, alignItems: "stretch" }}>
        {card(left, l, T.inkMuted)}
        <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", opacity: d }}>
          <div style={{ fontFamily: T.font, fontWeight: 800, fontSize: 44, color: T.negative,
            background: T.negativeTint, borderRadius: 20, padding: "14px 26px",
            fontVariantNumeric: "tabular-nums", transform: `scale(${interpolate(d, [0, 1], [0.7, 1], CLAMP)})` }}>{delta}</div>
          <div style={{ fontFamily: T.font, fontWeight: 700, fontSize: 20, color: T.inkMuted, marginTop: 10 }}>difference</div>
        </div>
        {card(right, r, T.primaryDeep)}
      </div>
      <div style={{ textAlign: "center", marginTop: 30, opacity: v.opacity, transform: `translateY(${v.y}px)` }}>
        <span style={{ fontFamily: T.font, fontWeight: 800, fontSize: 32, color: T.ink }}>{verdict}</span>
      </div>
    </div>
  );
};

/** F. CAUSAL STORY: node -> link -> node -> consequence, with live metric. */
export const CausalStory: React.FC<{
  kicker: string;
  steps: { label: string; sub: string }[];
  metric: string; metricLabel: string;
}> = ({ kicker, steps, metric, metricLabel }) => {
  const f = useCurrentFrame();
  const k = entry(f, 0, 14); const m = entry(f, 90, 18);
  return (
    <div style={{ opacity: k.opacity }}>
      <div style={{ textAlign: "center", marginBottom: 16 }}><Kicker text={kicker} /></div>
      <CausalDiagram steps={steps} />
      <div style={{ display: "flex", justifyContent: "center", marginTop: 8, opacity: m.opacity, transform: `translateY(${m.y}px)` }}>
        <GlassCard width={520} padding={30}>
          <div style={{ display: "flex", alignItems: "baseline", gap: 18, justifyContent: "center" }}>
            <span style={{ fontFamily: T.font, fontWeight: 700, fontSize: 22, color: T.inkMuted }}>{metricLabel}</span>
            <span style={{ fontFamily: T.font, fontWeight: 800, fontSize: 56, color: T.primaryDeep, fontVariantNumeric: "tabular-nums" }}>{metric}</span>
          </div>
        </GlassCard>
      </div>
    </div>
  );
};

/** G. PORTFOLIO STORY: value + allocation cards + chart + emphasized change. */
export const PortfolioStory: React.FC<{
  kicker: string; total: string; totalDelta: number;
  cards: { name: string; value: string; delta: number }[];
  chartData: { label: string; segments: { label: string; value: number; color: string }[] }[];
  emphasis: string;
}> = ({ kicker, total, totalDelta, cards, chartData, emphasis }) => {
  const f = useCurrentFrame();
  const k = entry(f, 0, 14);
  const t = entry(f, 12, 18); const c = entry(f, 30, 20); const ch = entry(f, 52, 20); const e = entry(f, 78, 16);
  return (
    <div style={{ width: 1560, opacity: k.opacity }}>
      <div style={{ textAlign: "center", marginBottom: 26 }}><Kicker text={kicker} /></div>
      <div style={{ display: "flex", gap: 36, alignItems: "flex-start" }}>
        <div style={{ flex: 1, opacity: t.opacity, transform: `translateY(${t.y}px)` }}>
          <GlassCard width={420} padding={36}>
            <div style={{ fontFamily: T.font, fontWeight: 700, fontSize: 22, color: T.inkMuted }}>Total portfolio</div>
            <div style={{ fontFamily: T.font, fontWeight: 800, fontSize: 72, color: T.ink, fontVariantNumeric: "tabular-nums", letterSpacing: -2, margin: "6px 0" }}>{total}</div>
            <Delta value={totalDelta} />
          </GlassCard>
          <div style={{ marginTop: 24, opacity: e.opacity }}>
            <GlassCard width={420} padding={28}>
              <div style={{ fontFamily: T.font, fontWeight: 700, fontSize: 23, color: T.primaryDeep, lineHeight: 1.5 }}>{emphasis}</div>
            </GlassCard>
          </div>
        </div>
        <div style={{ flex: 1.6, opacity: c.opacity, transform: `translateY(${c.y}px)` }}>
          <PortfolioCardStack cards={cards} />
        </div>
        <div style={{ flex: 1.2, opacity: ch.opacity, transform: `translateY(${ch.y}px)` }}>
          <GlassCard width={520} padding={32}>
            <div style={{ fontFamily: T.font, fontWeight: 700, fontSize: 22, color: T.inkMuted, marginBottom: 14 }}>Allocation mix</div>
            <StackedBar groups={chartData} />
          </GlassCard>
        </div>
      </div>
    </div>
  );
};

/** Chart -> thesis transformation scene. */
export const ChartThesisTransform: React.FC<{
  data: number[]; metric: string; caption: string; thesis: string;
}> = ({ data, metric, caption, thesis }) => {
  const f = useCurrentFrame();
  const th = interpolate(f, [100, 120], [0, 1], CLAMP);
  return (
    <div style={{ width: 1240 }}>
      <div style={{ opacity: 1 - th }}>
        <GlassCard width={1240} padding={40}>
          <ChartToMetric data={data} metric={metric} caption={caption} />
        </GlassCard>
      </div>
      <div style={{ position: "absolute", top: "38%", left: 0, right: 0, textAlign: "center",
        opacity: th, transform: `translateY(${interpolate(th, [0, 1], [30, 0], CLAMP)}px)` }}>
        <Kicker text="The thesis" />
        <div style={{ fontFamily: T.font, fontWeight: 800, fontSize: 72, color: T.ink, letterSpacing: -2,
          maxWidth: 1100, margin: "20px auto 0", lineHeight: 1.2 }}>{thesis}</div>
      </div>
    </div>
  );
};
