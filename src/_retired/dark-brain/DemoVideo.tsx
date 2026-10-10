import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import { Scene1Hook } from "./scenes/Scene1Hook";
import { Scene2Setup } from "./scenes/Scene2Setup";
import { Scene2bRate } from "./scenes/Scene2bRate";
import { Scene3Curve } from "./scenes/Scene3Curve";
import { Scene4TimeVsTiming } from "./scenes/Scene4TimeVsTiming";
import { Scene5Fees } from "./scenes/Scene5Fees";
import { Scene5bAutomate } from "./scenes/Scene5bAutomate";
import { Scene6Close } from "./scenes/Scene6Close";

export const FPS = 30;

// Scene durations in frames (audio length + ~1s breathing room)
const SCENES = [
  { name: "hook", Comp: Scene1Hook, audio: "scene1.mp3", frames: 221 },
  { name: "setup", Comp: Scene2Setup, audio: "scene2.mp3", frames: 342 },
  { name: "rate", Comp: Scene2bRate, audio: "scene2b.mp3", frames: 547 },
  { name: "curve", Comp: Scene3Curve, audio: "scene3.mp3", frames: 622 },
  { name: "timing", Comp: Scene4TimeVsTiming, audio: "scene4.mp3", frames: 655 },
  { name: "fees", Comp: Scene5Fees, audio: "scene5.mp3", frames: 424 },
  { name: "automate", Comp: Scene5bAutomate, audio: "scene5b.mp3", frames: 481 },
  { name: "close", Comp: Scene6Close, audio: "scene6.mp3", frames: 169 },
];

export const TOTAL_FRAMES = SCENES.reduce((a, s) => a + s.frames, 0);

export const DemoVideo: React.FC = () => {
  let from = 0;
  return (
    <AbsoluteFill style={{ background: "#070B12" }}>
      {SCENES.map(({ name, Comp, audio, frames }) => {
        const el = (
          <Sequence key={name} from={from} durationInFrames={frames} name={name}>
            <Comp />
            <Audio src={staticFile(`audio/${audio}`)} />
          </Sequence>
        );
        from += frames;
        return el;
      })}
    </AbsoluteFill>
  );
};
