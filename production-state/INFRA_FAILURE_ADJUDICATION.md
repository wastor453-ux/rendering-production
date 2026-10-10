# Render-Infrastructure Test Failures — Final Adjudication (2026-10-10)

Local verification closure. Each failure was traced to its root cause and
adjudicated. No test was weakened: all assertions stand as written.

## 1. `test_push_script_includes_all_scripts` — `assembly_contract.py` not in push script

**Trace:** `.github/scripts/assembly_contract.py` is imported only by
`tests/test_render_safety.py` (local). The two workflow references are comments
documenting it as the contract authority, not imports. No GitHub job executes
it; the q002 workflow runs no tests. It is not required by the supported
production path.
**Ruling:** correctly excluded from `push_p40_branch.py` FILES per the
production-path requirement rule. The test fires as designed; the firing is
adjudicated, not a defect. Revisit only if `test_render_safety.py` is ever
added to the pushed test set.

## 2. `test_push_script_includes_all_workflows` — `cleanup-artifacts.yml` not in push script

**Trace:** `.github/workflows/cleanup-artifacts.yml` ("Cleanup Old Artifacts",
trigger `workflow_run` on completed Render Production runs) deletes artifacts
beyond the 10 newest **repo-wide** — it does not implement Hamza's approved
run-history policy (keep 10 latest *Render Production* runs, delete the oldest
on the 11th), and the draft that does (`drafts/cleanup-runs.yml`) is
unapproved. It is not an approved workflow in the intended push scope.
**Ruling:** correctly excluded. Separate production-relevant finding: the
overbroad cleanup is the likely cause of the Q-004 chunk loss (runs
37990979375/37985185686 now have zero artifacts), which directly undermines
the assembly-only recovery law. Recommend Hamza rule on the cleanup scope
before any further production chunks are rendered.

## 3. `test_no_creative_files_in_patch` — `src/light/select.ts` in working-tree diff

**Trace:** `git diff HEAD --name-only` shows `src/light/select.ts` (D2
plan-authority + mandatory challenge + log-only disputes, R-2/R-3 evidence
work). Per Hamza's scope rule this work is intentional, uncommitted scope
awaiting his review; disagreements stay log-only, R-4 throw not activated
(verified: throw site still commented, `grep -c "throw new Error"` == 1 pre-existing).
**Ruling:** intentional scope, preserved. The failure is self-resolving: it
clears when the D2 work is committed after Hamza's approval. Not a defect.

## Standing

All three tests remain active tripwires. None was edited, skipped, or relaxed.
