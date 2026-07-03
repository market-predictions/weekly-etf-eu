from __future__ import annotations

import json

from tools.validate_etf_eu_closing_price_poc import (
    ARTIFACT,
    CONTRACT,
    NOTES,
    PREVIEW,
    REGISTRY,
    RUNNER,
    validate,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_expected_files_exist() -> None:
    assert CONTRACT.exists()
    assert RUNNER.exists()
    assert ARTIFACT.exists()
    assert PREVIEW.exists()
    assert NOTES.exists()
    assert REGISTRY.exists()


def test_contract_contains_required_evidence_fields() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    for field in [
        "isin", "fund_name", "ucits_status", "priips_kid_status", "exchange", "exchange_ticker",
        "trading_currency", "pricing_symbol", "latest_close_date", "latest_close", "pricing_source",
        "pricing_fetch_timestamp", "pricing_freshness_status", "ter_pct", "replication_method",
        "distribution_policy", "hedged_unhedged_status", "liquidity_spread_status", "candidate_thesis",
        "candidate_invalidation", "decision_status",
    ]:
        assert field in text


def test_artifact_identity_and_symbol_are_correct() -> None:
    data = _artifact()
    assert data["repository"] == "market-predictions/weekly-etf-eu"
    assert data["work_package_id"] == "ETF-EU-WP15Y"
    assert data["symbol"] == "SXR8.DE"
    assert data["isin"] == "IE00B5BMR087"
    assert data["exchange"] == "Xetra"
    assert data["exchange_ticker"] == "SXR8"
    assert data["trading_currency"] == "EUR"
    assert data["pricing_symbol"] == "SXR8.DE"


def test_provider_success_or_failure_shape_is_valid() -> None:
    data = _artifact()
    assert data["provider_status"] in {"success", "failed"}
    if data["provider_status"] == "success":
        assert data["latest_close_date"]
        assert isinstance(data["latest_close"], (int, float))
        assert data["pricing_source"]
        assert data["pricing_fetch_timestamp"]
        assert data["pricing_freshness_status"]
    else:
        assert data["latest_close"] is None
        assert data["provider_error"]
        assert data["pricing_poc_status"] == "failed_provider_or_symbol_unavailable"


def test_no_fake_or_us_proxy_price_is_accepted() -> None:
    data = _artifact()
    assert data["fake_price_used"] is False
    assert data["us_proxy_price_used"] is False
    assert data["symbol"] not in {"SPY", "QQQ", "GLD", "SMH", "PAVE"}


def test_client_grade_and_delivery_preflight_claims_remain_false() -> None:
    data = _artifact()
    assert data["valuation_grade"] is False
    assert data["pricing_evidence_for_client_grade"] is False
    assert data["pricing_evidence_for_delivery_preflight"] is False
    assert data["client_grade_claim"] is False
    assert data["client_grade_enough_for_delivery_preflight_discussion"] is False
    assert data["delivery_ready"] is False
    assert data["delivery_preflight_allowed"] is False


def test_no_portfolio_funding_or_delivery_authority_changed() -> None:
    data = _artifact()
    assert data["production_delivery"] is False
    assert data["portfolio_mutation"] is False
    assert data["candidate_promotion"] is False
    assert data["funding_authority"] is False
    assert data["receipt_artifact_created"] is False
    assert data["production_manifest_created"] is False
    assert data["source_pdf_replaced"] is False
    assert data["renderer_changed"] is False


def test_preview_is_client_readable() -> None:
    text = PREVIEW.read_text(encoding="utf-8")
    assert "# ETF EU Closing Price POC" in text
    assert "## What this proves" in text
    assert "## Closing price result" in text
    assert "This is a limited proof-of-concept" in text
    assert "SXR8.DE" in text


def test_validator_passes() -> None:
    result = validate()
    assert result["status"] == "valid"
    assert result["provider_status"] in {"success", "failed"}
    assert result["selected_next_package"]
