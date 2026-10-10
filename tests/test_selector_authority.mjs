// test_selector_authority.mjs — D2 authority resolution tests (log-only stage).
//
// Exercises the REAL modules: src/light/select.ts (selectVisualMode +
// resolveVisualModeAuthority) and src/light/evidence.ts (buildEvidence).
// D2 (approved): plan-authority + mandatory selector challenge + throw on
// disagreement. This stage implements plan-authority + mandatory challenge +
// log-only disputes; the throw is NOT active (separately authorized R-4).
//
// Run: node --test tests/test_selector_authority.mjs

import { test } from "node:test";
import assert from "node:assert/strict";
import {
  selectVisualMode,
  resolveVisualModeAuthority,
} from "../src/light/select.ts";
import { buildEvidence } from "../src/light/evidence.ts";

test("agreement: plan and selector concur → not disputed, plan renders", () => {
  const beat = {
    beat_id: "a1",
    semantic_role: "trend",
    visual_verb: "fall",
    visual_mode: "line_chart",
    intensity: 0.7,
    data_presence: true,
  };
  const ev = buildEvidence(beat, { values: [5.0, 4.0, 3.0] });
  assert.equal(ev.trend_presence, "down");
  const selected = selectVisualMode(ev);
  assert.equal(selected, "line_chart"); // challenge really ran
  const auth = resolveVisualModeAuthority("a1", "line_chart", ev);
  assert.equal(auth.agree, true);
  assert.equal(auth.disputed, false);
  assert.equal(auth.resolved_mode, "line_chart");
  assert.equal(auth.selected_mode, "line_chart");
});

test("disagreement: plan authority holds, dispute is flagged log-only", () => {
  const beat = {
    beat_id: "d1",
    semantic_role: "trend",
    visual_verb: "fall",
    visual_mode: "hero_typography", // plan says typography...
    intensity: 0.7,
    data_presence: true,
  };
  const ev = buildEvidence(beat, { values: [5.0, 4.0, 3.0] });
  const selected = selectVisualMode(ev);
  assert.equal(selected, "line_chart"); // ...selector says line_chart
  const auth = resolveVisualModeAuthority("d1", "hero_typography", ev);
  assert.equal(auth.agree, false);
  assert.equal(auth.disputed, true);
  // D2 plan-authority: the plan's mode is what renders (no silent override).
  assert.equal(auth.resolved_mode, "hero_typography");
  // The selector's answer is preserved on the record, not discarded.
  assert.equal(auth.selected_mode, "line_chart");
  assert.equal(auth.compiled_mode, "hero_typography");
});

test("missing evidence: challenge still runs, falls back safely, never throws", () => {
  const auth = resolveVisualModeAuthority("m1", "hero_number", {});
  assert.equal(auth.selected_mode, "hero_typography"); // documented fallback
  assert.equal(auth.resolved_mode, "hero_number"); // plan still authoritative
  assert.equal(typeof auth.disputed, "boolean");
});

test("null/undefined evidence fields do not crash the challenge", () => {
  const ev = buildEvidence(
    { beat_id: "m2", intensity: 0.5, data_presence: false },
    null
  );
  const auth = resolveVisualModeAuthority("m2", "dashboard", ev);
  assert.equal(auth.resolved_mode, "dashboard");
});

test("mandatory challenge: resolver always consults the live selector", () => {
  // Two different evidences through the same resolver must be able to
  // produce two different selected modes — proving the challenge is the
  // real selectVisualMode, not a stub.
  const evTrend = buildEvidence(
    { beat_id: "c1", semantic_role: "trend", visual_verb: "rise", intensity: 0.8, data_presence: true },
    { values: [1.0, 2.0, 4.0] }
  );
  const evNumber = buildEvidence(
    { beat_id: "c2", semantic_role: "number", visual_verb: "count", intensity: 0.9, data_presence: true, data_type: "statistic" },
    null
  );
  const a1 = resolveVisualModeAuthority("c1", "line_chart", evTrend);
  const a2 = resolveVisualModeAuthority("c2", "hero_number", evNumber);
  assert.equal(a1.selected_mode, "line_chart");
  assert.equal(a2.selected_mode, "hero_number");
  assert.notEqual(a1.selected_mode, a2.selected_mode);
});

test("both compositions route beats through the authority resolver", async () => {
  const { readFileSync } = await import("node:fs");
  const { join } = await import("node:path");
  // Tests run from the repository root (see package.json test script).
  const root = process.cwd();
  for (const f of ["src/ProductionBeats.tsx", "src/P3Rehearsal.tsx"]) {
    const src = readFileSync(join(root, f), "utf8");
    assert.match(
      src,
      /resolveVisualModeAuthority\(b\.beat_id, b\.visual_mode, evidence\)/,
      `${f} must resolve authority per beat`
    );
    assert.match(
      src,
      /REGISTRY\[authority\.resolved_mode\]/,
      `${f} must render the authority-resolved mode`
    );
    // The old discard pattern must be gone.
    assert.doesNotMatch(
      src,
      /const selected = selectVisualMode\(evidence\)/,
      `${f} must not call selectVisualMode directly anymore`
    );
    // Disagreement report must be consumable.
    assert.match(
      src,
      /export function getDisputedDecisions/,
      `${f} must export the dispute report`
    );
  }
});

