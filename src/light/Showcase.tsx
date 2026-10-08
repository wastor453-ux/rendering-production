// VisualShowcase v2 — FINAL COMPLETION PASS (2026-10-08).
// 23 visual modes (all motion-proven) + 7 combination scenes.
// Semantic animation: reveal -> build -> explain -> highlight -> transform -> resolve.
import React from "react";
import { Sequence, useCurrentFrame, staticFile, Img } from "remotion";
import { T } from "./tokens";
import { LightCanvas, GlassCard, Kicker, SectionHead } from "./primitives";

const Center: React.FC<{ children?: React.ReactNode }> = ({ children }) => (
  <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>{children}</div>
);
import { HeroTypography, HeroNumber, ThesisComposition, ClosingComposition, ImageryGlassOverlay } from "./editorial";
import {
  LineChartStory, AreaChartStory, BarChart, ComparisonBars, DonutChart,
  StackedBar, MultiSeriesChart,
} from "./charts";
import {
  MetricGrid, Dashboard, PortfolioCardStack, RankedTable, GlassNotification,
  FeatureIconSystem, RankingMovement,
} from "./ui";
import { BeforeAfter, TwoSidedComparison, CausalDiagram, CausalLoop, Timeline, FlowDiagram } from "./explain";
import {
  HeroData, ChartMetric, DashboardStory, ComparisonStory, CausalStory,
  PortfolioStory, ChartThesisTransform,
} from "./compositions";

const INTRO = 60;
const MODE_SEC = 120;
const COMBO_SEC = 170;

const savings = [7.8, 7.2, 8.1, 6.9, 7.5, 12.4, 11.8, 6.1, 4.9, 3.8, 3.1];
const saveLabels = ["2016", "2018", "2020", "2022", "2024", "2026"];

