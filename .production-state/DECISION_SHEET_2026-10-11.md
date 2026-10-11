# Combined Decision Sheet — P4.4 Batch Closure (2026-10-11)

**Purpose:** One approval pass for all outstanding user decisions.
Recommended defaults provided; Hamza picks or overrides.

---

## D1. Licensed imagery / B-16

**Issue:** No licensed imagery inventory. B-22 (provenance) blocked on this.
**Options in:** `~/workspace/your_files/impact-sounds-review/index.html` (Q-001/B-16 section)
**Recommended default:** Defer licensed imagery; continue with procedural/AI-generated
visuals only. Provenance ledger (`PROVENANCE.md`) tracks all current assets as
original/procedural. Revisit when channel revenue justifies licensing.
**Decision needed:** Approve deferral, or supply licensed assets.

## D2. Q-001 definition (F-01)

**Issue:** Q-001 referenced but never defined.
**Recommended default:** Q-001 = the first quality-bar video produced under the
locked Light Premium Fintech identity, meeting all H-01 creative criteria and
B-21 encode QA bar. It is the "definition of done" reference, not a specific
video file.
**Dependency note:** This definition references D3 (B-21) and D4 (H-01). If you
modify those thresholds/criteria, the Q-001 bar shifts accordingly. Approve D2
after D3/D4, or accept that the definition tracks whatever you approve there.
**Decision needed:** Approve definition, or provide your own.

## D3. Encode QA bar (B-21)

**Draft:** `.production-state/ENCODE_QA_BAR_DRAFT.md`
**Recommended defaults:**
- 1920×1080, 30fps constant, 0 black/frozen frames
- Audio sync drift < 100ms, true peak ≤ -1 dBTP, -14 LUFS ±1, CRF 18
**Decision needed:** Approve thresholds, adjust, or add VMAF/SSIM.

## D4. Creative approval criteria (H-01)

**Draft:** `.production-state/CREATIVE_APPROVAL_CRITERIA_DRAFT.md`
**Recommended defaults:** 16 measurable criteria across layout, typography,
motion, color, and audio-visual sync. Per-scene PASS/FAIL; one FAIL rejects
the scene, not the video.
**Decision needed:** Approve criteria, or modify.

## D5. Demo acceptance checklist (H-02)

**Draft:** `.production-state/DEMO_ACCEPTANCE_CHECKLIST_DRAFT.md`
**Recommended defaults:** Pre-dispatch gates (SHA verify, composition check,
pre-render gate, no Q-004 overwrite) + post-render acceptance (chunks complete,
duration match, no black/frozen frames) + issue-finding scope rules.
**Decision needed:** Approve checklist, or modify.

## D6. Q-004 visual verdicts (F-05, F-06, F-07)

**Status:** Visual direction REJECTED 2026-10-10. Three isolated defects fixed
(text overlap, headline clipping, $40.0T) — these do not constitute approval.
**No default recommended** — this is purely your eye.
**Decision needed:** Your verdict on whether the fixed Q-004 master is acceptable
as a reference, or if a new visual direction is required (gated on D4).

## NOT requiring a decision

**E-02 (impact sounds):** The pipeline safely routes around unapproved impacts.
`select_sfx_a1.py` §7: impact-class events NEVER auto-select; unroutable events
fail closed to silence. No blocker — sounds can be approved async via the
existing review package whenever you're ready.

---

## Authorization-gated (separate from decisions above)

- **E-04:** Full SFX mix — needs explicit authorization (stays `with_sfx_mix=false`)
- **C-12:** R-013 hosted rerun — needs explicit authorization
- **Renders:** B-12, B-20, B-03/B-06 proof, F-02 positive case — need render authorization
