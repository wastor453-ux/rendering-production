// CompoundInterest.tsx — 3-minute video on the power of compound interest.
// Generated from scratch: own beats, own data, no inherited styles.
// Duration: 180s @ 30fps = 5400 frames.

import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { LightCanvas, GlassCard, Kicker } from "../../light/primitives";
import { HeroTypography, HeroNumber } from "../../light/editorial";
import { ComparisonBars, LineChartStory } from "../../light/charts";

import beatDoc from "./data/beat_timeline.json";

const FPS = 30;
export const COMPOUNDINTEREST_TOTAL = 5400;
export const COMPOUNDINTEREST_FPS = FPS;

interface Beat {
  beat_id: string;
  start_time: number;
  end_time: number;
  visual_mode: string;
  claim: string;
  kicker?: string;
  focal_object?: string;
}

function BeatRenderer({ beat }: { beat: Beat }) {
  const lines = beat.claim.split("\n").filter(Boolean);

  switch (beat.visual_mode) {
    case "hero_typography":
      return (
        <LightCanvas>
          <GlassCard>
            <HeroTypography kicker={beat.kicker ?? "COMPOUND INTEREST"} lines={lines.length ? lines : [beat.claim]} />
          </GlassCard>
        </LightCanvas>
      );
    case "hero_number":
      return (
        <LightCanvas>
          <GlassCard>
            <HeroNumber kicker={beat.kicker ?? "RESULT"} value={1000000} prefix="$" caption="From just $200/month over 40 years" />
            <HeroTypography kicker={beat.kicker ?? ""} lines={lines.length ? lines : [beat.claim]} />
          </GlassCard>
        </LightCanvas>
      );
    case "comparison_bars":
      return (
        <LightCanvas>
          <GlassCard>
            <ComparisonBars
              left={{ label: "Start at 25", value: 100 }}
              right={{ label: "Start at 35", value: 50 }}
            />
          </GlassCard>
        </LightCanvas>
      );
    case "line_chart":
      return (
        <LightCanvas>
          <GlassCard>
            <LineChartStory data={[10, 15, 22, 32, 46, 66, 95, 137, 197, 284]} eventIndex={5} eventLabel="Growth accelerates" metric="Portfolio value ($K)" />
          </GlassCard>
        </LightCanvas>
      );
    default:
      return (
        <LightCanvas>
          <GlassCard>
            <HeroTypography kicker={beat.kicker ?? ""} lines={[beat.claim]} />
          </GlassCard>
        </LightCanvas>
      );
  }
}

export const CompoundInterest: React.FC = () => {
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
