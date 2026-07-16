from __future__ import annotations

import csv
import json
from pathlib import Path

from runtime.apply_etf_eu_broker_neutral_allocation_review import CONFIRMATION, apply_review
from runtime.build_etf_eu_broker_neutral_allocation_review import build_review
from tools.validate_etf_eu_broker_neutral_allocation_review import validate

ROOT = Path(__file__).resolve().parents[1]


def test_guarded_broker_neutral_model_activation_is_reconciled_and_idempotent(tmp_path: Path) -> None:
    state_path = tmp_path / "state.json"
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
                        "fund_name": "iShares Core S&P 500 UCITS ETF USD (Acc)",
                        "provider": "iShares / BlackRock",
                        "exchange_ticker": "SXR8",
                        "ticker": "SXR8",
                        "primary_exchange": "Xetra",
                        "trading_currency": "EUR",
                        "shares": 10,
                        "avg_entry_local": 710.0,
                        "current_price_local": 710.0,
                        "market_value_eur": 7100.0,
                        "price_date": "2026-07-14",
                        "portfolio_role": "U.S. equity overweight",
                        "conviction_tier": "Core satellite",
                    }
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    ledger_path = tmp_path / "ledger.csv"
    ledger_path.write_text(
        "trade_id,trade_date,source_report,isin,exchange_ticker,action,shares_delta,previous_weight_pct,new_weight_pct,weight_change_pct,target_weight_pct,conviction_tier,portfolio_role,funding_source_note\n"
        "bootstrap-2026-05-30-CASH,2026-05-30,bootstrap,,CASH,Initial cash-only state,0,0,0,0,0,,,bootstrap\n"
        "model-eu-2026-07-16-20260716_012900-02-SXR8-BUY,2026-07-16,allocation:old,IE00B5BMR087,SXR8,Buy,10,0,7.1,7.1,7.5,Core satellite,U.S. equity overweight,old\n",
        encoding="utf-8",
    )

    pricing_path = tmp_path / "pricing.json"
    pricing_path.write_text(
        json.dumps(
            {
                "rows": [
                    {"isin": "IE00B5BMR087", "ticker": "SXR8", "instrument_type": "UCITS ETF", "verification_status": "verified_ucits_trading_line", "pricing_status": "priced_non_authoritative", "currency": "EUR", "close_price": 711.66, "close_date": "2026-07-16"},
                    {"isin": "IE00BK5BQT80", "ticker": "VWCE", "instrument_type": "UCITS ETF", "verification_status": "verified_ucits_trading_line", "pricing_status": "priced_non_authoritative", "currency": "EUR", "close_price": 165.32, "close_date": "2026-07-16"},
                    {"isin": "IE00BDBRDM35", "ticker": "EUNA", "instrument_type": "UCITS ETF", "verification_status": "verified_ucits_trading_line", "pricing_status": "priced_non_authoritative", "currency": "EUR", "close_price": 4.913, "close_date": "2026-07-14"},
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )

    review_path = tmp_path / "review.json"
    review = build_review(
        policy_path=ROOT / "config/etf_eu_target_allocation.yml",
        portfolio_state_path=state_path,
        pricing_artifact_path=pricing_path,
        run_id="20260716_205500",
        report_date_raw="2026-07-16",
        output_path=review_path,
    )
    errors, warnings, evidence = validate(review)
    assert not errors
    validation_path = tmp_path / "validation.json"
    validation_path.write_text(
        json.dumps({"passed": True, "errors": errors, "warnings": warnings, **evidence}) + "\n",
        encoding="utf-8",
    )

    result = apply_review(
        review_path=review_path,
        validation_path=validation_path,
        portfolio_state_path=state_path,
        trade_ledger_path=ledger_path,
        policy_path=ROOT / "config/etf_eu_target_allocation.yml",
        confirmation=CONFIRMATION,
        output_path=tmp_path / "result.json",
    )
    assert result["status"] == "applied"
    assert result["post_activation_portfolio"] == {
        "cash_eur": 60439.44,
        "invested_market_value_eur": 39577.16,
        "nav_eur": 100016.6,
        "position_count": 3,
    }

    state = json.loads(state_path.read_text(encoding="utf-8"))
    positions = {row["exchange_ticker"]: row for row in state["positions"]}
    assert positions["SXR8"]["shares"] == 10
    assert positions["SXR8"]["current_price_local"] == 711.66
    assert positions["SXR8"]["market_value_eur"] == 7116.6
    assert positions["VWCE"]["shares"] == 151
    assert positions["VWCE"]["market_value_eur"] == 24963.32
    assert positions["EUNA"]["shares"] == 1526
    assert positions["EUNA"]["market_value_eur"] == 7497.24
    assert state["real_broker_execution"] is False

    rows = list(csv.DictReader(ledger_path.open("r", encoding="utf-8", newline="")))
    ids = {row["trade_id"] for row in rows}
    assert "model-eu-2026-07-16-20260716_205500-01-VWCE-BUY" in ids
    assert "model-eu-2026-07-16-20260716_205500-02-EUNA-BUY" in ids

    second = apply_review(
        review_path=review_path,
        validation_path=validation_path,
        portfolio_state_path=state_path,
        trade_ledger_path=ledger_path,
        policy_path=ROOT / "config/etf_eu_target_allocation.yml",
        confirmation=CONFIRMATION,
        output_path=tmp_path / "result2.json",
    )
    assert second["status"] == "already_applied"
    assert len(list(csv.DictReader(ledger_path.open("r", encoding="utf-8", newline="")))) == len(rows)
