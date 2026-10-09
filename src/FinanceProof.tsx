// FinanceProof — integrated proof: real VO + measured beats + visual engine +
// locked SFX bench + music. 7 beats, 1860 frames @30fps (62s).
//
// ⚠️  FIXTURE MARKER (P4.4 B-11): This file contains SYNTHETIC/ILLUSTRATIVE data
// for visual proof purposes only. It is NOT part of the production chain.
// Production visuals (HousingBroke, MoneyDying) use validated payloads via
// PayloadValidator. Do not copy these values into production.
import React from "react";
import { Sequence, useCurrentFrame } from "remotion";
import { LightCanvas, GlassCard, Kicker } from "./light/primitives";
import { HeroTypography, HeroNumber, ThesisComposition, ClosingComposition } from "./light/editorial";
import { LineChartStory, BarChart } from "./light/charts";
import { TwoSidedComparison, CausalDiagram } from "./light/explain";

// FIXTURE DATA (B-11): Synthetic illustrative values for visual proof.
// NOT production data. Production uses PayloadValidator.
const savings = [7.8, 7.2, 8.1, 6.9, 7.5, 12.4, 11.8, 6.1, 4.9, 3.8, 3.1];
const saveLabels = ["2016", "2018", "2020", "2022", "2024", "2026"];

const Center: React.FC<{ children?: React.ReactNode }> = ({ children }) => (
  <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>{children}</div>
);

const beats: { id: string; from: number; dur: number; el: React.ReactNode }[] = [
  { id: "b1_hook", from: 0, dur: 69, el: (
    <Center><HeroTypography kicker="Astor Legacy" lines={["Your savings account", "is lying to you."]} accentLine={1} /></Center>
  )},
  { id: "b2_number", from: 69, dur: 138, el: (
    <Center><HeroNumber kicker="Personal savings rate" value={3.1} suffix="%" decimals={1} caption="Lowest since 2008" impactAt={108 - 69} /></Center>
  )},
  { id: "b3_trend", from: 207, dur: 351, el: (
    <Center><GlassCard width={1080} padding={44}><Kicker text="Savings rate · 10 years" />
      <div style={{ marginTop: 16 }}><LineChartStory data={savings} labels={saveLabels}
        eventIndex={5} eventLabel="2020 spike" eventSub="Stimulus + lockdown saving" metric="3.1%" impactAt={300 - 207} /></div></GlassCard></Center>
  )},
  { id: "b4_compare", from: 570, dur: 576, el: (
    <Center><TwoSidedComparison
      left={{ title: "Renter", rows: [["Monthly cost", "$2,150"], ["Equity built", "$0"], ["Gap", "$0"]] }}
      right={{ title: "Owner", rows: [["Monthly cost", "$2,980"], ["Equity built", "$41k"], ["Gap", "$830"]] }}
      impactAt={729 - 570} impactRow={0} /></Center>
  )},
  { id: "b5_cause", from: 1161, dur: 288, el: (
    <Center><div><div style={{ textAlign: "center", marginBottom: 10 }}><Kicker text="Why it happened" /></div>
      <CausalDiagram steps={[
        { label: "Fed raised rates", sub: "borrowing costs up" },
        { label: "Spending slowed", sub: "demand cooled" },
        { label: "Cash sat still", sub: "savers waited" },
        { label: "Inflation ate 2.9%", sub: "every year" },
      ]} impactAt={1188 - 1161} impactNode={0} /></div></Center>
  )},
  { id: "b6_bars", from: 1449, dur: 255, el: (
    <Center><GlassCard width={1080} padding={44}><Kicker text="This year's return" />
      <div style={{ marginTop: 16 }}><BarChart data={[
        { label: "Stocks", value: 12 }, { label: "Bonds", value: 3 },
      ]} highlight={0} impactAt={1625 - 1449} impactBar={0} /></div></GlassCard></Center>
  )},
  { id: "b7_thesis", from: 1704, dur: 66, el: (
    <Center><ThesisComposition claim="The saver is becoming the investor." value="12%" delta={12} /></Center>
  )},
  { id: "b7_close", from: 1770, dur: 90, el: (
    <Center><ClosingComposition line1="Wealth is a legacy." line2="Build yours." /></Center>
  )},
];

export const PROOF_TOTAL = 1860;

export const FinanceProof: React.FC = () => (
  <>
    {beats.map((b) => (
      <Sequence key={b.id} from={b.from} durationInFrames={b.dur} name={b.id}>
        <LightCanvas>{b.el}</LightCanvas>
      </Sequence>
    ))}
  </>
);

// Segments for the resumable renderer.
export const PROOF_SEGMENTS = beats.map((b) => ({ id: `proof_${b.id}`, title: b.id, from: b.from, dur: b.dur }));
