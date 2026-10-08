// MaterialAB.tsx — TEST ONLY: material/background A/B.
//
// Both render the IDENTICAL production path (ProductionBeats, frames 540-1730,
// same beats/events/milestones/timing). The ONLY difference is the material
// theme provided via context:
//   MaterialA = current system (pixel-identical default)
//   MaterialB = refined Light Premium Fintech material

import React from "react";
import { ProductionBeats, PRODUCTION_TOTAL } from "./ProductionBeats";
import { MaterialProvider, MATERIAL_A, MATERIAL_B } from "./light/materialTheme";

export const MaterialA: React.FC = () => (
  <MaterialProvider material={MATERIAL_A}>
    <ProductionBeats />
  </MaterialProvider>
);

export const MaterialB: React.FC = () => (
  <MaterialProvider material={MATERIAL_B}>
    <ProductionBeats />
  </MaterialProvider>
);

export const MATERIAL_AB_TOTAL = PRODUCTION_TOTAL;
