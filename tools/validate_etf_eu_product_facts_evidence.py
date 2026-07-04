from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SOURCE_PLAN = Path("output/client_surface/etf_eu_cockpit_pdf_client_grade_evidence_acquisition_plan_20260703_000000.json")
SOURCE_GAP_AUDIT = Path("output/client_surface/etf_eu_cockpit_pdf_client_grade_evidence_gap_audit_20260703_000000.json")
SOURCE_CLOSEOUT = Path("output/client_surface/etf_eu_cockpit_pdf_visual_review_closeout_20260703_000000.json")
SOURCE_PDF_ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.json")
SOURCE_PDF = Path("output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.pdf")
PRODUCT_FACTS = Path("output/client_surface/etf_eu_product_facts_evidence_20260703_000000.json")
NOTES = Path("output/client_surface/etf_eu_product_facts_evidence_notes_20260703_000000.md")

REQUIRED_PRODUCT_GAPS = {
    "TER_or_ongoing_charge_evidence",
    "replication_method_evidence",
    "distribution_policy_evidence",
    "hedged_unhedged_status_evidence",
}

REQUIRED_REMAINING_CLIENT_GRADE_BLOCKERS = {
    "investment_thesis_for_proposed_funded_positions",
    "invalidation_criteria_for_proposed_funded_positions",
    "funding_decision_or_cash_posture",
    "PRIIPs_KID_availability_evidence",
    "liquidity_spread_evidence",
    "price_freshness_policy",
    "valuation_reconciliation_policy",
    "client_language_quality_gate",
}

REQUIRED_REMAINING_DELIVERY_BLOCKERS = {
    "all_client_grade_gates_passed",
    "delivery_receipt_or_manifest_contract",
    "recipient_configuration_authority",
    "SMTP_secret_authority",
    "production_delivery_manifest_path",
    "outbound_runbook",
    "post_send_verification_loop",
    "rollback_or_abort_policy",
}

REQUIRED_FALSE = [
    "client_grade_claim",
    "client_grade_enough_for_delivery_preflight_discussion",
    "delivery_ready",
    "delivery_preflight_allowed",
    "outbound_path_enabled",
    "production_delivery",
    "portfolio_mutation",
    "candidate_promotion",
    "funding_authority",
    "valuation_grade",
    "pricing_evidence_for_client_grade",
    "pricing_evidence_for_delivery_preflight",
    "receipt_artifact_created",
    "production_manifest_created",
    "recipient_config_changed",
    "smtp_or_secret_config_changed",
    "fake_price_used",
    "us_proxy_price_used",
    "live_price_fetch_performed",
    "live_data_fetch_performed",
    "pricing_evidence_changed",
    "recommendation_logic_changed",
    "source_pdf_replaced",
    "new_pdf_created",
    "renderer_changed",
]

FUND_FACT_FIELDS_WITH_SOURCE = [
    "TER_or_ongoing_charge",
    "replication_method",
    "distribution_policy",
    "hedged_unhedged_status",
]

