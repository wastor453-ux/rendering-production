// Editorial modes: hero typography, hero number, thesis/closing compositions,
// real-world imagery + glass overlay.
import React from "react";
import { Easing, interpolate, staticFile, useCurrentFrame, Img } from "remotion";
import { T, CLAMP, EXPO } from "./tokens";
import { GlassCard, Kicker, CountUp, Delta, entry } from "./primitives";
import { useMaterial } from "./materialTheme";
import { LineChart } from "./charts";
import { resolveScale } from "./compositionScale";

const expo = Easing.bezier(...EXPO);

export const HeroTypography: React.FC<{
  kicker: string; lines: string[]; accentLine?: number; align?: "left" | "center";
  supporting?: string; supportingDelay?: number;
}> = ({
  kicker, lines, accentLine = -1, align = "left", supporting, supportingDelay = 28,
}) => {
  const frame = useCurrentFrame();
  // Q004 defect 2026-10-10: 104px clips long headlines at the canvas edge
  // ("Three forces hit at once" lost its "T"). Scale by longest line:
  // >22 chars -> 80px, >18 -> 88px, else 104px. Conservative to guarantee
  // PAGE.marginX clearance at 1920px wide.
  const maxLen = Math.max(...lines.map((l) => l.length), 0);
  const fontSize = maxLen > 22 ? 80 : maxLen > 18 ? 88 : 104;
  // Supporting line fades in after the headline entrance settles, preventing
  // mid-entrance overlap (Q004 defect 2026-10-10).
  const sP = supporting
    ? interpolate(frame, [supportingDelay, supportingDelay + 12], [0, 1], { ...CLAMP, easing: expo })
    : 0;
  return (
    <div style={{ textAlign: align, padding: align === "center" ? "0 140px" : "0" }}>
      <div style={{ opacity: interpolate(frame, [0, 12], [0, 1], CLAMP), marginBottom: 26 }}>
        <Kicker text={kicker} />
      </div>
      {lines.map((ln, i) => {
        const d = 8 + i * 10;
        const p = interpolate(frame, [d, d + 16], [0, 1], { ...CLAMP, easing: expo });
        const isAccent = i === accentLine;
        return (
          <div key={ln} style={{
            opacity: p, transform: `translateY(${interpolate(p, [0, 1], [44, 0], CLAMP)}px)`,
            fontFamily: T.font, fontWeight: 800, fontSize, lineHeight: 1.12, letterSpacing: -2,
            color: isAccent ? T.primary : T.ink,
          }}>
            {ln}
          </div>
        );
      })}
      {supporting && (
        <div style={{
          opacity: sP,
          fontFamily: T.font, fontWeight: 600, fontSize: 34,
          color: T.inkMuted, marginTop: 24, textAlign: align === "center" ? "center" : "left",
        }}>
          {supporting}
        </div>
      )}
    </div>
  );
};

export const HeroNumber: React.FC<{
  kicker: string; value: number; prefix?: string; suffix?: string; decimals?: number; delta?: number; caption: string;
  impactAt?: number;
}> = ({ kicker, value, prefix = "", suffix = "", decimals = 0, delta, caption, impactAt }) => {
  const frame = useCurrentFrame();
  const { opacity, y } = entry(frame, 0, 14);
  // restrained settle pulse at the impact frame — premium, not a slam.
  // impactAt (local frame) overrides the default so the punch lands on the canonical event frame.
  const ip = impactAt ?? 46;
  const settle = interpolate(frame, [ip - 6, ip, ip + 16], [1, 1.035, 1], { ...CLAMP, easing: expo });
  return (
    <div style={{ textAlign: "center", opacity, transform: `translateY(${y}px) scale(${settle})` }}>
      <Kicker text={kicker} />
      <div style={{ margin: "22px 0 18px" }}>
        <CountUp value={value} prefix={prefix} suffix={suffix} decimals={decimals} fontSize={190} duration={42} />
      </div>
      {delta !== undefined && <Delta value={delta} />}
      <div style={{ fontFamily: T.font, fontWeight: 600, fontSize: 30, color: T.inkMuted, marginTop: 22 }}>{caption}</div>
    </div>
  );
};

export const ThesisComposition: React.FC<{ claim: string; value: string; delta: number }> = ({ claim, value, delta }) => {
  const frame = useCurrentFrame();
  const { opacity, y } = entry(frame, 0, 16);
  return (
    <div style={{ opacity, transform: `translateY(${y}px)`, display: "flex", gap: 40, alignItems: "center" }}>
      <div style={{ width: 760 }}>
        <Kicker text="The thesis" />
        <div style={{ fontFamily: T.font, fontWeight: 800, fontSize: 76, color: T.ink, lineHeight: 1.14, letterSpacing: -1.5, marginTop: 18 }}>{claim}</div>
        <div style={{ display: "flex", alignItems: "center", gap: 22, marginTop: 30 }}>
          <div style={{ fontFamily: T.font, fontWeight: 800, fontSize: 64, color: T.primaryDeep, fontVariantNumeric: "tabular-nums" }}>{value}</div>
          <Delta value={delta} />
        </div>
      </div>
      <GlassCard width={620} padding={36}>
        <div style={{ transform: "scale(0.66)", transformOrigin: "top left", width: 1360 }}>
          <LineChart data={[30, 28, 33, 29, 38, 44, 41, 52, 60, 58, 70, 82]} color={T.primaryDeep} />
        </div>
      </GlassCard>
    </div>
  );
};

