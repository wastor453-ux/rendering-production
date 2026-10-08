// ProductionBeats.tsx — PRODUCTION BEAT RUNTIME (P0 §7)
//
// Reads COMPILED JSON (never hand-written timing):
//   - beat_timeline.json  (from compile_beats.py)
//   - events.json         (from compile_events.py)
//
// For each beat:
//   1. builds SemanticEvidence from the compiled beat
//   2. calls selectVisualMode() — records the decision (Test F)
//   3. resolves the component for the COMPILED visual_mode
//   4. resolves the data payload via resolvePayload() (fail-closed)
//   5. builds the VisualEventMilestone and passes it via legacy adapters
//   6. renders through <Sequence>, preserving event IDs
//
// Mode authority: the compiled beat's visual_mode (AI editorial intent,
// validated by the compiler). The selector's output is recorded in the
// decision record; disagreements are surfaced, never silently applied.
//
// FinanceProof.tsx remains the legacy manual fixture. Do not delete it
// until this path passes golden regression (§12).

import React from "react";
import { Sequence } from "remotion";
import { LightCanvas, GlassCard, Kicker } from "./light/primitives";
import {
  HeroTypography, HeroNumber, ThesisComposition, ClosingComposition,
  ImageryGlassOverlay, RealWorldImagery,
} from "./light/editorial";
import { LineChartStory, BarChart, AreaChartStory, DonutChart, ComparisonBars } from "./light/charts";
import { TwoSidedComparison, CausalDiagram, BeforeAfter, CausalLoop, Timeline, FlowDiagram } from "./light/explain";
import {
  MetricGrid, Dashboard, PortfolioCardStack, RankedTable,
  GlassNotification, FeatureIconSystem,
} from "./light/ui";
import { selectVisualMode, SemanticEvidence } from "./light/select";
import { toLocalMilestone, legacyImpactProps, CompiledEvent, VisualEventMilestone } from "./light/milestone";
import { useMaterial } from "./light/materialTheme";
import { resolveScale } from "./light/compositionScale";

import beatDoc from "./compiled_p3/beat_timeline.json";
import eventsDoc from "./compiled_p3/events.json";
import heroNumber350k from "./compiled_p3/payloads/hero_number_350k.json";
// §9 — payloads imported statically (deterministic bundle); resolvePayload fails closed.
// import savingsRate from "./compiled/payloads/savings_rate_3_1.json";
// import savingsTrend from "./compiled/payloads/savings_trend_10y.json";
// import rentVsMortgage from "./compiled/payloads/rent_vs_mortgage.json";
// import stocksVsBonds from "./compiled/payloads/stocks_vs_bonds.json";

const FPS = 30;

// ---------------------------------------------------------------- payloads
// P3 rehearsal: hero_number payload
const PAYLOADS: Record<string, any> = {
  "payloads/hero_number_350k.json": heroNumber350k,
};

/** §9 — resolve a data_payload_ref to its payload. Unknown ref = throw (no invention). */
export function resolvePayload(ref: string | null | undefined): any {
  if (!ref) throw new Error(`resolvePayload: beat requires a payload but ref is null`);
  const p = PAYLOADS[ref];
  if (!p) throw new Error(`resolvePayload: unknown payload ref '${ref}' — no fallback`);
  return p;
}

// ------------------------------------------------------- selector decisions
export type SelectorDecision = {
  beat_id: string;
  compiled_mode: string;
  selected_mode: string;
  agree: boolean;
  evidence: SemanticEvidence;
};

export const SELECTOR_DECISIONS: SelectorDecision[] = [];

export function buildEvidence(b: any): SemanticEvidence {
  return {
    semantic_role: b.semantic_role,
    claim: b.claim,
    visual_verb: b.visual_verb,
    focal_object: b.focal_object,
    narrative_intensity: Math.round((b.intensity ?? 0.5) * 5),
    information_density: b.data_presence ? 4 : 2,
    comparison_state: b.comparison_state ?? "none",
    comparison_kind: b.comparison_kind ?? undefined,
    number_presence: b.data_type === "statistic",
    trend_presence: b.semantic_role === "trend" ? "down" : "none",
    causal_structure: b.visual_mode === "causal_diagram" ? "chain" : "none",
  };
}

