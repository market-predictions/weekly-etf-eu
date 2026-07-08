from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_mvp14_guarded_controlled_send_implementation_plan import (
    ARTIFACT,
    CONTRACT,
    DONOR_DIMENSIONS,
    NOTES,
    validate,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_expected_files_exist() -> None:
    assert CONTRACT.exists()
    assert ARTIFACT.exists()
    assert NOTES.exists()


def test_artifact_identity_and_source_package() -> None:
    data = _artifact()
    assert data["work_package_id"] == "ETF-EU-MVP14"
    assert data["source_work_package"] == "ETF-EU-MVP13"
    assert data["source_mvp13_artifact"] == "output/client_surface/etf_eu_mvp13_controlled_send_implementation_preflight_20260708_000000.json"


def test_reference_architecture_fields() -> None:
    data = _artifact()
    assert data["reference_architecture_repo"] == "market-predictions/weekly-etf"
    assert data["source_of_truth_repo"] == "market-predictions/weekly-etf-eu"
    assert data["reference_architecture_used"] is True
    assert data["port_behavior_not_us_assumptions"] is True
    assert data["us_assumptions_copied"] is False
    assert data["donor_port_comparison_preserved"] is True


def test_mvp13_and_reference_evidence() -> None:
    data = _artifact()
    assert data["mvp13_preflight_status"] == "controlled_send_preflight_ready"
    assert data["mvp13_selected_next_package"] == "ETF-EU-MVP14"
    assert data["mvp11_reference_run_id"] == "28963021481"
    assert data["mvp11_reference_conclusion"] == "success"
    assert data["mvp11_reference_mode"] == "dry_run"


def test_plan_flags_are_true() -> None:
    data = _artifact()
    for key in [
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
        "mvp13_validator_passed",
        "mvp12_validator_passed",
        "mvp11_validator_passed",
        "mvp10_validator_passed",
        "mvp09_validator_passed",
    ]:
        assert data[key] is True


def test_workflow_fields_are_valid() -> None:
    data = _artifact()
    assert data["workflow_guard_present"] is True
    assert data["workflow_guard_exit_present"] is True
    assert data["workflow_guard_removed"] is False
    assert data["workflow_mode_choices_preserved"] is True
    assert data["workflow_validate_only_choice_present"] is True
    assert data["workflow_dry_run_choice_present"] is True
    assert data["workflow_send_choice_present"] is True
    assert data["workflow_evidence_gate_present"] is True
    assert data["workflow_evidence_gate_after_run_bundle"] is True
    assert data["workflow_mvp09_evidence_validators_called"] is True


def test_plan_status_and_next_package() -> None:
    data = _artifact()
    assert data["plan_status"] in {"guarded_plan_ready", "guarded_plan_hardening_required"}
    if data["plan_status"] == "guarded_plan_ready":
        assert data["selected_next_package"] == "ETF-EU-MVP15"
    else:
        assert data["selected_next_package"] == "ETF-EU-MVP14-FIX"
    assert not data["selected_next_package"].startswith("ETF-EU-WP15")
    assert data["selected_next_package"] != "OPERATOR_ACTION_REQUIRED"


def test_boundary_flags_are_false() -> None:
    data = _artifact()
    for key in [
        "workflow_behavior_changed",
        "mail_transport_behavior_changed",
        "client_completion_claimed",
        "live_operation_performed",
        "private_values_exposed",
        "plain_contact_values_exposed",
        "portfolio_mutation",
        "funding_authority",
        "valuation_grade",
    ]:
        assert data[key] is False


def test_implementation_preconditions_are_valid() -> None:
    data = _artifact()
    preconditions = data["implementation_preconditions"]
    assert preconditions["manual_activation_required"] is True
    assert preconditions["push_runs_stay_validate_only"] is True
    assert preconditions["second_confirmation_required"] is True
    assert preconditions["all_existing_validators_required"] is True
    assert preconditions["pre_step_evidence_required"] is True
    assert preconditions["post_step_evidence_required"] is True
    assert preconditions["run_bundle_evidence_required"] is True
    assert preconditions["final_manifest_evidence_required"] is True
    assert preconditions["recipient_policy"] == "redacted_hash_only"
    assert preconditions["plain_recipient_storage_forbidden"] is True
    assert preconditions["completion_claim_requires_validated_receipt"] is True
    assert preconditions["delayed_receipt_check_required"] is True
    assert preconditions["delayed_receipt_check_minutes"] == 10


def test_evidence_and_receipt_plans_are_valid() -> None:
    data = _artifact()
    evidence = data["evidence_contract_plan"]
    assert evidence["language_pair"] == ["nl", "en"]
    assert evidence["recipient_policy"] == "redacted_hash_only"
    assert evidence["recipient_hashes_only"] is True
    assert evidence["plain_recipients_allowed"] is False
    assert evidence["receipt_status_required"] is True
    receipt = data["receipt_semantics_plan"]
    assert receipt["transport_layer_evidence_only"] is True
    assert receipt["transport_success_not_inbox_receipt"] is True
    assert receipt["receipt_confirmation_requires_external_check"] is True
    assert receipt["delayed_check_required"] is True
    assert receipt["delayed_check_minutes"] == 10
    assert receipt["completion_claim_default"] is False


def test_delayed_and_rollback_plans_are_valid() -> None:
    data = _artifact()
    delayed = data["delayed_verification_plan"]
    assert delayed["delayed_check_required"] is True
    assert delayed["delay_minutes"] == 10
    assert delayed["check_result_must_be_artifact"] is True
    rollback = data["rollback_plan"]
    assert rollback["rollback_required"] is True
    assert rollback["rollback_target"] == "restore_existing_guard_behavior"
    assert rollback["rollback_if_validator_fails"] is True
    assert rollback["rollback_if_evidence_missing"] is True


def test_boundary_donor_and_next_step_objects_are_valid() -> None:
    data = _artifact()
    assert data["boundary_decision"]["plan_only"] is True
    assert data["boundary_decision"]["workflow_behavior_changed"] is False
    donor = data["donor_port_comparison"]
    for dimension in DONOR_DIMENSIONS:
        assert donor[dimension]["reference_source"] == "weekly-etf"
        assert donor[dimension]["eu_source_of_truth"] == "weekly-etf-eu"
        assert donor[dimension]["port_status"] in {"ported", "adapted", "not_applicable"}
        assert donor[dimension]["us_assumptions_copied"] is False
    assert data["next_step_decision"]["recommended_next_package"] == data["selected_next_package"]
    assert data["next_step_decision"]["fallback_next_package"] == "ETF-EU-MVP14-FIX"
    assert data["next_step_decision"]["no_execution_in_mvp14"] is True


def test_validator_passes() -> None:
    result = validate()
    assert result["status"] == "valid"
    assert result["work_package_id"] == "ETF-EU-MVP14"
    assert result["plan_status"] == "guarded_plan_ready"
    assert result["selected_next_package"] == "ETF-EU-MVP15"
    assert result["reference_architecture_repo"] == "market-predictions/weekly-etf"
    assert result["source_of_truth_repo"] == "market-predictions/weekly-etf-eu"
    assert result["us_assumptions_copied"] is False
