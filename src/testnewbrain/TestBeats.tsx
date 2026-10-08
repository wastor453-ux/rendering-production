import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { MeshBackground } from "../premium/components/MeshBackground";
import { GlassCard } from "../premium/components/GlassCard";
import { KineticHeadline } from "../premium/components/Type";
import { P } from "../premium/theme";
import beatsData from "./beat_timeline.json";

const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const expo = Easing.bezier(0.16, 1, 0.3, 1);

type Beat = {
  id: string; start: number; end: number; verb: string; kind: string;
  title: string; sub: string; items?: string[]; left?: string; right?: string;
  title_frame?: number; sub_frame?: number; impact_lf?: number;
  card_frames?: number[]; cards_frames?: number[]; bar_lf?: [number, number];
};
const BEATS = (beatsData as { beats: Beat[] }).beats;
export const TEST_TOTAL = Math.ceil(111.1 * 30) + 30; // 3363

const useBeat = () => {
  const frame = useCurrentFrame();
  const t = frame / 30;
  const beat = BEATS.find((b) => t >= b.start && t < b.end) ?? BEATS[BEATS.length - 1];
  const local = frame - beat.start * 30;
  return { beat, local, frame };
};

const entry = (local: number) => {
  const p = interpolate(local, [0, 18], [0, 1], { ...CLAMP, easing: expo });
  return { opacity: p, y: interpolate(p, [0, 1], [46, 0], CLAMP) };
};

const Sub: React.FC<{ text: string; delay?: number; local: number }> = ({ text, local, delay = 14 }) => {
  if (!text) return null;
  return (
  <div style={{
    fontFamily: P.font, fontWeight: 600, fontSize: 30, color: P.muted, textAlign: "center",
    opacity: interpolate(local, [delay, delay + 12], [0, 1], CLAMP), marginTop: 20,
  }}>
    {text}
  </div>
  );
};

const HeadlineBeat: React.FC = () => {
  const { beat, local, frame } = useBeat();
  const { opacity, y } = entry(local);
  // KineticHeadline reads the global frame; shift its delay so the rise runs
  // beat-local (local 2..20) for every headline beat. b01 is unchanged.
  const startFrame = Math.round(beat.start * 30);
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity }}>
      <div style={{ transform: `translateY(${y}px)`, textAlign: "center", padding: "0 120px" }}>
        <div style={{ fontFamily: P.font, fontWeight: 800, fontSize: 26, letterSpacing: 10, color: P.neonBlue, marginBottom: 18 }}>
          {(beat as any).kicker ?? ""}
        </div>
        <KineticHeadline lines={[beat.title]} delay={(beat.title_frame ?? 20) - 18 - startFrame} fontSize={88} />
        <Sub text={beat.sub} local={local} delay={beat.sub_frame ?? 14} />
      </div>
    </AbsoluteFill>
  );
};

const NumberBeat: React.FC = () => {
  const { beat, local } = useBeat();
  const ilf = beat.impact_lf ?? 13;
  // slam: scale pulse peaks exactly at the event's visual impact frame
  const slam = interpolate(local, [ilf - 5, ilf, ilf + 11], [1, 1.14, 1], { ...CLAMP, easing: expo });
  const op = interpolate(local, [0, 10], [0, 1], CLAMP);
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: op }}>
      <div style={{ textAlign: "center", transform: `scale(${slam})` }}>
        <div style={{ fontFamily: P.font, fontWeight: 800, fontSize: 170, color: P.loss, letterSpacing: -4, fontVariantNumeric: "tabular-nums" }}>
          {beat.title}
        </div>
        <Sub text={beat.sub} local={local} delay={beat.sub_frame ?? 14} />
      </div>
    </AbsoluteFill>
  );
};

const BarFallBeat: React.FC = () => {
  const { local, beat } = useBeat();
  const [bf0, bf1] = beat.bar_lf ?? [10, 120];
  const p = interpolate(local, [bf0, bf1], [0, 1], { ...CLAMP, easing: expo });
  const op = interpolate(local, [0, 10], [0, 1], CLAMP);
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: op }}>
      <div style={{ textAlign: "center" }}>
        <div style={{ fontFamily: P.font, fontWeight: 800, fontSize: 64, color: P.ink, marginBottom: 30 }}>{beat.title}</div>
        <div style={{ width: 800, height: 60, background: "rgba(56,189,248,0.15)", borderRadius: 18, overflow: "hidden" }}>
          <div style={{ width: `${(1 - p * 0.85) * 100}%`, height: "100%", background: `linear-gradient(90deg, ${P.neonBlue}, ${P.loss})`, borderRadius: 18 }} />
        </div>
        <Sub text={beat.sub} local={local} />
      </div>
    </AbsoluteFill>
  );
};

