import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import { MD1Hook } from "./MD1Hook";
import { MD2Math } from "./MD2Math";
import { MD3Why } from "./MD3Why";
import { MD4Takeaway } from "./MD4Takeaway";

export const FPS = 30;

// "Your Money Is Dying While You Sleep" — 73.3s VO, split at scene pauses.
// Scene frames = VO seconds × 30 + ~30 padding.
const S1 = 450; // 14.0s VO — hook
const S2 = 798; // 25.6s VO — the autopsy (36-year decay)
const S3 = 495; // 15.5s VO — why it works
const S4 = 579; // 18.3s VO — the fix
export const MD_TOTAL = S1 + S2 + S3 + S4; // 2322 frames = 77.4s

export const MoneyDyingVideo: React.FC = () => {
  let at = 0;
  const seq = (dur: number, audio: string) => {
    const s = at;
    at += dur;
    return { s, dur, audio };
  };
  const a = seq(S1, "audio/md_s1.wav");
  const b = seq(S2, "audio/md_s2.wav");
  const c = seq(S3, "audio/md_s3.wav");
  const d = seq(S4, "audio/md_s4.wav");

  return (
    <AbsoluteFill style={{ background: "#F8FAFF" }}>
      {/* P4.4 migration: light canvas (#F8FAFF), was dark #0F0D24 */}
      <Sequence from={a.s} durationInFrames={a.dur}><MD1Hook /></Sequence>
      <Sequence from={b.s} durationInFrames={b.dur}><MD2Math /></Sequence>
      <Sequence from={c.s} durationInFrames={c.dur}><MD3Why /></Sequence>
      <Sequence from={d.s} durationInFrames={d.dur}><MD4Takeaway /></Sequence>
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
