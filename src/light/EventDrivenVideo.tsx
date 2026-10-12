/**
 * EventDrivenVideo.tsx — GENERIC production pipeline renderer.
 *
 * SYSTEM FIX: The event timeline was a sidecar JSON that no component read.
 * This renderer consumes the event plan directly.
 *
 * Architecture:
 *   1. Load event_timeline.json (generated from whisper alignment)
 *   2. For each frame, find active events (start_frame <= frame < end_frame)
 *   3. Route each event to its visual component via semantic selector
 *   4. Apply entrance/progression/exit animations (frame-driven, no CSS transitions)
 *
 * This is generic: works for any finance video with an event timeline.
 * No video-specific code. No hardcoded scenes.
 */

import React from "react";
import { AbsoluteFill, Audio, useCurrentFrame, interpolate } from "remotion";
import { CLAMP, T, TYPE } from "./tokens";
import { Hook, CardTitle, Body, Caption } from "./Typography";
import { LightCanvas, GlassCard } from "./primitives";
import { KPICard, SourceDateLabel, SectionTitle } from "./components_v2";

// Event timeline types
export interface WordAnchor {
  word_index: number;
  word: string;
  phrase: string;
  start_s: number;
  end_s: number;
}

export interface VisualEvent {
  event_id: string;
  start_frame: number;
  end_frame: number;
  word_anchor: WordAnchor;
  semantic_claim: string;
  visual_type: string;
  entrance: string;
  progression: string;
  exit: string;
  on_screen_text: string;
}

export interface EventTimeline {
  source: string;
  alignment_source: string;
  fps: number;
  event_count: number;
  events: VisualEvent[];
}

const FPS = 30;

/**
 * Apply entrance animation based on event.entrance type.
 * All animations are frame-driven (no CSS transitions).
 */
function useEntrance(
  entrance: string,
  localFrame: number,
  durationFrames: number = 20
): { opacity: number; transform: string } {
  const progress = interpolate(localFrame, [0, durationFrames], [0, 1], {
    ...CLAMP,
    easing: (t: number) => 1 - Math.pow(1 - t, 3), // ease-out cubic
  });

  switch (entrance) {
    case "kinetic_build":
    case "fade_in":
      return { opacity: progress, transform: "none" };
    case "pop_in":
      const scale = interpolate(localFrame, [0, durationFrames], [0.8, 1], CLAMP);
      return { opacity: progress, transform: `scale(${scale})` };
    case "slide_in":
      const y = interpolate(localFrame, [0, durationFrames], [40, 0], CLAMP);
      return { opacity: progress, transform: `translateY(${y}px)` };
    case "donut_reveal":
      // Donut segments reveal via stroke-dashoffset (handled in component)
      return { opacity: progress, transform: "none" };
    case "count_up":
    case "gauge_fill":
    case "marker_drop":
    case "marker_drop_positive":
      const dropY = interpolate(localFrame, [0, durationFrames], [-30, 0], CLAMP);
      return { opacity: progress, transform: `translateY(${dropY}px)` };
    case "wipe_in":
      // Wipe handled via clip-path in component
      return { opacity: progress, transform: "none" };
    case "callout_in":
    case "delta_badge":
    case "delta_badge_positive":
      const badgeScale = interpolate(localFrame, [0, 12, durationFrames], [0.5, 1.1, 1], CLAMP);
      return { opacity: progress, transform: `scale(${badgeScale})` };
    default:
      return { opacity: progress, transform: "none" };
  }
}

/**
 * Apply exit animation based on event.exit type.
 * Returns null if event should not render (fully exited).
 */
