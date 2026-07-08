from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_delivery_evidence import validate as validate_delivery_evidence
from tools.validate_etf_eu_mvp09_controlled_send_implementation_with_delivery_evidence import validate as validate_mvp09
from tools.validate_etf_eu_mvp10_workflow_delivery_evidence_integration import validate as validate_workflow_integration
from tools.validate_etf_eu_run_bundle_delivery_evidence import validate as validate_run_bundle_evidence

CONTRACT = Path("control/ETF_EU_MVP10_CONTROLLED_SEND_WORKFLOW_INTEGRATION_OR_GUARD_REPLACEMENT_V1.md")
ARTIFACT = Path("output/client_surface/etf_eu_mvp10_controlled_send_workflow_integration_or_guard_replacement_20260708_000000.json")
NOTES = Path("output/client_surface/etf_eu_mvp10_controlled_send_workflow_integration_or_guard_replacement_notes_20260708_000000.md")
WORKFLOW_VALIDATOR = Path("tools/validate_etf_eu_mvp10_workflow_delivery_evidence_integration.py")
EVIDENCE = Path("output/delivery/etf_eu_delivery_evidence_20260708_000000.json")
RUN_BUNDLE_FIXTURE = Path("output/runs/20260708_000000/etf_eu_run_bundle_delivery_evidence_fixture.json")

REQUIRED_TRUE = [
    "workflow_integration_created",
    "workflow_integration_validated",
    "existing_workflow_guard_preserved",
    "workflow_send_guard_present",
    "workflow_send_guard_exit_present",
    "delivery_evidence_gate_added",
    "delivery_evidence_gate_after_run_bundle",
    "delivery_evidence_validator_called",
    "run_bundle_delivery_evidence_validator_called",
    "mvp09_package_validator_called",
    "delivery_evidence_writer_created",
    "delivery_evidence_validator_created",
    "run_bundle_delivery_evidence_validator_created",
    "delivery_evidence_fixture_validated",
    "run_bundle_delivery_evidence_fixture_validated",
    "future_success_status_requires_caveat",
    "final_run_bundle_reference_required",
    "evidence_validator_required",
]

REQUIRED_FALSE = [
    "guard_replacement_created",
    "guard_replacement_validated",
    "workflow_send_guard_removed",
    "delivery_mode_send_unlocked",
    "receipt_file_created",
    "delivery_enabled",
    "production_delivery",
    "email_delivery",
    "pdf_generation",
    "delivery_receipt",
    "send_performed",
    "send_enablement_allowed",
    "delivery_success",
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


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate() -> dict[str, Any]:
    for path in [CONTRACT, ARTIFACT, NOTES, WORKFLOW_VALIDATOR, EVIDENCE, RUN_BUNDLE_FIXTURE]:
        _require(path.exists(), f"missing file: {path}")

    data = _load(ARTIFACT)
    _require(data.get("work_package_id") == "ETF-EU-MVP10", "wrong work package")
    _require(data.get("source_work_package") == "ETF-EU-MVP09", "wrong source package")
    _require(data.get("source_mvp09_artifact") == "output/client_surface/etf_eu_mvp09_controlled_send_implementation_with_delivery_evidence_20260708_000000.json", "MVP09 source path mismatch")
    _require(data.get("workflow_file") == ".github/workflows/send-weekly-etf-eu-report.yml", "workflow file mismatch")
    _require(data.get("workflow_integration_type") == "fixture_validation_gate", "integration type mismatch")
    _require(data.get("delivery_evidence_status") == "not_attempted", "evidence status mismatch")
    _require(data.get("recipient_data_policy") == "redacted_hash_only", "recipient policy mismatch")
    _require(data.get("required_languages") == ["nl", "en"], "required languages mismatch")

    for key in REQUIRED_TRUE:
        _require(data.get(key) is True, f"expected true for {key}")
    for key in REQUIRED_FALSE:
        _require(data.get(key) is False, f"expected false for {key}")

    for obj in ["workflow_integration_decision", "send_guard_decision", "failure_handling_decision", "next_step_decision"]:
        _require(isinstance(data.get(obj), dict), f"missing object: {obj}")

    workflow_decision = data["workflow_integration_decision"]
    _require(workflow_decision.get("delivery_evidence_gate_after_run_bundle") is True, "gate order decision mismatch")
    _require(workflow_decision.get("mvp09_package_validator_called") is True, "MVP09 validator decision mismatch")
    _require(workflow_decision.get("guard_replacement_created") is False, "guard replacement should not be created")

    guard = data["send_guard_decision"]
    _require(guard.get("existing_workflow_guard_preserved") is True, "existing guard not preserved")
    _require(guard.get("workflow_send_guard_removed") is False, "workflow guard removed")
    _require(guard.get("workflow_send_guard_exit_present") is True, "workflow guard exit missing")
    _require(guard.get("delivery_mode_send_unlocked") is False, "protected mode unlocked")
    _require(guard.get("send_enablement_allowed") is False, "send enablement allowed")

    failure = data["failure_handling_decision"]
    for key in [
        "fail_closed_without_delivery_evidence_gate",
        "fail_closed_without_run_bundle_evidence_gate",
        "fail_closed_without_mvp09_validator",
        "fail_closed_if_guard_removed",
        "fail_closed_if_send_mode_unlocked",
        "fail_closed_on_secret_exposure",
        "fail_closed_on_recipient_exposure",
    ]:
        _require(failure.get(key) is True, f"failure rule missing: {key}")
    _require(failure.get("delivery_success") is False, "failure object must not mark success")
    _require(failure.get("delivery_success_claimed") is False, "failure object must not claim success")
    _require(failure.get("delivery_success_claim_allowed") is False, "failure object must not allow success claim")

    selected = data.get("selected_next_package")
    _require(selected == "ETF-EU-MVP11", "selected next package mismatch")
    _require(not selected.startswith("ETF-EU-WP15"), "must not select WP15")
    _require(selected != "OPERATOR_ACTION_REQUIRED", "must not return operator action required")

    workflow_result = validate_workflow_integration()
    evidence_result = validate_delivery_evidence(EVIDENCE)
    run_bundle_result = validate_run_bundle_evidence(RUN_BUNDLE_FIXTURE)
    mvp09_result = validate_mvp09()
    _require(workflow_result["status"] == "valid", "workflow integration validator failed")
    _require(evidence_result["delivery_status"] == "not_attempted", "delivery evidence validator status mismatch")
    _require(run_bundle_result["delivery_evidence_status"] == "not_attempted", "run-bundle evidence validator status mismatch")
    _require(mvp09_result["selected_next_package"] == "ETF-EU-MVP10", "MVP09 regression mismatch")

    return {
        "status": "valid",
        "work_package_id": data["work_package_id"],
        "workflow_integration_type": data["workflow_integration_type"],
        "delivery_evidence_gate_added": data["delivery_evidence_gate_added"],
        "delivery_evidence_gate_after_run_bundle": data["delivery_evidence_gate_after_run_bundle"],
        "workflow_send_guard_present": data["workflow_send_guard_present"],
        "workflow_send_guard_removed": data["workflow_send_guard_removed"],
        "delivery_mode_send_unlocked": data["delivery_mode_send_unlocked"],
        "delivery_evidence_status": data["delivery_evidence_status"],
        "delivery_success": data["delivery_success"],
        "delivery_success_claimed": data["delivery_success_claimed"],
        "selected_next_package": data["selected_next_package"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
