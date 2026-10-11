# H-02: Demo Acceptance Checklist (DRAFT — needs Hamza's approval)

**Status:** APPROVED by Hamza 2026-10-11.

## Pre-dispatch gates
- [ ] Branch HEAD verified against expected SHA (no drift)
- [ ] Composition ID confirmed registered in `composition_contract.py`
- [ ] Frame range validated against canonical scene map (`HousingBroke.tsx`)
- [ ] `tools/pre_render_check.py` passes (8/8 checks)
- [ ] `with_sfx_mix=false` confirmed in dispatch inputs
- [ ] No Q-004 artifact overwrite (separate output path)

## Post-render acceptance
- [ ] All chunks rendered (no failures/skips in render matrix)
- [ ] Assembly completed without re-render
- [ ] Master duration matches expected (±1s)
- [ ] Audio guard passed (VO duration within 30s of video)
- [ ] No black/frozen frames (spot-check via `verify_visual.py`)
- [ ] Master artifact downloadable from GitHub

## Issue-finding scope
- [ ] Defects logged against scene/beat (not global verdicts)
- [ ] No creative approval implied by issue-finding review
- [ ] Q-004 master preserved untouched
