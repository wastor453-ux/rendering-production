import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import { H1Hook } from "./H1Hook";
import { H2Spike } from "./H2Spike";
import { H3Autopsy } from "./H3Autopsy";
import { H4Debt } from "./H4Debt";
import { H5Freeze } from "./H5Freeze";
import { H6Escape } from "./H6Escape";
import { H7Close } from "./H7Close";

export const FPS = 30;

// "The Housing Market Just Broke" — 12.7min VO, split at part pauses.
// Scene frames = VO seconds × 30 + ~30 padding.
const S1 = 2127; // 69.9s — hook
const S2 = 1626; // 53.2s — the spike
const S3 = 5448; // 180.6s — the autopsy
const S4 = 3603; // 119.1s — the debt spiral
const S5 = 3618; // 119.6s — the freeze
const S6 = 5574; // 184.8s — the escape
const S7 = 1155; // 37.5s — close
export const HB_TOTAL = S1 + S2 + S3 + S4 + S5 + S6 + S7; // 24151 = 13.4min

export const HousingBrokeVideo: React.FC = () => {
  let at = 0;
  const seq = (dur: number, audio: string) => {
    const s = at;
    at += dur;
    return { s, dur, audio };
  };
  const parts = [
    seq(S1, "audio/hb_p1.wav"),
    seq(S2, "audio/hb_p2.wav"),
    seq(S3, "audio/hb_p3.wav"),
    seq(S4, "audio/hb_p4.wav"),
    seq(S5, "audio/hb_p5.wav"),
    seq(S6, "audio/hb_p6.wav"),
    seq(S7, "audio/hb_p7.wav"),
  ];
  const Comps = [H1Hook, H2Spike, H3Autopsy, H4Debt, H5Freeze, H6Escape, H7Close];

  return (
    <AbsoluteFill style={{ background: "#0F0D24" }}>
      {parts.map((p, i) => {
        const Comp = Comps[i];
        return (
          <Sequence key={i} from={p.s} durationInFrames={p.dur}>
            <Comp />
          </Sequence>
        );
      })}
      {parts.map((p, i) => (
        <Sequence key={`a${i}`} from={p.s} durationInFrames={p.dur}>
          <Audio src={staticFile(p.audio)} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