export const ClosingComposition: React.FC<{ line1: string; line2: string }> = ({ line1, line2 }) => {
  const frame = useCurrentFrame();
  const p1 = interpolate(frame, [6, 26], [0, 1], { ...CLAMP, easing: expo });
  const p2 = interpolate(frame, [24, 44], [0, 1], { ...CLAMP, easing: expo });
  return (
    <div style={{ textAlign: "center" }}>
      <div style={{ opacity: p1, transform: `translateY(${interpolate(p1, [0, 1], [30, 0], CLAMP)}px)`,
        fontFamily: T.font, fontWeight: 800, fontSize: 84, color: T.ink, letterSpacing: -2 }}>{line1}</div>
      <div style={{ opacity: p2, transform: `translateY(${interpolate(p2, [0, 1], [30, 0], CLAMP)}px)`,
        fontFamily: T.font, fontWeight: 800, fontSize: 84, color: T.primary, letterSpacing: -2, marginTop: 10 }}>{line2}</div>
      <div style={{ opacity: interpolate(frame, [50, 64], [0, 1], CLAMP), marginTop: 44,
        fontFamily: T.font, fontWeight: 700, fontSize: 24, letterSpacing: 5, color: T.inkMuted }}>ASTOR LEGACY</div>
    </div>
  );
};

export const ImageryGlassOverlay: React.FC<{ title: string; metric: string; delta: number }> = ({ title, metric, delta }) => {
  const frame = useCurrentFrame();
  const { opacity, y } = entry(frame, 10, 18);
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <img src={staticFile("light/office.jpg")} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      <div style={{ position: "absolute", inset: 0, background: "linear-gradient(180deg, rgba(248,250,255,0.25) 0%, rgba(248,250,255,0.55) 100%)" }} />
      <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ opacity, transform: `translateY(${y}px)` }}>
          <GlassCard width={720} padding={52}>
            <Kicker text="Market context" />
            <div style={{ fontFamily: T.font, fontWeight: 800, fontSize: 58, color: T.ink, lineHeight: 1.2, margin: "18px 0 26px" }}>{title}</div>
            <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
              <div style={{ fontFamily: T.font, fontWeight: 800, fontSize: 72, color: T.primaryDeep, fontVariantNumeric: "tabular-nums" }}>{metric}</div>
              <Delta value={delta} />
            </div>
          </GlassCard>
        </div>
      </div>
    </div>
  );
};

// RealWorldImagery — P0 2026-10-09: production component for the
// real_world_financial_imagery mode (was Showcase-only fixture).
// Split-scale strategy: background image zooms at the policy background_scale;
// edge-anchored text stays at the policy content_scale (1.0x) to preserve
// designed positions. The component resolves its own scales via the policy;
// the registry Center detects split strategy and does not apply a uniform scale.
export const RealWorldImagery: React.FC<{
  image?: string;
  title: string;
  subtitle: string;
}> = ({ image = "light/office.jpg", title, subtitle }) => {
  const { compositionScale: requested } = useMaterial();
  const resolved = resolveScale("real_world_financial_imagery", requested);
  const bgScale = resolved.background_scale ?? 1.0;
  const contentScale = resolved.effective_scale;
  return (
    <div style={{ position: "absolute", inset: 0, overflow: "hidden" }}>
      <div style={{
        position: "absolute", inset: 0,
        display: "flex", alignItems: "center", justifyContent: "center",
        transform: `scale(${bgScale})`,
      }}>
        <Img src={staticFile(image)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </div>
      <div style={{
        position: "absolute", inset: 0,
        display: "flex", alignItems: "center", justifyContent: "center",
        transform: `scale(${contentScale})`,
      }}>
        <div style={{ position: "absolute", left: 120, bottom: 110 }}>
          <div style={{ fontFamily: T.font, fontWeight: 800, fontSize: 54, color: "#fff", textShadow: "0 2px 24px rgba(0,0,0,0.35)" }}>{title}</div>
          <div style={{ fontFamily: T.font, fontWeight: 600, fontSize: 26, color: "rgba(255,255,255,0.85)", marginTop: 8 }}>{subtitle}</div>
        </div>
      </div>
    </div>
  );
};
