from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SOURCE_CLIENT_GRADE = Path("output/client_surface/etf_eu_client_grade_authority_decision_20260703_000000.json")
SOURCE_LANGUAGE = Path("output/client_surface/etf_eu_client_language_quality_readiness_synthesis_20260703_000000.json")
SOURCE_DECISION = Path("output/client_surface/etf_eu_investment_thesis_invalidation_funding_posture_framework_20260703_000000.json")
SOURCE_INVESTABILITY = Path("output/client_surface/etf_eu_priips_kid_liquidity_spread_evidence_20260703_000000.json")
SOURCE_POLICY = Path("output/client_surface/etf_eu_pricing_freshness_valuation_policy_20260703_000000.json")
SOURCE_PRODUCT_FACTS = Path("output/client_surface/etf_eu_product_facts_evidence_20260703_000000.json")
SOURCE_PRICING = Path("output/client_surface/etf_eu_multi_line_pricing_preview_20260703_000000.json")
SOURCE_REGISTRY = Path("config/ucits_symbol_registry.yml")
SOURCE_PDF = Path("output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.pdf")
CONTRACT = Path("control/ETF_EU_DELIVERY_PREFLIGHT_CONTRACT_V1.md")
RUNBOOK = Path("control/ETF_EU_OUTBOUND_RUNBOOK_V1.md")
VERIFY_POLICY = Path("control/ETF_EU_POST_SEND_VERIFICATION_AND_ROLLBACK_POLICY_V1.md")
ARTIFACT = Path("output/client_surface/etf_eu_delivery_preflight_contract_runbook_20260703_000000.json")
NOTES = Path("output/client_surface/etf_eu_delivery_preflight_contract_runbook_notes_20260703_000000.md")

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
    "recipient_authority_created",
    "transport_authority_created",
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

REQUIRED_CONTRACT_FIELDS = {
    "contract_status",
    "contract_scope",
    "delivery_preflight_allowed",
    "delivery_execution_allowed",
    "required_inputs_count",
    "required_authorities",
    "required_artifacts_count",
    "blocking_conditions",
    "next_required_package",
}
REQUIRED_MANIFEST_FIELDS = {
    "contract_status",
    "manifest_created",
    "manifest_path_created",
    "required_manifest_fields_count",
    "manifest_authority",
    "production_delivery_status",
}
REQUIRED_RECEIPT_FIELDS = {
    "contract_status",
    "receipt_created",
    "required_receipt_fields_count",
    "receipt_authority",
}
REQUIRED_RECIPIENT_GATE_FIELDS = {
    "gate_status",
    "recipient_config_changed",
    "recipient_authority_created",
    "required_future_authority",
    "blocking_status",
}
REQUIRED_TRANSPORT_GATE_FIELDS = {
    "gate_status",
    "smtp_or_secret_config_changed",
    "transport_authority_created",
    "required_future_authority",
    "blocking_status",
}
REQUIRED_RUNBOOK_FIELDS = {
    "runbook_status",
    "execution_allowed",
    "preflight_checklist_defined",
    "recipient_gate_defined",
    "transport_gate_defined",
    "manifest_gate_defined",
    "delivery_execution_gate_defined",
    "abort_conditions_defined",
}
REQUIRED_LOOP_FIELDS = {
    "loop_status",
    "verification_allowed",
    "receipt_required_before_success_claim",
    "delayed_confirmation_policy_defined",
    "success_claim_rule",
}
REQUIRED_ROLLBACK_FIELDS = {
    "policy_status",
    "abort_conditions_defined",
    "rollback_allowed",
    "failure_state",
}

RESOLVED_GAPS = {
    "delivery_receipt_or_manifest_contract",
    "production_delivery_manifest_path",
    "outbound_runbook",
    "post_send_verification_loop",
    "rollback_or_abort_policy",
}
REMAINING_BLOCKERS = {
    "recipient_configuration_authority",
    "transport_configuration_authority",
    "explicit_delivery_preflight_authority",
}
VALID_SOURCE_TYPES = {
    "internal_artifact",
    "internal_policy",
    "decision_framework",
    "authority_decision",
    "delivery_preflight_contract",
    "outbound_runbook",
    "verification_policy",
}
VALID_AUTHORITY_LEVELS = VALID_SOURCE_TYPES

