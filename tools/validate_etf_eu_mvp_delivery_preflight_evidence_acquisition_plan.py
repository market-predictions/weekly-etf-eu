from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SOURCE_RT_DECISION = Path("output/client_surface/etf_eu_recipient_transport_authority_decision_20260703_000000.json")
SOURCE_RT_EVIDENCE = Path("output/client_surface/etf_eu_recipient_transport_authority_evidence_contract_20260703_000000.json")
SOURCE_PREFLIGHT_AUTHORITY = Path("output/client_surface/etf_eu_delivery_preflight_authority_decision_20260703_000000.json")
SOURCE_PREFLIGHT_CONTRACT = Path("output/client_surface/etf_eu_delivery_preflight_contract_runbook_20260703_000000.json")
SOURCE_CLIENT_GRADE = Path("output/client_surface/etf_eu_client_grade_authority_decision_20260703_000000.json")
SOURCE_PRICING = Path("output/client_surface/etf_eu_multi_line_pricing_preview_20260703_000000.json")
SOURCE_REGISTRY = Path("config/ucits_symbol_registry.yml")
SOURCE_PDF = Path("output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.pdf")
PLAN = Path("control/ETF_EU_MVP_DELIVERY_PREFLIGHT_EVIDENCE_ACQUISITION_PLAN_V1.md")
ARTIFACT = Path("output/client_surface/etf_eu_mvp_delivery_preflight_evidence_acquisition_plan_20260703_000000.json")
NOTES = Path("output/client_surface/etf_eu_mvp_delivery_preflight_evidence_acquisition_plan_notes_20260703_000000.md")

REMAINING_BLOCKERS = {
    "recipient_configuration_authority",
    "transport_configuration_authority",
    "explicit_delivery_preflight_authority",
}

