import React from "react";
import { AbsoluteFill } from "remotion";
import { MeshBackground } from "../components/MeshBackground";
import { GlassCard } from "../components/GlassCard";
import { KineticHeadline } from "../components/Type";
import { P } from "../theme";

/** S4 — Takeaway. Monumental close + tagline card. */
export const S4Takeaway: React.FC = () => (
  <AbsoluteFill>
    <MeshBackground />
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", gap: 48 }}>
      <div style={{ textAlign: "center" }}>
        <KineticHeadline
          lines={["Money that moves,", "outruns inflation"]}
          accentWord="moves"
          delay={8}
          fontSize={104}
        />
      </div>
      <GlassCard delay={70} width={900}>
        <div style={{ textAlign: "center", fontFamily: P.font }}>
          <div style={{ fontWeight: 800, fontSize: 54, color: P.ink, letterSpacing: -1 }}>
            Wealth is a legacy.
          </div>
          <div
            style={{
              fontWeight: 800,
              fontSize: 54,
              letterSpacing: -1,
              background: `linear-gradient(90deg, ${P.purple}, ${P.magenta})`,
              WebkitBackgroundClip: "text",
              backgroundClip: "text",
              color: "transparent",
            }}
          >
            Build yours.
          </div>
        </div>
      </GlassCard>
    </AbsoluteFill>
  </AbsoluteFill>
);
