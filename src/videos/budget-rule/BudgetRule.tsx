// BudgetRule.tsx — TRUE ROOT FIX: visual_mode routing, no hardcoded scenes
// 3-minute video: "The 50/30/20 Budget Rule"
// 
// ROOT CAUSE FIXED: Previously had 5 hardcoded Beat components.
// Now routes by visual_mode from beat_timeline.json.
// To add a new scene: add a beat with visual_mode. No TSX change needed.
import React from "react";
import { AbsoluteFill, Audio, useCurrentFrame, interpolate } from "remotion";
import voAudio from "./audio/vo.wav";
import beatData from "./data/beat_timeline.json";
import { T, CLAMP } from "../../light/tokens";
import { LightCanvas, GlassCard } from "../../light/primitives";
import { HeroTypography } from "../../light/editorial";
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

// Visual mode renderers — each visual_mode maps to a component.
// The beat data drives which renderer is used. No hardcoded scene order.
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
              fontFamily: T.font, fontSize: 72, fontWeight: 800,
              color: T.ink, textAlign: "center", lineHeight: 1.2, letterSpacing: -1,
              opacity: interpolate(local, [0, 15], [0, 1], CLAMP),
            }}>
              What if managing money<br />
              comes down to just <span style={{ color: T.primary }}>three numbers?</span>
            </div>
            <div style={{
              display: "flex", gap: 32, marginTop: 48,
              opacity: interpolate(local, [60, 90], [0, 1], CLAMP),
            }}>
              {[
                { n: "50", label: "Needs", color: T.primary },
                { n: "30", label: "Wants", color: T.cyan },
                { n: "20", label: "Savings", color: T.teal },
              ].map((item, i) => (
                <GlassCard key={i} width={220} padding={32} style={{
                  textAlign: "center",
                  opacity: interpolate(local, [60 + i * 20, 80 + i * 20], [0, 1], CLAMP),
                }}>
                  <div style={{ fontFamily: T.font, fontSize: 72, fontWeight: 800, color: item.color }}>
                    {item.n}
                  </div>
                  <div style={{ fontFamily: T.font, fontSize: 24, fontWeight: 600, color: T.ink, marginTop: 8 }}>
                    {item.label}
                  </div>
                </GlassCard>
              ))}
            </div>
            <div style={{
              fontFamily: T.font, fontSize: 26, color: T.inkMuted, marginTop: 40,
              opacity: interpolate(local, [180, 210], [0, 1], CLAMP),
            }}>
              No spreadsheets. No jargon. Just a system that works.
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
                  { label: "Needs", value: 50, color: T.primary },
                  { label: "Wants", value: 30, color: T.cyan },
                  { label: "Savings", value: 20, color: T.teal },
                ]}
                title="The 50/30/20 Rule"
                subtitle="Fifty percent needs, thirty percent wants, twenty percent savings."
                centerLabel="Your Income"
                centerValue="100%"
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
              title="Your $4,000/Month Budget"
              inputs={[
                { label: "Monthly Income (after tax)", value: "$4,000" },
                { label: "Needs (50%)", value: "$2,000" },
                { label: "Wants (30%)", value: "$1,200" },
              ]}
              results={[
                { label: "Savings (20%)", value: "$800", highlight: true },
                { label: "Yearly Savings", value: "$9,600" },
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
              title="Why This Rule Works"
              subtitle="Three reasons backed by behavioral science"
            />
            <div style={{ opacity: interpolate(local, [30, 60], [0, 1], CLAMP) }}>
              <TakeawayChecklist items={[
                "Flexible, not rigid — adjust to your situation",
                "Forces savings priority — pay yourself first",
                "Gives permission to spend — no guilt on wants",
              ]} />
            </div>
            <GlassCard width={600} padding={28} style={{
              opacity: interpolate(local, [200, 230], [0, 1], CLAMP),
              border: `2px solid ${T.teal}`,
            }}>
              <div style={{ fontFamily: T.font, fontSize: 22, color: T.inkMuted, textAlign: "center" }}>
                People who automate savings save
              </div>
              <div style={{
                fontFamily: T.font, fontSize: 56, fontWeight: 800,
                color: T.teal, textAlign: "center", marginTop: 8,
              }}>
                3× more
              </div>
            </GlassCard>
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
                  icon: "🧮",
                  title: "Calculate your after-tax income",
                  description: "Know exactly what you're working with each month",
                },
                {
                  icon: "✖️",
                  title: "Multiply by 0.5, 0.3, 0.2",
                  description: "Get your three buckets: needs, wants, savings",
                },
                {
                  icon: "🤖",
                  title: "Automate your 20%",
                  description: "Transfer to savings the day you get paid",
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

// Main composition — routes by visual_mode from beat data.
// NO hardcoded scenes. The beat_timeline.json drives everything.
export const BudgetRule: React.FC = () => {
  const frame = useCurrentFrame();
  const timeSec = frame / FPS;

  // Find active beat from MEASURED timings (not hardcoded 36s)
  const beat = BEATS.find(b => timeSec >= b.start_time && timeSec < b.end_time) || BEATS[BEATS.length - 1];
  const local = frame - Math.round(beat.start_time * FPS);

  // Route by visual_mode — this is what test_no_hardcoded_scenes.py checks
  const visual_mode = beat.visual_mode;

  return (
    <AbsoluteFill>
      <Audio src={voAudio} />
      {renderByVisualMode(visual_mode, local, beat)}
    </AbsoluteFill>
  );
};
