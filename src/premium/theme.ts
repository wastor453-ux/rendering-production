// Premium SaaS / Apple-Stripe motion system — Astor Legacy
// Hamza's locked visual identity (2026-10-07). Supersedes all previous styles.
import "@fontsource/plus-jakarta-sans/400.css";
import "@fontsource/plus-jakarta-sans/600.css";
import "@fontsource/plus-jakarta-sans/700.css";
import "@fontsource/plus-jakarta-sans/800.css";

export const P = {
  // Mesh gradient anchors
  indigo: "#1E1B4B",
  purple: "#7C3AED",
  neonBlue: "#38BDF8",
  magenta: "#EC4899",
  deepBg: "#0F0D24",
  // Glass card
  glassFill: "rgba(255,255,255,0.85)",
  glassBorder: "rgba(255,255,255,0.45)",
  glassRadius: 28,
  glassBlur: 25,
  // Type
  font: "'Plus Jakarta Sans', sans-serif",
  ink: "#14121F",
  muted: "#5B5870",
  // Semantic
  loss: "#E5484D",
  gain: "#16A34A",
  gold: "#F5B301",
  // Motion
  easeOutExpo: [0.16, 1, 0.3, 1] as const,
};

export const fmt$ = (n: number) =>
  "$" + Math.round(n).toLocaleString("en-US");
