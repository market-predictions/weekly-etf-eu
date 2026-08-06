from __future__ import annotations

from copy import deepcopy
from datetime import date

from pricing.build_current_session_close_results import resolve_previous_session_close_date
from tools.validate_etf_eu_portfolio_policy import validate


POLICY = {
    "schema_version": "etf_eu_portfolio_policy_v2",
    "policy_id": "TEST_POLICY",
    "active_release_mode": {
        "expected_funded_tickers": ["VWCE", "EUNA", "SXR8", "L0CK"],
        "allowed_funded_tickers": ["VWCE", "EUNA", "SXR8", "L0CK"],
        "minimum_position_count": 4,
        "maximum_position_count": 8,
        "minimum_cash_weight_pct": 35.0,
        "maximum_single_position_weight_pct": 50.0,
        "maximum_satellite_weight_pct": 15.0,
        "maximum_weight_by_ticker_pct": {"VWCE": 50.0, "EUNA": 15.0, "SXR8": 15.0, "L0CK": 15.0},
        "required_activation_tickers": ["L0CK"],
    },
    "reconciliation": {"nav_tolerance_eur": 1.0, "weight_tolerance_pct": 0.10},
}


def valid_state() -> dict:
    nav = 100_000.0
    values = {"VWCE": 25_000.0, "EUNA": 7_500.0, "SXR8": 7_500.0, "L0CK": 10_000.0}
    return {
        "schema_version": "etf_eu_production_convergence_state_v1",
        "official_portfolio": {
            "nav_eur": nav,
            "cash_eur": 50_000.0,
            "invested_market_value_eur": 50_000.0,
            "model_portfolio_only": True,
            "real_broker_execution": False,
            "positions": [
                {
                    "exchange_ticker": ticker,
                    "trading_currency": "EUR",
                    "market_value_eur": value,
                    "current_weight_pct": value / nav * 100.0,
                }
                for ticker, value in values.items()
            ],
            "last_model_capital_activation": {"activation_id": "TEST-L0CK"},
        },
        "stage_1_decision": {
            "activated_tickers": ["L0CK"],
            "executable_trade_intents": [],
        },
    }


def test_current_partial_activation_passes() -> None:
    result = validate(POLICY, valid_state())
    assert result["verdict"] == "PASS"
    assert result["blockers"] == []


def test_75_percent_vwce_is_blocked() -> None:
    state = valid_state()
    portfolio = state["official_portfolio"]
    portfolio["positions"][0]["market_value_eur"] = 75_000.0
    portfolio["positions"][0]["current_weight_pct"] = 75.0
    portfolio["invested_market_value_eur"] = 100_000.0
    portfolio["cash_eur"] = 0.0
    result = validate(POLICY, state)
    assert result["verdict"] == "FAIL"
    assert "maximum_single_position_weight" in result["blockers"]
    assert "ticker_weight_caps" in result["blockers"]
    assert "minimum_cash_reserve" in result["blockers"]


def test_sub_reserve_cash_is_blocked() -> None:
    state = valid_state()
    portfolio = state["official_portfolio"]
    portfolio["cash_eur"] = 10_000.0
    portfolio["nav_eur"] = 60_000.0
    portfolio["positions"][0]["current_weight_pct"] = 41.666667
    portfolio["positions"][1]["current_weight_pct"] = 12.5
    portfolio["positions"][2]["current_weight_pct"] = 12.5
    portfolio["positions"][3]["current_weight_pct"] = 16.666667
    result = validate(POLICY, state)
    assert result["verdict"] == "FAIL"
    assert "minimum_cash_reserve" in result["blockers"]


def test_unauthorized_ticker_is_blocked() -> None:
    state = valid_state()
    state["official_portfolio"]["positions"][3]["exchange_ticker"] = "VVSM"
    result = validate(POLICY, state)
    assert result["verdict"] == "FAIL"
    assert "release_roster_exact" in result["blockers"]
    assert "funded_tickers_allowed" in result["blockers"]


def test_nav_arithmetic_mismatch_is_blocked() -> None:
    state = deepcopy(valid_state())
    state["official_portfolio"]["nav_eur"] = 110_000.0
    result = validate(POLICY, state)
    assert result["verdict"] == "FAIL"
    assert "cash_plus_positions_equals_nav" in result["blockers"]


def test_xetra_next_session_rollover_preserves_previous_close_date() -> None:
    resolved, mode = resolve_previous_session_close_date(
        report_date=date(2026, 8, 5),
        last_trade_date=date(2026, 8, 6),
        observed_after_report_session=True,
    )
    assert resolved == date(2026, 8, 5)
    assert mode == "next_session_previous_close_rollover"


def test_xetra_stale_rollover_remains_fail_closed() -> None:
    resolved, mode = resolve_previous_session_close_date(
        report_date=date(2026, 8, 4),
        last_trade_date=date(2026, 8, 6),
        observed_after_report_session=True,
    )
    assert resolved is None
    assert mode is None
