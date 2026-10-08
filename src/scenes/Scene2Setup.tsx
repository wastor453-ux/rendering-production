import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Backdrop, Kicker } from "../components/ui";
import { theme, fmt$ } from "../theme";

const MONTHS = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"];

export const Scene2Setup: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const DUR = 342;
  return (
    <AbsoluteFill>
      <Backdrop />
      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: 56,
        }}
      >
        <Kicker>THE PLAN</Kicker>
        <div
          style={{
            fontFamily: theme.display,
            fontWeight: 800,
            fontSize: 96,
            color: theme.text,
            textAlign: "center",
          }}
        >
          <span style={{ color: theme.neon, textShadow: `0 0 50px ${theme.neon}` }}>
            $500
          </span>{" "}
          every single month
        </div>
        {/* month blocks fill progressively across the scene */}
        <div style={{ display: "flex", gap: 18 }}>
          {MONTHS.map((m, i) => {
            const onAt = 60 + (i * (DUR - 140)) / 12;
            const s = spring({
              frame: frame - onAt,
              fps,
              config: { damping: 13, stiffness: 260 },
            });
            const on = frame >= onAt;
            const scaleY = interpolate(s, [0, 1], [0.15, 1]);
            const h = interpolate(s, [0, 1], [60, 200]);
            return (
              <div
                key={i}
                style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 12 }}
              >
                <div
                  style={{
                    width: 92,
                    height: 200,
                    borderRadius: 18,
                    background: theme.panel,
                    border: `2px solid ${theme.panelBorder}`,
                    display: "flex",
                    alignItems: "flex-end",
                    justifyContent: "center",
                    overflow: "hidden",
                  }}
                >
                  <div
                    style={{
                      width: "100%",
                      height: on ? h : 0,
                      transform: `scaleY(${on ? Math.max(scaleY, 0.01) : 0.01})`,
                      transformOrigin: "bottom",
                      background: on
                        ? `linear-gradient(180deg, ${theme.neon}, #00B36B)`
                        : "transparent",
                      boxShadow: on ? `0 0 34px ${theme.neon}88` : undefined,
                      borderRadius: 12,
                    }}
                  />
                </div>
                <div
                  style={{
                    fontFamily: theme.body,
                    fontSize: 28,
                    fontWeight: 700,
                    color: on ? theme.neon : theme.dim,
                  }}
                >
                  {m}
                </div>
              </div>
            );
          })}
        </div>
        {/* running total */}
        <div
          style={{
            fontFamily: theme.display,
            fontWeight: 800,
            fontSize: 72,
            color: theme.text,
            fontVariantNumeric: "tabular-nums",
          }}
        >
          {fmt$(
            interpolate(frame, [60, DUR - 40], [0, 6000], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.out(Easing.exp),
            })
          )}{" "}
          <span style={{ fontSize: 36, color: theme.muted, fontWeight: 600 }}>
            in one year — on autopilot
          </span>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
