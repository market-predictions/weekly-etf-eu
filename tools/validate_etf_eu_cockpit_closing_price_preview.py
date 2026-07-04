from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SOURCE = Path("output/client_surface/etf_eu_closing_price_poc_20260703_000000.json")
REPAIR = Path("output/client_surface/etf_eu_closing_price_poc_provider_repair_20260703_000000.json")
MARKDOWN = Path("output/client_surface/etf_eu_cockpit_closing_price_preview_20260703_000000.md")
ARTIFACT = Path("output/client_surface/etf_eu_cockpit_closing_price_preview_20260703_000000.json")
PDF = Path("output/client_surface/etf_eu_cockpit_closing_price_preview_20260703_000000.pdf")

REQUIRED_FALSE = [
    "valuation_grade",
    "pricing_evidence_for_client_grade",
    "pricing_evidence_for_delivery_preflight",
    "production_delivery",
    "portfolio_mutation",
    "candidate_promotion",
    "funding_authority",
    "client_grade_claim",
    "delivery_ready",
    "delivery_preflight_allowed",
    "receipt_artifact_created",
    "production_manifest_created",
    "fake_price_used",
    "us_proxy_price_used",
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate() -> dict[str, Any]:
    for path in [SOURCE, REPAIR, MARKDOWN, ARTIFACT]:
        _require(path.exists(), f"missing file: {path}")
    data = _load(ARTIFACT)
    source = _load(SOURCE)
    _load(REPAIR)

    expected = {
        "work_package_id": "ETF-EU-WP15Z",
        "source_work_package": "ETF-EU-WP15Y-FIX",
        "symbol": "SXR8.DE",
        "isin": "IE00B5BMR087",
        "latest_close_date": "2026-07-03",
        "latest_close": 706.119995,
        "pricing_source": "yahoo_chart_v8",
        "provider_status": "success",
        "pricing_poc_status": "success_non_valuation_grade_close_obtained",
        "selected_next_package": "ETF-EU-WP15AA",
    }
    for key, value in expected.items():
        _require(data.get(key) == value, f"unexpected {key}: {data.get(key)!r}")

    _require(data.get("preview_surface_created") is True, "preview_surface_created must be true")
    _require(data.get("review_only") is True, "review_only must be true")
    _require(data.get("pdf_created") is False, "pdf_created must be false for committed connector artifact")
    _require(source.get("latest_close") == data.get("latest_close"), "source close mismatch")
    _require(source.get("latest_close_date") == data.get("latest_close_date"), "source close date mismatch")

    for key in REQUIRED_FALSE:
        _require(data.get(key) is False, f"expected false for {key}")

    if data.get("pdf_created") is True:
        _require(PDF.exists(), "pdf_created=true but PDF missing")

    text = MARKDOWN.read_text(encoding="utf-8")
    for marker in [
        "# ETF EU Cockpit - Closing Price Preview",
        "Eerste koers-POC",
        "IE00B5BMR087",
        "SXR8.DE",
        "2026-07-03",
        "706.119995",
        "yahoo_chart_v8",
        "Dit is een beperkte koers-POC",
    ]:
        _require(marker in text, f"preview missing marker: {marker}")

    return {
        "status": "valid",
        "work_package_id": data["work_package_id"],
        "symbol": data["symbol"],
        "latest_close_date": data["latest_close_date"],
        "latest_close": data["latest_close"],
        "pdf_created": data["pdf_created"],
        "selected_next_package": data["selected_next_package"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
