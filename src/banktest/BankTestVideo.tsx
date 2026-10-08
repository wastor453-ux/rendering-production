import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import { BankScene1 } from "./BankScene1";
import { BankScene2 } from "./BankScene2";
import { BankScene3 } from "./BankScene3";
import { BankScene4 } from "./BankScene4";
import { BankScene5 } from "./BankScene5";

export const FPS = 30;

// 180s pipeline test: 30s / 25s / 26s / 42s / 57s
const SCENES = [
  { name: "hook", Comp: BankScene1, frames: 900 },
  { name: "lending", Comp: BankScene2, frames: 750 },
  { name: "fractional", Comp: BankScene3, frames: 780 },
  { name: "bankrun", Comp: BankScene4, frames: 1260 },
  { name: "fineprint", Comp: BankScene5, frames: 1710 },
];

export const BANKTEST_TOTAL = SCENES.reduce((a, s) => a + s.frames, 0); // 5400

export const BankTestVideo: React.FC = () => {
  let from = 0;
  return (
    <AbsoluteFill style={{ background: "#FAFAF8", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
      {SCENES.map(({ name, Comp, frames }) => {
        const el = (
          <Sequence key={name} from={from} durationInFrames={frames} name={name}>
            <Comp />
          </Sequence>
        );
        from += frames;
        return el;
      })}
      <Audio src={staticFile("audio/banktest-vo.mp3")} />
    </AbsoluteFill>
  );
};
