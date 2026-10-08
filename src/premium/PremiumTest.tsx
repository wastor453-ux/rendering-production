import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import { S1Hook } from "./scenes/S1Hook";
import { S2Math } from "./scenes/S2Math";
import { S3Why } from "./scenes/S3Why";
import { S4Takeaway } from "./scenes/S4Takeaway";

export const FPS = 30;

// Measured from the single enhanced take (vo_full_enhanced.wav, 44.45s),
// split at inter-scene pauses + ~1s padding per scene
const S1 = 317; // 9.55s VO
const S2 = 471; // 14.69s VO
const S3 = 321; // 9.71s VO
const S4 = 345; // 10.50s VO
export const TOTAL = S1 + S2 + S3 + S4;

export const PremiumTest: React.FC = () => {
  let at = 0;
  const seq = (dur: number, audio: string) => {
    const s = at;
    at += dur;
    return { s, dur, audio };
  };
  const a = seq(S1, "audio/vo_s1_enhanced.wav");
  const b = seq(S2, "audio/vo_s2_enhanced.wav");
  const c = seq(S3, "audio/vo_s3_enhanced.wav");
  const d = seq(S4, "audio/vo_s4_enhanced.wav");

  return (
    <AbsoluteFill>
      <Sequence from={a.s} durationInFrames={a.dur}><S1Hook /></Sequence>
      <Sequence from={b.s} durationInFrames={b.dur}><S2Math /></Sequence>
      <Sequence from={c.s} durationInFrames={c.dur}><S3Why /></Sequence>
      <Sequence from={d.s} durationInFrames={d.dur}><S4Takeaway /></Sequence>
      <Sequence from={a.s} durationInFrames={a.dur}>
        <Audio src={staticFile(a.audio)} />
      </Sequence>
      <Sequence from={b.s} durationInFrames={b.dur}>
        <Audio src={staticFile(b.audio)} />
      </Sequence>
      <Sequence from={c.s} durationInFrames={c.dur}>
        <Audio src={staticFile(c.audio)} />
      </Sequence>
      <Sequence from={d.s} durationInFrames={d.dur}>
        <Audio src={staticFile(d.audio)} />
      </Sequence>
    </AbsoluteFill>
  );
};
