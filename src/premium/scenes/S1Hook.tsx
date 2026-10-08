import React from "react";
import { AbsoluteFill } from "remotion";
import { MeshBackground } from "../components/MeshBackground";
import { KineticHeadline } from "../components/Type";
import { P } from "../theme";

/** S1 — Hook. Headline + kicker over the mesh. Nothing else. */
export const S1Hook: React.FC = () => (
  <AbsoluteFill>
    <MeshBackground />
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", gap: 32 }}>
      <div style={{ fontFamily: P.font, fontWeight: 800, fontSize: 30, letterSpacing: 14, color: P.neonBlue }}>
        THE SLOW LEAK
      </div>
      <div style={{ textAlign: "center" }}>
        <KineticHeadline
          lines={["Your savings account", "is LYING to you"]}
          accentWord="LYING"
          delay={10}
          fontSize={110}
        />
      </div>
    </AbsoluteFill>
  </AbsoluteFill>
);
