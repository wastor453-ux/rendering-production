# 12 PARTIAL Rules — Human Judgment Requirements

**Do not relabel PASS without the evidence listed below.**

---

## P-01: Quality gate (verify-render.js before render)
- **Source:** `~/AGENTS.md` → Quality gate (2026-10-04)
- **Human judgment:** Run `node scripts/verify-render.js` manually; interpret violations in `verify-report.json`
- **Acceptance:** Script outputs PASS (not FAIL)
- **Reviewer:** Human operator (currently Cosmo)
- **Evidence for PASS:** `verify-report.json` with zero violations, dated before render
- **Why PARTIAL:** Script exists but no workflow/CI invokes it automatically

## P-02: interpolate clamp
- **Source:** `~/AGENTS.md` → Remotion lessons (2026-10-04)
- **Human judgment:** Code review — verify every `interpolate()` has `extrapolateLeft/Right: "clamp"`
- **Acceptance:** Zero unclamped interpolates in `src/`
- **Reviewer:** Code reviewer
- **Evidence for PASS:** `grep -rn "interpolate(" src/ | grep -v "extrapolate"` returns empty
- **Why PARTIAL:** Convention, not enforced by test

## P-03: Easing names
- **Source:** `~/AGENTS.md` → Remotion lessons (2026-10-04)
- **Human judgment:** Code review — verify `Easing.exp` not `Easing.expo`, `Easing.sin` not `Easing.sine`
- **Acceptance:** Zero invalid easing names in `src/`
- **Reviewer:** Code reviewer
- **Evidence for PASS:** `grep -rn "Easing.expo\|Easing.sine" src/` returns empty
- **Why PARTIAL:** Convention, not enforced by test

## P-04: Count-up snap
- **Source:** `~/AGENTS.md` → Remotion lessons (2026-10-04)
- **Human judgment:** Code review — verify counters snap to exact target at final frame
- **Acceptance:** All CountUp components snap; no `$999,023` instead of `$1,000,000`
- **Reviewer:** Code reviewer + visual spot-check
- **Evidence for PASS:** Rendered still at final frame shows exact target value
- **Why PARTIAL:** Convention, not enforced by test

## P-05: Rule chain precedence
- **Source:** `~/AGENTS.md` → Permanent rule chain v2.1.1
- **Human judgment:** Code review — verify no lower-level file weakens a higher-level gate
- **Acceptance:** No contradictions between AGENTS.md → SYSTEM_RULE_CHAIN → brains → schemas
- **Reviewer:** Human (architectural review)
- **Evidence for PASS:** RULE_OWNERSHIP_MAP.md shows no conflicts; manual review confirms
- **Why PARTIAL:** Architectural principle, not automatable

## P-06: Authority precedence (8 levels)
- **Source:** `crackit/SYSTEM_RULE_CHAIN.md` §0
- **Human judgment:** When rules conflict, apply the 8-level precedence manually
- **Acceptance:** Higher-level rule wins in all conflicts
- **Reviewer:** Human (during code review)
- **Evidence for PASS:** No unresolved conflicts in RULE_OWNERSHIP_MAP.md
- **Why PARTIAL:** Requires human judgment on conflicts

## P-07: Pipeline ordering
- **Source:** `crackit/SYSTEM_RULE_CHAIN.md` §1
- **Human judgment:** Verify stages run in order: word alignment → beats → events → visuals → SFX → music → mix → QA
- **Acceptance:** No stage skipped or reordered
- **Reviewer:** Human (production oversight)
- **Evidence for PASS:** Beat compilers are disconnected (known); manual verification of stage outputs
- **Why PARTIAL:** Compilers disconnected; pipeline is manual

## P-08: Data deserves data (Rule 1)
- **Source:** `crackit/VISUAL_BRAIN.md` §5 Rule 1
- **Human judgment:** For each beat with statistics, decide if data viz is better than headline
- **Acceptance:** ≥70% of data beats use viz (per CREATIVE_REVIEW_CRITERIA.md)
- **Reviewer:** Hamza (creative) or delegate
- **Evidence for PASS:** Beat audit showing ≥70% coverage
- **Why PARTIAL:** Requires creative judgment, not automatable

## P-09: Muted comprehension test
- **Source:** `crackit/VISUAL_BRAIN.md` §5 Rule 7
- **Human judgment:** Watch muted; can you understand each beat's main change?
- **Acceptance:** ≥80% of beats comprehensible without audio
- **Reviewer:** Hamza or delegate
- **Evidence for PASS:** Muted review checklist with per-beat pass/fail
- **Why PARTIAL:** Requires human viewing, not automatable

## P-10: No blur on reading layer
- **Source:** `crackit/VISUAL_BRAIN.md` §8
- **Human judgment:** Visual inspection — typography, numbers, charts must be crisp
- **Acceptance:** Zero blur on primary reading layer in sampled frames
- **Reviewer:** Human (visual QA)
- **Evidence for PASS:** Still inspection at 5+ timestamps, no blur found
- **Why PARTIAL:** Requires visual inspection

## P-11: Typography hierarchy
- **Source:** `crackit/VISUAL_BRAIN.md` §10
- **Human judgment:** Verify headline ≥64px, supporting ≤36px, label ≤24px; no overlap/clipping
- **Acceptance:** Clear hierarchy, zero overlap, zero clipping
- **Reviewer:** Human (visual QA)
- **Evidence for PASS:** Still inspection showing hierarchy intact
- **Why PARTIAL:** Requires visual inspection

## P-12: Phase 0-5 linear order / Focal hold / Same card
- **Source:** `crackit/EDITING_BRAIN.md` Phase 0
- **Human judgment:** Verify editorial phases run in order; focal holds ≤4.5s; no card repeated >2 beats
- **Acceptance:** All Phase 0 exit criteria met
- **Reviewer:** Human (editorial oversight)
- **Evidence for PASS:** Beat timeline review against Phase 0 checklist
- **Why PARTIAL:** Editorial judgment, not automatable

---

## Summary

All 12 require human judgment. None can be automated without losing the
judgment itself. They are PARTIAL because the human step hasn't been performed
and recorded — not because the rules are missing.
