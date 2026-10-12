// components_v2.tsx — Visual System v2.0 Missing Components
// Built from Hamza's A-to-Z Visual Package (all 4 reference images)
// 21 components catalogued in VISUAL_ESSENTIALS.md
//
// Section A: Reusable UI Components (9)
// Section B: Animation Behaviors (4 new)
// Story Diagrams (8)

import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { T, CLAMP } from "./tokens";
import { GlassCard, Kicker, entry } from "./primitives";

// ============================================================================
// SECTION A: REUSABLE ON-SCREEN COMPONENTS (from Motion Grammar image)
// ============================================================================

/** #28 — KPI Card with sparkline (large number + delta + mini chart) */
export const KPICard: React.FC<{
  label: string; value: string; delta?: number; deltaPeriod?: string;
  sparkData?: number[]; width?: number;
}> = ({ label, value, delta, deltaPeriod = "(30d)", sparkData = [], width = 420 }) => {
  const max = Math.max(...sparkData, 1);
  const min = Math.min(...sparkData, 0);
  const range = max - min || 1;
  const points = sparkData.map((v, i) =>
    `${(i / (sparkData.length - 1)) * 180},${40 - ((v - min) / range) * 32}`
  ).join(" ");

  return (
    <GlassCard width={width} padding={28}>
      <div style={{ fontFamily: T.font, fontSize: 20, fontWeight: 600, color: T.inkMuted }}>{label}</div>
      <div style={{ fontFamily: T.font, fontSize: 52, fontWeight: 800, color: T.ink, marginTop: 8, letterSpacing: -1 }}>
        {value}
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 16, marginTop: 12 }}>
        {delta !== undefined && (
          <span style={{
            fontFamily: T.font, fontSize: 22, fontWeight: 700,
            color: delta >= 0 ? T.successDeep : T.negativeDeep,
          }}>
            {delta >= 0 ? "▲" : "▼"} {Math.abs(delta).toFixed(1)}%
            <span style={{ fontWeight: 500, color: T.inkMuted, marginLeft: 6 }}>{deltaPeriod}</span>
          </span>
        )}
        {sparkData.length > 1 && (
          <svg width="180" height="40" style={{ marginLeft: "auto" }}>
            <polyline points={points} fill="none" stroke={T.primary} strokeWidth="2.5" />
          </svg>
        )}
      </div>
    </GlassCard>
  );
};

/** #29 — Source + Date Label (pill with calendar icon) */
export const SourceDateLabel: React.FC<{ source: string; date: string }> = ({ source, date }) => (
  <div style={{
    display: "inline-flex", alignItems: "center", gap: 12,
    fontFamily: T.font, fontSize: 18, fontWeight: 500, color: T.ink,
    background: "rgba(255,255,255,0.70)", border: `1px solid ${T.glassBorder}`,
    borderRadius: 999, padding: "12px 24px",
  }}>
    <span style={{ fontSize: 22 }}>📅</span>
    <span><strong>Source:</strong> {source}</span>
    <span style={{ color: T.inkMuted }}><strong>As of:</strong> {date}</span>
  </div>
);

/** #30 — Chart Legend (color dots + labels + values) */
export const ChartLegend: React.FC<{ items: { color: string; label: string; value?: string }[] }> = ({ items }) => (
  <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
    {items.map((item, i) => (
      <div key={i} style={{ display: "flex", alignItems: "center", gap: 12, fontFamily: T.font, fontSize: 20 }}>
        <div style={{ width: 20, height: 20, borderRadius: "50%", background: item.color }} />
        <span style={{ fontWeight: 500, color: T.ink, minWidth: 140 }}>{item.label}</span>
        {item.value && <span style={{ fontWeight: 700, color: T.ink, marginLeft: "auto" }}>{item.value}</span>}
      </div>
    ))}
  </div>
);

