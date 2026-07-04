from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SOURCE_LANGUAGE = Path("output/client_surface/etf_eu_client_language_quality_readiness_synthesis_20260703_000000.json")
SOURCE_DECISION = Path("output/client_surface/etf_eu_investment_thesis_invalidation_funding_posture_framework_20260703_000000.json")
SOURCE_INVESTABILITY = Path("output/client_surface/etf_eu_priips_kid_liquidity_spread_evidence_20260703_000000.json")
SOURCE_POLICY = Path("output/client_surface/etf_eu_pricing_freshness_valuation_policy_20260703_000000.json")
SOURCE_PRODUCT_FACTS = Path("output/client_surface/etf_eu_product_facts_evidence_20260703_000000.json")
SOURCE_PRICING = Path("output/client_surface/etf_eu_multi_line_pricing_preview_20260703_000000.json")
SOURCE_REGISTRY = Path("config/ucits_symbol_registry.yml")
SOURCE_PDF = Path("output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.pdf")
POLICY = Path("control/ETF_EU_CLIENT_GRADE_AUTHORITY_DECISION_POLICY_V1.md")
ARTIFACT = Path("output/client_surface/etf_eu_client_grade_authority_decision_20260703_000000.json")
NOTES = Path("output/client_surface/etf_eu_client_grade_authority_decision_notes_20260703_000000.md")

REQUIRED_DECISION_FIELDS = {
    "decision_status",
    "decision_result",
    "decision_reason",
    "client_grade_authority_created",
    "client_grade_claim",
    "client_grade_scope",
    "delivery_scope",
    "valuation_scope",
    "funding_scope",
    "portfolio_scope",
    "required_next_package",
}

REQUIRED_EVIDENCE_FIELDS = {
    "product_facts_evidence",
    "pricing_freshness_policy",
    "valuation_reconciliation_policy",
    "PRIIPs_KID_availability_evidence",
    "liquidity_spread_evidence",
    "investment_thesis_framework",
    "invalidation_criteria_framework",
    "funding_posture_framework",
    "client_language_quality_gate",
    "overall_evidence_chain_status",
}

REQUIRED_SOURCE_AUTHORITY_FIELDS = {
    "source_manifest_present",
    "source_references_traceable",
    "issuer_reference_present",
    "registry_reference_present",
    "pricing_artifact_present",
    "authority_limitations_disclosed",
    "overall_source_authority_status",
}

REQUIRED_LANGUAGE_FIELDS = {
    "dutch_first_gate_passed",
    "review_only_disclosure_present",
    "source_authority_wording_present",
    "residual_delivery_blocker_disclosure_present",
    "prohibited_transaction_language_blocked",
    "overall_client_language_status",
}

REQUIRED_PRICING_FIELDS = {
    "pricing_evidence_for_client_grade",
    "pricing_evidence_for_delivery_preflight",
    "latest_close_dates_fixed",
    "fake_price_used",
    "us_proxy_price_used",
    "live_price_fetch_performed",
    "pricing_evidence_changed",
    "overall_pricing_evidence_status",
}

REQUIRED_DELIVERY_BLOCKERS = {
    "delivery_receipt_or_manifest_contract",
    "recipient_configuration_authority",
    "SMTP_secret_authority",
    "production_delivery_manifest_path",
    "outbound_runbook",
    "post_send_verification_loop",
    "rollback_or_abort_policy",
}