CONTRACT_MARKERS = [
    "# ETF EU delivery-preflight contract v1",
    "## Purpose",
    "## Scope",
    "## Authority boundary",
    "## Delivery-preflight state model",
    "## Production manifest contract",
    "## Delivery receipt contract",
    "## Recipient authority gate",
    "## Transport authority gate",
    "## Preflight evidence requirements",
    "## What this contract does not authorize",
    "## Validation requirements",
]
RUNBOOK_MARKERS = [
    "# ETF EU outbound runbook v1",
    "## Purpose",
    "## Scope",
    "## Preconditions",
    "## Preflight checklist",
    "## Recipient gate",
    "## Transport gate",
    "## Manifest gate",
    "## Delivery execution gate",
    "## Post-send verification handoff",
    "## Abort conditions",
    "## What this runbook does not authorize",
    "## Validation requirements",
]
VERIFY_MARKERS = [
    "# ETF EU post-send verification and rollback policy v1",
    "## Purpose",
    "## Scope",
    "## Post-send verification loop",
    "## Receipt evidence requirements",
    "## Manifest evidence requirements",
    "## Failure handling",
    "## Rollback and abort policy",
    "## Delayed delivery confirmation policy",
    "## What this policy does not authorize",
    "## Validation requirements",
]
NOTE_MARKERS = [
    "# ETF-EU-WP15AM delivery-preflight contract and outbound runbook",
    "## Scope",
    "## Source artifacts",
    "## Delivery-preflight contract",
    "## Production manifest contract",
    "## Delivery receipt contract",
    "## Recipient authority gate",
    "## Transport authority gate",
    "## Outbound runbook",
    "## Post-send verification loop",
    "## Rollback and abort policy",
    "## Resolved delivery contract gaps",
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


def validate() -> dict[str, Any]:
    for path in [SOURCE_CLIENT_GRADE, SOURCE_LANGUAGE, SOURCE_DECISION, SOURCE_INVESTABILITY, SOURCE_POLICY, SOURCE_PRODUCT_FACTS, SOURCE_PRICING, SOURCE_REGISTRY, SOURCE_PDF, CONTRACT, RUNBOOK, VERIFY_POLICY, ARTIFACT, NOTES]:
        _require(path.exists(), f"missing file: {path}")

    client_grade = _load(SOURCE_CLIENT_GRADE)
    language = _load(SOURCE_LANGUAGE)
    decision = _load(SOURCE_DECISION)
    investability = _load(SOURCE_INVESTABILITY)
    policy = _load(SOURCE_POLICY)
    product_facts = _load(SOURCE_PRODUCT_FACTS)
    data = _load(ARTIFACT)

    _require(client_grade.get("work_package_id") == "ETF-EU-WP15AL", "client grade source mismatch")
    _require(language.get("work_package_id") == "ETF-EU-WP15AK", "language source mismatch")
    _require(decision.get("work_package_id") == "ETF-EU-WP15AJ", "decision source mismatch")
    _require(investability.get("work_package_id") == "ETF-EU-WP15AI", "investability source mismatch")
    _require(policy.get("work_package_id") == "ETF-EU-WP15AH", "policy source mismatch")
    _require(product_facts.get("work_package_id") == "ETF-EU-WP15AG", "product facts source mismatch")

    _require(data.get("work_package_id") == "ETF-EU-WP15AM", "wrong work package")
    _require(data.get("source_work_package") == "ETF-EU-WP15AL", "wrong source package")
    _require(data.get("source_client_grade_authority_artifact") == str(SOURCE_CLIENT_GRADE), "source client-grade artifact mismatch")
    _require(data.get("source_client_grade_pdf") == str(SOURCE_PDF), "source PDF mismatch")

    for key in [
        "delivery_preflight_contract_created",
        "delivery_preflight_contract_validated",
        "production_manifest_contract_created",
        "production_manifest_contract_validated",
        "delivery_receipt_contract_created",
        "delivery_receipt_contract_validated",
        "recipient_authority_gate_defined",
        "transport_authority_gate_defined",
        "outbound_runbook_created",
        "outbound_runbook_validated",
        "post_send_verification_loop_defined",
        "rollback_abort_policy_defined",
        "delivery_preflight_readiness_synthesis_created",
        "delivery_preflight_readiness_synthesis_validated",
        "client_grade_authority_created",
        "client_grade_claim",
    ]:
        _require(data.get(key) is True, f"expected true for {key}")

    _require(data.get("readiness_gate_status") == "delivery_preflight_contract_defined_not_authorized", "readiness status mismatch")
    _require(data.get("client_grade_status") == "authorized_no_delivery", "client grade status mismatch")
    _require(data.get("delivery_authorization_decision") == "remain_blocked", "delivery authorization mismatch")

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

    objects = {
        "delivery_preflight_contract": REQUIRED_CONTRACT_FIELDS,
        "production_manifest_contract": REQUIRED_MANIFEST_FIELDS,
        "delivery_receipt_contract": REQUIRED_RECEIPT_FIELDS,
        "recipient_authority_gate": REQUIRED_RECIPIENT_GATE_FIELDS,
        "transport_authority_gate": REQUIRED_TRANSPORT_GATE_FIELDS,
        "outbound_runbook": REQUIRED_RUNBOOK_FIELDS,
        "post_send_verification_loop": REQUIRED_LOOP_FIELDS,
        "rollback_abort_policy": REQUIRED_ROLLBACK_FIELDS,
    }
    for name, fields in objects.items():
        obj = data.get(name)
        _require(isinstance(obj, dict), f"missing object: {name}")
        _require_fields(obj, fields, name)

    _require(data["delivery_preflight_contract"]["contract_status"] == "defined_not_authorized", "contract status mismatch")
    _require(data["delivery_preflight_contract"]["delivery_preflight_allowed"] is False, "preflight allowed must be false")
    _require(data["delivery_preflight_contract"]["delivery_execution_allowed"] is False, "execution allowed must be false")
    _require(data["delivery_preflight_contract"]["next_required_package"] == "ETF-EU-WP15AN", "contract next package mismatch")
    _require(data["production_manifest_contract"]["manifest_created"] is False, "manifest must not be created")
    _require(data["delivery_receipt_contract"]["receipt_created"] is False, "receipt must not be created")
    _require(data["recipient_authority_gate"]["recipient_authority_created"] is False, "recipient authority must be false")
    _require(data["transport_authority_gate"]["transport_authority_created"] is False, "transport authority must be false")
    _require(data["outbound_runbook"]["execution_allowed"] is False, "runbook execution must be false")
    _require(data["post_send_verification_loop"]["verification_allowed"] is False, "verification must be false")
    _require(data["rollback_abort_policy"]["rollback_allowed"] is False, "rollback must be false")

    _require(set(data.get("resolved_delivery_contract_gaps", [])) == RESOLVED_GAPS, "resolved gaps mismatch")
    _require(set(data.get("remaining_delivery_preflight_blockers", [])) == REMAINING_BLOCKERS, "remaining blockers mismatch")

    manifest = data.get("source_manifest")
    _require(isinstance(manifest, list) and manifest, "source manifest missing")
    used_fields = " ".join(" ".join(source.get("used_for_fields", [])) for source in manifest)
    for required in ["delivery-preflight contract", "production manifest contract", "delivery receipt contract", "recipient authority gate", "transport authority gate", "outbound runbook", "post-send verification loop", "rollback abort policy"]:
        _require(required in used_fields, f"source support missing: {required}")
    for source in manifest:
        _require(source.get("source_type") in VALID_SOURCE_TYPES, "invalid source type")
        _require(source.get("authority_level") in VALID_AUTHORITY_LEVELS, "invalid authority level")
        _require(source.get("source_reference"), "source reference missing")

    for key in REQUIRED_FALSE:
        _require(data.get(key) is False, f"expected false for {key}")
    _require(data.get("review_only") is False, "review_only must remain false after client-grade authority")
    _require(data.get("pricing_evidence_for_client_grade") is True, "client-grade pricing evidence must remain true")
    _require(data.get("selected_next_package") in {"ETF-EU-WP15AN", "ETF-EU-WP15AM-FIX"}, "invalid next package")

    text_map = {
        CONTRACT: CONTRACT_MARKERS,
        RUNBOOK: RUNBOOK_MARKERS,
        VERIFY_POLICY: VERIFY_MARKERS,
        NOTES: NOTE_MARKERS,
    }
    for path, markers in text_map.items():
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            _require(marker in text, f"{path} missing marker: {marker}")

    return {
        "status": "valid",
        "work_package_id": data["work_package_id"],
        "readiness_gate_status": data["readiness_gate_status"],
        "delivery_preflight_contract_created": data["delivery_preflight_contract_created"],
        "delivery_preflight_contract_validated": data["delivery_preflight_contract_validated"],
        "outbound_runbook_created": data["outbound_runbook_created"],
        "outbound_runbook_validated": data["outbound_runbook_validated"],
        "delivery_preflight_allowed": data["delivery_preflight_allowed"],
        "production_delivery": data["production_delivery"],
        "receipt_artifact_created": data["receipt_artifact_created"],
        "production_manifest_created": data["production_manifest_created"],
        "recipient_authority_created": data["recipient_authority_created"],
        "transport_authority_created": data["transport_authority_created"],
        "resolved_delivery_contract_gaps_count": len(data["resolved_delivery_contract_gaps"]),
        "remaining_delivery_preflight_blockers_count": len(data["remaining_delivery_preflight_blockers"]),
        "selected_next_package": data["selected_next_package"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
