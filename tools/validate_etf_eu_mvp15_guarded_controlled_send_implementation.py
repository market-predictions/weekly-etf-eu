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
from tools.validate_etf_eu_mvp14_guarded_controlled_send_implementation_plan import validate as validate_mvp14

CONTRACT = Path("control/ETF_EU_MVP15_GUARDED_CONTROLLED_SEND_IMPLEMENTATION_V1.md")
ARTIFACT = Path("output/client_surface/etf_eu_mvp15_guarded_controlled_send_implementation_20260708_000000.json")
NOTES = Path("output/client_surface/etf_eu_mvp15_guarded_controlled_send_implementation_notes_20260708_000000.md")
WORKFLOW = Path(".github/workflows/send-weekly-etf-eu-report.yml")
WRITER = Path("runtime/write_etf_eu_delivery_evidence.py")
RECEIPT = Path("runtime/check_etf_eu_delivery_receipt.py")

TRUE_FIELDS = [
    "reference_architecture_used",
    "port_behavior_not_us_assumptions",
    "mvp14_validator_passed",
    "mvp13_validator_passed",
    "mvp12_validator_passed",
    "mvp11_validator_passed",
    "mvp10_validator_passed",
    "mvp09_validator_passed",
    "workflow_updated",
    "workflow_behavior_changed",
    "workflow_mode_choices_preserved",
    "workflow_validate_only_choice_present",
    "workflow_dry_run_choice_present",
    "workflow_send_choice_present",
    "workflow_confirmation_input_present",
    "workflow_confirmation_default_not_confirmed",
    "workflow_guarded_path_requires_confirmation",
    "workflow_push_runs_validate_only",
    "workflow_validators_before_guarded_placeholder",
    "workflow_evidence_gate_before_guarded_placeholder",
    "workflow_run_bundle_before_evidence_gate",
    "workflow_guarded_placeholder_isolated",
    "workflow_guarded_placeholder_not_run_in_mvp15",
    "pre_step_evidence_writer_created",
    "post_step_evidence_writer_created",
    "evidence_schema_extended",
    "receipt_check_helper_created",
    "delayed_check_supported",
    "rollback_rule_created",
    "plain_contact_storage_forbidden",
]

