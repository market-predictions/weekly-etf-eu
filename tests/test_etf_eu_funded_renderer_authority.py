from __future__ import annotations

from runtime.apply_etf_eu_donor_parity_contract import apply_contract
from runtime.render_etf_eu_client_grade_v2_funded import (
    funded_overlay,
    patch_copy,
    position_table,
    validate_client_surface,
)


def state() -> dict:
    raw = {
        "state_valid": True,
        "portfolio": {
            "nav_eur": 100000.0,
            "cash_eur": 50000.0,
            "invested_market_value_eur": 50000.0,
            "positions": [
                {"ticker": "VWCE", "fund_name": "Global", "isin": "IE00BK5BQT80", "shares": 151, "current_weight_pct": 25.0, "current_price_local": 165.0, "market_value_eur": 24915.0, "price_date": "2026-08-07", "strategic_target_weight_pct": 50.0, "phase_target_weight_pct": 25.0, "target_weight_pct": 25.0},
                {"ticker": "EUNA", "fund_name": "Bonds", "isin": "IE00BDBRDM35", "shares": 1526, "current_weight_pct": 7.5, "current_price_local": 4.9, "market_value_eur": 7477.4, "price_date": "2026-08-07", "strategic_target_weight_pct": 15.0, "target_weight_pct": 7.5},
                {"ticker": "SXR8", "fund_name": "S&P 500", "isin": "IE00B5BMR087", "shares": 10, "current_weight_pct": 7.0, "current_price_local": 705.0, "market_value_eur": 7050.0, "price_date": "2026-08-07", "target_weight_pct": 7.5},
                {"ticker": "L0CK", "fund_name": "Cyber", "isin": "IE00BG0J4C88", "shares": 934, "current_weight_pct": 10.2, "current_price_local": 10.9, "market_value_eur": 10180.6, "price_date": "2026-08-07", "target_weight_pct": 10.2},
            ],
        },
        "authority": {"portfolio_mutation": False, "trade_ledger_mutation": False},
        "verification_funnel": {"observed_lines": 10, "verified_lines": 4},
        "opportunity_radar": [
            {"candidate_tickers": ["VWCE"], "status": "operationally_mature_not_funded"},
            {"candidate_tickers": ["L0CK"], "status": "operationally_mature_not_funded"},
        ],
        "next_run_input": {"priority_candidates": ["SXRV"], "required_actions": []},
        "allocation_map": [],
    }
    return apply_contract(raw)


def test_funded_overlay_preserves_normalized_allocation_map_and_four_position_state() -> None:
    normalized = state()
    original_allocation = list(normalized["allocation_map"])
    overlaid = funded_overlay(normalized)
    assert overlaid["allocation_map"] == original_allocation
    assert overlaid["funded_consistency"]["position_count"] == 4
    assert set(overlaid["funded_consistency"]["funded_tickers"]) == {"VWCE", "EUNA", "SXR8", "L0CK"}
    assert overlaid["verification_funnel"]["decision"].startswith("preserve_protected_funded_state")
    assert "three_position" not in overlaid["verification_funnel"]["decision"]


def test_position_table_has_current_weight_and_reunderwriting_but_no_target_column() -> None:
    overlaid = funded_overlay(state())
    for language in ("nl", "en"):
        rendered = position_table(overlaid, language)
        lowered = rendered.lower()
        assert "l0ck" in lowered
        assert "strategic target" not in lowered
        assert "strategisch doel" not in lowered
        assert "phase target" not in lowered
        assert "fasedoel" not in lowered
        assert "re-underwriting" in lowered


def test_patch_copy_converts_stale_prefunding_copy_and_client_gate_passes() -> None:
    overlaid = funded_overlay(state())
    stale_en = " ".join(
        [
            "Retain cash",
            "The S&amp;P 500 UCITS lines are operationally most advanced, but capital deployment requires a separate allocation decision.",
            "This week: no portfolio transaction; the EU model portfolio remains fully in cash.",
            "The portfolio is not yet invested. This is a deliberate capital-preservation state.",
            "Retain EUR 100,000 cash until a separate allocation decision is made.",
            "<p>Position analysis active.</p>",
        ]
    )
    rendered = patch_copy(stale_en, overlaid, "en")
    validate_client_surface(rendered, overlaid)
    assert "4 protected model positions" in rendered
    assert all(ticker in rendered for ticker in ("VWCE", "EUNA", "SXR8", "L0CK"))


def test_client_gate_rejects_retired_target_copy() -> None:
    overlaid = funded_overlay(state())
    bad = "VWCE EUNA SXR8 L0CK strategic target"
    try:
        validate_client_surface(bad, overlaid)
    except RuntimeError as exc:
        assert "ETF_EU_RETIRED_CLIENT_COPY_LEAK" in str(exc)
    else:
        raise AssertionError("retired target copy should fail closed")