/** #31 — Annotation Callout (info box with pointer line) */
export const AnnotationCallout: React.FC<{ text: string; x?: number; y?: number }> = ({ text, x = 0, y = 0 }) => (
  <div style={{ position: "relative" }}>
    <div style={{
      fontFamily: T.font, fontSize: 20, fontWeight: 500, color: T.ink,
      background: "rgba(234,241,255,0.90)", border: `1px solid ${T.blueTint}`,
      borderRadius: 16, padding: "16px 20px", maxWidth: 320,
      display: "flex", gap: 12, alignItems: "flex-start",
    }}>
      <span style={{
        width: 28, height: 28, borderRadius: "50%", background: T.primary,
        color: "white", display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 16, fontWeight: 700, flexShrink: 0,
      }}>i</span>
      <span>{text}</span>
    </div>
    {/* Pointer line */}
    <svg style={{ position: "absolute", left: "50%", top: "100%", width: 2, height: 40 }}>
      <line x1="1" y1="0" x2="1" y2="32" stroke={T.primary} strokeWidth="2" />
      <circle cx="1" cy="36" r="5" fill={T.primary} />
    </svg>
  </div>
);

/** #32 — Compare A/B Cards (with "Better" badge) */
export const CompareABCARDS: React.FC<{
  optionA: { label: string; value: string; metric: string };
  optionB: { label: string; value: string; metric: string; isBetter?: boolean };
}> = ({ optionA, optionB }) => (
  <div style={{ display: "flex", gap: 24 }}>
    {[
      { ...optionA, isBetter: false },
      { ...optionB },
    ].map((opt, i) => (
      <GlassCard key={i} width={280} padding={28} style={{
        border: opt.isBetter ? `2px solid ${T.teal}` : undefined,
        position: "relative",
      }}>
        {opt.isBetter && (
          <div style={{
            position: "absolute", top: -14, right: 20,
            background: T.teal, color: "white", fontFamily: T.font,
            fontSize: 16, fontWeight: 700, padding: "4px 16px", borderRadius: 999,
          }}>
            Better
          </div>
        )}
        <div style={{ fontFamily: T.font, fontSize: 18, fontWeight: 600, color: T.primary }}>{opt.label}</div>
        <div style={{ fontFamily: T.font, fontSize: 44, fontWeight: 800, color: T.ink, marginTop: 8 }}>{opt.value}</div>
        <div style={{ fontFamily: T.font, fontSize: 18, color: T.inkMuted, marginTop: 4 }}>{opt.metric}</div>
      </GlassCard>
    ))}
  </div>
);

/** #33 — Assumption Tag (pill with info icon) */
export const AssumptionTag: React.FC<{ text: string }> = ({ text }) => (
  <div style={{
    display: "inline-flex", alignItems: "center", gap: 10,
    fontFamily: T.font, fontSize: 18, fontWeight: 500, color: T.inkMuted,
    background: "rgba(255,255,255,0.60)", border: `1px solid ${T.glassBorder}`,
    borderRadius: 999, padding: "10px 20px",
  }}>
    <span style={{
      width: 24, height: 24, borderRadius: "50%",
      background: T.fog, color: T.primary,
      display: "flex", alignItems: "center", justifyContent: "center",
      fontSize: 14, fontWeight: 700,
    }}>A</span>
    {text}
    <span style={{ fontSize: 16 }}>ⓘ</span>
  </div>
);

/** #34 — Section Title / Lower Third */
export const SectionTitle: React.FC<{ title: string; subtitle?: string }> = ({ title, subtitle }) => (
  <div>
    <div style={{ fontFamily: T.font, fontSize: 38, fontWeight: 800, color: T.ink, letterSpacing: -0.5 }}>
      {title}
    </div>
    {subtitle && (
      <div style={{ fontFamily: T.font, fontSize: 22, fontWeight: 400, color: T.inkMuted, marginTop: 6 }}>
        {subtitle}
      </div>
    )}
    <div style={{ width: 80, height: 6, borderRadius: 3, background: `linear-gradient(90deg, ${T.primary}, ${T.cyan})`, marginTop: 12 }} />
  </div>
);

/** #35 — Key Takeaway Checklist */
export const TakeawayChecklist: React.FC<{ items: string[] }> = ({ items }) => (
  <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
    {items.map((item, i) => (
      <div key={i} style={{ display: "flex", alignItems: "center", gap: 14 }}>
        <div style={{
          width: 32, height: 32, borderRadius: "50%", background: T.teal,
          display: "flex", alignItems: "center", justifyContent: "center",
          color: "white", fontSize: 18, fontWeight: 700, flexShrink: 0,
        }}>✓</div>
        <span style={{ fontFamily: T.font, fontSize: 22, fontWeight: 500, color: T.ink }}>{item}</span>
      </div>
    ))}
  </div>
);

