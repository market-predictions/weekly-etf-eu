from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SOURCE_MVP02 = Path("output/client_surface/etf_eu_mvp_operator_evidence_intake_and_dry_run_20260703_000000.json")
SOURCE_MVP01 = Path("output/client_surface/etf_eu_mvp_delivery_preflight_execution_readiness_20260703_000000.json")
SOURCE_MVP_PLAN = Path("output/client_surface/etf_eu_mvp_delivery_preflight_evidence_acquisition_plan_20260703_000000.json")
SOURCE_RT_DECISION = Path("output/client_surface/etf_eu_recipient_transport_authority_decision_20260703_000000.json")
SOURCE_PREFLIGHT_CONTRACT = Path("output/client_surface/etf_eu_delivery_preflight_contract_runbook_20260703_000000.json")
SOURCE_PREFLIGHT_AUTHORITY = Path("output/client_surface/etf_eu_delivery_preflight_authority_decision_20260703_000000.json")
SOURCE_CLIENT_GRADE = Path("output/client_surface/etf_eu_client_grade_authority_decision_20260703_000000.json")
SOURCE_PRICING = Path("output/client_surface/etf_eu_multi_line_pricing_preview_20260703_000000.json")
SOURCE_REGISTRY = Path("config/ucits_symbol_registry.yml")
SOURCE_PDF = Path("output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.pdf")
TEMPLATE = Path("control/runtime_reference_templates/ETF_EU_MVP_OPERATOR_EVIDENCE_REFERENCE_TEMPLATE.md")
RUNBOOK = Path("control/ETF_EU_MVP_OPERATOR_EVIDENCE_COMPLETION_AND_PREFLIGHT_DRY_RUN_V1.md")
ARTIFACT = Path("output/client_surface/etf_eu_mvp_operator_evidence_completion_and_preflight_dry_run_20260703_000000.json")
NOTES = Path("output/client_surface/etf_eu_mvp_operator_evidence_completion_and_preflight_dry_run_notes_20260703_000000.md")

REMAINING_BLOCKERS = {"recipient_configuration_authority", "transport_configuration_authority", "explicit_delivery_preflight_authority"}

REQUIRED_FALSE = [
    "operator_evidence_present", "operator_evidence_complete", "dry_run_preflight_allowed", "dry_run_preflight_performed",
    "delivery_preflight_allowed", "execution_allowed_now", "send_allowed", "production_delivery", "dry_run_manifest_created",
    "manifest_created", "receipt_artifact_created", "production_manifest_created", "delivery_success_claimed",
    "delivery_success_claim_allowed", "recipient_authority_created", "transport_authority_created", "recipient_config_changed",
    "smtp_or_secret_config_changed", "secret_values_exposed", "recipient_plaintext_values_exposed", "valuation_grade",
    "funding_authority", "portfolio_mutation", "candidate_promotion", "pricing_evidence_for_delivery_preflight",
    "live_price_fetch_performed", "live_data_fetch_performed", "pricing_evidence_changed", "source_pdf_replaced",
    "new_pdf_created", "renderer_changed",
]

OBJECT_FIELDS = {
    "operator_evidence_completion_checklist": {
        "recipient_set_reference_id_complete", "recipient_set_hash_complete", "recipient_owner_approval_reference_complete",
        "recipient_rollback_reference_complete", "transport_reference_id_complete", "transport_presence_check_reference_complete",
        "transport_owner_approval_reference_complete", "transport_rollback_reference_complete", "explicit_mvp_preflight_authority_reference_complete",
        "operator_evidence_required", "operator_evidence_present", "operator_evidence_complete", "operator_evidence_status",
    },
    "placeholder_detection": {"template_inspected", "placeholder_values_detected", "blank_values_detected", "missing_fields_detected", "placeholder_detection_status"},
    "dry_run_eligibility_decision": {"decision_status", "decision_result", "decision_reason", "dry_run_preflight_allowed", "delivery_preflight_allowed", "execution_allowed_now", "send_allowed", "production_delivery", "required_next_step"},
    "dry_run_execution_result": {"dry_run_execution_attempted", "dry_run_preflight_performed", "delivery_preflight_performed", "send_performed", "dry_run_manifest_created", "manifest_created", "production_delivery", "execution_result_status"},
    "success_claim_boundary": {"manifest_required_for_success_claim", "dry_run_manifest_required_for_success_claim", "receipt_required_for_delivery_success_claim", "dry_run_manifest_created", "manifest_created", "receipt_artifact_created", "production_manifest_created", "delivery_success_claimed", "delivery_success_claim_allowed"},
    "mvp_next_step": {"mvp_next_step_created", "mvp_next_step_status", "recommended_next_package", "fallback_next_package", "no_more_abstract_gates", "next_package_type"},
}

