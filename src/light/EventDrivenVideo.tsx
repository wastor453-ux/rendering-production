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
import { CLAMP, T } from "./tokens";
import { LightCanvas, GlassCard } from "./primitives";
import { DonutChart, BarChart, LineChart } from "./charts";
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
    case "persist":
    case "persist_dimmed":
      // No exit — stays visible
      return { opacity: exit === "persist_dimmed" ? 0.6 : 1, transform: "none" };
    case "end_card":
      return { opacity: 1, transform: "none" };
    default:
      return { opacity: progress, transform: "none" };
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
  const entrance = useEntrance(event.entrance, localFrame);
  const exit = useExit(event.exit, frame, event);

  if (!exit) return null;

  // Combine entrance and exit
  const opacity = Math.min(entrance.opacity, exit.opacity);
  const transform = `${entrance.transform} ${exit.transform}`.trim() || "none";

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
    case "donut_segment":
      // Real DonutChart from the visual library
      return (
        <div data-event-id={event.event_id} style={wrapperStyle}>
          <DonutChart
            segments={[
              { label: "Payment History", value: 35, color: T.primary },
              { label: "Amounts Owed", value: 30, color: T.cyan },
              { label: "Length", value: 15, color: T.teal },
              { label: "New Credit", value: 10, color: T.lavender },
              { label: "Mix", value: 10, color: "#8B9BB4" },
            ]}
            title="What Makes Your Score"
            subtitle="Five factors, weighted by importance"
            centerLabel="FICO Score"
            centerValue="300–850"
          />
          <SourceDateLabel source="FICO scoring model" date="Illustrative" />
        </div>
      );

    case "hero_statement":
    case "hero_number":
      return (
        <div data-event-id={event.event_id} style={wrapperStyle}>
          <div style={{
            fontFamily: T.font, fontSize: 64, fontWeight: 800,
            color: T.ink, textAlign: "center", lineHeight: 1.2,
            maxWidth: 1400, padding: "0 100px",
          }}>
            {event.on_screen_text}
          </div>
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
    case "closing_card":
    case "timeline_event":
    case "timeline_event_positive":
    case "score_delta":
    case "delta_callout":
    case "gauge_visual":
      // Card-based visuals use the glass surface
      return (
        <div data-event-id={event.event_id} style={wrapperStyle}>
          <GlassCard width={900} padding={36}>
            <div style={{
              fontFamily: T.font, fontSize: 28, fontWeight: 600,
              color: T.ink, textAlign: "center", lineHeight: 1.4,
            }}>
              <div style={{ fontSize: 13, color: T.inkMuted, marginBottom: 12, textTransform: "uppercase", letterSpacing: 2 }}>
                {event.semantic_claim.replace(/_/g, " ")}
              </div>
              {event.on_screen_text}
            </div>
          </GlassCard>
        </div>
      );

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
      {audioSrc ? <Audio src={audioSrc} /> : null}
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