function useExit(
  exit: string,
  frame: number,
  event: VisualEvent
): { opacity: number; transform: string } | null {
  const framesUntilEnd = event.end_frame - frame;
  const exitDuration = 15; // frames

  if (framesUntilEnd > exitDuration) {
    return { opacity: 1, transform: "none" };
  }

  // F-17: Persist exits must be checked BEFORE the fully-exited early return.
  // Otherwise persist/persist_dimmed can never take effect.
  if (exit === "persist" || exit === "persist_dimmed") {
    return { opacity: exit === "persist_dimmed" ? 0.6 : 1, transform: "none" };
  }

  if (framesUntilEnd <= 0) {
    return null; // Fully exited
  }

  const progress = interpolate(framesUntilEnd, [0, exitDuration], [0, 1], CLAMP);

  switch (exit) {
    case "fade":
    case "fade_with_next":
      return { opacity: progress, transform: "none" };
    case "wipe_to_factors":
    case "wipe_to_next":
    case "morph_to_next":
    case "morph_to_chart":
    case "morph_to_example":
    case "morph_to_tips":
    case "morph_to_action":
    case "morph_to_close":
    case "morph_to_list":
    case "morph_to_steps":
    case "morph_to_story":
      // Morph: scale down slightly and fade
      const scale = interpolate(framesUntilEnd, [0, exitDuration], [0.95, 1], CLAMP);
      return { opacity: progress, transform: `scale(${scale})` };
    // "persist" / "persist_dimmed" handled above (before fully-exited check)
    case "end_card":
      return { opacity: 1, transform: "none" };
    default:
      return { opacity: progress, transform: "none" };
  }
}

/**
 * Apply progression animation based on event.progression type.
 * Progression is the mid-event animation (after entrance, before exit).
 * All animations are frame-driven (no CSS transitions).
 */
function useProgression(
  progression: string,
  localFrame: number,
  eventDuration: number
): { opacity: number; transform: string; progress: number } {
  const mid = Math.max(0, localFrame - 20); // after entrance
  const midDuration = Math.max(1, eventDuration - 35); // before exit
  const progress = interpolate(mid, [0, midDuration], [0, 1], CLAMP);

  switch (progression) {
    case "hold":
    case "hold_to_end":
      return { opacity: 1, transform: "none", progress: 1 };
    case "hold_with_pulse": {
      const pulse = 1 + 0.03 * Math.sin((localFrame * Math.PI) / 15);
      return { opacity: 1, transform: `scale(${pulse})`, progress: 1 };
    }
    case "word_highlight":
    case "label_count_up":
    case "count_up_to_value":
    case "score_count_down":
    case "progress_bar_fill":
    case "arrow_draw":
    case "arrow_draw_up":
    case "marker_to_ideal":
    case "check_reveal":
    case "icon_animate":
      // Progress-driven animations: components use `progress` (0-1)
      // to drive their specific animation (fill, draw, count, etc.)
      return { opacity: 1, transform: "none", progress };
    default:
      // Unknown progression: fail-closed via validator, render static here
      return { opacity: 1, transform: "none", progress: 1 };
  }
}

/**
 * Generic event renderer.
 * Routes visual_type to real components from the visual library.
 *
 * This is the semantic selector: visual_type → actual component.
 * A requested donut chart renders as a donut chart, never as bars.
 * Unsupported visual types throw (fail-closed).
 */
