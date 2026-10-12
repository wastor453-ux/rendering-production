// materialTheme.tsx — Visual System v2.0 (from Hamza's A-to-Z Package)
// Updated 2026-10-12: matches new tokens (Navy #102044, Blue #3478F6, Inter font)
//
// MATERIAL A = Visual System v2.0 (production default)
// MATERIAL B = Refined atmospheric (deeper blooms, more opaque glass)

import React from "react";
import { T as TOKENS } from "./tokens";

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
  compositionScale: number;
};

export const MATERIAL_A: MaterialTokens = {
  canvas: "linear-gradient(135deg, #F8FBFF 0%, #F1F6FF 48%, #EFEDFF 100%)",
  blobOpacity: 1.0,
  blobLavenderOpacity: TOKENS.bloomLavenderOpacity,
  blobBlueOpacity: TOKENS.bloomBlueOpacity,
  blobPeachOpacity: 0, // Removed: peach not in v2.0 palette
  glassFill: TOKENS.glassFill,
  glassBorder: TOKENS.glassBorder,
  glassBorderWidth: 1,
  glassShadow: TOKENS.glassShadow,
  compositionScale: 1.0,
};

export const MATERIAL_B: MaterialTokens = {
  canvas: "linear-gradient(135deg, #F8FBFF 0%, #F1F6FF 48%, #EFEDFF 100%)",
  blobOpacity: 1.0,
  blobLavenderOpacity: 0.20,
  blobBlueOpacity: 0.28,
  blobPeachOpacity: 0,
  glassFill: "rgba(255,255,255,0.92)",
  glassBorder: "rgba(216,230,250,0.80)",
  glassBorderWidth: 1,
  glassShadow: "0 12px 36px rgba(40,85,170,0.10), inset 0 1px 0 rgba(255,255,255,0.95)",
  compositionScale: 1.0,
};

const Ctx = React.createContext<MaterialTokens>(MATERIAL_A);
export const useMaterial = () => React.useContext(Ctx);
export const MaterialProvider: React.FC<{ material: MaterialTokens; children?: React.ReactNode }> =
  ({ material, children }) => <Ctx.Provider value={material}>{children}</Ctx.Provider>;

// Composition A/B (scale is the ONLY variable).
export const COMP_A: MaterialTokens = { ...MATERIAL_A, compositionScale: 1.0 };
export const COMP_B: MaterialTokens = { ...MATERIAL_A, compositionScale: 1.28 };