test("evidence is never derived from the mode under challenge", () => {
  // The authority resolver receives evidence built WITHOUT the candidate
  // mode: changing only visual_mode leaves the evidence identical, so the
  // challenge cannot be circular.
  const payload = { values: [3.0, 2.0, 1.0] };
  const evA = buildEvidence(
    { beat_id: "e1", semantic_role: "trend", visual_mode: "causal_diagram", intensity: 0.7, data_presence: true },
    payload
  );
  const evB = buildEvidence(
    { beat_id: "e1", semantic_role: "trend", visual_mode: "hero_typography", intensity: 0.7, data_presence: true },
    payload
  );
  assert.deepEqual(evA, evB);
  const auth = resolveVisualModeAuthority("e1", "causal_diagram", evA);
  assert.equal(auth.selected_mode, "line_chart");
  assert.equal(auth.disputed, true); // honestly disputed, honestly logged
});

// ---------------------------------------------------------------------------
// Log-only contract cases (D2 plan-authority, throw NOT active).
// ---------------------------------------------------------------------------

test("log-only contract (a): agreement → disputed=false, resolved_mode is the compiled mode", () => {
  const ev = buildEvidence(
    { beat_id: "la1", semantic_role: "trend", visual_verb: "rise", intensity: 0.8, data_presence: true },
    { values: [1.0, 2.0, 4.0] }
  );
  assert.equal(ev.trend_presence, "up"); // measured from data, not invented
  const compiled = "line_chart";
  const auth = resolveVisualModeAuthority("la1", compiled, ev);
  assert.equal(auth.agree, true);
  assert.equal(auth.disputed, false); // log-only: nothing to flag
  assert.equal(auth.resolved_mode, compiled); // plan authority
  assert.equal(auth.resolved_mode, auth.compiled_mode);
});

test("log-only contract (b): disagreement → disputed=true but resolved_mode is still the compiled mode (no throw)", () => {
  const ev = buildEvidence(
    { beat_id: "lb1", semantic_role: "trend", visual_verb: "fall", intensity: 0.7, data_presence: true },
    { values: [5.0, 4.0, 3.0] }
  );
  const compiled = "causal_diagram"; // plan says diagram...
  let auth;
  assert.doesNotThrow(() => {
    // ...selector says line_chart — log-only stage, the throw is not active.
    auth = resolveVisualModeAuthority("lb1", compiled, ev);
  });
  assert.equal(auth.selected_mode, "line_chart");
  assert.equal(auth.agree, false);
  assert.equal(auth.disputed, true); // flagged for the log
  assert.equal(auth.resolved_mode, compiled); // plan authority: the compiled mode still renders
  assert.equal(auth.resolved_mode, auth.compiled_mode);
});

test("log-only contract (c): missing evidence/empty payload → evidence fields are 'none', resolver never crashes", () => {
  const ev = buildEvidence({ beat_id: "lc1" }, null);
  assert.equal(ev.trend_presence, "none"); // fail closed, not invented
  assert.equal(ev.causal_structure, "none");
  const auth = resolveVisualModeAuthority("lc1", "hero_typography", ev);
  assert.equal(typeof auth.resolved_mode, "string");
  assert.equal(auth.resolved_mode, "hero_typography"); // plan still authoritative
  assert.equal(auth.disputed, false); // fallback agrees; nothing to flag
  assert.equal(typeof auth.disputed, "boolean");
});

test("log-only contract (d): REGISTRY[resolved_mode] is what renders (ProductionBeats lookup)", () => {
  // Mirrors ProductionBeats.tsx renderBeat: the renderer is looked up by
  // authority.resolved_mode, and a missing entry throws (no silent fallback).
  const REGISTRY = {
    hero_typography: "HeroTypography",
    line_chart: "LineChart",
    causal_diagram: "CausalDiagram",
  };
  const lookup = (authority) => {
    const render = REGISTRY[authority.resolved_mode];
    if (!render)
      throw new Error(`no renderer for mode '${authority.resolved_mode}' (no silent fallback)`);
    return render;
  };
  // Disputed beat: plan says causal_diagram, selector challenges line_chart.
  const ev = buildEvidence(
    { beat_id: "ld1", semantic_role: "trend", visual_verb: "fall", intensity: 0.7, data_presence: true },
    { values: [5.0, 4.0, 3.0] }
  );
  const authority = resolveVisualModeAuthority("ld1", "causal_diagram", ev);
  assert.equal(authority.disputed, true);
  const render = lookup(authority);
  assert.equal(render, "CausalDiagram"); // the PLAN's renderer renders
  assert.equal(render, REGISTRY[authority.compiled_mode]);
  assert.notEqual(render, REGISTRY[authority.selected_mode]); // selector's pick does NOT render
  // Agreement keeps rendering the agreed mode.
  const ev2 = buildEvidence(
    { beat_id: "ld2", semantic_role: "trend", visual_verb: "rise", intensity: 0.8, data_presence: true },
    { values: [1.0, 2.0, 4.0] }
  );
  const ok = resolveVisualModeAuthority("ld2", "line_chart", ev2);
  assert.equal(lookup(ok), "LineChart");
});
