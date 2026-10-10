# SFX Policy (2026-10-10)

**Authority:** Hamza's order + SOUND_DESIGN.md §4/§7/§8

## Routine sounds: AUTOMATIC

The selector (`tools/select_sfx_a1.py`) runs autonomously for:
- `policy: "auto"` events
- Score ≥75 (semantic 40 + timing 30 + energy 20 + fatigue 10)
- Anti-fatigue enforced (1/beat, 12-frame spacing, ≤2/sec, variety)

**No per-sound approval required.** The laws are the approval.

## Major-impact sounds: CONSERVATIVE

- `policy: "manual"` events are NEVER auto-selected.
- They remain silent until Hamza's explicit ear approval.
- Current: 9 impact sounds awaiting review (in `your_files/impact-sounds-review/`).

## Full mix: DISABLED

- `with_sfx_mix: false` is the locked default.
- The pre-render gate REJECTS `with_sfx_mix: true` without authorization file.
- Enabling requires Hamza's explicit order, recorded in
  `.production-state/authorizations/sfx_mix.json`.

## Silence is the default

- Below threshold → silence (not a fallback sound).
- Unknown policy → fail closed (silence + log).
- `policy: "none"` → silence, always.

---

**Summary:** Machine handles routine. Human handles impact. Mix stays off.
