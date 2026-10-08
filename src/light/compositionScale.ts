// compositionScale.ts — Mode-aware composition scale policy.
//
// Resolution: requested_scale → mode constraints → safe-area fit → effective_scale.
// Fail closed: unknown modes or unsatisfiable constraints return 1.0.
//
// This is a static policy (no rendering). Geometry comes from
// crackit/composition_scale_policy.json (canonical).

export const POLICY_VERSION = "1.0.0";
export const REQUESTED_SCALE = 1.28;
export const SAFE_MARGIN_PX = 96;
export const CANVAS_W = 1920;
export const CANVAS_H = 1080;
export const FAIL_CLOSED_SCALE = 1.0;

export type ScaleStrategy = "uniform" | "split";

export interface ModeScalePolicy {
  strategy: ScaleStrategy;
  max_scale?: number;
  background_scale?: number;
  content_scale?: number;
  content_width?: number;
  content_height?: number;
  constraint_note?: string;
}

export interface ResolvedScale {
  mode: string;
  strategy: ScaleStrategy;
  /** For uniform: the single scale. For split: the content scale. */
  effective_scale: number;
  background_scale?: number;
  requested: number;
  capped_by_max: boolean;
  capped_by_safe_area: boolean;
  fail_closed: boolean;
}

// Mode policies (mirrors composition_scale_policy.json).
// content_width/height are UNSCALED design dimensions.
const MODE_POLICIES: Record<string, ModeScalePolicy> = {
  hero_typography: { strategy: "uniform", max_scale: 1.28, content_width: 1140, content_height: 130 },
  hero_number: { strategy: "uniform", max_scale: 1.28, content_width: 800, content_height: 300 },
  line_chart: { strategy: "uniform", max_scale: 1.28, content_width: 1080, content_height: 420 },
  area_chart: { strategy: "uniform", max_scale: 1.28, content_width: 1080, content_height: 420 },
  bar_chart: { strategy: "uniform", max_scale: 1.28, content_width: 1080, content_height: 450 },
  comparison_bars: { strategy: "uniform", max_scale: 1.28, content_width: 1080, content_height: 320 },
  donut_allocation: { strategy: "uniform", max_scale: 1.28, content_width: 700, content_height: 340 },
  metric_grid: { strategy: "uniform", max_scale: 1.28, content_width: 1200, content_height: 300 },
  dashboard: { strategy: "uniform", max_scale: 1.28, content_width: 1000, content_height: 420 },
  portfolio_card_stack: { strategy: "uniform", max_scale: 1.28, content_width: 1200, content_height: 350 },
  ranked_table: { strategy: "uniform", max_scale: 1.28, content_width: 600, content_height: 420 },
  glass_notification: { strategy: "uniform", max_scale: 1.28, content_width: 400, content_height: 120 },
  feature_icon_system: { strategy: "uniform", max_scale: 1.28, content_width: 800, content_height: 300 },
  before_after: { strategy: "uniform", max_scale: 1.28, content_width: 800, content_height: 300 },
  two_sided_comparison: { strategy: "uniform", max_scale: 1.28, content_width: 1156, content_height: 335 },
  causal_diagram: { strategy: "uniform", max_scale: 1.152, content_width: 1260, content_height: 400,
    constraint_note: "1680px SVG, nodes span 1260px; 1.152 keeps 96px safe margins" },
  causal_loop: { strategy: "uniform", max_scale: 1.28, content_width: 683, content_height: 567 },
  timeline: { strategy: "uniform", max_scale: 1.2, content_width: 1440, content_height: 300,
    constraint_note: "1680px SVG, content spans 1440px; 1.2 keeps 96px safe margins" },
  flow_diagram: { strategy: "uniform", max_scale: 1.28, content_width: 1329, content_height: 200,
    constraint_note: "Measured 1701px at 1.28x; fits at 1.28x" },
  real_world_financial_imagery: { strategy: "split", background_scale: 1.28, content_scale: 1.0,
    constraint_note: "Full-bleed image zooms at 1.28x; edge-anchored text stays at 1.0x" },
  imagery_plus_glass_overlay: { strategy: "uniform", max_scale: 1.28, content_width: 720, content_height: 400,
    constraint_note: "Centered card; background zoom acceptable" },
  thesis_composition: { strategy: "uniform", max_scale: 1.28, content_width: 900, content_height: 400 },
  closing_composition: { strategy: "uniform", max_scale: 1.28, content_width: 600, content_height: 250 },
};

export const POLICY_MODE_IDS = Object.keys(MODE_POLICIES);

/**
 * Resolve the effective scale for a mode.
 * Order: requested_scale → mode max_scale → safe-area fit → effective.
 * Fail closed: unknown mode or unsatisfiable constraint → 1.0.
 */
export function resolveScale(mode: string, requested: number = REQUESTED_SCALE): ResolvedScale {
  const policy = MODE_POLICIES[mode];
  if (!policy) {
    return { mode, strategy: "uniform", effective_scale: FAIL_CLOSED_SCALE,
      requested, capped_by_max: false, capped_by_safe_area: false, fail_closed: true };
  }

  if (policy.strategy === "split") {
    return { mode, strategy: "split",
      effective_scale: policy.content_scale ?? FAIL_CLOSED_SCALE,
      background_scale: policy.background_scale ?? FAIL_CLOSED_SCALE,
      requested, capped_by_max: true, capped_by_safe_area: false, fail_closed: false };
  }

  const maxScale = policy.max_scale ?? REQUESTED_SCALE;
  const capped = Math.min(requested, maxScale);
  const capped_by_max = capped < requested;

  let effective = capped;
  let capped_by_safe_area = false;
  if (policy.content_width && policy.content_height) {
    const fitW = (CANVAS_W - 2 * SAFE_MARGIN_PX) / policy.content_width;
    const fitH = (CANVAS_H - 2 * SAFE_MARGIN_PX) / policy.content_height;
    const fit = Math.min(fitW, fitH);
    if (fit < effective) {
      effective = fit;
      capped_by_safe_area = true;
    }
  }

  // Fail closed: never go below 1.0 (don't shrink the design).
  if (effective < FAIL_CLOSED_SCALE) {
    return { mode, strategy: "uniform", effective_scale: FAIL_CLOSED_SCALE,
      requested, capped_by_max, capped_by_safe_area: true, fail_closed: true };
  }

  return { mode, strategy: "uniform", effective_scale: effective,
    requested, capped_by_max, capped_by_safe_area, fail_closed: false };
}

/** Verify a resolved scale keeps content within safe areas. Returns violation or null. */
export function checkSafeArea(mode: string, scale: number): string | null {
  const policy = MODE_POLICIES[mode];
  if (!policy || policy.strategy === "split" || !policy.content_width || !policy.content_height) return null;
  const sw = policy.content_width * scale;
  const sh = policy.content_height * scale;
  const marginX = (CANVAS_W - sw) / 2;
  const marginY = (CANVAS_H - sh) / 2;
  if (marginX < SAFE_MARGIN_PX) return `${mode}: horizontal margin ${marginX.toFixed(0)}px < ${SAFE_MARGIN_PX}px at scale ${scale}`;
  if (marginY < SAFE_MARGIN_PX) return `${mode}: vertical margin ${marginY.toFixed(0)}px < ${SAFE_MARGIN_PX}px at scale ${scale}`;
  return null;
}
