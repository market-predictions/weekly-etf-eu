from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SOURCE_DECISION = Path("output/client_surface/etf_eu_investment_thesis_invalidation_funding_posture_framework_20260703_000000.json")
SOURCE_INVESTABILITY = Path("output/client_surface/etf_eu_priips_kid_liquidity_spread_evidence_20260703_000000.json")
SOURCE_POLICY = Path("output/client_surface/etf_eu_pricing_freshness_valuation_policy_20260703_000000.json")
SOURCE_PRODUCT_FACTS = Path("output/client_surface/etf_eu_product_facts_evidence_20260703_000000.json")
SOURCE_PRICING = Path("output/client_surface/etf_eu_multi_line_pricing_preview_20260703_000000.json")
SOURCE_REGISTRY = Path("config/ucits_symbol_registry.yml")
SOURCE_PDF = Path("output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.pdf")
LANGUAGE_POLICY = Path("control/ETF_EU_CLIENT_LANGUAGE_QUALITY_GATE_V1.md")
ARTIFACT = Path("output/client_surface/etf_eu_client_language_quality_readiness_synthesis_20260703_000000.json")
NOTES = Path("output/client_surface/etf_eu_client_language_quality_readiness_synthesis_notes_20260703_000000.md")

REQUIRED_GATE_FIELDS = {
    "gate_status",
    "dutch_first_required",
    "review_only_disclosure_status",
    "source_authority_wording_status",
    "residual_blocker_disclosure_status",
    "transaction_language_status",
    "funding_language_status",
    "delivery_language_status",
    "valuation_language_status",
    "allowed_client_surface_terms",
    "prohibited_client_surface_terms",
    "client_grade_limitation",
    "delivery_preflight_limitation",
}

REQUIRED_SYNTHESIS_FIELDS = {
    "review_only_readiness_status",
    "client_grade_status",
    "delivery_preflight_status",
    "production_delivery_status",
    "funding_status",
    "valuation_status",
    "portfolio_status",
    "resolved_gates",
    "remaining_gates",
    "final_authority_position",
    "next_required_package",
}

REQUIRED_RESOLVED_GATES = {
    "product_facts_evidence",
    "pricing_freshness_policy",
    "valuation_reconciliation_policy",
    "PRIIPs_KID_availability_evidence",
    "liquidity_spread_evidence",
    "investment_thesis_framework",
    "invalidation_criteria_framework",
    "funding_posture_framework",
    "client_language_quality_gate",
}

