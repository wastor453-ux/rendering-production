const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");

test("visual mode registry has a non-empty, unique set of mode IDs", () => {
  const schema = JSON.parse(fs.readFileSync(path.join(root, "src/visual_mode_schema.json"), "utf8"));
  assert.equal(typeof schema.schema_version, "string");
  assert.ok(Array.isArray(schema.modes) && schema.modes.length > 0, "modes must be a non-empty array");
  const ids = schema.modes.map((mode) => mode.id);
  assert.ok(ids.every((id) => typeof id === "string" && id.trim().length > 0), "every mode needs an ID");
  assert.equal(new Set(ids).size, ids.length, "mode IDs must be unique");
  for (const mode of schema.modes) {
    assert.ok(typeof mode.family === "string" && mode.family.length > 0, `${mode.id}: family is required`);
    assert.ok(Array.isArray(mode.verbs), `${mode.id}: verbs must be an array`);
    assert.ok(Array.isArray(mode.best_for), `${mode.id}: best_for must be an array`);
  }
});

test("package test command cannot be the default placeholder failure", () => {
  const pkg = JSON.parse(fs.readFileSync(path.join(root, "package.json"), "utf8"));
  assert.match(pkg.scripts.test, /node --test/);
  assert.doesNotMatch(pkg.scripts.test, /no test specified|exit 1/);
});
