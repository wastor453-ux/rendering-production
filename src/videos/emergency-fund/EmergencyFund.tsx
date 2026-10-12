// EmergencyFund.tsx — 3-minute video on building an emergency fund.
// Generated from scratch: own beats, own data, no inherited styles.
// Duration: 180s @ 30fps = 5400 frames.

import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { LightCanvas, GlassCard } from "../../light/primitives";
import { HeroTypography, HeroNumber } from "../../light/editorial";
import { ComparisonBars, LineChartStory } from "../../light/charts";

import beatDoc from "./data/beat_timeline.json";

const FPS = 30;
export const EMERGENCYFUND_TOTAL = 5400;
export const EMERGENCYFUND_FPS = FPS;

interface Beat {
  beat_id: string;
  start_time: number;
  end_time: number;
  visual_mode: string;
  claim: string;
  kicker?: string;
}

function BeatRenderer({ beat }: { beat: Beat }) {
  const lines = beat.claim.split("\n").filter(Boolean);
  switch (beat.visual_mode) {
    case "hero_typography":
      return (<LightCanvas><GlassCard><HeroTypography kicker={beat.kicker ?? "EMERGENCY FUND"} lines={lines.length ? lines : [beat.claim]} /></GlassCard></LightCanvas>);
    case "hero_number":
      return (<LightCanvas><GlassCard><HeroNumber kicker="SHOCKING STAT" value={60} suffix="%" caption="Can't cover a $1000 emergency" /><HeroTypography kicker="" lines={[beat.claim]} /></GlassCard></LightCanvas>);
    case "comparison_bars":
      return (<LightCanvas><GlassCard><ComparisonBars left={{ label: "3 months", value: 50 }} right={{ label: "6 months", value: 100 }} /></GlassCard></LightCanvas>);
    case "line_chart":
      return (<LightCanvas><GlassCard><LineChartStory data={[500, 800, 1100, 1400, 1700, 2000, 2300, 2600, 2900, 3200]} eventIndex={5} eventLabel="Steady growth" metric="Fund balance ($)" /></GlassCard></LightCanvas>);
    default:
      return (<LightCanvas><GlassCard><HeroTypography kicker="" lines={[beat.claim]} /></GlassCard></LightCanvas>);
  }
}

export const EmergencyFund: React.FC = () => {
  const frame = useCurrentFrame();
  const time = frame / FPS;
  const beats = Array.isArray(beatDoc) ? beatDoc : (beatDoc as any).beats;
  const beat = beats.find((b: Beat) => time >= b.start_time && time < b.end_time) ?? beats[0];
  return (<AbsoluteFill><BeatRenderer beat={beat} /></AbsoluteFill>);
};
