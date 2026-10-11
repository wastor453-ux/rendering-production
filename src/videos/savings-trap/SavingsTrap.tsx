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
  const frame = useCurrentFrame();
  const localFrame = frame - Math.floor(beat.start_time * FPS);

  switch (beat.visual_mode) {
    case "hero_typography":
      return (
        <LightCanvas>
          <GlassCard>
            {beat.kicker && <Kicker>{beat.kicker}</Kicker>}
            <HeroTypography text={beat.text} frame={localFrame} />
          </GlassCard>
        </LightCanvas>
      );
    case "hero_number":
      return (
        <LightCanvas>
          <GlassCard>
            {beat.kicker && <Kicker>{beat.kicker}</Kicker>}
            <HeroNumber value={beat.number ?? 0} suffix="%" frame={localFrame} />
            <HeroTypography text={beat.text} frame={localFrame} />
          </GlassCard>
        </LightCanvas>
      );
    case "comparison_bars":
      return (
        <LightCanvas>
          <GlassCard>
            {beat.kicker && <Kicker>{beat.kicker}</Kicker>}
            <ComparisonBars
              leftLabel="$10K Today"
              leftValue={100}
              rightLabel="$10K in 10Y"
              rightValue={73}
              frame={localFrame}
            />
          </GlassCard>
        </LightCanvas>
      );
    case "line_chart":
      return (
        <LightCanvas>
          <GlassCard>
            {beat.kicker && <Kicker>{beat.kicker}</Kicker>}
            <LineChartStory
              data={[100, 97, 94, 91, 88, 85, 82, 79, 76, 73]}
              frame={localFrame}
            />
          </GlassCard>
        </LightCanvas>
      );
    default:
      return (
        <LightCanvas>
          <GlassCard>
            <HeroTypography text={beat.text} frame={localFrame} />
          </GlassCard>
        </LightCanvas>
      );
  }
}

export const SavingsTrap: React.FC = () => {
  const frame = useCurrentFrame();
  const time = frame / FPS;

  const beat = (beatDoc as any).beats.find(
    (b: Beat) => time >= b.start_time && time < b.end_time
  ) ?? (beatDoc as any).beats[0];

  return (
    <AbsoluteFill>
      <BeatRenderer beat={beat} />
    </AbsoluteFill>
  );
};