const CascadeBeat: React.FC = () => {
  const { beat, local } = useBeat();
  const op = interpolate(local, [0, 10], [0, 1], CLAMP);
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", gap: 22, opacity: op }}>
      <div style={{ fontFamily: P.font, fontWeight: 800, fontSize: 56, color: P.ink, marginBottom: 10 }}>{beat.title}</div>
      {(beat.items ?? []).map((it, i) => {
        const cf = (beat.card_frames ?? [])[i] ?? (12 + i * 22);
        const d = cf - 14;
        const p = interpolate(local, [d, cf], [0, 1], { ...CLAMP, easing: expo });
        return (
          <div key={it} style={{ opacity: p, transform: `translateY(${interpolate(p, [0, 1], [30, 0], CLAMP)}px)` }}>
            <GlassCard width={760} delay={0}>
              <div style={{ fontFamily: P.font, fontWeight: 700, fontSize: 36, color: P.ink, textAlign: "center", padding: "6px 12px" }}>
                {it} <span style={{ color: P.loss }}>↗</span>
              </div>
            </GlassCard>
          </div>
        );
      })}
      <Sub text={beat.sub} local={local} delay={80} />
    </AbsoluteFill>
  );
};

const SplitBeat: React.FC = () => {
  const { beat, local } = useBeat();
  const op = interpolate(local, [0, 10], [0, 1], CLAMP);
  const tf = beat.title_frame ?? 10;
  const tp = interpolate(local, [tf - 10, tf], [0, 1], { ...CLAMP, easing: expo });
  const cfs = beat.cards_frames ?? [38];
  const lp = interpolate(local, [cfs[0] - 16, cfs[0]], [0, 1], { ...CLAMP, easing: expo });
  const rp = interpolate(local, [(cfs[1] ?? cfs[0]) - 16, cfs[1] ?? cfs[0]], [0, 1], { ...CLAMP, easing: expo });
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: op }}>
      <div style={{ textAlign: "center" }}>
        <div style={{ fontFamily: P.font, fontWeight: 800, fontSize: 72, color: P.gold, marginBottom: 8, opacity: tp }}>{beat.title}</div>
        <Sub text={beat.sub} local={local} delay={beat.sub_frame ?? 14} />
        <div style={{ display: "flex", gap: 28, marginTop: 36, justifyContent: "center" }}>
          <div style={{ opacity: lp, transform: `translateX(${interpolate(lp, [0, 1], [-40, 0], CLAMP)}px)` }}>
            <GlassCard width={460} delay={0}>
              <div style={{ fontFamily: P.font, fontWeight: 800, fontSize: 38, color: P.gain, textAlign: "center", padding: "10px" }}>{beat.left}</div>
            </GlassCard>
          </div>
          <div style={{ opacity: rp, transform: `translateX(${interpolate(rp, [0, 1], [40, 0], CLAMP)}px)` }}>
            <GlassCard width={460} delay={0}>
              <div style={{ fontFamily: P.font, fontWeight: 800, fontSize: 38, color: P.loss, textAlign: "center", padding: "10px" }}>{beat.right}</div>
            </GlassCard>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

const CloseBeat: React.FC = () => {
  const { local } = useBeat();
  const op = interpolate(local, [0, 14], [0, 1], CLAMP);
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: op }}>
      <div style={{ textAlign: "center" }}>
        <div style={{ fontFamily: P.font, fontWeight: 800, fontSize: 64, color: P.ink }}>Wealth is a legacy.</div>
        <div style={{
          fontFamily: P.font, fontWeight: 800, fontSize: 64,
          background: `linear-gradient(90deg, ${P.purple}, ${P.magenta})`,
          WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent",
        }}>
          Build yours.
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const TestNewBrainVideo: React.FC = () => {
  const { beat } = useBeat();
  return (
    <AbsoluteFill style={{ background: "#0F0D24" }}>
      <MeshBackground />
      {beat.kind === "headline" && <HeadlineBeat />}
      {beat.kind === "number" && <NumberBeat />}
      {beat.kind === "barfall" && <BarFallBeat />}
      {beat.kind === "cascade" && <CascadeBeat />}
      {beat.kind === "split" && <SplitBeat />}
      {beat.kind === "close" && <CloseBeat />}
    </AbsoluteFill>
  );
};
