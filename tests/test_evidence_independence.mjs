// test_evidence_independence.mjs — R-3 counterexample tests.
//
// These tests import the REAL builder (src/light/evidence.ts — the module
// both ProductionBeats.tsx and P3Rehearsal.tsx now call), not a replica.
// Each case is a counterexample to the old defects:
//   OLD-1: trend_presence was "down" whenever semantic_role === "trend"
//   OLD-2: causal_structure was "chain" whenever visual_mode === "causal_diagram"
//
// Run: node --test tests/test_evidence_independence.mjs
// (Node >= 23.6 strips types natively; no build step.)

import { test } from "node:test";
import assert from "node:assert/strict";
import {
  buildEvidence,
  inferTrendDirection,
  inferCausalStructure,
} from "../src/light/evidence.ts";

// Real payload fixture: savings_trend_10y values (7.8 -> 3.1, measured down).
const SAVINGS_TREND_VALUES = [7.8, 7.2, 8.1, 6.9, 7.5, 12.4, 11.8, 6.1, 4.9, 3.8, 3.1];

test("COUNTEREXAMPLE OLD-1a: trend-labeled beat with RISING data is 'up', not 'down'", () => {
  const beat = { beat_id: "x1", semantic_role: "trend", visual_mode: "line_chart" };
  const payload = { values: [1.0, 2.0, 3.0, 5.0] };
  assert.equal(inferTrendDirection(beat, payload), "up");
});

test("COUNTEREXAMPLE OLD-1b: trend-labeled beat with NO data is 'none', not 'down'", () => {
  const beat = { beat_id: "x2", semantic_role: "trend", visual_mode: "line_chart" };
  assert.equal(inferTrendDirection(beat, null), "none");
  assert.equal(inferTrendDirection(beat, undefined), "none");
  assert.equal(inferTrendDirection(beat, {}), "none");
});

test("COUNTEREXAMPLE OLD-2a: causal_diagram mode with NO causal links is 'none', not 'chain'", () => {
  const beat = { beat_id: "x3", visual_mode: "causal_diagram" };
  assert.equal(inferCausalStructure(beat, null), "none");
});

test("COUNTEREXAMPLE OLD-2b: non-causal mode WITH measured links is 'chain', not 'none'", () => {
  const beat = {
    beat_id: "x4",
    visual_mode: "hero_typography",
    causal_links: [{ from: "a", to: "b" }],
  };
  assert.equal(inferCausalStructure(beat, null), "chain");
});

test("compiler-authored trend_direction wins over measured payload (documented precedence)", () => {
  const beat = { beat_id: "x5", semantic_role: "trend", trend_direction: "down" };
  const rising = { values: [1.0, 9.0] };
  assert.equal(inferTrendDirection(beat, rising), "down");
});

test("flat series (within noise floor) is 'none', not a direction", () => {
  const beat = { beat_id: "x6", semantic_role: "trend" };
  assert.equal(inferTrendDirection(beat, { values: [10.0, 10.1, 9.9, 10.0] }), "none");
  assert.equal(inferTrendDirection(beat, { values: [5, 5, 5, 5] }), "none");
});

test("non-numeric payload values fail closed to 'none'", () => {
  const beat = { beat_id: "x7", semantic_role: "trend" };
  assert.equal(inferTrendDirection(beat, { values: ["a", "b"] }), "none");
  assert.equal(inferTrendDirection(beat, { values: [1] }), "none");
});

test("real fixture: savings_trend_10y measures 'down' (behavior preserved on real data)", () => {
  const beat = { beat_id: "b?", semantic_role: "trend", visual_mode: "line_chart" };
  assert.equal(
    inferTrendDirection(beat, { values: SAVINGS_TREND_VALUES }),
    "down"
  );
});

test("causal_loop flag yields 'loop'; authored structure wins", () => {
  assert.equal(
    inferCausalStructure({ causal_links: [{ a: 1 }], causal_loop: true }, null),
    "loop"
  );
  assert.equal(
    inferCausalStructure({ causal_structure: "flow", visual_mode: "hero_typography" }, null),
    "flow"
  );
});