RUNBOOK_MARKERS = [
    "# ETF EU MVP operator evidence completion and preflight dry-run v1", "## Purpose", "## Scope", "## MVP boundary", "## Source artifacts", "## Operator evidence reference inspection", "## Evidence completion rule", "## Placeholder detection rule", "## Dry-run eligibility rule", "## Dry-run execution rule", "## Dry-run manifest rule", "## Send boundary", "## Success claim boundary", "## What this package may execute", "## What this package must not execute", "## Next MVP step", "## Validation requirements",
]
NOTE_MARKERS = [
    "# ETF-EU-MVP03 operator evidence completion and preflight dry-run", "## Scope", "## Source artifacts", "## Operator evidence template inspection", "## Placeholder detection", "## Dry-run eligibility decision", "## Dry-run execution result", "## Success claim boundary", "## Remaining client-grade blockers", "## Remaining delivery-preflight blockers", "## Boundary checks", "## Decision", "## Next package",
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
    for path in [SOURCE_MVP02, SOURCE_MVP01, SOURCE_MVP_PLAN, SOURCE_RT_DECISION, SOURCE_PREFLIGHT_CONTRACT, SOURCE_PREFLIGHT_AUTHORITY, SOURCE_CLIENT_GRADE, SOURCE_PRICING, SOURCE_REGISTRY, SOURCE_PDF, TEMPLATE, RUNBOOK, ARTIFACT, NOTES]:
        _require(path.exists(), f"missing file: {path}")

    source = _load(SOURCE_MVP02)
    data = _load(ARTIFACT)
    _require(source.get("work_package_id") == "ETF-EU-MVP02", "source MVP02 mismatch")
    _require(source.get("selected_next_package") == "ETF-EU-MVP03", "source did not hand off to MVP03")

    _require(data.get("work_package_id") == "ETF-EU-MVP03", "wrong work package")
    _require(data.get("source_work_package") == "ETF-EU-MVP02", "wrong source package")
    _require(data.get("source_mvp_operator_evidence_intake_artifact") == str(SOURCE_MVP02), "source MVP02 path mismatch")
    _require(data.get("source_mvp_execution_readiness_artifact") == str(SOURCE_MVP01), "source MVP01 path mismatch")
    _require(data.get("source_mvp_evidence_acquisition_plan_artifact") == str(SOURCE_MVP_PLAN), "source MVP plan path mismatch")
    _require(data.get("source_recipient_transport_authority_decision_artifact") == str(SOURCE_RT_DECISION), "source RT decision path mismatch")
    _require(data.get("source_delivery_preflight_contract_artifact") == str(SOURCE_PREFLIGHT_CONTRACT), "source preflight contract path mismatch")
    _require(data.get("source_delivery_preflight_authority_artifact") == str(SOURCE_PREFLIGHT_AUTHORITY), "source preflight authority path mismatch")
    _require(data.get("source_client_grade_authority_artifact") == str(SOURCE_CLIENT_GRADE), "source client-grade path mismatch")
    _require(data.get("source_pricing_artifact") == str(SOURCE_PRICING), "source pricing path mismatch")
    _require(data.get("source_registry") == str(SOURCE_REGISTRY), "source registry mismatch")
    _require(data.get("source_client_grade_pdf") == str(SOURCE_PDF), "source PDF mismatch")
    _require(data.get("operator_evidence_completion_and_dry_run_path") == str(RUNBOOK), "runbook path mismatch")
    _require(data.get("operator_evidence_reference_template_path") == str(TEMPLATE), "template path mismatch")

    template_text = TEMPLATE.read_text(encoding="utf-8")
    _require("<operator supplied reference>" in template_text or "<operator supplied hash>" in template_text, "template placeholders not detected")

    for key in ["operator_evidence_completion_check_created", "operator_evidence_completion_check_validated", "mvp_series_continued", "no_more_abstract_gates", "operator_evidence_required", "placeholder_values_detected", "manifest_required_for_success_claim", "dry_run_manifest_required_for_success_claim", "receipt_required_for_delivery_success_claim", "client_grade_authority_created", "client_grade_claim", "pricing_evidence_for_client_grade"]:
        _require(data.get(key) is True, f"expected true for {key}")

    _require(data.get("operator_evidence_status") == "missing_required_for_dry_run_execution", "operator evidence status mismatch")
    _require(data.get("recipient_transport_authority_status") == "not_authorized", "RT status mismatch")
    _require(data.get("delivery_preflight_status") == "not_authorized", "preflight status mismatch")
    _require(data.get("delivery_authorization_decision") == "remain_blocked", "delivery authorization mismatch")
    _require(data.get("client_grade_status") == "authorized_no_delivery", "client-grade status mismatch")

    for key in REQUIRED_FALSE:
        _require(data.get(key) is False, f"expected false for {key}")

    _require(data.get("pdf_exists") is True, "PDF must exist")
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

    for name, fields in OBJECT_FIELDS.items():
        obj = data.get(name)
        _require(isinstance(obj, dict), f"missing object: {name}")
        _require_fields(obj, fields, name)

    _require(data["placeholder_detection"]["template_inspected"] is True, "template not inspected")
    _require(data["placeholder_detection"]["placeholder_values_detected"] is True, "placeholders should be detected")
    _require(data["placeholder_detection"]["placeholder_detection_status"] == "placeholders_present", "placeholder status mismatch")
    _require(data["dry_run_eligibility_decision"]["decision_result"] == "not_eligible_for_dry_run_execution", "dry-run decision mismatch")
    _require(data["dry_run_execution_result"]["execution_result_status"] == "not_executed_evidence_missing", "execution result mismatch")
    _require(data["success_claim_boundary"]["delivery_success_claimed"] is False, "delivery success must not be claimed")
    _require(data["mvp_next_step"]["recommended_next_package"] == "ETF-EU-MVP04", "recommended next package mismatch")

    _require(data.get("remaining_client_grade_blockers") == [], "client-grade blockers must be empty")
    _require(set(data.get("remaining_delivery_preflight_blockers", [])) == REMAINING_BLOCKERS, "remaining blockers mismatch")
    _require(data.get("selected_next_package") == "ETF-EU-MVP04", "selected next package mismatch")
    _require(not data.get("selected_next_package", "").startswith("ETF-EU-WP15"), "selected next package must not return to WP15")

    manifest = data.get("source_manifest")
    _require(isinstance(manifest, list) and manifest, "source manifest missing")

    for path, markers in {RUNBOOK: RUNBOOK_MARKERS, NOTES: NOTE_MARKERS}.items():
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            _require(marker in text, f"{path} missing marker: {marker}")

    return {
        "status": "valid",
        "work_package_id": data["work_package_id"],
        "operator_evidence_completion_check_created": data["operator_evidence_completion_check_created"],
        "operator_evidence_completion_check_validated": data["operator_evidence_completion_check_validated"],
        "mvp_series_continued": data["mvp_series_continued"],
        "no_more_abstract_gates": data["no_more_abstract_gates"],
        "operator_evidence_required": data["operator_evidence_required"],
        "operator_evidence_present": data["operator_evidence_present"],
        "operator_evidence_complete": data["operator_evidence_complete"],
        "operator_evidence_status": data["operator_evidence_status"],
        "placeholder_values_detected": data["placeholder_values_detected"],
        "dry_run_preflight_allowed": data["dry_run_preflight_allowed"],
        "dry_run_preflight_performed": data["dry_run_preflight_performed"],
        "delivery_preflight_allowed": data["delivery_preflight_allowed"],
        "send_allowed": data["send_allowed"],
        "production_delivery": data["production_delivery"],
        "dry_run_manifest_created": data["dry_run_manifest_created"],
        "manifest_created": data["manifest_created"],
        "receipt_artifact_created": data["receipt_artifact_created"],
        "delivery_success_claimed": data["delivery_success_claimed"],
        "selected_next_package": data["selected_next_package"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
