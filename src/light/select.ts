// STEP 9 — semantic visual selection (VISUAL_BRAIN §2, §5).
// Never beat.kind -> template. Evaluate the semantic evidence, then select.
import schema from "../visual_mode_schema.json";

export type SemanticEvidence = {
  semantic_role?: string;   // claim|number|comparison|trend|mechanism|ranking|allocation|timeline|consequence|thesis|imagery|ui
  claim?: string;
  visual_verb?: string;
  focal_object?: string;
  narrative_intensity?: number;   // 1-5
  information_density?: number;   // 1-5
  comparison_state?: "none" | "A_vs_B" | "before_after" | "ranked";
  // Refined 2026-10-08 (b6 arbitration): what KIND of A_vs_B comparison.
  //   magnitude_gap      — one shared metric, story is the SIZE of the gap (stocks 12% vs bonds 3%)
  //   attribute_contrast — N attributes per side, story is the PATTERN (renter vs owner: cost/equity/gap)
  comparison_kind?: "magnitude_gap" | "attribute_contrast";
  // Added 2026-10-09 (P0 registry): scope of a magnitude_gap comparison.
  //   pair   — exactly two items (rent $2,150 vs mortgage $2,980) → comparison_bars
  //   series — 3+ categories → bar_chart (default, preserves existing behavior)
  comparison_scope?: "pair" | "series";
  // Added 2026-10-09 (P0 registry): form of an allocation.
  //   shares   — proportional breakdown → donut_allocation (default)
  //   accounts — discrete account/asset cards → portfolio_card_stack
  //   overview — dense multi-metric → dashboard (via information_density)
  allocation_form?: "shares" | "accounts" | "overview";
  // Added 2026-10-09 (P0 registry): form of a UI element.
  //   notification — single alert → glass_notification (default for ui role)
  //   icon_system  — set of steps/actions/categories → feature_icon_system
  ui_form?: "notification" | "icon_system";
  number_presence?: boolean;
  // Added 2026-10-09 (P1.1): character of a trend.
  //   cumulative  — build-up/accumulation over time → area_chart
  //   directional — ordinary trajectory/movement → line_chart (default)
  trend_character?: "cumulative" | "directional";
  // Added 2026-10-09 (P1.1): temporal frame of a comparison.
  //   transition — then-vs-now / old-vs-new / pre-vs-post → before_after
  //   static     — A-vs-B attribute contrast → two_sided_comparison (default)
  // Only applies when explicitly set; never overrides explicit comparison_state.
  temporal_frame?: "transition" | "static";
  trend_presence?: "none" | "up" | "down" | "volatile";
  causal_structure?: "none" | "chain" | "loop" | "flow";
};

const MODES: { id: string; family: string; verbs: string[]; best_for: string[] }[] =
  (schema as any).modes;

const has = (arr: string[], keys: string[]) =>
  arr.some((x) => keys.some((k) => x.toLowerCase().includes(k)));

