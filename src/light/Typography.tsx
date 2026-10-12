/**
 * Typography.tsx — Explicit semantic typography roles.
 * 
 * Each component declares its semantic role. The validator checks
 * that the role is valid and the size is within the role's range.
 * No weight-based inference.
 */

import React from "react";
import { TYPE, T } from "./tokens";

type Role = keyof typeof TYPE;

interface TypeProps {
  children: React.ReactNode;
  size?: number; // Override within role range (validated)
  style?: React.CSSProperties;
  role: Role; // Explicit semantic role
}

function TypeText({ children, size, style, role }: TypeProps) {
  const spec = TYPE[role];
  // Use size override if provided, else use role's max (or min for hook)
  const fontSize = size ?? (role === "hook" ? spec.min + 12 : spec.max);
  
  // Validate at render time (fail-closed in dev)
  if (fontSize < spec.min || fontSize > spec.max) {
    throw new Error(
      `Typography role "${role}" size ${fontSize}px out of range [${spec.min}-${spec.max}]`
    );
  }
  
  return (
    <div
      data-typography-role={role}
      style={{
        fontFamily: T.font,
        fontSize,
        fontWeight: spec.weight,
        ...style,
      }}
    >
      {children}
    </div>
  );
}

// Explicit role components
export const Hook = (p: Omit<TypeProps, "role">) => <TypeText {...p} role="hook" />;
export const Heading = (p: Omit<TypeProps, "role">) => <TypeText {...p} role="heading" />;
export const CardTitle = (p: Omit<TypeProps, "role">) => <TypeText {...p} role="cardTitle" />;
export const Body = (p: Omit<TypeProps, "role">) => <TypeText {...p} role="body" />;
export const Axis = (p: Omit<TypeProps, "role">) => <TypeText {...p} role="axis" />;
export const Caption = (p: Omit<TypeProps, "role">) => <TypeText {...p} role="caption" />;
