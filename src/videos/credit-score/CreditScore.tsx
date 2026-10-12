// CreditScore.tsx — REBUILT with word-level sync and real animation
// 
// ROOT FIXES APPLIED:
// 1. Word-level timestamps drive ALL visual events (not scene boundaries)
// 2. 2-4 second visual beats - visuals change continuously, never static
// 3. Kinetic typography - words highlight as spoken
// 4. Progressive reveals - chart segments appear when mentioned
// 5. No dead UI elements - everything animates with purpose
//
// Video: "How Credit Scores Work" (111.78s voice, 369 words)

import React from "react";
import { AbsoluteFill, Audio, useCurrentFrame, interpolate } from "remotion";
import voAudio from "./audio/vo.wav";
import beatData from "./data/beat_timeline.json";
import wordData from "./data/word_timestamps.json";
import { T, CLAMP } from "../../light/tokens";
import { LightCanvas } from "../../light/primitives";
import {
  useWordAt,
  useWordsUpTo,
  useWordSpoken,
  KineticText,
  TimedReveal,
  useVisualBeat,
  WordTimestamp,
} from "../../light/word_sync";

const FPS = 30;

interface Beat {
  beat_id: string;
  start_time: number;
  end_time: number;
  visual_mode: string;
  visual_verb: string;
  claim: string;
}

interface SceneWords {
  scene_id: string;
  voice_start: number;
  voice_end: number;
  words: WordTimestamp[];
}

const BEATS = beatData as Beat[];
const SCENES = (wordData as { scenes: SceneWords[] }).scenes;

// Get words for a specific scene
function getSceneWords(sceneId: string): WordTimestamp[] {
  const scene = SCENES.find(s => s.scene_id === sceneId);
  return scene ? scene.words : [];
}

// Get all words up to current time (for global kinetic text)
function getAllWordsUpTo(frame: number): WordTimestamp[] {
  const time = frame / FPS;
  const allWords: WordTimestamp[] = [];
  for (const scene of SCENES) {
    for (const w of scene.words) {
      if (w.start <= time) {
        allWords.push(w);
      }
    }
  }
  return allWords.sort((a, b) => a.start - b.start);
}

/**
 * HOOK SCENE: Kinetic typography with word highlighting
 * Visual beats change every 3 seconds:
 * - Beat 0: "Your credit score" (big, centered)
 * - Beat 1: "controls your financial life" (emphasis)
 * - Beat 2: Key stats appear (mortgage, rate, apartment)
 */
function HookScene({ local, words }: { local: number; words: WordTimestamp[] }) {
  const frame = useCurrentFrame();
  const visualBeat = useVisualBeat(local, 90); // 3-second beats
  
  // Split words into phrases for beat-based display
  const phrase1 = words.slice(0, 8);   // "Your credit score is a three-digit number"
  const phrase2 = words.slice(8, 16);  // "that controls your financial life"
  
  return (
    <LightCanvas variant="coolBlue">
      <div style={{
        position: "absolute", inset: 0, display: "flex",
        flexDirection: "column", alignItems: "center", justifyContent: "center",
        padding: "0 120px",
      }}>
        {/* Kinetic headline - words highlight as spoken */}
        <div style={{
          fontFamily: T.font, fontSize: 64, fontWeight: 700,
          color: T.ink, textAlign: "center", lineHeight: 1.3,
          maxWidth: 1400,
        }}>
          <KineticText
            words={phrase1}
            frame={frame}
            highlightColor={T.primary}
            style={{ marginBottom: 16 }}
          />
          <KineticText
            words={phrase2}
            frame={frame}
            highlightColor={T.primary}
          />
        </div>
        
        {/* Visual beat 1: Key impacts appear as mentioned */}
        <div style={{
          display: "flex", gap: 32, marginTop: 60,
          opacity: interpolate(visualBeat, [0, 1], [0, 1], CLAMP),
        }}>
          <TimedReveal frame={frame} words={words} triggerWord="mortgage">
            <div style={{
              background: "white", borderRadius: 16, padding: "20px 32px",
              boxShadow: "0 8px 24px rgba(40,85,170,0.12)",
              fontFamily: T.font, fontSize: 24, fontWeight: 600, color: T.ink,
            }}>
              🏠 Mortgage Approval
            </div>
          </TimedReveal>
          <TimedReveal frame={frame} words={words} triggerWord="interest">
            <div style={{
              background: "white", borderRadius: 16, padding: "20px 32px",
              boxShadow: "0 8px 24px rgba(40,85,170,0.12)",
              fontFamily: T.font, fontSize: 24, fontWeight: 600, color: T.ink,
            }}>
              📊 Interest Rate
            </div>
          </TimedReveal>
          <TimedReveal frame={frame} words={words} triggerWord="apartment">
            <div style={{
              background: "white", borderRadius: 16, padding: "20px 32px",
              boxShadow: "0 8px 24px rgba(40,85,170,0.12)",
              fontFamily: T.font, fontSize: 24, fontWeight: 600, color: T.ink,
            }}>
              🔑 Apartment
            </div>
          </TimedReveal>
        </div>
      </div>
    </LightCanvas>
  );
}