/** #36 — Disclaimer Strip (full-width) */
export const DisclaimerStrip: React.FC<{ text?: string }> = ({
  text = "This information is for educational purposes only and does not constitute financial advice. Past performance is not a guarantee of future results."
}) => (
  <div style={{
    display: "flex", gap: 16, alignItems: "flex-start",
    background: "rgba(234,241,255,0.60)", borderRadius: 16,
    padding: "20px 28px", width: "100%",
  }}>
    <span style={{
      width: 32, height: 32, borderRadius: "50%", background: T.primary,
      color: "white", display: "flex", alignItems: "center", justifyContent: "center",
      fontSize: 18, fontWeight: 700, flexShrink: 0,
    }}>ⓘ</span>
    <span style={{ fontFamily: T.font, fontSize: 18, color: T.inkMuted, lineHeight: 1.5 }}>{text}</span>
  </div>
);

// ============================================================================
// STORY DIAGRAMS (from Money Mechanics + Story System images)
// ============================================================================

/** #10 — Paycheck → Cash Flow diagram */
export const PaycheckFlow: React.FC<{
  income: string;
  branches: { icon: string; label: string; amount: string; pct: string; color: string }[];
}> = ({ income, branches }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 32 }}>
    <GlassCard width={240} padding={28} style={{ textAlign: "center" }}>
      <div style={{ fontSize: 48 }}>💼</div>
      <div style={{ fontFamily: T.font, fontSize: 22, fontWeight: 700, color: T.ink, marginTop: 12 }}>Paycheck</div>
      <div style={{ fontFamily: T.font, fontSize: 18, color: T.inkMuted }}>(Income)</div>
      <div style={{ fontFamily: T.font, fontSize: 20, fontWeight: 600, color: T.primary, marginTop: 8 }}>{income}</div>
    </GlassCard>
    <div style={{ fontSize: 36, color: T.primary }}>→</div>
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      {branches.map((b, i) => (
        <div key={i} style={{
          display: "flex", alignItems: "center", gap: 16,
          background: b.color, borderRadius: 16, padding: "16px 24px", minWidth: 320,
        }}>
          <span style={{ fontSize: 32 }}>{b.icon}</span>
          <div>
            <div style={{ fontFamily: T.font, fontSize: 20, fontWeight: 700, color: T.ink }}>{b.label}</div>
            <div style={{ fontFamily: T.font, fontSize: 18, color: T.inkMuted }}>{b.amount} ({b.pct})</div>
          </div>
        </div>
      ))}
    </div>
  </div>
);

/** #13 — Mortgage Payment Stack (horizontal stacked breakdown) */
export const MortgageStack: React.FC<{
  components: { label: string; sublabel: string; pct: string; color: string; width: number }[];
}> = ({ components }) => (
  <div style={{ width: "100%" }}>
    <div style={{ display: "flex", borderRadius: 16, overflow: "hidden", height: 80 }}>
      {components.map((c, i) => (
        <div key={i} style={{
          width: `${c.width}%`, background: c.color,
          display: "flex", alignItems: "center", justifyContent: "center",
          flexDirection: "column", padding: "8px",
        }}>
          <div style={{ fontFamily: T.font, fontSize: 18, fontWeight: 700, color: "white" }}>{c.label}</div>
          <div style={{ fontFamily: T.font, fontSize: 16, color: "rgba(255,255,255,0.85)" }}>{c.pct}</div>
        </div>
      ))}
    </div>
    <div style={{ marginTop: 16 }}>
      {components.map((c, i) => (
        <div key={i} style={{ display: "flex", gap: 12, fontFamily: T.font, fontSize: 18, marginTop: 6 }}>
          <div style={{ width: 16, height: 16, borderRadius: 4, background: c.color, marginTop: 4 }} />
          <span style={{ fontWeight: 600, color: T.ink }}>{c.label}</span>
          <span style={{ color: T.inkMuted }}>({c.sublabel})</span>
          <span style={{ marginLeft: "auto", fontWeight: 700, color: T.ink }}>{c.pct}</span>
        </div>
      ))}
    </div>
  </div>
);

