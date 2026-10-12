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
import { CLAMP } from "./tokens";
import { LightCanvas } from "./primitives";

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
 * Routes visual_type to the appropriate component.
 * 
 * NOTE: This is the integration point for the visual library.
 * Each visual_type should map to a real component from src/light/.
 * Currently renders semantic placeholders; Phase B3 wires real components.
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

  // Route to visual component by type
  // TODO (Phase B3): Replace placeholders with real library components:
  //   donut_segment → DonutChart from src/light/charts.tsx
  //   hero_statement → HeroTypography from src/light/primitives.tsx
  //   score_card → KPICard from src/light/components_v2.tsx
  //   etc.
  return (
    <div
      data-event-id={event.event_id}
      data-visual-type={event.visual_type}
      data-concept={event.semantic_claim}
      style={{
        opacity,
        transform: `${entrance.transform} ${exit.transform}`.trim() || "none",
        position: "absolute",
        inset: 0,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        pointerEvents: "none",
      }}
    >
      <div
        style={{
          fontFamily: "Inter, sans-serif",
          fontSize: 32,
          fontWeight: 600,
          color: "#102044",
          background: "rgba(255,255,255,0.92)",
          borderRadius: 16,
          padding: "24px 40px",
          boxShadow: "0 8px 24px rgba(40,85,170,0.12)",
          maxWidth: 1200,
          textAlign: "center",
        }}
      >
        <div style={{ fontSize: 14, color: "#8B9BB4", marginBottom: 8 }}>
          [{event.visual_type} · {event.semantic_claim}]
        </div>
        {event.on_screen_text}
      </div>
    </div>
  );
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
 *   import timeline from "./data/event_timeline.json";
 *   import voAudio from "./audio/vo.wav";
 *   export const MyVideo = () => (
 *     <EventDrivenVideo timeline={timeline} audioSrc={voAudio} />
 *   );
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