NOTE_MARKERS = [
    "# ETF-EU-WP15AG product facts evidence",
    "## Scope",
    "## Source artifacts",
    "## Source manifest",
    "## Fund-level evidence",
    "## Trading-line evidence",
    "## Resolved product-fact gaps",
    "## Remaining client-grade blockers",
    "## Remaining delivery-preflight blockers",
    "## Boundary checks",
    "## Decision",
    "## Next package",
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _require_false_flags(data: dict[str, Any]) -> None:
    for key in REQUIRED_FALSE:
        _require(data.get(key) is False, f"expected false for {key}")


def validate() -> dict[str, Any]:
    for path in [SOURCE_PLAN, SOURCE_GAP_AUDIT, SOURCE_CLOSEOUT, SOURCE_PDF_ARTIFACT, SOURCE_PDF, PRODUCT_FACTS, NOTES]:
        _require(path.exists(), f"missing file: {path}")

    source_plan = _load(SOURCE_PLAN)
    source_gap_audit = _load(SOURCE_GAP_AUDIT)
    source_closeout = _load(SOURCE_CLOSEOUT)
    source_pdf_artifact = _load(SOURCE_PDF_ARTIFACT)
    data = _load(PRODUCT_FACTS)
    notes = NOTES.read_text(encoding="utf-8")

    _require(source_plan.get("work_package_id") == "ETF-EU-WP15AF", "source WP15AF acquisition plan mismatch")
    _require(source_gap_audit.get("work_package_id") == "ETF-EU-WP15AE", "source WP15AE gap audit mismatch")
    _require(source_closeout.get("work_package_id") == "ETF-EU-WP15AC", "source WP15AC closeout mismatch")
    _require(source_pdf_artifact.get("work_package_id") == "ETF-EU-WP15AB", "source WP15AB PDF artifact mismatch")

    _require(data.get("work_package_id") == "ETF-EU-WP15AG", "wrong work package")
    _require(data.get("source_work_package") == "ETF-EU-WP15AF", "wrong source work package")
    _require(data.get("source_acquisition_plan_artifact") == str(SOURCE_PLAN), "source plan path mismatch")
    _require(data.get("source_gap_audit_artifact") == str(SOURCE_GAP_AUDIT), "source gap audit path mismatch")
    _require(data.get("source_review_only_pdf") == str(SOURCE_PDF), "source PDF path mismatch")

    _require(data.get("product_facts_evidence_acquired") is True, "product facts evidence not acquired")
    _require(data.get("product_facts_evidence_validated") is True, "product facts evidence not validated")
    _require(data.get("readiness_gate_status") == "product_facts_acquired_not_client_grade", "wrong readiness gate status")
    _require(data.get("accepted_review_only_foundation") is True, "review-only foundation not accepted")
    _require(data.get("delivery_authorization_decision") == "remain_blocked", "delivery authorization must remain blocked")
    _require(data.get("review_only") is True, "review_only must be true")

    _require(data.get("pdf_exists") is True, "pdf_exists must be true")
    _require(data.get("pdf_page_count") == 4, "PDF page count mismatch")
    _require(data.get("successful_rows_count") == 2, "successful rows mismatch")
    _require(data.get("failed_rows_count") == 0, "failed rows mismatch")
    _require(data.get("skipped_rows_count") == 1, "skipped rows mismatch")
    _require(data.get("first_successful_symbol") == "SXR8.DE", "SXR8 symbol mismatch")
    _require(data.get("first_successful_close_date") == "2026-07-03", "SXR8 date mismatch")
    _require(data.get("first_successful_close") == 706.119995, "SXR8 close mismatch")
    _require(data.get("second_successful_symbol") == "CSPX.L", "CSPX symbol mismatch")
    _require(data.get("second_successful_close_date") == "2026-07-03", "CSPX date mismatch")
    _require(data.get("second_successful_close") == 807.859985, "CSPX close mismatch")
    _require(data.get("smh_status") == "skipped_pending_registry_status", "SMH status mismatch")

    fund = data.get("fund_product_facts")
    _require(isinstance(fund, dict) and fund, "fund_product_facts missing")
    _require(fund.get("isin") == "IE00B5BMR087", "fund ISIN mismatch")
    _require(bool(fund.get("fund_name")), "fund name missing")
    _require(bool(fund.get("issuer")), "issuer missing")

    confidence = fund.get("field_confidence")
    _require(isinstance(confidence, dict) and confidence, "field confidence missing")
    for field in FUND_FACT_FIELDS_WITH_SOURCE:
        _require(bool(fund.get(field)), f"{field} missing")
        _require(bool(fund.get(f"{field}_source")), f"{field} source missing")
        _require(bool(fund.get(f"{field}_source_date")), f"{field} source date missing")
        _require(confidence.get(field) in {"confirmed", "needs_cross_check", "not_found", "not_applicable"}, f"{field} confidence invalid")

    trading_lines = data.get("trading_line_facts")
    _require(isinstance(trading_lines, list) and trading_lines, "trading_line_facts missing")
    by_symbol = {line.get("symbol"): line for line in trading_lines}
    for symbol in ["SXR8.DE", "CSPX.L"]:
        _require(symbol in by_symbol, f"{symbol} missing")
        line = by_symbol[symbol]
        _require(line.get("isin") == "IE00B5BMR087", f"{symbol} ISIN mismatch")
        _require(line.get("maps_to_same_fund") is True, f"{symbol} does not map to same fund")
        _require(bool(line.get("line_identity_source")), f"{symbol} line source missing")
        _require(bool(line.get("line_identity_source_date")), f"{symbol} line source date missing")

    resolved = set(data.get("resolved_product_fact_gaps", []))
    _require(resolved == REQUIRED_PRODUCT_GAPS, "resolved product fact gaps mismatch")

    client_blockers = set(data.get("remaining_client_grade_blockers", []))
    _require(client_blockers, "remaining client-grade blockers empty")
    _require(REQUIRED_REMAINING_CLIENT_GRADE_BLOCKERS.issubset(client_blockers), "remaining client-grade blockers missing required items")

    delivery_blockers = set(data.get("remaining_delivery_preflight_blockers", []))
    _require(delivery_blockers, "remaining delivery-preflight blockers empty")
    _require(REQUIRED_REMAINING_DELIVERY_BLOCKERS.issubset(delivery_blockers), "remaining delivery-preflight blockers missing required items")

    source_manifest = data.get("source_manifest")
    _require(isinstance(source_manifest, list) and source_manifest, "source manifest missing")
    required_source_fields = {
        "source_id",
        "source_type",
        "source_title",
        "source_reference",
        "retrieval_timestamp",
        "authority_level",
        "used_for_fields",
    }
    for source in source_manifest:
        for field in required_source_fields:
            _require(field in source and source[field], f"source manifest missing {field}")
        _require(source["authority_level"] in {"official_issuer", "official_exchange", "official_regulatory", "internal_artifact", "secondary_cross_check"}, f"invalid authority level: {source['authority_level']}")
    _require(any(source.get("authority_level") == "official_issuer" for source in source_manifest), "official issuer source missing")

    _require_false_flags(data)
    _require(data.get("selected_next_package") == "ETF-EU-WP15AH", "wrong next package")

    for marker in NOTE_MARKERS:
        _require(marker in notes, f"notes missing marker: {marker}")

    return {
        "status": "valid",
        "work_package_id": data["work_package_id"],
        "readiness_gate_status": data["readiness_gate_status"],
        "product_facts_evidence_acquired": data["product_facts_evidence_acquired"],
        "product_facts_evidence_validated": data["product_facts_evidence_validated"],
        "resolved_product_fact_gaps_count": len(data["resolved_product_fact_gaps"]),
        "remaining_client_grade_blockers_count": len(data["remaining_client_grade_blockers"]),
        "remaining_delivery_preflight_blockers_count": len(data["remaining_delivery_preflight_blockers"]),
        "client_grade_claim": data["client_grade_claim"],
        "delivery_preflight_allowed": data["delivery_preflight_allowed"],
        "selected_next_package": data["selected_next_package"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
