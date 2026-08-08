from __future__ import annotations

from copy import deepcopy
from datetime import date

from pricing.build_current_session_close_results import resolve_previous_session_close_date
from tools.validate_etf_eu_portfolio_policy import validate


ACTIVATION_ID = "TEST-L0CK"
POLICY = {
    "schema_version": "etf_eu_portfolio_policy_v2",
    "policy_id": "TEST_LINEAGE_POLICY",
    "allocation_lineage": {
        "method": "protected_state_plus_explicit_authorized_mutation",
        "current_activation_id": ACTIVATION_ID,
        "required_activated_tickers": ["L0CK"],
    },
    "reconciliation": {
        "nav_tolerance_eur": 1.0,
        "cash_tolerance_eur": 0.01,
        "weight_tolerance_pct": 0.10,
        "market_value_tolerance_eur": 1.0,
    },
}


def protected_state() -> dict:
    values = {
        "VWCE": (100, 250.0),
        "EUNA": (1500, 5.0),
        "SXR8": (10, 750.0),
        "L0CK": (1000, 10.0),
    }
    invested = sum(shares * price for shares, price in values.values())
    cash = 50_000.0
    nav = invested + cash
    return {
        "schema_version": "etf_eu_portfolio_state_v2",
        "nav_eur": nav,
        "cash_eur": cash,
        "invested_market_value_eur": invested,
        "model_portfolio_only": True,
        "real_broker_execution": False,
        "last_model_capital_activation": {"activation_id": ACTIVATION_ID},
        "positions": [
            {
                "exchange_ticker": symbol,
                "trading_currency": "EUR",
                "shares": shares,
                "current_price_local": price,
                "market_value_eur": shares * price,
                "current_weight_pct": shares * price / nav * 100.0,
            }
            for symbol, (shares, price) in values.items()
        ],
    }


def candidate_state() -> dict:
    return {
        "schema_version": "etf_eu_production_convergence_state_v1",
        "official_portfolio": deepcopy(protected_state()),
        "stage_1_decision": {
            "activated_tickers": ["L0CK"],
            "executable_trade_intents": [],
        },
    }


def decision() -> dict:
    return {
        "schema_version": "etf_eu_stage1_allocation_decision_v1",
        "activation_id": ACTIVATION_ID,
        "allocation_status": "ready_for_guarded_model_activation",
        "decisions": [
            {"action": "buy", "exchange_ticker": "L0CK", "shares_delta": 1000}
        ],
    }


def revalue(portfolio: dict, symbol: str, new_price: float) -> None:
    for row in portfolio["positions"]:
        if row["exchange_ticker"] == symbol:
            row["current_price_local"] = new_price
            row["market_value_eur"] = row["shares"] * new_price
    invested = sum(row["market_value_eur"] for row in portfolio["positions"])
    portfolio["invested_market_value_eur"] = invested
    portfolio["nav_eur"] = invested + portfolio["cash_eur"]
    for row in portfolio["positions"]:
        row["current_weight_pct"] = row["market_value_eur"] / portfolio["nav_eur"] * 100.0


def test_protected_valuation_state_passes() -> None:
    result = validate(POLICY, candidate_state(), protected_state(), decision())
    assert result["verdict"] == "PASS"
    assert result["blockers"] == []


def test_allocator_created_75_percent_vwce_is_blocked_by_lineage() -> None:
    state = candidate_state()
    portfolio = state["official_portfolio"]
    vwce = next(row for row in portfolio["positions"] if row["exchange_ticker"] == "VWCE")
    vwce["shares"] = 300
    vwce["current_price_local"] = 250.0
    vwce["market_value_eur"] = 75_000.0
    portfolio["cash_eur"] = 0.0
    portfolio["invested_market_value_eur"] = sum(row["market_value_eur"] for row in portfolio["positions"])
    portfolio["nav_eur"] = portfolio["invested_market_value_eur"]
    for row in portfolio["positions"]:
        row["current_weight_pct"] = row["market_value_eur"] / portfolio["nav_eur"] * 100.0
    result = validate(POLICY, state, protected_state(), decision())
    assert result["verdict"] == "FAIL"
    assert "protected_share_identity_preserved" in result["blockers"]
    assert "protected_cash_preserved" in result["blockers"]


def test_market_driven_75_percent_weight_is_observed_not_arbitrarily_blocked() -> None:
    state = candidate_state()
    revalue(state["official_portfolio"], "VWCE", 2250.0)
    result = validate(POLICY, state, protected_state(), decision())
    assert result["verdict"] == "PASS"
    assert result["portfolio"]["largest_position_ticker"] == "VWCE"
    assert result["portfolio"]["largest_position_weight_pct"] == 75.0
    assert result["portfolio"]["concentration_is_observation_not_hard_cap"] is True


def test_unauthorized_ticker_is_blocked() -> None:
    state = candidate_state()
    state["official_portfolio"]["positions"][3]["exchange_ticker"] = "VVSM"
    result = validate(POLICY, state, protected_state(), decision())
    assert result["verdict"] == "FAIL"
    assert "protected_ticker_roster_preserved" in result["blockers"]


def test_unauthorized_cash_change_is_blocked() -> None:
    state = candidate_state()
    portfolio = state["official_portfolio"]
    portfolio["cash_eur"] = 10_000.0
    portfolio["nav_eur"] = portfolio["invested_market_value_eur"] + portfolio["cash_eur"]
    for row in portfolio["positions"]:
        row["current_weight_pct"] = row["market_value_eur"] / portfolio["nav_eur"] * 100.0
    result = validate(POLICY, state, protected_state(), decision())
    assert result["verdict"] == "FAIL"
    assert "protected_cash_preserved" in result["blockers"]


def test_nav_arithmetic_mismatch_is_blocked() -> None:
    state = candidate_state()
    state["official_portfolio"]["nav_eur"] += 10_000.0
    result = validate(POLICY, state, protected_state(), decision())
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
