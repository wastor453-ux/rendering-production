import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import { PTScene1 } from "./scenes/PTScene1";
import { PTScene2 } from "./scenes/PTScene2";
import { PTScene3 } from "./scenes/PTScene3";
import { PTScene4 } from "./scenes/PTScene4";
import { PTScene5 } from "./scenes/PTScene5";
import { PTScene6 } from "./scenes/PTScene6";

export const FPS = 30;

// Pipeline stress test: 6 scenes x 150 frames = 900 frames = 30s.
// "The $10,000 Question" — exercises every phase of EDITING_BRAIN.md:
// chart draw + velocity swell, count-up snap, compare-card springs,
// bar cascade, stat grid, badge/logo overshoot impacts, camera moves,
// VO ducking, and the full quality gate.
const SCENES = [
  { name: "hook", Comp: PTScene1, frames: 150 },
  { name: "problem", Comp: PTScene2, frames: 150 },
  { name: "compare", Comp: PTScene3, frames: 150 },
  { name: "mechanism", Comp: PTScene4, frames: 150 },
  { name: "proof", Comp: PTScene5, frames: 150 },
  { name: "cta", Comp: PTScene6, frames: 150 },
];

export const PIPETEST_TOTAL = SCENES.reduce((a, s) => a + s.frames, 0); // 900

export const PipeTestVideo: React.FC = () => {
  let from = 0;
  return (
    <AbsoluteFill
      style={{ background: "#FAFAF8", fontFamily: "'Plus Jakarta Sans', sans-serif" }}
    >
      {SCENES.map(({ name, Comp, frames }) => {
        const el = (
          <Sequence key={name} from={from} durationInFrames={frames} name={name}>
            <Comp />
          </Sequence>
        );
        from += frames;
        return el;
      })}
      {/* deterministic master: VO + new-bench SFX + ducked roomtone, 30.0s */}
      <Audio src={staticFile("audio/pipetest-master.mp3")} />
    </AbsoluteFill>
  );
};
