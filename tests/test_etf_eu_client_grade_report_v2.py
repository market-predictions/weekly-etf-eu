from __future__ import annotations

from argparse import Namespace
from copy import deepcopy

from runtime.build_etf_eu_client_grade_report_state import build_state
from runtime.render_etf_eu_client_grade_report import build_html


PRICING = "output/pricing/ucits_close_price_validation_basket_results_20260712_125000.json"


def _state():
    return build_state(
        Namespace(
            portfolio_state="output/etf_eu_portfolio_state.json",
            valuation_history="output/etf_eu_valuation_history.csv",
            pricing_artifact=PRICING,
            macro_pack="output/macro/latest.json",
            registry="config/ucits_symbol_registry.yml",
            run_id="test_client_grade_v2",
            source_run_id="20260712_125000",
            report_date="2026-07-12",
            report_suffix="260712",
        )
    )


def test_cash_only_state_uses_truthful_callout_and_full_report_structure() -> None:
    state = _state()
    assert state["state_valid"] is True
    assert state["portfolio"]["position_count"] == 0
    assert state["equity_curve"]["show_chart"] is False
    assert state["verification_funnel"]["verified_lines"] == 2

    nl = build_html(state, language="nl")
    en = build_html(state, language="en")

    assert "Beleggersrapport" in nl
    assert "Analistenrapport" in nl
    assert "Besliscockpit" in nl
    assert "UCITS-kandidaten en prijsbewijs" in nl
    assert '<div class="cash-callout">' in nl
    assert '<svg class="equity-curve-svg"' not in nl
    assert "Macro-refresh vereist" in nl
    assert "candidate_requires_verification" not in nl
    assert "Investor report" in en
    assert "Analyst report" in en
    assert "research only" in en


def test_equity_curve_activates_only_with_meaningful_history() -> None:
    state = deepcopy(_state())
    state["equity_curve"].update(
        {
            "show_chart": True,
            "latest_nav_matches_state": True,
            "points": [
                {"date": "2026-05-30", "nav_eur": 100000.0},
                {"date": "2026-07-12", "nav_eur": 100000.0},
            ],
        }
    )
    html = build_html(state, language="nl")
    assert '<svg class="equity-curve-svg"' in html
    assert '<div class="cash-callout">' not in html
