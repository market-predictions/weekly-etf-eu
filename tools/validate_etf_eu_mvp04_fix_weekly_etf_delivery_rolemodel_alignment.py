from __future__ import annotations

import json
from pathlib import Path
from typing import Any

WORKFLOW = Path(".github/workflows/send-weekly-etf-eu-report.yml")
CONTRACT = Path("control/ETF_EU_MVP04_FIX_WEEKLY_ETF_DELIVERY_ROLEMODEL_ALIGNMENT_V1.md")
ARTIFACT = Path("output/client_surface/etf_eu_mvp04_fix_weekly_etf_delivery_rolemodel_alignment_20260704_000000.json")
NOTES = Path("output/client_surface/etf_eu_mvp04_fix_weekly_etf_delivery_rolemodel_alignment_notes_20260704_000000.md")

SECRET_NAMES = [
    "MRKT_RPRTS_SMTP_HOST",
    "MRKT_RPRTS_SMTP_PORT",
    "MRKT_RPRTS_SMTP_USER",
    "MRKT_RPRTS_SMTP_PASS",
    "MRKT_RPRTS_MAIL_FROM",
    "MRKT_RPRTS_MAIL_TO",
    "MRKT_RPRTS_MAIL_TO_NL",
]

REQUIRED_TRUE = [
    "manual_evidence_route_superseded",
    "operator_hash_requirement_removed",
    "workflow_delivery_mode_input_created",
    "dry_run_mode_declared",
    "send_mode_declared",
    "send_mode_blocked_until_eu_sender_validated",
    "rolemodel_secret_names_declared",
    "manifest_required_for_success_claim",
    "delivery_manifest_framework_exists",
    "run_bundle_manifest_framework_exists",
]

REQUIRED_FALSE = [
    "operator_reference_template_required_for_delivery",
    "secret_values_exposed",
    "recipient_plaintext_values_exposed",
    "production_delivery",
    "send_performed",
    "email_delivery",
    "delivery_success_claimed",
    "delivery_success_claim_allowed",
    "operator_action_required",
    "selected_next_package_is_mvp05",
    "selected_next_package_is_wp15",
    "portfolio_mutation",
    "candidate_promotion",
    "funding_authority",
    "valuation_grade",
    "pricing_evidence_changed",
    "source_pdf_replaced",
    "new_pdf_created",
    "renderer_changed",
]

WORKFLOW_MARKERS = [
    "delivery_mode:",
    "default: \"validate_only\"",
    "- validate_only",
    "- dry_run",
    "- send",
    "ETF_EU_DELIVERY_MODE",
    "Guard EU send mode until sender entrypoint is promoted",
    "ETF_EU_SEND_MODE_REQUESTED",
    "ETF_EU_DELIVERY_DRY_RUN_MODE",
]

CONTRACT_MARKERS = [
    "# ETF EU MVP04-FIX weekly-etf delivery rolemodel alignment v1",
    "manual_evidence_route_superseded=true",
    "workflow_delivery_mode_input_created=true",
    "selected_next_step=RUN_WORKFLOW_VALIDATE_ONLY_OR_DRY_RUN",
]

NOTE_MARKERS = [
    "# ETF-EU-MVP04-FIX weekly-etf delivery rolemodel alignment",
    "manual_evidence_route_superseded=true",
    "selected_next_step=RUN_WORKFLOW_VALIDATE_ONLY_OR_DRY_RUN",
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate() -> dict[str, Any]:
    for path in [WORKFLOW, CONTRACT, ARTIFACT, NOTES]:
        _require(path.exists(), f"missing file: {path}")

    data = _load(ARTIFACT)
    workflow = WORKFLOW.read_text(encoding="utf-8")
    contract = CONTRACT.read_text(encoding="utf-8")
    notes = NOTES.read_text(encoding="utf-8")

    _require(data.get("work_package_id") == "ETF-EU-MVP04-FIX", "wrong work_package_id")
    _require(data.get("source_work_package") == "ETF-EU-MVP04", "wrong source_work_package")
    _require(data.get("rolemodel_repository") == "market-predictions/weekly-etf", "wrong rolemodel repository")
    _require(data.get("eu_workflow") == str(WORKFLOW), "wrong EU workflow path")
    _require(data.get("alignment_contract_path") == str(CONTRACT), "wrong contract path")

    for key in REQUIRED_TRUE:
        _require(data.get(key) is True, f"expected true for {key}")
    for key in REQUIRED_FALSE:
        _require(data.get(key) is False, f"expected false for {key}")

    _require(data.get("delivery_mode_default") == "validate_only", "default delivery mode mismatch")
    _require(data.get("push_delivery_mode") == "validate_only", "push delivery mode mismatch")
    _require(set(data.get("delivery_mode_options", [])) == {"validate_only", "dry_run", "send"}, "delivery mode options mismatch")
    _require(data.get("delivery_workflow_alignment_status") == "rolemodel_gated_safe_default", "alignment status mismatch")
    _require(data.get("delivery_execution_status") == "validate_only_or_dry_run_ready", "delivery execution status mismatch")
    _require(data.get("send_execution_status") == "blocked_pending_eu_sender_entrypoint_validation", "send execution status mismatch")
    _require(data.get("manual_operator_action_required_status") == "superseded_by_workflow_alignment", "manual route status mismatch")
    _require(data.get("selected_next_step") == "RUN_WORKFLOW_VALIDATE_ONLY_OR_DRY_RUN", "selected next step mismatch")
    _require(data.get("selected_next_package") == "RUN_WORKFLOW_VALIDATE_ONLY_OR_DRY_RUN", "selected next package mismatch")
    _require(not str(data.get("selected_next_package", "")).startswith("ETF-EU-MVP05"), "must not select MVP05")
    _require(not str(data.get("selected_next_package", "")).startswith("ETF-EU-WP15"), "must not select WP15")

    for secret_name in SECRET_NAMES:
        _require(secret_name in workflow, f"workflow missing rolemodel secret name: {secret_name}")
        _require(secret_name in data.get("rolemodel_secret_names", []), f"artifact missing rolemodel secret name: {secret_name}")

    for marker in WORKFLOW_MARKERS:
        _require(marker in workflow, f"workflow missing marker: {marker}")
    for marker in CONTRACT_MARKERS:
        _require(marker in contract, f"contract missing marker: {marker}")
    for marker in NOTE_MARKERS:
        _require(marker in notes, f"notes missing marker: {marker}")

    return {
        "status": "valid",
        "work_package_id": data["work_package_id"],
        "manual_evidence_route_superseded": data["manual_evidence_route_superseded"],
        "workflow_delivery_mode_input_created": data["workflow_delivery_mode_input_created"],
        "delivery_mode_default": data["delivery_mode_default"],
        "dry_run_mode_declared": data["dry_run_mode_declared"],
        "send_mode_declared": data["send_mode_declared"],
        "send_mode_blocked_until_eu_sender_validated": data["send_mode_blocked_until_eu_sender_validated"],
        "rolemodel_secret_names_declared": data["rolemodel_secret_names_declared"],
        "operator_action_required": data["operator_action_required"],
        "selected_next_package": data["selected_next_package"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