FALSE_FIELDS = [
    "us_assumptions_copied",
    "plain_contact_values_exposed",
    "private_values_exposed",
    "guarded_operation_performed",
    "guarded_mode_run_performed",
    "completion_claimed",
    "receipt_confirmed",
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
    "controlled_send_implementation",
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
    for token in ["send_confirmation", "not_confirmed", "confirm_guarded_send"]:
        _require(token in text, f"missing confirmation token: {token}")
    _require("ETF_EU_SEND_MODE_REQUESTED" in text, "missing guarded mode marker")
    _require("ETF_EU_SEND_CONFIRMATION" in text, "missing confirmation env")
    _require("ETF_EU_SEND_CONFIRMATION_MISSING" in text, "missing missing-confirmation block")
    _require("ETF_EU_GUARDED_SEND_CONFIRMATION_OK" in text, "missing confirmation ok marker")
    _require("MODE=\"validate_only\"" in text, "push runs must force validate_only")
    _require("CONFIRMATION=\"not_confirmed\"" in text, "push runs must force not_confirmed")
    _require("MVP15 guarded transport placeholder" in text, "missing isolated guarded placeholder")
    _require("ETF_EU_MVP15_TRANSPORT_PLACEHOLDER" in text, "missing placeholder marker")
    _require("runtime.write_etf_eu_delivery_evidence" in text, "missing evidence writer call")
    _require("--stage pre" in text, "missing pre evidence stage")
    _require("--stage post" in text, "missing post evidence stage")
    _require("runtime.check_etf_eu_delivery_receipt" in text, "missing receipt helper call")
    run_bundle_index = text.index("Build and validate run bundle manifest")
    gate_index = text.index("Validate MVP09 delivery evidence integration gate")
    placeholder_index = text.index("MVP15 guarded transport placeholder")
    _require(run_bundle_index < gate_index < placeholder_index, "run bundle and evidence gate must precede placeholder")
    _require("tools/validate_etf_eu_delivery_evidence.py" in text, "missing delivery evidence validator call")
    _require("tools/validate_etf_eu_run_bundle_delivery_evidence.py" in text, "missing run bundle delivery evidence validator call")
    _require("tools/validate_etf_eu_mvp09_controlled_send_implementation_with_delivery_evidence.py" in text, "missing MVP09 validator call")


def _validate_helpers() -> None:
    writer = WRITER.read_text(encoding="utf-8")
    receipt = RECEIPT.read_text(encoding="utf-8")
    for token in ["attempt_pending", "transport_succeeded_unconfirmed", "receipt_not_found_after_delay", "--mvp15-static", "--stage"]:
        _require(token in writer, f"missing writer token: {token}")
    for token in ["etf_eu_delivery_receipt_check_v1", "delay_minutes", "receipt_confirmed", "receipt_not_found_after_delay", "mvp15_static"]:
        _require(token in receipt, f"missing receipt helper token: {token}")


def validate() -> dict[str, Any]:
    for path in [CONTRACT, ARTIFACT, NOTES, WORKFLOW, WRITER, RECEIPT]:
        _require(path.exists(), f"missing file: {path}")
    data = _load(ARTIFACT)

    _require(data.get("work_package_id") == "ETF-EU-MVP15", "wrong work package")
    _require(data.get("source_work_package") == "ETF-EU-MVP14", "wrong source package")
    _require(data.get("reference_architecture_repo") == "market-predictions/weekly-etf", "wrong reference repo")
    _require(data.get("source_of_truth_repo") == "market-predictions/weekly-etf-eu", "wrong source-of-truth repo")
    _require(data.get("mvp14_plan_status") == "guarded_plan_ready", "wrong MVP14 plan status")
    _require(data.get("mvp14_selected_next_package") == "ETF-EU-MVP15", "wrong MVP14 next package")
    _require(data.get("mvp11_reference_run_id") == "28963021481", "wrong reference run")
    _require(data.get("mvp11_reference_conclusion") == "success", "wrong reference conclusion")
    _require(data.get("mvp11_reference_mode") == "dry_run", "wrong reference mode")

    for key in TRUE_FIELDS:
        _require(data.get(key) is True, f"expected true for {key}")
    for key in FALSE_FIELDS:
        _require(data.get(key) is False, f"expected false for {key}")
    _require(data.get("recipient_policy") == "redacted_hash_only", "recipient policy mismatch")
    _require(data.get("receipt_status") == "not_attempted", "receipt status mismatch")

    status = data.get("implementation_status")
    selected = data.get("selected_next_package")
    if status == "guarded_static_implementation_green":
        _require(selected == "ETF-EU-MVP16", "green implementation must select MVP16")
    elif status == "guarded_static_implementation_hardening_required":
        _require(selected == "ETF-EU-MVP15-FIX", "hardening implementation must select MVP15-FIX")
    else:
        raise AssertionError("invalid implementation status")
    _require(selected != "OPERATOR_ACTION_REQUIRED", "must not select operator action required")
    _require(not selected.startswith("ETF-EU-WP15"), "must not select WP15")

    for obj in ["confirmation_gate", "evidence_contract", "receipt_semantics", "delayed_verification", "rollback_plan", "boundary_decision", "donor_port_comparison", "next_step_decision"]:
        _require(isinstance(data.get(obj), dict), f"missing object: {obj}")

    gate = data["confirmation_gate"]
    _require(gate.get("mode_requires_confirmation") is True, "confirmation rule missing")
    _require(gate.get("confirmation_input_name") == "send_confirmation", "confirmation input mismatch")
    _require(gate.get("confirmation_required_value") == "confirm_guarded_send", "confirmation value mismatch")
    _require(gate.get("confirmation_default") == "not_confirmed", "confirmation default mismatch")
    _require(gate.get("missing_confirmation_blocks_before_guarded_placeholder") is True, "missing block rule")
    _require(gate.get("push_runs_cannot_use_guarded_path") is True, "push guard missing")

    evidence = data["evidence_contract"]
    for key in ["pre_step_evidence_required", "post_step_evidence_required", "evidence_path_required", "run_bundle_links_evidence", "final_manifest_links_evidence", "workflow_run_id_required", "workflow_job_id_required", "commit_sha_required", "run_id_required", "report_paths_required", "recipient_hashes_only", "operation_result_required", "receipt_status_required"]:
        _require(evidence.get(key) is True, f"evidence contract expected true: {key}")
    _require(evidence.get("language_pair") == ["nl", "en"], "language pair mismatch")
    _require(evidence.get("recipient_policy") == "redacted_hash_only", "evidence recipient policy mismatch")
    _require(evidence.get("plain_contacts_allowed") is False, "plain contacts allowed")

    receipt = data["receipt_semantics"]
    _require(receipt.get("operation_result_not_inbox_receipt") is True, "receipt caveat missing")
    _require(receipt.get("completion_claim_default") is False, "completion default mismatch")
    _require(receipt.get("completion_claim_requires_receipt_confirmed") is True, "completion receipt rule missing")
    _require(receipt.get("receipt_confirmation_requires_external_check") is True, "external check missing")

    delayed = data["delayed_verification"]
    _require(delayed.get("delayed_check_supported") is True, "delayed check unsupported")
    _require(delayed.get("delay_minutes") == 10, "delay minutes mismatch")
    _require(delayed.get("check_result_must_be_artifact") is True, "check artifact missing")

    rollback = data["rollback_plan"]
    _require(rollback.get("rollback_supported") is True, "rollback unsupported")
    _require(rollback.get("rollback_target") == "restore_mvp14_guarded_plan_or_prior_guard", "rollback target mismatch")

    boundary = data["boundary_decision"]
    _require(boundary.get("implementation_only") is True, "implementation_only missing")
    for key in ["guarded_operation_performed", "guarded_mode_run_performed", "completion_claimed", "receipt_confirmed", "private_values_exposed", "plain_contact_values_exposed", "portfolio_mutation", "funding_authority", "valuation_grade", "us_assumptions_copied"]:
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
    _require(next_step.get("recommended_next_package") == selected, "next step selected mismatch")
    _require(next_step.get("fallback_next_package") == "ETF-EU-MVP15-FIX", "fallback mismatch")
    _require(next_step.get("no_guarded_operation_in_mvp15") is True, "no operation flag missing")

    _validate_workflow()
    _validate_helpers()

    for result, name in [
        (validate_mvp14(), "MVP14"),
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
        "implementation_status": status,
        "selected_next_package": selected,
        "reference_architecture_repo": data["reference_architecture_repo"],
        "source_of_truth_repo": data["source_of_truth_repo"],
        "us_assumptions_copied": data["us_assumptions_copied"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