// ------------------------------------------------------------------ registry
export type BeatCtx = {
  beat: any;
  event: CompiledEvent | null;
  milestone: VisualEventMilestone | null;
  payload: any;
  pres: any;
};

const Center: React.FC<{ mode: string; children?: React.ReactNode }> = ({ mode, children }) => {
  const { compositionScale: requested } = useMaterial();
  const resolved = resolveScale(mode, requested);
  // Split-strategy modes (e.g. real_world_financial_imagery) resolve their own
  // layer scales internally; Center only positions, never applies a uniform scale.
  if (resolved.strategy === "split") {
    return (
      <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ position: "absolute", inset: 0 }}>{children}</div>
      </div>
    );
  }
  // Fail-closed: resolveScale never returns a clipping scale; unknown modes get 1.0.
  const scale = resolved.effective_scale;
  return (
    <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", transform: `scale(${scale})` }}>{children}</div>
    </div>
  );
};

export const REGISTRY: Record<string, (ctx: BeatCtx) => React.ReactNode> = {
  hero_typography: ({ pres }) => (
    <Center mode="hero_typography"><HeroTypography kicker={pres.kicker ?? ""} lines={pres.lines ?? []} accentLine={pres.accentLine ?? 0} /></Center>
  ),
  hero_number: ({ milestone, payload, pres }) => {
    const v = payload?.values?.[0];
    if (typeof v !== "number") throw new Error("hero_number: payload.values[0] must be a number");
    return (
      <Center mode="hero_number"><HeroNumber kicker={pres.kicker ?? ""} value={v}
        suffix={payload.unit ?? ""} decimals={1} caption={pres.caption ?? ""}
        {...(milestone ? legacyImpactProps(milestone) : {})} /></Center>
    );
  },
  line_chart: ({ milestone, payload, pres }) => (
    <Center mode="line_chart"><GlassCard width={1080} padding={44}><Kicker text={pres.kicker ?? ""} />
      <div style={{ marginTop: 16 }}><LineChartStory
        data={payload.values} labels={pres.labels ?? []}
        eventIndex={pres.eventIndex ?? 0} eventLabel={pres.eventLabel ?? ""} eventSub={pres.eventSub ?? ""}
        metric={pres.metric ?? ""}
        {...(milestone ? legacyImpactProps(milestone) : {})} /></div></GlassCard></Center>
  ),
  two_sided_comparison: ({ milestone, pres }) => (
    <Center mode="two_sided_comparison"><TwoSidedComparison left={pres.left} right={pres.right}
      {...(milestone ? legacyImpactProps(milestone, { row: pres.impactRow ?? 0 }) : {})} /></Center>
  ),
  causal_diagram: ({ milestone, pres }) => (
    <Center mode="causal_diagram"><div><div style={{ textAlign: "center", marginBottom: 10 }}><Kicker text={pres.kicker ?? ""} /></div>
      <CausalDiagram steps={pres.steps ?? []}
        {...(milestone ? legacyImpactProps(milestone, { node: pres.impactNode ?? 0 }) : {})} /></div></Center>
  ),
  bar_chart: ({ milestone, payload, pres }) => {
    const data = (payload.values as any[]).map((d) => ({ label: d.label, value: d.value }));
    return (
      <Center mode="bar_chart"><GlassCard width={1080} padding={44}><Kicker text={pres.kicker ?? ""} />
        <div style={{ marginTop: 16 }}><BarChart data={data} highlight={pres.highlight ?? 0}
          {...(milestone ? legacyImpactProps(milestone, { bar: pres.impactBar ?? 0 }) : {})} /></div></GlassCard></Center>
    );
  },
  closing_composition: ({ pres }) => (
    <Center mode="closing_composition"><div>
      <ThesisComposition claim={pres.thesisClaim ?? ""} value={pres.thesisValue ?? ""} delta={pres.thesisDelta ?? 0} />
      <div style={{ marginTop: 24 }}><ClosingComposition line1={pres.closeLine1 ?? ""} line2={pres.closeLine2 ?? ""} /></div>
    </div></Center>
  ),
  // P0 2026-10-09: 12 selector-reachable modes wired into the live registry.
  area_chart: ({ milestone, payload, pres }) => (
    <Center mode="area_chart"><GlassCard width={1080} padding={44}><Kicker text={pres.kicker ?? ""} />
      <div style={{ marginTop: 16 }}><AreaChartStory
        data={payload.values} highlightFrom={pres.highlightFrom ?? 0} highlightTo={pres.highlightTo ?? 0}
        highlightLabel={pres.highlightLabel ?? ""} metric={pres.metric ?? ""}
        {...(milestone ? legacyImpactProps(milestone) : {})} /></div></GlassCard></Center>
  ),
  donut_allocation: ({ pres }) => {
    const segments = pres.segments ?? [];
    if (!Array.isArray(segments) || segments.length === 0) throw new Error("donut_allocation: pres.segments must be a non-empty array");
    return (
      <Center mode="donut_allocation"><GlassCard width={720} padding={44}><Kicker text={pres.kicker ?? ""} />
        <div style={{ marginTop: 16 }}><DonutChart segments={segments} /></div></GlassCard></Center>
    );
  },
  metric_grid: ({ pres }) => {
    const metrics = pres.metrics ?? [];
    if (!Array.isArray(metrics) || metrics.length === 0) throw new Error("metric_grid: pres.metrics must be a non-empty array");
    return (
      <Center mode="metric_grid"><MetricGrid metrics={metrics} /></Center>
    );
  },
  dashboard: ({ payload, pres }) => (
    <Center mode="dashboard"><Dashboard
      portfolioLabel={pres.kicker ?? "Portfolio"}
      portfolioValue={payload?.values?.[0] ?? 0}
      portfolioDelta={pres.portfolioDelta ?? 0}
      accounts={pres.accounts ?? []}
      growthLabel={pres.growthLabel ?? "Growth"}
      growthData={payload?.values?.slice(1) ?? []}
    /></Center>
  ),
  ranked_table: ({ pres }) => {
    const rows = pres.rows ?? [];
    if (!Array.isArray(rows) || rows.length === 0) throw new Error("ranked_table: pres.rows must be a non-empty array");
    return (
      <Center mode="ranked_table"><RankedTable title={pres.title ?? ""} rows={rows} /></Center>
    );
  },
  glass_notification: ({ pres }) => (
    <Center mode="glass_notification"><GlassNotification title={pres.title ?? ""} body={pres.body ?? ""} /></Center>
  ),
  before_after: ({ pres }) => {
    if (!pres.before || !pres.after) throw new Error("before_after: pres.before and pres.after are required");
    return (
      <Center mode="before_after"><BeforeAfter before={pres.before} after={pres.after} /></Center>
    );
  },
  causal_loop: ({ pres }) => {
    const steps = pres.steps ?? [];
    if (!Array.isArray(steps) || steps.length === 0) throw new Error("causal_loop: pres.steps must be a non-empty array");
    return (
      <Center mode="causal_loop"><CausalLoop steps={steps} /></Center>
    );
  },
  timeline: ({ pres }) => {
    const events = pres.events ?? [];
    if (!Array.isArray(events) || events.length === 0) throw new Error("timeline: pres.events must be a non-empty array");
    return (
      <Center mode="timeline"><div><div style={{ textAlign: "center", marginBottom: 10 }}><Kicker text={pres.kicker ?? ""} /></div>
        <Timeline events={events} /></div></Center>
    );
  },
  flow_diagram: ({ pres }) => {
    const nodes = pres.nodes ?? [];
    if (!Array.isArray(nodes) || nodes.length === 0) throw new Error("flow_diagram: pres.nodes must be a non-empty array");
    return (
      <Center mode="flow_diagram"><FlowDiagram nodes={nodes} /></Center>
    );
  },
  imagery_plus_glass_overlay: ({ payload, pres }) => (
    <Center mode="imagery_plus_glass_overlay"><ImageryGlassOverlay
      title={pres.title ?? ""} metric={pres.metric ?? ""} delta={payload?.values?.[0] ?? 0} /></Center>
  ),
  thesis_composition: ({ pres }) => (
    <Center mode="thesis_composition"><ThesisComposition
      claim={pres.thesisClaim ?? ""} value={pres.thesisValue ?? ""} delta={pres.thesisDelta ?? 0} /></Center>
  ),
  // P0 2026-10-09: 4 previously orphaned modes now in the live chain.
  comparison_bars: ({ pres }) => {
    if (!pres.left || !pres.right) throw new Error("comparison_bars: pres.left and pres.right are required");
    return (
      <Center mode="comparison_bars"><GlassCard width={1080} padding={48}><Kicker text={pres.kicker ?? ""} />
        <div style={{ marginTop: 16 }}><ComparisonBars left={pres.left} right={pres.right} /></div></GlassCard></Center>
    );
  },
  portfolio_card_stack: ({ pres }) => {
    const cards = pres.cards ?? [];
    if (!Array.isArray(cards) || cards.length === 0) throw new Error("portfolio_card_stack: pres.cards must be a non-empty array");
    return (
      <Center mode="portfolio_card_stack"><PortfolioCardStack cards={cards} /></Center>
    );
  },
  feature_icon_system: ({ pres }) => {
    const items = pres.items ?? [];
    if (!Array.isArray(items) || items.length === 0) throw new Error("feature_icon_system: pres.items must be a non-empty array");
    return (
      <Center mode="feature_icon_system"><div><div style={{ textAlign: "center", marginBottom: 20 }}><Kicker text={pres.kicker ?? ""} /></div>
        <FeatureIconSystem items={items} /></div></Center>
    );
  },
  real_world_financial_imagery: ({ pres }) => (
    // Split-scale mode: RealWorldImagery resolves its own layer scales via the
    // policy; Center detects the split strategy and does not apply a uniform scale.
    <Center mode="real_world_financial_imagery"><RealWorldImagery
      image={pres.image ?? "light/office.jpg"} title={pres.title ?? ""} subtitle={pres.subtitle ?? ""} /></Center>
  ),
};

