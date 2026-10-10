# Unified Pre-Render Enforcement Checklist

**Derived from:** VISUAL_BRAIN.md, EDITING_BRAIN.md, SOUND_DESIGN.md, SYSTEM_RULE_CHAIN.md
**Purpose:** Single gate that must pass before any production render dispatch.
**No new laws.** Every item maps to an existing canonical source.

## How to use

Run `python3 tools/pre_render_check.py` before dispatching. It exits non-zero
on any FAIL. No bypass exists — the dispatch script calls this first.

---

## CHECKS

### 1. Visual Identity Lock
- **Source:** VISUAL_BRAIN.md §0, EDITING_BRAIN.md (Immutable locks)
- **Requirement:** Light Premium Fintech only. No dark/neon in default path.
- **Enforcer:** `tools/pre_render_check.py::check_visual_identity()`
- **Consumer:** Render workflow
- **Test:** `tests/test_pre_render.py::test_rejects_dark_identity`
- **Evidence:** `design_tokens.json` hash matches canonical

### 2. Visual Variety Law
- **Source:** VISUAL_BRAIN.md §6
- **Requirement:** ≤2 typography-led beats in a row; no composition repeated >2x
- **Enforcer:** `tools/pre_render_check.py::check_variety()`
- **Consumer:** Beat compiler
- **Test:** `tests/test_pre_render.py::test_rejects_typography_run`
- **Evidence:** `beat_timeline.json` mode sequence

### 3. Data Deserves Data
- **Source:** VISUAL_BRAIN.md §5 Rule 1
- **Requirement:** Beats with measurable statistics use data viz, not plain headline
- **Enforcer:** `tools/pre_render_check.py::check_data_viz()`
- **Consumer:** Visual selector
- **Test:** `tests/test_pre_render.py::test_rejects_headline_for_data`
- **Evidence:** Beat `visual_mode` vs `semantic_role` mapping

### 4. SFX Default Silence
- **Source:** SOUND_DESIGN.md §4, §7, §8
- **Requirement:** Selector defaults to silence; threshold 75; major-impact manual only
- **Enforcer:** `tools/select_sfx_a1.py` (fail-closed)
- **Consumer:** `tools/compile_sfx_triggers_a1.py`
- **Test:** `tests/test_select_sfx_a1.py` (15 tests)
- **Evidence:** Asset map with silence entries

### 5. SFX Mix Disabled
- **Source:** Hamza's standing order (2026-10-10)
- **Requirement:** `with_sfx_mix: false` unless explicitly authorized
- **Enforcer:** `tools/pre_render_check.py::check_sfx_mix_flag()`
- **Consumer:** Dispatch script
- **Test:** `tests/test_pre_render.py::test_rejects_sfx_mix_without_auth`
- **Evidence:** Workflow input value

### 6. No Production Render Without Authorization
- **Source:** Hamza's standing order
- **Requirement:** Explicit user authorization required for any production dispatch
- **Enforcer:** `tools/pre_render_check.py::check_authorization()`
- **Consumer:** `tools/dispatch_production.py`
- **Test:** `tests/test_pre_render.py::test_rejects_unauthorized_dispatch`
- **Evidence:** Authorization token/record

### 7. Assembly Recovery Ready
- **Source:** AGENTS.md (Render recovery law)
- **Requirement:** classify_failure.py, build_ledger.py, reassemble workflow available
- **Enforcer:** `tools/pre_render_check.py::check_recovery_tools()`
- **Consumer:** Monitor
- **Test:** `tests/test_render_safety.py` (15 tests)
- **Evidence:** Tool existence + test pass

### 8. Creative Approval (NEW 2026-10-10)
- **Source:** Hamza's order — Q004 visual direction rejected
- **Requirement:** Visual direction must have explicit approval before production render
- **Enforcer:** `tools/pre_render_check.py::check_creative_approval()`
- **Consumer:** Dispatch script
- **Test:** `tests/test_pre_render.py::test_rejects_unapproved_visuals`
- **Evidence:** Approval record with Hamza's verdict

---

## BYPASS ATTEMPTS (must all fail)

| Attempt | Expected result |
|---------|----------------|
| Set `with_sfx_mix: true` without auth | REJECT |
| Dispatch without creative approval | REJECT |
| Dark identity in composition | REJECT |
| 3+ typography beats in a row | REJECT |
| Headline for data beat | REJECT |
| Missing recovery tools | REJECT |
| Unauthorized dispatch | REJECT |
