// ModeRegression.tsx — TEST ONLY: 23-mode composition regression.
//
// Renders all 23 production visual modes (fixtures from Showcase) through:
//   Material B colors + 1.28x composition scale (COMP_B)
// Each mode gets a 90-frame slot; settled state ~frame 75.
// The selector determinism check runs separately in test_mode_selector.ts.

import React from "react";
import { Sequence } from "remotion";
import { LightCanvas } from "./light/primitives";
import { MaterialProvider, COMP_B, useMaterial } from "./light/materialTheme";
import { resolveScale } from "./light/compositionScale";
import { SHOWCASE_MODES } from "./light/Showcase";

export const MODE_SLOT = 90;

const ScaledCenter: React.FC<{ mode: string; children?: React.ReactNode }> = ({ mode, children }) => {
  const { compositionScale: requested } = useMaterial();
  const scale = resolveScale(mode, requested).effective_scale;
  return (
    <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", transform: `scale(${scale})` }}>{children}</div>
    </div>
  );
};

export const ModeRegression: React.FC = () => (
  <MaterialProvider material={COMP_B}>
    <>
      {SHOWCASE_MODES.map((m, i) => (
        <Sequence key={m.id} from={i * MODE_SLOT} durationInFrames={MODE_SLOT} name={m.id}>
          <LightCanvas>
            <ScaledCenter mode={m.id}>{m.el}</ScaledCenter>
          </LightCanvas>
        </Sequence>
      ))}
    </>
  </MaterialProvider>
);

export const MODE_REGRESSION_TOTAL = SHOWCASE_MODES.length * MODE_SLOT;
export const MODE_IDS = SHOWCASE_MODES.map((m) => m.id);
