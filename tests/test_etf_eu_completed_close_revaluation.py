from __future__ import annotations

from datetime import date

import pandas as pd

from pricing.build_ucits_completed_close_validation_basket_results import select_latest_completed_close
from tools.revalue_etf_eu_portfolio_state import revalue_state


def test_completed_close_excludes_report_date_partial_bar() -> None:
    series = pd.Series(
        [100.0, 101.5, 999.0],
        index=pd.to_datetime(["2026-07-23", "2026-07-24", "2026-07-27"]),
    )
    price, close_date = select_latest_completed_close(series, date(2026, 7, 27))
    assert price == 101.5
    assert close_date == "2026-07-24"


def test_revaluation_updates_prices_nav_weights_and_clears_trade_delta() -> None:
    state = {
        "starting_capital_eur": 100000.0,
        "cash_eur": 60000.0,
        "invested_market_value_eur": 40000.0,
        "nav_eur": 100000.0,
        "positions": [
            {
                "exchange_ticker": "AAA",
                "trading_currency": "EUR",
                "shares": 100,
                "avg_entry_local": 100.0,
                "current_price_local": 100.0,
                "market_value_eur": 10000.0,
                "current_weight_pct": 10.0,
                "shares_delta_this_run": 100,
            },
            {
                "exchange_ticker": "BBB",
                "trading_currency": "EUR",
                "shares": 200,
                "avg_entry_local": 150.0,
                "current_price_local": 150.0,
                "market_value_eur": 30000.0,
                "current_weight_pct": 30.0,
                "shares_delta_this_run": 200,
            },
        ],
    }
    pricing = {
        "rows": [
            {
                "ticker": "AAA",
                "currency": "EUR",
                "close_date": "2026-07-24",
                "close_price": 105.0,
                "pricing_status": "priced_non_authoritative",
                "verification_status": "verified_ucits_trading_line",
                "completed_close": True,
                "source_name": "test",
                "source_quality_status": "test_only",
            },
            {
                "ticker": "BBB",
                "currency": "EUR",
                "close_date": "2026-07-24",
                "close_price": 148.0,
                "pricing_status": "priced_non_authoritative",
                "verification_status": "verified_ucits_trading_line",
                "completed_close": True,
                "source_name": "test",
                "source_quality_status": "test_only",
            },
        ]
    }
    updated, evidence = revalue_state(
        state=state,
        pricing=pricing,
        run_id="20260727_120000",
        report_date=date(2026, 7, 27),
    )
    assert updated["invested_market_value_eur"] == 40100.0
    assert updated["nav_eur"] == 100100.0
    assert updated["positions"][0]["current_price_local"] == 105.0
    assert updated["positions"][1]["current_price_local"] == 148.0
    assert all(row["shares_delta_this_run"] == 0 for row in updated["positions"])
    assert all(row["last_action"] == "Hold" for row in updated["positions"])
    assert evidence["completed_close_gate_passed"] is True
    assert evidence["quantity_mutation"] is False
