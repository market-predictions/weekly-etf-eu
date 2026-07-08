from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_mvp09_controlled_send_implementation_with_delivery_evidence import validate as validate_mvp09
from tools.validate_etf_eu_mvp10_controlled_send_workflow_integration_or_guard_replacement import validate as validate_mvp10
from tools.validate_etf_eu_mvp11_workflow_dry_run_verification_with_integrated_evidence_gate import validate as validate_mvp11
from tools.validate_etf_eu_mvp12_next_decision_package import validate as validate_mvp12
from tools.validate_etf_eu_mvp13_controlled_send_implementation_preflight import validate as validate_mvp13

CONTRACT = Path("control/ETF_EU_MVP14_GUARDED_CONTROLLED_SEND_IMPLEMENTATION_PLAN_V1.md")
ARTIFACT = Path("output/client_surface/etf_eu_mvp14_guarded_controlled_send_implementation_plan_20260708_000000.json")
NOTES = Path("output/client_surface/etf_eu_mvp14_guarded_controlled_send_implementation_plan_notes_20260708_000000.md")
WORKFLOW = Path(".github/workflows/send-weekly-etf-eu-report.yml")

TRUE_FIELDS = [
    "reference_architecture_used",
    "port_behavior_not_us_assumptions",
    "donor_port_comparison_preserved",
    "mvp13_validator_passed",
    "mvp12_validator_passed",
    "mvp11_validator_passed",
    "mvp10_validator_passed",
    "mvp09_validator_passed",
    "implementation_plan_created",
    "implementation_plan_validated",
    "decision_framework_created",
    "input_state_contract_created",
    "output_contract_created",
    "operational_runbook_created",
    "workflow_delta_plan_created",
    "evidence_contract_plan_created",
    "receipt_semantics_plan_created",
    "delayed_verification_plan_created",
    "rollback_plan_created",
    "workflow_guard_present",
    "workflow_guard_exit_present",
    "workflow_mode_choices_preserved",
    "workflow_validate_only_choice_present",
    "workflow_dry_run_choice_present",
    "workflow_send_choice_present",
    "workflow_evidence_gate_present",
    "workflow_evidence_gate_after_run_bundle",
    "workflow_mvp09_evidence_validators_called",
    "plan_only",
]

FALSE_FIELDS = [
    "us_assumptions_copied",
    "workflow_guard_removed",
    "workflow_behavior_changed",
    "mail_transport_behavior_changed",
    "client_completion_claimed",
    "live_operation_performed",
    "private_values_exposed",
    "plain_contact_values_exposed",
    "portfolio_mutation",
    "funding_authority",
    "valuation_grade",
]