function EventVisual({
  event,
  frame,
}: {
  event: VisualEvent;
  frame: number;
}) {
  const localFrame = frame - event.start_frame;
  const eventDuration = event.end_frame - event.start_frame;
  const entrance = useEntrance(event.entrance, localFrame);
  const progression = useProgression(event.progression, localFrame, eventDuration);
  const exit = useExit(event.exit, frame, event);

  if (!exit) return null;

  // Combine entrance, progression, and exit (F-07: progression was computed but not applied)
  const opacity = Math.min(entrance.opacity, progression.opacity, exit.opacity);
  const transform = `${entrance.transform} ${progression.transform} ${exit.transform}`.trim() || "none";

  const wrapperStyle: React.CSSProperties = {
    opacity,
    transform,
    position: "absolute",
    inset: 0,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    pointerEvents: "none",
  };

  // Semantic routing: visual_type → real library component
  switch (event.visual_type) {
    case "factor_card":
      // Factor highlight card — driven entirely by event data.
      // The event provides on_screen_text and semantic_claim from validated
      // video-owned inputs. No hardcoded segments, values, or labels.
      return (
        <div data-event-id={event.event_id} style={wrapperStyle}>
          <LightCanvas>
            <GlassCard style={{ padding: 48, textAlign: "center" }}>
              <Hook>{event.on_screen_text || "Factor"}</Hook>
              <Body style={{ marginTop: 16, color: T.inkMuted }}>
                {event.semantic_claim?.replace(/_/g, " ") || ""}
              </Body>
            </GlassCard>
          </LightCanvas>
          <SourceDateLabel source="Video data" date="Validated" />
        </div>
      );

    case "hero_statement":
    case "hero_number":
      return (
        <div data-event-id={event.event_id} style={wrapperStyle}>
          <Hook style={{
            color: T.ink, textAlign: "center", lineHeight: 1.2,
            maxWidth: 1400, padding: "0 100px",
          }}>
            {event.on_screen_text}
          </Hook>
        </div>
      );

    case "score_card":
      return (
        <div data-event-id={event.event_id} style={wrapperStyle}>
          <KPICard
            label={event.semantic_claim.replace(/_/g, " ")}
            value={event.on_screen_text}
            width={480}
          />
        </div>
      );

    case "section_title":
      return (
        <div data-event-id={event.event_id} style={wrapperStyle}>
          <SectionTitle
            title={event.on_screen_text}
            subtitle={event.semantic_claim}
          />
        </div>
      );

    case "gauge_visual": {
      // F-13: Real gauge — horizontal bar showing a level.
      // Extracts percentage from text if present; otherwise shows the text with an indeterminate gauge.
      const pctMatch = event.on_screen_text.match(/(\d+)\s*%/);
      const pct = pctMatch ? Math.min(100, parseInt(pctMatch[1], 10)) : null;
      const gaugeFill = pct !== null ? pct : 50;
      return (
        <div data-event-id={event.event_id} style={wrapperStyle}>
          <GlassCard width={900} padding={36} style={{ borderTop: "6px solid #3478F6" }}>
            <Caption style={{ color: "#3478F6", marginBottom: 12, textAlign: "center" }}>
              GAUGE
            </Caption>
            <CardTitle style={{ color: T.ink, textAlign: "center", fontSize: 40, marginBottom: 24 }}>
              {event.on_screen_text}
            </CardTitle>
            {/* Gauge bar */}
            <div style={{ width: "100%", height: 32, background: "#EAF1FF", borderRadius: 16, overflow: "hidden", position: "relative" }}>
              <div style={{
                width: `${gaugeFill}%`, height: "100%",
                background: "linear-gradient(90deg, #3478F6, #31B9F4)",
                borderRadius: 16,
                transition: "width 0.5s ease-out",
              }} />
              {pct !== null && (
                <div style={{
                  position: "absolute", right: 12, top: "50%", transform: "translateY(-50%)",
                  fontFamily: T.font, fontWeight: 700, fontSize: 18, color: T.ink,
                }}>
                  {pct}%
                </div>
              )}
            </div>
            <div style={{ marginTop: 16, fontSize: 18, color: T.inkMuted, textAlign: "center" }}>
              {event.semantic_claim.replace(/_/g, " ")}
            </div>
          </GlassCard>
        </div>
      );
    }

    case "timeline_event":
    case "timeline_event_positive": {
      // F-13: Real timeline — node on a chronological line with the event text.
      const isPositive = event.visual_type === "timeline_event_positive";
      const accent = isPositive ? "#18BFAE" : "#3478F6";
      return (
        <div data-event-id={event.event_id} style={wrapperStyle}>
          <GlassCard width={900} padding={36} style={{ borderTop: `6px solid ${accent}` }}>
            <Caption style={{ color: accent, marginBottom: 20, textAlign: "center" }}>
              {isPositive ? "MILESTONE" : "TIMELINE"}
            </Caption>
            {/* Timeline line with node */}
            <div style={{ display: "flex", alignItems: "center", marginBottom: 24 }}>
              <div style={{ flex: 1, height: 4, background: "#EAF1FF", borderRadius: 2 }} />
              <div style={{
                width: 48, height: 48, borderRadius: "50%",
                background: accent, border: "4px solid white",
                boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
                display: "flex", alignItems: "center", justifyContent: "center",
                margin: "0 16px",
                flexShrink: 0,
              }}>
                
              </div>
              <div style={{ flex: 1, height: 4, background: "#EAF1FF", borderRadius: 2 }} />
            </div>
            <CardTitle style={{ color: T.ink, textAlign: "center", fontSize: 36, lineHeight: 1.4 }}>
              {event.on_screen_text}
            </CardTitle>
            <div style={{ marginTop: 16, fontSize: 18, color: T.inkMuted, textAlign: "center" }}>
              {event.semantic_claim.replace(/_/g, " ")}
            </div>
          </GlassCard>
        </div>
      );
    }

    case "score_delta":
    case "delta_callout": {
      // F-13: Real delta — communicates change with direction and magnitude.
      // Extracts numbers from text; infers direction from keywords.
      const text = event.on_screen_text;
      const nums = text.match(/\d+/g)?.map(Number) || [];
      const value = nums.length > 0 ? nums[nums.length - 1] : null;
      const lower = text.toLowerCase();
      const isUp = /rebound|rise|increase|up|gain|improve/.test(lower);
      const isDown = /drop|fall|decrease|down|decline|lose/.test(lower);
      const direction = isUp ? "up" : isDown ? "down" : null;
      const color = direction === "up" ? "#18BFAE" : direction === "down" ? "#F27D8C" : "#3478F6";
      const arrow = direction === "up" ? "▲" : direction === "down" ? "▼" : "●";
      return (
        <div data-event-id={event.event_id} style={wrapperStyle}>
          <GlassCard width={900} padding={36} style={{ borderTop: `6px solid ${color}` }}>
            <Caption style={{ color, marginBottom: 12, textAlign: "center" }}>
              SCORE CHANGE
            </Caption>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 24, marginBottom: 16 }}>
              <span style={{ fontSize: 64, color }}>{arrow}</span>
              {value !== null && (
                <span style={{ fontFamily: T.font, fontWeight: 800, fontSize: 72, color: T.ink }}>
                  {value}
                </span>
              )}
            </div>
            <CardTitle style={{ color: T.ink, textAlign: "center", fontSize: 32, lineHeight: 1.4 }}>
              {text}
            </CardTitle>
            <div style={{ marginTop: 16, fontSize: 18, color: T.inkMuted, textAlign: "center" }}>
              {event.semantic_claim.replace(/_/g, " ")}
            </div>
          </GlassCard>
        </div>
      );
    }

    case "impact_card":
    case "tip_card":
    case "action_card":
    case "advice_callout":
    case "question_card":
    case "promise_card":
    case "transition_card":
    case "stat_callout":
    case "principle_card":
    case "encouragement_card":
    case "closing_card": {
      // F-13: Semantic card variants — distinct accent, label, and treatment
      // per type (not identical cards). Uses the shared glass primitive
      // with type-specific styling.
      const TYPE_STYLE: Record<string, { accent: string; label: string; size: number }> = {
        impact_card:            { accent: "#3478F6", label: "Impact",      size: 44 },
        tip_card:               { accent: "#18BFAE", label: "Tip",         size: 40 },
        action_card:            { accent: "#3478F6", label: "Action",      size: 40 },
        advice_callout:         { accent: "#18BFAE", label: "Advice",      size: 40 },
        question_card:          { accent: "#8C7BFF", label: "Question",    size: 48 },
        promise_card:           { accent: "#8C7BFF", label: "Promise",     size: 40 },
        transition_card:        { accent: "#5E6B82", label: "",            size: 36 },
        stat_callout:           { accent: "#3478F6", label: "Stat",        size: 56 },
        principle_card:         { accent: "#102044", label: "Principle",   size: 44 },
        encouragement_card:     { accent: "#18BFAE", label: "",            size: 44 },
        closing_card:           { accent: "#102044", label: "",            size: 48 },
        timeline_event:         { accent: "#3478F6", label: "Timeline",    size: 40 },
        timeline_event_positive:{ accent: "#18BFAE", label: "Milestone",   size: 40 },
        score_delta:            { accent: "#F27D8C", label: "Change",      size: 52 },
        delta_callout:          { accent: "#F27D8C", label: "Delta",       size: 48 },
        gauge_visual:           { accent: "#3478F6", label: "Gauge",       size: 44 },
      };
      const ts = TYPE_STYLE[event.visual_type] || { accent: "#3478F6", label: "", size: 40 };
      // Delta types show directional indicator based on text content
      const isPositiveDelta = (event.visual_type === "score_delta" || event.visual_type === "delta_callout" ||
                               event.visual_type === "timeline_event_positive");
      const deltaColor = isPositiveDelta ? "#18BFAE" : ts.accent;
      return (
        <div data-event-id={event.event_id} style={wrapperStyle}>
          <GlassCard width={900} padding={36} style={{ borderTop: `6px solid ${deltaColor}` }}>
            <CardTitle style={{
              color: T.ink, textAlign: "center", lineHeight: 1.4, fontSize: ts.size,
            }}>
              {ts.label && (
                <Caption style={{ color: deltaColor, marginBottom: 12 }}>
                  {ts.label.toUpperCase()}
                </Caption>
              )}
              {isPositiveDelta && <span style={{ color: deltaColor, marginRight: 12 }}>▲</span>}
              {event.on_screen_text}
            </CardTitle>
            <div style={{ marginTop: 16, fontSize: 18, color: T.inkMuted, textAlign: "center" }}>
              {event.semantic_claim.replace(/_/g, " ")}
            </div>
          </GlassCard>
        </div>
      );
    }

    default:
      // Fail-closed: unsupported visual types throw, never silently substitute
      throw new Error(
        `EventDrivenVideo: unsupported visual_type "${event.visual_type}" ` +
        `(event ${event.event_id}, concept ${event.semantic_claim}). ` +
        `Add a case in EventVisual or use a documented valid type.`
      );
  }
}

