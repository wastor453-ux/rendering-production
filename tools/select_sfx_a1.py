#!/usr/bin/env python3
"""
select_sfx_a1.py — Autonomous A1 SFX selector (LOCAL ONLY).

Implements the SOUND_DESIGN.md §4 decision engine using ONLY measured
manifest fields (category, duration_s, peak_time_s, peak_dbfs, rms_dbfs).
Does NOT require semantic_roles/visual_verbs enrichment (0/180 assets
carry those fields as of 2026-10-10; the selector is explicit about this).

Pipeline position:
    events.json (with sfx_policy) 
      -> select_sfx_a1.py -> asset_map.json 
      -> compile_sfx_triggers_a1.py -> sfx_triggers.json 
      -> mix_sfx.py

Selection laws (from SOUND_DESIGN.md):
  §4  Default = none. Score >= 75 to select.
      semantic fit 40 / timing fit 30 / energy fit 20 / fatigue fit 10.
  §4  Hard context locks: glitch, money, continuous-data, click-family, review.
  §7  Impact-class events NEVER auto-select (human ear gate, §14).
  §8  Anti-fatigue: no back-to-back reuse; 12f click breathing; <=2 per 1.0s;
      <=1 per beat.
  §9  Continuous data motion: single swell, never ticker clicks (not a one-shot).

Inputs:
  --events    JSON: {"events": [{"event_id", "beat_id", "semantic_role",
                    "visual_verb", "motion_scale", "visual_impact_frame",
                    "sfx_policy"}]}
                  sfx_policy: "auto" | "manual" | "none"
                  "manual" = human selects (impact class, ear gate)
                  "none"   = explicitly silent
                  "auto"   = this selector decides (may still choose silence)
  --manifest  A1 MANIFEST.json (canonical)
  --out       asset_map.json output: {event_id: asset_filename}
              Events assigned silence are OMITTED (not mapped to null).

Fail-closed: unknown category, unroutable role, or scoring below threshold
  -> silence (omitted), never a guessed asset. Any structural error exits 2.

LOCAL ONLY: not referenced by any workflow.
"""

import argparse
import json
import sys

FPS = 30
SCORE_THRESHOLD = 75
CLICK_BREATHING_FRAMES = 12
MAX_ONESHOTS_PER_SEC = 2


class Fail(Exception):
    pass


# ---------------------------------------------------------------------------
# Category -> role class (from measured A1 category field only).
# Categories NOT listed here are hold (never auto-selected).
# ---------------------------------------------------------------------------
CATEGORY_ROLE = {
    # money / data
    "8-Bit Coin": "money",
    "Digital number dicrease": "data",
    "Digital number increse": "data",
    # whoosh
    "Swipe": "whoosh",
    "Interface Delete Swoosh": "whoosh",
    # pop
    "Interface Pop": "pop",
    "Notification Chime": "pop",
    "Confirmation": "pop",
    # click (one family per video — see select())
    "Botton Clikcs": "click",
    "Menu Selection": "click",
    "Toggle Switch": "click",
    "UI Hover": "click",
    "Picker Wheel Detent Tick": "click",
    "Message Sent": "click",
    "Call End": "click",
    # HOLD — never auto-selected:
    #   "Alert", "Error"        -> glitch lock (needs explicit error semantics)
    #   "Loading"               -> continuous, not a one-shot
    #   "graph down", "graph rise" -> impact class (human ear gate)
}

# semantic_role -> allowed role classes
ROLE_ALLOW = {
    "money": {"money", "data"},
    "data_tick": {"data", "click"},
    "ui_confirm": {"click", "pop"},
    "card_entrance": {"whoosh", "pop"},
    "number_reveal": {"pop", "whoosh", "data"},
    "headline": {"whoosh", "pop"},
    # impact roles are NEVER auto-selected (ear gate)
    "impact": set(),
    "deep_impact": set(),
}

# motion_scale -> preferred asset duration range (seconds)
MOTION_DURATION = {
    "micro": (0.0, 0.6),
    "small": (0.0, 1.2),
    "medium": (0.3, 2.5),
    "large": (0.8, 4.0),
}