DONOR_DIMENSIONS = [
    "decision_framework",
    "input_state_contract",
    "output_contract",
    "operational_runbook",
    "workflow_guard_pattern",
    "delivery_evidence_pattern",
    "run_bundle_manifest_pattern",
    "validator_chain_pattern",
    "receipt_or_manifest_evidence_pattern",
    "delayed_check_or_post_run_verification_pattern",
    "controlled_send_implementation_plan",
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _validate_workflow() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    for token in ["validate_only", "dry_run", "send"]:
        _require(token in text, f"missing workflow mode token: {token}")
    _require("ETF_EU_SEND_MODE_REQUESTED" in text, "missing guard marker")
    _require("exit 1" in text, "missing guard exit")
    run_bundle_index = text.index("Build and validate run bundle manifest")
    gate_index = text.index("Validate MVP09 delivery evidence integration gate")
    _require(run_bundle_index < gate_index, "evidence gate must follow run bundle step")
    for token in [
        "tools/validate_etf_eu_delivery_evidence.py",
        "tools/validate_etf_eu_run_bundle_delivery_evidence.py",
        "tools/validate_etf_eu_mvp09_controlled_send_implementation_with_delivery_evidence.py",
    ]:
        _require(token in text, f"missing workflow validator call: {token}")


def validate() -> dict[str, Any]:
    for path in [CONTRACT, ARTIFACT, NOTES, WORKFLOW]:
        _require(path.exists(), f"missing file: {path}")
    data = _load(ARTIFACT)

    _require(data.get("work_package_id") == "ETF-EU-MVP14", "wrong work package")
    _require(data.get("source_work_package") == "ETF-EU-MVP13", "wrong source package")
    _require(data.get("reference_architecture_repo") == "market-predictions/weekly-etf", "wrong reference repo")
    _require(data.get("source_of_truth_repo") == "market-predictions/weekly-etf-eu", "wrong source-of-truth repo")
    _require(data.get("mvp13_preflight_status") == "controlled_send_preflight_ready", "wrong MVP13 status")
    _require(data.get("mvp13_selected_next_package") == "ETF-EU-MVP14", "wrong MVP13 next package")
    _require(data.get("mvp11_reference_run_id") == "28963021481", "wrong reference run")
    _require(data.get("mvp11_reference_conclusion") == "success", "wrong reference conclusion")
    _require(data.get("mvp11_reference_mode") == "dry_run", "wrong reference mode")

    for key in TRUE_FIELDS:
        _require(data.get(key) is True, f"expected true for {key}")
    for key in FALSE_FIELDS:
        _require(data.get(key) is False, f"expected false for {key}")

    status = data.get("plan_status")
    selected = data.get("selected_next_package")
    if status == "guarded_plan_ready":
        _require(selected == "ETF-EU-MVP15", "ready plan must select MVP15")
    elif status == "guarded_plan_hardening_required":
        _require(selected == "ETF-EU-MVP14-FIX", "hardening plan must select MVP14-FIX")
    else:
        raise AssertionError("invalid plan status")
    _require(selected != "OPERATOR_ACTION_REQUIRED", "must not select operator action required")
    _require(not selected.startswith("ETF-EU-WP15"), "must not select WP15")

    for obj in ["implementation_preconditions", "evidence_contract_plan", "receipt_semantics_plan", "delayed_verification_plan", "rollback_plan", "boundary_decision", "donor_port_comparison", "next_step_decision"]:
        _require(isinstance(data.get(obj), dict), f"missing object: {obj}")

    preconditions = data["implementation_preconditions"]
    for key in ["manual_activation_required", "push_runs_stay_validate_only", "second_confirmation_required", "all_existing_validators_required", "pre_step_evidence_required", "post_step_evidence_required", "run_bundle_evidence_required", "final_manifest_evidence_required", "plain_recipient_storage_forbidden", "completion_claim_requires_validated_receipt", "transport_result_not_equal_inbox_receipt", "delayed_receipt_check_required", "failure_closes_without_completion_claim", "rollback_to_existing_guard_required"]:
        _require(preconditions.get(key) is True, f"precondition not true: {key}")
    _require(preconditions.get("recipient_policy") == "redacted_hash_only", "recipient policy mismatch")
    _require(preconditions.get("delayed_receipt_check_minutes") == 10, "delay minutes mismatch")

    evidence = data["evidence_contract_plan"]
    _require(evidence.get("language_pair") == ["nl", "en"], "language pair mismatch")
    _require(evidence.get("recipient_policy") == "redacted_hash_only", "evidence recipient policy mismatch")
    _require(evidence.get("recipient_hashes_only") is True, "recipient hashes only missing")
    _require(evidence.get("plain_recipients_allowed") is False, "plain recipients allowed")
    _require(evidence.get("receipt_status_required") is True, "receipt status missing")

    receipt = data["receipt_semantics_plan"]
    _require(receipt.get("transport_layer_evidence_only") is True, "transport evidence flag missing")
    _require(receipt.get("transport_success_not_inbox_receipt") is True, "inbox receipt caveat missing")
    _require(receipt.get("delayed_check_minutes") == 10, "receipt delay mismatch")
    _require(receipt.get("completion_claim_default") is False, "completion default must be false")

    delayed = data["delayed_verification_plan"]
    _require(delayed.get("delayed_check_required") is True, "delayed check missing")
    _require(delayed.get("delay_minutes") == 10, "delayed verification minutes mismatch")
    _require(delayed.get("check_result_must_be_artifact") is True, "delayed artifact missing")

    rollback = data["rollback_plan"]
    _require(rollback.get("rollback_required") is True, "rollback missing")
    _require(rollback.get("rollback_target") == "restore_existing_guard_behavior", "rollback target mismatch")

    boundary = data["boundary_decision"]
    _require(boundary.get("plan_only") is True, "plan_only missing")
    for key in ["workflow_behavior_changed", "mail_transport_behavior_changed", "client_completion_claimed", "live_operation_performed", "private_values_exposed", "plain_contact_values_exposed", "portfolio_mutation", "funding_authority", "valuation_grade"]:
        _require(boundary.get(key) is False, f"boundary expected false for {key}")

    donor = data["donor_port_comparison"]
    for dimension in DONOR_DIMENSIONS:
        entry = donor.get(dimension)
        _require(isinstance(entry, dict), f"missing donor dimension: {dimension}")
        _require(entry.get("reference_source") == "weekly-etf", f"wrong donor source for {dimension}")
        _require(entry.get("eu_source_of_truth") == "weekly-etf-eu", f"wrong EU source for {dimension}")
        _require(entry.get("port_status") in {"ported", "adapted", "not_applicable"}, f"bad port status for {dimension}")
        _require(entry.get("us_assumptions_copied") is False, f"US assumptions copied for {dimension}")

    next_step = data["next_step_decision"]
    _require(next_step.get("recommended_next_package") == selected, "next-step package mismatch")
    _require(next_step.get("fallback_next_package") == "ETF-EU-MVP14-FIX", "fallback mismatch")
    _require(next_step.get("no_execution_in_mvp14") is True, "no execution flag missing")

    _validate_workflow()

    for result, name in [
        (validate_mvp13(), "MVP13"),
        (validate_mvp12(), "MVP12"),
        (validate_mvp11(), "MVP11"),
        (validate_mvp10(), "MVP10"),
        (validate_mvp09(), "MVP09"),
    ]:
        _require(result["status"] == "valid", f"{name} validator failed")

    return {
        "status": "valid",
        "work_package_id": data["work_package_id"],
        "plan_status": status,
        "selected_next_package": selected,
        "reference_architecture_repo": data["reference_architecture_repo"],
        "source_of_truth_repo": data["source_of_truth_repo"],
        "us_assumptions_copied": data["us_assumptions_copied"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
