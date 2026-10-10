// layout.ts — LAYOUT SYSTEM (VISUAL_BRAIN §10/§11)
//
// The brain demands: consistent grid rhythm, clear alignment axes,
// left-aligned text when more natural, fixed card tiers.
// This module is the single source of truth for scene layout.
// Every scene MUST use these values — no ad-hoc widths or alignments.

import { T } from "./tokens";

/** Card width tiers. Scenes pick a tier, never an arbitrary pixel width. */
export const CARD_W = {
  /** Narrow: single metric, toast, small callout */
  S: 640,
  /** Standard: charts, comparisons, most beats */
  M: 960,
  /** Wide: dashboards, full-bleed data stories */
  L: 1280,
} as const;

/** Page geometry (1920x1080). */
export const PAGE = {
  width: 1920,
  height: 1080,
  /** Side margin — all content aligns to this axis */
  marginX: 160,
  /** Vertical rhythm */
  marginTop: 120,
  marginBottom: 120,
  gapSection: 48,
  gapCard: 32,
  gapTight: 16,
} as const;

/**
 * Text alignment law (VISUAL_BRAIN §10):
 * - Hero/claim text: LEFT aligned (per approved reference)
 * - Centered ONLY for: single hero numbers, closing thesis, symmetric comparisons
 * - Never center paragraphs of supporting copy
 */
export const ALIGN = {
  hero: "left" as const,
  supporting: "left" as const,
  heroNumber: "center" as const,
  closing: "center" as const,
  comparison: "center" as const,
};

/**
 * Vertical placement law:
 * - Primary content: vertically centered as a group
 * - Kicker/label: above the hero, left-aligned to the same axis
 * - Supporting card: below the hero, same left axis
 * Text does NOT jump between top and bottom between beats.
 */
export const PLACEMENT = {
  /** Content block is centered vertically; internal order is kicker → hero → supporting */
  flow: "kicker-hero-supporting" as const,
} as const;
