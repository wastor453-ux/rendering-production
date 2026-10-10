// evidence.ts — R-3 EVIDENCE INDEPENDENCE (2026-10-10)
//
// Builds the SemanticEvidence the visual-mode selector challenges the plan with.
// HARD LAW: evidence must be measured from data, never derived from the answer
// being evaluated.
//
// The defects this replaces:
//   - trend_presence was hardcoded "down" whenever semantic_role === "trend"
//     (trend direction invented from a label, not measured from data).
//   - causal_structure was "chain" whenever visual_mode === "causal_diagram"
//     (evidence derived from the mode under challenge — circular).
//
// Rules:
//   1. trend_presence comes from (a) an explicit compiler-authored
//      `trend_direction` on the beat, else (b) a measured numeric series on the
//      resolved payload (`payload.values`), else "none". NEVER from
//      semantic_role or visual_mode.
//   2. causal_structure comes from (a) an explicit compiler-authored
//      `causal_structure` on the beat, else (b) a non-empty `causal_links`
//      list on the beat or payload, else "none". NEVER from visual_mode.
//   3. Unknown / unmeasurable => "none" (fail closed). "none" lets the
//      selector fall through to its other rules instead of forcing a mode
//      on invented evidence.
//
// This module is intentionally free of JSX and of non-erasable TypeScript
// syntax so the real builder (not a replica) can be executed directly by
// Node's type stripping in tests/test_evidence_independence.mjs.

import type { SemanticEvidence } from "./select";

export type TrendPresence = "up" | "down" | "none";
export type CausalPresence = "chain" | "loop" | "flow" | "none";

/** Noise floor: a series whose end-to-end move is <5% of its range is "flat". */
const FLAT_THRESHOLD = 0.05;

/**
 * Measure trend direction. `beat.trend_direction` (compiler-authored from
 * data at compile time) wins when present; otherwise measure first-vs-last
 * on a numeric `payload.values` series; otherwise "none".
 */
export function inferTrendDirection(beat: any, payload?: any): TrendPresence {
  const authored = (beat?.trend_direction ?? "").toLowerCase();
  if (authored === "up" || authored === "down") return authored;

  const values = payload?.values;
  if (
    Array.isArray(values) &&
    values.length >= 2 &&
    values.every((v: unknown) => typeof v === "number" && Number.isFinite(v))
  ) {
    const first = values[0] as number;
    const last = values[values.length - 1] as number;
    const span = Math.max(...(values as number[])) - Math.min(...(values as number[]));
    if (span === 0) return "none";
    const delta = last - first;
    if (Math.abs(delta) < FLAT_THRESHOLD * span) return "none";
    return delta > 0 ? "up" : "down";
  }
  return "none";
}

/**
 * Measure causal structure. `beat.causal_structure` (compiler-authored)
 * wins when present; otherwise a non-empty `causal_links` list on the beat
 * or payload means "chain" (or "loop" when explicitly marked); else "none".
 */
export function inferCausalStructure(beat: any, payload?: any): CausalPresence {
  const authored = (beat?.causal_structure ?? "").toLowerCase();
  if (authored === "chain" || authored === "loop" || authored === "flow") return authored;

  const links = beat?.causal_links ?? payload?.causal_links;
  if (Array.isArray(links) && links.length > 0) {
    if (beat?.causal_loop === true || payload?.causal_loop === true) return "loop";
    return "chain";
  }
  return "none";
}

/**
 * Build selector evidence for one compiled beat. Pass the resolved payload
 * (or null) so trend/causal fields are measured from data.
 */
export function buildEvidence(b: any, payload?: any): SemanticEvidence {
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
    trend_presence: inferTrendDirection(b, payload),
    causal_structure: inferCausalStructure(b, payload),
  };
}
