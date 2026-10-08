// B6Arbitration.tsx — TEST ONLY (not production).
// b6 arbitration: identical narration timing, data, and milestone.
//   A = bar_chart (plan's preferred mode)
//   B = two_sided_comparison (selector's output)
// Renders the same beat (48.3-56.5s) both ways for visual arbitration.

import React from "react";
import { Sequence } from "remotion";
import { LightCanvas, GlassCard, Kicker } from "./light/primitives";
import { BarChart } from "./light/charts";
import { TwoSidedComparison } from "./light/explain";
import { toLocalMilestone, legacyImpactProps } from "./light/milestone";

import beatDoc from "./compiled/beat_timeline.json";
import eventsDoc from "./compiled/events.json";
import stocksVsBonds from "./compiled/payloads/stocks_vs_bonds.json";

const FPS = 30;
const beat = (beatDoc as any).beats.find((b: any) => b.beat_id === "b6");
const ev = (eventsDoc as any).events.find((e: any) => e.event_id === "b6_e1");
const FROM = Math.floor(beat.start_time * FPS); // 1449
const DUR = Math.ceil(beat.end_time * FPS) - FROM;
const ms = toLocalMilestone(ev, FROM);
const pres = beat.presentation;

const payload = stocksVsBonds as any;
const stocks = payload.values.find((v: any) => v.label === "Stocks").value; // 12
const bonds = payload.values.find((v: any) => v.label === "Bonds").value;    // 3
const infl = payload.baseline; // 2.9 — real returns derived, not invented

const Center: React.FC<{ children?: React.ReactNode }> = ({ children }) => (
  <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>{children}</div>
);

// A — bar_chart (plan preference)
export const B6A: React.FC = () => (
  <Sequence from={FROM} durationInFrames={DUR} name="b6A_bar">
    <LightCanvas><Center>
      <GlassCard width={1080} padding={44}><Kicker text={pres.kicker} />
        <div style={{ marginTop: 16 }}><BarChart
          data={payload.values.map((d: any) => ({ label: d.label, value: d.value }))}
          highlight={pres.highlight ?? 0}
          {...legacyImpactProps(ms, { bar: pres.impactBar ?? 0 })} /></div>
      </GlassCard>
    </Center></LightCanvas>
  </Sequence>
);

// B — two_sided_comparison (selector output), same data + same milestone
export const B6B: React.FC = () => (
  <Sequence from={FROM} durationInFrames={DUR} name="b6B_twosided">
    <LightCanvas><Center>
      <TwoSidedComparison
        left={{ title: "Stocks", rows: [["Annual return", `${stocks}%`], ["Real return", `${(stocks - infl).toFixed(1)}%`]] }}
        right={{ title: "Bonds", rows: [["Annual return", `${bonds}%`], ["Real return", `${(bonds - infl).toFixed(1)}%`]] }}
        {...legacyImpactProps(ms, { row: 0 })} />
    </Center></LightCanvas>
  </Sequence>
);

export const B6A_TOTAL = FROM + DUR;
export const B6B_TOTAL = FROM + DUR;