def load_a1(manifest_path):
    try:
        with open(manifest_path) as f:
            m = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise Fail(f"cannot load manifest: {e}")
    assets = m["assets"] if isinstance(m, dict) and "assets" in m else m
    if not isinstance(assets, list) or not assets:
        raise Fail("manifest has no assets list")
    # Only routable assets: category in CATEGORY_ROLE AND peak_time_s measured
    routable = []
    for a in assets:
        cat = a.get("category")
        if cat not in CATEGORY_ROLE:
            continue  # hold category
        if a.get("peak_time_s") is None:
            continue  # enrichment mandatory
        routable.append(a)
    if not routable:
        raise Fail("no routable assets in manifest")
    return routable


def score_asset(asset, event, last_asset, use_counts):
    """Return (score, reason_parts). Score < 75 -> silence.

    Uses only measured fields. Semantic fit is category->role class match
    against the event's semantic_role allow-list.
    """
    role_class = CATEGORY_ROLE[asset["category"]]
    allowed = ROLE_ALLOW.get(event.get("semantic_role"), set())
    parts = []
    score = 0

    # semantic fit: 40 — role class must be allowed for this semantic_role
    if role_class in allowed:
        score += 40
        parts.append(f"semantic+40({role_class})")
    else:
        parts.append(f"semantic+0({role_class} not in {sorted(allowed)})")
        return 0, parts  # hard fail: wrong meaning

    # timing fit: 30 — peak must allow a non-negative trigger frame
    peak = asset["peak_time_s"]
    impact_f = event["visual_impact_frame"]
    trigger_f = impact_f - round(peak * FPS)
    if trigger_f >= 0:
        score += 30
        parts.append("timing+30")
    else:
        parts.append(f"timing+0(peak {peak}s -> negative trigger)")
        return score, parts

    # energy fit: 20 — duration matches motion_scale; peak not clipping-hot
    motion = event.get("motion_scale", "medium")
    lo, hi = MOTION_DURATION.get(motion, (0.0, 4.0))
    dur = asset.get("duration_s", 0)
    peak_db = asset.get("peak_dbfs", -99)
    energy_ok = lo <= dur <= hi and peak_db <= -1.0
    if energy_ok:
        score += 20
        parts.append(f"energy+20(dur {dur:.2f}s, peak {peak_db:.1f}dB)")
    else:
        parts.append(f"energy+0(dur {dur:.2f}s vs [{lo},{hi}], peak {peak_db:.1f}dB)")

    # fatigue fit: 10 — prefer least-recently-used; penalize immediate repeat
    fn = asset["filename"]
    if fn == last_asset:
        parts.append("fatigue+0(same as last)")
    else:
        # +10 for unused, scaling down with use count (variety pressure)
        uses = use_counts.get(fn, 0)
        bonus = max(0, 10 - uses * 3)
        score += bonus
        parts.append(f"fatigue+{bonus}(used {uses}x)")

    return score, parts


