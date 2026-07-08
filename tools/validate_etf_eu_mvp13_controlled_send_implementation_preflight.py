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

CONTRACT = Path("control/ETF_EU_MVP13_CONTROLLED_SEND_IMPLEMENTATION_PREFLIGHT_V1.md")
ARTIFACT = Path("output/client_surface/etf_eu_mvp13_controlled_send_implementation_preflight_20260708_000000.json")
NOTES = Path("output/client_surface/etf_eu_mvp13_controlled_send_implementation_preflight_notes_20260708_000000.md")
WORKFLOW = Path(".github/workflows/send-weekly-etf-eu-report.yml")

REQUIRED_TRUE = [
    "reference_architecture_used",
    "port_behavior_not_us_assumptions",
    "donor_port_comparison_created",
    "donor_port_comparison_validated",
    "preflight_contract_created",
    "preflight_contract_validated",
    "decision_framework_created",
    "input_state_contract_created",
    "output_contract_created",
    "operational_runbook_created",
    "mvp11_gate_passed",
    "mvp12_validator_passed",
    "mvp11_validator_passed",
    "mvp10_validator_passed",
    "mvp09_validator_passed",
    "workflow_guard_present",
    "workflow_guard_exit_present",
    "workflow_mode_choices_preserved",
    "workflow_validate_only_choice_present",
    "workflow_dry_run_choice_present",
    "workflow_send_choice_present",
    "workflow_evidence_gate_present",
    "workflow_evidence_gate_after_run_bundle",
    "workflow_mvp09_evidence_validators_called",
]

REQUIRED_FALSE = [
    "us_assumptions_copied",
    "workflow_guard_removed",
    "live_mode_used",
    "live_mode_unlocked",
    "client_completion_claimed",
    "live_transport_performed",
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

    _require(data.get("work_package_id") == "ETF-EU-MVP13", "wrong work package")
    _require(data.get("source_work_package") == "ETF-EU-MVP12", "wrong source package")
    _require(data.get("reference_architecture_repo") == "market-predictions/weekly-etf", "wrong reference repo")
    _require(data.get("source_of_truth_repo") == "market-predictions/weekly-etf-eu", "wrong source-of-truth repo")
    _require(data.get("mvp12_selected_next_package") == "ETF-EU-MVP13", "MVP12 selected package mismatch")
    _require(data.get("mvp11_workflow_run_id") == "28963021481", "MVP11 run id mismatch")
    _require(data.get("mvp11_workflow_conclusion") == "success", "MVP11 conclusion mismatch")
    _require(data.get("mvp11_run_mode") == "dry_run", "MVP11 mode mismatch")

    for key in REQUIRED_TRUE:
        _require(data.get(key) is True, f"expected true for {key}")
    for key in REQUIRED_FALSE:
        _require(data.get(key) is False, f"expected false for {key}")

    status = data.get("preflight_status")
    selected = data.get("selected_next_package")
    if status == "controlled_send_preflight_ready":
        _require(selected == "ETF-EU-MVP14", "ready status must select MVP14")
    elif status == "preflight_hardening_required":
        _require(selected == "ETF-EU-MVP13-FIX", "hardening status must select MVP13-FIX")
    else:
        raise AssertionError("invalid preflight status")
    _require(selected != "OPERATOR_ACTION_REQUIRED", "must not select operator action required")
    _require(not selected.startswith("ETF-EU-WP15"), "must not select WP15")

    donor = data.get("donor_port_comparison")
    _require(isinstance(donor, dict), "missing donor comparison")
    for dimension in DONOR_DIMENSIONS:
        entry = donor.get(dimension)
        _require(isinstance(entry, dict), f"missing donor dimension: {dimension}")
        _require(entry.get("reference_source") == "weekly-etf", f"wrong donor source for {dimension}")
        _require(entry.get("eu_source_of_truth") == "weekly-etf-eu", f"wrong EU source for {dimension}")
        _require(entry.get("port_status") in {"ported", "adapted", "not_applicable"}, f"bad port status for {dimension}")
        _require(entry.get("us_assumptions_copied") is False, f"US assumptions copied for {dimension}")

    for obj in ["implementation_preconditions", "boundary_decision", "next_step_decision"]:
        _require(isinstance(data.get(obj), dict), f"missing object: {obj}")
    preconditions = data["implementation_preconditions"]
    for key in ["mvp12_green", "mvp11_green", "mvp10_green", "mvp09_green", "workflow_guard_present", "workflow_guard_exit_present", "workflow_evidence_gate_present", "workflow_evidence_gate_after_run_bundle"]:
        _require(preconditions.get(key) is True, f"precondition not true: {key}")
    _require(preconditions.get("recipient_policy") == "redacted_hash_only", "recipient policy mismatch")
    _require(preconditions.get("language_pair") == ["nl", "en"], "language pair mismatch")

    boundary = data["boundary_decision"]
    _require(boundary.get("preflight_only") is True, "preflight_only missing")
    for key in ["live_mode_used", "live_mode_unlocked", "workflow_guard_removed", "client_completion_claimed", "live_transport_performed", "private_values_exposed", "plain_contact_values_exposed", "portfolio_mutation", "funding_authority", "valuation_grade"]:
        _require(boundary.get(key) is False, f"boundary expected false for {key}")

    next_step = data["next_step_decision"]
    _require(next_step.get("recommended_next_package") == selected, "next step selected mismatch")
    _require(next_step.get("fallback_next_package") == "ETF-EU-MVP13-FIX", "fallback mismatch")
    _require(next_step.get("no_execution_in_mvp13") is True, "no execution flag missing")

    _validate_workflow()

    for result, name in [
        (validate_mvp12(), "MVP12"),
        (validate_mvp11(), "MVP11"),
        (validate_mvp10(), "MVP10"),
        (validate_mvp09(), "MVP09"),
    ]:
        _require(result["status"] == "valid", f"{name} validator failed")

    return {
        "status": "valid",
        "work_package_id": data["work_package_id"],
        "preflight_status": status,
        "selected_next_package": selected,
        "reference_architecture_repo": data["reference_architecture_repo"],
        "source_of_truth_repo": data["source_of_truth_repo"],
        "us_assumptions_copied": data["us_assumptions_copied"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
