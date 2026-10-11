// PipelineProbe.tsx — MINIMAL pipeline validation composition.
// Purpose: verify the render pipeline works end-to-end with a fresh,
// dependency-free composition. No audio, no JSON imports, no assets.
// If this renders but FromScratchLight doesn't, the bug is in FromScratchLight.
// If this also fails, the bug is in the pipeline itself.

import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";

const FPS = 30;
const DURATION_SECONDS = 5;

export const PIPELINEPROBE_TOTAL = Math.round(DURATION_SECONDS * FPS);
export const PIPELINEPROBE_FPS = FPS;

export const PipelineProbe: React.FC = () => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();

  // Simple animated background color
  const progress = frame / PIPELINEPROBE_TOTAL;
  const hue = Math.round(210 + progress * 60); // blue to purple shift

  return (
    <AbsoluteFill
      style={{
        backgroundColor: `hsl(${hue}, 60%, 15%)`,
        justifyContent: "center",
        alignItems: "center",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <div
        style={{
          color: "#FFFFFF",
          fontSize: Math.round(width * 0.06),
          fontFamily: "system-ui, sans-serif",
          fontWeight: 700,
          textAlign: "center",
        }}
      >
        PIPELINE PROBE
      </div>
      <div
        style={{
          color: "#88CCFF",
          fontSize: Math.round(width * 0.03),
          fontFamily: "system-ui, sans-serif",
          marginTop: 20,
        }}
      >
        Frame {frame} / {PIPELINEPROBE_TOTAL}
      </div>
    </AbsoluteFill>
  );
};
