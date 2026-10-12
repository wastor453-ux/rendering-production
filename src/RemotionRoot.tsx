import React from "react";
import { Composition } from "remotion";
import { SavingsTrap, SAVINGSTRAP_TOTAL } from "./videos/savings-trap/SavingsTrap";
import { CompoundInterest } from "./videos/compound-interest/CompoundInterest";
import { EmergencyFund } from "./videos/emergency-fund/EmergencyFund";
// DARK BRAIN REMOVED 2026-10-10: DemoVideo, StyleRefs, InflationRef retired (used src/theme.ts dark neon system)
// See _retired/dark-brain/ for archived files.
import { MoneyDyingVideo, MD_TOTAL, FPS as MD_FPS } from "./videos/moneydying/MoneyDying";
import { FinanceProof, PROOF_TOTAL } from "./videos/finance-proof/FinanceProof";
import { ProductionBeats, PRODUCTION_TOTAL } from "./videos/production-beats/ProductionBeats";
import { FromScratch } from "./videos/fromscratch/FromScratch";
import { FromScratchLight, FROMSCRATCH_LIGHT_TOTAL, FROMSCRATCH_LIGHT_FPS } from "./videos/fromscratch-light/FromScratchLight";

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
        id="SavingsTrap"
        component={SavingsTrap}
        durationInFrames={SAVINGSTRAP_TOTAL}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition id="CompoundInterest" component={CompoundInterest} durationInFrames={5400} fps={30} width={1920} height={1080} />
      <Composition id="EmergencyFund" component={EmergencyFund} durationInFrames={5400} fps={30} width={1920} height={1080} />
    </>
  );
};
