from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CONTRACT = Path("control/ETF_EU_COCKPIT_PDF_READINESS_EVIDENCE_ACQUISITION_CONTRACT_V1.md")
RUNNER = Path("runtime/fetch_etf_eu_closing_price_poc.py")
ARTIFACT = Path("output/client_surface/etf_eu_closing_price_poc_20260703_000000.json")
PREVIEW = Path("output/client_surface/etf_eu_closing_price_poc_preview_20260703_000000.md")
NOTES = Path("output/client_surface/etf_eu_readiness_evidence_acquisition_contract_notes_20260703_000000.md")
REGISTRY = Path("config/ucits_symbol_registry.yml")
REPAIR = Path("output/client_surface/etf_eu_closing_price_poc_provider_repair_20260703_000000.json")

REQUIRED_FILES = [CONTRACT, RUNNER, ARTIFACT, PREVIEW, NOTES, REGISTRY, REPAIR]
REQUIRED_FALSE = [
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
    "fake_price_used",
    "us_proxy_price_used",
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate() -> dict[str, Any]:
    for path in REQUIRED_FILES:
        _require(path.exists(), f"missing file: {path}")

    data = _load_json(ARTIFACT)
    repair = _load_json(REPAIR)

    expected = {
        "schema_version": "etf_eu_closing_price_poc_v1",
        "repository": "market-predictions/weekly-etf-eu",
        "work_package_id": "ETF-EU-WP15Y",
        "legacy_work_package_id": "WP15Y",
        "symbol": "SXR8.DE",
        "isin": "IE00B5BMR087",
        "exchange": "Xetra",
        "exchange_ticker": "SXR8",
        "trading_currency": "EUR",
        "pricing_symbol": "SXR8.DE",
        "provider_status": "success",
        "pricing_poc_status": "success_non_valuation_grade_close_obtained",
        "selected_next_package": "ETF-EU-WP15Z",
    }
    for key, value in expected.items():
        _require(data.get(key) == value, f"unexpected {key}: {data.get(key)!r}")

    _require(data.get("limited_pricing_poc_performed") is True, "limited_pricing_poc_performed must be true")
    _require(data.get("latest_close_date") == "2026-07-03", "unexpected latest_close_date")
    _require(isinstance(data.get("latest_close"), (int, float)), "latest_close must be numeric")
    _require(data["latest_close"] > 0, "latest_close must be positive")
    _require(data.get("pricing_source") == "yahoo_chart_v8", "unexpected pricing_source")
    _require(bool(data.get("pricing_fetch_timestamp")), "pricing_fetch_timestamp missing")
    _require(data.get("pricing_freshness_status") == "latest_available_daily_close_from_provider", "unexpected freshness status")

    for key in REQUIRED_FALSE:
        _require(data.get(key) is False, f"expected false for {key}")

    _require(repair.get("work_package_id") == "ETF-EU-WP15Y-FIX", "repair artifact work_package_id mismatch")
    _require(repair.get("source_work_package") == "ETF-EU-WP15Y", "repair artifact source mismatch")
    _require(repair.get("repair_status") == "success", "repair_status must be success")
    _require(repair.get("successful_provider") == "yahoo_chart_v8", "successful_provider mismatch")
    _require(repair.get("latest_close") == data.get("latest_close"), "repair latest_close mismatch")
    _require(repair.get("latest_close_date") == data.get("latest_close_date"), "repair latest_close_date mismatch")
    _require(repair.get("selected_next_package") == "ETF-EU-WP15Z", "repair next package mismatch")

    preview = PREVIEW.read_text(encoding="utf-8")
    for marker in ["# ETF EU Closing Price POC", "SXR8.DE", "IE00B5BMR087", "2026-07-03", "706.119995", "success"]:
        _require(marker in preview, f"preview missing marker: {marker}")

    return {
        "status": "valid",
        "provider_status": data["provider_status"],
        "latest_close_date": data["latest_close_date"],
        "latest_close": data["latest_close"],
        "selected_next_package": data["selected_next_package"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
