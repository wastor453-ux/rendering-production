// Explanation modes: before/after, two-sided comparison, causal diagram,
// causal loop, timeline, flow diagram.
import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import { T, CLAMP, EXPO } from "./tokens";
import { GlassCard, Label, entry } from "./primitives";

const expo = Easing.bezier(...EXPO);

export const BeforeAfter: React.FC<{ before: { label: string; value: string }; after: { label: string; value: string } }> = ({ before, after }) => {
  const frame = useCurrentFrame();
  const morph = interpolate(frame, [35, 70], [0, 1], { ...CLAMP, easing: expo });
  const card = (s: { label: string; value: string }, tint: string, fg: string, active: boolean) => (
    <GlassCard width={480} padding={44} style={{ opacity: active ? 1 : 0.55, transform: `scale(${active ? 1 : 0.96})` }}>
      <Label text={s.label} />
      <div style={{ fontFamily: T.font, fontWeight: 800, fontSize: 76, color: fg, marginTop: 12, fontVariantNumeric: "tabular-nums" }}>{s.value}</div>
    </GlassCard>
  );
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 40, opacity: interpolate(frame, [0, 12], [0, 1], CLAMP) }}>
      {card(before, T.negativeTint, "#B44A4A", morph < 0.5)}
      <div style={{ fontFamily: T.font, fontWeight: 800, fontSize: 54, color: T.primary,
        transform: `translateX(${interpolate(morph, [0, 1], [-10, 10], CLAMP)}px)` }}>→</div>
      {card(after, T.successTint, "#1E7F5C", morph >= 0.5)}
    </div>
  );
};

export const TwoSidedComparison: React.FC<{
  left: { title: string; rows: [string, string][] }; right: { title: string; rows: [string, string][] };
  impactAt?: number; impactRow?: number;
}> = ({ left, right, impactAt, impactRow = 0 }) => {
  const frame = useCurrentFrame();
  const lp = interpolate(frame, [6, 24], [0, 1], { ...CLAMP, easing: expo });
  const rp = interpolate(frame, [18, 36], [0, 1], { ...CLAMP, easing: expo });
  // punch highlight on the impact row at the canonical frame (SFX-synced)
  const ip = impactAt ?? 50;
  const punch = interpolate(frame, [ip - 4, ip, ip + 12], [0, 1, 0], { ...CLAMP, easing: expo });
  const side = (s: { title: string; rows: [string, string][] }, p: number, dir: number, accent: string, isRight: boolean) => (
    <div style={{ opacity: p, transform: `translateX(${interpolate(p, [0, 1], [50 * dir, 0], CLAMP)}px)` }}>
      <GlassCard width={560} padding={40}>
        <div style={{ fontFamily: T.font, fontWeight: 800, fontSize: 38, color: T.ink, marginBottom: 20 }}>{s.title}</div>
        {s.rows.map(([k, v], i) => {
          const rowP = interpolate(frame, [26 + i * 8, 36 + i * 8], [0, 1], CLAMP);
          const isPunch = isRight && i === impactRow && punch > 0;
          return (
            <div key={k} style={{ display: "flex", justifyContent: "space-between", padding: "13px 0",
              borderBottom: `1px solid ${T.glassBorder}`, opacity: rowP,
              background: isPunch ? `rgba(83,104,247,${0.10 * punch})` : "transparent",
              borderRadius: 10, transform: isPunch ? `scale(${1 + 0.02 * punch})` : "scale(1)" }}>
              <Label text={k} size={24} />
              <div style={{ fontFamily: T.font, fontWeight: 800, fontSize: 28, color: accent, fontVariantNumeric: "tabular-nums" }}>{v}</div>
            </div>
          );
        })}
      </GlassCard>
    </div>
  );
  return (
    <div style={{ display: "flex", gap: 36, alignItems: "flex-start" }}>
      {side(left, lp, -1, T.primaryDeep, false)}
      {side(right, rp, 1, "#1E7F5C", true)}
    </div>
  );
};

