from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SOURCE_PRODUCT_FACTS = Path("output/client_surface/etf_eu_product_facts_evidence_20260703_000000.json")
SOURCE_PRODUCT_FACTS_NOTES = Path("output/client_surface/etf_eu_product_facts_evidence_notes_20260703_000000.md")
SOURCE_PLAN = Path("output/client_surface/etf_eu_cockpit_pdf_client_grade_evidence_acquisition_plan_20260703_000000.json")
SOURCE_GAP_AUDIT = Path("output/client_surface/etf_eu_cockpit_pdf_client_grade_evidence_gap_audit_20260703_000000.json")
SOURCE_READINESS_GATE = Path("output/client_surface/etf_eu_cockpit_pdf_client_grade_readiness_gate_v2_20260703_000000.json")
SOURCE_CLOSEOUT = Path("output/client_surface/etf_eu_cockpit_pdf_visual_review_closeout_20260703_000000.json")
SOURCE_PDF_ARTIFACT = Path("output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.json")
SOURCE_PDF = Path("output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.pdf")
PRICING_POLICY = Path("control/ETF_EU_PRICING_FRESHNESS_POLICY_V1.md")
VALUATION_POLICY = Path("control/ETF_EU_VALUATION_RECONCILIATION_POLICY_V1.md")
POLICY_ARTIFACT = Path("output/client_surface/etf_eu_pricing_freshness_valuation_policy_20260703_000000.json")
NOTES = Path("output/client_surface/etf_eu_pricing_freshness_valuation_policy_notes_20260703_000000.md")

REQUIRED_FRESHNESS_CATEGORIES = {
    "current_completed_session",
    "one_trading_day_lag",
    "stale_but_reviewable",
    "stale_blocking",
    "unpriced_or_pending_verification",
}

REQUIRED_RECONCILIATION_RULES = {
    "isin_first_identity_required",
    "same_isin_lines_may_map_to_same_fund",
    "trading_currency_must_remain_line_level",
    "no_fx_conversion_without_authorized_fx_policy",
    "no_portfolio_valuation_without_valuation_grade_authority",
    "skipped_lines_cannot_be_inferred_from_related_lines",
    "review_only_prices_do_not_authorize_delivery",
}

REQUIRED_RESOLVED_POLICY_GAPS = {
    "price_freshness_policy",
    "valuation_reconciliation_policy",
}

