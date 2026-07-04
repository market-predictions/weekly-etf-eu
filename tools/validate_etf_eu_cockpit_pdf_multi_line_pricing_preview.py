from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SOURCE_PRICING = Path("output/client_surface/etf_eu_multi_line_pricing_preview_20260703_000000.json")
SOURCE_PREVIEW = Path("output/client_surface/etf_eu_cockpit_multi_line_pricing_preview_20260703_000000.json")
SOURCE_REPAIR = Path("output/client_surface/etf_eu_multi_line_pricing_universe_repair_20260703_000000.json")
ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.json")
NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_visual_review_20260703_000000.md")
PDF = Path("output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.pdf")
RENDERER = Path("runtime/build_etf_eu_cockpit_pdf_multi_line_pricing_preview.py")

EXPECTED_PDF = "output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.pdf"
OLD_PDFS = {
    "output/client_surface/etf_eu_cockpit_pdf_premium_dutch_refinement_candidate_20260703_000000.pdf",
    "output/client_surface/etf_eu_cockpit_closing_price_preview_20260703_000000.pdf",
    "output/client_surface/etf_eu_cockpit_multi_line_pricing_preview_20260703_000000.pdf",
}
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
    for path in [SOURCE_PRICING, SOURCE_PREVIEW, SOURCE_REPAIR, ARTIFACT, NOTES, RENDERER]:
        _require(path.exists(), f"missing file: {path}")

    artifact = _load(ARTIFACT)
    source = _load(SOURCE_PREVIEW)
    repair = _load(SOURCE_REPAIR)

    _require(artifact.get("work_package_id") == "ETF-EU-WP15AB", "wrong work package")
    _require(artifact.get("source_work_package") == "ETF-EU-WP15AA-FIX", "wrong source package")
    _require(artifact.get("pdf_preview_path") == EXPECTED_PDF, "unexpected PDF path")
    _require(artifact.get("pdf_preview_path") not in OLD_PDFS, "PDF path reuses prior candidate")
    _require(artifact.get("pdf_created") is True, "pdf_created must be true")
    _require(PDF.exists(), "PDF file is missing")
    _require(PDF.stat().st_size > 1000, "PDF file is unexpectedly small")
    _require(artifact.get("pdf_page_count") == 4, "expected 4 PDF pages")
    _require(artifact.get("successful_rows_count") == 2, "expected two successful rows")
    _require(artifact.get("failed_rows_count") == 0, "expected zero failed rows")
    _require(artifact.get("skipped_rows_count") == 1, "expected one skipped row")
    _require(artifact.get("mandatory_sxr8_success") is True, "SXR8 flag missing")
    _require(artifact.get("at_least_one_additional_verified_eu_line_success") is True, "second line flag missing")
    _require(artifact.get("first_successful_symbol") == "SXR8.DE", "first symbol mismatch")
    _require(artifact.get("first_successful_close_date") == "2026-07-03", "SXR8 date mismatch")
    _require(artifact.get("first_successful_close") == 706.119995, "SXR8 close mismatch")
    _require(artifact.get("second_successful_symbol") == "CSPX.L", "second symbol mismatch")
    _require(artifact.get("second_successful_close_date") == "2026-07-03", "CSPX date mismatch")
    _require(artifact.get("second_successful_close") == 807.859985, "CSPX close mismatch")
    _require(artifact.get("pricing_source") == "yahoo_chart_v8", "pricing source mismatch")
    _require(source.get("successful_rows_count") == 2, "source row count mismatch")
    _require(repair.get("repair_status") == "success", "repair artifact is not success")
    for key in REQUIRED_FALSE:
        _require(artifact.get(key) is False, f"expected false for {key}")

    notes = NOTES.read_text(encoding="utf-8")
    for marker in ["accepted_for_review_only_continuation", "SXR8.DE", "CSPX.L", "SMH"]:
        _require(marker in notes, f"notes missing marker: {marker}")

    return {
        "status": "valid",
        "work_package_id": "ETF-EU-WP15AB",
        "pdf_created": artifact["pdf_created"],
        "pdf_page_count": artifact["pdf_page_count"],
        "selected_next_package": artifact["selected_next_package"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