/** #14 — Rent vs Buy comparison */
export const RentVsBuy: React.FC<{
  factors: { icon: string; label: string; sublabel: string }[];
  rentPoints: string[];
  buyPoints: string[];
}> = ({ factors, rentPoints, buyPoints }) => (
  <div>
    <div style={{
      display: "inline-block", fontFamily: T.font, fontSize: 18, fontWeight: 600,
      background: T.fog, padding: "8px 24px", borderRadius: 999, marginBottom: 20,
    }}>
      Key Factors to Consider
    </div>
    <div style={{ display: "flex", gap: 16, marginBottom: 24 }}>
      {factors.map((f, i) => (
        <GlassCard key={i} width={200} padding={20} style={{ textAlign: "center" }}>
          <div style={{ fontSize: 32 }}>{f.icon}</div>
          <div style={{ fontFamily: T.font, fontSize: 18, fontWeight: 700, color: T.ink, marginTop: 8 }}>{f.label}</div>
          <div style={{ fontFamily: T.font, fontSize: 15, color: T.inkMuted }}>{f.sublabel}</div>
        </GlassCard>
      ))}
    </div>
    <div style={{ display: "flex", gap: 24, alignItems: "center" }}>
      <GlassCard width={300} padding={24} style={{ background: "rgba(240,235,255,0.90)" }}>
        <div style={{ fontSize: 32 }}>🏠</div>
        <div style={{ fontFamily: T.font, fontSize: 24, fontWeight: 800, color: T.ink, marginTop: 8 }}>Rent</div>
        {rentPoints.map((p, i) => (
          <div key={i} style={{ fontFamily: T.font, fontSize: 17, color: T.inkMuted, marginTop: 6 }}>{p}</div>
        ))}
      </GlassCard>
      <div style={{
        width: 56, height: 56, borderRadius: "50%", background: T.fog,
        display: "flex", alignItems: "center", justifyContent: "center",
        fontFamily: T.font, fontWeight: 800, color: T.primary, flexShrink: 0,
      }}>VS</div>
      <GlassCard width={300} padding={24} style={{ background: "rgba(221,247,236,0.90)" }}>
        <div style={{ fontSize: 32 }}>🏡</div>
        <div style={{ fontFamily: T.font, fontSize: 24, fontWeight: 800, color: T.ink, marginTop: 8 }}>Buy</div>
        {buyPoints.map((p, i) => (
          <div key={i} style={{ fontFamily: T.font, fontSize: 17, color: T.inkMuted, marginTop: 6 }}>{p}</div>
        ))}
      </GlassCard>
    </div>
  </div>
);

/** #15 — Inflation Timeline (3-stage: Today → 10 years → 20 years) */
export const InflationTimeline: React.FC<{
  stages: { label: string; amount: string; items: string; icon: string }[];
}> = ({ stages }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
    {stages.map((s, i) => (
      <React.Fragment key={i}>
        <GlassCard width={220} padding={24} style={{ textAlign: "center" }}>
          <div style={{ fontFamily: T.font, fontSize: 18, fontWeight: 600, color: T.inkMuted }}>{s.label}</div>
          <div style={{ fontFamily: T.font, fontSize: 32, fontWeight: 800, color: T.ink, marginTop: 8 }}>{s.amount}</div>
          <div style={{ fontSize: 48, margin: "12px 0" }}>{s.icon}</div>
          <div style={{ fontFamily: T.font, fontSize: 18, color: T.inkMuted }}>≈ {s.items}</div>
        </GlassCard>
        {i < stages.length - 1 && (
          <div style={{ fontSize: 32, color: T.primary, flexShrink: 0 }}>→</div>
        )}
      </React.Fragment>
    ))}
  </div>
);

/** #17 — Emergency Fund Ladder (5-tier stepped progression) */
export const FundLadder: React.FC<{
  tiers: { label: string; amount: string; period: string; color: string; height: number }[];
}> = ({ tiers }) => {
  const maxHeight = Math.max(...tiers.map(t => t.height));
  return (
    <div style={{ display: "flex", alignItems: "flex-end", gap: 16 }}>
      {tiers.map((t, i) => (
        <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
          <div style={{
            width: 140, height: (t.height / maxHeight) * 200,
            background: t.color, borderRadius: "16px 16px 8px 8px",
            display: "flex", alignItems: "flex-start", justifyContent: "center", paddingTop: 16,
          }}>
            <span style={{ fontSize: 28 }}>🛡️</span>
          </div>
          <div style={{ fontFamily: T.font, fontSize: 18, fontWeight: 700, color: T.ink, textAlign: "center" }}>{t.label}</div>
          <div style={{ fontFamily: T.font, fontSize: 16, color: T.primary, fontWeight: 600 }}>{t.amount}</div>
          <div style={{ fontFamily: T.font, fontSize: 15, color: T.inkMuted }}>{t.period}</div>
        </div>
      ))}
    </div>
  );
};