REQUIRED_FALSE = [
    "delivery_ready",
    "delivery_preflight_authority_created",
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
    "secret_values_exposed",
    "recipient_plaintext_values_exposed",
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

REQUIRED_EVIDENCE_FIELDS = {
    "recipient_set_reference_id_required",
    "recipient_set_hash_required",
    "recipient_owner_approval_reference_required",
    "recipient_rollback_reference_required",
    "transport_reference_id_required",
    "transport_presence_check_reference_required",
    "transport_owner_approval_reference_required",
    "transport_rollback_reference_required",
    "explicit_mvp_preflight_authority_reference_required",
    "secret_values_allowed",
    "plaintext_recipient_values_allowed",
}
REQUIRED_RECIPIENT_FIELDS = {
    "recipient_evidence_status",
    "recipient_set_reference_id_present",
    "recipient_set_hash_present",
    "recipient_owner_approval_reference_present",
    "recipient_rollback_reference_present",
    "recipient_plaintext_values_exposed",
    "recipient_config_changed",
    "recipient_authority_created",
    "acquisition_method",
    "recording_location",
}
REQUIRED_TRANSPORT_FIELDS = {
    "transport_evidence_status",
    "transport_reference_id_present",
    "transport_presence_check_reference_present",
    "transport_owner_approval_reference_present",
    "transport_rollback_reference_present",
    "secret_values_exposed",
    "smtp_or_secret_config_changed",
    "transport_authority_created",
    "acquisition_method",
    "recording_location",
}
REQUIRED_APPROVAL_FIELDS = {
    "approval_status",
    "recipient_owner_approval_reference_present",
    "transport_owner_approval_reference_present",
    "explicit_mvp_preflight_authority_reference_present",
    "approval_method",
}
REQUIRED_ROLLBACK_FIELDS = {
    "rollback_status",
    "recipient_rollback_reference_present",
    "transport_rollback_reference_present",
    "rollback_method",
}
REQUIRED_HANDOFF_FIELDS = {
    "mvp_handoff_created",
    "mvp_handoff_status",
    "next_package_type",
    "recommended_next_package",
    "fallback_next_package",
    "no_more_abstract_gates",
    "execution_allowed_now",
    "requires_operator_evidence_before_execution",
}
PLAN_MARKERS = [
    "# ETF EU MVP delivery-preflight evidence acquisition plan v1",
    "## Purpose",
    "## Scope",
    "## MVP boundary",
    "## Evidence required from user/operator",
    "## Recipient evidence acquisition",
    "## Transport evidence acquisition",
    "## Owner approval evidence",
    "## Rollback evidence",
    "## Validation method",
    "## Where evidence is recorded",
    "## What must never be committed",
    "## MVP delivery-preflight handoff",
    "## Stop rule against further abstract gating",
    "## Validation requirements",
]
NOTE_MARKERS = [
    "# ETF-EU-WP15AQ MVP delivery-preflight evidence acquisition plan",
    "## Scope",
    "## Source artifacts",
    "## Evidence required",
    "## Recipient evidence acquisition",
    "## Transport evidence acquisition",
    "## Approval evidence acquisition",
    "## Rollback evidence acquisition",
    "## MVP handoff",
    "## Stop recursive gating",
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


def validate() -> dict[str, Any]:
    for path in [SOURCE_RT_DECISION, SOURCE_RT_EVIDENCE, SOURCE_PREFLIGHT_AUTHORITY, SOURCE_PREFLIGHT_CONTRACT, SOURCE_CLIENT_GRADE, SOURCE_PRICING, SOURCE_REGISTRY, SOURCE_PDF, PLAN, ARTIFACT, NOTES]:
        _require(path.exists(), f"missing file: {path}")

    rt_decision = _load(SOURCE_RT_DECISION)
    data = _load(ARTIFACT)

    _require(rt_decision.get("work_package_id") == "ETF-EU-WP15AP", "source decision mismatch")
    _require(data.get("work_package_id") == "ETF-EU-WP15AQ", "wrong work package")
    _require(data.get("source_work_package") == "ETF-EU-WP15AP", "wrong source package")
    _require(data.get("source_recipient_transport_authority_decision_artifact") == str(SOURCE_RT_DECISION), "source RT decision path mismatch")
    _require(data.get("source_recipient_transport_authority_evidence_contract_artifact") == str(SOURCE_RT_EVIDENCE), "source RT evidence path mismatch")
    _require(data.get("source_delivery_preflight_authority_artifact") == str(SOURCE_PREFLIGHT_AUTHORITY), "source preflight authority path mismatch")
    _require(data.get("source_delivery_preflight_contract_artifact") == str(SOURCE_PREFLIGHT_CONTRACT), "source preflight contract path mismatch")
    _require(data.get("source_client_grade_authority_artifact") == str(SOURCE_CLIENT_GRADE), "source client-grade path mismatch")
    _require(data.get("source_pricing_artifact") == str(SOURCE_PRICING), "source pricing path mismatch")
    _require(data.get("source_registry") == str(SOURCE_REGISTRY), "source registry mismatch")
    _require(data.get("source_client_grade_pdf") == str(SOURCE_PDF), "source PDF mismatch")
    _require(data.get("mvp_evidence_acquisition_plan_path") == str(PLAN), "plan path mismatch")

    for key in [
        "mvp_evidence_acquisition_plan_created",
        "mvp_evidence_acquisition_plan_validated",
        "final_evidence_plan_before_mvp_execution",
        "stop_recursive_gating",
        "client_grade_authority_created",
        "client_grade_claim",
        "pricing_evidence_for_client_grade",
    ]:
        _require(data.get(key) is True, f"expected true for {key}")

    _require(data.get("selected_next_package") == "ETF-EU-MVP01", "selected next package must be ETF-EU-MVP01")
    _require(not str(data.get("selected_next_package", "")).startswith("ETF-EU-WP15"), "selected next package must not be another abstract WP15 gate")
    _require(data.get("recipient_transport_authority_status") == "not_authorized", "RT authority status mismatch")
    _require(data.get("delivery_preflight_status") == "not_authorized", "preflight status mismatch")
    _require(data.get("delivery_authorization_decision") == "remain_blocked", "delivery authorization mismatch")
    _require(data.get("client_grade_status") == "authorized_no_delivery", "client-grade status mismatch")

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
        "evidence_required": REQUIRED_EVIDENCE_FIELDS,
        "recipient_evidence_acquisition": REQUIRED_RECIPIENT_FIELDS,
        "transport_evidence_acquisition": REQUIRED_TRANSPORT_FIELDS,
        "approval_evidence_acquisition": REQUIRED_APPROVAL_FIELDS,
        "rollback_evidence_acquisition": REQUIRED_ROLLBACK_FIELDS,
        "mvp_handoff": REQUIRED_HANDOFF_FIELDS,
    }
    for name, fields in objects.items():
        obj = data.get(name)
        _require(isinstance(obj, dict), f"missing object: {name}")
        _require_fields(obj, fields, name)

    evidence = data["evidence_required"]
    for key in REQUIRED_EVIDENCE_FIELDS - {"secret_values_allowed", "plaintext_recipient_values_allowed"}:
        _require(evidence[key] is True, f"expected required evidence true: {key}")
    _require(evidence["secret_values_allowed"] is False, "secret values must not be allowed")
    _require(evidence["plaintext_recipient_values_allowed"] is False, "plaintext recipients must not be allowed")

    recipient = data["recipient_evidence_acquisition"]
    _require(recipient["recipient_evidence_status"] == "missing_required_for_mvp_execution", "recipient evidence status mismatch")
    for key in ["recipient_set_reference_id_present", "recipient_set_hash_present", "recipient_owner_approval_reference_present", "recipient_rollback_reference_present", "recipient_plaintext_values_exposed", "recipient_config_changed", "recipient_authority_created"]:
        _require(recipient[key] is False, f"recipient field must be false: {key}")

    transport = data["transport_evidence_acquisition"]
    _require(transport["transport_evidence_status"] == "missing_required_for_mvp_execution", "transport evidence status mismatch")
    for key in ["transport_reference_id_present", "transport_presence_check_reference_present", "transport_owner_approval_reference_present", "transport_rollback_reference_present", "secret_values_exposed", "smtp_or_secret_config_changed", "transport_authority_created"]:
        _require(transport[key] is False, f"transport field must be false: {key}")

    approval = data["approval_evidence_acquisition"]
    _require(approval["approval_status"] == "missing_required_for_mvp_execution", "approval status mismatch")
    _require(approval["explicit_mvp_preflight_authority_reference_present"] is False, "explicit MVP authority reference should be missing")

    rollback = data["rollback_evidence_acquisition"]
    _require(rollback["rollback_status"] == "missing_required_for_mvp_execution", "rollback status mismatch")

    handoff = data["mvp_handoff"]
    _require(handoff["mvp_handoff_created"] is True, "handoff must be created")
    _require(handoff["mvp_handoff_status"] == "ready_for_evidence_collection_not_execution", "handoff status mismatch")
    _require(handoff["next_package_type"] == "mvp_delivery_preflight_execution", "next package type mismatch")
    _require(handoff["recommended_next_package"] == "ETF-EU-MVP01", "recommended next package mismatch")
    _require(handoff["fallback_next_package"] == "ETF-EU-WP15AQ-FIX", "fallback mismatch")
    _require(handoff["no_more_abstract_gates"] is True, "no_more_abstract_gates must be true")
    _require(handoff["execution_allowed_now"] is False, "execution must not be allowed now")
    _require(handoff["requires_operator_evidence_before_execution"] is True, "operator evidence must be required")

    _require(data.get("remaining_client_grade_blockers") == [], "client-grade blockers must be empty")
    _require(set(data.get("remaining_delivery_preflight_blockers", [])) == REMAINING_BLOCKERS, "remaining blockers mismatch")

    for key in REQUIRED_FALSE:
        _require(data.get(key) is False, f"expected false for {key}")
    _require(data.get("review_only") is False, "review_only must remain false")

    manifest = data.get("source_manifest")
    _require(isinstance(manifest, list) and manifest, "source manifest missing")
    used = " ".join(" ".join(source.get("used_for_fields", [])) for source in manifest)
    for required in ["final evidence acquisition plan", "mvp handoff", "stop recursive gating", "delivery-preflight blocker preservation"]:
        _require(required in used, f"source support missing: {required}")

    for path, markers in {PLAN: PLAN_MARKERS, NOTES: NOTE_MARKERS}.items():
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            _require(marker in text, f"{path} missing marker: {marker}")

    return {
        "status": "valid",
        "work_package_id": data["work_package_id"],
        "mvp_evidence_acquisition_plan_created": data["mvp_evidence_acquisition_plan_created"],
        "mvp_evidence_acquisition_plan_validated": data["mvp_evidence_acquisition_plan_validated"],
        "final_evidence_plan_before_mvp_execution": data["final_evidence_plan_before_mvp_execution"],
        "stop_recursive_gating": data["stop_recursive_gating"],
        "no_more_abstract_gates": handoff["no_more_abstract_gates"],
        "execution_allowed_now": handoff["execution_allowed_now"],
        "recommended_next_package": handoff["recommended_next_package"],
        "recipient_authority_created": data["recipient_authority_created"],
        "transport_authority_created": data["transport_authority_created"],
        "delivery_preflight_allowed": data["delivery_preflight_allowed"],
        "production_delivery": data["production_delivery"],
        "remaining_delivery_preflight_blockers_count": len(data["remaining_delivery_preflight_blockers"]),
        "selected_next_package": data["selected_next_package"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