REQUIRED_FALSE = [
    "delivery_ready",
    "delivery_preflight_allowed",
    "outbound_path_enabled",
    "production_delivery",
    "portfolio_mutation",
    "candidate_promotion",
    "funding_authority",
    "valuation_grade",
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

VALID_SOURCE_TYPES = {
    "internal_artifact",
    "internal_policy",
    "decision_framework",
    "language_quality_policy",
    "authority_decision_policy",
    "authority_decision",
}
VALID_AUTHORITY_LEVELS = VALID_SOURCE_TYPES

POLICY_MARKERS = [
    "# ETF EU client-grade authority decision policy v1",
    "## Purpose",
    "## Scope",
    "## Authority boundary",
    "## Evidence-chain sufficiency requirements",
    "## Source-authority sufficiency requirements",
    "## Pricing evidence limitation",
    "## Valuation-grade limitation",
    "## Funding limitation",
    "## Portfolio mutation limitation",
    "## Delivery-preflight limitation",
    "## Positive authority decision rule",
    "## Negative authority decision rule",
    "## Validation requirements",
]

NOTE_MARKERS = [
    "# ETF-EU-WP15AL client-grade authority decision",
    "## Scope",
    "## Source artifacts",
    "## Client-grade authority policy",
    "## Authority decision",
    "## Evidence-chain sufficiency",
    "## Source-authority sufficiency",
    "## Client-language sufficiency",
    "## Pricing evidence sufficiency",
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


def _require_fields(obj: dict[str, Any], fields: set[str], label: str) -> None:
    for field in fields:
        _require(field in obj, f"{label} missing field: {field}")
        _require(obj[field] not in (None, "", []), f"{label} empty field: {field}")


def _require_false_flags(data: dict[str, Any]) -> None:
    for key in REQUIRED_FALSE:
        _require(data.get(key) is False, f"expected false for {key}")


def validate() -> dict[str, Any]:
    for path in [SOURCE_LANGUAGE, SOURCE_DECISION, SOURCE_INVESTABILITY, SOURCE_POLICY, SOURCE_PRODUCT_FACTS, SOURCE_PRICING, SOURCE_REGISTRY, SOURCE_PDF, POLICY, ARTIFACT, NOTES]:
        _require(path.exists(), f"missing file: {path}")

    language = _load(SOURCE_LANGUAGE)
    decision_source = _load(SOURCE_DECISION)
    investability = _load(SOURCE_INVESTABILITY)
    policy_source = _load(SOURCE_POLICY)
    product_facts = _load(SOURCE_PRODUCT_FACTS)
    data = _load(ARTIFACT)
    policy_text = POLICY.read_text(encoding="utf-8")
    notes_text = NOTES.read_text(encoding="utf-8")

    _require(language.get("work_package_id") == "ETF-EU-WP15AK", "source language mismatch")
    _require(decision_source.get("work_package_id") == "ETF-EU-WP15AJ", "source decision mismatch")
    _require(investability.get("work_package_id") == "ETF-EU-WP15AI", "source investability mismatch")
    _require(policy_source.get("work_package_id") == "ETF-EU-WP15AH", "source policy mismatch")
    _require(product_facts.get("work_package_id") == "ETF-EU-WP15AG", "source product facts mismatch")

    _require(data.get("work_package_id") == "ETF-EU-WP15AL", "wrong work package")
    _require(data.get("source_work_package") == "ETF-EU-WP15AK", "wrong source work package")
    _require(data.get("source_language_quality_artifact") == str(SOURCE_LANGUAGE), "language artifact path mismatch")
    _require(data.get("source_decision_framework_artifact") == str(SOURCE_DECISION), "decision artifact path mismatch")
    _require(data.get("source_investability_evidence_artifact") == str(SOURCE_INVESTABILITY), "investability path mismatch")
    _require(data.get("source_policy_artifact") == str(SOURCE_POLICY), "policy path mismatch")
    _require(data.get("source_product_facts_artifact") == str(SOURCE_PRODUCT_FACTS), "product facts path mismatch")
    _require(data.get("source_pricing_artifact") == str(SOURCE_PRICING), "pricing path mismatch")
    _require(data.get("source_registry") == str(SOURCE_REGISTRY), "registry path mismatch")
    _require(data.get("source_review_only_pdf") == str(SOURCE_PDF), "PDF path mismatch")
    _require(data.get("client_grade_authority_policy_path") == str(POLICY), "policy path mismatch")

    _require(data.get("client_grade_authority_decision_created") is True, "authority decision not created")
    _require(data.get("client_grade_authority_decision_validated") is True, "authority decision not validated")
    _require(data.get("accepted_review_only_foundation") is True, "foundation not accepted")
    _require(data.get("client_language_quality_gate_passed") is True, "language gate not passed")
    _require(data.get("delivery_authorization_decision") == "remain_blocked", "delivery authorization must remain blocked")

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

    decision = data.get("client_grade_authority_decision")
    _require(isinstance(decision, dict), "authority decision missing")
    _require_fields(decision, REQUIRED_DECISION_FIELDS, "authority decision")

    evidence = data.get("evidence_chain_sufficiency")
    _require(isinstance(evidence, dict), "evidence chain sufficiency missing")
    _require_fields(evidence, REQUIRED_EVIDENCE_FIELDS, "evidence chain sufficiency")

    source_authority = data.get("source_authority_sufficiency")
    _require(isinstance(source_authority, dict), "source authority sufficiency missing")
    _require_fields(source_authority, REQUIRED_SOURCE_AUTHORITY_FIELDS, "source authority sufficiency")

    language_sufficiency = data.get("client_language_sufficiency")
    _require(isinstance(language_sufficiency, dict), "client language sufficiency missing")
    _require_fields(language_sufficiency, REQUIRED_LANGUAGE_FIELDS, "client language sufficiency")

    pricing = data.get("pricing_evidence_sufficiency")
    _require(isinstance(pricing, dict), "pricing evidence sufficiency missing")
    _require_fields(pricing, REQUIRED_PRICING_FIELDS, "pricing evidence sufficiency")

    positive = data.get("client_grade_authority_created") is True
    if positive:
        _require(data.get("client_grade_claim") is True, "positive branch requires client_grade_claim=true")
        _require(data.get("client_grade_status") == "authorized_no_delivery", "positive client grade status mismatch")
        _require(data.get("client_grade_enough_for_delivery_preflight_discussion") is True, "positive branch delivery discussion flag mismatch")
        _require(data.get("readiness_gate_status") == "client_grade_authority_created_delivery_blocked", "positive readiness status mismatch")
        _require(data.get("review_only") is False, "positive branch review_only must be false")
        _require(data.get("pricing_evidence_for_client_grade") is True, "positive branch pricing evidence flag mismatch")
        _require(data.get("pricing_evidence_for_delivery_preflight") is False, "delivery pricing evidence must remain false")
        _require(data.get("remaining_client_grade_blockers") == [], "positive branch client grade blockers must be empty")
        _require("all_client_grade_gates_passed" not in data.get("remaining_delivery_preflight_blockers", []), "all_client_grade_gates_passed must be removed")
        _require(data.get("selected_next_package") == "ETF-EU-WP15AM", "positive next package mismatch")
        _require(decision["decision_result"] == "authorized_no_delivery", "positive decision result mismatch")
        _require(decision["client_grade_authority_created"] is True, "positive decision authority mismatch")
        _require(decision["client_grade_claim"] is True, "positive decision claim mismatch")
        _require(decision["required_next_package"] == "ETF-EU-WP15AM", "positive required next package mismatch")
    else:
        _require(data.get("client_grade_claim") is False, "negative branch requires client_grade_claim=false")
        _require(data.get("client_grade_status") == "not_authorized", "negative client grade status mismatch")
        _require(data.get("client_grade_enough_for_delivery_preflight_discussion") is False, "negative branch delivery discussion flag mismatch")
        _require(data.get("readiness_gate_status") == "client_grade_authority_not_created", "negative readiness status mismatch")
        _require(data.get("review_only") is True, "negative branch review_only must be true")
        _require(data.get("pricing_evidence_for_client_grade") is False, "negative branch pricing evidence flag mismatch")
        _require(data.get("remaining_client_grade_blockers"), "negative branch client grade blockers must be non-empty")
        _require("all_client_grade_gates_passed" in data.get("remaining_delivery_preflight_blockers", []), "negative branch all_client_grade_gates_passed missing")
        _require(data.get("selected_next_package") == "ETF-EU-WP15AL-FIX", "negative next package mismatch")

    _require(REQUIRED_DELIVERY_BLOCKERS.issubset(set(data.get("remaining_delivery_preflight_blockers", []))), "delivery blockers missing")

    manifest = data.get("source_manifest")
    _require(isinstance(manifest, list) and manifest, "source manifest missing")
    used_fields = " ".join(" ".join(source.get("used_for_fields", [])) for source in manifest)
    for required in ["client-grade authority decision", "evidence-chain sufficiency", "source-authority sufficiency", "client-language sufficiency", "pricing evidence sufficiency"]:
        _require(required in used_fields, f"source support missing: {required}")
    for source in manifest:
        _require(source.get("source_type") in VALID_SOURCE_TYPES, "invalid source type")
        _require(source.get("authority_level") in VALID_AUTHORITY_LEVELS, "invalid authority level")
        _require(source.get("source_reference"), "source reference missing")

    _require_false_flags(data)
    _require(data.get("selected_next_package") in {"ETF-EU-WP15AM", "ETF-EU-WP15AL-FIX"}, "invalid next package")

    for field, value in evidence.items():
        if field != "overall_evidence_chain_status":
            _require(value == "passed", f"evidence field not passed: {field}")
    _require(evidence["overall_evidence_chain_status"] == "passed", "overall evidence status mismatch")
    _require(source_authority["overall_source_authority_status"] == "passed", "source authority status mismatch")
    _require(language_sufficiency["overall_client_language_status"] == "passed", "client language status mismatch")
    _require(pricing["overall_pricing_evidence_status"] == "passed_for_client_grade_only", "pricing status mismatch")

    for marker in POLICY_MARKERS:
        _require(marker in policy_text, f"policy missing marker: {marker}")
    for marker in NOTE_MARKERS:
        _require(marker in notes_text, f"notes missing marker: {marker}")

    return {
        "status": "valid",
        "work_package_id": data["work_package_id"],
        "readiness_gate_status": data["readiness_gate_status"],
        "client_grade_authority_decision_created": data["client_grade_authority_decision_created"],
        "client_grade_authority_decision_validated": data["client_grade_authority_decision_validated"],
        "client_grade_authority_created": data["client_grade_authority_created"],
        "client_grade_claim": data["client_grade_claim"],
        "client_grade_status": data["client_grade_status"],
        "client_grade_enough_for_delivery_preflight_discussion": data["client_grade_enough_for_delivery_preflight_discussion"],
        "remaining_client_grade_blockers_count": len(data["remaining_client_grade_blockers"]),
        "remaining_delivery_preflight_blockers_count": len(data["remaining_delivery_preflight_blockers"]),
        "delivery_preflight_allowed": data["delivery_preflight_allowed"],
        "production_delivery": data["production_delivery"],
        "valuation_grade": data["valuation_grade"],
        "funding_authority": data["funding_authority"],
        "portfolio_mutation": data["portfolio_mutation"],
        "selected_next_package": data["selected_next_package"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
