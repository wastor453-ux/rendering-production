#!/usr/bin/env python3
"""
compile_sfx_triggers_a1.py — A1-adapted SFX trigger compiler (LOCAL ONLY).

Vendored/adapted from ~/workspace/crackit/tools/compile_sfx_triggers.py.
Differences:
  1. Reads the canonical A1 MANIFEST.json (a dict with an "assets" list;
     asset key is "filename", NOT "file"). The original crashes with a
     KeyError on this manifest (0/180 assets carry "file").
  2. Timing per the SOUND_DESIGN.md law (peak-based), NOT transient_offset_ms:
       trigger_frame = impact_frame - round(peak_time_s * fps)
       trigger_s     = trigger_frame / fps
       peak_s        = impact_frame / fps        (asset's measured peak lands
                                                 exactly on the visual impact)
     transient_offset_ms is absent from A1 (0/180) and is not consulted.
  3. Fail-closed: missing peak_time_s, unknown asset, or a negative
     trigger_frame raises (never silently clamps or defaults).
  4. Importable/testable: compute_trigger() and build_triggers().

LOCAL ONLY: not referenced by any workflow, generates no audio.

Usage:
    python3 compile_sfx_triggers_a1.py --events events.json \
        --manifest ~/workspace/crackit/A1_sfx/MANIFEST.json \
        --asset-map asset_map.json --out sfx_triggers.json [--fps 30]

events.json shape: {"events": [{"event_id", "beat_id", "phrase",
    "sfx" (truthy = SFX for this event), "visual_impact_frame"}]}
asset_map.json shape: {event_id: asset_filename}
"""

import argparse
import json
import sys


class Fail(Exception):
    pass


def compute_trigger(impact_frame, peak_time_s, fps=30):
    """Peak-based trigger math. Raises Fail on invalid input.

    Returns (trigger_frame, trigger_s, peak_s).
    """
    if not isinstance(impact_frame, int) or impact_frame < 0:
        raise Fail(f"invalid impact_frame: {impact_frame!r}")
    if peak_time_s is None:
        raise Fail("peak_time_s is missing (A1 enrichment mandatory)")
    if not isinstance(peak_time_s, (int, float)) or peak_time_s < 0:
        raise Fail(f"invalid peak_time_s: {peak_time_s!r}")
    if not isinstance(fps, int) or fps <= 0:
        raise Fail(f"invalid fps: {fps!r}")
    trigger_frame = impact_frame - round(peak_time_s * fps)
    if trigger_frame < 0:
        raise Fail(
            f"negative trigger_frame: impact_frame={impact_frame}, "
            f"peak_time_s={peak_time_s} -> {trigger_frame}. "
            f"Choose a shorter-peak asset or move the impact later."
        )
    return trigger_frame, round(trigger_frame / fps, 3), round(impact_frame / fps, 3)


def load_a1_assets(manifest):
    """Return {filename: asset_dict} from the canonical A1 manifest.

    Accepts the canonical dict-with-"assets" shape or a bare asset list.
    Raises Fail if any asset lacks filename or peak_time_s.
    """
    if isinstance(manifest, dict) and "assets" in manifest:
        assets = manifest["assets"]
    elif isinstance(manifest, list):
        assets = manifest
    else:
        raise Fail("unrecognized manifest shape (need dict.assets or asset list)")
    by_name = {}
    for a in assets:
        fn = a.get("filename")
        if not fn:
            raise Fail("A1 asset missing 'filename' (original 'file' key does not exist)")
        if a.get("peak_time_s") is None:
            raise Fail(f"asset '{fn}': peak_time_s missing (enrichment mandatory)")
        by_name[fn] = a
    return by_name


def build_triggers(events, assets_by_name, asset_map, fps=30):
    """Core pipeline (no I/O). Returns the triggers list."""
    triggers = []
    for e in events:
        eid = e["event_id"]
        if not e.get("sfx"):
            continue  # no SFX for this event (default-silence)
        asset = asset_map.get(eid)
        if not asset:
            raise Fail(f"{eid}: no asset in asset map (SFX selection must assign one)")
        a = assets_by_name.get(asset)
        if a is None:
            raise Fail(f"{eid}: asset '{asset}' not in A1 manifest")
        impact_f = e["visual_impact_frame"]
        peak = a["peak_time_s"]
        trigger_frame, trigger_s, peak_s = compute_trigger(impact_f, peak, fps)
        triggers.append({
            "event_id": eid,
            "beat_id": e["beat_id"],
            "phrase": e["phrase"],
            "asset": asset,
            "asset_id": a.get("asset_id"),
            "visual_impact_frame": impact_f,
            "impact_time_s": peak_s,
            "peak_time_s": peak,
            "onset_s": a.get("onset_s"),
            "trigger_frame": trigger_frame,
            "trigger_s": trigger_s,
            "peak_s": peak_s,
            "chain": f"{eid} -> impact_frame {impact_f} -> peak {peak}s "
                     f"(-{round(peak * fps)}f) -> trigger_frame {trigger_frame} "
                     f"({trigger_s}s) -> peak {peak_s}s (frame {impact_f})",
        })
    return triggers


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--events", required=True)
    ap.add_argument("--manifest", required=True,
                    help="canonical A1 MANIFEST.json (dict with assets list)")
    ap.add_argument("--asset-map", required=True,
                    help="JSON: {event_id: asset_filename} — the SFX selection output")
    ap.add_argument("--out", required=True)
    ap.add_argument("--fps", type=int, default=30)
    a = ap.parse_args()

    def load(p):
        try:
            with open(p) as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            raise Fail(f"cannot load {p}: {e}")

    events = load(a.events)["events"]
    assets_by_name = load_a1_assets(load(a.manifest))
    asset_map = load(a.asset_map)

    triggers = build_triggers(events, assets_by_name, asset_map, a.fps)

    with open(a.out, "w") as f:
        json.dump({"schema": "astor-legacy-sfx-triggers-v1",
                   "timing_law": "trigger_frame = impact_frame - round(peak_time_s * fps) "
                                 "(SOUND_DESIGN.md; peak-based, not transient_offset_ms)",
                   "source_events": a.events,
                   "triggers": triggers}, f, indent=1)
    print(f"SFX TRIGGER PASS (A1/peak): {len(triggers)} triggers -> {a.out}")
    for t in triggers:
        print(f"  {t['chain']}")


if __name__ == "__main__":
    try:
        main()
    except Fail as e:
        print(f"SFX TRIGGER FAIL: {e}", file=sys.stderr)
        sys.exit(2)
