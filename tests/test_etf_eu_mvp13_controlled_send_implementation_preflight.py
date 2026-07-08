from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_mvp13_controlled_send_implementation_preflight import (
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
    assert data["work_package_id"] == "ETF-EU-MVP13"
    assert data["source_work_package"] == "ETF-EU-MVP12"
    assert data["source_mvp12_artifact"] == "output/client_surface/etf_eu_mvp12_next_decision_package_20260708_000000.json"


def test_reference_architecture_fields() -> None:
    data = _artifact()
    assert data["reference_architecture_repo"] == "market-predictions/weekly-etf"
    assert data["source_of_truth_repo"] == "market-predictions/weekly-etf-eu"
    assert data["reference_architecture_used"] is True
    assert data["port_behavior_not_us_assumptions"] is True
    assert data["us_assumptions_copied"] is False
    assert data["donor_port_comparison_created"] is True
    assert data["donor_port_comparison_validated"] is True


def test_mvp12_and_mvp11_evidence_present() -> None:
    data = _artifact()
    assert data["mvp12_selected_next_package"] == "ETF-EU-MVP13"
    assert data["mvp11_workflow_run_id"] == "28963021481"
    assert data["mvp11_workflow_conclusion"] == "success"
    assert data["mvp11_run_mode"] == "dry_run"
    assert data["mvp11_gate_passed"] is True


def test_preflight_framework_flags_are_true() -> None:
    data = _artifact()
    for key in [
        "preflight_contract_created",
        "preflight_contract_validated",
        "decision_framework_created",
        "input_state_contract_created",
        "output_contract_created",
        "operational_runbook_created",
        "mvp12_validator_passed",
        "mvp11_validator_passed",
        "mvp10_validator_passed",
        "mvp09_validator_passed",
    ]:
        assert data[key] is True


def test_workflow_preflight_fields_are_valid() -> None:
    data = _artifact()
    assert data["workflow_guard_present"] is True
    assert data["workflow_guard_removed"] is False
    assert data["workflow_guard_exit_present"] is True
    assert data["workflow_mode_choices_preserved"] is True
    assert data["workflow_validate_only_choice_present"] is True
    assert data["workflow_dry_run_choice_present"] is True
    assert data["workflow_send_choice_present"] is True
    assert data["workflow_evidence_gate_present"] is True
    assert data["workflow_evidence_gate_after_run_bundle"] is True
    assert data["workflow_mvp09_evidence_validators_called"] is True


def test_preflight_status_and_next_package() -> None:
    data = _artifact()
    assert data["preflight_status"] in {"controlled_send_preflight_ready", "preflight_hardening_required"}
    if data["preflight_status"] == "controlled_send_preflight_ready":
        assert data["selected_next_package"] == "ETF-EU-MVP14"
    else:
        assert data["selected_next_package"] == "ETF-EU-MVP13-FIX"
    assert not data["selected_next_package"].startswith("ETF-EU-WP15")
    assert data["selected_next_package"] != "OPERATOR_ACTION_REQUIRED"


def test_boundary_flags_are_false() -> None:
    data = _artifact()
    for key in [
        "live_mode_used",
        "live_mode_unlocked",
        "workflow_guard_removed",
        "client_completion_claimed",
        "live_transport_performed",
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
    assert preconditions["mvp12_green"] is True
    assert preconditions["mvp11_green"] is True
    assert preconditions["mvp10_green"] is True
    assert preconditions["mvp09_green"] is True
    assert preconditions["workflow_guard_present"] is True
    assert preconditions["workflow_guard_exit_present"] is True
    assert preconditions["workflow_evidence_gate_present"] is True
    assert preconditions["workflow_evidence_gate_after_run_bundle"] is True
    assert preconditions["recipient_policy"] == "redacted_hash_only"
    assert preconditions["language_pair"] == ["nl", "en"]


def test_donor_port_comparison_is_valid() -> None:
    data = _artifact()
    donor = data["donor_port_comparison"]
    for dimension in DONOR_DIMENSIONS:
        assert donor[dimension]["reference_source"] == "weekly-etf"
        assert donor[dimension]["eu_source_of_truth"] == "weekly-etf-eu"
        assert donor[dimension]["port_status"] in {"ported", "adapted", "not_applicable"}
        assert donor[dimension]["us_assumptions_copied"] is False


def test_decision_objects_are_valid() -> None:
    data = _artifact()
    assert data["boundary_decision"]["preflight_only"] is True
    assert data["next_step_decision"]["recommended_next_package"] == data["selected_next_package"]
    assert data["next_step_decision"]["fallback_next_package"] == "ETF-EU-MVP13-FIX"
    assert data["next_step_decision"]["no_execution_in_mvp13"] is True


def test_validator_passes() -> None:
    result = validate()
    assert result["status"] == "valid"
    assert result["work_package_id"] == "ETF-EU-MVP13"
    assert result["preflight_status"] == "controlled_send_preflight_ready"
    assert result["selected_next_package"] == "ETF-EU-MVP14"
    assert result["reference_architecture_repo"] == "market-predictions/weekly-etf"
    assert result["source_of_truth_repo"] == "market-predictions/weekly-etf-eu"
    assert result["us_assumptions_copied"] is False
