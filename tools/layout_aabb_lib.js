/**
 * Shared layout-AABB math. Uses Remotion's REAL spring()/interpolate() —
 * the same functions the renderer evaluates — so emitted boxes match
 * rendered frames exactly.
 *
 * Element descriptor: { id, x, y, w, h, startFrame? }
 *   - Elements WITHOUT startFrame are static (no pop-in transform).
 */
const { spring, interpolate, Easing } = require("remotion");

const FPS = 30;
const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" };

// Exact replica of the popIn() helper used by the test scenes.
function popIn(frame, startFrame) {
  const f = frame - startFrame;
  const s = spring({ frame: f, fps: FPS, config: { mass: 1, tension: 180, friction: 12 } });
  const scale = interpolate(s, [0, 1], [0.6, 1], CLAMP);
  const y = interpolate(f, [0, 20], [40, 0], { ...CLAMP, easing: Easing.out(Easing.cubic) });
  return { scale, y };
}

// CSS `translateY(y) scale(s)` with default center origin:
// scale about the box center, then shift by y.
function aabb(el, frame) {
  let scale = 1, dy = 0;
  if (el.startFrame != null) {
    const p = popIn(frame, el.startFrame);
    scale = p.scale; dy = p.y;
  }
  const cx = el.x + el.w / 2;
  const cy = el.y + el.h / 2 + dy;
  const hw = (el.w / 2) * scale;
  const hh = (el.h / 2) * scale;
  const r = (v) => Math.round(v * 100) / 100;
  return { id: el.id, x1: r(cx - hw), y1: r(cy - hh), x2: r(cx + hw), y2: r(cy + hh) };
}

function emitLayout(elements, frames, fps = FPS) {
  return {
    fps,
    layoutFrames: frames.map((frame) => ({
      frame,
      elements: elements.map((el) => aabb(el, frame)),
    })),
  };
}

module.exports = { FPS, popIn, aabb, emitLayout };
