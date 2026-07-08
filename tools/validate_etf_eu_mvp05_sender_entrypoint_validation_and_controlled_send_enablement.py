from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CONTRACT = Path("control/ETF_EU_MVP05_SENDER_ENTRYPOINT_VALIDATION_AND_CONTROLLED_SEND_ENABLEMENT_V1.md")
ARTIFACT = Path("output/client_surface/etf_eu_mvp05_sender_entrypoint_validation_and_controlled_send_enablement_20260708_000000.json")
NOTES = Path("output/client_surface/etf_eu_mvp05_sender_entrypoint_validation_and_controlled_send_enablement_notes_20260708_000000.md")
WORKFLOW = Path(".github/workflows/send-weekly-etf-eu-report.yml")
LATEST_DELIVERY_MANIFEST = "output/delivery/etf_eu_delivery_manifest_20260708_142840.json"
LATEST_RUN_BUNDLE = "output/runs/20260708_142840/etf_eu_run_bundle_manifest.json"

ROLEMODEL_ENV_NAMES = {
    "MRKT_RPRTS_SMTP_HOST",
    "MRKT_RPRTS_SMTP_PORT",
    "MRKT_RPRTS_SMTP_USER",
    "MRKT_RPRTS_SMTP_PASS",
    "MRKT_RPRTS_MAIL_FROM",
    "MRKT_RPRTS_MAIL_TO",
    "MRKT_RPRTS_MAIL_TO_NL",
}

REQUIRED_FALSE = [
    "delivery_enabled",
    "production_delivery",
    "email_delivery",
    "pdf_generation",
    "delivery_receipt",
    "sender_entrypoint_validated",
    "send_enablement_allowed",
    "delivery_mode_send_unlocked",
    "workflow_send_guard_removed",
    "delivery_success_claimed",
    "delivery_success_claim_allowed",
    "portfolio_mutation",
    "candidate_promotion",
    "funding_authority",
    "valuation_grade",
    "pricing_evidence_changed",
    "source_pdf_replaced",
    "new_pdf_created",
    "renderer_changed",
]

REQUIRED_TRUE = [
    "sender_entrypoint_validation_created",
    "sender_entrypoint_inventory_created",
    "workflow_send_guard_present",
    "rolemodel_secret_names_declared",
    "dutch_primary_delivery_rule_created",
    "english_companion_delivery_rule_created",
    "delivery_manifest_transition_rule_created",
    "run_bundle_transition_rule_created",
    "receipt_rule_created",
    "success_claim_rule_created",
]

NESTED_OBJECTS = {
    "sender_entrypoint_validation",
    "send_guard_decision",
    "manifest_transition_decision",
    "receipt_and_success_boundary",
    "next_step_decision",
}

CONTRACT_MARKERS = [
    "# ETF EU MVP05 sender entrypoint validation and controlled send enablement v1",
    "## Confirmed dry-run evidence",
    "## Sender entrypoint inventory",
    "## Send guard rule",
    "## Delivery manifest transition rule",
    "## Receipt rule",
    "## Success claim rule",
]

