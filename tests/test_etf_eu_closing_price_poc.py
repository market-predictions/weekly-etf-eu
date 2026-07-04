from __future__ import annotations

import json

from tools.validate_etf_eu_closing_price_poc import (
    ARTIFACT,
    CONTRACT,
    NOTES,
    PREVIEW,
    REGISTRY,
    REPAIR,
    RUNNER,
    validate,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _repair() -> dict:
    return json.loads(REPAIR.read_text(encoding="utf-8"))


def test_expected_files_exist() -> None:
    assert CONTRACT.exists()
    assert RUNNER.exists()
    assert ARTIFACT.exists()
    assert PREVIEW.exists()
    assert NOTES.exists()
    assert REGISTRY.exists()
    assert REPAIR.exists()


def test_runner_contains_provider_logic() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    assert "query1.finance.yahoo.com" in text
    assert "SXR8.DE" in text
    assert "IE00B5BMR087" in text


def test_artifact_success_shape() -> None:
    data = _artifact()
    assert data["provider_status"] == "success"
    assert data["pricing_poc_status"] == "success_non_valuation_grade_close_obtained"
    assert data["symbol"] == "SXR8.DE"
    assert data["isin"] == "IE00B5BMR087"
    assert data["trading_currency"] == "EUR"
    assert data["latest_close_date"] == "2026-07-03"
    assert isinstance(data["latest_close"], (int, float))
    assert data["latest_close"] > 0
    assert data["pricing_source"] == "yahoo_chart_v8"
    assert data["pricing_fetch_timestamp"]
    assert data["pricing_freshness_status"] == "latest_available_daily_close_from_provider"


def test_no_proxy_or_manual_price_flags() -> None:
    data = _artifact()
    assert data["fake_price_used"] is False
    assert data["us_proxy_price_used"] is False
    assert data["symbol"] not in {"SPY", "QQQ", "GLD", "SMH", "PAVE"}


def test_no_authority_flags_remain_false() -> None:
    data = _artifact()
    for key in [
        "valuation_grade",
        "pricing_evidence_for_client_grade",
        "pricing_evidence_for_delivery_preflight",
        "production_delivery",
        "portfolio_mutation",
        "candidate_promotion",
        "funding_authority",
        "client_grade_claim",
        "client_grade_enough_for_delivery_preflight_discussion",
        "delivery_ready",
        "delivery_preflight_allowed",
        "receipt_artifact_created",
        "production_manifest_created",
        "source_pdf_replaced",
        "renderer_changed",
    ]:
        assert data[key] is False


def test_preview_shows_successful_close() -> None:
    text = PREVIEW.read_text(encoding="utf-8")
    assert "# ETF EU Closing Price POC" in text
    assert "SXR8.DE" in text
    assert "IE00B5BMR087" in text
    assert "2026-07-03" in text
    assert "706.119995" in text
    assert "success" in text


def test_repair_artifact_matches_success() -> None:
    data = _artifact()
    repair = _repair()
    assert repair["work_package_id"] == "ETF-EU-WP15Y-FIX"
    assert repair["source_work_package"] == "ETF-EU-WP15Y"
    assert repair["repair_status"] == "success"
    assert repair["successful_provider"] == "yahoo_chart_v8"
    assert repair["latest_close_date"] == data["latest_close_date"]
    assert repair["latest_close"] == data["latest_close"]
    assert repair["selected_next_package"] == "ETF-EU-WP15Z"


def test_validator_passes() -> None:
    result = validate()
    assert result["status"] == "valid"
    assert result["provider_status"] == "success"
    assert result["selected_next_package"] == "ETF-EU-WP15Z"
