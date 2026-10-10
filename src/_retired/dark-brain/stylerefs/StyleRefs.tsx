import React from "react";

// Three 1920x1080 identity directions, same content, side by side.
// Rendered as one 5760x1080 still, then cropped into thirds.

const frame: React.CSSProperties = {
  width: 1920, height: 1080, position: "relative", overflow: "hidden",
  display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
};

const Tag: React.FC<{ label: string; bg: string; fg: string }> = ({ label, bg, fg }) => (
  <div style={{ position: "absolute", top: 44, left: 60, fontSize: 26, fontWeight: 800, letterSpacing: 4, color: fg, background: bg, padding: "12px 28px", borderRadius: 999, fontFamily: "Inter, sans-serif" }}>
    {label}
  </div>
);

const Desc: React.FC<{ text: string; color: string }> = ({ text, color }) => (
  <div style={{ position: "absolute", bottom: 100, left: 0, right: 0, textAlign: "center", fontSize: 30, fontWeight: 600, color, fontFamily: "Inter, sans-serif", padding: "0 120px", lineHeight: 1.5 }}>
    {text}
  </div>
);

/* ============ STYLE A — Pastel Fintech (Humphrey evolved) ============ */
const StyleA: React.FC = () => (
  <div style={{ ...frame, fontFamily: "'Plus Jakarta Sans', sans-serif", background: "#FAFAF8", color: "#1A1B25",
    backgroundImage: "radial-gradient(#E0E0EE 1.3px, transparent 1.3px)", backgroundSize: "34px 34px" }}>
    <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 10, background: "linear-gradient(90deg,#4F46E5,#8B5CF6,#4F46E5)" }} />
    <Tag label="STYLE A" bg="#EEEDFE" fg="#4F46E5" />
    <div style={{ fontSize: 32, fontWeight: 800, letterSpacing: 14, color: "#4F46E5", marginBottom: 34 }}>THE MILLION-DOLLAR HABIT</div>
    <div style={{ fontSize: 148, fontWeight: 800, lineHeight: 1.1, textAlign: "center", letterSpacing: -2 }}>
      <span style={{ color: "#4F46E5" }}>$500/month</span> for 30 years<br />
      becomes <span style={{ background: "#4F46E5", color: "#fff", padding: "4px 40px", borderRadius: 28 }}>$1,000,000</span>
    </div>
    <div style={{ display: "flex", gap: 36, marginTop: 60 }}>
      {[["START AT 25", "$1,745,504", "40 years · $500/mo · 8%", true], ["START AT 35", "$745,180", "30 years · $500/mo · 8%", false]].map(([t, v, sub, hl]) => (
        <div key={t as string} style={{ background: "#fff", borderRadius: 28, padding: "36px 50px", minWidth: 500, boxShadow: "0 14px 44px rgba(26,27,37,.08)", border: "1px solid #ECECF3" }}>
          <div style={{ fontSize: 25, fontWeight: 700, letterSpacing: 6, color: "#8A8AA3", marginBottom: 12 }}>{t}</div>
          <div style={{ fontSize: 74, fontWeight: 800, color: hl ? "#4F46E5" : "#1A1B25", fontVariantNumeric: "tabular-nums" }}>{v}</div>
          <div style={{ fontSize: 29, color: "#8A8AA3", marginTop: 8 }}>{sub}</div>
        </div>
      ))}
    </div>
    <Desc text="Friendly fintech. Soft indigo on warm paper. Approachable, modern, app-like trust." color="#6B6B85" />
    <div style={{ position: "absolute", bottom: 40, fontSize: 26, fontWeight: 800, letterSpacing: 12, color: "#B9B9D1" }}>CRACKIT FINANCE</div>
  </div>
);

