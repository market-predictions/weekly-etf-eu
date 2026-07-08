from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_sender_entrypoint import validate as validate_sender

CONTRACT = Path("control/ETF_EU_MVP06_SENDER_ENTRYPOINT_IMPLEMENTATION_OR_VALIDATION_V1.md")
ARTIFACT = Path("output/client_surface/etf_eu_mvp06_sender_entrypoint_implementation_or_validation_20260708_000000.json")
NOTES = Path("output/client_surface/etf_eu_mvp06_sender_entrypoint_implementation_or_validation_notes_20260708_000000.md")
ENTRYPOINT = Path("runtime/send_etf_eu_report_runtime_html.py")
SENDER_VALIDATOR = Path("tools/validate_etf_eu_sender_entrypoint.py")
WORKFLOW = Path(".github/workflows/send-weekly-etf-eu-report.yml")
MVP05 = Path("output/client_surface/etf_eu_mvp05_sender_entrypoint_validation_and_controlled_send_enablement_20260708_000000.json")

REQUIRED_TRUE = [
    "eu_sender_entrypoint_created",
    "eu_sender_entrypoint_selected",
    "sender_entrypoint_validated",
    "preflight_no_send_mode_supported",
    "dutch_primary_supported",
    "english_companion_supported",
    "non_canonical_artifacts_ignored",
    "workflow_send_guard_present",
]

REQUIRED_FALSE = [
    "us_report_name_assumption_detected",
    "delivery_enabled",
    "production_delivery",
    "email_delivery",
    "pdf_generation",
    "delivery_receipt",
    "send_performed",
    "send_enablement_allowed",
    "delivery_mode_send_unlocked",
    "workflow_send_guard_removed",
    "delivery_success_claimed",
    "delivery_success_claim_allowed",
    "secret_values_exposed",
    "recipient_plaintext_values_exposed",
    "portfolio_mutation",
    "candidate_promotion",
    "funding_authority",
    "valuation_grade",
    "pricing_evidence_changed",
    "source_pdf_replaced",
    "new_pdf_created",
    "renderer_changed",
]

CONTRACT_MARKERS = [
    "# ETF EU MVP06 sender entrypoint implementation or validation v1",
    "## Sender entrypoint implemented",
    "## Sender preflight behavior",
    "## Dutch-primary and English companion support",
    "## Non-canonical artifact handling",
    "## Send guard decision",
]