export const SHOWCASE_MODES: { id: string; title: string; el: React.ReactNode }[] = [
  { id: "hero_typography", title: "Hero Typography",
    el: <Center><HeroTypography kicker="Astor Legacy" lines={["Wealth is a legacy.", "Build yours."]} accentLine={1} /></Center> },
  { id: "hero_number", title: "Hero Number",
    el: <Center><HeroNumber kicker="Personal savings rate" value={3.1} suffix="%" decimals={1} delta={-2.4} caption="Lowest since 2008" /></Center> },
  { id: "line_chart", title: "Line Chart — Event + Annotation",
    el: <Center><GlassCard width={1080} padding={44}><Kicker text="Savings rate · 10 years" />
      <div style={{ marginTop: 16 }}><LineChartStory data={savings} labels={saveLabels}
        eventIndex={5} eventLabel="2020 spike" eventSub="Stimulus + lockdown saving" metric="3.1%" /></div></GlassCard></Center> },
  { id: "area_chart", title: "Area Chart — Highlighted Period",
    el: <Center><GlassCard width={1080} padding={44}><Kicker text="Cumulative inflows" />
      <div style={{ marginTop: 16 }}><AreaChartStory data={[5, 9, 14, 22, 31, 45, 62, 84, 110, 142]}
        highlightFrom={5} highlightTo={8} highlightLabel="Rate-hike era" metric="$142B" /></div></GlassCard></Center> },
  { id: "bar_chart", title: "Bar Chart",
    el: <Center><GlassCard width={1080} padding={44}><Kicker text="Debt by category" />
      <div style={{ marginTop: 16 }}><BarChart data={[
        { label: "Mortgage", value: 82 }, { label: "Auto", value: 41 },
        { label: "Cards", value: 63 }, { label: "Student", value: 35 }]} highlight={2} /></div></GlassCard></Center> },
  { id: "comparison_bars", title: "Comparison Bars",
    el: <Center><GlassCard width={1080} padding={48}><Kicker text="Monthly housing cost" />
      <div style={{ marginTop: 28 }}><ComparisonBars left={{ label: "Median rent", value: 2150 }} right={{ label: "Median mortgage", value: 2980 }} /></div></GlassCard></Center> },
  { id: "donut_allocation", title: "Donut Allocation",
    el: <Center><DonutChart segments={[
      { label: "Stocks", value: 55, color: "#5368F7" },
      { label: "Bonds", value: 25, color: "#C9D0FF" },
      { label: "Cash", value: 20, color: "#51C59A" }]} /></Center> },
  { id: "metric_grid", title: "Metric Grid",
    el: <Center><div><div style={{ textAlign: "center", marginBottom: 34 }}><Kicker text="Market snapshot" /></div>
      <MetricGrid metrics={[{ label: "S&P 500", value: "6,482", delta: 1.2 }, { label: "Inflation", value: "2.9%", delta: -1.4 },
        { label: "10Y Yield", value: "4.21%", delta: -0.8 }, { label: "Unemployment", value: "4.3%", delta: 0.6 }]} /></div></Center> },
  { id: "dashboard", title: "Dashboard",
    el: <Center><Dashboard /></Center> },
  { id: "portfolio_card_stack", title: "Portfolio Card Stack",
    el: <Center><div><div style={{ textAlign: "center", marginBottom: 40 }}><Kicker text="Allocation" /></div>
      <PortfolioCardStack cards={[{ name: "Stocks", value: "$58,200", delta: 12.4 }, { name: "Bonds", value: "$24,800", delta: 3.1 },
        { name: "Cash", value: "$18,400", delta: 1.2 }, { name: "Real Estate", value: "$42,000", delta: -2.4 }]} /></div></Center> },
  { id: "ranked_table", title: "Ranked Table",
    el: <Center><RankedTable title="Top Holdings" rows={[
      { name: "Apple (AAPL)", value: "$12,430", delta: 2.4 }, { name: "Microsoft (MSFT)", value: "$10,280", delta: 1.8 },
      { name: "NVIDIA (NVDA)", value: "$8,760", delta: 3.2 }, { name: "Tesla (TSLA)", value: "$6,420", delta: -0.6 }]} /></Center> },
  { id: "glass_notification", title: "Glass Notification",
    el: <Center><GlassNotification title="Payment successful" body="Your funds have been transferred." /></Center> },
  { id: "feature_icon_system", title: "Feature Icon System",
    el: <Center><div><div style={{ textAlign: "center", marginBottom: 40 }}><Kicker text="Four moves" /></div>
      <FeatureIconSystem items={[{ title: "Invest", sub: "Build long-term wealth" }, { title: "Save", sub: "Reach your goals" },
        { title: "Spend", sub: "Manage with confidence" }, { title: "Grow", sub: "Unlock opportunities" }]} /></div></Center> },
  { id: "before_after", title: "Before / After",
    el: <Center><BeforeAfter before={{ label: "Mortgage rate · 2021", value: "3.0%" }} after={{ label: "Mortgage rate · today", value: "6.5%" }} /></Center> },
  { id: "two_sided_comparison", title: "Two-Sided Comparison",
    el: <Center><TwoSidedComparison left={{ title: "Renter", rows: [["Monthly cost", "$2,150"], ["Equity built", "$0"], ["Flexibility", "High"]] }}
      right={{ title: "Owner", rows: [["Monthly cost", "$2,980"], ["Equity built", "$41k"], ["Flexibility", "Low"]] }} /></Center> },
  { id: "causal_diagram", title: "Causal Diagram",
    el: <Center><div><div style={{ textAlign: "center", marginBottom: 10 }}><Kicker text="How rate hikes cool inflation" /></div>
      <CausalDiagram steps={[{ label: "Rate hikes", sub: "Fed raises rates" }, { label: "Borrowing costs", sub: "mortgages, cards up" },
        { label: "Spending slows", sub: "demand cools" }, { label: "Inflation cools", sub: "prices stabilize" }]} /></div></Center> },
  { id: "causal_loop", title: "Causal Loop",
    el: <Center><CausalLoop steps={[{ label: "Low savings", sub: "3% rate" }, { label: "More debt", sub: "cards fill gap" },
      { label: "Interest burden", sub: "$1.26T/yr" }, { label: "Less savings", sub: "cycle repeats" }]} /></Center> },
  { id: "timeline", title: "Timeline",
    el: <Center><div><div style={{ textAlign: "center", marginBottom: 20 }}><Kicker text="Rate cycle" /></div>
      <Timeline events={[{ year: "2020", label: "Rates cut to 0%" }, { year: "2022", label: "Hiking begins" },
        { year: "2023", label: "Peak 5.5%" }, { year: "2024", label: "First cuts" }, { year: "2026", label: "New normal" }]} /></div></Center> },
  { id: "flow_diagram", title: "Flow Diagram",
    el: <Center><FlowDiagram nodes={["Paycheck", "Bills", "Savings", "Investments"]} /></Center> },
  { id: "real_world_financial_imagery", title: "Real-World Imagery",
    el: <div style={{ position: "absolute", inset: 0 }}>
      <Img src={staticFile("light/office.jpg")} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      <div style={{ position: "absolute", left: 120, bottom: 110 }}>
        <div style={{ fontFamily: T.font, fontWeight: 800, fontSize: 54, color: "#fff", textShadow: "0 2px 24px rgba(0,0,0,0.35)" }}>The economy, up close</div>
        <div style={{ fontFamily: T.font, fontWeight: 600, fontSize: 26, color: "rgba(255,255,255,0.85)", marginTop: 8 }}>Real-world imagery · placeholder asset</div>
      </div>
    </div> },
  { id: "imagery_plus_glass_overlay", title: "Imagery + Glass Overlay",
    el: <ImageryGlassOverlay title="Markets at a turning point" metric="$40.0T" delta={8.2} /> },
  { id: "thesis_composition", title: "Thesis Composition",
    el: <Center><ThesisComposition claim="The saver is becoming the investor." value="$1.2T" delta={8.4} /></Center> },
  { id: "closing_composition", title: "Closing Composition",
    el: <Center><ClosingComposition line1="Wealth is a legacy." line2="Build yours." /></Center> },
];

