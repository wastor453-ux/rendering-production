// SavingsTrap.tsx — 3-minute full pipeline test video.
// Topic: Why savings accounts lose value to inflation.
// Generated from scratch: own beats, own data, no inherited styles.
// Duration: 180s @ 30fps = 5400 frames.

import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { LightCanvas, GlassCard, Kicker } from "../../light/primitives";
import { HeroTypography, HeroNumber } from "../../light/editorial";
import { ComparisonBars, LineChartStory } from "../../light/charts";

import beatDoc from "./data/beat_timeline.json";

const FPS = 30;
export const SAVINGSTRAP_TOTAL = 5400;
export const SAVINGSTRAP_FPS = FPS;

interface Beat {
  beat_id: string;
  start_time: number;
  end_time: number;
  visual_mode: string;
  text: string;
  kicker?: string;
  number?: number;
}

function BeatRenderer({ beat }: { beat: Beat }) {
  // Components use useCurrentFrame() internally - no frame prop needed.
  // HeroTypography needs lines: string[] (not text: string)
  // ComparisonBars needs left/right as nested objects (not flat props)
  const lines = beat.text.split("\n").filter(Boolean);

  switch (beat.visual_mode) {
    case "hero_typography":
      return (
        <LightCanvas>
          <GlassCard>
            <HeroTypography kicker={beat.kicker ?? ""} lines={lines.length ? lines : [beat.text]} />
          </GlassCard>
        </LightCanvas>
      );
    case "hero_number":
      return (
        <LightCanvas>
          <GlassCard>
            <HeroNumber kicker={beat.kicker ?? "INFLATION"} value={beat.number ?? 0} suffix="%" caption="Average annual inflation eroding savings" />
            <HeroTypography kicker={beat.kicker ?? ""} lines={lines.length ? lines : [beat.text]} />
          </GlassCard>
        </LightCanvas>
      );
    case "comparison_bars":
      return (
        <LightCanvas>
          <GlassCard>
            <ComparisonBars
              left={{ label: "$10K Today", value: 100 }}
              right={{ label: "$10K in 10Y", value: 73 }}
            />
          </GlassCard>
        </LightCanvas>
      );
    case "line_chart":
      return (
        <LightCanvas>
          <GlassCard>
            <LineChartStory data={[100, 97, 94, 91, 88, 85, 82, 79, 76, 73]} eventIndex={5} eventLabel="Purchasing power drops 27%" metric="Value of $10K" />
          </GlassCard>
        </LightCanvas>
      );
    default:
      return (
        <LightCanvas>
          <GlassCard>
            <HeroTypography kicker={beat.kicker ?? ""} lines={[beat.text]} />
          </GlassCard>
        </LightCanvas>
      );
  }
}

export const SavingsTrap: React.FC = () => {
  const frame = useCurrentFrame();
  const time = frame / FPS;

  const beats = Array.isArray(beatDoc) ? beatDoc : (beatDoc as any).beats;
  const beat = beats.find(
    (b: Beat) => time >= b.start_time && time < b.end_time
  ) ?? beats[0];

  return (
    <AbsoluteFill>
      <BeatRenderer beat={beat} />
    </AbsoluteFill>
  );
};
