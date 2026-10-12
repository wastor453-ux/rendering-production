// Visual System v2.0 — from Hamza's A-to-Z Visual Package (2026-10-12)
// Light Premium Fintech • Atmospheric Blur Backgrounds
// Source: HousingBroke_Visual_System_A_to_Z_v1 (texts/names removed, visual DNA only)
//
// COLOR TOKENS (from reference boards):
//   Navy #102044 = primary text, titles, axes
//   Primary Blue #3478F6 = core data, emphasis, focus
//   Cyan #31B9F4 = secondary data, highlights
//   Teal #18BFAE = positive / alternate series
//   Lavender #8C7BFF = secondary category, soft glow
//   Fog #EAF1FF = cool surface tint
//   White #FFFFFF = glass card face
//   Coral #F27D8C = negative values ONLY, sparingly
//
// BACKGROUND (5-layer atmospheric recipe):
//   Layer 01 — Base wash: #F8FBFF → #F1F6FF → #EFEDFF (135° linear, never flat)
//   Layer 02 — Blue bloom: radial at 9%/9%, #5393FF at 24% opacity, blur 100-180px
//   Layer 03 — Lavender bloom: radial at 92%/24%, #8C7BFF at 16% opacity, blur 120-220px
//   Layer 04 — Cyan bloom: radial at 66%/100%, #31B9F4 at 12% opacity, blur 100-180px
//   Layer 05 — Fine mist: optional faint curves, opacity 3-9%, blur 8-24px
//
// GLASS PANELS:
//   Face: white at 86-94% opacity
//   Corner radius: 18-28px (at 1920x1080)
//   Border: 1-1.5px #D8E6FA at 50-80% opacity
//   Shadow: 0 10px 30px rgba(40,85,170,0.06-0.10) — soft, cool-tinted, no dark drops
//   Backdrop blur: 16-28px (only where background visible through panel)
//
// TYPOGRAPHY (Inter first, Manrope alternate):
//   Main hook: 52-76px Bold/700 — one dominant thought, 1-3 short lines
//   Scene heading: 30-42px Semibold/600
//   Card title: 22-28px Semibold/600
//   Body: 18-22px Regular/400
//   Axis/legend: 16-18px minimum Medium/500
//
// RULES:
//   - Background is ALWAYS atmospheric, NEVER flat solid fill
//   - Foreground (text, charts, icons) is ALWAYS crisp, 0px blur
//   - One clear focal point per scene; white space is a design element
//   - Color roles are locked: blue=primary, cyan/teal=comparison, coral=negative only
//   - Motion: 0.5-1.0s ease-out, one movement at a time, end on stable frame

export const T = {
  // === Core (from ZIP) ===
  navy: "#102044",
  primary: "#3478F6",
  cyan: "#31B9F4",
  teal: "#18BFAE",
  lavender: "#8C7BFF",
  fog: "#EAF1FF",
  white: "#FFFFFF",
  coral: "#F27D8C",

  // === Semantic aliases (backward compatible) ===
  canvas: "#F8FBFF",
  canvasAlt: "#EFF5FF",
  canvasDeep: "#EFEDFF",
  ink: "#102044",
  inkMuted: "#5E6B82",
  primaryDeep: "#2A5FD9",
  blueTint: "#DCE6FF",
  success: "#18BFAE",
  successTint: "#DDF7EC",
  successDeep: "#0E7A6B",
  warning: "#F2B35D",
  warningTint: "#FFF0D7",
  negative: "#F27D8C",
  negativeTint: "#FFE2E2",
  negativeDeep: "#C45A6A",

  // === Glass (from ZIP panel recipe) ===
  glassFill: "rgba(255,255,255,0.90)",
  glassBorder: "rgba(216,230,250,0.70)",
  glassShadow: "0 10px 30px rgba(40,85,170,0.08), inset 0 1px 0 rgba(255,255,255,0.95)",
  glassBlur: 20,

  // === Background blooms (from ZIP 5-layer recipe) ===
  bloomBlue: "#5393FF",
  bloomBlueOpacity: 0.24,
  bloomLavenderOpacity: 0.16,
  bloomCyanOpacity: 0.12,

  // === Typography ===
  font: "'Inter', 'Manrope', Arial, sans-serif",
  radiusS: 12,
  radiusM: 18,
  radiusL: 24,
} as const;

// === Motion (from ZIP motion grammar) ===
export const EXPO = [0.16, 1, 0.3, 1] as const;
export const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// Motion timing defaults (seconds at 30fps)
export const MOTION = {
  lineDraw: { min: 15, max: 30 },      // 0.5-1.0s
  barRise: { min: 15, max: 24 },       // 0.5-0.8s
  countUp: { min: 18, max: 30 },       // 0.6-1.0s
  cardReveal: { min: 12, max: 24 },    // 0.4-0.8s
  sceneTransition: { min: 9, max: 24 }, // 0.3-0.8s
} as const;

// Type scale (at 1920x1080)
export const TYPE = {
  hook: { min: 52, max: 76, weight: 700 },
  heading: { min: 30, max: 42, weight: 600 },
  cardTitle: { min: 22, max: 28, weight: 600 },
  body: { min: 18, max: 22, weight: 400 },
  axis: { min: 16, max: 18, weight: 500 },
} as const;
