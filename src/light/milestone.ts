// milestone.ts — UNIVERSAL VISUAL MILESTONE INTERFACE (P0 §6)
//
// One contract for every semantic visual event. The event compiler owns the
// canonical frames; the renderer receives this milestone and solves its local
// animation so the punch lands EXACTLY on localImpactFrame.
//
// The old per-component props (impactAt, impactRow, impactNode, impactBar)
// remain as compatibility adapters — see legacyImpactProps() below.
// New production code routes through this interface.

export type VisualEventMilestone = {
  eventId: string;
  beatId: string;
  /** canonical frames on the full-composition timeline (30fps) */
  globalStartFrame: number;
  globalImpactFrame: number;
  globalSettleFrame: number;
  /** frames relative to the beat's <Sequence> start */
  localStartFrame: number;
  localImpactFrame: number;
  localSettleFrame: number;
  visualMode: string;
  visualVerb: string;
  semanticRole: string;
};

export type CompiledEvent = {
  event_id: string;
  beat_id: string;
  phrase: string;
  anchor_time_s: number;
  semantic_role: string;
  visual_verb: string;
  visual_mode: string;
  visual_start_frame: number;
  visual_impact_frame: number;
  visual_settle_frame: number;
};

/** Convert a compiled (global-frame) event into the local-frame milestone
 *  for a beat rendered inside <Sequence from={beatFromFrame}>. */
export function toLocalMilestone(
  ev: CompiledEvent,
  beatFromFrame: number,
): VisualEventMilestone {
  return {
    eventId: ev.event_id,
    beatId: ev.beat_id,
    globalStartFrame: ev.visual_start_frame,
    globalImpactFrame: ev.visual_impact_frame,
    globalSettleFrame: ev.visual_settle_frame,
    localStartFrame: ev.visual_start_frame - beatFromFrame,
    localImpactFrame: ev.visual_impact_frame - beatFromFrame,
    localSettleFrame: ev.visual_settle_frame - beatFromFrame,
    visualMode: ev.visual_mode,
    visualVerb: ev.visual_verb,
    semanticRole: ev.semantic_role,
  };
}

/** Compatibility adapter: map the universal milestone onto the legacy
 *  per-component timing props. New components should accept the milestone
 *  directly instead of growing new props. */
export function legacyImpactProps(
  m: VisualEventMilestone,
  opts?: { row?: number; node?: number; bar?: number },
): { impactAt: number; impactRow?: number; impactNode?: number; impactBar?: number } {
  const out: ReturnType<typeof legacyImpactProps> = { impactAt: m.localImpactFrame };
  if (opts?.row !== undefined) out.impactRow = opts.row;
  if (opts?.node !== undefined) out.impactNode = opts.node;
  if (opts?.bar !== undefined) out.impactBar = opts.bar;
  return out;
}