/** #22 — Calculator Card (worked example with inputs) */
export const CalculatorCard: React.FC<{
  title: string;
  inputs: { label: string; value: string }[];
  results: { label: string; value: string; highlight?: boolean }[];
}> = ({ title, inputs, results }) => (
  <GlassCard width={560} padding={32}>
    <div style={{ fontFamily: T.font, fontSize: 24, fontWeight: 700, color: T.ink, marginBottom: 20 }}>{title}</div>
    <div style={{ display: "flex", flexDirection: "column", gap: 12, marginBottom: 24 }}>
      {inputs.map((inp, i) => (
        <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ fontFamily: T.font, fontSize: 19, color: T.inkMuted }}>{inp.label}</span>
          <div style={{
            fontFamily: T.font, fontSize: 19, fontWeight: 600, color: T.ink,
            background: T.fog, padding: "8px 20px", borderRadius: 10, minWidth: 120, textAlign: "right",
          }}>{inp.value}</div>
        </div>
      ))}
    </div>
    <div style={{
      background: `linear-gradient(135deg, ${T.primary}, ${T.cyan})`,
      color: "white", textAlign: "center", padding: "14px", borderRadius: 12,
      fontFamily: T.font, fontSize: 20, fontWeight: 700, marginBottom: 20,
    }}>
      Calculate
    </div>
    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      {results.map((r, i) => (
        <div key={i} style={{ display: "flex", justifyContent: "space-between" }}>
          <span style={{ fontFamily: T.font, fontSize: 19, color: T.inkMuted }}>{r.label}</span>
          <span style={{
            fontFamily: T.font, fontSize: r.highlight ? 28 : 22,
            fontWeight: 800, color: r.highlight ? T.primary : T.ink,
          }}>{r.value}</span>
        </div>
      ))}
    </div>
  </GlassCard>
);

/** #25 — Risks Grid (2×2 warning cards) */
export const RisksGrid: React.FC<{
  title?: string;
  risks: { icon: string; title: string; description: string }[];
}> = ({ title = "Important to know", risks }) => (
  <div>
    <div style={{
      display: "flex", alignItems: "center", gap: 12, marginBottom: 20,
      fontFamily: T.font, fontSize: 26, fontWeight: 800, color: T.ink,
    }}>
      <span style={{ fontSize: 32 }}>⚠️</span> {title}
    </div>
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
      {risks.map((r, i) => (
        <GlassCard key={i} width={320} padding={24}>
          <div style={{ display: "flex", gap: 14, alignItems: "flex-start" }}>
            <span style={{ fontSize: 32 }}>{r.icon}</span>
            <div>
              <div style={{ fontFamily: T.font, fontSize: 20, fontWeight: 700, color: T.ink }}>{r.title}</div>
              <div style={{ fontFamily: T.font, fontSize: 17, color: T.inkMuted, marginTop: 6 }}>{r.description}</div>
            </div>
          </div>
        </GlassCard>
      ))}
    </div>
  </div>
);

/** #26 — Action Checklist (numbered steps) */
export const ActionChecklist: React.FC<{
  title?: string;
  steps: { icon: string; title: string; description: string }[];
}> = ({ title = "Steps You Can Take", steps }) => (
  <div>
    <div style={{ fontFamily: T.font, fontSize: 28, fontWeight: 800, color: T.ink, marginBottom: 20 }}>{title}</div>
    <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
      {steps.map((s, i) => (
        <GlassCard key={i} width={560} padding={20}>
          <div style={{ display: "flex", gap: 18, alignItems: "center" }}>
            <div style={{
              width: 48, height: 48, borderRadius: "50%", background: T.primary,
              color: "white", display: "flex", alignItems: "center", justifyContent: "center",
              fontFamily: T.font, fontSize: 22, fontWeight: 800, flexShrink: 0,
            }}>{i + 1}</div>
            <span style={{ fontSize: 32 }}>{s.icon}</span>
            <div>
              <div style={{ fontFamily: T.font, fontSize: 20, fontWeight: 700, color: T.ink }}>{s.title}</div>
              <div style={{ fontFamily: T.font, fontSize: 17, color: T.inkMuted }}>{s.description}</div>
            </div>
          </div>
        </GlassCard>
      ))}
    </div>
  </div>
);