const combos: { id: string; title: string; el: React.ReactNode }[] = [
  { id: "combo_hero_data", title: "Combo · Hero + Data",
    el: <Center><HeroData kicker="The big picture" claim="Housing costs broke the budget."
      value={2980} prefix="$" chartData={savings} chartLabels={saveLabels}
      annotation="Costs up 38% since 2021" kpi="$830" kpiLabel="Monthly gap" /></Center> },
  { id: "combo_chart_metric", title: "Combo · Chart + Metric",
    el: <Center><ChartMetric kicker="Savings collapse" data={savings} labels={saveLabels}
      eventIndex={5} eventLabel="2020 stimulus spike" eventSub="Then the long slide"
      metric="3.1%" metricLabel="Today" /></Center> },
  { id: "combo_dashboard_story", title: "Combo · Dashboard Story",
    el: <Center><DashboardStory kicker="Your money, live" primary={{ label: "Net worth", value: "$143,400", delta: 6.2 }}
      secondary={[{ label: "Cash", value: "$18.4k", delta: 1.2 }, { label: "Invested", value: "$125k", delta: 7.8 }]}
      chartData={[100, 104, 103, 109, 114, 112, 119, 125, 131, 143]} state="On track — ahead of plan" /></Center> },
  { id: "combo_comparison_story", title: "Combo · Comparison Story",
    el: <Center><ComparisonStory kicker="Rent vs own" left={{ title: "Renter", value: "$2,150", rows: [["Equity built", "$0"], ["Flexibility", "High"]] }}
      right={{ title: "Owner", value: "$2,980", rows: [["Equity built", "$41k"], ["Flexibility", "Low"]] }}
      delta="+$830" verdict="Owning costs more monthly — but builds $41k equity." /></Center> },
  { id: "combo_causal_story", title: "Combo · Causal Story",
    el: <Center><CausalStory kicker="Why inflation cooled" steps={[
      { label: "Rate hikes", sub: "Fed raises rates" }, { label: "Borrowing costs", sub: "mortgages, cards up" },
      { label: "Spending slows", sub: "demand cools" }, { label: "Inflation cools", sub: "prices stabilize" }]}
      metric="2.9%" metricLabel="Inflation today" /></Center> },
  { id: "combo_portfolio_story", title: "Combo · Portfolio Story",
    el: <Center><PortfolioStory kicker="Portfolio review" total="$143,400" totalDelta={6.2}
      cards={[{ name: "Stocks", value: "$58,200", delta: 12.4 }, { name: "Bonds", value: "$24,800", delta: 3.1 },
        { name: "Cash", value: "$18,400", delta: 1.2 }, { name: "Real Estate", value: "$42,000", delta: -2.4 }]}
      chartData={[
        { label: "2024", segments: [{ label: "Stocks", value: 50, color: "#5368F7" }, { label: "Bonds", value: 30, color: "#C9D0FF" }, { label: "Cash", value: 20, color: "#51C59A" }] },
        { label: "2025", segments: [{ label: "Stocks", value: 55, color: "#5368F7" }, { label: "Bonds", value: 25, color: "#C9D0FF" }, { label: "Cash", value: 20, color: "#51C59A" }] },
        { label: "2026", segments: [{ label: "Stocks", value: 58, color: "#5368F7" }, { label: "Bonds", value: 24, color: "#C9D0FF" }, { label: "Cash", value: 18, color: "#51C59A" }] },
      ]}
      emphasis="Stocks drove 80% of this year's growth." /></Center> },
  { id: "combo_chart_thesis", title: "Combo · Chart → Thesis",
    el: <Center><ChartThesisTransform data={savings} metric="3.1%" caption="Lowest savings rate since 2008"
      thesis="The saver is becoming the investor." /></Center> },
];

