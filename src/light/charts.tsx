// charts.tsx v2.0 — Rebuilt from Graph Atlas image (exact styles)
// 10 chart components matching reference image specifications
// Rules: REPLACEMENT_RULES.md

import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import { T, CLAMP, EXPO } from "./tokens";
import { TrustStrip } from "./primitives";

const expo = Easing.bezier(...EXPO);
const W = 900; const H = 420; const PAD = 56;

// === Math helpers (verified) ===
const scale = (data: number[], i: number, min: number, max: number) => {
  const x = PAD + (i / Math.max(1, data.length - 1)) * (W - PAD * 2);
  const y = H - PAD - ((data[i] - min) / Math.max(1e-9, max - min)) * (H - PAD * 2);
  return [x, y] as const;
};

const linePath = (data: number[]) => {
  if (data.length === 0) return "";
  const min = Math.min(...data); const max = Math.max(...data);
  return data.map((_, i) => {
    const [x, y] = scale(data, i, min, max);
    return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");
};

// === Chart Card Wrapper (from Graph Atlas) ===
const ChartCard: React.FC<{
  title: string; subtitle: string; children: React.ReactNode;
  source?: string; date?: string; units?: string; width?: number;
}> = ({ title, subtitle, children, source, date, units, width = 980 }) => (
  <div style={{
    width, background: "rgba(255,255,255,0.90)",
    borderRadius: 24, border: "1px solid rgba(216,230,250,0.70)",
    boxShadow: "0 10px 30px rgba(40,85,170,0.08)",
    padding: 32,
  }}>
    <div style={{ fontFamily: T.font, fontSize: 28, fontWeight: 800, color: T.ink }}>{title}</div>
    <div style={{ fontFamily: T.font, fontSize: 20, fontWeight: 400, color: T.inkMuted, marginTop: 6 }}>{subtitle}</div>
    <div style={{ marginTop: 24 }}>{children}</div>
    {(source || date || units) && (
      <TrustStrip source={source} date={date} units={units} />
    )}
  </div>
);

// === 1. LineChart — Portfolio Value Over Time (Graph Atlas #1) ===
export const LineChart: React.FC<{
  data: number[]; labels?: string[]; color?: string;
  title?: string; subtitle?: string; source?: string; date?: string;
  endpointLabel?: string;
}> = ({
  data, labels = [], color = T.primary,
  title = "Portfolio Value Over Time", subtitle = "Track how your investments grow over time.",
  source, date, endpointLabel,
}) => {
  const frame = useCurrentFrame();
  const draw = interpolate(frame, [8, 55], [0, 1], { ...CLAMP, easing: expo });
  const d = linePath(data);
  const totalLen = 2400;
  const min = Math.min(...data); const max = Math.max(...data);
  const [lx, ly] = scale(data, data.length - 1, min, max);

  return (
    <ChartCard title={title} subtitle={subtitle} source={source} date={date} units="USD">
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        {/* Grid: light blue, horizontal only */}
        {[0.2, 0.4, 0.6, 0.8].map((t) => (
          <line key={t} x1={PAD} x2={W - PAD} y1={H * t} y2={H * t}
            stroke="#DCE6FF" strokeWidth={1} />
        ))}
        {/* Y labels */}
        {[0, 0.25, 0.5, 0.75, 1].map((t) => {
          const val = min + (max - min) * t;
          const y = H - PAD - t * (H - PAD * 2);
          return (
            <text key={t} x={PAD - 12} y={y + 6} textAnchor="end"
              fontFamily={T.font} fontSize={16} fontWeight={500} fill={T.inkMuted}>
              ${Math.round(val / 1000)}k
            </text>
          );
        })}
        {/* Line */}
        <path d={d} fill="none" stroke={color} strokeWidth={3} strokeLinecap="round"
          strokeDasharray={totalLen} strokeDashoffset={totalLen * (1 - draw)} />
        {/* Endpoint dot + label */}
        {draw > 0.85 && (() => {
          const op = interpolate(draw, [0.85, 1], [0, 1], CLAMP);
          return (
            <g opacity={op}>
              <circle cx={lx} cy={ly} r={8} fill={color} />
              <circle cx={lx} cy={ly} r={4} fill="#fff" />
              {endpointLabel && (
                <g>
                  <rect x={lx + 16} y={ly - 28} width={110} height={36} rx={8}
                    fill={color} />
                  <text x={lx + 71} y={ly - 4} textAnchor="middle"
                    fontFamily={T.font} fontSize={18} fontWeight={700} fill="#fff">
                    {endpointLabel}
                  </text>
                </g>
              )}
            </g>
          );
        })()}
        {/* X labels */}
        {labels.map((lb, i) => {
          if (i % Math.max(1, Math.ceil(labels.length / 6)) !== 0) return null;
          const [x] = scale(data, i, min, max);
          return (
            <text key={i} x={x} y={H - 14} textAnchor="middle"
              fontFamily={T.font} fontSize={16} fontWeight={500} fill={T.inkMuted}>
              {lb}
            </text>
          );
        })}
      </svg>
    </ChartCard>
  );
};

// === 2. AreaChart — Compound Interest (Graph Atlas #5) ===
export const AreaChart: React.FC<{
  data: number[]; secondaryData?: number[];
  title?: string; subtitle?: string; source?: string;
}> = ({
  data, secondaryData,
  title = "Compound Interest", subtitle = "Small contributions grow over time with compounding.",
  source,
}) => {
  const frame = useCurrentFrame();
  const draw = interpolate(frame, [8, 50], [0, 1], { ...CLAMP, easing: expo });
  const fillOp = interpolate(frame, [40, 70], [0, 1], CLAMP);

  const d = linePath(data);
  const min = 0; const max = Math.max(...data, ...(secondaryData || [0]));
  const [fx] = scale(data, data.length - 1, min, max);
  const area = `${d} L${fx.toFixed(1)},${(H - PAD).toFixed(1)} L${PAD},${(H - PAD).toFixed(1)} Z`;

  const d2 = secondaryData ? linePath(secondaryData) : "";
  const [fx2] = secondaryData ? scale(secondaryData, secondaryData.length - 1, min, max) : [0];
  const area2 = secondaryData ? `${d2} L${fx2.toFixed(1)},${(H - PAD).toFixed(1)} L${PAD},${(H - PAD).toFixed(1)} Z` : "";

  return (
    <ChartCard title={title} subtitle={subtitle} source={source} units="USD" date="Illustrative">
      {/* Legend */}
      <div style={{ display: "flex", gap: 24, marginBottom: 16, fontFamily: T.font, fontSize: 18 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{ width: 16, height: 16, borderRadius: "50%", background: T.primary }} />
          <span style={{ fontWeight: 500 }}>With compound interest</span>
        </div>
        {secondaryData && (
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{ width: 16, height: 16, borderRadius: "50%", background: T.teal }} />
            <span style={{ fontWeight: 500 }}>Principal only</span>
          </div>
        )}
      </div>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        <defs>
          <linearGradient id="areaPrimary" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={T.primary} stopOpacity={0.25} />
            <stop offset="100%" stopColor={T.primary} stopOpacity={0.02} />
          </linearGradient>
          <linearGradient id="areaSecondary" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={T.teal} stopOpacity={0.20} />
            <stop offset="100%" stopColor={T.teal} stopOpacity={0.02} />
          </linearGradient>
          <clipPath id="areaClip">
            <rect x={PAD} y={0} width={(W - PAD * 2) * draw} height={H} />
          </clipPath>
        </defs>
        {[0.2, 0.4, 0.6, 0.8].map((t) => (
          <line key={t} x1={PAD} x2={W - PAD} y1={H * t} y2={H * t} stroke="#DCE6FF" strokeWidth={1} />
        ))}
        <g clipPath="url(#areaClip)">
          {secondaryData && <path d={area2} fill="url(#areaSecondary)" opacity={fillOp} />}
          <path d={area} fill="url(#areaPrimary)" opacity={fillOp} />
          <path d={d} fill="none" stroke={T.primary} strokeWidth={3} strokeLinecap="round" />
          {secondaryData && <path d={d2} fill="none" stroke={T.teal} strokeWidth={2.5} strokeLinecap="round" />}
        </g>
        {/* Y labels */}
        {[0, 0.5, 1].map((t) => {
          const val = max * t;
          const y = H - PAD - t * (H - PAD * 2);
          return (
            <text key={t} x={PAD - 12} y={y + 6} textAnchor="end"
              fontFamily={T.font} fontSize={16} fontWeight={500} fill={T.inkMuted}>
              ${Math.round(val / 1000)}k
            </text>
          );
        })}
      </svg>
    </ChartCard>
  );
};

// === 3. BarChart — Monthly Spending (Graph Atlas #2) ===
export const BarChart: React.FC<{
  data: { label: string; value: number }[];
  title?: string; subtitle?: string; source?: string;
}> = ({
  data,
  title = "Monthly Spending", subtitle = "See where your money goes each month.",
  source,
}) => {
  const frame = useCurrentFrame();
  const max = Math.max(...data.map((d) => d.value));
  const bw = (W - PAD * 2) / data.length;

  return (
    <ChartCard title={title} subtitle={subtitle} source={source} units="USD">
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        {[0.25, 0.5, 0.75, 1].map((t) => {
          const y = H - PAD - t * (H - PAD * 2);
          const val = max * t;
          return (
            <g key={t}>
              <line x1={PAD} x2={W - PAD} y1={y} y2={y} stroke="#DCE6FF" strokeWidth={1} />
              <text x={PAD - 12} y={y + 6} textAnchor="end"
                fontFamily={T.font} fontSize={16} fontWeight={500} fill={T.inkMuted}>
                ${Math.round(val).toLocaleString()}
              </text>
            </g>
          );
        })}
        {data.map((d, i) => {
          const h = ((H - PAD * 2) * d.value) / max;
          const p = interpolate(frame, [8 + i * 7, 30 + i * 7], [0, 1], { ...CLAMP, easing: expo });
          const x = PAD + i * bw + bw * 0.22;
          const w = bw * 0.56;
          const op = interpolate(frame, [8 + i * 7, 16 + i * 7], [0, 1], CLAMP);
          // Gradient: blue for first, fading to gray
          const color = i === 0 ? T.primary : i === 1 ? T.cyan : i === 2 ? T.lavender : "#C5D0E8";
          return (
            <g key={d.label} opacity={op}>
              <rect x={x} y={H - PAD - h * p} width={w} height={Math.max(0.1, h * p)} rx={8} fill={color} />
              {p > 0.9 && (
                <text x={x + w / 2} y={H - PAD - h - 12} textAnchor="middle"
                  fontFamily={T.font} fontSize={20} fontWeight={700} fill={T.ink}>
                  ${d.value.toLocaleString()}
                </text>
              )}
              <text x={x + w / 2} y={H - 14} textAnchor="middle"
                fontFamily={T.font} fontSize={18} fontWeight={500} fill={T.inkMuted}>
                {d.label}
              </text>
            </g>
          );
        })}
      </svg>
    </ChartCard>
  );
};

// === 4. ComparisonBars — Scenario Comparison (Graph Atlas #9) ===
export const ComparisonBars: React.FC<{
  left: { label: string; value: number };
  right: { label: string; value: number };
  title?: string; subtitle?: string;
}> = ({ left, right, title = "Scenario Comparison", subtitle = "Different assumptions. Different outcomes." }) => {
  const frame = useCurrentFrame();
  const max = Math.max(left.value, right.value);
  const pL = interpolate(frame, [8, 30], [0, 1], { ...CLAMP, easing: expo });
  const pR = interpolate(frame, [18, 40], [0, 1], { ...CLAMP, easing: expo });

  const Bar = ({ item, p, color, x }: any) => {
    const h = ((H - 120) * item.value) / max;
    return (
      <g>
        <rect x={x} y={H - 80 - h * p} width={120} height={Math.max(0.1, h * p)} rx={10} fill={color} />
        {p > 0.9 && (
          <text x={x + 60} y={H - 88 - h} textAnchor="middle"
            fontFamily={T.font} fontSize={22} fontWeight={800} fill={T.ink}>
            ${item.value.toLocaleString()}
          </text>
        )}
        <text x={x + 60} y={H - 40} textAnchor="middle"
          fontFamily={T.font} fontSize={18} fontWeight={600} fill={T.ink}>
          {item.label}
        </text>
      </g>
    );
  };

  return (
    <ChartCard title={title} subtitle={subtitle} units="USD">
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        <Bar item={left} p={pL} color={T.teal} x={W / 2 - 160} />
        <Bar item={right} p={pR} color={T.primary} x={W / 2 + 40} />
      </svg>
      <div style={{ fontFamily: T.font, fontSize: 15, color: T.inkMuted, fontStyle: "italic", marginTop: 12, textAlign: "center" }}>
        Hypothetical results. Not a guarantee of future performance.
      </div>
    </ChartCard>
  );
};

// === 5. DonutChart — Budget Allocation (Graph Atlas #3) ===
export const DonutChart: React.FC<{
  segments: { label: string; value: number; color?: string }[];
  title?: string; subtitle?: string; centerLabel?: string; centerValue?: string;
}> = ({
  segments,
  title = "Budget Allocation", subtitle = "A balanced budget helps you reach your goals.",
  centerLabel = "Total", centerValue,
}) => {
  const frame = useCurrentFrame();
  const total = segments.reduce((s, seg) => s + seg.value, 0);
  const colors = [T.primary, T.cyan, T.lavender, T.teal, "#C5D0E8"];

  const R = 130; const IR = 85; const CX = 220; const CY = 210;
  let angle = -90;

  const segs = segments.map((seg, i) => {
    const pct = seg.value / total;
    const sweep = pct * 360;
    const startAngle = angle;
    angle += sweep;

    const p = interpolate(frame, [10 + i * 8, 32 + i * 8], [0, 1], { ...CLAMP, easing: Easing.inOut(Easing.ease) });
    const currentSweep = sweep * p;

    const x1 = CX + R * Math.cos((startAngle * Math.PI) / 180);
    const y1 = CY + R * Math.sin((startAngle * Math.PI) / 180);
    const x2 = CX + R * Math.cos(((startAngle + currentSweep) * Math.PI) / 180);
    const y2 = CY + R * Math.sin(((startAngle + currentSweep) * Math.PI) / 180);
    const x3 = CX + IR * Math.cos(((startAngle + currentSweep) * Math.PI) / 180);
    const y3 = CY + IR * Math.sin(((startAngle + currentSweep) * Math.PI) / 180);
    const x4 = CX + IR * Math.cos((startAngle * Math.PI) / 180);
    const y4 = CY + IR * Math.sin((startAngle * Math.PI) / 180);

    const large = currentSweep > 180 ? 1 : 0;
    const d = `M${x1},${y1} A${R},${R} 0 ${large},1 ${x2},${y2} L${x3},${y3} A${IR},${IR} 0 ${large},0 ${x4},${y4} Z`;

    // Label position
    const midAngle = startAngle + sweep / 2;
    const lx = CX + (R + 32) * Math.cos((midAngle * Math.PI) / 180);
    const ly = CY + (R + 32) * Math.sin((midAngle * Math.PI) / 180);

    return { d, seg, pct, color: seg.color || colors[i % colors.length], lx, ly, midAngle };
  });

  return (
    <ChartCard title={title} subtitle={subtitle}>
      <div style={{ display: "flex", gap: 48, alignItems: "center" }}>
        <svg width={440} height={420} viewBox="0 0 440 420">
          {segs.map((s, i) => (
            <g key={i}>
              <path d={s.d} fill={s.color} />
              {frame > 40 + i * 8 && (
                <text x={s.lx} y={s.ly} textAnchor="middle"
                  fontFamily={T.font} fontSize={18} fontWeight={700} fill={T.ink}>
                  {Math.round(s.pct * 100)}%
                </text>
              )}
            </g>
          ))}
          <text x={CX} y={CY - 8} textAnchor="middle"
            fontFamily={T.font} fontSize={18} fontWeight={500} fill={T.inkMuted}>
            {centerLabel}
          </text>
          <text x={CX} y={CY + 24} textAnchor="middle"
            fontFamily={T.font} fontSize={32} fontWeight={800} fill={T.ink}>
            {centerValue || `$${total.toLocaleString()}`}
          </text>
        </svg>
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          {segs.map((s, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 12, fontFamily: T.font, fontSize: 20 }}>
              <div style={{ width: 20, height: 20, borderRadius: "50%", background: s.color }} />
              <span style={{ fontWeight: 500, color: T.ink, minWidth: 120 }}>{s.seg.label}</span>
              <span style={{ fontWeight: 700, color: T.ink, marginLeft: "auto" }}>
                {Math.round(s.pct * 100)}%
              </span>
            </div>
          ))}
        </div>
      </div>
    </ChartCard>
  );
};