NOTE_MARKERS = [
    "# ETF-EU-MVP05 sender entrypoint validation and controlled send enablement",
    "## Confirmed dry-run evidence",
    "## Sender entrypoint inventory",
    "## Send guard decision",
    "## Manifest transition decision",
    "## Receipt and success boundary",
    "## Boundaries preserved",
    "## Decision",
    "## Next package",
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate() -> dict[str, Any]:
    for path in [CONTRACT, ARTIFACT, NOTES, WORKFLOW]:
        _require(path.exists(), f"missing file: {path}")

    data = _load(ARTIFACT)
    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    contract_text = CONTRACT.read_text(encoding="utf-8")
    notes_text = NOTES.read_text(encoding="utf-8")

    _require(data.get("work_package_id") == "ETF-EU-MVP05", "wrong work package")
    _require(data.get("source_work_package") == "ETF-EU-MVP04-FIX-VALIDATE-ONLY-02", "wrong source package")
    _require(data.get("latest_validated_workflow_mode") == "dry_run", "wrong workflow mode")
    _require(data.get("validate_only_status") == "green", "validate_only not green")
    _require(data.get("dry_run_status") == "green", "dry_run not green")
    _require(data.get("latest_delivery_manifest") == LATEST_DELIVERY_MANIFEST, "latest delivery manifest mismatch")
    _require(data.get("latest_run_bundle") == LATEST_RUN_BUNDLE, "latest run bundle mismatch")
    _require(data.get("delivery_manifest_validation") == "passed", "delivery manifest validation mismatch")
    _require(data.get("run_bundle_validation") == "passed", "run bundle validation mismatch")
    _require(data.get("delivery_manifest_status") == "available", "delivery manifest status mismatch")
    _require(data.get("sender_entrypoint_validation_status") == "not_validated_yet", "sender validation status mismatch")

    for key in REQUIRED_TRUE:
        _require(data.get(key) is True, f"expected true for {key}")
    for key in REQUIRED_FALSE:
        _require(data.get(key) is False, f"expected false for {key}")

    private_key = "secret_values_exposed"
    recipients_key = "recipient_plaintext_values_exposed"
    _require(data.get(private_key) is False, f"expected false for {private_key}")
    _require(data.get(recipients_key) is False, f"expected false for {recipients_key}")

    _require(set(data.get("rolemodel_secret_names", [])) == ROLEMODEL_ENV_NAMES, "rolemodel env names mismatch")
    for env_name in ROLEMODEL_ENV_NAMES:
        _require(env_name in workflow_text, f"workflow missing rolemodel env name: {env_name}")

    _require("Guard EU send mode until sender entrypoint is promoted" in workflow_text, "workflow send guard missing")
    _require("ETF_EU_SEND_MODE_REQUESTED" in workflow_text, "send guard marker missing")
    _require("exit 1" in workflow_text, "send guard must remain blocking")

    for obj_name in NESTED_OBJECTS:
        _require(isinstance(data.get(obj_name), dict), f"missing nested object: {obj_name}")

    se = data["sender_entrypoint_validation"]
    _require(se.get("sender_entrypoint_inventory_created") is True, "sender inventory missing")
    _require(se.get("sender_entrypoint_candidates") == ["send_report_runtime_html.py", "send_report.py"], "sender candidates mismatch")
    _require(se.get("eu_sender_entrypoint_selected") is False, "EU sender should not be selected")
    _require(se.get("sender_entrypoint_validated") is False, "sender entrypoint should not be validated")

    guard = data["send_guard_decision"]
    _require(guard.get("workflow_send_guard_present") is True, "send guard missing")
    _require(guard.get("workflow_send_guard_removed") is False, "send guard removed")
    _require(guard.get("delivery_mode_send_unlocked") is False, "send unlocked too early")
    _require(guard.get("send_enablement_allowed") is False, "send enablement allowed too early")

    manifest = data["manifest_transition_decision"]
    _require(manifest.get("delivery_manifest_framework_exists") is True, "delivery manifest framework missing")
    _require(manifest.get("run_bundle_manifest_framework_exists") is True, "run bundle framework missing")
    _require(manifest.get("current_delivery_manifest_status") == "available", "manifest current status mismatch")
    _require(manifest.get("manifest_transition_validated") is False, "manifest transition should not be validated")

    receipt = data["receipt_and_success_boundary"]
    _require(receipt.get("receipt_required_for_delivery_success_claim") is True, "receipt requirement missing")
    _require(receipt.get("delivery_receipt") is False, "receipt must be false")
    _require(receipt.get("delivery_success_claimed") is False, "delivery success claimed")
    _require(receipt.get("delivery_success_claim_allowed") is False, "delivery success allowed too early")

    next_step = data["next_step_decision"]
    _require(next_step.get("recommended_next_package") == "ETF-EU-MVP06", "wrong recommended next package")
    _require(next_step.get("no_return_to_manual_evidence_route") is True, "manual route return not blocked")
    _require(next_step.get("no_return_to_wp15_gating") is True, "WP15 return not blocked")

    selected = data.get("selected_next_package")
    _require(selected == "ETF-EU-MVP06", "selected next package mismatch")
    _require(not selected.startswith("ETF-EU-WP15"), "must not select WP15")
    _require(selected != "OPERATOR_ACTION_REQUIRED", "must not return to operator action required")

    _require(isinstance(data.get("source_manifest"), list) and data["source_manifest"], "source manifest missing")

    for marker in CONTRACT_MARKERS:
        _require(marker in contract_text, f"contract missing marker: {marker}")
    for marker in NOTE_MARKERS:
        _require(marker in notes_text, f"notes missing marker: {marker}")

    return {
        "status": "valid",
        "work_package_id": data["work_package_id"],
        "latest_validated_workflow_mode": data["latest_validated_workflow_mode"],
        "validate_only_status": data["validate_only_status"],
        "dry_run_status": data["dry_run_status"],
        "latest_delivery_manifest": data["latest_delivery_manifest"],
        "latest_run_bundle": data["latest_run_bundle"],
        "sender_entrypoint_validation_created": data["sender_entrypoint_validation_created"],
        "sender_entrypoint_validated": data["sender_entrypoint_validated"],
        "send_enablement_allowed": data["send_enablement_allowed"],
        "delivery_mode_send_unlocked": data["delivery_mode_send_unlocked"],
        "workflow_send_guard_present": data["workflow_send_guard_present"],
        "workflow_send_guard_removed": data["workflow_send_guard_removed"],
        "production_delivery": data["production_delivery"],
        "email_delivery": data["email_delivery"],
        "delivery_receipt": data["delivery_receipt"],
        "delivery_success_claimed": data["delivery_success_claimed"],
        "selected_next_package": data["selected_next_package"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
