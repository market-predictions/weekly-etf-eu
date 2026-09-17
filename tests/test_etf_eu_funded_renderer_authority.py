from __future__ import annotations

from runtime.apply_etf_eu_donor_parity_contract import apply_contract
from runtime.render_etf_eu_client_grade_v2_funded import (
    build_html,
    funded_overlay,
    validate_client_surface,
)


def state() -> dict:
    raw = {
        "state_valid": True,
        "report_date": "2026-08-07",
        "portfolio": {
            "starting_capital_eur": 100000.0,
            "nav_eur": 100000.0,
            "cash_eur": 50000.0,
            "invested_market_value_eur": 50000.0,
            "since_inception_return_pct": 0.0,
            "positions": [
                {"ticker": "VWCE", "fund_name": "Global", "isin": "IE00BK5BQT80", "shares": 151, "current_weight_pct": 25.0, "current_price_local": 165.0, "market_value_eur": 24915.0, "price_date": "2026-08-07", "pricing_status": "fresh_exact_unverified", "verification_status": "fresh_exact_unverified", "strategic_target_weight_pct": 50.0, "phase_target_weight_pct": 25.0, "target_weight_pct": 25.0},
                {"ticker": "EUNA", "fund_name": "Bonds", "isin": "IE00BDBRDM35", "shares": 1526, "current_weight_pct": 7.5, "current_price_local": 4.9, "market_value_eur": 7477.4, "price_date": "2026-08-07", "pricing_status": "fresh_exact_unverified", "verification_status": "fresh_exact_unverified", "strategic_target_weight_pct": 15.0, "target_weight_pct": 7.5},
                {"ticker": "SXR8", "fund_name": "S&P 500", "isin": "IE00B5BMR087", "shares": 10, "current_weight_pct": 7.0, "current_price_local": 705.0, "market_value_eur": 7050.0, "price_date": "2026-08-07", "pricing_status": "fresh_exact_unverified", "verification_status": "fresh_exact_unverified", "target_weight_pct": 7.5},
                {"ticker": "L0CK", "fund_name": "Cyber", "isin": "IE00BG0J4C88", "shares": 934, "current_weight_pct": 10.2, "current_price_local": 10.9, "market_value_eur": 10180.6, "price_date": "2026-08-07", "pricing_status": "fresh_exact_unverified", "verification_status": "fresh_exact_unverified", "target_weight_pct": 10.2},
            ],
        },
        "pricing": {
            "rows": [
                {"ticker": ticker, "authority_status": "fresh_exact_unverified", "verification_status": "fresh_exact_unverified", "close_date": "2026-08-07", "close_price": 1.0, "currency": "EUR", "primary_provider": "provider_a", "verification_providers": []}
                for ticker in ("VWCE", "EUNA", "SXR8", "L0CK")
            ]
        },
        "macro": {"fresh_for_report": True, "regime": "Test regime", "regime_nl": "Testregime", "fed": {}, "ecb": {}},
        "authority": {"portfolio_mutation": False, "trade_ledger_mutation": False},
        "verification_funnel": {"observed_lines": 10, "priced_lines": 4, "authorized_lines": 4, "verified_lines": 0, "primary_only_lines": 4, "unresolved_lines": 6},
        "opportunity_radar": [
            {"candidate_tickers": ["VWCE"], "status": "operationally_mature_not_funded", "name_nl": "Wereld", "name_en": "Global"},
            {"candidate_tickers": ["L0CK"], "status": "operationally_mature_not_funded", "name_nl": "Cyber", "name_en": "Cyber"},
        ],
        "next_run_input": {"priority_candidates": ["SXRV"], "required_actions": []},
        "allocation_map": [],
        "equity_curve": {"show_chart": False, "fallback_nl": "Onvoldoende historie.", "fallback_en": "Insufficient history."},
        "current_reunderwriting": {"status": "COMPLETE", "cash_after_explanation": "Cash remains tactical reserve."},
    }
    return apply_contract(raw)


def test_funded_overlay_preserves_normalized_allocation_map_and_four_position_state() -> None:
    normalized = state()
    original_allocation = list(normalized["allocation_map"])
    overlaid = funded_overlay(normalized)
    assert overlaid["allocation_map"] == original_allocation
    assert overlaid["funded_consistency"]["position_count"] == 4
    assert set(overlaid["funded_consistency"]["funded_tickers"]) == {"VWCE", "EUNA", "SXR8", "L0CK"}
    assert overlaid["funded_consistency"]["normalized_state_authority"] is True
    assert overlaid["funded_consistency"]["historical_target_copy_rendered"] is False


def test_native_html_has_current_funded_state_but_no_retired_target_copy() -> None:
    overlaid = funded_overlay(state())
    for language in ("nl", "en"):
        rendered = build_html(overlaid, language)
        lowered = rendered.casefold()
        assert "l0ck" in lowered
        assert "strategic target" not in lowered
        assert "strategisch doel" not in lowered
        assert "phase target" not in lowered
        assert "fasedoel" not in lowered
        assert "re-underwriting" in lowered


def test_native_html_needs_no_prefunding_semantic_repair() -> None:
    overlaid = funded_overlay(state())
    for language in ("nl", "en"):
        rendered = build_html(overlaid, language)
        lowered = rendered.casefold()
        assert all(ticker.casefold() in lowered for ticker in ("VWCE", "EUNA", "SXR8", "L0CK"))
        for stale in (
            "retain cash",
            "remains fully in cash",
            "portfolio is not yet invested",
            "cash behouden",
            "volledig in cash",
            "portefeuille is nog niet belegd",
        ):
            assert stale.casefold() not in lowered


def test_client_gate_rejects_retired_target_copy() -> None:
    overlaid = funded_overlay(state())
    bad = build_html(overlaid, "en") + " strategic target"
    try:
        validate_client_surface(bad, overlaid)
    except RuntimeError as exc:
        assert "ETF_EU_RETIRED_CLIENT_COPY_LEAK" in str(exc)
    else:
        raise AssertionError("retired target copy should fail closed")
