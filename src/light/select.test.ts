// Selector test harness — executed by esbuild+node, not hand-checked.
import { selectVisualMode, resolveModeName, LEGACY_MAP, SemanticEvidence } from "./select";

const cases: { name: string; ev: SemanticEvidence; expect: string[] }[] = [
  { name: "savings rate statistic", ev: { semantic_role: "number", claim: "savings rate fell to 3%", visual_verb: "count", number_presence: true, narrative_intensity: 4 }, expect: ["hero_number"] },
  { name: "10y trend", ev: { semantic_role: "trend", visual_verb: "rise", trend_presence: "up" }, expect: ["line_chart"] },
  { name: "volume story", ev: { semantic_role: "trend", visual_verb: "accumulate", trend_presence: "up" }, expect: ["area_chart"] },
  { name: "rent vs mortgage", ev: { semantic_role: "comparison", comparison_state: "A_vs_B" }, expect: ["two_sided_comparison"] },
  { name: "rate before/after", ev: { semantic_role: "comparison", comparison_state: "before_after" }, expect: ["before_after"] },
  { name: "top holdings", ev: { semantic_role: "ranking", comparison_state: "ranked" }, expect: ["ranked_table"] },
  { name: "spending mix", ev: { semantic_role: "allocation", information_density: 2 }, expect: ["donut_allocation"] },
  { name: "portfolio overview", ev: { semantic_role: "allocation", information_density: 4 }, expect: ["dashboard"] },
  { name: "why inflation cools", ev: { semantic_role: "mechanism", causal_structure: "chain" }, expect: ["causal_diagram"] },
  { name: "debt spiral", ev: { semantic_role: "mechanism", causal_structure: "loop" }, expect: ["causal_loop"] },
  { name: "money flow", ev: { semantic_role: "mechanism", causal_structure: "flow" }, expect: ["flow_diagram"] },
  { name: "rate cycle history", ev: { semantic_role: "timeline" }, expect: ["timeline"] },
  { name: "major thesis", ev: { semantic_role: "thesis", narrative_intensity: 5 }, expect: ["thesis_composition"] },
  { name: "closing", ev: { semantic_role: "close" }, expect: ["closing_composition"] },
  { name: "strong claim no data", ev: { semantic_role: "claim", number_presence: false }, expect: ["hero_typography"] },
  { name: "dense multi-metric", ev: { information_density: 4 }, expect: ["dashboard"] },
  { name: "payment confirmed", ev: { semantic_role: "ui", visual_verb: "confirm" }, expect: ["glass_notification"] },
  { name: "legacy headline alias", ev: {}, expect: [] },
];

const results = cases.map((c) => {
  if (c.name === "legacy headline alias") {
    const r = resolveModeName("headline");
    const l = resolveModeName("barfall");
    return { case: c.name, resolve_headline: r, resolve_barfall: l,
             legacy_map_ok: r === "hero_typography" && l === "bar_chart" };
  }
  const got = selectVisualMode(c.ev);
  return { case: c.name, selected: got, expected: c.expect, pass: c.expect.includes(got) };
});
const npass = results.filter((r: any) => r.pass !== false && r.legacy_map_ok !== false).length;
console.log(JSON.stringify({ total: results.length, passed: npass, results }, null, 1));