test("buildEvidence end-to-end: payload threaded through, other fields intact", () => {
  const beat = {
    beat_id: "b9",
    semantic_role: "trend",
    claim: "Savings are collapsing",
    visual_verb: "plunge",
    focal_object: "savings line",
    intensity: 0.9,
    data_presence: true,
    data_type: "series",
    comparison_state: "none",
    visual_mode: "line_chart",
  };
  const ev = buildEvidence(beat, { values: [3.0, 2.0, 1.0] });
  assert.equal(ev.trend_presence, "down");
  assert.equal(ev.causal_structure, "none");
  assert.equal(ev.semantic_role, "trend");
  assert.equal(ev.claim, "Savings are collapsing");
  assert.equal(ev.narrative_intensity, 5); // Math.round(0.9*5)
  assert.equal(ev.information_density, 4); // data_presence true
  assert.equal(ev.number_presence, false); // data_type !== "statistic"
});

test("buildEvidence without payload: trend/causal fail closed, rest intact", () => {
  const beat = {
    beat_id: "b10",
    semantic_role: "trend",
    visual_mode: "causal_diagram",
    intensity: 0.5,
    data_presence: false,
  };
  const ev = buildEvidence(beat);
  // OLD code would have said down/chain here. NEW: no data => none/none.
  assert.equal(ev.trend_presence, "none");
  assert.equal(ev.causal_structure, "none");
});

test("COUNTEREXAMPLE: changing ONLY visual_mode does not change the evidence", () => {
  const base = {
    beat_id: "b11",
    semantic_role: "claim",
    claim: "Costs are rising",
    intensity: 0.7,
    data_presence: true,
  };
  const payload = { values: [5.0, 4.0, 3.0] };
  const evA = buildEvidence({ ...base, visual_mode: "causal_diagram" }, payload);
  const evB = buildEvidence({ ...base, visual_mode: "hero_typography" }, payload);
  const evC = buildEvidence({ ...base, visual_mode: "line_chart" }, payload);
  assert.deepEqual(evA, evB);
  assert.deepEqual(evB, evC);
  // And the measured trend survives regardless of the candidate mode.
  assert.equal(evA.trend_presence, "down");
});

test("COUNTEREXAMPLE: changing ONLY semantic_role does not invent a trend", () => {
  const payload = { values: [1.0, 2.0, 3.0] };
  const evTrend = buildEvidence(
    { beat_id: "b12", semantic_role: "trend", visual_mode: "line_chart" },
    payload
  );
  const evClaim = buildEvidence(
    { beat_id: "b12", semantic_role: "claim", visual_mode: "line_chart" },
    payload
  );
  // Same measured data => same trend evidence, whatever the label says.
  assert.equal(evTrend.trend_presence, "up");
  assert.equal(evClaim.trend_presence, "up");
});

test("ProductionBeats and P3Rehearsal share one evidence implementation", async () => {
  const { readFileSync } = await import("node:fs");
  const { join, dirname } = await import("node:path");
  const { fileURLToPath } = await import("node:url");
  const root = join(dirname(fileURLToPath(import.meta.url)), "..");
  for (const f of ["src/ProductionBeats.tsx", "src/P3Rehearsal.tsx"]) {
    const src = readFileSync(join(root, f), "utf8");
    // Both import the shared builder ...
    assert.match(
      src,
      /import \{ buildEvidence \} from "\.\/light\/evidence"/,
      `${f} must import buildEvidence from ./light/evidence`
    );
    // ... and neither defines its own copy.
    assert.doesNotMatch(
      src,
      /export function buildEvidence/,
      `${f} must not define its own buildEvidence`
    );
    // Both thread the resolved payload into the builder.
    assert.match(
      src,
      /buildEvidence\(b, payload\)/,
      `${f} must pass the resolved payload to buildEvidence`
    );
  }
});
