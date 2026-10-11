// FromScratch.tsx — From-scratch pipeline test composition (2026-10-11)
// Renders the 5-beat "If I Started Investing in 2026" video.
// Beat timeline: src/compiled_fromscratch/beat_timeline.json
// Audio: public/audio/fromscratch_beat*.wav

import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame } from "remotion";
import beatDoc from "../compiled_fromscratch/beat_timeline.json";

const FPS = 30;

function BeatCard({ beat }: { beat: any }) {
  const frame = useCurrentFrame();
  const opacity = Math.min(1, frame / 15);
  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0e1a", justifyContent: "center", alignItems: "center", opacity }}>
      <div style={{ textAlign: "center", padding: 80 }}>
        <div style={{ fontSize: 28, color: "#8892b0", letterSpacing: 4, marginBottom: 24 }}>
          WILLIAM ASTOR
        </div>
        <div style={{ fontSize: 72, color: "#ffffff", fontWeight: 800, marginBottom: 32, maxWidth: 1400 }}>
          {beat.headline}
        </div>
        <div style={{ fontSize: 32, color: "#a8b2d1", maxWidth: 1200 }}>
          {beat.body}
        </div>
        {beat.metric && (
          <div style={{ fontSize: 120, color: "#64ffda", fontWeight: 900, marginTop: 32 }}>
            {beat.metric.value}
            <div style={{ fontSize: 28, color: "#8892b0" }}>{beat.metric.label}</div>
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
}

export function FromScratch() {
  const beats = (beatDoc as any).beats || [];
  let currentFrame = 0;
  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0e1a" }}>
      {beats.map((beat: any, i: number) => {
        const startFrame = Math.round(beat.start_s * FPS);
        const durationFrames = Math.round(beat.duration_s * FPS);
        const el = (
          <Sequence key={beat.beat_id} from={startFrame} durationInFrames={durationFrames}>
            <BeatCard beat={beat} />
            <Audio src={staticFile(`audio/fromscratch_${beat.audio.replace("audio/", "")}`)} />
          </Sequence>
        );
        return el;
      })}
    </AbsoluteFill>
  );
}
