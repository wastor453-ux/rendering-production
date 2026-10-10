// materialTheme.tsx — MATERIAL A/B THEMING (test only)
//
// A = current Light Premium Fintech tokens (pixel-identical default).
// B = refined material: deeper atmospheric background, more opaque glass,
//     crisper thin border, stronger soft shadow. Still near-white/cool-gray,
//     blue/lavender only. No dark, no neon, no glow, no heavy gradients.
//
// Components read tokens via useMaterial(). With no provider, A is used —
// the production path is untouched.

import React from "react";
import { T as TOKENS_A } from "./tokens";

export type MaterialTokens = {
  canvas: string;
  blobOpacity: number;
  blobLavenderOpacity: number;
  blobBlueOpacity: number;
  blobPeachOpacity: number;
  glassFill: string;
  glassBorder: string;
  glassBorderWidth: number;
  glassShadow: string;
  /** Composition scale for the beat content (1.0 = current). Background stays full-bleed. */
  compositionScale: number;
};

export const MATERIAL_A: MaterialTokens = {
  canvas: TOKENS_A.canvas,
  blobOpacity: 0.55,
  blobLavenderOpacity: 0.5,
  blobBlueOpacity: 0.6,
  blobPeachOpacity: 0.28,
  glassFill: TOKENS_A.glassFill,
  glassBorder: TOKENS_A.glassBorder,
  glassBorderWidth: 1,
  glassShadow: `${TOKENS_A.glassShadow}, inset 0 1px 0 rgba(255,255,255,0.9)`,
  compositionScale: 1.0,
};

export const MATERIAL_B: MaterialTokens = {
  // near-white cool-gray, a touch deeper for atmospheric separation
  canvas: "#F3F6FB",
  blobOpacity: 0.62,
  blobLavenderOpacity: 0.68,
  blobBlueOpacity: 0.78,
  blobPeachOpacity: 0.30,
  // more opaque glass -> stronger card/background separation
  glassFill: "rgba(255,255,255,0.86)",
  // refined thin border: crisper edge, still 1px, still cool blue-gray
  glassBorder: "rgba(128,146,192,0.62)",
  glassBorderWidth: 1,
  // softer, deeper lift
  glassShadow: "0 26px 72px rgba(71,91,140,0.18), inset 0 1px 0 rgba(255,255,255,0.95)",
  compositionScale: 1.0,
};

const Ctx = React.createContext<MaterialTokens>(MATERIAL_B);
export const useMaterial = () => React.useContext(Ctx);
export const MaterialProvider: React.FC<{ material: MaterialTokens; children?: React.ReactNode }> =
  ({ material, children }) => <Ctx.Provider value={material}>{children}</Ctx.Provider>;

// Composition A/B (canonical Material B colors; scale is the ONLY variable).
export const COMP_A: MaterialTokens = { ...MATERIAL_B, compositionScale: 1.0 };
export const COMP_B: MaterialTokens = { ...MATERIAL_B, compositionScale: 1.28 };
