import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import { TrialScene1 } from "./scenes/TrialScene1";
import { TrialScene2 } from "./scenes/TrialScene2";
import { TrialScene3 } from "./scenes/TrialScene3";
import { TrialScene4 } from "./scenes/TrialScene4";

export const FPS = 30;

// Fixed 30-second timeline: 6s / 9s / 9s / 6s
const SCENES = [
  { name: "problem", Comp: TrialScene1, audio: "trial1.mp3", frames: 180 },
  { name: "plan", Comp: TrialScene2, audio: "trial2.mp3", frames: 270 },
  { name: "engine", Comp: TrialScene3, audio: "trial3.mp3", frames: 270 },
  { name: "cta", Comp: TrialScene4, audio: "trial4.mp3", frames: 180 },
];

export const TRIAL_TOTAL = SCENES.reduce((a, s) => a + s.frames, 0); // 900

export const TrialVideo: React.FC = () => {
  let from = 0;
  return (
    <AbsoluteFill style={{ background: "#FAFAF8", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
      {SCENES.map(({ name, Comp, audio, frames }) => {
        const el = (
          <Sequence key={name} from={from} durationInFrames={frames} name={name}>
            <Comp />
          </Sequence>
        );
        from += frames;
        return el;
      })}
      {/* single deterministic master: VO + pro SFX + ducked roomtone, 30.0s */}
      <Audio src={staticFile("audio/trial-master.mp3")} />
    </AbsoluteFill>
  );
};