REQUIRED_REMAINING_CLIENT_GRADE_BLOCKERS = {
    "investment_thesis_for_proposed_funded_positions",
    "invalidation_criteria_for_proposed_funded_positions",
    "funding_decision_or_cash_posture",
    "PRIIPs_KID_availability_evidence",
    "liquidity_spread_evidence",
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

PRICING_POLICY_MARKERS = [
    "# ETF EU pricing freshness policy v1",
    "## Purpose",
    "## Scope",
    "## Authority boundary",
    "## Freshness categories",
    "## Completed-session rule",
    "## Weekend and exchange-holiday handling",
    "## Multi-line close-date handling",
    "## Stale-price handling",
    "## Review-only interpretation",
    "## Client-grade limitation",
    "## Delivery-preflight limitation",
    "## Non-authorized actions",
    "## Required future evidence before client-grade",
    "## Validation requirements",
]

VALUATION_POLICY_MARKERS = [
    "# ETF EU valuation reconciliation policy v1",
    "## Purpose",
    "## Scope",
    "## Authority boundary",
    "## ISIN-first reconciliation principle",
    "## Trading-line reconciliation",
    "## Currency-aware interpretation",
    "## Same-fund line mapping",
    "## Close-date mismatch handling",
    "## Price-source mismatch handling",
    "## Review-only valuation posture",
    "## Why this is not valuation-grade",
    "## Client-grade limitation",
    "## Delivery-preflight limitation",
    "## Non-authorized actions",
    "## Required future evidence before valuation-grade or client-grade",
    "## Validation requirements",
]

NOTE_MARKERS = [
    "# ETF-EU-WP15AH pricing freshness and valuation reconciliation policy",
    "## Scope",
    "## Source artifacts",
    "## Policy documents",
    "## Pricing freshness policy",
    "## Valuation reconciliation policy",
    "## Current line classifications",
    "## Resolved policy gaps",
    "## Remaining client-grade blockers",
    "## Remaining delivery-preflight blockers",
    "## Boundary checks",
    "## Decision",
    "## Next package",
]

VALID_AUTHORITY_LEVELS = {
    "internal_artifact",
    "internal_policy",
    "official_issuer",
    "official_exchange",
    "official_regulatory",
    "secondary_cross_check",
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _require_markers(text: str, markers: list[str], label: str) -> None:
    for marker in markers:
        _require(marker in text, f"{label} missing marker: {marker}")


def _require_false_flags(data: dict[str, Any]) -> None:
    for key in REQUIRED_FALSE:
        _require(data.get(key) is False, f"expected false for {key}")


def validate() -> dict[str, Any]:
    required_paths = [
        SOURCE_PRODUCT_FACTS,
        SOURCE_PRODUCT_FACTS_NOTES,
        SOURCE_PLAN,
        SOURCE_GAP_AUDIT,
        SOURCE_READINESS_GATE,
        SOURCE_CLOSEOUT,
        SOURCE_PDF_ARTIFACT,
        SOURCE_PDF,
        PRICING_POLICY,
        VALUATION_POLICY,
        POLICY_ARTIFACT,
        NOTES,
    ]
    for path in required_paths:
        _require(path.exists(), f"missing file: {path}")

    product_facts = _load(SOURCE_PRODUCT_FACTS)
    plan = _load(SOURCE_PLAN)
    gap_audit = _load(SOURCE_GAP_AUDIT)
    readiness = _load(SOURCE_READINESS_GATE)
    closeout = _load(SOURCE_CLOSEOUT)
    pdf_artifact = _load(SOURCE_PDF_ARTIFACT)
    data = _load(POLICY_ARTIFACT)

    pricing_policy_text = PRICING_POLICY.read_text(encoding="utf-8")
    valuation_policy_text = VALUATION_POLICY.read_text(encoding="utf-8")
    notes_text = NOTES.read_text(encoding="utf-8")

    _require(product_facts.get("work_package_id") == "ETF-EU-WP15AG", "source product facts mismatch")
    _require(plan.get("work_package_id") == "ETF-EU-WP15AF", "source acquisition plan mismatch")
    _require(gap_audit.get("work_package_id") == "ETF-EU-WP15AE", "source gap audit mismatch")
    _require(readiness.get("work_package_id") == "ETF-EU-WP15AD", "source readiness gate mismatch")
    _require(closeout.get("work_package_id") == "ETF-EU-WP15AC", "source closeout mismatch")
    _require(pdf_artifact.get("work_package_id") == "ETF-EU-WP15AB", "source PDF artifact mismatch")

    _require(data.get("work_package_id") == "ETF-EU-WP15AH", "wrong work package")
    _require(data.get("source_work_package") == "ETF-EU-WP15AG", "wrong source work package")
    _require(data.get("source_product_facts_artifact") == str(SOURCE_PRODUCT_FACTS), "source product facts path mismatch")
    _require(data.get("source_product_facts_notes") == str(SOURCE_PRODUCT_FACTS_NOTES), "source product facts notes path mismatch")
    _require(data.get("source_acquisition_plan_artifact") == str(SOURCE_PLAN), "source plan path mismatch")
    _require(data.get("source_gap_audit_artifact") == str(SOURCE_GAP_AUDIT), "source gap audit path mismatch")
    _require(data.get("source_readiness_gate_artifact") == str(SOURCE_READINESS_GATE), "source readiness gate path mismatch")
    _require(data.get("source_review_only_pdf") == str(SOURCE_PDF), "source PDF path mismatch")
    _require(data.get("pricing_freshness_policy_path") == str(PRICING_POLICY), "pricing policy path mismatch")
    _require(data.get("valuation_reconciliation_policy_path") == str(VALUATION_POLICY), "valuation policy path mismatch")

    _require(data.get("pricing_freshness_policy_created") is True, "pricing freshness policy not created")
    _require(data.get("valuation_reconciliation_policy_created") is True, "valuation reconciliation policy not created")
    _require(data.get("pricing_freshness_policy_validated") is True, "pricing freshness policy not validated")
    _require(data.get("valuation_reconciliation_policy_validated") is True, "valuation reconciliation policy not validated")
    _require(data.get("readiness_gate_status") == "pricing_and_valuation_policy_defined_not_client_grade", "wrong readiness gate status")
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
    _require(data.get("first_successful_freshness_policy_status") == "current_completed_session", "SXR8 freshness mismatch")

    _require(data.get("second_successful_symbol") == "CSPX.L", "CSPX symbol mismatch")
    _require(data.get("second_successful_close_date") == "2026-07-03", "CSPX date mismatch")
    _require(data.get("second_successful_close") == 807.859985, "CSPX close mismatch")
    _require(data.get("second_successful_freshness_policy_status") == "current_completed_session", "CSPX freshness mismatch")

    _require(data.get("smh_status") == "skipped_pending_registry_status", "SMH status mismatch")
    _require(data.get("smh_freshness_policy_status") == "unpriced_or_pending_verification", "SMH freshness mismatch")

    categories = set(data.get("pricing_freshness_categories", []))
    _require(REQUIRED_FRESHNESS_CATEGORIES.issubset(categories), "missing pricing freshness categories")

    rules = set(data.get("valuation_reconciliation_rules", []))
    _require(REQUIRED_RECONCILIATION_RULES.issubset(rules), "missing valuation reconciliation rules")

    resolved = set(data.get("resolved_policy_gaps", []))
    _require(resolved == REQUIRED_RESOLVED_POLICY_GAPS, "resolved policy gaps mismatch")

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
        _require(source["authority_level"] in VALID_AUTHORITY_LEVELS, f"invalid authority level: {source['authority_level']}")

    internal_policy_refs = {
        source.get("source_reference")
        for source in source_manifest
        if source.get("authority_level") == "internal_policy"
    }
    _require(str(PRICING_POLICY) in internal_policy_refs, "pricing internal_policy source missing")
    _require(str(VALUATION_POLICY) in internal_policy_refs, "valuation internal_policy source missing")

    _require_false_flags(data)
    _require(data.get("selected_next_package") == "ETF-EU-WP15AI", "wrong next package")

    _require_markers(pricing_policy_text, PRICING_POLICY_MARKERS, "pricing policy")
    _require_markers(valuation_policy_text, VALUATION_POLICY_MARKERS, "valuation policy")
    _require_markers(notes_text, NOTE_MARKERS, "notes")

    for category in REQUIRED_FRESHNESS_CATEGORIES:
        _require(category in pricing_policy_text, f"pricing policy missing category: {category}")
    for rule in REQUIRED_RECONCILIATION_RULES:
        _require(rule in valuation_policy_text or rule in json.dumps(data), f"valuation rule missing: {rule}")

    return {
        "status": "valid",
        "work_package_id": data["work_package_id"],
        "readiness_gate_status": data["readiness_gate_status"],
        "pricing_freshness_policy_created": data["pricing_freshness_policy_created"],
        "valuation_reconciliation_policy_created": data["valuation_reconciliation_policy_created"],
        "pricing_freshness_policy_validated": data["pricing_freshness_policy_validated"],
        "valuation_reconciliation_policy_validated": data["valuation_reconciliation_policy_validated"],
        "resolved_policy_gaps_count": len(data["resolved_policy_gaps"]),
        "remaining_client_grade_blockers_count": len(data["remaining_client_grade_blockers"]),
        "remaining_delivery_preflight_blockers_count": len(data["remaining_delivery_preflight_blockers"]),
        "client_grade_claim": data["client_grade_claim"],
        "delivery_preflight_allowed": data["delivery_preflight_allowed"],
        "valuation_grade": data["valuation_grade"],
        "selected_next_package": data["selected_next_package"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
