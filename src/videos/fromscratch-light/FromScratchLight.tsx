// FromScratchLight — Light Premium Fintech composition
// Uses ./light/ components per VISUAL_BRAIN.md v2.0
// Routes each beat's visual_mode to the correct light component.
// NEVER dark. NEVER hardcoded backgrounds. ALWAYS light system.
import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import { LightCanvas, GlassCard, Kicker } from "../../light/primitives";
import { HeroTypography, HeroNumber } from "../../light/editorial";
import { ComparisonBars, LineChartStory } from "../../light/charts";
import { T } from "../../light/tokens";

interface Beat {
  beat_id: string;
  headline: string;
  body: string;
  metric?: { label: string; value: string };
  audio: string;
  start_s: number;
  duration_s: number;
  visual_mode: string;
}

const BEATS: Beat[] = [
  {
    beat_id: "b1",
    headline: "Start From Zero",
    body: "Not hot stocks. Not crypto hype. Something boring that works.",
    audio: "audio/fromscratch_beat1.wav",
    start_s: 0.0,
    duration_s: 14.4,
    visual_mode: "hero_typography",
  },
  {
    beat_id: "b2",
    headline: "4% Safety Net",
    body: "Three months expenses. High-yield savings. Before any investment.",
    metric: { label: "High-yield savings 2026", value: "4%" },
    audio: "audio/fromscratch_beat2.wav",
    start_s: 14.4,
    duration_s: 18.9,
    visual_mode: "hero_number",
  },
  {
    beat_id: "b3",
    headline: "Tax-Free Growth",
    body: "Roth IRA vs taxable. The account matters more than the stock.",
    audio: "audio/fromscratch_beat3.wav",
    start_s: 33.3,
    duration_s: 20.4,
    visual_mode: "comparison_bars",
  },
  {
    beat_id: "b4",
    headline: "One Index Fund",
    body: "VTI. Automatic contributions. Twenty years. Never lost.",
    audio: "audio/fromscratch_beat4.wav",
    start_s: 53.7,
    duration_s: 21.4,
    visual_mode: "line_chart",
  },
  {
    beat_id: "b5",
    headline: "Wealth Is a Legacy",
    body: "Never invest what you need in 5 years. Never panic sell. Never time the market.",
    audio: "audio/fromscratch_beat5.wav",
    start_s: 75.1,
    duration_s: 15.2,
    visual_mode: "hero_typography",
  },
];

const FPS = 30;

// Visual mode router — maps visual_mode to light component
const BeatVisual: React.FC<{ beat: Beat }> = ({ beat }) => {
  switch (beat.visual_mode) {
    case "hero_number":
      return (
        <HeroNumber
          kicker="SAFETY FIRST"
          value={4}
          suffix="%"
          caption={beat.metric?.label ?? beat.headline}
        />
      );
    case "comparison_bars":
      return (
        <div style={{ width: "100%", height: "100%", display: "flex", alignItems: "center", justifyContent: "center", padding: 120 }}>
          <GlassCard style={{ width: "100%", padding: 60 }}>
            <Kicker text={beat.headline} />
            <ComparisonBars
              left={{ label: "Roth IRA", value: 100 }}
              right={{ label: "Taxable", value: 72 }}
            />
            <div style={{ marginTop: 32, fontSize: 28, color: T.inkMuted, fontFamily: T.font, textAlign: "center" }}>
              {beat.body}
            </div>
          </GlassCard>
        </div>
      );
    case "line_chart":
      return (
        <div style={{ width: "100%", height: "100%", display: "flex", alignItems: "center", justifyContent: "center", padding: 120 }}>
          <GlassCard style={{ width: "100%", padding: 60 }}>
            <Kicker text={beat.headline} />
            <LineChartStory
              data={[100, 108, 115, 112, 125, 138, 142, 155, 168, 175, 190, 205, 218, 235, 250, 268, 285, 300, 325, 350]}
              labels={["2006", "2010", "2014", "2018", "2022", "2026"]}
              eventIndex={19}
              eventLabel="20-year growth"
              eventSub={beat.body}
              metric="3.5x"
            />
          </GlassCard>
        </div>
      );
    case "hero_typography":
    default:
      return (
        <HeroTypography
          kicker="INVESTING 2026"
          lines={[beat.headline]}
          accentLine={0}
          align="center"
          supporting={beat.body}
        />
      );
  }
};

export const FromScratchLight: React.FC = () => {
  return (
    <LightCanvas>
      {BEATS.map((beat) => {
        const startFrame = Math.round(beat.start_s * FPS);
        const durationFrames = Math.round(beat.duration_s * FPS);
        return (
          <Sequence
            key={beat.beat_id}
            from={startFrame}
            durationInFrames={durationFrames}
            name={beat.beat_id}
          >
            <AbsoluteFill>
              <BeatVisual beat={beat} />
            </AbsoluteFill>
            <Audio src={staticFile(beat.audio)} />
          </Sequence>
        );
      })}
    </LightCanvas>
  );
};

export const FROMSCRATCH_LIGHT_TOTAL = Math.round(90.3 * FPS);
export const FROMSCRATCH_LIGHT_FPS = FPS;