export function selectVisualMode(ev: SemanticEvidence): string {
  const role = (ev.semantic_role ?? "").toLowerCase();
  const verb = (ev.visual_verb ?? "").toLowerCase();

  // Rule 2 — mechanisms deserve diagrams
  if (ev.causal_structure === "loop") return "causal_loop";
  if (ev.causal_structure === "chain") return "causal_diagram";
  if (ev.causal_structure === "flow") return "flow_diagram";
  if (role.includes("mechanism")) return has([verb], ["loop"]) ? "causal_loop" : "causal_diagram";

  // Rule 3 — comparisons deserve paired structure.
  // Refined 2026-10-08 (b6 arbitration): A_vs_B splits by comparison KIND.
  //   magnitude_gap      -> bar_chart (one shared metric; story is the SIZE of the gap)
  //   attribute_contrast -> two_sided_comparison (N attributes per side; story is the pattern)
  // Unspecified kind keeps the legacy default (two_sided_comparison) — no silent behavior change.
  // P1.1 2026-10-09: explicit temporal transition → before_after.
  // Only when the editor marks temporal_frame="transition". Does NOT turn
  // every A_vs_B into before_after — static contrasts keep existing routing.
  if (ev.temporal_frame === "transition") return "before_after";
  if (ev.comparison_state === "before_after") return "before_after";
  if (ev.comparison_state === "A_vs_B") {
    if (ev.comparison_kind === "magnitude_gap") {
      // P0 2026-10-09: pair scope → comparison_bars (two items);
      // series scope (or unspecified) → bar_chart (preserves existing behavior).
      return ev.comparison_scope === "pair" ? "comparison_bars" : "bar_chart";
    }
    return "two_sided_comparison";
  }
  if (ev.comparison_state === "ranked") return "ranked_table";

  // Rule 1 — data deserves data
  const trend = ev.trend_presence === "up" || ev.trend_presence === "down" || ev.trend_presence === "volatile";
  if (role.includes("trend") || trend) {
    // P1.1 2026-10-09: cumulative build-up → area_chart via semantic evidence.
    // trend_character is the primary signal; verb substring is legacy fallback.
    if (ev.trend_character === "cumulative") return "area_chart";
    if (has([verb, role], ["accumul", "volume", "cumul"])) return "area_chart";
    return "line_chart";
  }
  // P1.1 2026-10-09: semantic_role "rank"/"ranking" IS the ranking objective.
  // A ranked/leaderboard intent naturally wants ranked_table, not bar_chart.
  // (comparison_state="ranked" still works via the explicit check above.)
  if (role.includes("rank")) return "ranked_table";
  // P0 2026-10-09: imagery checked before the generic number rule —
  // imagery+number is a specific combination (glass overlay), not a generic metric.
  if (role.includes("imagery")) return ev.number_presence ? "imagery_plus_glass_overlay" : "real_world_financial_imagery";
  if (role.includes("allocat") || role.includes("portfolio")) {
    // P0 2026-10-09: allocation form determines the renderer.
    //   accounts → portfolio_card_stack (discrete account cards)
    //   overview (or density≥4) → dashboard (dense multi-metric)
    //   shares (default) → donut_allocation (proportional breakdown)
    if (ev.allocation_form === "accounts") return "portfolio_card_stack";
    if (ev.allocation_form === "overview" || (ev.information_density ?? 0) >= 4) return "dashboard";
    return "donut_allocation";
  }
  if (role.includes("number") || ev.number_presence) {
    return (ev.narrative_intensity ?? 0) >= 4 ? "hero_number" : "metric_grid";
  }

  if (role.includes("timeline") || role.includes("history")) return "timeline";
  if (role.includes("thesis")) return "thesis_composition";
  if (role.includes("close") || role.includes("consequence")) return "closing_composition";
  if (role.includes("ui") || role.includes("transaction") || role.includes("threshold")) {
    // P0 2026-10-09: icon_system form → feature_icon_system (set of steps/actions);
    // default → glass_notification (single alert).
    return ev.ui_form === "icon_system" ? "feature_icon_system" : "glass_notification";
  }

  // Rule 6 — typography is a premium accent, not the default
  if (role.includes("claim") || role.includes("hook")) return "hero_typography";

  // Fallback: dashboard for dense multi-metric, else hero typography
  return (ev.information_density ?? 0) >= 3 ? "dashboard" : "hero_typography";
}

/** Legacy mode compatibility aliases (VISUAL_BRAIN §4). */
export const LEGACY_MAP: Record<string, string> = {
  headline: "hero_typography",
  number: "hero_number",
  barfall: "bar_chart",
  cascade: "portfolio_card_stack",
  split: "two_sided_comparison",
  close: "closing_composition",
};

export function resolveModeName(name: string): string {
  if (MODES.some((m) => m.id === name)) return name;
  return LEGACY_MAP[name] ?? "hero_typography";
}
