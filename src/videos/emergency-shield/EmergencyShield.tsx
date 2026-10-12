// EmergencyShield.tsx — TRUE ROOT FIX: visual_mode routing, no hardcoded scenes
// Video: "Emergency Fund: Your Financial Safety Net"
// Beats GENERATED from VO measurements via tools/generate_beats_from_vo.py
import React from "react";
import { AbsoluteFill, Audio, useCurrentFrame, interpolate } from "remotion";
import voAudio from "./audio/vo.wav";
import beatData from "./data/beat_timeline.json";
import { T, CLAMP } from "../../light/tokens";
import { LightCanvas, GlassCard } from "../../light/primitives";
import { DonutChart } from "../../light/charts";
import {
  CalculatorCard,
  TakeawayChecklist,
  ActionChecklist,
  SectionTitle,
} from "../../light/components_v2";

const FPS = 30;

interface Beat {
  beat_id: string;
  start_time: number;
  end_time: number;
  visual_mode: string;
  visual_verb: string;
  claim: string;
}

const BEATS = beatData as Beat[];

const renderByVisualMode = (visual_mode: string, local: number, beat: Beat): React.ReactNode => {
  switch (visual_mode) {
    case "hero_typography":
      return (
        <LightCanvas variant="coolBlue">
          <div style={{
            position: "absolute", inset: 0, display: "flex",
            flexDirection: "column", alignItems: "center", justifyContent: "center",
            padding: "0 100px",
          }}>
            <div style={{
              fontFamily: T.font, fontSize: 68, fontWeight: 800,
              color: T.ink, textAlign: "center", lineHeight: 1.2,
              opacity: interpolate(local, [0, 15], [0, 1], CLAMP),
            }}>
              What happens when your<br />
              <span style={{ color: T.primary }}>car breaks down tomorrow?</span>
            </div>
            <div style={{
              fontFamily: T.font, fontSize: 26, color: T.inkMuted, marginTop: 40,
              textAlign: "center", opacity: interpolate(local, [60, 90], [0, 1], CLAMP),
            }}>
              One surprise can destroy years of progress.<br />A safety net changes everything.
            </div>
          </div>
        </LightCanvas>
      );

    case "donut_chart":
      return (
        <LightCanvas variant="lavenderHorizon">
          <div style={{
            position: "absolute", inset: 0, display: "flex",
            alignItems: "center", justifyContent: "center", padding: "0 80px",
          }}>
            <div style={{
              opacity: interpolate(local, [0, 20], [0, 1], CLAMP),
              transform: `scale(${interpolate(local, [0, 20], [0.9, 1], CLAMP)})`,
            }}>
              <DonutChart
                segments={[
                  { label: "Mini Fund", value: 1000, color: T.teal },
                  { label: "3 Months", value: 7500, color: T.primary },
                  { label: "6 Months", value: 15000, color: T.cyan },
                ]}
                title="Emergency Fund Targets"
                subtitle="Start with $1,000, build to 3-6 months of expenses."
                centerLabel="Your Safety Net"
                centerValue="$1K → $15K"
              />
            </div>
          </div>
        </LightCanvas>
      );

    case "calculator":
      return (
        <LightCanvas variant="glassAurora">
          <div style={{
            position: "absolute", inset: 0, display: "flex",
            alignItems: "center", justifyContent: "center",
            opacity: interpolate(local, [0, 20], [0, 1], CLAMP),
          }}>
            <CalculatorCard
              title="Build Your Fund"
              inputs={[
                { label: "Monthly Expenses", value: "$2,500" },
                { label: "3-Month Target", value: "$7,500" },
                { label: "Monthly Savings", value: "$500" },
              ]}
              results={[
                { label: "Time to Goal", value: "15 months", highlight: true },
                { label: "At $300/mo", value: "25 months" },
              ]}
            />
          </div>
        </LightCanvas>
      );

    case "takeaway_checklist":
      return (
        <LightCanvas variant="softOrb">
          <div style={{
            position: "absolute", inset: 0, display: "flex", flexDirection: "column",
            alignItems: "center", justifyContent: "center", gap: 32,
          }}>
            <SectionTitle
              title="Where to Keep It"
              subtitle="Liquid, safe, and separate"
            />
            <div style={{ opacity: interpolate(local, [30, 60], [0, 1], CLAMP) }}>
              <TakeawayChecklist items={[
                "High-yield savings: 4-5% APY, FDIC insured",
                "NOT stocks — market drops when you need cash",
                "Separate from checking — avoid temptation",
                "Automate every payday — even $50 builds momentum",
              ]} />
            </div>
          </div>
        </LightCanvas>
      );

    case "action_checklist":
      return (
        <LightCanvas variant="calmExecutive">
          <div style={{
            position: "absolute", inset: 0, display: "flex",
            alignItems: "center", justifyContent: "center",
            opacity: interpolate(local, [0, 20], [0, 1], CLAMP),
          }}>
            <ActionChecklist
              title="Start Today: 3 Steps"
              steps={[
                {
                  icon: "🏦",
                  title: "Open high-yield savings",
                  description: "Takes 10 minutes online",
                },
                {
                  icon: "🤖",
                  title: "Automate payday transfer",
                  description: "Pay yourself first, every time",
                },
                {
                  icon: "🎯",
                  title: "Hit $1,000 mini-goal",
                  description: "Celebrate, then keep building",
                },
              ]}
            />
          </div>
        </LightCanvas>
      );

    default:
      return (
        <LightCanvas variant="coolBlue">
          <div style={{
            position: "absolute", inset: 0, display: "flex",
            alignItems: "center", justifyContent: "center",
          }}>
            <div style={{ fontFamily: T.font, fontSize: 32, color: T.inkMuted }}>
              Unknown visual_mode: {visual_mode}
            </div>
          </div>
        </LightCanvas>
      );
  }
};

export const EmergencyShield: React.FC = () => {
  const frame = useCurrentFrame();
  const timeSec = frame / FPS;

  const beat = BEATS.find(b => timeSec >= b.start_time && timeSec < b.end_time) || BEATS[BEATS.length - 1];
  const local = frame - Math.round(beat.start_time * FPS);
  const visual_mode = beat.visual_mode;

  return (
    <AbsoluteFill>
      <Audio src={voAudio} />
      {renderByVisualMode(visual_mode, local, beat)}
    </AbsoluteFill>
  );
};
