import React from "react";
import { Composition } from "remotion";
// DARK BRAIN REMOVED 2026-10-10: DemoVideo, StyleRefs, InflationRef retired (used src/theme.ts dark neon system)
// See _retired/dark-brain/ for archived files.
import { TrialVideo, TRIAL_TOTAL } from "./trial/TrialVideo";
import { StressTest, STRESS_TOTAL } from "./stress/StressTest";
import { PipeTestVideo, PIPETEST_TOTAL } from "./pipetest/PipeTest";
import { HysaTest, HYSA_TOTAL } from "./hysa/HysaTest";
import { BankTestVideo, BANKTEST_TOTAL } from "./banktest/BankTestVideo";
import { RecutVideo, RECUT_TOTAL, FPS as RECUT_FPS } from "./recut/RecutVideo";
import { MoneyDyingVideo, MD_TOTAL, FPS as MD_FPS } from "./moneydying/MoneyDying";
import { HousingBrokeVideo, HB_TOTAL, FPS as HB_FPS } from "./housing/HousingBroke";
import { VisualShowcase, SHOWCASE_TOTAL } from "./light/Showcase";
import { FinanceProof, PROOF_TOTAL } from "./FinanceProof";
import { ProductionBeats, PRODUCTION_TOTAL } from "./ProductionBeats";
import { P3Rehearsal, P3_TOTAL } from "./P3Rehearsal";
import { B6A, B6B, B6A_TOTAL } from "./B6Arbitration";
import { CalibrationV0, CalibrationV1, CalibrationV2, CalibrationV3 } from "./test/VisualCalibration";
import { ChainTest, CHAINTEST_TOTAL } from "./ChainTest";
import { MaterialA, MaterialB, MATERIAL_AB_TOTAL } from "./MaterialAB";
import { CompositionA, CompositionB, COMP_AB_TOTAL } from "./CompositionAB";
import { ModeRegression, MODE_REGRESSION_TOTAL } from "./ModeRegression";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* DARK BRAIN REMOVED: DemoVideo, StyleRefs, InflationRef retired 2026-10-10 */}
      <Composition
        id="TrialVideo"
        component={TrialVideo}
        durationInFrames={TRIAL_TOTAL}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="StressTest"
        component={StressTest}
        durationInFrames={STRESS_TOTAL}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="PipeTestVideo"
        component={PipeTestVideo}
        durationInFrames={PIPETEST_TOTAL}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="HysaTest"
        component={HysaTest}
        durationInFrames={HYSA_TOTAL}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="BankTestVideo"
        component={BankTestVideo}
        durationInFrames={BANKTEST_TOTAL}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="RecutVideo"
        component={RecutVideo}
        durationInFrames={RECUT_TOTAL}
        fps={RECUT_FPS}
        width={1920}
        height={1080}
      />
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
      <Composition
        id="HousingBroke"
        component={HousingBrokeVideo}
        durationInFrames={HB_TOTAL}
        fps={HB_FPS}
        width={1920}
        height={1080}
      />
      {/* ISOLATED VISUAL CALIBRATION - Phase 1B, temporary */}
      <Composition id="CalibrationV0" component={CalibrationV0} durationInFrames={300} fps={30} width={1920} height={1080} />
      <Composition id="CalibrationV1" component={CalibrationV1} durationInFrames={300} fps={30} width={1920} height={1080} />
      <Composition id="CalibrationV2" component={CalibrationV2} durationInFrames={300} fps={30} width={1920} height={1080} />
      <Composition id="CalibrationV3" component={CalibrationV3} durationInFrames={300} fps={30} width={1920} height={1080} />
      <Composition
        id="FinanceProof"
        component={FinanceProof}
        durationInFrames={PROOF_TOTAL}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="B6A"
        component={B6A}
        durationInFrames={B6A_TOTAL}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="B6B"
        component={B6B}
        durationInFrames={B6A_TOTAL}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="ChainTest"
        component={ChainTest}
        durationInFrames={CHAINTEST_TOTAL}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="MaterialA"
        component={MaterialA}
        durationInFrames={MATERIAL_AB_TOTAL}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="MaterialB"
        component={MaterialB}
        durationInFrames={MATERIAL_AB_TOTAL}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="CompositionA"
        component={CompositionA}
        durationInFrames={COMP_AB_TOTAL}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="CompositionB"
        component={CompositionB}
        durationInFrames={COMP_AB_TOTAL}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="ModeRegression"
        component={ModeRegression}
        durationInFrames={MODE_REGRESSION_TOTAL}
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