// ============================================================================
// SECTION B: ANIMATION BEHAVIORS (from Motion Grammar image)
// ============================================================================

/** #41 — Cash-Flow Arrows (animated flow between nodes) */
export const CashFlowArrows: React.FC<{
  nodes: { label: string; color: string }[];
  progress?: number;
}> = ({ nodes, progress = 1 }) => {
  const frame = useCurrentFrame();
  const p = progress !== undefined ? progress : interpolate(frame, [0, 60], [0, 1], CLAMP);
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      {nodes.map((n, i) => (
        <React.Fragment key={i}>
          <div style={{
            background: n.color, borderRadius: 12, padding: "16px 28px",
            fontFamily: T.font, fontSize: 20, fontWeight: 700, color: "white",
            opacity: p > i / nodes.length ? 1 : 0.3,
          }}>
            {n.label}
          </div>
          {i < nodes.length - 1 && (
            <div style={{
              fontSize: 28, color: T.primary,
              opacity: p > (i + 0.5) / nodes.length ? 1 : 0.2,
            }}>→</div>
          )}
        </React.Fragment>
      ))}
    </div>
  );
};

/** #42 — Debt Balance Progress (animated shrinking bar) */
export const DebtProgress: React.FC<{
  startBalance: number; currentBalance: number; label?: string;
}> = ({ startBalance, currentBalance, label = "Remaining Balance" }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [0, 60], [0, 1], { ...CLAMP, easing: Easing.out(Easing.exp) });
  const balance = startBalance - (startBalance - currentBalance) * p;
  const pct = (balance / startBalance) * 100;

  return (
    <div style={{ width: "100%" }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
        <span style={{ fontFamily: T.font, fontSize: 20, fontWeight: 600, color: T.ink }}>{label}</span>
        <span style={{ fontFamily: T.font, fontSize: 24, fontWeight: 800, color: T.ink }}>
          ${balance.toLocaleString()}
        </span>
      </div>
      <div style={{ height: 24, borderRadius: 12, background: T.fog, overflow: "hidden" }}>
        <div style={{
          height: "100%", width: `${pct}%`, borderRadius: 12,
          background: `linear-gradient(90deg, ${T.primary}, ${T.cyan})`,
        }} />
      </div>
    </div>
  );
};

/** #43 — Timeline Marker Travel (dot moves along timeline) */
export const TimelineMarker: React.FC<{
  steps: string[]; currentStep?: number;
}> = ({ steps, currentStep }) => {
  const frame = useCurrentFrame();
  const active = currentStep !== undefined ? currentStep :
    Math.min(steps.length - 1, Math.floor(interpolate(frame, [0, 90], [0, steps.length], CLAMP)));

  return (
    <div style={{ display: "flex", alignItems: "center", width: "100%" }}>
      {steps.map((s, i) => (
        <React.Fragment key={i}>
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
            <div style={{
              width: i <= active ? 36 : 24, height: i <= active ? 36 : 24,
              borderRadius: "50%",
              background: i <= active ? T.primary : T.blueTint,
              border: i === active ? `4px solid ${T.cyan}` : "none",
              display: "flex", alignItems: "center", justifyContent: "center",
              color: "white", fontFamily: T.font, fontWeight: 700, fontSize: 14,
            }}>
              {i < active ? "✓" : i + 1}
            </div>
            <span style={{
              fontFamily: T.font, fontSize: 16,
              fontWeight: i === active ? 700 : 500,
              color: i <= active ? T.ink : T.inkMuted,
            }}>{s}</span>
          </div>
          {i < steps.length - 1 && (
            <div style={{
              flex: 1, height: 4, borderRadius: 2, margin: "0 8px", marginBottom: 32,
              background: i < active ? T.primary : T.blueTint,
            }} />
          )}
        </React.Fragment>
      ))}
    </div>
  );
};

/** #44 — Highlight Reveal (spotlight on key element) */
export const HighlightReveal: React.FC<{
  children: React.ReactNode; delay?: number;
}> = ({ children, delay = 0 }) => {
  const frame = useCurrentFrame();
  const { opacity } = entry(frame, delay, 18);

  return (
    <div style={{
      position: "relative", opacity,
      padding: 4, borderRadius: 20,
      background: `linear-gradient(135deg, ${T.primary}40, ${T.cyan}40)`,
    }}>
      <div style={{ borderRadius: 16, background: "white", padding: 4 }}>
        {children}
      </div>
    </div>
  );
};
