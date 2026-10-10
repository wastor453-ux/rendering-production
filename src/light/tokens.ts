// Light Premium Fintech — design tokens (from crackit/design_tokens.json v1.0)
// Single source of truth for all light renderer components.
export const T = {
  canvas: "#F8FAFF",
  canvasAlt: "#EEF3FA",
  ink: "#10213F",
  inkMuted: "#5E6B82",
  primary: "#5368F7",
  primaryDeep: "#3E55D9",
  lavender: "#C9D0FF",
  blueTint: "#DCE6FF",
  success: "#51C59A",
  successTint: "#DDF7EC",
  successDeep: "#1E7F5C",
  warning: "#F2B35D",
  warningTint: "#FFF0D7",
  negative: "#EE8A8A",
  negativeTint: "#FFE2E2",
  negativeDeep: "#B44A4A",
  accentPeach: "#F7C6B7",
  glassFill: "rgba(255,255,255,0.86)",
  glassBorder: "rgba(128,146,192,0.62)",
  glassShadow: "0 26px 72px rgba(71,91,140,0.18), inset 0 1px 0 rgba(255,255,255,0.95)",
  font: "'Plus Jakarta Sans', Arial, sans-serif",
  radiusS: 12,
  radiusM: 18,
  radiusL: 24,
} as const;

export const EXPO = [0.16, 1, 0.3, 1] as const;
export const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
