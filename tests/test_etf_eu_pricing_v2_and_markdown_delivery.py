from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

import pytest

from pricing.ucits_close_price_validation_contract_v2 import validate_payload
from runtime.build_etf_eu_client_grade_report_state_v2 import build_state
from runtime.reconcile_etf_eu_funded_markdown import (
    reconcile_funded_markdown,
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
                "market_value_eur": 12447.9,
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
                "source_id": "provider_consensus",
                "source_name": "Development provider consensus",
                "source_quality_status": "development_consensus",
                "source_agreement_status": "qualified_development_consensus",
                "observed_at_utc": "2026-08-08T00:00:00Z",
                "requested_report_date": "2026-08-07",
                "completed_close_on_or_before_report_date": True,
                "valuation_grade": True,
                "fundable": False,
                "blockers": [],
                "provider_symbols": {"provider_a": ticker, "provider_b": ticker},
                "agreeing_providers": ["provider_a", "provider_b"],
                "agreement_spread_pct": 0.1,
                "verification_status": "verified_ucits_trading_line",
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
        "rows": rows,
    }


def test_v2_pricing_contract_accepts_four_funded_consensus_lines() -> None:
    result = validate_payload(
        _pricing(),
        expected_report_date="2026-08-07",
        portfolio_state=_portfolio(),
        require_funded_consensus=True,
    )
    assert result["valid"] is True
    assert result["funded_position_count"] == 4
    assert all(row["passed"] for row in result["funded_evidence"])


def test_v2_pricing_contract_rejects_v1_schema_and_one_provider() -> None:
    payload = _pricing()
    payload["schema_version"] = "ucits_close_price_validation_basket_results_v1"
    payload["rows"][0]["agreeing_providers"] = ["provider_a"]
    result = validate_payload(
        payload,
        expected_report_date="2026-08-07",
        portfolio_state=_portfolio(),
        require_funded_consensus=True,
    )
    assert result["valid"] is False
    assert any("pricing schema" in blocker for blocker in result["blockers"])
    assert any("fewer_than_two_agreeing_providers" in blocker for blocker in result["blockers"])


def test_v2_pricing_contract_rejects_report_date_drift() -> None:
    result = validate_payload(
        _pricing(),
        expected_report_date="2026-08-10",
        portfolio_state=_portfolio(),
        require_funded_consensus=True,
    )
    assert result["valid"] is False
    assert any("report_date mismatch" in blocker for blocker in result["blockers"])


def test_markdown_reconciliation_is_dynamic_and_contains_l0ck() -> None:
    state = {"portfolio": _portfolio()}
    source_nl = "\n".join(
        [
            "- **Actie:** geen transactie; EUR 100.000 cash behouden.",
            "- **Reden:** de portefeuille bevat nog geen gefinancierde UCITS-posities en de huidige prijsrun levert marktobservaties, geen zelfstandige basis voor aankoop of waardering.",
            "- **Beste operationele kandidaat:** de geverifieerde S&P 500 UCITS-lijnen blijven het verst gevorderd voor verdere bevestiging bij de broker en van de handelslijn.",
        ]
    )
    result_nl = reconcile_funded_markdown(source_nl, state, language="nl")
    assert "4 gefinancierde UCITS-posities" in result_nl
    assert "L0CK" in result_nl
    assert validate_funded_markdown(result_nl, state, language="nl") == []

    source_en = "\n".join(
        [
            "- **Action:** no trade; retain EUR 100,000 cash.",
            "- **Reason:** the portfolio still has no funded UCITS positions and the current pricing run provides market observations, not an independent basis for purchase or valuation.",
            "- **Most advanced operational candidate:** the verified S&P 500 UCITS lines remain furthest advanced for broker and trading-line confirmation.",
        ]
    )
    result_en = reconcile_funded_markdown(source_en, state, language="en")
    assert "4 funded UCITS positions" in result_en
    assert "L0CK" in result_en
    assert validate_funded_markdown(result_en, state, language="en") == []


def test_markdown_validator_rejects_three_position_and_retired_target_copy() -> None:
    state = {"portfolio": _portfolio()}
    bad = "The model portfolio contains three funded UCITS positions. Strategic target weight. VWCE EUNA SXR8 L0CK"
    blockers = validate_funded_markdown(bad, state, language="en")
    assert blockers
    assert any("three funded" in blocker for blocker in blockers)
    assert any("strategic target" in blocker for blocker in blockers)


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
    assert state["schema_version"] == "etf_eu_client_grade_report_state_v2"
    assert state["pricing_contract"]["report_pricing_gate_passed"] is True
    assert state["pricing_contract"]["funded_two_provider_consensus_required"] is True

    payload = _pricing()
    payload["report_pricing_gate_passed"] = False
    pricing_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(RuntimeError, match="Canonical v2 pricing contract failed"):
        build_state(args)