const node = (x: number, y: number, label: string, sub: string, p: number, accent = T.primary) => (
  <g key={label} opacity={p}>
    <rect x={x - 150} y={y - 62} width={300} height={124} rx={20} fill="#fff" stroke={T.glassBorder} strokeWidth={1.5} />
    <rect x={x - 150} y={y - 62} width={10} height={124} rx={5} fill={accent} />
    <text x={x + 4} y={y - 8} textAnchor="middle" fontFamily={T.font} fontWeight={800} fontSize={30} fill={T.ink}>{label}</text>
    <text x={x + 4} y={y + 28} textAnchor="middle" fontFamily={T.font} fontWeight={600} fontSize={22} fill={T.inkMuted}>{sub}</text>
  </g>
);
const edge = (x1: number, y1: number, x2: number, y2: number, p: number) => (
  <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={T.primary} strokeWidth={4} strokeLinecap="round"
    strokeDasharray={400} strokeDashoffset={400 * (1 - p)} opacity={0.75} />
);

export const CausalDiagram: React.FC<{ steps: { label: string; sub: string }[]; impactAt?: number; impactNode?: number }> = ({ steps, impactAt, impactNode = 0 }) => {
  const frame = useCurrentFrame();
  const n = steps.length;
  const xs = steps.map((_, i) => 240 + i * ((1440 - 480) / Math.max(1, n - 1)));
  const y = 400;
  // punch pulse on the impact node at the canonical frame (SFX-synced)
  const ip = impactAt ?? 14;
  const pulse = interpolate(frame, [ip - 5, ip, ip + 14], [0, 1, 0], { ...CLAMP, easing: expo });
  return (
    <svg width={1680} height={800} viewBox="0 0 1680 800">
      {steps.slice(0, -1).map((_, i) =>
        edge(xs[i] + 150, y, xs[i + 1] - 150, y, interpolate(frame, [20 + i * 22, 34 + i * 22], [0, 1], { ...CLAMP, easing: expo }))
      )}
      {steps.map((s, i) => {
        const p = interpolate(frame, [8 + i * 22, 20 + i * 22], [0, 1], { ...CLAMP, easing: expo });
        const isPunch = i === impactNode && pulse > 0;
        return (
          <g key={s.label} opacity={p}>
            <rect x={xs[i] - 150} y={y - 62} width={300} height={124} rx={20} fill="#fff" stroke={T.glassBorder} strokeWidth={1.5} />
            <rect x={xs[i] - 150} y={y - 62} width={10} height={124} rx={5} fill={i === n - 1 ? T.negative : T.primary} />
            {isPunch && (
              <rect x={xs[i] - 150 - 14 * pulse} y={y - 62 - 14 * pulse} width={300 + 28 * pulse} height={124 + 28 * pulse}
                rx={26} fill="none" stroke={T.primary} strokeWidth={3} opacity={0.8 * (1 - pulse * 0.35)} />
            )}
            <text x={xs[i] + 4} y={y - 8} textAnchor="middle" fontFamily={T.font} fontWeight={800} fontSize={30} fill={T.ink}>{s.label}</text>
            <text x={xs[i] + 4} y={y + 28} textAnchor="middle" fontFamily={T.font} fontWeight={600} fontSize={22} fill={T.inkMuted}>{s.sub}</text>
          </g>
        );
      })}
    </svg>
  );
};

