from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from pricing.ucits_price_provider_engine import build_legacy_validation_artifact
from pricing.ucits_primary_verification_legacy import apply_primary_verification_to_legacy
from runtime.build_etf_eu_client_grade_report_state_v2 import build_state
from runtime.reconcile_etf_eu_funded_markdown import reconcile_funded_markdown, validate_funded_markdown
from tools.validate_ucits_close_price_validation_basket_results import validate as validate_pricing


FUNDED = [
    ("VWCE", "IE00BK5BQT80"),
    ("EUNA", "IE00BDBRDM35"),
    ("SXR8", "IE00B5BMR087"),
    ("L0CK", "IE00BG0J4C88"),
]


def _portfolio() -> dict:
    return {
        "portfolio_mode": "model_portfolio",
        "base_currency": "EUR",
        "inception_date": "2026-07-01",
        "starting_capital_eur": 100000.0,
        "cash_eur": 50208.40,
        "invested_market_value_eur": 49791.60,
        "nav_eur": 100000.0,
        "positions": [
            {
                "exchange_ticker": ticker,
                "ticker": ticker,
                "isin": isin,
                "shares": 1,
                "market_value_eur": 12447.9,
            }
            for ticker, isin in FUNDED
        ],
    }


def _qualification() -> dict:
    lines = []
    for index, (ticker, isin) in enumerate(FUNDED, start=1):
        providers = [
            {
                "provider": "provider_a",
                "provider_symbol": ticker,
                "pricing_status": "priced",
                "close_date": "2026-08-07",
                "close_price": 100.0 + index,
                "observed_at_utc": "2026-08-08T00:00:00Z",
                "blockers": [],
            },
            {
                "provider": "provider_b",
                "provider_symbol": ticker,
                "pricing_status": "priced",
                "close_date": "2026-08-07",
                "close_price": 100.0 + index + 0.01,
                "observed_at_utc": "2026-08-08T00:00:00Z",
                "blockers": [],
            },
        ]
        lines.append(
            {
                "basket_id": f"funded-{index}",
                "fund_name": ticker,
                "instrument_type": "UCITS ETF",
                "exchange": "Xetra",
                "ticker": ticker,
                "expected_isin": isin,
                "expected_venue_code": "XETR",
                "expected_currency": "EUR",
                "funded": True,
                "selected_close_date": "2026-08-07",
                "selected_close_price": 100.0 + index,
                "consensus_close_price": 100.0 + index,
                "primary_provider": "provider_a",
                "primary_close_price": 100.0 + index,
                "static_primary_provider_symbol_binding": True,
                "same_date_provider_count": 2,
                "qualification_status": "fresh_exact_verified",
                "verification_status": "verified_same_date_within_tolerance",
                "verification_providers": ["provider_b"],
                "static_identity_binding": True,
                "static_identity_binding_status": "verified_static_exact_line",
                "static_identity_registry_id": f"funded-{index}",
                "identity_assurance_status": "static_registry_verified_exact_line",
                "identity_anchor_provider_count": 0,
                "valuation_grade": True,
                "provider_results": providers,
                "agreeing_providers": ["provider_a", "provider_b"],
                "agreement_spread_pct": 0.01,
            }
        )
    return {
        "schema_version": "ucits_price_provider_qualification_v1",
        "generated_at_utc": "2026-08-08T00:00:00Z",
        "report_date": "2026-08-07",
        "provider_order": ["provider_a", "provider_b"],
        "provider_configuration": {},
        "funded_line_count": 4,
        "funded_pricing_authorized_count": 4,
        "funded_verified_count": 4,
        "funded_unverified_count": 0,
        "funded_consensus_count": 4,
        "funded_static_identity_bound_count": 4,
        "funded_identity_anchor_count": 4,
        "report_pricing_gate_passed": True,
        "pricing_authority_policy": {
            "mode": "donor_aligned_primary_plus_verification_v1",
            "primary_provider_symbol_binding_required": True,
            "second_provider_required_for_liveness": False,
            "same_date_disagreement_blocks": True,
        },
        "identity_policy": {
            "static_exact_line_binding_required": True,
            "live_metadata_anchor_required_each_run": False,
        },
        "lines": lines,
    }


def test_candidate_pricing_state_and_markdown_path_end_to_end(tmp_path: Path) -> None:
    qualification_path = tmp_path / "qualification.json"
    pricing_path = tmp_path / "pricing.json"
    portfolio_path = tmp_path / "portfolio.json"
    macro_path = tmp_path / "macro.json"
    registry_path = tmp_path / "registry.yml"
    history_path = tmp_path / "history.csv"

    qualification_path.write_text(json.dumps(_qualification()), encoding="utf-8")
    portfolio_path.write_text(json.dumps(_portfolio()), encoding="utf-8")
    macro_path.write_text(json.dumps({"report_date": "2026-08-07"}), encoding="utf-8")
    registry_path.write_text("funds: []\n", encoding="utf-8")
    history_path.write_text("date,nav_eur,cash_eur,invested_market_value_eur\n", encoding="utf-8")

    build_legacy_validation_artifact(
        qualification_path=qualification_path,
        output_path=pricing_path,
        source_basket="config/ucits_close_price_validation_basket.yml",
        run_id="e2e-test",
    )
    apply_primary_verification_to_legacy(
        qualification_path=qualification_path,
        legacy_path=pricing_path,
    )

    pricing_result = validate_pricing(
        pricing_path,
        portfolio_state=portfolio_path,
        expected_report_date="2026-08-07",
    )
    assert pricing_result["valid"] is True
    assert pricing_result["funded_position_count"] == 4

    state = build_state(
        Namespace(
            portfolio_state=str(portfolio_path),
            valuation_history=str(history_path),
            pricing_artifact=str(pricing_path),
            macro_pack=str(macro_path),
            registry=str(registry_path),
            run_id="e2e-test",
            source_run_id="e2e-test",
            report_date="2026-08-07",
            report_suffix="260807",
        )
    )
    assert state["state_valid"] is True
    assert state["pricing_contract"]["report_pricing_gate_passed"] is True
    assert state["pricing_contract"]["funded_exact_primary_pricing_required"] is True
    assert state["pricing_contract"]["second_provider_required_for_liveness"] is False
    assert state["pricing_contract"]["funded_two_provider_consensus_required"] is False

    nl = reconcile_funded_markdown(
        "- **Reden:** de portefeuille bevat nog geen gefinancierde UCITS-posities en de huidige prijsrun levert marktobservaties, geen zelfstandige basis voor aankoop of waardering.",
        state,
        language="nl",
    )
    en = reconcile_funded_markdown(
        "- **Reason:** the portfolio still has no funded UCITS positions and the current pricing run provides market observations, not an independent basis for purchase or valuation.",
        state,
        language="en",
    )
    assert validate_funded_markdown(nl, state, language="nl") == []
    assert validate_funded_markdown(en, state, language="en") == []
    assert "4 gefinancierde UCITS-posities" in nl
    assert "4 funded UCITS positions" in en
    assert "L0CK" in nl and "L0CK" in en
