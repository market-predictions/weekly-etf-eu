from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SOURCE_MVP01 = Path("output/client_surface/etf_eu_mvp_delivery_preflight_execution_readiness_20260703_000000.json")
SOURCE_MVP_PLAN = Path("output/client_surface/etf_eu_mvp_delivery_preflight_evidence_acquisition_plan_20260703_000000.json")
SOURCE_RT_DECISION = Path("output/client_surface/etf_eu_recipient_transport_authority_decision_20260703_000000.json")
SOURCE_PREFLIGHT_CONTRACT = Path("output/client_surface/etf_eu_delivery_preflight_contract_runbook_20260703_000000.json")
SOURCE_PREFLIGHT_AUTHORITY = Path("output/client_surface/etf_eu_delivery_preflight_authority_decision_20260703_000000.json")
SOURCE_CLIENT_GRADE = Path("output/client_surface/etf_eu_client_grade_authority_decision_20260703_000000.json")
SOURCE_PRICING = Path("output/client_surface/etf_eu_multi_line_pricing_preview_20260703_000000.json")
SOURCE_REGISTRY = Path("config/ucits_symbol_registry.yml")
SOURCE_PDF = Path("output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.pdf")
INTAKE = Path("control/ETF_EU_MVP_OPERATOR_EVIDENCE_INTAKE_AND_DRY_RUN_V1.md")
TEMPLATE = Path("control/runtime_reference_templates/ETF_EU_MVP_OPERATOR_EVIDENCE_REFERENCE_TEMPLATE.md")
ARTIFACT = Path("output/client_surface/etf_eu_mvp_operator_evidence_intake_and_dry_run_20260703_000000.json")
NOTES = Path("output/client_surface/etf_eu_mvp_operator_evidence_intake_and_dry_run_notes_20260703_000000.md")

REMAINING_BLOCKERS = {"recipient_configuration_authority", "transport_configuration_authority", "explicit_delivery_preflight_authority"}

REQUIRED_FALSE = [
    "operator_evidence_present", "operator_evidence_complete", "dry_run_preflight_allowed", "dry_run_preflight_performed",
    "delivery_preflight_allowed", "execution_allowed_now", "send_allowed", "production_delivery",
    "dry_run_manifest_created", "manifest_created", "receipt_artifact_created", "production_manifest_created",
    "delivery_success_claimed", "delivery_success_claim_allowed", "recipient_authority_created", "transport_authority_created",
    "recipient_config_changed", "smtp_or_secret_config_changed", "secret_values_exposed", "recipient_plaintext_values_exposed",
    "valuation_grade", "funding_authority", "portfolio_mutation", "candidate_promotion", "pricing_evidence_for_delivery_preflight",
    "live_price_fetch_performed", "live_data_fetch_performed", "pricing_evidence_changed", "source_pdf_replaced", "new_pdf_created", "renderer_changed",
]

REQUIRED_OBJECT_FIELDS = {
    "operator_evidence_intake_checklist": {
        "recipient_set_reference_id_present", "recipient_set_hash_present", "recipient_owner_approval_reference_present",
        "recipient_rollback_reference_present", "transport_reference_id_present", "transport_presence_check_reference_present",
        "transport_owner_approval_reference_present", "transport_rollback_reference_present", "explicit_mvp_preflight_authority_reference_present",
        "operator_evidence_required", "operator_evidence_present", "operator_evidence_complete", "operator_evidence_status",
    },
    "dry_run_eligibility_decision": {
        "decision_status", "decision_result", "decision_reason", "dry_run_preflight_allowed", "delivery_preflight_allowed",
        "execution_allowed_now", "send_allowed", "production_delivery", "required_next_step",
    },
    "dry_run_execution_boundary": {
        "dry_run_preflight_prepared", "dry_run_preflight_performed", "delivery_preflight_performed", "send_performed",
        "dry_run_manifest_created", "manifest_created", "production_delivery", "execution_boundary_status",
    },
    "success_claim_boundary": {
        "manifest_required_for_success_claim", "receipt_required_for_delivery_success_claim", "dry_run_manifest_created", "manifest_created",
        "receipt_artifact_created", "production_manifest_created", "delivery_success_claimed", "delivery_success_claim_allowed",
    },
    "mvp_next_step": {
        "mvp_next_step_created", "mvp_next_step_status", "recommended_next_package", "fallback_next_package", "no_more_abstract_gates", "next_package_type",
    },
}

