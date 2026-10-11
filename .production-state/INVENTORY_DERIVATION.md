# 23-File Inventory — Derivation and Scope

## How the inventory was derived

**Step 1:** Started from `SYSTEM_RULE_CHAIN.md` §0 (the 8-level precedence hierarchy).
This is the canonical entry point — it lists every authoritative source in order.

**Step 2:** For each of the 8 levels, resolved the file path and verified existence:
1. `~/AGENTS.md` — workspace operating constraints
2. `crackit/SYSTEM_RULE_CHAIN.md` — cross-domain ordering
3. `crackit/EDITORIAL_BRAIN.md` — editorial intent
4. `crackit/EDITORIAL_BEAT_SCHEMA.json` + `crackit/VO_EVENT_ALIGNMENT_SCHEMA.json` — machine contracts
5. `crackit/EDITING_BRAIN.md` — execution gates
6. `skills/sound-design/SOUND_DESIGN.md` + `crackit/SFX_EVENT_SCHEMA.json` — audio
7. `skills/sound-design/SKILL.md` — operator entry
8. `crackit/skill-playbook.md` + `crackit/PIPELINE.md` — stage routing

**Step 3:** Added visual identity files referenced by the brains:
- `crackit/VISUAL_BRAIN.md` (referenced by EDITING_BRAIN.md immutable locks)
- `crackit/design_tokens.json` (referenced by VISUAL_BRAIN.md §9)
- `crackit/visual_mode_schema.json` (referenced by VISUAL_BRAIN.md §3)
- `crackit/RULE_OWNERSHIP_MAP.md` (the map itself, references all above)

**Step 4:** Added demo-video enforcement files (created 2026-10-10):
- `.production-state/PRE_RENDER_CHECKLIST.md`
- `.production-state/RULE_TRACEABILITY_AUDIT.md`
- `tools/pre_render_check.py`
- `tools/select_sfx_a1.py`
- `tools/compile_sfx_triggers_a1.py`
- `tools/mix_sfx.py`
- `.github/scripts/classify_failure.py`
- `.github/scripts/build_ledger.py`

**Total: 23 files** (15 canonical + 8 enforcement)

---

## Recursive references examined

For each canonical file, followed its outbound references:
- `SYSTEM_RULE_CHAIN.md` → references all 8 levels (verified)
- `RULE_OWNERSHIP_MAP.md` → references 15 rule domains (verified)
- `VISUAL_BRAIN.md` → references `design_tokens.json`, `visual_mode_schema.json` (verified)
- `EDITING_BRAIN.md` → references `VISUAL_BRAIN.md` (verified)
- `SOUND_DESIGN.md` → references `SFX_EVENT_SCHEMA.json` (verified)

**No dangling references found.** All outbound links resolve.

---

## Workflows, scripts, tests, configuration examined

**Workflows:** `.github/workflows/render-production.yml`
- Verified: `with_sfx_mix` defaults false, `workflow_dispatch` only trigger
- Verified: no auto-publish, no auto-cleanup

**Scripts:** All files in `tools/` and `.github/scripts/` that enforce rules
- `pre_render_check.py` (gate)
- `select_sfx_a1.py` (SFX)
- `classify_failure.py`, `build_ledger.py` (recovery)

**Tests:** `tests/test_*.py` (347 tests)
- Verified: `test_pre_render.py`, `test_completeness_audit.py`, `test_select_sfx_a1.py`, `test_render_safety.py`

**Configuration:** `.production-state/authorizations/` (empty — correctly blocking)

---

## Unreferenced candidate rule files

Searched `~/workspace/crackit/` and `~/workspace/skills/` for `.md` files
not in the inventory:

| File | Status | Reason excluded |
|------|--------|-----------------|
| `ARCHITECTURE_VALIDATION_2026-10-10.md` | Informational | Audit report, not a rule source |
| `FINAL_COMPLETION_REPORT.md` | Informational | Historical report |
| `PIPELINE_DIAGNOSTIC_REPORT.md` | Informational | Diagnostic, not normative |
| `RETRAINING_2026-10-08.md` | Historical | Superseded by current brains |
| `*_retired/*` | Retired | Explicitly retired (dark brain) |

**None contain operative rules.** All are reports, history, or retired.

---

## Audit scope and limitations

**In scope:**
- All 8 levels of the rule chain precedence
- All enforcement mechanisms in demo-video
- All tests that prove enforcement
- Workflow configuration for safety flags

**Out of scope (with reason):**
- `node_modules/` — third-party, not rule sources
- `__pycache__/` — generated, not authoritative
- `.git/` — version control, not rules
- `~/workspace/your_files/` — user outputs, not rule sources
- Retired dark brain (`_retired/`) — explicitly superseded

**Limitations:**
1. **Human-judgment rules** (12 PARTIAL) cannot be proven by file existence alone.
   They require a human to perform the judgment and record evidence.
2. **Runtime behavior** (e.g., actual Remotion rendering) cannot be verified
   without executing a render, which is prohibited.
3. **Hosted proof** (GitHub Actions) is separate from local file completeness.
   This audit covers local only.