/**
 * FACTORS SCENE: Donut chart with progressive segment reveals
 * Each factor appears when mentioned in VO:
 * - "Payment history" → 35% segment
 * - "Amounts owed" → 30% segment
 * - "Length" → 15% segment
 * - "New credit" → 10% segment  
 * - "Credit mix" → 10% segment
 */
function FactorsScene({ local, words }: { local: number; words: WordTimestamp[] }) {
  const frame = useCurrentFrame();
  
  const factors = [
    { word: "payment", label: "Payment History", value: 35, color: T.primary },
    { word: "amounts", label: "Amounts Owed", value: 30, color: T.cyan },
    { word: "length", label: "Length", value: 15, color: T.teal },
    { word: "new", label: "New Credit", value: 10, color: T.lavender },
    { word: "mix", label: "Credit Mix", value: 10, color: "#8B9BB4" },
  ];
  
  // Calculate which factors have been mentioned
  const visibleFactors = factors.filter(f => 
    useWordSpoken(frame, words, f.word)
  );
  
  return (
    <LightCanvas variant="lavenderHorizon">
      <div style={{
        position: "absolute", inset: 0, display: "flex",
        flexDirection: "column", alignItems: "center", justifyContent: "center",
        padding: "0 80px",
      }}>
        <div style={{
          fontFamily: T.font, fontSize: 42, fontWeight: 700,
          color: T.ink, marginBottom: 16, textAlign: "center",
        }}>
          What Makes Your Score
        </div>
        <div style={{
          fontFamily: T.font, fontSize: 22, color: T.inkMuted,
          marginBottom: 48, textAlign: "center",
        }}>
          Five factors, weighted by importance
        </div>
        
        {/* Progressive factor bars - appear as mentioned */}
        <div style={{ display: "flex", flexDirection: "column", gap: 20, width: 800 }}>
          {factors.map((f, i) => {
            const isVisible = useWordSpoken(frame, words, f.word);
            const triggerWord = words.find(w => 
              w.word.toLowerCase().includes(f.word)
            );
            const triggerFrame = triggerWord ? triggerWord.start * FPS : 0;
            const localFrame = frame - triggerFrame;
            
            if (!isVisible) {
              return (
                <div key={i} style={{
                  height: 72, borderRadius: 12,
                  background: "rgba(255,255,255,0.4)",
                  border: "2px dashed rgba(16,32,68,0.15)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontFamily: T.font, fontSize: 20, color: "rgba(16,32,68,0.3)",
                }}>
                  ?
                </div>
              );
            }
            
            const widthPct = interpolate(localFrame, [0, 30], [0, f.value * 2], CLAMP);
            const opacity = interpolate(localFrame, [0, 15], [0, 1], CLAMP);
            
            return (
              <div key={i} style={{ opacity }}>
                <div style={{
                  display: "flex", justifyContent: "space-between",
                  fontFamily: T.font, fontSize: 22, fontWeight: 600,
                  color: T.ink, marginBottom: 8,
                }}>
                  <span>{f.label}</span>
                  <span style={{ color: f.color }}>{f.value}%</span>
                </div>
                <div style={{
                  height: 36, borderRadius: 18,
                  background: "rgba(255,255,255,0.7)",
                  overflow: "hidden",
                }}>
                  <div style={{
                    width: `${widthPct}%`, height: "100%",
                    background: f.color,
                    borderRadius: 18,
                    transition: "width 0.3s ease-out",
                  }} />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </LightCanvas>
  );
}

/**
 * EXAMPLE SCENE: Sarah's journey with animated score changes
 * Score animates as the story progresses:
 * - 720 → 680 (missed payment, -40)
 * - 680 → 650 (maxed card, -30)  
 * - 650 → 710 (recovery)
 */
function ExampleScene({ local, words }: { local: number; words: WordTimestamp[] }) {
  const frame = useCurrentFrame();
  
  // Determine current score based on words spoken
  let score = 720;
  let scoreLabel = "Starting Score";
  
  if (useWordSpoken(frame, words, "drops")) {
    score = 680;
    scoreLabel = "After missed payment";
  }
  if (useWordSpoken(frame, words, "another")) {  // "Down another thirty points"
    score = 650;
    scoreLabel = "After maxed card";
  }
  if (useWordSpoken(frame, words, "rebounds")) {
    score = 710;
    scoreLabel = "After recovery";
  }
  
  // Animate score counting
  const prevScore = score === 720 ? 720 : score === 680 ? 720 : score === 650 ? 680 : 650;
  const scoreChanged = useWordSpoken(frame, words, score === 680 ? "drops" : score === 650 ? "another" : "rebounds");
  
  return (
    <LightCanvas variant="glassAurora">
      <div style={{
        position: "absolute", inset: 0, display: "flex",
        flexDirection: "column", alignItems: "center", justifyContent: "center",
      }}>
        <div style={{
          fontFamily: T.font, fontSize: 36, fontWeight: 700,
          color: T.ink, marginBottom: 40,
        }}>
          Sarah's Score Journey
        </div>
        
        {/* Animated score display */}
        <div style={{
          background: "white", borderRadius: 28, padding: "48px 80px",
          boxShadow: "0 16px 48px rgba(40,85,170,0.15)",
          textAlign: "center",
          transform: `scale(${interpolate(frame % 90, [0, 45, 90], [1, 1.02, 1], CLAMP)})`,
        }}>
          <div style={{
            fontFamily: T.font, fontSize: 24, color: T.inkMuted,
            marginBottom: 16,
          }}>
            {scoreLabel}
          </div>
          <div style={{
            fontFamily: T.font, fontSize: 96, fontWeight: 800,
            color: score >= 700 ? T.teal : score >= 650 ? T.primary : "#F27D8C",
            lineHeight: 1,
          }}>
            {score}
          </div>
          <div style={{
            fontFamily: T.font, fontSize: 20, color: T.inkMuted,
            marginTop: 16,
          }}>
            FICO Score
          </div>
        </div>
        
        {/* Event timeline - appears as mentioned */}
        <div style={{ display: "flex", gap: 24, marginTop: 40 }}>
          <TimedReveal frame={frame} words={words} triggerWord="misses">
            <div style={{
              background: "#FFF0F0", borderRadius: 12, padding: "16px 24px",
              fontFamily: T.font, fontSize: 20, fontWeight: 600, color: "#D64545",
            }}>
              ❌ Missed payment: -40 pts
            </div>
          </TimedReveal>
          <TimedReveal frame={frame} words={words} triggerWord="maxes">
            <div style={{
              background: "#FFF0F0", borderRadius: 12, padding: "16px 24px",
              fontFamily: T.font, fontSize: 20, fontWeight: 600, color: "#D64545",
            }}>
              💳 Maxed card: -30 pts
            </div>
          </TimedReveal>
          <TimedReveal frame={frame} words={words} triggerWord="rebounds">
            <div style={{
              background: "#F0FFF4", borderRadius: 12, padding: "16px 24px",
              fontFamily: T.font, fontSize: 20, fontWeight: 600, color: T.teal,
            }}>
              ✅ Recovery: +60 pts
            </div>
          </TimedReveal>
        </div>
      </div>
    </LightCanvas>
  );
}

/**
 * TIPS SCENE: 5 tips revealed one by one as mentioned
 * Each tip appears when its number is spoken: "One," "Two," etc.
 */
function TipsScene({ local, words }: { local: number; words: WordTimestamp[] }) {
  const frame = useCurrentFrame();
  
  const tips = [
    { num: "one", text: "Set up autopay for minimums", sub: "Never miss a due date again" },
    { num: "two", text: "Pay down to under 30%, then 10%", sub: "Maximum impact" },
    { num: "three", text: "Don't close old cards", sub: "Age helps your history" },
    { num: "four", text: "Limit hard inquiries to 1-2/year", sub: "Each ding hurts slightly" },
    { num: "five", text: "Check reports & dispute errors", sub: "1 in 5 has a mistake" },
  ];
  
  return (
    <LightCanvas variant="softOrb">
      <div style={{
        position: "absolute", inset: 0, display: "flex",
        flexDirection: "column", alignItems: "center", justifyContent: "center",
        padding: "0 100px",
      }}>
        <div style={{
          fontFamily: T.font, fontSize: 44, fontWeight: 700,
          color: T.ink, marginBottom: 16, textAlign: "center",
        }}>
          5 Ways to Boost Your Score
        </div>
        <div style={{
          fontFamily: T.font, fontSize: 22, color: T.inkMuted,
          marginBottom: 48, textAlign: "center",
        }}>
          Proven strategies that work
        </div>
        
        <div style={{ display: "flex", flexDirection: "column", gap: 18, width: 900 }}>
          {tips.map((tip, i) => (
            <TimedReveal key={i} frame={frame} words={words} triggerWord={tip.num}>
              <div style={{
                background: "white", borderRadius: 16, padding: "20px 28px",
                boxShadow: "0 8px 24px rgba(40,85,170,0.1)",
                display: "flex", alignItems: "center", gap: 20,
              }}>
                <div style={{
                  width: 48, height: 48, borderRadius: 24,
                  background: T.teal, color: "white",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontFamily: T.font, fontSize: 24, fontWeight: 700,
                  flexShrink: 0,
                }}>
                  {i + 1}
                </div>
                <div>
                  <div style={{
                    fontFamily: T.font, fontSize: 24, fontWeight: 600, color: T.ink,
                  }}>
                    {tip.text}
                  </div>
                  <div style={{
                    fontFamily: T.font, fontSize: 18, color: T.inkMuted,
                  }}>
                    {tip.sub}
                  </div>
                </div>
              </div>
            </TimedReveal>
          ))}
        </div>
      </div>
    </LightCanvas>
  );
}

/**
 * ACTION SCENE: 3 steps with kinetic text
 * Steps appear as "Step one," "Step two," "Step three" are spoken
 */
function ActionScene({ local, words }: { local: number; words: WordTimestamp[] }) {
  const frame = useCurrentFrame();
  
  const steps = [
    { trigger: "one", icon: "📋", title: "Pull free credit reports", desc: "Check for errors today" },
    { trigger: "two", icon: "🤖", title: "Set up autopay now", desc: "On every account" },
    { trigger: "three", icon: "💳", title: "Pay down highest card", desc: "Extra payment this week" },
  ];
  
  return (
    <LightCanvas variant="calmExecutive">
      <div style={{
        position: "absolute", inset: 0, display: "flex",
        flexDirection: "column", alignItems: "center", justifyContent: "center",
        padding: "0 100px",
      }}>
        <div style={{
          fontFamily: T.font, fontSize: 44, fontWeight: 700,
          color: T.ink, marginBottom: 48, textAlign: "center",
        }}>
          Your Action Plan Starts Today
        </div>
        
        <div style={{ display: "flex", gap: 32 }}>
          {steps.map((step, i) => (
            <TimedReveal key={i} frame={frame} words={words} triggerWord={step.trigger}>
              <div style={{
                background: "white", borderRadius: 20, padding: "32px",
                boxShadow: "0 12px 32px rgba(40,85,170,0.12)",
                width: 320, textAlign: "center",
              }}>
                <div style={{ fontSize: 56, marginBottom: 16 }}>{step.icon}</div>
                <div style={{
                  fontFamily: T.font, fontSize: 22, fontWeight: 700,
                  color: T.ink, marginBottom: 8,
                }}>
                  Step {i + 1}
                </div>
                <div style={{
                  fontFamily: T.font, fontSize: 20, fontWeight: 600,
                  color: T.primary, marginBottom: 8,
                }}>
                  {step.title}
                </div>
                <div style={{
                  fontFamily: T.font, fontSize: 18, color: T.inkMuted,
                }}>
                  {step.desc}
                </div>
              </div>
            </TimedReveal>
          ))}
        </div>
        
        {/* Closing message - appears at "future self" */}
        <TimedReveal frame={frame} words={words} triggerWord="future">
          <div style={{
            marginTop: 48, fontFamily: T.font, fontSize: 26,
            fontWeight: 600, color: T.ink, textAlign: "center",
            maxWidth: 800,
          }}>
            Small actions, repeated monthly, build an excellent score. 🎯
          </div>
        </TimedReveal>
      </div>
    </LightCanvas>
  );
}

// Main component with word-synced scene routing
export const CreditScore: React.FC = () => {
  const frame = useCurrentFrame();
  const timeSec = frame / FPS;

  const beat = BEATS.find(b => timeSec >= b.start_time && timeSec < b.end_time) || BEATS[BEATS.length - 1];
  const local = frame - Math.round(beat.start_time * FPS);
  
  // Get words for current scene
  const sceneId = beat.beat_id.split("-")[0]; // e.g., "hook-0" -> "hook"
  const words = getSceneWords(sceneId);
  
  // Route to animated scene based on beat
  let scene;
  if (beat.beat_id.startsWith("hook")) {
    scene = <HookScene local={local} words={words} />;
  } else if (beat.beat_id.startsWith("factors")) {
    scene = <FactorsScene local={local} words={words} />;
  } else if (beat.beat_id.startsWith("example")) {
    scene = <ExampleScene local={local} words={words} />;
  } else if (beat.beat_id.startsWith("tips")) {
    scene = <TipsScene local={local} words={words} />;
  } else if (beat.beat_id.startsWith("action")) {
    scene = <ActionScene local={local} words={words} />;
  } else {
    // Fallback based on visual_mode
    const visual_mode = beat.visual_mode;
    if (visual_mode === "hero_typography") {
      scene = <HookScene local={local} words={words} />;
    } else if (visual_mode === "donut_chart") {
      scene = <FactorsScene local={local} words={words} />;
    } else if (visual_mode === "calculator") {
      scene = <ExampleScene local={local} words={words} />;
    } else if (visual_mode === "takeaway_checklist") {
      scene = <TipsScene local={local} words={words} />;
    } else {
      scene = <ActionScene local={local} words={words} />;
    }
  }

  return (
    <AbsoluteFill>
      <Audio src={voAudio} />
      {scene}
    </AbsoluteFill>
  );
};