// ------------------------------------------------------------------ runtime
const eventsByBeat: Record<string, CompiledEvent[]> = {};
for (const e of (eventsDoc as any).events as CompiledEvent[]) {
  (eventsByBeat[e.beat_id] ||= []).push(e);
}

function renderBeat(b: any): React.ReactNode {
  const from = Math.floor(b.start_time * FPS);
  const dur = Math.ceil(b.end_time * FPS) - from;

  // §8 — selector runs on compiled evidence; decision recorded.
  const evidence = buildEvidence(b);
  const selected = selectVisualMode(evidence);
  SELECTOR_DECISIONS.push({
    beat_id: b.beat_id, compiled_mode: b.visual_mode,
    selected_mode: selected, agree: selected === b.visual_mode, evidence,
  });

  // Mode authority: the compiled (compiler-validated) mode.
  const render = REGISTRY[b.visual_mode];
  if (!render) throw new Error(`ProductionBeats: no renderer for mode '${b.visual_mode}' (no silent fallback)`);

  const evs = eventsByBeat[b.beat_id] ?? [];
  const ev0 = evs[0] ?? null;
  const milestone = ev0 ? toLocalMilestone(ev0, from) : null;

  // §9 — data modes resolve real payloads; throws when missing.
  const payload = b.data_presence ? resolvePayload(b.data_payload_ref) : null;

  const el = render({ beat: b, event: ev0, milestone, payload, pres: b.presentation ?? {} });
  return (
    <Sequence key={b.beat_id} from={from} durationInFrames={dur} name={b.beat_id}>
      <LightCanvas>{el}</LightCanvas>
    </Sequence>
  );
}

export const P3_BEATS = (beatDoc as any).beats as any[];

export const P3Rehearsal: React.FC = () => <>{P3_BEATS.map(renderBeat)}</>;

export const P3_TOTAL = Math.ceil(
  Math.max(...P3_BEATS.map((b: any) => b.end_time)) * FPS,
);
