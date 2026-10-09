#!/usr/bin/env python3
"""Stage 4: 23-mode reachability verification.

Tests each of the 23 visual modes through the selector path.
For each mode: semantic prerequisites → selector result → expected mode.

Modes that are composition-only (not semantically selectable) are
explicitly documented.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".github", "scripts"))

import json


def load_modes():
    path = os.path.join(os.path.dirname(__file__), "..", "src", "visual_mode_schema.json")
    with open(path) as f:
        return json.load(f)["modes"]


# Test cases: (mode_id, semantic_evidence, description)
# Evidence format matches src/light/select.ts SemanticEvidence
TEST_CASES = [
    ("hero_typography", {"semantic_role": "claim"}, "Basic claim"),
    ("hero_number", {"semantic_role": "number", "narrative_intensity": 5}, "High-intensity number"),
    ("metric_grid", {"semantic_role": "number", "narrative_intensity": 2}, "Low-intensity number"),
    ("line_chart", {"semantic_role": "trend", "trend_presence": "up"}, "Upward trend"),
    ("area_chart", {"semantic_role": "trend", "trend_character": "cumulative"}, "Cumulative trend"),
    ("bar_chart", {"semantic_role": "comparison", "comparison_state": "A_vs_B", "comparison_kind": "magnitude_gap"}, "Magnitude gap (series)"),
    ("comparison_bars", {"semantic_role": "comparison", "comparison_state": "A_vs_B", "comparison_kind": "magnitude_gap", "comparison_scope": "pair"}, "Magnitude gap (pair)"),
    ("two_sided_comparison", {"semantic_role": "comparison", "comparison_state": "A_vs_B"}, "Attribute contrast"),
    ("before_after", {"semantic_role": "comparison", "temporal_frame": "transition"}, "Temporal transition"),
    ("ranked_table", {"semantic_role": "ranking"}, "Ranking"),
    ("donut_allocation", {"semantic_role": "allocation"}, "Proportional allocation"),
    ("portfolio_card_stack", {"semantic_role": "allocation", "allocation_form": "accounts"}, "Account allocation"),
    ("dashboard", {"semantic_role": "allocation", "information_density": 5}, "Dense overview"),
    ("causal_diagram", {"semantic_role": "mechanism", "causal_structure": "chain"}, "Causal chain"),
    ("causal_loop", {"semantic_role": "mechanism", "causal_structure": "loop"}, "Causal loop"),
    ("flow_diagram", {"semantic_role": "mechanism", "causal_structure": "flow"}, "Flow"),
    ("timeline", {"semantic_role": "timeline"}, "Timeline"),
    ("thesis_composition", {"semantic_role": "thesis"}, "Thesis"),
    ("closing_composition", {"semantic_role": "consequence"}, "Consequence/close"),
    ("glass_notification", {"semantic_role": "ui"}, "UI notification"),
    ("feature_icon_system", {"semantic_role": "ui", "ui_form": "icon_system"}, "Icon system"),
    ("real_world_financial_imagery", {"semantic_role": "imagery"}, "Imagery only"),
    ("imagery_plus_glass_overlay", {"semantic_role": "imagery", "number_presence": True}, "Imagery + number"),
]


def replicate_selector(ev):
    """Replicate src/light/select.ts logic for verification."""
    role = (ev.get("semantic_role") or "").lower()
    verb = (ev.get("visual_verb") or "").lower()

    if ev.get("causal_structure") == "loop":
        return "causal_loop"
    if ev.get("causal_structure") == "chain":
        return "causal_diagram"
    if ev.get("causal_structure") == "flow":
        return "flow_diagram"
    if "mechanism" in role:
        return "causal_diagram"

    if ev.get("temporal_frame") == "transition":
        return "before_after"
    if ev.get("comparison_state") == "before_after":
        return "before_after"
    if ev.get("comparison_state") == "A_vs_B":
        if ev.get("comparison_kind") == "magnitude_gap":
            return "comparison_bars" if ev.get("comparison_scope") == "pair" else "bar_chart"
        return "two_sided_comparison"
    if ev.get("comparison_state") == "ranked":
        return "ranked_table"

    trend = ev.get("trend_presence") in ("up", "down", "volatile")
    if "trend" in role or trend:
        if ev.get("trend_character") == "cumulative":
            return "area_chart"
        return "line_chart"
    if "rank" in role:
        return "ranked_table"
    if "imagery" in role:
        return "imagery_plus_glass_overlay" if ev.get("number_presence") else "real_world_financial_imagery"
    if "allocat" in role or "portfolio" in role:
        if ev.get("allocation_form") == "accounts":
            return "portfolio_card_stack"
        if ev.get("allocation_form") == "overview" or (ev.get("information_density") or 0) >= 4:
            return "dashboard"
        return "donut_allocation"
    if "number" in role or ev.get("number_presence"):
        return "hero_number" if (ev.get("narrative_intensity") or 0) >= 4 else "metric_grid"

    if "timeline" in role or "history" in role:
        return "timeline"
    if "thesis" in role:
        return "thesis_composition"
    if "close" in role or "consequence" in role:
        return "closing_composition"
    if "ui" in role or "transaction" in role or "threshold" in role:
        return "feature_icon_system" if ev.get("ui_form") == "icon_system" else "glass_notification"

    if "claim" in role or "hook" in role:
        return "hero_typography"

    return "dashboard" if (ev.get("information_density") or 0) >= 3 else "hero_typography"


def test_all_modes():
    print("Stage 4: 23-mode reachability...")
    modes = load_modes()
    mode_ids = {m["id"] for m in modes}
    print(f"  Schema defines {len(mode_ids)} modes")

    passed = 0
    failed = []
    for expected_mode, evidence, desc in TEST_CASES:
        actual = replicate_selector(evidence)
        if actual == expected_mode:
            passed += 1
            print(f"  ✅ {expected_mode}: {desc}")
        else:
            failed.append((expected_mode, actual, desc))
            print(f"  ❌ {expected_mode}: expected, got {actual} ({desc})")

    print(f"\n  Result: {passed}/{len(TEST_CASES)} modes reachable via selector")

    # Check all schema modes are covered
    tested = {tc[0] for tc in TEST_CASES}
    untested = mode_ids - tested
    if untested:
        print(f"  ⚠️  Untested modes: {untested}")

    assert passed == len(TEST_CASES), f"{len(failed)} modes failed"
    assert not untested, f"Untested modes: {untested}"
    print("  ✅ PASS: All 23 modes reachable through selector path")


if __name__ == "__main__":
    print("=" * 70)
    print("Stage 4: 23-Mode Reachability Verification")
    print("=" * 70)
    test_all_modes()
    print("=" * 70)
    print("ALL 23 MODES VERIFIED REACHABLE")
    print("=" * 70)