INTAKE_MARKERS = [
    "# ETF EU MVP operator evidence intake and dry-run v1", "## Purpose", "## Scope", "## MVP boundary", "## Source artifacts",
    "## Operator evidence intake fields", "## Operator evidence reference template", "## Evidence validation rule", "## Dry-run eligibility rule",
    "## Dry-run execution boundary", "## Send boundary", "## Manifest and receipt rule", "## What this package may create",
    "## What this package must not create", "## Next MVP step", "## Validation requirements",
]
NOTE_MARKERS = [
    "# ETF-EU-MVP02 operator evidence intake and delivery-preflight dry-run", "## Scope", "## Source artifacts", "## Operator evidence intake",
    "## Dry-run eligibility decision", "## Dry-run execution boundary", "## Success claim boundary", "## Remaining client-grade blockers",
    "## Remaining delivery-preflight blockers", "## Boundary checks", "## Decision", "## Next package",
]
TEMPLATE_MARKERS = [
    "recipient_set_reference_id=<operator supplied reference>", "recipient_set_hash=<operator supplied hash>",
    "transport_reference_id=<operator supplied reference>", "explicit_mvp_preflight_authority_reference=<operator supplied reference>",
    "Use references and hashes only.",
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
    for path in [SOURCE_MVP01, SOURCE_MVP_PLAN, SOURCE_RT_DECISION, SOURCE_PREFLIGHT_CONTRACT, SOURCE_PREFLIGHT_AUTHORITY, SOURCE_CLIENT_GRADE, SOURCE_PRICING, SOURCE_REGISTRY, SOURCE_PDF, INTAKE, TEMPLATE, ARTIFACT, NOTES]:
        _require(path.exists(), f"missing file: {path}")

    source_mvp01 = _load(SOURCE_MVP01)
    data = _load(ARTIFACT)
    _require(source_mvp01.get("work_package_id") == "ETF-EU-MVP01", "source MVP01 mismatch")
    _require(source_mvp01.get("selected_next_package") == "ETF-EU-MVP02", "source did not hand off to MVP02")

    _require(data.get("work_package_id") == "ETF-EU-MVP02", "wrong work package")
    _require(data.get("source_work_package") == "ETF-EU-MVP01", "wrong source package")
    _require(data.get("source_mvp_execution_readiness_artifact") == str(SOURCE_MVP01), "source MVP01 path mismatch")
    _require(data.get("source_mvp_evidence_acquisition_plan_artifact") == str(SOURCE_MVP_PLAN), "source MVP plan path mismatch")
    _require(data.get("source_recipient_transport_authority_decision_artifact") == str(SOURCE_RT_DECISION), "source RT decision path mismatch")
    _require(data.get("source_delivery_preflight_contract_artifact") == str(SOURCE_PREFLIGHT_CONTRACT), "source preflight contract path mismatch")
    _require(data.get("source_delivery_preflight_authority_artifact") == str(SOURCE_PREFLIGHT_AUTHORITY), "source preflight authority path mismatch")
    _require(data.get("source_client_grade_authority_artifact") == str(SOURCE_CLIENT_GRADE), "source client-grade path mismatch")
    _require(data.get("source_pricing_artifact") == str(SOURCE_PRICING), "source pricing path mismatch")
    _require(data.get("source_registry") == str(SOURCE_REGISTRY), "source registry mismatch")
    _require(data.get("source_client_grade_pdf") == str(SOURCE_PDF), "source PDF mismatch")
    _require(data.get("operator_evidence_intake_path") == str(INTAKE), "intake path mismatch")
    _require(data.get("operator_evidence_reference_template_path") == str(TEMPLATE), "template path mismatch")

    for key in [
        "operator_evidence_intake_created", "operator_evidence_intake_validated", "mvp_series_continued", "no_more_abstract_gates",
        "operator_evidence_required", "manifest_required_for_success_claim", "receipt_required_for_delivery_success_claim",
        "client_grade_authority_created", "client_grade_claim", "pricing_evidence_for_client_grade",
    ]:
        _require(data.get(key) is True, f"expected true for {key}")

    _require(data.get("operator_evidence_status") == "missing_required_for_dry_run", "operator evidence status mismatch")
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

    for name, fields in REQUIRED_OBJECT_FIELDS.items():
        obj = data.get(name)
        _require(isinstance(obj, dict), f"missing object: {name}")
        _require_fields(obj, fields, name)

    checklist = data["operator_evidence_intake_checklist"]
    _require(checklist["operator_evidence_required"] is True, "operator evidence must be required")
    _require(checklist["operator_evidence_present"] is False, "operator evidence must be absent")
    _require(checklist["operator_evidence_complete"] is False, "operator evidence must be incomplete")
    _require(checklist["operator_evidence_status"] == "missing_required_for_dry_run", "operator checklist status mismatch")

    decision = data["dry_run_eligibility_decision"]
    _require(decision["decision_status"] == "validated", "decision status mismatch")
    _require(decision["decision_result"] == "not_eligible_for_dry_run", "decision result mismatch")
    _require(decision["decision_reason"] == "operator_evidence_missing", "decision reason mismatch")
    _require(decision["required_next_step"] == "operator_evidence_completion", "required next step mismatch")

    boundary = data["dry_run_execution_boundary"]
    _require(boundary["dry_run_preflight_prepared"] is True, "dry-run must be prepared")
    for key in ["dry_run_preflight_performed", "delivery_preflight_performed", "send_performed", "dry_run_manifest_created", "manifest_created", "production_delivery"]:
        _require(boundary[key] is False, f"boundary expected false: {key}")
    _require(boundary["execution_boundary_status"] == "intake_created_not_executed", "boundary status mismatch")

    success = data["success_claim_boundary"]
    _require(success["manifest_required_for_success_claim"] is True, "manifest requirement missing")
    _require(success["receipt_required_for_delivery_success_claim"] is True, "receipt requirement missing")
    for key in ["dry_run_manifest_created", "manifest_created", "receipt_artifact_created", "production_manifest_created", "delivery_success_claimed", "delivery_success_claim_allowed"]:
        _require(success[key] is False, f"success expected false: {key}")

    next_step = data["mvp_next_step"]
    _require(next_step["mvp_next_step_created"] is True, "MVP next step missing")
    _require(next_step["mvp_next_step_status"] == "operator_evidence_completion_required", "MVP next step status mismatch")
    _require(next_step["recommended_next_package"] == "ETF-EU-MVP03", "recommended next package mismatch")
    _require(next_step["fallback_next_package"] == "ETF-EU-MVP02-FIX", "fallback next package mismatch")
    _require(next_step["no_more_abstract_gates"] is True, "abstract gate stop rule missing")

    _require(data.get("remaining_client_grade_blockers") == [], "client-grade blockers must be empty")
    _require(set(data.get("remaining_delivery_preflight_blockers", [])) == REMAINING_BLOCKERS, "remaining blockers mismatch")
    _require(data.get("selected_next_package") == "ETF-EU-MVP03", "selected next package mismatch")
    _require(not data.get("selected_next_package", "").startswith("ETF-EU-WP15"), "selected next package must not return to WP15")

    manifest = data.get("source_manifest")
    _require(isinstance(manifest, list) and manifest, "source manifest missing")

    for path, markers in {INTAKE: INTAKE_MARKERS, NOTES: NOTE_MARKERS, TEMPLATE: TEMPLATE_MARKERS}.items():
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            _require(marker in text, f"{path} missing marker: {marker}")

    return {
        "status": "valid",
        "work_package_id": data["work_package_id"],
        "operator_evidence_intake_created": data["operator_evidence_intake_created"],
        "operator_evidence_intake_validated": data["operator_evidence_intake_validated"],
        "mvp_series_continued": data["mvp_series_continued"],
        "no_more_abstract_gates": data["no_more_abstract_gates"],
        "operator_evidence_required": data["operator_evidence_required"],
        "operator_evidence_present": data["operator_evidence_present"],
        "operator_evidence_complete": data["operator_evidence_complete"],
        "operator_evidence_status": data["operator_evidence_status"],
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