def select(events, assets):
    """Core selection. Returns {event_id: filename}. Silence = omitted."""
    # Group assets by role class for rotation
    by_role = {}
    for a in assets:
        by_role.setdefault(CATEGORY_ROLE[a["category"]], []).append(a)
    # Sort each group by peak_time_s for determinism
    for v in by_role.values():
        v.sort(key=lambda a: (a["peak_time_s"], a["filename"]))

    asset_map = {}
    last_asset = None
    use_counts = {}  # filename -> times selected (variety pressure)
    last_click_time = None
    click_family = None  # one click family per video (§8)
    beat_used = set()
    selected_times = []  # (trigger_s estimate) for density cap

    # Click families: group click assets by category stem
    click_families = {}
    for a in assets:
        if CATEGORY_ROLE[a["category"]] == "click":
            fam = a["category"]
            click_families.setdefault(fam, []).append(a)

    for e in sorted(events, key=lambda x: x["visual_impact_frame"]):
        eid = e["event_id"]
        policy = e.get("sfx_policy", "none")

        if policy == "none":
            continue  # explicitly silent
        if policy == "manual":
            continue  # human ear gate (impact class) — not our decision
        if policy != "auto":
            raise Fail(f"{eid}: unknown sfx_policy {policy!r}")

        # §8: max one one-shot per beat
        beat = e.get("beat_id")
        if beat in beat_used:
            continue
        # §8: max 2 one-shots per 1.0s window (use impact time as proxy)
        t_s = e["visual_impact_frame"] / FPS
        if sum(1 for s in selected_times if 0 <= t_s - s < 1.0) >= MAX_ONESHOTS_PER_SEC:
            continue
        # §8: 12-frame click breathing room
        # (checked after role is known; provisional here)

        allowed = ROLE_ALLOW.get(e.get("semantic_role"), set())
        if not allowed:
            continue  # unroutable semantic_role -> silence

        # Candidate pool: assets whose role class is allowed
        candidates = [a for a in assets if CATEGORY_ROLE[a["category"]] in allowed]
        if not candidates:
            continue

        # One click family per video: lock to first-used family
        click_cands = [a for a in candidates if CATEGORY_ROLE[a["category"]] == "click"]
        if click_cands:
            if click_family is None:
                # pick the family with the best-scoring asset
                best_fam, best_score = None, -1
                for fam, fam_assets in click_families.items():
                    for a in fam_assets:
                        s, _ = score_asset(a, e, last_asset, use_counts)
                        if s > best_score:
                            best_score, best_fam = s, fam
                click_family = best_fam
            candidates = [a for a in candidates
                          if CATEGORY_ROLE[a["category"]] != "click"
                          or a["category"] == click_family]

        # Score and pick best
        scored = []
        for a in candidates:
            s, parts = score_asset(a, e, last_asset, use_counts)
            scored.append((s, a, parts))
        scored.sort(key=lambda x: (-x[0], x[1]["peak_time_s"], x[1]["filename"]))
        best_score, best, best_parts = scored[0]

        if best_score < SCORE_THRESHOLD:
            continue  # below threshold -> silence

        # Final anti-fatigue: click breathing room
        if CATEGORY_ROLE[best["category"]] == "click" and last_click_time is not None:
            gap_f = round((t_s - last_click_time) * FPS)
            if gap_f < CLICK_BREATHING_FRAMES:
                continue

        asset_map[eid] = best["filename"]
        last_asset = best["filename"]
        use_counts[best["filename"]] = use_counts.get(best["filename"], 0) + 1
        if CATEGORY_ROLE[best["category"]] == "click":
            last_click_time = t_s
        beat_used.add(beat)
        selected_times.append(t_s)

    return asset_map


def main():
    ap = argparse.ArgumentParser(description="Autonomous A1 SFX selector (LOCAL ONLY)")
    ap.add_argument("--events", required=True, help="events.json with sfx_policy")
    ap.add_argument("--manifest", required=True, help="A1 MANIFEST.json")
    ap.add_argument("--out", required=True, help="asset_map.json output")
    ap.add_argument("--report", default=None, help="optional selection report JSON")
    a = ap.parse_args()

    try:
        with open(a.events) as f:
            events = json.load(f)["events"]
    except (OSError, json.JSONDecodeError, KeyError) as e:
        raise Fail(f"cannot load events: {e}")
    if not isinstance(events, list):
        raise Fail("events.json must have an 'events' list")

    assets = load_a1(a.manifest)
    asset_map = select(events, assets)

    with open(a.out, "w") as f:
        json.dump(asset_map, f, indent=1, sort_keys=True)

    n_auto = sum(1 for e in events if e.get("sfx_policy") == "auto")
    n_silent = n_auto - len(asset_map)
    print(f"SFX SELECT: {len(asset_map)} selected / {n_auto} auto-policy "
          f"({n_silent} silent by law) -> {a.out}")

    if a.report:
        with open(a.report, "w") as f:
            json.dump({
                "schema": "astor-legacy-sfx-selection-v1",
                "law": "SOUND_DESIGN.md §4/§7/§8; default=silence; threshold=75",
                "enrichment_note": "semantic_roles/visual_verbs absent from A1 "
                                   "(0/180); selection uses measured category, "
                                   "duration_s, peak_time_s, peak_dbfs only",
                "selected": len(asset_map),
                "auto_events": n_auto,
                "silent_by_law": n_silent,
                "asset_map": asset_map,
            }, f, indent=1)


if __name__ == "__main__":
    try:
        main()
    except Fail as e:
        print(f"SFX SELECT FAIL: {e}", file=sys.stderr)
        sys.exit(2)
