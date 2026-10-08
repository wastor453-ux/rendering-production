// Selector distribution report — representative 24-beat finance script.
import { selectVisualMode, SemanticEvidence } from "./select";

const beats: { id: string; ev: SemanticEvidence }[] = [
  { id: "b01", ev: { semantic_role: "hook", visual_verb: "reveal", narrative_intensity: 5 } },
  { id: "b02", ev: { semantic_role: "number", visual_verb: "count", number_presence: true, narrative_intensity: 4 } },
  { id: "b03", ev: { semantic_role: "trend", visual_verb: "fall", trend_presence: "down" } },
  { id: "b04", ev: { semantic_role: "cause", visual_verb: "connect", causal_structure: "chain" } },
  { id: "b05", ev: { semantic_role: "comparison", visual_verb: "compare", comparison_state: "A_vs_B" } },
  { id: "b06", ev: { semantic_role: "number", visual_verb: "count", number_presence: true } },
  { id: "b07", ev: { semantic_role: "mechanism", visual_verb: "accumulate", causal_structure: "flow" } },
  { id: "b08", ev: { semantic_role: "ranking", visual_verb: "reveal", comparison_state: "ranked" } },
  { id: "b09", ev: { semantic_role: "claim", visual_verb: "highlight", narrative_intensity: 3 } },
  { id: "b10", ev: { semantic_role: "allocation", visual_verb: "split", information_density: 2 } },
  { id: "b11", ev: { semantic_role: "trend", visual_verb: "rise", trend_presence: "up" } },
  { id: "b12", ev: { semantic_role: "effect", visual_verb: "transform", comparison_state: "before_after" } },
  { id: "b13", ev: { semantic_role: "example", visual_verb: "zoom", narrative_intensity: 2 } },
  { id: "b14", ev: { semantic_role: "mechanism", visual_verb: "collide", causal_structure: "loop" } },
  { id: "b15", ev: { semantic_role: "number", visual_verb: "count", number_presence: true, trend_presence: "down" } },
  { id: "b16", ev: { semantic_role: "timeline", visual_verb: "track" } },
  { id: "b17", ev: { semantic_role: "comparison", visual_verb: "split", comparison_state: "A_vs_B", information_density: 3 } },
  { id: "b18", ev: { semantic_role: "claim", visual_verb: "lock", narrative_intensity: 4 } },
  { id: "b19", ev: { semantic_role: "allocation", visual_verb: "reveal", information_density: 4 } },
  { id: "b20", ev: { semantic_role: "cause", visual_verb: "connect", causal_structure: "chain", number_presence: true } },
  { id: "b21", ev: { semantic_role: "escalation", visual_verb: "rise", narrative_intensity: 5, trend_presence: "up" } },
  { id: "b22", ev: { semantic_role: "payoff", visual_verb: "reveal", narrative_intensity: 5 } },
  { id: "b23", ev: { semantic_role: "thesis", visual_verb: "lock", narrative_intensity: 5 } },
  { id: "b24", ev: { semantic_role: "close", visual_verb: "freeze" } },
];

const picks = beats.map((b) => ({ id: b.id, mode: selectVisualMode(b.ev) }));
const counts: Record<string, number> = {};
picks.forEach((p) => { counts[p.mode] = (counts[p.mode] || 0) + 1; });
const typoOnly = (counts["hero_typography"] || 0);
const numberOnly = (counts["hero_number"] || 0);
const chartData = ["line_chart","area_chart","bar_chart","comparison_bars","donut_allocation","metric_grid"]
  .reduce((s, m) => s + (counts[m] || 0), 0);
const uiDash = ["dashboard","portfolio_card_stack","ranked_table","glass_notification","feature_icon_system"]
  .reduce((s, m) => s + (counts[m] || 0), 0);
const comps = ["before_after","two_sided_comparison"].reduce((s, m) => s + (counts[m] || 0), 0);
const diagrams = ["causal_diagram","causal_loop","timeline","flow_diagram"].reduce((s, m) => s + (counts[m] || 0), 0);
const n = beats.length;
const pct = (x: number) => ((x / n) * 100).toFixed(1) + "%";
console.log(JSON.stringify({
  total_beats: n,
  picks,
  distribution: {
    typography_only: pct(typoOnly), number_only: pct(numberOnly),
    chart_data: pct(chartData), dashboard_ui: pct(uiDash),
    comparisons: pct(comps), diagrams_timeline: pct(diagrams),
    thesis_closing: pct((counts["thesis_composition"] || 0) + (counts["closing_composition"] || 0)),
  },
  headline_dominance_check: typoOnly <= Math.ceil(n * 0.25) ? "PASS" : "FAIL",
}, null, 1));
