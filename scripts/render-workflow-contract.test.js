const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const workflow = fs.readFileSync(path.join(root, ".github/workflows/render-production.yml"), "utf8");

test("production workflow has bounded defaults consistent with validation", () => {
  assert.match(workflow, /max_parallel:[\s\S]{0,120}default: '10'/);
  assert.match(workflow, /bounded\("MAX_PARALLEL", 1, 10\)/);
  assert.match(workflow, /bounded\("CRF", 0, 51\)/);
  assert.match(workflow, /at most 100000 frames/);
});

test("assembly rejects missing chunks and requires contiguous frame coverage", () => {
  assert.match(workflow, /if not metas:[\s\S]{0,80}no chunk metadata found/);
  assert.match(workflow, /cid != expected_id/);
  assert.match(workflow, /a != expected_start/);
  assert.match(workflow, /expected_start != end \+ 1/);
  assert.match(workflow, /checksum FAIL chunk/);
});

test("assembly creates a newline-delimited concat list and invokes ffmpeg", () => {
  assert.match(workflow, /out\.write\([\s\S]{0,180}\\n/);
  assert.match(workflow, /ffmpeg -y -f concat -safe 0 -i concat\.txt -c copy/);
});