export const CausalLoop: React.FC<{ steps: { label: string; sub: string }[] }> = ({ steps }) => {
  const frame = useCurrentFrame();
  const cx = 840; const cy = 400; const R = 260;
  const pos = (i: number) => {
    const a = -Math.PI / 2 + (i / steps.length) * Math.PI * 2;
    return [cx + R * Math.cos(a), cy + R * 1.05 * Math.sin(a)] as const;
  };
  const loopP = interpolate(frame, [8 + steps.length * 14, 26 + steps.length * 14], [0, 1], { ...CLAMP, easing: expo });
  return (
    <svg width={1680} height={800} viewBox="0 0 1680 800">
      <ellipse cx={cx} cy={cy} rx={R} ry={R * 1.05} fill="none" stroke={T.primary} strokeWidth={4}
        strokeDasharray={2200} strokeDashoffset={2200 * (1 - loopP)} opacity={0.6} />
      {steps.map((s, i) => {
        const [x, y] = pos(i);
        return node(x, y, s.label, s.sub, interpolate(frame, [8 + i * 20, 20 + i * 20], [0, 1], { ...CLAMP, easing: expo }));
      })}
    </svg>
  );
};

export const Timeline: React.FC<{ events: { year: string; label: string }[] }> = ({ events }) => {
  const frame = useCurrentFrame();
  const draw = interpolate(frame, [8, 60], [0, 1], { ...CLAMP, easing: expo });
  const n = events.length;
  return (
    <svg width={1680} height={600} viewBox="0 0 1680 600">
      <line x1={120} y1={300} x2={120 + 1440 * draw} y2={300} stroke={T.primary} strokeWidth={6} strokeLinecap="round" />
      {events.map((e, i) => {
        const x = 120 + (i / Math.max(1, n - 1)) * 1440;
        const p = interpolate(frame, [14 + i * 14, 26 + i * 14], [0, 1], { ...CLAMP, easing: expo });
        const above = i % 2 === 0;
        return (
          <g key={e.year} opacity={p}>
            <circle cx={x} cy={300} r={13} fill={T.primaryDeep} stroke="#fff" strokeWidth={4} />
            <line x1={x} y1={300} x2={x} y2={above ? 190 : 410} stroke={T.glassBorder} strokeWidth={2} />
            <text x={x} y={above ? 150 : 470} textAnchor="middle" fontFamily={T.font} fontWeight={800} fontSize={30} fill={T.primaryDeep}>{e.year}</text>
            <text x={x} y={above ? 118 : 502} textAnchor="middle" fontFamily={T.font} fontWeight={600} fontSize={23} fill={T.inkMuted}>{e.label}</text>
          </g>
        );
      })}
    </svg>
  );
};

export const FlowDiagram: React.FC<{ nodes: string[] }> = ({ nodes }) => {
  const frame = useCurrentFrame();
  const n = nodes.length;
  const totalW = n * 300 + (n - 1) * 90;
  const startX = (1680 - totalW) / 2;
  return (
    <svg width={1680} height={500} viewBox="0 0 1680 500">
      {nodes.slice(0, -1).map((_, i) => {
        const x1 = startX + (i + 1) * 300 + i * 90 - 20;
        const x2 = startX + (i + 1) * 300 + (i + 1) * 90 - 70;
        const w = interpolate(frame, [24 + i * 20, 40 + i * 20], [0, 1], { ...CLAMP, easing: expo });
        return (
          <g key={i} opacity={w}>
            <rect x={x1} y={228} width={(x2 - x1) * w} height={14} rx={7} fill={T.primary} opacity={0.5} />
            <polygon points={`${x2},220 ${x2},262 ${x2 + 26},241`} fill={T.primary} />
          </g>
        );
      })}
      {nodes.map((nd, i) => {
        const x = startX + i * 390;
        const p = interpolate(frame, [8 + i * 20, 22 + i * 20], [0, 1], { ...CLAMP, easing: expo });
        return (
          <g key={nd} opacity={p} transform={`translate(0 ${interpolate(p, [0, 1], [30, 0], CLAMP)})`}>
            <rect x={x} y={170} width={300} height={142} rx={22} fill="#fff" stroke={T.glassBorder} strokeWidth={1.5} />
            <text x={x + 150} y={252} textAnchor="middle" fontFamily={T.font} fontWeight={800} fontSize={30} fill={T.ink}>{nd}</text>
          </g>
        );
      })}
    </svg>
  );
};
