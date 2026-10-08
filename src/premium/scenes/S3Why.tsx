import React from "react";
import { AbsoluteFill } from "remotion";
import { MeshBackground } from "../components/MeshBackground";
import { KineticHeadline, Toast } from "../components/Type";

/** S3 — Why it works. Three toasts, then the punchline. */
export const S3Why: React.FC = () => (
  <AbsoluteFill>
    <MeshBackground />
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", gap: 28 }}>
      <Toast delay={8} tone="info">No crash</Toast>
      <Toast delay={45} tone="info">No warning</Toast>
      <Toast delay={82} tone="warn">No headlines</Toast>
      <div style={{ marginTop: 40, textAlign: "center" }}>
        <KineticHeadline
          lines={["A slow leak is invisible —", "which is exactly why it works"]}
          delay={130}
          fontSize={72}
        />
      </div>
    </AbsoluteFill>
  </AbsoluteFill>
);
