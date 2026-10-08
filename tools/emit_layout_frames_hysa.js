/**
 * HYSA explainer (stress test 02) driver. Geometry mirrors hysa-test/TIMELINE.json.
 * Usage: node tools/emit_layout_frames_hysa.js
 * Output: hysa-test/layout_manifest_hysa.json (layoutFrames + real decay dataSeries)
 */
const fs = require("fs");
const path = require("path");
const { emitLayout } = require("./layout_aabb_lib");

const ELEMENTS = [
  { id: "card-hysa",     x: 80,  y: 320, w: 856,  h: 400, startFrame: 30 },
  { id: "card-inflation",x: 984, y: 320, w: 856,  h: 400, startFrame: 45 },
  { id: "card-chart",    x: 80,  y: 768, w: 1760, h: 232 }, // static, fade/slide only
];
const FRAMES = [40, 75, 150, 280]; // mandated audit frames

const manifest = {
  ...emitLayout(ELEMENTS, FRAMES),
  // Real displayed series: -1% real return over 5 years (100 * 0.99^y).
  // Tagged decay_metric: the validator requires velocity <= 0 (any positive
  // jump = FAIL). This is the honest direction for a loss trend — growth
  // monotonicity would reject the very data the chart is supposed to show.
  dataSeries: [
    { property: "decay_metric", step: 1, values: [100.0, 99.0, 98.01, 97.03, 96.06, 95.10] },
  ],
};

const out = path.join(__dirname, "..", "hysa-test", "layout_manifest_hysa.json");
fs.writeFileSync(out, JSON.stringify(manifest, null, 1));
console.log("wrote", out);
for (const lf of manifest.layoutFrames) {
  console.log(
    `frame ${lf.frame}:`,
    lf.elements.map((e) => `${e.id} [${e.x1},${e.y1} → ${e.x2},${e.y2}]`).join("  ")
  );
}
