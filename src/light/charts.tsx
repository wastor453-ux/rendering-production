// Vector charts: line, area, bar, comparison bars, donut. All SVG, all animated.
import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import { T, CLAMP, EXPO } from "./tokens";

const expo = Easing.bezier(...EXPO);
const W = 900; const H = 420; const PAD = 56;

const scale = (data: number[], i: number, min: number, max: number) => {
  const x = PAD + (i / Math.max(1, data.length - 1)) * (W - PAD * 2);
  const y = H - PAD - ((data[i] - min) / Math.max(1e-9, max - min)) * (H - PAD * 2);
  return [x, y] as const;
};
const path = (data: number[]) => {
  const min = Math.min(...data); const max = Math.max(...data);
  return data.map((_, i) => { const [x, y] = scale(data, i, min, max); return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`; }).join(" ");
};

export const LineChart: React.FC<{ data: number[]; labels?: string[]; color?: string; highlightLast?: boolean }> = ({
  data, labels = [], color = T.primary, highlightLast = true,
}) => {
  const frame = useCurrentFrame();
  const draw = interpolate(frame, [8, 55], [0, 1], { ...CLAMP, easing: expo });
  const d = path(data);
  const totalLen = 2400;
  const [lx, ly] = scale(data, data.length - 1, Math.min(...data), Math.max(...data));
  return (
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
      {[0.25, 0.5, 0.75].map((t) => (
        <line key={t} x1={PAD} x2={W - PAD} y1={H * t} y2={H * t} stroke={T.inkMuted} strokeOpacity={0.14} strokeWidth={1} />
      ))}
      <path d={d} fill="none" stroke={color} strokeWidth={5} strokeLinecap="round"
        strokeDasharray={totalLen} strokeDashoffset={totalLen * (1 - draw)} />
      {highlightLast && draw > 0.85 && (() => {
        const op = interpolate(draw, [0.85, 1], [0, 1], CLAMP);
        return (<g opacity={op}>
          <circle cx={lx} cy={ly} r={11} fill={color} />
          <circle cx={lx} cy={ly} r={11} fill="none" stroke={color} strokeOpacity={0.35} strokeWidth={3} />
          <circle cx={lx} cy={ly} r={5.5} fill="#fff" />
        </g>);
      })()}
      {labels.map((lb, i) => {
        if (i % Math.ceil(labels.length / 5) !== 0) return null;
        const [x] = scale(data, i, Math.min(...data), Math.max(...data));
        return <text key={i} x={x} y={H - 14} textAnchor="middle" fontFamily={T.font} fontSize={19} fill={T.inkMuted} fontWeight={600}>{lb}</text>;
      })}
    </svg>
  );
};

export const AreaChart: React.FC<{ data: number[]; color?: string }> = ({ data, color = T.primary }) => {
  const frame = useCurrentFrame();
  const draw = interpolate(frame, [8, 50], [0, 1], { ...CLAMP, easing: expo });
  const fill = interpolate(frame, [40, 70], [0, 1], CLAMP);
  const d = path(data);
  const min = Math.min(...data); const max = Math.max(...data);
  const [fx] = scale(data, data.length - 1, min, max);
  const area = `${d} L${fx.toFixed(1)},${(H - PAD).toFixed(1)} L${PAD},${(H - PAD).toFixed(1)} Z`;
  return (
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
      <defs>
        <linearGradient id="areaFill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity={0.32} />
          <stop offset="100%" stopColor={color} stopOpacity={0.02} />
        </linearGradient>
        <clipPath id="areaClip"><rect x={PAD} y={0} width={(W - PAD * 2) * draw} height={H} /></clipPath>
      </defs>
      <g clipPath="url(#areaClip)">
        <path d={area} fill="url(#areaFill)" opacity={fill} />
        <path d={d} fill="none" stroke={color} strokeWidth={5} strokeLinecap="round" />
      </g>
    </svg>
  );
};

export const BarChart: React.FC<{ data: { label: string; value: number }[]; color?: string; highlight?: number; impactAt?: number; impactBar?: number }> = ({
  data, color = T.primary, highlight = -1, impactAt, impactBar = 0,
}) => {
  const frame = useCurrentFrame();
  const max = Math.max(...data.map((d) => d.value));
  const bw = (W - PAD * 2) / data.length;
  // punch pulse on the impact bar at the canonical frame (SFX-synced)
  const ip = impactAt ?? 33;
  const pulse = interpolate(frame, [ip - 5, ip, ip + 14], [0, 1, 0], { ...CLAMP, easing: expo });
  return (
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
      {data.map((d, i) => {
        const h = ((H - PAD * 2) * d.value) / max;
        const p = interpolate(frame, [8 + i * 7, 30 + i * 7], [0, 1], { ...CLAMP, easing: expo });
        const x = PAD + i * bw + bw * 0.22; const w = bw * 0.56;
        const isHl = i === highlight;
        const isPunch = i === impactBar && pulse > 0;
        return (
          <g key={d.label} opacity={interpolate(frame, [8 + i * 7, 16 + i * 7], [0, 1], CLAMP)}>
            <rect x={x} y={H - PAD - h * p} width={w} height={Math.max(0.1, h * p)} rx={9}
              fill={isHl ? T.primaryDeep : color} opacity={isHl ? 1 : 0.55 + (0.45 * i) / data.length}
              transform={isPunch ? `scale(1 ${1 + 0.06 * pulse})` : undefined} style={{ transformOrigin: `${x + w / 2}px ${H - PAD}px` }} />
            {isPunch && (
              <rect x={x - 10 * pulse} y={H - PAD - h * p - 10 * pulse} width={w + 20 * pulse} height={Math.max(0.1, h * p) + 10 * pulse}
                rx={14} fill="none" stroke={T.primaryDeep} strokeWidth={3} opacity={0.8 * (1 - pulse * 0.35)} />
            )}
            <text x={x + w / 2} y={H - 14} textAnchor="middle" fontFamily={T.font} fontSize={19} fill={T.inkMuted} fontWeight={600}>{d.label}</text>
          </g>
        );
      })}
    </svg>
  );
};

export const ComparisonBars: React.FC<{ left: { label: string; value: number }; right: { label: string; value: number } }> = ({ left, right }) => {
  const frame = useCurrentFrame();
  const max = Math.max(left.value, right.value);
  const p = interpolate(frame, [10, 45], [0, 1], { ...CLAMP, easing: expo });
  const bar = (v: number, color: string, tint: string) => (
    <div style={{ flex: 1 }}>
      <div style={{ height: 26, borderRadius: 13, background: tint, overflow: "hidden" }}>
        <div style={{ width: `${(v / max) * 100 * p}%`, height: "100%", background: color, borderRadius: 13 }} />
      </div>
    </div>
  );
  const row = (s: { label: string; value: number }, color: string, tint: string, fmt: string) => (
    <div style={{ display: "flex", alignItems: "center", gap: 24, marginBottom: 26 }}>
      <div style={{ width: 220, fontFamily: T.font, fontWeight: 700, fontSize: 30, color: T.ink }}>{s.label}</div>
      {bar(s.value, color, tint)}
      <div style={{ width: 200, fontFamily: T.font, fontWeight: 800, fontSize: 34, color: T.ink, fontVariantNumeric: "tabular-nums" }}>{fmt}</div>
    </div>
  );
  return (
    <div style={{ width: W, opacity: interpolate(frame, [0, 12], [0, 1], CLAMP) }}>
      {row(left, T.primary, T.blueTint, `$${left.value.toLocaleString()}`)}
      {row(right, T.negative, T.negativeTint, `$${right.value.toLocaleString()}`)}
    </div>
  );
};

export const DonutChart: React.FC<{ segments: { label: string; value: number; color: string }[] }> = ({ segments }) => {
  const frame = useCurrentFrame();
  const total = segments.reduce((s, x) => s + x.value, 0);
  const R = 130; const C = 2 * Math.PI * R;
  const build = interpolate(frame, [8, 50], [0, 1], { ...CLAMP, easing: expo });
  let acc = 0;
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 60 }}>
      <svg width={340} height={340} viewBox="0 0 340 340">
        <g transform="rotate(-90 170 170)">
          {segments.map((s, i) => {
            const frac = s.value / total;
            const el = (
              <circle key={s.label} cx={170} cy={170} r={R} fill="none" stroke={s.color} strokeWidth={44}
                strokeDasharray={`${frac * C * build} ${C}`} strokeDashoffset={-acc * C * build}
                strokeLinecap="butt" opacity={interpolate(frame, [8 + i * 8, 18 + i * 8], [0, 1], CLAMP)} />
            );
            acc += frac;
            return el;
          })}
        </g>
        <text x={170} y={162} textAnchor="middle" fontFamily={T.font} fontWeight={800} fontSize={44} fill={T.ink}>100%</text>
        <text x={170} y={196} textAnchor="middle" fontFamily={T.font} fontWeight={600} fontSize={22} fill={T.inkMuted}>allocated</text>
      </svg>
      <div>
        {segments.map((s, i) => (
          <div key={s.label} style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 14,
            opacity: interpolate(frame, [14 + i * 8, 24 + i * 8], [0, 1], CLAMP) }}>
            <div style={{ width: 22, height: 22, borderRadius: 7, background: s.color }} />
            <div style={{ fontFamily: T.font, fontWeight: 700, fontSize: 28, color: T.ink, width: 220 }}>{s.label}</div>
            <div style={{ fontFamily: T.font, fontWeight: 700, fontSize: 28, color: T.inkMuted }}>{Math.round((s.value / total) * 100)}%</div>
          </div>
        ))}
      </div>
    </div>
  );
};

// ============ ADVANCED CHART STORYTELLING (2026-10-08 completion pass) ============
// reveal -> build -> explain -> highlight -> transform -> resolve.
// Animate the INFORMATIONAL CHANGE, not every property.

/** 1. LINE -> HIGHLIGHTED EVENT -> ANNOTATION. Draw, mark the inflection, explain it. */
export const LineChartStory: React.FC<{
  data: number[]; labels?: string[];
  eventIndex: number; eventLabel: string; eventSub?: string;
  metric?: string; impactAt?: number;
}> = ({ data, labels = [], eventIndex, eventLabel, eventSub, metric, impactAt }) => {
  const frame = useCurrentFrame();
  const draw = interpolate(frame, [8, 60], [0, 1], { ...CLAMP, easing: expo });
  const min = Math.min(...data); const max = Math.max(...data);
  const d = path(data);
  const totalLen = 2400;
  const [ex, ey] = scale(data, eventIndex, min, max);
  const mark = interpolate(frame, [62, 78], [0, 1], { ...CLAMP, easing: expo });
  const note = interpolate(frame, [80, 96], [0, 1], { ...CLAMP, easing: expo });
  const met = metric ? interpolate(frame, [98, 112], [0, 1], CLAMP) : 0;
  // impact pulse on the event marker at the canonical frame (SFX-synced punch)
  const ip = impactAt ?? 70;
  const pulse = interpolate(frame, [ip - 5, ip, ip + 14], [0, 1, 0], { ...CLAMP, easing: expo });
  const [lx, ly] = scale(data, data.length - 1, min, max);
  return (
    <svg width={W} height={H + 90} viewBox={`0 0 ${W} ${H + 90}`}>
      {[0.25, 0.5, 0.75].map((t) => (
        <line key={t} x1={PAD} x2={W - PAD} y1={H * t} y2={H * t} stroke={T.inkMuted} strokeOpacity={0.14} strokeWidth={1} />
      ))}
      <path d={d} fill="none" stroke={T.primary} strokeWidth={5} strokeLinecap="round"
        strokeDasharray={totalLen} strokeDashoffset={totalLen * (1 - draw)} />
      {draw > 0.85 && (
        <g opacity={interpolate(draw, [0.85, 1], [0, 1], CLAMP)}>
          <circle cx={lx} cy={ly} r={10} fill={T.primary} />
          <circle cx={lx} cy={ly} r={5} fill="#fff" />
        </g>
      )}
      {mark > 0 && (
        <g opacity={mark}>
          <line x1={ex} y1={ey - 26} x2={ex} y2={PAD - 6} stroke={T.negative} strokeWidth={2.5} strokeDasharray="7 6" />
          <circle cx={ex} cy={ey} r={13 + 4 * mark} fill="none" stroke={T.negative} strokeWidth={4} />
          <circle cx={ex} cy={ey} r={8} fill={T.negative} />
          {pulse > 0 && (
            <circle cx={ex} cy={ey} r={16 + 26 * pulse} fill="none" stroke={T.negative} strokeWidth={3} opacity={0.85 * (1 - pulse * 0.4)} />
          )}
        </g>
      )}
      {note > 0 && (
        <g opacity={note} transform={`translate(0 ${(1 - note) * 18})`}>
          <rect x={Math.min(Math.max(ex - 170, PAD), W - PAD - 340)} y={H + 18} width={340} height={64} rx={16}
            fill="#fff" stroke={T.glassBorder} strokeWidth={1.5} />
          <text x={Math.min(Math.max(ex - 170, PAD), W - PAD - 340) + 170} y={H + 46} textAnchor="middle"
            fontFamily={T.font} fontWeight={800} fontSize={24} fill={T.ink}>{eventLabel}</text>
          {eventSub && (
            <text x={Math.min(Math.max(ex - 170, PAD), W - PAD - 340) + 170} y={H + 68} textAnchor="middle"
              fontFamily={T.font} fontWeight={600} fontSize={19} fill={T.inkMuted}>{eventSub}</text>
          )}
        </g>
      )}
      {metric && met > 0 && (
        <text x={W - PAD} y={44} textAnchor="end" fontFamily={T.font} fontWeight={800} fontSize={30}
          fill={T.primaryDeep} opacity={met} fontVariantNumeric="tabular-nums">{metric}</text>
      )}
      {labels.map((lb, i) => {
        if (i % Math.ceil(labels.length / 5) !== 0) return null;
        const [x] = scale(data, i, min, max);
        return <text key={i} x={x} y={H - 14} textAnchor="middle" fontFamily={T.font} fontSize={19} fill={T.inkMuted} fontWeight={600}>{lb}</text>;
      })}
    </svg>
  );
};

/** 2. AREA STORY: progressive draw + fill reveal + highlighted period + metric callout. */
export const AreaChartStory: React.FC<{
  data: number[]; highlightFrom: number; highlightTo: number;
  highlightLabel: string; metric: string;
}> = ({ data, highlightFrom, highlightTo, highlightLabel, metric }) => {
  const frame = useCurrentFrame();
  const draw = interpolate(frame, [8, 55], [0, 1], { ...CLAMP, easing: expo });
  const fill = interpolate(frame, [42, 72], [0, 1], CLAMP);
  const hl = interpolate(frame, [74, 92], [0, 1], CLAMP);
  const met = interpolate(frame, [94, 108], [0, 1], CLAMP);
  const d = path(data);
  const min = Math.min(...data); const max = Math.max(...data);
  const [fx] = scale(data, data.length - 1, min, max);
  const area = `${d} L${fx.toFixed(1)},${(H - PAD).toFixed(1)} L${PAD},${(H - PAD).toFixed(1)} Z`;
  const [hx0] = scale(data, highlightFrom, min, max);
  const [hx1] = scale(data, highlightTo, min, max);
  return (
    <svg width={W} height={H + 60} viewBox={`0 0 ${W} ${H + 60}`}>
      <defs>
        <linearGradient id="areaStoryFill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={T.primary} stopOpacity={0.32} />
          <stop offset="100%" stopColor={T.primary} stopOpacity={0.02} />
        </linearGradient>
        <clipPath id="areaStoryClip"><rect x={PAD} y={0} width={(W - PAD * 2) * draw} height={H + 60} /></clipPath>
      </defs>
      <rect x={hx0} y={PAD - 20} width={Math.max(8, hx1 - hx0)} height={H - PAD * 2 + 20}
        fill={T.primary} opacity={0.1 * hl} rx={10} />
      <g clipPath="url(#areaStoryClip)">
        <path d={area} fill="url(#areaStoryFill)" opacity={fill} />
        <path d={d} fill="none" stroke={T.primary} strokeWidth={5} strokeLinecap="round" />
      </g>
      {hl > 0 && (
        <text x={(hx0 + hx1) / 2} y={H + 34} textAnchor="middle" fontFamily={T.font} fontWeight={800}
          fontSize={23} fill={T.primaryDeep} opacity={hl}>{highlightLabel}</text>
      )}
      {met > 0 && (
        <text x={W - PAD} y={40} textAnchor="end" fontFamily={T.font} fontWeight={800} fontSize={32}
          fill={T.ink} opacity={met} fontVariantNumeric="tabular-nums">{metric}</text>
      )}
    </svg>
  );
};

/** 3. STACKED BAR: segments build sequentially, total resolves. */
export const StackedBar: React.FC<{
  groups: { label: string; segments: { label: string; value: number; color: string }[] }[];
}> = ({ groups }) => {
  const frame = useCurrentFrame();
  const maxTotal = Math.max(...groups.map((g) => g.segments.reduce((s, x) => s + x.value, 0)));
  const bw = (W - PAD * 2) / groups.length;
  return (
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
      {groups.map((g, gi) => {
        const total = g.segments.reduce((s, x) => s + x.value, 0);
        const bh = ((H - PAD * 2) * total) / maxTotal;
        const x = PAD + gi * bw + bw * 0.24; const w = bw * 0.52;
        let acc = 0;
        return (
          <g key={g.label} opacity={interpolate(frame, [8 + gi * 10, 18 + gi * 10], [0, 1], CLAMP)}>
            {g.segments.map((s, si) => {
              const sh = (bh * s.value) / total;
              const p = interpolate(frame, [14 + gi * 10 + si * 9, 32 + gi * 10 + si * 9], [0, 1], { ...CLAMP, easing: expo });
              const y = H - PAD - acc - sh * p;
              acc += sh * p;
              return <rect key={s.label} x={x} y={y} width={w} height={Math.max(0.1, sh * p)}
                rx={si === g.segments.length - 1 ? 9 : 3} fill={s.color} opacity={0.92} />;
            })}
            <text x={x + w / 2} y={H - PAD + 44} textAnchor="middle" fontFamily={T.font} fontSize={21}
              fill={T.ink} fontWeight={800} fontVariantNumeric="tabular-nums">
              ${total.toLocaleString()}
            </text>
            <text x={x + w / 2} y={H - 14} textAnchor="middle" fontFamily={T.font} fontSize={19} fill={T.inkMuted} fontWeight={600}>{g.label}</text>
          </g>
        );
      })}
    </svg>
  );
};

/** 5+6. INDEXED / MULTI-SERIES: normalized baseline, animated divergence, endpoint callouts. */
export const MultiSeriesChart: React.FC<{
  series: { label: string; color: string; data: number[] }[];
  indexed?: boolean;
}> = ({ series, indexed = false }) => {
  const frame = useCurrentFrame();
  const norm = series.map((s) => {
    if (!indexed) return s.data;
    const b = s.data[0] || 1;
    return s.data.map((v) => ((v - b) / b) * 100);
  });
  const all = norm.flat();
  const min = Math.min(...all); const max = Math.max(...all);
  const totalLen = 2400;
  return (
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
      {[0.25, 0.5, 0.75].map((t) => (
        <line key={t} x1={PAD} x2={W - PAD} y1={H * t} y2={H * t} stroke={T.inkMuted} strokeOpacity={0.14} strokeWidth={1} />
      ))}
      {indexed && (
        <line x1={PAD} x2={W - PAD} y1={scale([0], 0, min, max)[1]} y2={scale([0], 0, min, max)[1]}
          stroke={T.inkMuted} strokeWidth={2} strokeDasharray="8 7" opacity={0.6} />
      )}
      {series.map((s, si) => {
        const d = path(norm[si]);
        const draw = interpolate(frame, [8 + si * 16, 55 + si * 16], [0, 1], { ...CLAMP, easing: expo });
        const [lx, ly] = scale(norm[si], norm[si].length - 1, min, max);
        const lastV = s.data[s.data.length - 1];
        return (
          <g key={s.label}>
            <path d={d} fill="none" stroke={s.color} strokeWidth={4.5} strokeLinecap="round"
              strokeDasharray={totalLen} strokeDashoffset={totalLen * (1 - draw)} />
            {draw > 0.9 && (
              <g opacity={interpolate(draw, [0.9, 1], [0, 1], CLAMP)}>
                <circle cx={lx} cy={ly} r={8} fill={s.color} />
                <text x={Math.min(lx + 16, W - PAD - 130)} y={ly - 12} fontFamily={T.font} fontWeight={800}
                  fontSize={22} fill={s.color}>{s.label}</text>
                <text x={Math.min(lx + 16, W - PAD - 130)} y={ly + 14} fontFamily={T.font} fontWeight={700}
                  fontSize={21} fill={T.inkMuted} fontVariantNumeric="tabular-nums">
                  {indexed ? `${lastV >= 0 ? "+" : ""}${lastV.toFixed(0)}%` : lastV.toLocaleString()}
                </text>
              </g>
            )}
          </g>
        );
      })}
      <g opacity={interpolate(frame, [8, 24], [0, 1], CLAMP)}>
        {series.map((s, si) => (
          <g key={s.label} transform={`translate(${PAD + si * 200}, 26)`}>
            <rect width={20} height={20} rx={6} fill={s.color} />
            <text x={30} y={16} fontFamily={T.font} fontWeight={700} fontSize={21} fill={T.ink}>{s.label}</text>
          </g>
        ))}
      </g>
    </svg>
  );
};

/** 9. CHART -> METRIC transformation: semantic continuity, data hands off to KPI. */
export const ChartToMetric: React.FC<{
  data: number[]; metric: string; caption: string;
}> = ({ data, metric, caption }) => {
  const frame = useCurrentFrame();
  const draw = interpolate(frame, [6, 48], [0, 1], { ...CLAMP, easing: expo });
  const morph = interpolate(frame, [58, 95], [0, 1], { ...CLAMP, easing: expo });
  const d = path(data);
  const totalLen = 2400;
  const min = Math.min(...data); const max = Math.max(...data);
  const [lx, ly] = scale(data, data.length - 1, min, max);
  return (
    <div style={{ width: W, height: H, position: "relative", opacity: interpolate(frame, [0, 10], [0, 1], CLAMP) }}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ opacity: 1 - morph }}>
        <path d={d} fill="none" stroke={T.primary} strokeWidth={5} strokeLinecap="round"
          strokeDasharray={totalLen} strokeDashoffset={totalLen * (1 - draw)} />
        {draw > 0.8 && <circle cx={lx} cy={ly} r={10 * morph + 10} fill={T.primary} opacity={1 - morph * 0.5} />}
      </svg>
      <div style={{
        position: "absolute", inset: 0, display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center",
        opacity: morph, transform: `scale(${interpolate(morph, [0, 1], [0.86, 1], CLAMP)})`,
      }}>
        <div style={{ fontFamily: T.font, fontWeight: 800, fontSize: 110, color: T.ink,
          fontVariantNumeric: "tabular-nums", letterSpacing: -3 }}>{metric}</div>
        <div style={{ fontFamily: T.font, fontWeight: 600, fontSize: 30, color: T.inkMuted, marginTop: 10 }}>{caption}</div>
      </div>
    </div>
  );
};
