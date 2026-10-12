// CreditScore.tsx — TRUE ROOT FIX: visual_mode routing, no hardcoded scenes
// Video: "How Credit Scores Work"
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
              Your credit score controls<br />
              <span style={{ color: T.primary }}>your financial life.</span>
            </div>
            <div style={{
              fontFamily: T.font, fontSize: 26, color: T.inkMuted, marginTop: 40,
              textAlign: "center", opacity: interpolate(local, [60, 90], [0, 1], CLAMP),
            }}>
              Yet most people have no idea how it's calculated.
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
                  { label: "Payment History", value: 35, color: T.primary },
                  { label: "Amounts Owed", value: 30, color: T.cyan },
                  { label: "Length", value: 15, color: T.teal },
                  { label: "New Credit", value: 10, color: T.lavender },
                  { label: "Mix", value: 10, color: T.inkMuted },
                ]}
                title="What Makes Your Score"
                subtitle="Five factors, weighted by importance."
                centerLabel="FICO Score"
                centerValue="300-850"
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
              title="Sarah's Score Journey"
              inputs={[
                { label: "Starting Score", value: "720" },
                { label: "Missed Payment", value: "-40 pts" },
                { label: "Maxed Card", value: "-30 pts" },
              ]}
              results={[
                { label: "Low Point", value: "650", highlight: true },
                { label: "After Recovery", value: "710" },
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
              title="5 Ways to Boost Your Score"
              subtitle="Proven strategies that work"
            />
            <div style={{ opacity: interpolate(local, [30, 60], [0, 1], CLAMP) }}>
              <TakeawayChecklist items={[
                "Autopay minimums — never miss a due date",
                "Pay down to under 30%, then under 10%",
                "Keep old cards open — age helps",
                "Limit hard inquiries to 1-2 per year",
                "Dispute errors — 1 in 5 reports has one",
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
                  icon: "📋",
                  title: "Pull free credit reports",
                  description: "Check for errors at AnnualCreditReport.com",
                },
                {
                  icon: "🤖",
                  title: "Set up autopay now",
                  description: "On every account, today",
                },
                {
                  icon: "💳",
                  title: "Pay down highest card",
                  description: "Extra payment this week",
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

export const CreditScore: React.FC = () => {
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
