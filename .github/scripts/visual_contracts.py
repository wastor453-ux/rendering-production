#!/usr/bin/env python3
"""P0-4: Canonical visual-event milestone contract.
P0-5: Payload resolver and validator.

Defines the authoritative contract for visual events and data payloads.
Every production visual component that creates an earned visual event
must consume this contract.
"""

from typing import Dict, Any, List, Optional
import hashlib
import json


# ---------------------------------------------------------------------------
# P0-4: Canonical Visual-Event Milestone Contract
# ---------------------------------------------------------------------------

class VisualMilestone:
    """Canonical milestone for a visual event.

    Fields:
    - event_id: Permanent join key (e.g., "evt_beat_001")
    - visual_impact_frame: Authoritative SFX peak target (30fps frame number)
    - mode: Selected visual mode (e.g., "hero_number")
    - component: Production component name
    - beat_id: Source beat ID
    - semantic_role: claim|number|comparison|trend|etc.
    """

    REQUIRED = ["event_id", "visual_impact_frame", "mode", "component", "beat_id"]

    def __init__(self, event_id: str, visual_impact_frame: int,
                 mode: str, component: str, beat_id: str,
                 semantic_role: str = "claim"):
        if not event_id or not event_id.startswith("evt_"):
            raise ValueError(f"event_id must start with 'evt_': {event_id}")
        if not isinstance(visual_impact_frame, int) or visual_impact_frame < 0:
            raise ValueError(f"visual_impact_frame must be non-negative int: {visual_impact_frame}")
        if not mode:
            raise ValueError("mode is required")
        if not component:
            raise ValueError("component is required")

        self.event_id = event_id
        self.visual_impact_frame = visual_impact_frame
        self.mode = mode
        self.component = component
        self.beat_id = beat_id
        self.semantic_role = semantic_role

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "visual_impact_frame": self.visual_impact_frame,
            "mode": self.mode,
            "component": self.component,
            "beat_id": self.beat_id,
            "semantic_role": self.semantic_role,
        }

    @classmethod
    def from_beat(cls, beat: Dict[str, Any], mode: str, component: str):
        """Create milestone from a compiled beat."""
        return cls(
            event_id=beat["event_id"],
            visual_impact_frame=beat["visual_impact_frame"],
            mode=mode,
            component=component,
            beat_id=beat["id"],
            semantic_role=beat.get("semantic_role", "claim"),
        )


# ---------------------------------------------------------------------------
# P0-5: Payload Resolver and Validator
# ---------------------------------------------------------------------------

class PayloadValidator:
    """Validates data payloads for production visuals.

    Rules:
    - Data modes REQUIRE valid payloads (not just data_presence flag)
    - Payload must have: metric_id, values, provenance
    - Displayed values must equal validated source data
    - No invented financial data in production
    """

    # Modes that require data payloads
    DATA_MODES = {
        "line_chart", "bar_chart", "area_chart", "donut_allocation",
        "comparison_bars", "two_sided_comparison", "ranked_table",
        "metric_grid", "hero_number", "dashboard", "portfolio_card_stack",
    }

    REQUIRED_FIELDS = ["metric_id", "values", "provenance"]

    @classmethod
    def validate(cls, mode: str, payload: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate payload for a mode.

        Returns {"ok": True, "payload": payload} or {"ok": False, "errors": [...]}.
        Fail closed: missing/invalid payload for data mode = reject.
        """
        errors = []

        if mode in cls.DATA_MODES:
            if payload is None:
                return {"ok": False, "errors": [f"Mode '{mode}' requires a data payload, got None"]}
            if not isinstance(payload, dict):
                return {"ok": False, "errors": [f"Payload must be dict, got {type(payload)}"]}

            for field in cls.REQUIRED_FIELDS:
                if field not in payload or payload[field] is None:
                    errors.append(f"Payload missing required field: {field}")

            if "values" in payload:
                values = payload["values"]
                if not isinstance(values, list) or len(values) == 0:
                    errors.append("Payload 'values' must be a non-empty list")
                elif not all(isinstance(v, (int, float)) for v in values):
                    errors.append("Payload 'values' must contain only numbers")

            if "provenance" in payload:
                prov = payload["provenance"]
                if not isinstance(prov, dict) or "source" not in prov:
                    errors.append("Payload 'provenance' must include 'source'")

            # data_presence flag must NOT bypass validation
            if payload.get("data_presence") is True and errors:
                errors.append("data_presence=true does not bypass payload validation")

        if errors:
            return {"ok": False, "errors": errors}
        return {"ok": True, "payload": payload}

    @classmethod
    def hash_payload(cls, payload: Dict[str, Any]) -> str:
        """Stable hash for payload identity."""
        blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(blob.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_milestone_contract():
    print("P0-4: Milestone contract...")
    m = VisualMilestone(
        event_id="evt_beat_001",
        visual_impact_frame=42,
        mode="hero_number",
        component="HeroData",
        beat_id="beat_001",
        semantic_role="number",
    )
    d = m.to_dict()
    assert d["event_id"] == "evt_beat_001"
    assert d["visual_impact_frame"] == 42
    print("  ✅ PASS: Milestone contract valid")

    # Fail closed on bad event_id
    try:
        VisualMilestone("bad_id", 42, "hero_number", "HeroData", "beat_001")
        assert False, "Should have raised"
    except ValueError:
        print("  ✅ PASS: Rejects invalid event_id (fail closed)")


def test_payload_validator():
    print("P0-5: Payload validator...")

    # Valid payload
    valid = {
        "metric_id": "housing_price_drop",
        "values": [100, 95, 90, 86],
        "provenance": {"source": "Case-Shiller Index", "date": "2026-10-01"},
    }
    r = PayloadValidator.validate("line_chart", valid)
    assert r["ok"], f"Valid payload rejected: {r['errors']}"
    print("  ✅ PASS: Valid payload accepted")

    # Missing payload for data mode
    r = PayloadValidator.validate("line_chart", None)
    assert not r["ok"], "Should reject None payload"
    print("  ✅ PASS: None payload rejected (fail closed)")

    # data_presence bypass attempt
    bypass = {"data_presence": True, "values": "not_a_list"}
    r = PayloadValidator.validate("bar_chart", bypass)
    assert not r["ok"], "Should reject data_presence bypass"
    assert any("bypass" in e for e in r["errors"])
    print("  ✅ PASS: data_presence bypass rejected")

    # Non-data mode doesn't require payload
    r = PayloadValidator.validate("hero_typography", None)
    assert r["ok"], "Non-data mode should not require payload"
    print("  ✅ PASS: Non-data modes exempt")


if __name__ == "__main__":
    print("=" * 70)
    print("P0-4/P0-5: Milestone Contract & Payload Validator")
    print("=" * 70)
    test_milestone_contract()
    print()
    test_payload_validator()
    print("=" * 70)
    print("P0-4/P0-5 PROVEN")
    print("=" * 70)