// === 6-10: Story variants (keep existing, wrapped in ChartCard) ===
export const LineChartStory: React.FC<{
  data: number[]; title: string; subtitle?: string; kpi?: string;
}> = ({ data, title, subtitle, kpi }) => (
  <LineChart data={data} title={title} subtitle={subtitle || ""} endpointLabel={kpi} />
);

export const AreaChartStory: React.FC<{
  data: number[]; title: string; subtitle?: string;
}> = ({ data, title, subtitle }) => (
  <AreaChart data={data} title={title} subtitle={subtitle || ""} />
);

export const StackedBar: React.FC<{
  groups: { label: string; stacks: { label: string; value: number; color: string }[] }[];
  title?: string; subtitle?: string;
}> = ({ groups, title = "Stacked Breakdown", subtitle = "" }) => {
  const frame = useCurrentFrame();
  const maxTotal = Math.max(...groups.map(g => g.stacks.reduce((s, x) => s + x.value, 0)));
  const bw = (W - PAD * 2) / groups.length;

  return (
    <ChartCard title={title} subtitle={subtitle} units="USD">
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        {groups.map((g, gi) => {
          const total = g.stacks.reduce((s, x) => s + x.value, 0);
          const p = interpolate(frame, [8 + gi * 8, 32 + gi * 8], [0, 1], { ...CLAMP, easing: expo });
          const x = PAD + gi * bw + bw * 0.25;
          const w = bw * 0.5;
          let yOff = 0;
          return (
            <g key={g.label}>
              {g.stacks.map((s, si) => {
                const h = ((H - PAD * 2) * s.value) / maxTotal;
                const y = H - PAD - yOff - h * p;
                yOff += h * p;
                return (
                  <rect key={si} x={x} y={y} width={w} height={Math.max(0.1, h * p)}
                    fill={s.color} rx={si === g.stacks.length - 1 ? 8 : 0} />
                );
              })}
              {p > 0.9 && (
                <text x={x + w / 2} y={H - PAD - (total / maxTotal) * (H - PAD * 2) - 12}
                  textAnchor="middle" fontFamily={T.font} fontSize={18} fontWeight={700} fill={T.ink}>
                  ${Math.round(total).toLocaleString()}
                </text>
              )}
              <text x={x + w / 2} y={H - 14} textAnchor="middle"
                fontFamily={T.font} fontSize={16} fontWeight={500} fill={T.inkMuted}>
                {g.label}
              </text>
            </g>
          );
        })}
      </svg>
      {/* Legend */}
      {groups[0] && (
        <div style={{ display: "flex", gap: 20, marginTop: 16, fontFamily: T.font, fontSize: 16 }}>
          {groups[0].stacks.map((s, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <div style={{ width: 14, height: 14, borderRadius: 4, background: s.color }} />
              <span>{s.label}</span>
            </div>
          ))}
        </div>
      )}
    </ChartCard>
  );
};

