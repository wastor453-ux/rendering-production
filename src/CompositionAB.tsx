// CompositionAB.tsx — TEST ONLY: composition scale A/B.
//
// Both render the IDENTICAL production path (ProductionBeats, frames 540-1730,
// canonical Material B colors, same beats/events/milestones/timing).
// The ONLY variable is compositionScale:
//   CompositionA = 1.00 (current production composition)
//   CompositionB = 1.28 (enlarged focal objects, more canvas use)

import React from "react";
import { ProductionBeats, PRODUCTION_TOTAL } from "./ProductionBeats";
import { MaterialProvider, COMP_A, COMP_B } from "./light/materialTheme";

export const CompositionA: React.FC = () => (
  <MaterialProvider material={COMP_A}>
    <ProductionBeats />
  </MaterialProvider>
);

export const CompositionB: React.FC = () => (
  <MaterialProvider material={COMP_B}>
    <ProductionBeats />
  </MaterialProvider>
);

export const COMP_AB_TOTAL = PRODUCTION_TOTAL;