/* ============ STYLE B — Editorial Trust (serif, gold) ============ */
const StyleB: React.FC = () => (
  <div style={{ ...frame, fontFamily: "Inter, sans-serif", background: "#F7F3EA", color: "#14213D" }}>
    <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 10, background: "#C9A227" }} />
    <Tag label="STYLE B" bg="#14213D" fg="#F7F3EA" />
    <div style={{ fontSize: 29, fontWeight: 600, letterSpacing: 16, color: "#8A7B4F", marginBottom: 38 }}>THE MILLION-DOLLAR HABIT</div>
    <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 136, fontWeight: 900, lineHeight: 1.12, textAlign: "center" }}>
      <span style={{ color: "#9A7B1E", fontStyle: "italic" }}>$500</span> a month, thirty years,<br />one <span style={{ color: "#9A7B1E", fontStyle: "italic" }}>million</span> dollars.
    </div>
    <div style={{ display: "flex", marginTop: 66, borderTop: "2px solid #14213D", borderBottom: "2px solid #14213D" }}>
      {[["START AT 25", "$1,745,504", "40 years · $500/mo · 8%", true], ["START AT 35", "$745,180", "30 years · $500/mo · 8%", false]].map(([t, v, sub, hl], i) => (
        <div key={t as string} style={{ padding: "36px 66px", minWidth: 540, textAlign: "center", borderLeft: i ? "1px solid #D8CFB8" : "none" }}>
          <div style={{ fontSize: 25, fontWeight: 600, letterSpacing: 8, color: "#8A7B4F", marginBottom: 14 }}>{t}</div>
          <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 80, fontWeight: 800, color: hl ? "#9A7B1E" : "#14213D", fontVariantNumeric: "tabular-nums" }}>{v}</div>
          <div style={{ fontSize: 28, color: "#6B6353", marginTop: 10 }}>{sub}</div>
        </div>
      ))}
    </div>
    <Desc text="Newspaper-grade authority. Serif headlines, gold accents, ruled lines. Reads as established and serious." color="#8A7B4F" />
    <div style={{ position: "absolute", bottom: 40, fontSize: 25, fontWeight: 600, letterSpacing: 14, color: "#8A7B4F" }}>CRACKIT FINANCE</div>
  </div>
);

/* ============ STYLE C — Swiss Minimal (emerald) ============ */
const StyleC: React.FC = () => (
  <div style={{ ...frame, fontFamily: "Inter, sans-serif", background: "#FFFFFF", color: "#0A0A0A" }}>
    <Tag label="STYLE C" bg="#0A0A0A" fg="#fff" />
    <div style={{ fontSize: 29, fontWeight: 700, letterSpacing: 12, color: "#0E7C5B", marginBottom: 42 }}>THE MILLION-DOLLAR HABIT</div>
    <div style={{ fontSize: 146, fontWeight: 800, lineHeight: 1.06, textAlign: "center", letterSpacing: -5 }}>
      $500/month × 30 years<br /><span style={{ color: "#0E7C5B" }}>= $1,000,000</span>
    </div>
    <div style={{ display: "flex", gap: 32, marginTop: 68, width: 1480 }}>
      <div style={{ flex: 1, background: "#0E7C5B", borderRadius: 20, padding: "42px 50px" }}>
        <div style={{ fontSize: 24, fontWeight: 700, letterSpacing: 5, color: "#BFE8D8", marginBottom: 14 }}>START AT 25</div>
        <div style={{ fontSize: 76, fontWeight: 800, letterSpacing: -2, color: "#fff", fontVariantNumeric: "tabular-nums" }}>$1,745,504</div>
        <div style={{ fontSize: 28, color: "#BFE8D8", marginTop: 10 }}>40 years · $500/mo · 8%</div>
      </div>
      <div style={{ flex: 1, background: "#fff", border: "1px solid #E8E8E8", borderRadius: 20, padding: "42px 50px" }}>
        <div style={{ fontSize: 24, fontWeight: 700, letterSpacing: 5, color: "#9A9A9A", marginBottom: 14 }}>START AT 35</div>
        <div style={{ fontSize: 76, fontWeight: 800, letterSpacing: -2, color: "#0A0A0A", fontVariantNumeric: "tabular-nums" }}>$745,180</div>
        <div style={{ fontSize: 28, color: "#9A9A9A", marginTop: 10 }}>30 years · $500/mo · 8%</div>
      </div>
    </div>
    <Desc text="Ultra-clean institutional. One emerald accent, hairline cards, maximum whitespace. Bank-grade minimalism." color="#9A9A9A" />
    <div style={{ position: "absolute", bottom: 40, fontSize: 25, fontWeight: 800, letterSpacing: 10, color: "#0A0A0A" }}>CRACKIT<span style={{ color: "#0E7C5B" }}>FINANCE</span></div>
  </div>
);

export const StyleRefs: React.FC = () => (
  <div style={{ display: "flex", width: 5760, height: 1080 }}>
    <StyleA /><StyleB /><StyleC />
  </div>
);
