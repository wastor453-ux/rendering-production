import React from "react";
import { Composition } from "remotion";
// DARK BRAIN REMOVED 2026-10-10: DemoVideo, StyleRefs, InflationRef retired (used src/theme.ts dark neon system)
// See _retired/dark-brain/ for archived files.
import { MoneyDyingVideo, MD_TOTAL, FPS as MD_FPS } from "./moneydying/MoneyDying";
import { VisualShowcase, SHOWCASE_TOTAL } from "./light/Showcase";
import { FinanceProof, PROOF_TOTAL } from "./FinanceProof";
import { ProductionBeats, PRODUCTION_TOTAL } from "./ProductionBeats";
import { FromScratch } from "./FromScratch";
import { FromScratchLight, FROMSCRATCH_LIGHT_TOTAL, FROMSCRATCH_LIGHT_FPS } from "./FromScratchLight";
import { P3Rehearsal, P3_TOTAL } from "./P3Rehearsal";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* DARK BRAIN REMOVED: DemoVideo, StyleRefs, InflationRef retired 2026-10-10 */}
{/* P4.4: PremiumTest retired 2026-10-09 — old dark brain */}
      {/* P4.4: TestNewBrain retired 2026-10-09 — used old dark brain, beat compiler does not exist */}
      <Composition
        id="MoneyDying"
        component={MoneyDyingVideo}
        durationInFrames={MD_TOTAL}
        fps={MD_FPS}
        width={1920}
        height={1080}
      />
      {/* ISOLATED VISUAL CALIBRATION - Phase 1B, temporary */}
<Composition
        id="FinanceProof"
        component={FinanceProof}
        durationInFrames={PROOF_TOTAL}
        fps={30}
        width={1920}
        height={1080}
      />
<Composition
        id="ProductionBeats"
        component={ProductionBeats}
        durationInFrames={PRODUCTION_TOTAL}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="FromScratch"
        component={FromScratch}
        durationInFrames={2709}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="FromScratchLight"
        component={FromScratchLight}
        durationInFrames={FROMSCRATCH_LIGHT_TOTAL}
        fps={FROMSCRATCH_LIGHT_FPS}
        width={1920}
        height={1080}
      />
      <Composition
        id="P3Rehearsal"
        component={P3Rehearsal}
        durationInFrames={P3_TOTAL}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="VisualShowcase"
        component={VisualShowcase}
        durationInFrames={SHOWCASE_TOTAL}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
