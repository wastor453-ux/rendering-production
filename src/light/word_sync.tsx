/**
 * Word-Sync Animation Framework
 * 
 * ROOT FIX: Visuals must react to spoken words, not just scene boundaries.
 * 
 * This provides:
 * 1. useWordAt(frame, words) - get current word at frame
 * 2. WordHighlight - kinetic typography that highlights spoken words
 * 3. TimedReveal - reveal elements at specific word timestamps
 * 4. ProgressiveChart - animate chart segments as they're mentioned
 * 
 * Every visual change is driven by word timestamps, ensuring
 * millisecond-level VO/visual alignment.
 */

import React from "react";
import { useCurrentFrame, interpolate } from "remotion";
import { CLAMP } from "./tokens";

export interface WordTimestamp {
  word: string;
  start: number;  // seconds
  end: number;    // seconds
  scene_id?: string;
}

const FPS = 30;

/**
 * Get the word being spoken at a given frame.
 * Returns null if no word is active (silence/pause).
 */
export function useWordAt(frame: number, words: WordTimestamp[]): WordTimestamp | null {
  const time = frame / FPS;
  return words.find(w => time >= w.start && time < w.end) || null;
}

/**
 * Get all words spoken up to a given frame (for progressive reveals).
 */
export function useWordsUpTo(frame: number, words: WordTimestamp[]): WordTimestamp[] {
  const time = frame / FPS;
  return words.filter(w => w.start <= time);
}

/**
 * Check if a specific word (or phrase) has been spoken by a frame.
 * Use for triggering visual events at exact word moments.
 */
export function useWordSpoken(frame: number, words: WordTimestamp[], targetWord: string): boolean {
  const time = frame / FPS;
  const target = targetWord.toLowerCase().replace(/[^a-z0-9]/g, "");
  return words.some(w => {
    const clean = w.word.toLowerCase().replace(/[^a-z0-9]/g, "");
    return clean === target && w.start <= time;
  });
}

/**
 * Kinetic Typography: Display text with current word highlighted.
 * Words appear as they're spoken, current word is emphasized.
 */
export function KineticText({
  words,
  frame,
  style,
  highlightColor = "#3478F6",
  baseColor = "#102044",
}: {
  words: WordTimestamp[];
  frame: number;
  style?: React.CSSProperties;
  highlightColor?: string;
  baseColor?: string;
}) {
  const time = frame / FPS;
  
  return (
    <div style={{ ...style, lineHeight: 1.4 }}>
      {words.map((w, i) => {
        const isSpoken = w.start <= time;
        const isCurrent = time >= w.start && time < w.end;
        
        // Words fade in as they're spoken
        const opacity = isSpoken ? 1 : 0.25;
        
        // Current word gets highlighted and slightly scaled
        const scale = isCurrent ? 1.08 : 1;
        const color = isCurrent ? highlightColor : baseColor;
        const fontWeight = isCurrent ? 800 : 600;
        
        return (
          <span
            key={i}
            style={{
              opacity: interpolate(frame, [w.start * FPS - 5, w.start * FPS], [0.25, 1], CLAMP),
              color,
              fontWeight,
              transform: `scale(${scale})`,
              display: "inline-block",
              marginRight: "0.3em",
              transition: "all 0.15s ease-out",
            }}
          >
            {w.word}
          </span>
        );
      })}
    </div>
  );
}

/**
 * TimedReveal: Show children only after a specific word is spoken.
 * Use for revealing chart segments, bullet points, etc. at exact moments.
 */
export function TimedReveal({
  frame,
  words,
  triggerWord,
  children,
  animationFrames = 15,
}: {
  frame: number;
  words: WordTimestamp[];
  triggerWord: string;
  children: React.ReactNode;
  animationFrames?: number;
}) {
  const time = frame / FPS;
  const target = triggerWord.toLowerCase().replace(/[^a-z0-9]/g, "");
  
  const triggerWordData = words.find(w => 
    w.word.toLowerCase().replace(/[^a-z0-9]/g, "") === target
  );
  
  if (!triggerWordData) return null;
  
  const triggerFrame = triggerWordData.start * FPS;
  const localFrame = frame - triggerFrame;
  
  if (localFrame < 0) return null;
  
  const opacity = interpolate(localFrame, [0, animationFrames], [0, 1], CLAMP);
  const translateY = interpolate(localFrame, [0, animationFrames], [20, 0], CLAMP);
  const scale = interpolate(localFrame, [0, animationFrames], [0.95, 1], CLAMP);
  
  return (
    <div style={{ opacity, transform: `translateY(${translateY}px) scale(${scale})` }}>
      {children}
    </div>
  );
}

/**
 * ProgressiveList: Reveal list items one by one as their trigger words are spoken.
 * Each item specifies which word triggers its reveal.
 */
export function ProgressiveList({
  frame,
  words,
  items,
}: {
  frame: number;
  words: WordTimestamp[];
  items: { triggerWord: string; content: React.ReactNode }[];
}) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {items.map((item, i) => (
        <TimedReveal
          key={i}
          frame={frame}
          words={words}
          triggerWord={item.triggerWord}
        >
          {item.content}
        </TimedReveal>
      ))}
    </div>
  );
}

/**
 * Visual beat indicator: Changes every 2-4 seconds to maintain retention.
 * Returns the current beat index based on frame.
 * Use to cycle through visual variations within a scene.
 */
export function useVisualBeat(frame: number, beatDurationFrames: number = 90): number {
  // Default 90 frames = 3 seconds at 30fps
  return Math.floor(frame / beatDurationFrames);
}