export const MultiSeriesChart: React.FC<{
  series: { label: string; data: number[]; color: string }[];
  labels?: string[]; title?: string; subtitle?: string;
}> = ({ series, labels = [], title = "Comparison", subtitle = "" }) => {
  const frame = useCurrentFrame();
  const draw = interpolate(frame, [8, 55], [0, 1], { ...CLAMP, easing: expo });
  const allData = series.flatMap(s => s.data);
  const min = Math.min(...allData); const max = Math.max(...allData);

  return (
    <ChartCard title={title} subtitle={subtitle}>
      <div style={{ display: "flex", gap: 20, marginBottom: 16, fontFamily: T.font, fontSize: 17 }}>
        {series.map((s, i) => (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{ width: 14, height: 14, borderRadius: "50%", background: s.color }} />
            <span style={{ fontWeight: 500 }}>{s.label}</span>
          </div>
        ))}
      </div>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        {[0.2, 0.4, 0.6, 0.8].map((t) => (
          <line key={t} x1={PAD} x2={W - PAD} y1={H * t} y2={H * t} stroke="#DCE6FF" strokeWidth={1} />
        ))}
        {series.map((s, si) => (
          <path key={si} d={linePath(s.data)} fill="none" stroke={s.color} strokeWidth={3}
            strokeLinecap="round" strokeDasharray={2400} strokeDashoffset={2400 * (1 - draw)} />
        ))}
      </svg>
    </ChartCard>
  );
};

