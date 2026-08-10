from __future__ import annotations

import csv
from pathlib import Path

from runtime.apply_etf_eu_donor_parity_contract import apply_contract, write_recommendation_scorecard


def sample_state() -> dict:
    return {
        "portfolio": {
            "nav_eur": 100000.0,
            "cash_eur": 50000.0,
            "positions": [
                {"ticker": "VWCE", "isin": "IE00BK5BQT80", "shares": 100, "current_weight_pct": 25.0, "portfolio_role": "Global core"},
                {"ticker": "EUNA", "isin": "IE00BDBRDM35", "shares": 1000, "current_weight_pct": 7.5, "portfolio_role": "Bonds"},
                {"ticker": "SXR8", "isin": "IE00B5BMR087", "shares": 10, "current_weight_pct": 7.0, "portfolio_role": "US overweight"},
                {"ticker": "L0CK", "isin": "IE00BG0J4C88", "shares": 934, "current_weight_pct": 10.2, "portfolio_role": "Cyber"},
            ],
        },
        "verification_funnel": {"minimum_cash_pct": 35.0, "maximum_new_etf_pct": 15.0},
        "authority": {},
    }


def test_contract_removes_shadow_controls_and_preserves_four_positions() -> None:
    state = apply_contract(sample_state())
    assert state["cash_policy"]["fixed_minimum_cash_pct"] is None
    assert state["authority"]["retired_shadow_rules_executable"] is False
    assert state["authority"]["research_only_transition_values_executable"] is False
    assert state["verification_funnel"].get("minimum_cash_pct") is None
    assert state["verification_funnel"].get("maximum_new_etf_pct") is None
    assert state["verification_funnel"]["model_investability_requires_broker_permission"] is False
    assert state["verification_funnel"]["real_execution_may_require_broker_permission"] is True
    assert {row["ticker"] for row in state["recommendation_memory"]} == {"VWCE", "EUNA", "SXR8", "L0CK"}


def test_allocation_map_has_no_fixed_cash_floor_or_strategic_target_copy() -> None:
    state = apply_contract(sample_state())
    text = " ".join(str(value) for row in state["allocation_map"] for value in row.values()).lower()
    # Current measured weights may legitimately equal a historical target percentage.
    # Reject policy semantics, not the numeric value itself.
    forbidden_policy_phrases = (
        "35% minimum cash",
        "35% minimum-cash",
        "minimum cash 35%",
        "15% maximum new etf",
        "15% max new etf",
        "7.50% minimum cash",
        "7,50% minimum cash",
        "minimum cash 7.50%",
        "minimum cash 7,50%",
        "strategic target",
        "strategisch doel",
    )
    for phrase in forbidden_policy_phrases:
        assert phrase not in text
    assert "no fixed cash floor" in text


def test_scorecard_is_current_and_contains_every_funded_position(tmp_path: Path) -> None:
    state = apply_contract(sample_state())
    out = tmp_path / "scorecard.csv"
    write_recommendation_scorecard(state, out, "2026-08-07", "test-run")
    rows = list(csv.DictReader(out.open(encoding="utf-8")))
    assert {row["ticker"] for row in rows} == {"VWCE", "EUNA", "SXR8", "L0CK"}
    assert {row["report_date"] for row in rows} == {"2026-08-07"}
    assert {row["run_id"] for row in rows} == {"test-run"}


def test_embedded_exposure_semantics_are_descriptive_only() -> None:
    state = apply_contract(sample_state())
    assert state["authority"]["embedded_exposure_semantics"] == "measured_lower_bound_descriptive_not_required_minimum"
    assert state["donor_parity_contract"]["shadow_allocation_caps_are_current_authority"] is False
