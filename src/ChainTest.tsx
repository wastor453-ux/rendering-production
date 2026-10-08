// ChainTest.tsx — TEST ONLY: independent compiler-chain validation.
// Uses ONLY compiled output (never hand-authored beat_timeline):
//   tests/chain/beat_timeline.json  <- compile_beats.py (fresh words + fresh plan)
//   tests/chain/events.json          <- compile_events.py
//   tests/chain/beat_timeline_arbitration.json <- arbitrate.ts
// Renders through the SAME ProductionBeats registry + milestone machinery.

import React from "react";
import { Sequence } from "remotion";
import { LightCanvas } from "./light/primitives";
import { REGISTRY, BeatCtx, resolvePayload, buildEvidence } from "./ProductionBeats";
import { toLocalMilestone } from "./light/milestone";
import { selectVisualMode } from "./light/select";

import beatDoc from "./chaintest/beat_timeline.json";
import eventsDoc from "./chaintest/events.json";
import arbDoc from "./chaintest/beat_timeline_arbitration.json";
import hiddenFees from "./chaintest/payloads/hidden_fees_348.json";

const FPS = 30;

// test-local payloads (fail-closed like production)
const PAYLOADS: Record<string, any> = {
  "payloads/hidden_fees_348.json": hiddenFees,
};
function resolveTestPayload(ref: string) {
  const p = PAYLOADS[ref];
  if (!p) throw new Error(`ChainTest: unknown payload ref '${ref}'`);
  return p;
}

const arbByBeat: Record<string, any> = {};
for (const r of (arbDoc as any).records) arbByBeat[r.beat_id] = r;

const eventsByBeat: Record<string, any[]> = {};
for (const e of (eventsDoc as any).events) (eventsByBeat[e.beat_id] ||= []).push(e);

function renderBeat(b: any) {
  const from = Math.floor(b.start_time * FPS);
  const dur = Math.ceil(b.end_time * FPS) - from;
  const arb = arbByBeat[b.beat_id];
  if (!arb) throw new Error(`ChainTest: no arbitration record for ${b.beat_id}`);
  const mode = arb.resolved_mode; // arbitration decides, never hand-typed
  const render = REGISTRY[mode];
  if (!render) throw new Error(`ChainTest: no renderer for resolved mode '${mode}'`);
  const evs = eventsByBeat[b.beat_id] ?? [];
  const milestone = evs[0] ? toLocalMilestone(evs[0], from) : null;
  const payload = b.data_presence ? resolveTestPayload(b.data_payload_ref) : null;
  const el = render({ beat: b, event: evs[0] ?? null, milestone, payload, pres: b.presentation ?? {} } as BeatCtx);
  return (
    <Sequence key={b.beat_id} from={from} durationInFrames={dur} name={b.beat_id}>
      <LightCanvas>{el}</LightCanvas>
    </Sequence>
  );
}

const beats = (beatDoc as any).beats as any[];
export const ChainTest: React.FC = () => <>{beats.map(renderBeat)}</>;
export const CHAINTEST_TOTAL = Math.ceil(Math.max(...beats.map((b: any) => b.end_time)) * FPS);