export const SHOWCASE_TOTAL = INTRO + SHOWCASE_MODES.length * MODE_SEC + combos.length * COMBO_SEC;

const TitleCard: React.FC = () => (
  <LightCanvas>
    <Center>
      <div style={{ textAlign: "center" }}>
        <div style={{ fontFamily: T.font, fontWeight: 700, fontSize: 24, letterSpacing: 8, color: T.inkMuted }}>ASTOR LEGACY</div>
        <div style={{ fontFamily: T.font, fontWeight: 800, fontSize: 92, color: T.ink, letterSpacing: -2, marginTop: 20 }}>Light Premium Fintech</div>
        <div style={{ fontFamily: T.font, fontWeight: 600, fontSize: 32, color: T.primary, marginTop: 16 }}>Visual system showcase · 23 modes + 7 compositions</div>
      </div>
    </Center>
  </LightCanvas>
);

const SectionShell: React.FC<{ index: string; title: string; children: React.ReactNode }> = ({ index, title, children }) => {
  const frame = useCurrentFrame();
  return (
    <LightCanvas>
      <SectionHead index={index} title={title} local={frame} />
      {children}
    </LightCanvas>
  );
};

const allSections = [
  ...SHOWCASE_MODES.map((s, i) => ({ ...s, index: `${String(i + 1).padStart(2, "0")} / ${SHOWCASE_MODES.length + combos.length}`, dur: MODE_SEC })),
  ...combos.map((s, i) => ({ ...s, index: `C${i + 1} / ${combos.length}`, dur: COMBO_SEC })),
];

export const VisualShowcase: React.FC = () => {
  let cursor = INTRO;
  return (
    <>
      <Sequence from={0} durationInFrames={INTRO} name="title"><TitleCard /></Sequence>
      {allSections.map((s) => {
        const from = cursor; cursor += s.dur;
        return (
          <Sequence key={s.id} from={from} durationInFrames={s.dur} name={s.title}>
            <SectionShell index={s.index} title={s.title}>{s.el}</SectionShell>
          </Sequence>
        );
      })}
    </>
  );
};

// Frame ranges for the resumable segment renderer (exported for tooling).
export const SHOWCASE_SEGMENTS: { id: string; title: string; from: number; dur: number }[] = (() => {
  let cursor = INTRO;
  const segs: { id: string; title: string; from: number; dur: number }[] = [{ id: "seg_00_title", title: "Title", from: 0, dur: INTRO }];
  allSections.forEach((s, i) => {
    segs.push({ id: `seg_${String(i + 1).padStart(2, "0")}_${s.id}`, title: s.title, from: cursor, dur: s.dur });
    cursor += s.dur;
  });
  return segs;
})();
