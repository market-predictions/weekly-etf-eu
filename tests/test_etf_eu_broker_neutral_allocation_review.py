from __future__ import annotations

import json
from pathlib import Path

import yaml

from runtime.build_etf_eu_broker_neutral_allocation_review import build_review
from tools.validate_etf_eu_broker_neutral_allocation_review import validate

ROOT = Path(__file__).resolve().parents[1]


def test_active_portfolio_revaluation_and_first_tranche_trade_intents(tmp_path: Path) -> None:
    state_path = tmp_path / "portfolio.json"
    state_path.write_text(
        json.dumps(
            {
                "schema_version": "etf_eu_portfolio_state_v2",
                "cash_eur": 92900.0,
                "invested_market_value_eur": 7100.0,
                "nav_eur": 100000.0,
                "positions": [
                    {
                        "isin": "IE00B5BMR087",
                        "exchange_ticker": "SXR8",
                        "trading_currency": "EUR",
                        "shares": 10,
                        "avg_entry_local": 710.0,
                        "current_price_local": 710.0,
                        "price_date": "2026-07-14",
                    }
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    pricing_path = tmp_path / "pricing.json"
    pricing_path.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "isin": "IE00B5BMR087",
                        "ticker": "SXR8",
                        "instrument_type": "UCITS ETF",
                        "verification_status": "verified_ucits_trading_line",
                        "pricing_status": "priced_non_authoritative",
                        "currency": "EUR",
                        "close_price": 711.66,
                        "close_date": "2026-07-16",
                    },
                    {
                        "isin": "IE00BK5BQT80",
                        "ticker": "VWCE",
                        "instrument_type": "UCITS ETF",
                        "verification_status": "verified_ucits_trading_line",
                        "pricing_status": "priced_non_authoritative",
                        "currency": "EUR",
                        "close_price": 165.32,
                        "close_date": "2026-07-16",
                    },
                    {
                        "isin": "IE00BDBRDM35",
                        "ticker": "EUNA",
                        "instrument_type": "UCITS ETF",
                        "verification_status": "verified_ucits_trading_line",
                        "pricing_status": "priced_non_authoritative",
                        "currency": "EUR",
                        "close_price": 4.913,
                        "close_date": "2026-07-14",
                    },
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )

    review = build_review(
        policy_path=ROOT / "config/etf_eu_target_allocation.yml",
        portfolio_state_path=state_path,
        pricing_artifact_path=pricing_path,
        run_id="20260716_204700",
        report_date_raw="2026-07-16",
        output_path=tmp_path / "review.json",
    )

    assert review["portfolio_revaluation"]["invested_market_value_eur"] == 7116.6
    assert review["portfolio_revaluation"]["nav_eur"] == 100016.6
    assert review["portfolio_revaluation"]["nav_change_eur"] == 16.6

    intents = {row["exchange_ticker"]: row for row in review["trade_intents"]}
    assert set(intents) == {"VWCE", "EUNA"}
    assert intents["VWCE"]["shares_delta"] == 151
    assert intents["VWCE"]["trade_value_eur"] == 24963.32
    assert intents["EUNA"]["shares_delta"] == 1526
    assert intents["EUNA"]["trade_value_eur"] == 7497.238

    allocation = review["allocation_decision"]
    assert allocation["status"] == "ready_for_guarded_model_activation"
    assert allocation["trade_intent_count"] == 2
    assert allocation["new_position_authorized"] is True
    assert allocation["second_tranche_authorized"] is False
    assert allocation["portfolio_mutation"] is False
    assert allocation["cash_after_decision_eur"] == 60439.442
    assert allocation["invested_after_decision_eur"] == 39577.158
    assert allocation["nav_after_decision_eur"] == 100016.6
    assert allocation["nav_reconciliation_ok"] is True

    sxr8 = next(row for row in review["decision_rows"] if row.get("exchange_ticker") == "SXR8")
    assert sxr8["action"] == "hold_existing"
    assert sxr8["shares_delta"] == 0

    errors, _, evidence = validate(review)
    assert not errors
    assert evidence["review_valid"] is True
    assert evidence["active_portfolio_revaluation_passed"] is True
    assert evidence["broker_neutral_model_authority_passed"] is True
    assert evidence["ready_for_guarded_model_activation"] is True


def test_policy_is_explicitly_broker_neutral() -> None:
    policy = yaml.safe_load((ROOT / "config/etf_eu_target_allocation.yml").read_text(encoding="utf-8"))
    activation = policy["activation"]
    assert activation["broker_specific_permission_required_for_model"] is False
    assert activation["broker_permission_required_for_real_execution"] is True
