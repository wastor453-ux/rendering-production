// LEGACY — RETIRED from the default finance visual path (2026-10-08).
// The permanent identity is LIGHT PREMIUM FINTECH (crackit/VISUAL_BRAIN.md,
// tokens in src/light/tokens.ts). This dark theme remains ONLY so previously
// rendered compositions (TestNewBrain, HousingBroke, etc.) keep building.
// Do NOT use for new videos.
// CrackIt faceless finance — dark neon design system
export const theme = {
  bg: "#070B12",
  bg2: "#0B111C",
  panel: "#0E1626",
  panelBorder: "#1B2740",
  grid: "rgba(56, 189, 248, 0.07)",
  neon: "#00FF9D", // primary accent — money green
  cyan: "#22D3EE", // secondary accent — data cyan
  red: "#FF4D5E", // loss / warning
  amber: "#FFB020",
  text: "#F2F5F9",
  muted: "#8A94A6",
  dim: "#4A5568",
  display: "'Space Grotesk', 'Inter', sans-serif",
  body: "'Inter', sans-serif",
};

export const fmt$ = (n: number) =>
  "$" + Math.round(n).toLocaleString("en-US");
