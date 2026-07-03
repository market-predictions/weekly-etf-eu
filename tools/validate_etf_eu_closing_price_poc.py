from __future__ import annotations

import json
from pathlib import Path

CONTRACT = Path("control/ETF_EU_COCKPIT_PDF_READINESS_EVIDENCE_ACQUISITION_CONTRACT_V1.md")
RUNNER = Path("runtime/fetch_etf_eu_closing_price_poc.py")
ARTIFACT = Path("output/client_surface/etf_eu_closing_price_poc_20260703_000000.json")
PREVIEW = Path("output/client_surface/etf_eu_closing_price_poc_preview_20260703_000000.md")
NOTES = Path("output/client_surface/etf_eu_readiness_evidence_acquisition_contract_notes_20260703_000000.md")
REGISTRY = Path("config/ucits_symbol_registry.yml")

REQUIRED_CONTRACT_FIELDS = [
    "isin", "fund_name", "ucits_status", "priips_kid_status", "exchange", "exchange_ticker",
    "trading_currency", "pricing_symbol", "latest_close_date", "latest_close", "pricing_source",
    "pricing_fetch_timestamp", "pricing_freshness_status", "ter_pct", "replication_method",
    "distribution_policy", "hedged_unhedged_status", "liquidity_spread_status", "candidate_thesis",
    "candidate_invalidation", "decision_status",
]


def _assert_file(path: Path) -> None:
    if not path.exists():
        raise AssertionError(f"missing file: {path}")


def _assert_false(data: dict, key: str) -> None:
    if data.get(key) is not False:
        raise AssertionError(f"expected false for {key}")


def validate() -> dict[str, str]:
    for path in [CONTRACT, RUNNER, ARTIFACT, PREVIEW, NOTES, REGISTRY]:
        _assert_file(path)

    contract_text = CONTRACT.read_text(encoding="utf-8")
    for field in REQUIRED_CONTRACT_FIELDS:
        if field not in contract_text:
            raise AssertionError(f"contract missing field: {field}")
    for marker in ["registry evidence", "pricing evidence", "fund facts evidence", "liquidity/spread evidence", "decision evidence", "rendered output evidence"]:
        if marker not in contract_text:
            raise AssertionError(f"contract missing evidence class: {marker}")

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
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
    }
    for key, value in expected.items():
        if data.get(key) != value:
            raise AssertionError(f"unexpected {key}: {data.get(key)!r}")

    if data.get("limited_pricing_poc_performed") is not True:
        raise AssertionError("limited_pricing_poc_performed must be true")
    for key in [
        "valuation_grade", "pricing_evidence_for_client_grade", "pricing_evidence_for_delivery_preflight",
        "production_delivery", "portfolio_mutation", "candidate_promotion", "funding_authority",
        "client_grade_claim", "client_grade_enough_for_delivery_preflight_discussion", "delivery_ready",
        "delivery_preflight_allowed", "receipt_artifact_created", "production_manifest_created",
        "source_pdf_replaced", "renderer_changed", "fake_price_used", "us_proxy_price_used",
    ]:
        _assert_false(data, key)

    status = data.get("provider_status")
    if status not in {"success", "failed"}:
        raise AssertionError("provider_status must be success or failed")
    if status == "success":
        if not data.get("latest_close_date"):
            raise AssertionError("success requires latest_close_date")
        if not isinstance(data.get("latest_close"), (int, float)):
            raise AssertionError("success requires numeric latest_close")
        if not data.get("pricing_source") or not data.get("pricing_fetch_timestamp") or not data.get("pricing_freshness_status"):
            raise AssertionError("success requires source/timestamp/freshness")
    else:
        if data.get("latest_close") is not None:
            raise AssertionError("failed provider result must not contain latest_close")
        if not data.get("provider_error"):
            raise AssertionError("failed provider result must explain provider_error")
        if data.get("pricing_poc_status") != "failed_provider_or_symbol_unavailable":
            raise AssertionError("failed result must use explicit failure status")

    preview = PREVIEW.read_text(encoding="utf-8")
    for marker in ["# ETF EU Closing Price POC", "SXR8.DE", "IE00B5BMR087", "limited proof-of-concept"]:
        if marker not in preview:
            raise AssertionError(f"preview missing marker: {marker}")

    if not data.get("selected_next_package"):
        raise AssertionError("selected_next_package missing")
    return {"status": "valid", "provider_status": status, "selected_next_package": data["selected_next_package"]}


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
