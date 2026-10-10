# Pre-existing Python Test Failures — Recorded 2026-10-10

These 3 failures exist in `tests/test_render_infra.py` and reproduce on the
clean base (verified via `git stash` — all 3 fail with my changes reverted).
They are NOT caused by the R-008/R-013 work and are NOT silently excluded;
the full suite reports them honestly. Scope is not expanded to fix them here.

## 1. test_push_script_includes_all_scripts
- **Class:** `TestPushScriptCompleteness`
- **Failure:** `AssertionError: '.github/scripts/assembly_contract.py' not found in ...`
- **Cause:** The push script's FILES list does not include every `.github/scripts/*.py`.
  The test enumerates all scripts and requires each to appear in the push script.
- **Evidence:** Reproduces on base (stashed state), independent of R-008 changes.

## 2. test_push_script_includes_all_workflows
- **Class:** `TestPushScriptCompleteness`
- **Failure:** `AssertionError: '.github/workflows/cleanup-artifacts.yml' not found in ...`
- **Cause:** The push script's FILES list does not include every `.github/workflows/*.yml`.
- **Evidence:** Reproduces on base (stashed state), independent of R-008 changes.

## 3. test_no_raw_input_interpolation_in_shell
- **Class:** `TestWorkflowContracts`
- **Failure:** `AssertionError: raw input interpolation in shell at line 235: if [ -z "${{ inputs.resume_from_run_id }}" ]; then`
- **Cause:** The workflow interpolates `${{ inputs.resume_from_run_id }}` directly in
  a shell `if` at line 235 (plan job), which the contract test forbids.
- **Evidence:** Reproduces on base (stashed state), independent of R-008 changes.

## Suite summary
- `python3 -m unittest discover -s tests`: 304 tests, 301 pass, 3 fail (all above).
- `npm test`: exit 0.
- R-008 suite (`tests/test_r008_snapshot.py`): 16/16 pass.
- R-013 suite (`tests/test_r013_guard.py`): 6/6 pass.
