/**
 * Stress-test driver. Geometry mirrors src/stress/StressTest.tsx.
 * Usage: node tools/emit_layout_frames.js
 * Output: layout_manifest_stress.json
 */
const fs = require("fs");
const path = require("path");
const { emitLayout } = require("./layout_aabb_lib");

const ELEMENTS = [
  { id: "card-alex", x: 80,  y: 296, w: 856, h: 480, startFrame: 15 },
  { id: "card-ben",  x: 984, y: 296, w: 856, h: 480, startFrame: 25 },
];
const FRAMES = [20, 40, 75, 110, 149]; // inflection indices per the physics spec

const manifest = {
  ...emitLayout(ELEMENTS, FRAMES),
  // NOTE: the stress scene carries no cumulative data series, so dataSeries
  // is intentionally absent — the validator skips monotonicity rather than
  // checking fabricated values.
};

const out = path.join(__dirname, "..", "layout_manifest_stress.json");
fs.writeFileSync(out, JSON.stringify(manifest, null, 1));
console.log("wrote", out);
for (const lf of manifest.layoutFrames) {
  console.log(
    `frame ${lf.frame}:`,
    lf.elements.map((e) => `${e.id} [${e.x1},${e.y1} → ${e.x2},${e.y2}]`).join("  ")
  );
}
