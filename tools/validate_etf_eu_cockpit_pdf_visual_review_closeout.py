from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PDF = Path("output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.pdf")
PDF_ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.json")
PDF_NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_visual_review_20260703_000000.md")
CLOSEOUT = Path("output/client_surface/etf_eu_cockpit_pdf_visual_review_closeout_20260703_000000.json")
CLOSEOUT_NOTES = Path("output/client_surface/etf_eu_cockpit_pdf_visual_review_closeout_20260703_000000.md")

ALLOWED_DECISIONS = {
    "accepted_for_review_only_foundation",
    "accepted_with_minor_visual_notes",
    "rejected_needs_pdf_render_fix",
    "blocked_pdf_missing_or_unreadable",
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
REQUIRED_NOTE_MARKERS = [
    "title visible",
    "review-only status visible",
    "two successful rows visible",
    "SXR8.DE close visible and correct",
    "CSPX.L close visible and correct",
    "SMH pending/skipped visible",
    "boundary caveat visible",
    "no U.S. proxy price shown as investable",
    "no funding or portfolio mutation implied",
    "no delivery-ready claim",
    "PDF path is separate from prior candidates",
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate() -> dict[str, Any]:
    for path in [PDF, PDF_ARTIFACT, PDF_NOTES, CLOSEOUT, CLOSEOUT_NOTES]:
        _require(path.exists(), f"missing file: {path}")

    pdf_artifact = _load(PDF_ARTIFACT)
    closeout = _load(CLOSEOUT)
    notes = CLOSEOUT_NOTES.read_text(encoding="utf-8")

    _require(closeout.get("work_package_id") == "ETF-EU-WP15AC", "wrong work package")
    _require(closeout.get("source_work_package") == "ETF-EU-WP15AB", "wrong source package")
    _require(closeout.get("visual_review_performed") is True, "visual review not performed")
    _require(closeout.get("visual_decision") in ALLOWED_DECISIONS, "invalid visual decision")
    _require(closeout.get("pdf_exists") is True, "pdf_exists must be true")
    _require(closeout.get("pdf_page_count") == 4, "pdf page count mismatch")
    _require(pdf_artifact.get("pdf_created") is True, "WP15AB pdf_created mismatch")
    _require(pdf_artifact.get("pdf_page_count") == 4, "WP15AB page count mismatch")
    _require(closeout.get("successful_rows_count") == 2, "successful row count mismatch")
    _require(closeout.get("failed_rows_count") == 0, "failed row count mismatch")
    _require(closeout.get("skipped_rows_count") == 1, "skipped row count mismatch")
    _require(closeout.get("first_successful_symbol") == "SXR8.DE", "SXR8 symbol mismatch")
    _require(closeout.get("first_successful_close_date") == "2026-07-03", "SXR8 date mismatch")
    _require(closeout.get("first_successful_close") == 706.119995, "SXR8 close mismatch")
    _require(closeout.get("second_successful_symbol") == "CSPX.L", "CSPX symbol mismatch")
    _require(closeout.get("second_successful_close_date") == "2026-07-03", "CSPX date mismatch")
    _require(closeout.get("second_successful_close") == 807.859985, "CSPX close mismatch")
    _require(closeout.get("smh_status") == "skipped_pending_registry_status", "SMH status mismatch")
    _require(closeout.get("review_only") is True, "review_only must be true")
    for key in REQUIRED_FALSE:
        _require(closeout.get(key) is False, f"expected false for {key}")

    if closeout.get("visual_decision") in {"accepted_for_review_only_foundation", "accepted_with_minor_visual_notes"}:
        _require(closeout.get("accepted_for_review_only_foundation") is True, "accepted flag mismatch")
        _require(closeout.get("selected_next_package") == "ETF-EU-WP15AD", "accepted closeout must select WP15AD")
    else:
        _require(closeout.get("accepted_for_review_only_foundation") is False, "rejected flag mismatch")
        _require(closeout.get("selected_next_package") == "ETF-EU-WP15AC-FIX", "rejected closeout must select WP15AC-FIX")

    for marker in REQUIRED_NOTE_MARKERS:
        _require(marker in notes, f"closeout notes missing marker: {marker}")

    return {
        "status": "valid",
        "work_package_id": "ETF-EU-WP15AC",
        "visual_decision": closeout["visual_decision"],
        "accepted_for_review_only_foundation": closeout["accepted_for_review_only_foundation"],
        "selected_next_package": closeout["selected_next_package"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