REQUIRED_DELIVERY_BLOCKERS = {
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
    "client_grade_authority_created",
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

VALID_SOURCE_TYPES = {
    "internal_artifact",
    "internal_policy",
    "decision_framework",
    "language_quality_policy",
    "readiness_synthesis",
}
VALID_AUTHORITY_LEVELS = VALID_SOURCE_TYPES

POLICY_MARKERS = [
    "# ETF EU client language quality gate v1",
    "## Purpose",
    "## Scope",
    "## Authority boundary",
    "## Dutch-first client-language standard",
    "## Review-only disclosure requirements",
    "## Source-authority wording requirements",
    "## Residual blocker disclosure requirements",
    "## Prohibited client-facing wording",
    "## Readiness synthesis rules",
    "## Client-grade limitation",
    "## Delivery-preflight limitation",
    "## Validation requirements",
]

NOTE_MARKERS = [
    "# ETF-EU-WP15AK client language quality gate and readiness synthesis",
    "## Scope",
    "## Source artifacts",
    "## Language quality policy",
    "## Client-language quality gate",
    "## Readiness synthesis",
    "## Resolved client-language gaps",
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
    for path in [SOURCE_DECISION, SOURCE_INVESTABILITY, SOURCE_POLICY, SOURCE_PRODUCT_FACTS, SOURCE_PRICING, SOURCE_REGISTRY, SOURCE_PDF, LANGUAGE_POLICY, ARTIFACT, NOTES]:
        _require(path.exists(), f"missing file: {path}")

    decision = _load(SOURCE_DECISION)
    investability = _load(SOURCE_INVESTABILITY)
    policy = _load(SOURCE_POLICY)
    product_facts = _load(SOURCE_PRODUCT_FACTS)
    data = _load(ARTIFACT)
    policy_text = LANGUAGE_POLICY.read_text(encoding="utf-8")
    notes_text = NOTES.read_text(encoding="utf-8")

    _require(decision.get("work_package_id") == "ETF-EU-WP15AJ", "source decision mismatch")
    _require(investability.get("work_package_id") == "ETF-EU-WP15AI", "source investability mismatch")
    _require(policy.get("work_package_id") == "ETF-EU-WP15AH", "source policy mismatch")
    _require(product_facts.get("work_package_id") == "ETF-EU-WP15AG", "source product facts mismatch")

    _require(data.get("work_package_id") == "ETF-EU-WP15AK", "wrong work package")
    _require(data.get("source_work_package") == "ETF-EU-WP15AJ", "wrong source work package")
    _require(data.get("source_decision_framework_artifact") == str(SOURCE_DECISION), "decision artifact path mismatch")
    _require(data.get("source_investability_evidence_artifact") == str(SOURCE_INVESTABILITY), "investability path mismatch")
    _require(data.get("source_policy_artifact") == str(SOURCE_POLICY), "policy path mismatch")
    _require(data.get("source_product_facts_artifact") == str(SOURCE_PRODUCT_FACTS), "product facts path mismatch")
    _require(data.get("source_pricing_artifact") == str(SOURCE_PRICING), "pricing path mismatch")
    _require(data.get("source_registry") == str(SOURCE_REGISTRY), "registry path mismatch")
    _require(data.get("source_review_only_pdf") == str(SOURCE_PDF), "PDF path mismatch")
    _require(data.get("language_quality_policy_path") == str(LANGUAGE_POLICY), "language policy path mismatch")

    for key in [
        "client_language_quality_gate_created",
        "client_language_quality_gate_validated",
        "source_authority_wording_validated",
        "residual_blocker_disclosure_validated",
        "readiness_synthesis_created",
        "readiness_synthesis_validated",
        "client_language_quality_gate_passed",
        "accepted_review_only_foundation",
        "review_only",
    ]:
        _require(data.get(key) is True, f"expected true for {key}")

    _require(data.get("readiness_gate_status") == "client_language_gate_passed_not_delivery_ready", "wrong readiness gate status")
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

    gate = data.get("client_language_quality_gate")
    _require(isinstance(gate, dict), "client language quality gate missing")
    _require_fields(gate, REQUIRED_GATE_FIELDS, "client language quality gate")
    _require(gate["gate_status"] == "passed_review_only_language_gate", "gate status mismatch")
    _require(gate["dutch_first_required"] is True, "Dutch-first requirement mismatch")
    _require(gate["review_only_disclosure_status"] == "passed", "review-only disclosure mismatch")
    _require(gate["source_authority_wording_status"] == "passed", "source-authority wording mismatch")
    _require(gate["residual_blocker_disclosure_status"] == "passed", "residual blocker disclosure mismatch")
    for key in ["transaction_language_status", "funding_language_status", "delivery_language_status", "valuation_language_status"]:
        _require(gate[key] == "blocked", f"{key} must be blocked")

    synthesis = data.get("readiness_synthesis")
    _require(isinstance(synthesis, dict), "readiness synthesis missing")
    _require_fields(synthesis, REQUIRED_SYNTHESIS_FIELDS, "readiness synthesis")
    _require(synthesis["review_only_readiness_status"] == "review_only_language_gate_passed", "review-only readiness mismatch")
    _require(synthesis["client_grade_status"] == "not_authorized", "client grade status mismatch")
    _require(synthesis["delivery_preflight_status"] == "blocked", "delivery-preflight status mismatch")
    _require(synthesis["production_delivery_status"] == "blocked", "production delivery status mismatch")
    _require(synthesis["funding_status"] == "not_authorized", "funding status mismatch")
    _require(synthesis["valuation_status"] == "not_authorized", "valuation status mismatch")
    _require(synthesis["portfolio_status"] == "no_mutation", "portfolio status mismatch")
    _require(set(synthesis["resolved_gates"]) == REQUIRED_RESOLVED_GATES, "resolved gates mismatch")
    _require(REQUIRED_DELIVERY_BLOCKERS.issubset(set(synthesis["remaining_gates"])), "remaining gates missing delivery blockers")
    _require(synthesis["final_authority_position"] == "review_only_not_delivery_ready", "final authority position mismatch")
    _require(synthesis["next_required_package"] == "ETF-EU-WP15AL", "next required package mismatch")

    _require(data.get("resolved_client_language_gaps") == ["client_language_quality_gate"], "resolved client language gaps mismatch")
    _require(data.get("remaining_client_grade_blockers") == [], "remaining client grade blockers must be empty")
    _require(REQUIRED_DELIVERY_BLOCKERS.issubset(set(data.get("remaining_delivery_preflight_blockers", []))), "delivery blockers missing")

    manifest = data.get("source_manifest")
    _require(isinstance(manifest, list) and manifest, "source manifest missing")
    used_fields = " ".join(" ".join(source.get("used_for_fields", [])) for source in manifest)
    for required in ["client language quality gate", "source-authority wording", "residual blocker disclosure", "readiness synthesis"]:
        _require(required in used_fields, f"source support missing: {required}")
    for source in manifest:
        _require(source.get("source_type") in VALID_SOURCE_TYPES, "invalid source type")
        _require(source.get("authority_level") in VALID_AUTHORITY_LEVELS, "invalid authority level")
        _require(source.get("source_reference"), "source reference missing")

    _require_false_flags(data)
    _require(data.get("selected_next_package") in {"ETF-EU-WP15AL", "ETF-EU-WP15AK-FIX"}, "invalid next package")

    # Prohibited terms are allowed only inside the explicit prohibited_client_surface_terms list or policy section.
    allowed_terms = set(gate.get("allowed_client_surface_terms", []))
    prohibited_terms = set(gate.get("prohibited_client_surface_terms", []))
    _require("onder beoordeling" in allowed_terms, "allowed Dutch term missing")
    _require("koopadvies" in prohibited_terms, "prohibited Dutch term missing")
    _require("klaar voor verzending" in prohibited_terms, "prohibited delivery term missing")

    for marker in POLICY_MARKERS:
        _require(marker in policy_text, f"policy missing marker: {marker}")
    for marker in NOTE_MARKERS:
        _require(marker in notes_text, f"notes missing marker: {marker}")

    return {
        "status": "valid",
        "work_package_id": data["work_package_id"],
        "readiness_gate_status": data["readiness_gate_status"],
        "client_language_quality_gate_created": data["client_language_quality_gate_created"],
        "client_language_quality_gate_validated": data["client_language_quality_gate_validated"],
        "source_authority_wording_validated": data["source_authority_wording_validated"],
        "residual_blocker_disclosure_validated": data["residual_blocker_disclosure_validated"],
        "readiness_synthesis_created": data["readiness_synthesis_created"],
        "readiness_synthesis_validated": data["readiness_synthesis_validated"],
        "client_language_quality_gate_passed": data["client_language_quality_gate_passed"],
        "resolved_client_language_gaps_count": len(data["resolved_client_language_gaps"]),
        "remaining_client_grade_blockers_count": len(data["remaining_client_grade_blockers"]),
        "remaining_delivery_preflight_blockers_count": len(data["remaining_delivery_preflight_blockers"]),
        "client_grade_claim": data["client_grade_claim"],
        "client_grade_authority_created": data["client_grade_authority_created"],
        "delivery_preflight_allowed": data["delivery_preflight_allowed"],
        "valuation_grade": data["valuation_grade"],
        "funding_authority": data["funding_authority"],
        "portfolio_mutation": data["portfolio_mutation"],
        "selected_next_package": data["selected_next_package"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
