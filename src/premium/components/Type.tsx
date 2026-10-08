import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import { P } from "../theme";

const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const expo = Easing.bezier(0.16, 1, 0.3, 1);

/** Kinetic headline — mask slide-up reveal, one accent word in gradient. */
export const KineticHeadline: React.FC<{
  lines: string[];
  accentWord?: string;
  delay?: number;
  fontSize?: number;
  color?: string;
}> = ({ lines, accentWord, delay = 0, fontSize = 96, color = "#FFFFFF" }) => {
  const frame = useCurrentFrame();
  return (
    <div style={{ fontFamily: P.font, fontWeight: 800, fontSize, lineHeight: 1.12, letterSpacing: -2 }}>
      {lines.map((line, i) => {
        const d = delay + i * 8;
        const p = interpolate(frame, [d, d + 18], [0, 1], { ...CLAMP, easing: expo });
        const y = interpolate(p, [0, 1], [110, 0], CLAMP);
        return (
          <div key={i} style={{ overflow: "hidden", paddingBottom: 6 }}>
            <div style={{ opacity: p, transform: `translateY(${y}%)` }}>
              {accentWord && line.includes(accentWord) ? (
                <span style={{ color }}>
                  {line.split(accentWord)[0]}
                  <span
                    style={{
                      background: `linear-gradient(90deg, ${P.gold}, ${P.magenta})`,
                      WebkitBackgroundClip: "text",
                      backgroundClip: "text",
                      color: "transparent",
                    }}
                  >
                    {accentWord}
                  </span>
                  {line.split(accentWord)[1]}
                </span>
              ) : (
                <span style={{ color }}>{line}</span>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};

/** UI system toast — slides/fades from screen edge. Replaces ink stamps. */
export const Toast: React.FC<{
  children: React.ReactNode;
  delay?: number;
  tone?: "warn" | "info";
}> = ({ children, delay = 0, tone = "info" }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [delay, delay + 16], [0, 1], { ...CLAMP, easing: expo });
  const x = interpolate(p, [0, 1], [80, 0], CLAMP);
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 16,
        background: P.glassFill,
        backdropFilter: `blur(${P.glassBlur}px)`,
        border: `1px solid ${P.glassBorder}`,
        borderRadius: 20,
        padding: "20px 32px",
        fontFamily: P.font,
        fontWeight: 600,
        fontSize: 36,
        color: P.ink,
        boxShadow: "0 16px 48px rgba(15,13,36,0.25)",
        opacity: p,
        transform: `translateX(${x}px)`,
      }}
    >
      <div
        style={{
          width: 44,
          height: 44,
          borderRadius: 22,
          background: tone === "warn" ? P.loss : P.neonBlue,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "#fff",
          fontSize: 26,
          fontWeight: 800,
        }}
      >
        {tone === "warn" ? "!" : "i"}
      </div>
      {children}
    </div>
  );
};
