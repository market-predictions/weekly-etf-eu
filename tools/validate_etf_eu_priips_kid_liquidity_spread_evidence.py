from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SOURCE_POLICY_ARTIFACT = Path("output/client_surface/etf_eu_pricing_freshness_valuation_policy_20260703_000000.json")
SOURCE_PRODUCT_FACTS = Path("output/client_surface/etf_eu_product_facts_evidence_20260703_000000.json")
SOURCE_PRICING_ARTIFACT = Path("output/client_surface/etf_eu_multi_line_pricing_preview_20260703_000000.json")
SOURCE_REGISTRY = Path("config/ucits_symbol_registry.yml")
SOURCE_PDF = Path("output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.pdf")
EVIDENCE_ARTIFACT = Path("output/client_surface/etf_eu_priips_kid_liquidity_spread_evidence_20260703_000000.json")
NOTES = Path("output/client_surface/etf_eu_priips_kid_liquidity_spread_evidence_notes_20260703_000000.md")

REQUIRED_FUND_FIELDS = {
    "isin",
    "fund_name",
    "issuer",
    "priips_kid_status",
    "priips_kid_document_available",
    "priips_kid_source_reference",
    "priips_kid_source_title",
    "priips_kid_source_type",
    "priips_kid_source_date_or_retrieval_timestamp",
    "priips_kid_language_or_locale_if_available",
    "priips_kid_authority_level",
    "priips_kid_confidence",
    "review_only_interpretation",
    "client_grade_limitation",
}

REQUIRED_LINE_FIELDS = {
    "symbol",
    "isin",
    "exchange",
    "trading_currency",
    "line_status",
    "freshness_policy_status",
    "liquidity_evidence_status",
    "spread_evidence_status",
    "liquidity_source_reference",
    "spread_source_reference",
    "liquidity_source_title",
    "spread_source_title",
    "liquidity_source_type",
    "spread_source_type",
    "liquidity_source_date_or_retrieval_timestamp",
    "spread_source_date_or_retrieval_timestamp",
    "liquidity_authority_level",
    "spread_authority_level",
    "liquidity_confidence",
    "spread_confidence",
    "review_only_liquidity_interpretation",
    "review_only_spread_interpretation",
    "client_grade_limitation",
    "valuation_grade_limitation",
}

REQUIRED_RESOLVED_INVESTABILITY_GAPS = {
    "PRIIPs_KID_availability_evidence",
    "liquidity_spread_evidence",
}