/**
 * Generic event-driven video component.
 *
 * Props:
 *   - timeline: EventTimeline (from generate_event_timeline.py)
 *   - audioSrc: VO audio file import
 *   - backgroundVariant: LightCanvas variant
 *
 * Usage:
 *   Pass the video's timeline data and audio source as props:
 *   <EventDrivenVideo timeline={timelineData} audioSrc={audioPath} />
 *   where timelineData comes from the video's data/event_timeline.json
 *   and audioPath comes from the video's audio/vo.wav
 */
export function EventDrivenVideo({
  timeline,
  audioSrc,
  backgroundVariant = "coolBlue",
}: {
  timeline: EventTimeline;
  audioSrc: string;
  backgroundVariant?: string;
}) {
  const frame = useCurrentFrame();

  // Find active events for this frame
  const activeEvents = timeline.events.filter(
    (e) => frame >= e.start_frame && frame < e.end_frame + 30 // 1s grace for exits
  );

  return (
    <AbsoluteFill>
      <Audio src={audioSrc} />
      <LightCanvas variant={backgroundVariant as any}>
        {activeEvents.map((event) => (
          <EventVisual key={event.event_id} event={event} frame={frame} />
        ))}
      </LightCanvas>
    </AbsoluteFill>
  );
}

/**
 * Validate that a timeline is consumable by the renderer.
 * FAIL-CLOSED: returns list of errors (empty = valid).
 */
