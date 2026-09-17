from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

import pytest

from pricing.ucits_close_price_validation_contract_v2 import validate_payload
from runtime.build_etf_eu_client_grade_report_state_v2 import build_state
from runtime.reconcile_etf_eu_funded_markdown import (
    reconcile_funded_markdown,
    render_funded_markdown,
    validate_funded_markdown,
)


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
                "avg_entry_local": 100.0,
                "current_price_local": 100.0,
                "market_value_local": 12447.9,
                "market_value_eur": 12447.9,
                "current_weight_pct": 12.4479,
                "trading_currency": "EUR",
            }
            for ticker, isin in FUNDED
        ],
    }


def _pricing() -> dict:
    rows = []
    for index, (ticker, isin) in enumerate(FUNDED, start=1):
        rows.append(
            {
                "basket_id": f"funded-{index}",
                "fund_name": ticker,
                "instrument_type": "UCITS ETF",
                "exchange": "Xetra",
                "ticker": ticker,
                "isin": isin,
                "venue_code": "XETR",
                "currency": "EUR",
                "pricing_status": "priced_non_authoritative",
                "close_date": "2026-08-07",
                "close_price": 100.0 + index,
                "source_id": "provider_a",
                "source_name": "provider_a exact completed close",
                "source_quality_status": "fresh_exact_verified",
                "source_agreement_status": "fresh_exact_verified",
                "observed_at_utc": "2026-08-08T00:00:00Z",
                "requested_report_date": "2026-08-07",
                "completed_close_on_or_before_report_date": True,
                "completed_close_on_requested_report_date": True,
                "valuation_grade": True,
                "fundable": False,
                "blockers": [],
                "primary_provider": "provider_a",
                "static_identity_binding": True,
                "static_identity_binding_status": "verified_static_exact_line",
                "static_identity_registry_id": f"funded-{index}",
                "identity_assurance_status": "static_registry_verified_exact_line",
                "static_primary_provider_symbol_binding": True,
                "verification_status": "verified_same_date_within_tolerance",
                "verification_providers": ["provider_b"],
                "provider_symbols": {"provider_a": ticker, "provider_b": ticker},
                "agreeing_providers": ["provider_a", "provider_b"],
                "same_date_provider_count": 2,
                "agreement_spread_pct": 0.1,
            }
        )
    return {
        "schema_version": "ucits_close_price_validation_basket_results_v2",
        "run_id": "test-run",
        "report_date": "2026-08-07",
        "source_basket": "config/ucits_close_price_validation_basket.yml",
        "generated_at_utc": "2026-08-08T00:00:00Z",
        "line_count": len(rows),
        "priced_line_count": len(rows),
        "failed_line_count": 0,
        "source_chain": ["provider_a", "provider_b"],
        "provider_configuration": {},
        "report_pricing_gate_passed": True,
        "valuation_grade": True,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
        "pricing_authority_policy": {
            "mode": "donor_aligned_primary_plus_verification_v1",
            "primary_provider_symbol_binding_required": True,
            "second_provider_required_for_liveness": False,
            "same_date_disagreement_blocks": True,
        },
        "rows": rows,
    }


def _primary_only_markdown_state() -> dict:
    position = {
        "exchange_ticker": "VWCE",
        "ticker": "VWCE",
        "isin": "IE00BK5BQT80",
        "shares": 2,
        "current_price_local": 169.06,
        "market_value_eur": 338.12,
        "current_weight_pct": 25.27,
        "price_date": "2026-08-07",
        "pricing_status": "fresh_exact_unverified",
        "verification_status": "fresh_exact_unverified",
        "primary_provider": "provider_a",
        "verification_providers": [],
        "current_allocation_decision": "hold",
    }
    return {
        "report_date": "2026-08-07",
        "portfolio": {
            "cash_eur": 1000.0,
            "invested_market_value_eur": 338.12,
            "nav_eur": 1338.12,
            "positions": [position],
        },
        "pricing": {
            "rows": [
                {
                    "ticker": "VWCE",
                    "fund_name": "Vanguard FTSE All-World UCITS ETF",
                    "isin": "IE00BK5BQT80",
                    "exchange": "Xetra",
                    "close_date": "2026-08-07",
                    "close_price": 169.06,
                    "currency": "EUR",
                    "authority_status": "fresh_exact_unverified",
                    "verification_status": "fresh_exact_unverified",
                    "primary_provider": "provider_a",
                    "verification_providers": [],
                }
            ]
        },
    }


def test_v2_pricing_contract_accepts_four_funded_verified_lines() -> None:
    result = validate_payload(
        _pricing(),
        expected_report_date="2026-08-07",
        portfolio_state=_portfolio(),
        require_funded_consensus=True,
    )
    assert result["valid"] is True
    assert result["funded_position_count"] == 4
    assert all(row["passed"] for row in result["funded_evidence"])