REQUIRED_REMAINING_CLIENT_GRADE_BLOCKERS = {
    "investment_thesis_for_proposed_funded_positions",
    "invalidation_criteria_for_proposed_funded_positions",
    "funding_decision_or_cash_posture",
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

VALID_SOURCE_TYPES = {
    "official_issuer_page",
    "official_issuer_document",
    "official_exchange_page",
    "official_regulatory_page",
    "internal_artifact",
    "secondary_cross_check",
}

VALID_AUTHORITY_LEVELS = {
    "official_issuer",
    "official_exchange",
    "official_regulatory",
    "internal_artifact",
    "secondary_cross_check",
}

VALID_EVIDENCE_STATUSES = {"available", "not_found", "needs_cross_check", "not_applicable"}
VALID_CONFIDENCE_VALUES = {"confirmed", "needs_cross_check", "not_found", "not_applicable"}

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

NOTE_MARKERS = [
    "# ETF-EU-WP15AI PRIIPs/KID and liquidity/spread investability evidence",
    "## Scope",
    "## Source artifacts",
    "## Source manifest",
    "## Fund-level PRIIPs/KID evidence",
    "## Line-level liquidity/spread evidence",
    "## Resolved investability gaps",
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


def _require_fields(obj: dict[str, Any], fields: set[str], label: str) -> None:
    for field in fields:
        _require(field in obj, f"{label} missing field: {field}")
        _require(obj[field] not in (None, "", []), f"{label} empty field: {field}")


def validate() -> dict[str, Any]:
    for path in [
        SOURCE_POLICY_ARTIFACT,
        SOURCE_PRODUCT_FACTS,
        SOURCE_PRICING_ARTIFACT,
        SOURCE_REGISTRY,
        SOURCE_PDF,
        EVIDENCE_ARTIFACT,
        NOTES,
    ]:
        _require(path.exists(), f"missing file: {path}")

    policy_artifact = _load(SOURCE_POLICY_ARTIFACT)
    product_facts = _load(SOURCE_PRODUCT_FACTS)
    data = _load(EVIDENCE_ARTIFACT)
    notes = NOTES.read_text(encoding="utf-8")

    _require(policy_artifact.get("work_package_id") == "ETF-EU-WP15AH", "source policy artifact mismatch")
    _require(product_facts.get("work_package_id") == "ETF-EU-WP15AG", "source product facts mismatch")

    _require(data.get("work_package_id") == "ETF-EU-WP15AI", "wrong work package")
    _require(data.get("source_work_package") == "ETF-EU-WP15AH", "wrong source work package")
    _require(data.get("source_policy_artifact") == str(SOURCE_POLICY_ARTIFACT), "source policy artifact path mismatch")
    _require(data.get("source_product_facts_artifact") == str(SOURCE_PRODUCT_FACTS), "source product facts path mismatch")
    _require(data.get("source_pricing_artifact") == str(SOURCE_PRICING_ARTIFACT), "source pricing artifact path mismatch")
    _require(data.get("source_registry") == str(SOURCE_REGISTRY), "source registry path mismatch")
    _require(data.get("source_review_only_pdf") == str(SOURCE_PDF), "source PDF path mismatch")

    _require(data.get("priips_kid_evidence_acquired") is True, "PRIIPs/KID evidence not acquired")
    _require(data.get("liquidity_spread_evidence_acquired") is True, "liquidity/spread evidence not acquired")
    _require(data.get("investability_evidence_validated") is True, "investability evidence not validated")
    _require(data.get("readiness_gate_status") == "investability_evidence_acquired_not_client_grade", "wrong readiness gate status")
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

    fund = data.get("fund_level_priips_kid_evidence")
    _require(isinstance(fund, dict), "fund-level PRIIPs/KID evidence must be an object")
    _require_fields(fund, REQUIRED_FUND_FIELDS, "fund-level PRIIPs/KID evidence")
    _require(fund["isin"] == "IE00B5BMR087", "fund ISIN mismatch")
    _require(fund["fund_name"] == "iShares Core S&P 500 UCITS ETF USD (Acc)", "fund name mismatch")
    _require(fund["issuer"] == "iShares / BlackRock", "issuer mismatch")
    _require(fund["priips_kid_status"] in {"available", "not_found", "needs_cross_check"}, "invalid PRIIPs/KID status")
    _require(isinstance(fund["priips_kid_document_available"], bool), "PRIIPs/KID availability must be boolean")
    _require(fund["priips_kid_authority_level"] in VALID_AUTHORITY_LEVELS, "invalid PRIIPs/KID authority level")
    _require(fund["priips_kid_confidence"] in {"confirmed", "needs_cross_check", "not_found"}, "invalid PRIIPs/KID confidence")

    lines = data.get("line_level_liquidity_spread_evidence")
    _require(isinstance(lines, list) and lines, "line-level liquidity/spread evidence missing")
    by_symbol = {line.get("symbol"): line for line in lines}
    _require("SXR8.DE" in by_symbol, "SXR8.DE line evidence missing")
    _require("CSPX.L" in by_symbol, "CSPX.L line evidence missing")
    _require("SMH" not in by_symbol, "SMH must not have funded/valuation line evidence")

    expected_lines = {
        "SXR8.DE": ("Xetra", "EUR"),
        "CSPX.L": ("London Stock Exchange", "USD"),
    }
    for symbol, (exchange, currency) in expected_lines.items():
        line = by_symbol[symbol]
        _require_fields(line, REQUIRED_LINE_FIELDS, f"{symbol} line evidence")
        _require(line["isin"] == "IE00B5BMR087", f"{symbol} ISIN mismatch")
        _require(line["exchange"] == exchange, f"{symbol} exchange mismatch")
        _require(line["trading_currency"] == currency, f"{symbol} currency mismatch")
        _require(line["line_status"] == "success", f"{symbol} line status mismatch")
        _require(line["freshness_policy_status"] == "current_completed_session", f"{symbol} freshness mismatch")
        _require(line["liquidity_evidence_status"] in VALID_EVIDENCE_STATUSES, f"{symbol} invalid liquidity status")
        _require(line["spread_evidence_status"] in VALID_EVIDENCE_STATUSES, f"{symbol} invalid spread status")
        _require(line["liquidity_authority_level"] in VALID_AUTHORITY_LEVELS, f"{symbol} invalid liquidity authority")
        _require(line["spread_authority_level"] in VALID_AUTHORITY_LEVELS, f"{symbol} invalid spread authority")
        _require(line["liquidity_confidence"] in VALID_CONFIDENCE_VALUES, f"{symbol} invalid liquidity confidence")
        _require(line["spread_confidence"] in VALID_CONFIDENCE_VALUES, f"{symbol} invalid spread confidence")

    resolved = set(data.get("resolved_investability_gaps", []))
    _require(resolved == REQUIRED_RESOLVED_INVESTABILITY_GAPS, "resolved investability gaps mismatch")

    client_blockers = set(data.get("remaining_client_grade_blockers", []))
    _require(client_blockers, "remaining client-grade blockers empty")
    _require(REQUIRED_REMAINING_CLIENT_GRADE_BLOCKERS.issubset(client_blockers), "remaining client-grade blockers missing required items")

    delivery_blockers = set(data.get("remaining_delivery_preflight_blockers", []))
    _require(delivery_blockers, "remaining delivery-preflight blockers empty")
    _require(REQUIRED_REMAINING_DELIVERY_BLOCKERS.issubset(delivery_blockers), "remaining delivery-preflight blockers missing required items")

    manifest = data.get("source_manifest")
    _require(isinstance(manifest, list) and manifest, "source manifest missing")
    required_source_fields = {
        "source_id",
        "source_type",
        "source_title",
        "source_reference",
        "retrieval_timestamp",
        "authority_level",
        "used_for_fields",
    }
    for source in manifest:
        for field in required_source_fields:
            _require(field in source and source[field], f"source manifest missing {field}")
        _require(source["source_type"] in VALID_SOURCE_TYPES, f"invalid source type: {source['source_type']}")
        _require(source["authority_level"] in VALID_AUTHORITY_LEVELS, f"invalid authority level: {source['authority_level']}")

    used_fields = " ".join(" ".join(source.get("used_for_fields", [])) for source in manifest)
    _require("PRIIPs" in used_fields or "KID" in used_fields, "no source supports PRIIPs/KID evidence")
    _require("SXR8.DE" in used_fields or "SXR8" in used_fields, "no source supports SXR8 evidence")
    _require("CSPX.L" in used_fields or "CSPX" in used_fields, "no source supports CSPX evidence")

    _require_false_flags(data)
    _require(data.get("selected_next_package") in {"ETF-EU-WP15AJ", "ETF-EU-WP15AI-FIX"}, "invalid next package")

    for marker in NOTE_MARKERS:
        _require(marker in notes, f"notes missing marker: {marker}")

    return {
        "status": "valid",
        "work_package_id": data["work_package_id"],
        "readiness_gate_status": data["readiness_gate_status"],
        "priips_kid_evidence_acquired": data["priips_kid_evidence_acquired"],
        "liquidity_spread_evidence_acquired": data["liquidity_spread_evidence_acquired"],
        "investability_evidence_validated": data["investability_evidence_validated"],
        "resolved_investability_gaps_count": len(data["resolved_investability_gaps"]),
        "remaining_client_grade_blockers_count": len(data["remaining_client_grade_blockers"]),
        "remaining_delivery_preflight_blockers_count": len(data["remaining_delivery_preflight_blockers"]),
        "client_grade_claim": data["client_grade_claim"],
        "delivery_preflight_allowed": data["delivery_preflight_allowed"],
        "valuation_grade": data["valuation_grade"],
        "selected_next_package": data["selected_next_package"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
