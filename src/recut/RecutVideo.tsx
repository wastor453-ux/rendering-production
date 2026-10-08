import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame, interpolate } from "remotion";
import { CLAMP } from "./presets";
import { Beat1, Beat2, Beat3 } from "./BeatsA";
import { Beat4, Beat5, Beat6 } from "./BeatsB";
import { Beat7, Beat8, Beat9 } from "./BeatsC";
import { Beat10, Beat11, Beat12 } from "./BeatsD";

export const FPS = 30;
export const RECUT_TOTAL = 5400; // 180s

// Beat start frames (from STORYBOARD_RECUT.md)
const BEATS: { start: number; dur: number; Comp: React.FC }[] = [
  { start: 0, dur: 195, Comp: Beat1 },
  { start: 195, dur: 258, Comp: Beat2 },
  { start: 453, dur: 471, Comp: Beat3 },
  { start: 924, dur: 246, Comp: Beat4 },
  { start: 1170, dur: 618, Comp: Beat5 },
  { start: 1788, dur: 648, Comp: Beat6 },
  { start: 2436, dur: 666, Comp: Beat7 },
  { start: 3102, dur: 114, Comp: Beat8 },
  { start: 3216, dur: 678, Comp: Beat9 },
  { start: 3894, dur: 834, Comp: Beat10 },
  { start: 4728, dur: 255, Comp: Beat11 },
  { start: 4983, dur: 417, Comp: Beat12 },
];

const FADE = 12; // 0.4s gradient crossfade between beats

const BeatWithFade: React.FC<{ start: number; dur: number; Comp: React.FC; first?: boolean }> = ({ start, dur, Comp, first }) => {
  const frame = useCurrentFrame();
  const from = first ? start : start - FADE;
  const local = frame - from;
  const opacity = first ? 1 : interpolate(local, [0, FADE], [0, 1], { ...CLAMP });
  if (frame < from || frame >= start + dur) return null;
  return (
    <AbsoluteFill style={{ opacity }}>
      <Sequence from={from} durationInFrames={dur + (first ? 0 : FADE)}>
        <Comp />
      </Sequence>
    </AbsoluteFill>
  );
};

export const RecutVideo: React.FC = () => {
  return (
    <AbsoluteFill style={{ background: "#FAFAF8" }}>
      {BEATS.map((b, i) => (
        <BeatWithFade key={i} start={b.start} dur={b.dur} Comp={b.Comp} first={i === 0} />
      ))}
      <Audio src={staticFile("audio/VO_3MIN.mp3")} />
    </AbsoluteFill>
  );
};
