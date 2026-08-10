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
                {"ticker": "VWCE", "isin": "IE00BK5BQT80", "shares": 100, "current_weight_pct": 25.0, "portfolio_role": "Global core", "strategic_target_weight_pct": 50.0, "phase_target_weight_pct": 25.0, "target_weight_pct": 25.0},
                {"ticker": "EUNA", "isin": "IE00BDBRDM35", "shares": 1000, "current_weight_pct": 7.5, "portfolio_role": "Bonds", "strategic_target_weight_pct": 15.0, "target_weight_pct": 7.5},
                {"ticker": "SXR8", "isin": "IE00B5BMR087", "shares": 10, "current_weight_pct": 7.0, "portfolio_role": "US overweight", "strategic_target_weight_pct": 15.0, "target_weight_pct": 7.5},
                {"ticker": "L0CK", "isin": "IE00BG0J4C88", "shares": 934, "current_weight_pct": 10.2, "portfolio_role": "Cyber", "target_weight_pct": 10.2},
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


def test_legacy_target_fields_are_historical_metadata_not_live_position_authority() -> None:
    state = apply_contract(sample_state())
    for row in state["portfolio"]["positions"]:
        assert "strategic_target_weight_pct" not in row
        assert "phase_target_weight_pct" not in row
        assert "target_weight_pct" not in row
        assert row["historical_allocation_metadata_authority"] == "non_current_cap01_or_transition_context"
        assert row["current_allocation_target_authority"] == "none_without_explicit_current_allocation_decision"
        assert row["historical_allocation_metadata"]
    assert state["parity_completeness"]["allocation_target_metadata_sanitized"] is True
    assert state["authority"]["legacy_target_fields_current_authority"] is False


def test_missing_current_reunderwriting_stays_unresolved_not_implicit_hold() -> None:
    state = apply_contract(sample_state())
    for row in state["recommendation_memory"]:
        assert row["would_initiate_today"] == "Unresolved"
        assert row["would_initiate_at_current_weight"] == "Unresolved"
        assert row["fresh_cash_implication"] == "Review required"
        assert row["reunderwriting_complete"] is False
        assert row["reunderwriting_status"] == "UNRESOLVED"
        assert row["action_clock_status"] == "UNRESOLVED_REUNDERWRITING_REQUIRED"
        assert "before treating Hold as current authority" in row["required_next_action"]
    assert state["parity_completeness"]["unresolved_reunderwriting_count"] == 4
    assert state["parity_completeness"]["all_funded_positions_have_current_reunderwriting"] is False


def test_material_cash_requires_explicit_classification_without_creating_cash_floor() -> None:
    state = apply_contract(sample_state())
    cash = state["cash_policy"]
    assert cash["cash_weight_pct"] == 50.0
    assert cash["material_position"] is True
    assert cash["deploy_or_explain_review_required_if_actionable_fundable_lane_exists"] is True
    assert cash["cash_classification"] == "Unresolved — explicit classification required"
    assert cash["cash_classification_complete"] is False
    assert cash["fixed_minimum_cash_pct"] is None
    assert cash["automatic_trade_authority"] is False


def test_allocation_map_has_no_fixed_cash_floor_or_strategic_target_copy() -> None:
    state = apply_contract(sample_state())
    text = " ".join(str(value) for row in state["allocation_map"] for value in row.values()).lower()
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
    assert {row["reunderwriting_status"] for row in rows} == {"UNRESOLVED"}
    assert "fresh_cash_implication" in rows[0]
    assert "action_clock_status" in rows[0]


def test_embedded_exposure_and_donor_threshold_semantics_are_descriptive_only() -> None:
    state = apply_contract(sample_state())
    assert state["authority"]["embedded_exposure_semantics"] == "measured_lower_bound_descriptive_not_required_minimum"
    assert state["donor_parity_contract"]["shadow_allocation_caps_are_current_authority"] is False
    assert state["donor_parity_contract"]["donor_cash_thresholds_are_review_rules_not_allocation_caps"] is True
    assert state["donor_parity_contract"]["donor_factor_40pct_is_concentration_disclosure_not_position_cap"] is True