export const ChartToMetric: React.FC<{
  data: number[]; metric: string; label: string; delta?: number;
}> = ({ data, metric, label, delta }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [8, 40], [0, 1], { ...CLAMP, easing: expo });

  return (
    <div style={{ display: "flex", gap: 32, alignItems: "center" }}>
      <div style={{ flex: 1 }}>
        <LineChart data={data} title="" subtitle="" />
      </div>
      <div style={{
        background: "rgba(255,255,255,0.90)", borderRadius: 24,
        border: "1px solid rgba(216,230,250,0.70)", padding: 32, minWidth: 280,
        opacity: p, transform: `translateX(${(1 - p) * 40}px)`,
      }}>
        <div style={{ fontFamily: T.font, fontSize: 20, color: T.inkMuted, fontWeight: 600 }}>{label}</div>
        <div style={{ fontFamily: T.font, fontSize: 56, fontWeight: 800, color: T.ink, marginTop: 8 }}>{metric}</div>
        {delta !== undefined && (
          <div style={{
            fontFamily: T.font, fontSize: 22, fontWeight: 700, marginTop: 12,
            color: delta >= 0 ? T.successDeep : T.negativeDeep,
          }}>
            {delta >= 0 ? "▲" : "▼"} {Math.abs(delta).toFixed(1)}%
          </div>
        )}
      </div>
    </div>
  );
};
