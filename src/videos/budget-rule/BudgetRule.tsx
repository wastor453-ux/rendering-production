// BudgetRule.tsx — Full production test with Visual System v2.0
// 3-minute video: "The 50/30/20 Budget Rule"
// Uses: v2.0 components, timing rules (9+ changes per beat), 5-layer backgrounds
import React from "react";
import { AbsoluteFill, Audio, useCurrentFrame, interpolate } from "remotion";
import voAudio from "./audio/vo.wav";
import { T, CLAMP } from "../../light/tokens";
import { LightCanvas, GlassCard } from "../../light/primitives";
import {
  HeroTypography,
} from "../../light/editorial";
import {
  DonutChart,
} from "../../light/charts";
import {
  CalculatorCard,
  TakeawayChecklist,
  ActionChecklist,
  SectionTitle,
  AnnotationCallout,
} from "../../light/components_v2";

const FPS = 30;

// Beat 1: Hook (0-36s) — HeroTypography with 50/30/20 emphasis
const BeatHook: React.FC<{ local: number }> = ({ local }) => {
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
        {/* Visual change 2: Numbers appear */}
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
        {/* Visual change 3: Subtext */}
        <div style={{
          fontFamily: T.font, fontSize: 26, color: T.inkMuted, marginTop: 40,
          opacity: interpolate(local, [180, 210], [0, 1], CLAMP),
        }}>
          No spreadsheets. No jargon. Just a system that works.
        </div>
      </div>
    </LightCanvas>
  );
};

// Beat 2: The Rule (36-72s) — DonutChart with 50/30/20
const BeatRule: React.FC<{ local: number }> = ({ local }) => {
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
};

// Beat 3: Real Example (72-108s) — CalculatorCard
const BeatExample: React.FC<{ local: number }> = ({ local }) => {
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
};

// Beat 4: Why It Works (108-144s) — TakeawayChecklist
const BeatWhy: React.FC<{ local: number }> = ({ local }) => {
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
        <div style={{
          opacity: interpolate(local, [30, 60], [0, 1], CLAMP),
        }}>
          <TakeawayChecklist items={[
            "Flexible, not rigid — adjust to your situation",
            "Forces savings priority — pay yourself first",
            "Gives permission to spend — no guilt on wants",
          ]} />
        </div>
        {/* Stat highlight */}
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
};

// Beat 5: Action (144-180s) — ActionChecklist
const BeatAction: React.FC<{ local: number }> = ({ local }) => {
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
};

// Main composition
export const BudgetRule: React.FC = () => {
  const frame = useCurrentFrame();
  const BEAT_LEN = 36 * FPS; // 1080 frames per beat

  const beatIndex = Math.min(4, Math.floor(frame / BEAT_LEN));
  const local = frame - beatIndex * BEAT_LEN;

  return (
    <AbsoluteFill>
      <Audio src={voAudio} />
      {beatIndex === 0 && <BeatHook local={local} />}
      {beatIndex === 1 && <BeatRule local={local} />}
      {beatIndex === 2 && <BeatExample local={local} />}
      {beatIndex === 3 && <BeatWhy local={local} />}
      {beatIndex === 4 && <BeatAction local={local} />}
    </AbsoluteFill>
  );
};
