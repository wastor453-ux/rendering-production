import React from "react";

// Reference frame: "How inflation eats savings" — Hamza's pick: Style A (Pastel Fintech), exact tokens.

const INK = "#1A1B25";
const MUTED = "#8A8AA3";
const INDIGO = "#4F46E5";
const VIOLET = "#8B5CF6";
const PALE = "#EEEDFE";
const PAPER = "#FAFAF8";
const RED = "#E5484D";

export const InflationRef: React.FC = () => (
  <div
    style={{
      width: 1920, height: 1080, position: "relative", overflow: "hidden",
      background: PAPER, backgroundImage: "radial-gradient(#E0E0EE 1.3px, transparent 1.3px)",
      backgroundSize: "34px 34px", fontFamily: "'Plus Jakarta Sans', sans-serif",
      display: "flex", flexDirection: "column", alignItems: "center", paddingTop: 110,
    }}
  >
    <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 10,
      background: `linear-gradient(90deg, ${INDIGO}, ${VIOLET}, ${INDIGO})` }} />
    <div style={{ fontSize: 32, fontWeight: 800, letterSpacing: 14, color: INDIGO, marginBottom: 28 }}>
      INFLATION
    </div>
    <div style={{ fontSize: 104, fontWeight: 800, color: INK, letterSpacing: -2, marginBottom: 44 }}>
      $10,000 in savings
    </div>

    {/* main card */}
    <div
      style={{
        width: 1420, background: "#FFFFFF", borderRadius: 28, border: "1px solid #ECECF3",
        boxShadow: "0 14px 44px rgba(26,27,37,.08)", padding: "48px 60px",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 30 }}>
        <div style={{ background: INDIGO, color: "#fff", fontSize: 34, fontWeight: 800, padding: "14px 34px", borderRadius: 20 }}>
          TODAY — $10,000
        </div>
        <div style={{ fontSize: 76, fontWeight: 800, color: INK, fontVariantNumeric: "tabular-nums" }}>
          $7,441
        </div>
      </div>
      <div style={{ display: "flex", height: 72, borderRadius: 18, overflow: "hidden", background: PALE }}>
        <div style={{ width: "74.4%", background: INDIGO }} />
        <div style={{ width: "25.6%", background: RED }} />
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 18 }}>
        <span style={{ fontSize: 30, fontWeight: 700, color: INDIGO }}>Buying power left</span>
        <span style={{ fontSize: 30, fontWeight: 700, color: RED }}>Eaten by 3% inflation</span>
      </div>
    </div>

    {/* pale indigo loss card */}
    <div
      style={{
        marginTop: 36, background: PALE, borderRadius: 20, padding: "26px 54px",
        fontSize: 40, fontWeight: 800, color: INDIGO,
      }}
    >
      −$2,559 eaten by 3% inflation over 10 years
    </div>

    <div style={{ marginTop: 44, fontSize: 52, fontWeight: 800, color: INK }}>
      Your money didn't move. Its <span style={{ color: INDIGO }}>value</span> did.
    </div>
  </div>
);