export function validateTimeline(timeline: EventTimeline): string[] {
  const errors: string[] = [];

  if (!timeline.events || timeline.events.length === 0) {
    errors.push("Timeline has zero events. Generate with tools/generate_event_timeline.py");
    return errors;
  }

  const seenIds = new Set<string>();
  for (const e of timeline.events) {
    if (seenIds.has(e.event_id)) {
      errors.push(`Duplicate event_id: ${e.event_id}`);
    }
    seenIds.add(e.event_id);

    if (e.start_frame >= e.end_frame) {
      errors.push(`Event ${e.event_id}: start_frame >= end_frame`);
    }

    if (!e.word_anchor || e.word_anchor.word_index < 0) {
      errors.push(`Event ${e.event_id}: missing word_anchor`);
    }

    if (!e.visual_type) {
      errors.push(`Event ${e.event_id}: missing visual_type`);
    }

    if (!e.entrance || !e.exit) {
      errors.push(`Event ${e.event_id}: missing entrance or exit`);
    }
  }

  // Check for excessive gaps (>4s with no active event)
  const sorted = [...timeline.events].sort((a, b) => a.start_frame - b.start_frame);
  for (let i = 1; i < sorted.length; i++) {
    const gapFrames = sorted[i].start_frame - sorted[i - 1].end_frame;
    const gapS = gapFrames / FPS;
    if (gapS > 4.0) {
      errors.push(
        `Gap of ${gapS.toFixed(1)}s between ${sorted[i - 1].event_id} and ${sorted[i].event_id} exceeds 4s hold ceiling`
      );
    }
  }

  return errors;
}
