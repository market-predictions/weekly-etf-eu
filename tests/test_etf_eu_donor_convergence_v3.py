from __future__ import annotations

import argparse
from pathlib import Path

from runtime import adapt_weekly_etf_macro_for_eu as macro
from runtime import render_etf_eu_client_grade_v3_converged as renderer
from tools import build_etf_eu_routine_report_package_v2 as package


def test_current_funded_valuation_uses_report_date_completed_closes_and_preserves_quantities() -> None:
    state = {
        "portfolio": {
            "cash_eur": 50_000.0,
            "positions": [
                {"ticker": "VWCE", "shares": 10, "current_price_local": 90.0},
                {"ticker": "EUNA", "shares": 20, "current_price_local": 4.0},
                {"ticker": "SXR8", "shares": 2, "current_price_local": 650.0},
                {"ticker": "L0CK", "shares": 100, "current_price_local": 10.0},
            ],
        }
    }
    pricing = {
        "rows": [
            {"ticker": "VWCE", "close_price": 100.0, "close_date": "2026-08-07", "currency": "EUR", "completed_close_on_or_before_report_date": True, "source_name": "a", "source_agreement_status": "pass"},
            {"ticker": "EUNA", "close_price": 5.0, "close_date": "2026-08-07", "currency": "EUR", "completed_close_on_or_before_report_date": True, "source_name": "a", "source_agreement_status": "pass"},
            {"ticker": "SXR8", "close_price": 700.0, "close_date": "2026-08-07", "currency": "EUR", "completed_close_on_or_before_report_date": True, "source_name": "a", "source_agreement_status": "pass"},
            {"ticker": "L0CK", "close_price": 11.0, "close_date": "2026-08-07", "currency": "EUR", "completed_close_on_or_before_report_date": True, "source_name": "a", "source_agreement_status": "pass"},
        ]
    }
    before = [(row["ticker"], row["shares"]) for row in state["portfolio"]["positions"]]
    result = package._apply_current_funded_valuation(state, pricing, "2026-08-07")
    after = [(row["ticker"], row["shares"]) for row in result["portfolio"]["positions"]]
    assert before == after
    assert result["portfolio"]["cash_eur"] == 50_000.0
    assert result["portfolio"]["invested_market_value_eur"] == 3600.0
    assert result["portfolio"]["nav_eur"] == 53_600.0
    assert all(row["price_date"] == "2026-08-07" for row in result["portfolio"]["positions"])
    assert all(row["pricing_status"] == "current_completed_close_from_run_pricing" for row in result["portfolio"]["positions"])


def test_valuation_history_replaces_same_report_date_and_reconciles_latest_nav(tmp_path: Path) -> None:
    history = tmp_path / "history.csv"
    history.write_text(
        "date,nav_eur,cash_eur,invested_market_value_eur,daily_return_pct,since_inception_return_pct,drawdown_pct,comment,source_report\n"
        "2026-08-05,100000.00,50000.00,50000.00,0.000000,0.000000,0.000000,old,old\n"
        "2026-08-07,99999.00,50000.00,49999.00,-0.001000,-0.001000,-0.001000,stale,stale\n",
        encoding="utf-8",
    )
    state = {"portfolio": {"starting_capital_eur": 100000.0, "nav_eur": 101234.56, "cash_eur": 50208.40, "invested_market_value_eur": 51026.16}}
    rows = package._persist_current_valuation_history(history, state, "2026-08-07", "current")
    assert [row["date"] for row in rows].count("2026-08-07") == 1
    assert rows[-1]["nav_eur"] == 101234.56
    equity = package._equity_from_history(rows, {"nav_eur": 101234.56, "position_count": 4})
    assert equity["latest_nav_matches_state"] is True


def test_macro_freshness_uses_underlying_donor_date_not_wrapper_date() -> None:
    donor = {
        "report_date": "2026-08-07",
        "generated_at_utc": "2026-08-07T12:00:00Z",
        "current_context_refresh": {"historical_donor_report_date": "2026-07-29"},
    }
    donor_date, raw, source = macro._underlying_donor_date(donor)
    assert raw == "2026-07-29"
    assert source == "current_context_refresh.historical_donor_report_date"
    assert donor_date.isoformat() == "2026-07-29"


def test_macro_adapter_rejects_wrapper_that_masks_stale_underlying_evidence() -> None:
    donor = {
        "report_date": "2026-08-07",
        "generated_at_utc": "2026-08-07T12:00:00Z",
        "current_context_refresh": {"historical_donor_report_date": "2026-07-29"},
    }
    try:
        macro.adapt(donor, report_date="2026-08-07", run_id="x", source_url="file://x", source_sha256="0" * 64)
    except RuntimeError as exc:
        assert "underlying donor macro evidence" in str(exc) or "not current enough" in str(exc)
    else:
        raise AssertionError("stale underlying donor evidence was incorrectly refreshed by wrapper date")


def test_v3_renderer_sanitizer_rejects_retired_client_control() -> None:
    state = {"portfolio": {"positions": [{"ticker": "VWCE"}]}}
    try:
        renderer._final_sanitize("reserve minimaal 7,50%", state, "nl")
    except RuntimeError as exc:
        assert "retired/shadow authority" in str(exc)
    else:
        raise AssertionError("retired cash control was not rejected")
