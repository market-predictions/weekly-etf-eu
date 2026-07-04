from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SOURCE = Path("output/client_surface/etf_eu_cockpit_closing_price_preview_20260703_000000.json")
PRICING = Path("output/client_surface/etf_eu_multi_line_pricing_preview_20260703_000000.json")
PREVIEW = Path("output/client_surface/etf_eu_cockpit_multi_line_pricing_preview_20260703_000000.json")
MARKDOWN = Path("output/client_surface/etf_eu_cockpit_multi_line_pricing_preview_20260703_000000.md")
REPAIR = Path("output/client_surface/etf_eu_multi_line_pricing_universe_repair_20260703_000000.json")
PDF = Path("output/client_surface/etf_eu_cockpit_multi_line_pricing_preview_20260703_000000.pdf")

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
US_PROXY_SYMBOLS = {"SPY", "QQQ", "GLD", "SMH", "PAVE"}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _row(rows: list[dict[str, Any]], symbol: str) -> dict[str, Any]:
    for row in rows:
        if row.get("pricing_symbol") == symbol:
            return row
    raise AssertionError(f"missing row: {symbol}")


def validate() -> dict[str, Any]:
    for path in [SOURCE, PRICING, PREVIEW, MARKDOWN, REPAIR]:
        _require(path.exists(), f"missing file: {path}")
    pricing = _load(PRICING)
    preview = _load(PREVIEW)
    repair = _load(REPAIR)
    source = _load(SOURCE)

    for data in [pricing, preview]:
        _require(data.get("work_package_id") == "ETF-EU-WP15AA-FIX", "wrong work package")
        _require(data.get("source_work_package") == "ETF-EU-WP15AA", "wrong source package")
        _require(data.get("pricing_rows"), "pricing_rows must be non-empty")
        _require(data.get("successful_rows_count") >= 2, "expected at least two successful rows")
        _require(data.get("skipped_rows_count") == 1, "expected one skipped row")
        _require(data.get("selected_next_package") == "ETF-EU-WP15AB", "unexpected next package")
        _require(data.get("at_least_one_additional_verified_eu_line_success") is True, "second line success flag missing")
        for key in REQUIRED_FALSE:
            _require(data.get(key) is False, f"expected false for {key}")
        if data.get("pdf_created") is True:
            _require(PDF.exists(), "pdf_created=true but PDF is missing")

    _require(repair.get("repair_status") == "success", "repair must be success")
    _require(repair.get("successful_second_line_symbol") == "CSPX.L", "second line must be CSPX.L")
    _require(repair.get("successful_second_line_close") == 807.859985, "CSPX repair close mismatch")
    _require(repair.get("selected_next_package") == "ETF-EU-WP15AB", "repair next package mismatch")

    sxr8 = _row(preview["pricing_rows"], "SXR8.DE")
    _require(sxr8["isin"] == "IE00B5BMR087", "SXR8 ISIN mismatch")
    _require(sxr8["latest_close_date"] == "2026-07-03", "SXR8 close date mismatch")
    _require(sxr8["latest_close"] == 706.119995, "SXR8 close mismatch")
    _require(sxr8["pricing_source"] == "yahoo_chart_v8", "SXR8 source mismatch")
    _require(sxr8["provider_status"] == "success", "SXR8 provider status mismatch")
    _require(source["latest_close"] == sxr8["latest_close"], "source close mismatch")

    cspx = _row(preview["pricing_rows"], "CSPX.L")
    _require(cspx["isin"] == "IE00B5BMR087", "CSPX ISIN mismatch")
    _require(cspx["latest_close_date"] == "2026-07-03", "CSPX close date mismatch")
    _require(cspx["latest_close"] == 807.859985, "CSPX close mismatch")
    _require(cspx["pricing_source"] == "yahoo_chart_v8", "CSPX source mismatch")
    _require(cspx["provider_status"] == "success", "CSPX provider status mismatch")

    for row in preview["pricing_rows"]:
        if row.get("pricing_symbol") in US_PROXY_SYMBOLS:
            _require(row.get("line_status") != "success", "US proxy symbol must not be success")
        if row.get("line_status") != "success":
            _require(row.get("latest_close") is None, "skipped/failed row must not contain close")

    text = MARKDOWN.read_text(encoding="utf-8")
    for marker in ["SXR8.DE", "CSPX.L", "706.119995", "807.859985", "2026-07-03", "yahoo_chart_v8", "beperkte multi-line koerspreview"]:
        _require(marker in text, f"markdown missing marker: {marker}")

    return {
        "status": "valid",
        "work_package_id": "ETF-EU-WP15AA-FIX",
        "successful_rows_count": preview["successful_rows_count"],
        "skipped_rows_count": preview["skipped_rows_count"],
        "selected_next_package": preview["selected_next_package"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