def test_v2_pricing_contract_accepts_single_exact_primary_as_unverified() -> None:
    payload = _pricing()
    row = payload["rows"][0]
    row["source_quality_status"] = "fresh_exact_unverified"
    row["source_agreement_status"] = "fresh_exact_unverified"
    row["verification_status"] = "unverified_no_same_date_verifier"
    row["verification_providers"] = []
    row["agreeing_providers"] = ["provider_a"]
    row["same_date_provider_count"] = 1
    result = validate_payload(
        payload,
        expected_report_date="2026-08-07",
        portfolio_state=_portfolio(),
        require_funded_consensus=True,
    )
    assert result["valid"] is True


def test_v2_pricing_contract_rejects_v1_schema() -> None:
    payload = _pricing()
    payload["schema_version"] = "ucits_close_price_validation_basket_results_v1"
    result = validate_payload(
        payload,
        expected_report_date="2026-08-07",
        portfolio_state=_portfolio(),
        require_funded_consensus=True,
    )
    assert result["valid"] is False
    assert any("pricing schema" in blocker for blocker in result["blockers"])


def test_v2_pricing_contract_rejects_report_date_drift() -> None:
    result = validate_payload(
        _pricing(),
        expected_report_date="2026-08-10",
        portfolio_state=_portfolio(),
        require_funded_consensus=True,
    )
    assert result["valid"] is False
    assert any("report_date mismatch" in blocker for blocker in result["blockers"])


def test_markdown_compatibility_alias_ignores_stale_source_and_renders_current_state() -> None:
    state = _primary_only_markdown_state()
    stale_source = "The portfolio remains fully in cash. two-provider completed-close consensus."
    result = reconcile_funded_markdown(stale_source, state, language="en")
    assert "1 funded UCITS positions (VWCE)" in result
    assert "Exact close · no current independent verifier" in result
    assert "remains fully in cash" not in result
    assert "two-provider completed-close consensus" not in result
    assert validate_funded_markdown(result, state, language="en") == []


def test_native_markdown_is_bilingual_and_primary_only_truthful() -> None:
    state = _primary_only_markdown_state()
    nl = render_funded_markdown(state, language="nl")
    en = render_funded_markdown(state, language="en")
    assert "1 gefinancierde UCITS-posities (VWCE)" in nl
    assert "Exacte slotkoers · geen actuele onafhankelijke verifier" in nl
    assert "1 funded UCITS positions (VWCE)" in en
    assert "Exact close · no current independent verifier" in en
    assert "| Exact close · independently verified |" not in en
    assert "| Exacte slotkoers · onafhankelijk geverifieerd |" not in nl
    assert validate_funded_markdown(nl, state, language="nl") == []
    assert validate_funded_markdown(en, state, language="en") == []


def test_markdown_validator_rejects_wrong_count_and_retired_target_copy() -> None:
    state = {"portfolio": _portfolio()}
    bad = "The model portfolio contains three funded UCITS positions. Strategic target weight. VWCE EUNA SXR8 L0CK"
    blockers = validate_funded_markdown(bad, state, language="en")
    assert blockers
    assert any("dynamic funded position count" in blocker for blocker in blockers)
    assert any("strategic target weight" in blocker for blocker in blockers)


def test_markdown_validator_rejects_retired_universal_source_count_claims() -> None:
    state = _primary_only_markdown_state()
    stale = "\n".join(
        [
            "1 funded UCITS positions (VWCE)",
            "1 of 1 funded lines have authorized exact-line completed-close pricing.",
            "A current price verification with two independent sources is available for all funded positions.",
        ]
    )
    blockers = validate_funded_markdown(stale, state, language="en")
    assert any("two independent sources" in blocker for blocker in blockers)


def test_normalized_state_builder_requires_v2_gate(tmp_path: Path) -> None:
    pricing_path = tmp_path / "pricing.json"
    portfolio_path = tmp_path / "portfolio.json"
    macro_path = tmp_path / "macro.json"
    registry_path = tmp_path / "registry.yml"
    history_path = tmp_path / "history.csv"

    pricing_path.write_text(json.dumps(_pricing()), encoding="utf-8")
    portfolio_path.write_text(json.dumps(_portfolio()), encoding="utf-8")
    macro_path.write_text(json.dumps({"report_date": "2026-08-07"}), encoding="utf-8")
    registry_path.write_text("funds: []\n", encoding="utf-8")
    history_path.write_text("date,nav_eur,cash_eur,invested_market_value_eur\n", encoding="utf-8")

    args = Namespace(
        portfolio_state=str(portfolio_path),
        valuation_history=str(history_path),
        pricing_artifact=str(pricing_path),
        macro_pack=str(macro_path),
        registry=str(registry_path),
        run_id="test-run",
        source_run_id="test-run",
        report_date="2026-08-07",
        report_suffix="260807",
    )
    state = build_state(args)
    assert state["state_valid"] is True
    assert state["schema_version"] == "etf_eu_client_grade_report_state_v3"
    assert state["pricing_contract"]["report_pricing_gate_passed"] is True
    assert state["pricing_contract"]["funded_exact_primary_pricing_required"] is True
    assert state["pricing_contract"]["second_provider_required_for_liveness"] is False
    assert state["pricing_contract"]["funded_two_provider_consensus_required"] is False

    payload = _pricing()
    payload["report_pricing_gate_passed"] = False
    pricing_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(RuntimeError, match="Canonical v2 pricing contract failed"):
        build_state(args)