NOTE_MARKERS = [
    "# ETF-EU-MVP06 sender entrypoint implementation or validation",
    "## Source evidence",
    "## Sender entrypoint implemented",
    "## Sender preflight behavior",
    "## Dutch-primary and English companion support",
    "## Non-canonical artifact handling",
    "## Send guard decision",
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
    for path in [CONTRACT, ARTIFACT, NOTES, ENTRYPOINT, SENDER_VALIDATOR, WORKFLOW, MVP05]:
        _require(path.exists(), f"missing file: {path}")

    data = _load(ARTIFACT)
    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    contract_text = CONTRACT.read_text(encoding="utf-8")
    notes_text = NOTES.read_text(encoding="utf-8")

    _require(data.get("work_package_id") == "ETF-EU-MVP06", "wrong work package")
    _require(data.get("source_work_package") == "ETF-EU-MVP05", "wrong source work package")
    _require(data.get("source_mvp05_artifact") == str(MVP05), "wrong MVP05 artifact path")
    _require(data.get("eu_sender_entrypoint_path") == str(ENTRYPOINT), "wrong sender entrypoint path")
    _require(data.get("sender_entrypoint_validation_status") == "validated_no_send", "sender status mismatch")

    for key in REQUIRED_TRUE:
        _require(data.get(key) is True, f"expected true for {key}")
    for key in REQUIRED_FALSE:
        _require(data.get(key) is False, f"expected false for {key}")

    _require(data.get("latest_validated_workflow_mode") == "dry_run", "workflow mode mismatch")
    _require(data.get("validate_only_status") == "green", "validate_only mismatch")
    _require(data.get("dry_run_status") == "green", "dry_run mismatch")
    _require(data.get("latest_delivery_manifest") == "output/delivery/etf_eu_delivery_manifest_20260708_142840.json", "delivery manifest mismatch")
    _require(data.get("latest_run_bundle") == "output/runs/20260708_142840/etf_eu_run_bundle_manifest.json", "run bundle mismatch")
    _require(data.get("delivery_manifest_validation") == "passed", "delivery manifest validation mismatch")
    _require(data.get("run_bundle_validation") == "passed", "run bundle validation mismatch")
    _require(data.get("delivery_manifest_status") == "available", "delivery manifest status mismatch")

    sender = data.get("sender_entrypoint_validation")
    _require(isinstance(sender, dict), "missing sender object")
    _require(sender.get("eu_sender_entrypoint_selected_path") == str(ENTRYPOINT), "sender object path mismatch")
    _require(sender.get("sender_entrypoint_validated") is True, "sender object not validated")
    _require(sender.get("preflight_no_send_mode_supported") is True, "preflight unsupported")
    _require(sender.get("dutch_primary_supported") is True, "Dutch primary unsupported")
    _require(sender.get("english_companion_supported") is True, "English companion unsupported")
    _require(sender.get("us_report_name_assumption_detected") is False, "US report-name assumption detected")
    _require(sender.get("send_performed") is False, "sender object send performed")

    guard = data.get("send_guard_decision")
    _require(isinstance(guard, dict), "missing guard object")
    _require(guard.get("workflow_send_guard_present") is True, "guard missing")
    _require(guard.get("workflow_send_guard_removed") is False, "guard removed")
    _require(guard.get("delivery_mode_send_unlocked") is False, "send unlocked")
    _require(guard.get("send_enablement_allowed") is False, "send enablement allowed")

    next_step = data.get("next_step_decision")
    _require(isinstance(next_step, dict), "missing next step object")
    _require(next_step.get("recommended_next_package") == "ETF-EU-MVP07", "wrong next package")
    _require(next_step.get("no_return_to_manual_evidence_route") is True, "manual route return not blocked")
    _require(next_step.get("no_return_to_wp15_gating") is True, "WP15 return not blocked")

    selected = data.get("selected_next_package")
    _require(selected == "ETF-EU-MVP07", "selected next package mismatch")
    _require(not selected.startswith("ETF-EU-WP15"), "must not select WP15")
    _require(selected != "OPERATOR_ACTION_REQUIRED", "must not return to operator action")

    _require("Guard EU send mode until sender entrypoint is promoted" in workflow_text, "workflow guard marker missing")
    _require("ETF_EU_SEND_MODE_REQUESTED" in workflow_text, "workflow send marker missing")
    _require("exit 1" in workflow_text, "workflow guard must remain blocking")

    for marker in CONTRACT_MARKERS:
        _require(marker in contract_text, f"contract missing marker: {marker}")
    for marker in NOTE_MARKERS:
        _require(marker in notes_text, f"notes missing marker: {marker}")

    sender_result = validate_sender(Path("output"))
    _require(sender_result.get("send_performed") is False, "sender validation performed send")
    _require(sender_result.get("delivery_success_claimed") is False, "sender validation claimed success")

    return {
        "status": "valid",
        "work_package_id": data["work_package_id"],
        "eu_sender_entrypoint_created": data["eu_sender_entrypoint_created"],
        "eu_sender_entrypoint_selected": data["eu_sender_entrypoint_selected"],
        "sender_entrypoint_validated": data["sender_entrypoint_validated"],
        "sender_entrypoint_validation_status": data["sender_entrypoint_validation_status"],
        "preflight_no_send_mode_supported": data["preflight_no_send_mode_supported"],
        "dutch_primary_supported": data["dutch_primary_supported"],
        "english_companion_supported": data["english_companion_supported"],
        "us_report_name_assumption_detected": data["us_report_name_assumption_detected"],
        "send_performed": data["send_performed"],
        "delivery_mode_send_unlocked": data["delivery_mode_send_unlocked"],
        "workflow_send_guard_removed": data["workflow_send_guard_removed"],
        "delivery_success_claimed": data["delivery_success_claimed"],
        "selected_next_package": data["selected_next_package"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
