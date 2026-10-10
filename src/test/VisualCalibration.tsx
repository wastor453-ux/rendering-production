/**
 * ISOLATED VISUAL CALIBRATION TEST - Phase 1B
 * 
 * Temporary test composition. Does NOT modify production files.
 * Renders H1 f180 with 4 material variants for visual comparison.
 * 
 * V0: Current MATERIAL_B (baseline)
 * V1: Stronger canvas (#E7EBFB candidate), cards unchanged
 * V2: Current canvas, 2-3px border, stronger shadow, tinted card fill
 * V3: V1 + V2 combined
 */

import React from "react";
import { AbsoluteFill } from "remotion";
import { MaterialProvider, MATERIAL_B, MaterialTokens } from "../light/materialTheme";
import { H1Hook } from "../housing/H1Hook";

// V0: Baseline (current MATERIAL_B, unchanged)
const V0: MaterialTokens = { ...MATERIAL_B };

// V1: Stronger, more uniform cool lavender canvas; cards unchanged
const V1: MaterialTokens = {
  ...MATERIAL_B,
  canvas: "#E7EBFB", // candidate, NOT approved
  blobOpacity: 0.85,
  blobLavenderOpacity: 0.90,
  blobBlueOpacity: 0.95,
  blobPeachOpacity: 0.40,
};

// V2: Current canvas; visible 2-3px edge, stronger shadow, cool-tinted fill
const V2: MaterialTokens = {
  ...MATERIAL_B,
  glassFill: "rgba(244,245,253,0.94)", // subtle cool tint
  glassBorder: "rgba(128,146,192,0.85)",
  glassBorderWidth: 2, // 2px visible edge band
  glassShadow: "0 32px 80px rgba(71,91,140,0.28), 0 8px 24px rgba(71,91,140,0.15), inset 0 1px 0 rgba(255,255,255,0.95)",
};

// V3: V1 + V2 combined
const V3: MaterialTokens = {
  ...V1,
  glassFill: V2.glassFill,
  glassBorder: V2.glassBorder,
  glassBorderWidth: V2.glassBorderWidth,
  glassShadow: V2.glassShadow,
};

const VariantFrame: React.FC<{ material: MaterialTokens }> = ({ material }) => (
  <AbsoluteFill>
    <MaterialProvider material={material}>
      <H1Hook />
    </MaterialProvider>
  </AbsoluteFill>
);

// Four isolated compositions, one per variant
// Each renders a single frame (f180) for still extraction
export const CalibrationV0: React.FC = () => <VariantFrame material={V0} />;
export const CalibrationV1: React.FC = () => <VariantFrame material={V1} />;
export const CalibrationV2: React.FC = () => <VariantFrame material={V2} />;
export const CalibrationV3: React.FC = () => <VariantFrame material={V3} />;
