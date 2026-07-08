from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_mvp15_guarded_controlled_send_implementation import (
    ARTIFACT,
    CONTRACT,
    DONOR_DIMENSIONS,
    NOTES,
    RECEIPT,
    WORKFLOW,
    WRITER,
    validate,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_expected_files_exist() -> None:
    assert CONTRACT.exists()
    assert ARTIFACT.exists()
    assert NOTES.exists()
    assert WORKFLOW.exists()
    assert WRITER.exists()
    assert RECEIPT.exists()


def test_artifact_identity_and_source_package() -> None:
    data = _artifact()
    assert data["work_package_id"] == "ETF-EU-MVP15"
    assert data["source_work_package"] == "ETF-EU-MVP14"
    assert data["source_mvp14_artifact"] == "output/client_surface/etf_eu_mvp14_guarded_controlled_send_implementation_plan_20260708_000000.json"


def test_reference_architecture_fields() -> None:
    data = _artifact()
    assert data["reference_architecture_repo"] == "market-predictions/weekly-etf"
    assert data["source_of_truth_repo"] == "market-predictions/weekly-etf-eu"
    assert data["reference_architecture_used"] is True
    assert data["port_behavior_not_us_assumptions"] is True
    assert data["us_assumptions_copied"] is False


def test_mvp14_and_reference_evidence() -> None:
    data = _artifact()
    assert data["mvp14_plan_status"] == "guarded_plan_ready"
    assert data["mvp14_selected_next_package"] == "ETF-EU-MVP15"
    assert data["mvp11_reference_run_id"] == "28963021481"
    assert data["mvp11_reference_conclusion"] == "success"
    assert data["mvp11_reference_mode"] == "dry_run"


def test_workflow_confirmation_gate_present() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "send_confirmation" in text
    assert "not_confirmed" in text
    assert "confirm_guarded_send" in text
    assert "ETF_EU_SEND_CONFIRMATION_MISSING" in text
    assert "ETF_EU_GUARDED_SEND_CONFIRMATION_OK" in text
    assert "MODE=\"validate_only\"" in text
    assert "CONFIRMATION=\"not_confirmed\"" in text


def test_workflow_guarded_placeholder_is_isolated_after_validators() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "Build and validate run bundle manifest" in text
    assert "Validate MVP09 delivery evidence integration gate" in text
    assert "MVP15 guarded transport placeholder" in text
    assert text.index("Build and validate run bundle manifest") < text.index("Validate MVP09 delivery evidence integration gate")
    assert text.index("Validate MVP09 delivery evidence integration gate") < text.index("MVP15 guarded transport placeholder")
    assert "runtime.write_etf_eu_delivery_evidence" in text
    assert "--stage pre" in text
    assert "--stage post" in text
    assert "runtime.check_etf_eu_delivery_receipt" in text


def test_workflow_fields_in_artifact_are_valid() -> None:
    data = _artifact()
    for key in [
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
    ]:
        assert data[key] is True


def test_helpers_and_evidence_contract_are_valid() -> None:
    data = _artifact()
    assert data["pre_step_evidence_writer_created"] is True
    assert data["post_step_evidence_writer_created"] is True
    assert data["evidence_schema_extended"] is True
    assert data["receipt_check_helper_created"] is True
    assert data["delayed_check_supported"] is True
    assert data["rollback_rule_created"] is True
    evidence = data["evidence_contract"]
    assert evidence["language_pair"] == ["nl", "en"]
    assert evidence["recipient_policy"] == "redacted_hash_only"
    assert evidence["recipient_hashes_only"] is True
    assert evidence["plain_contacts_allowed"] is False
    assert evidence["receipt_status_required"] is True


def test_confirmation_receipt_delayed_and_rollback_objects_are_valid() -> None:
    data = _artifact()
    gate = data["confirmation_gate"]
    assert gate["mode_requires_confirmation"] is True
    assert gate["confirmation_input_name"] == "send_confirmation"
    assert gate["confirmation_required_value"] == "confirm_guarded_send"
    assert gate["confirmation_default"] == "not_confirmed"
    receipt = data["receipt_semantics"]
    assert receipt["operation_result_not_inbox_receipt"] is True
    assert receipt["completion_claim_default"] is False
    assert receipt["completion_claim_requires_receipt_confirmed"] is True
    delayed = data["delayed_verification"]
    assert delayed["delayed_check_supported"] is True
    assert delayed["delay_minutes"] == 10
    assert delayed["check_result_must_be_artifact"] is True
    rollback = data["rollback_plan"]
    assert rollback["rollback_supported"] is True
    assert rollback["rollback_if_validator_fails"] is True
    assert rollback["rollback_if_evidence_missing"] is True


def test_boundary_flags_are_false() -> None:
    data = _artifact()
    for key in [
        "plain_contact_values_exposed",
        "private_values_exposed",
        "guarded_operation_performed",
        "guarded_mode_run_performed",
        "completion_claimed",
        "receipt_confirmed",
        "portfolio_mutation",
        "funding_authority",
        "valuation_grade",
    ]:
        assert data[key] is False
    boundary = data["boundary_decision"]
    assert boundary["implementation_only"] is True
    for key in [
        "guarded_operation_performed",
        "guarded_mode_run_performed",
        "completion_claimed",
        "receipt_confirmed",
        "private_values_exposed",
        "plain_contact_values_exposed",
        "portfolio_mutation",
        "funding_authority",
        "valuation_grade",
        "us_assumptions_copied",
    ]:
        assert boundary[key] is False


def test_donor_port_comparison_is_valid() -> None:
    data = _artifact()
    donor = data["donor_port_comparison"]
    for dimension in DONOR_DIMENSIONS:
        assert donor[dimension]["reference_source"] == "weekly-etf"
        assert donor[dimension]["eu_source_of_truth"] == "weekly-etf-eu"
        assert donor[dimension]["port_status"] in {"ported", "adapted", "not_applicable"}
        assert donor[dimension]["us_assumptions_copied"] is False


def test_selected_next_package_is_valid() -> None:
    data = _artifact()
    assert data["implementation_status"] in {"guarded_static_implementation_green", "guarded_static_implementation_hardening_required"}
    if data["implementation_status"] == "guarded_static_implementation_green":
        assert data["selected_next_package"] == "ETF-EU-MVP16"
    else:
        assert data["selected_next_package"] == "ETF-EU-MVP15-FIX"
    assert not data["selected_next_package"].startswith("ETF-EU-WP15")
    assert data["selected_next_package"] != "OPERATOR_ACTION_REQUIRED"


def test_validator_passes() -> None:
    result = validate()
    assert result["status"] == "valid"
    assert result["work_package_id"] == "ETF-EU-MVP15"
    assert result["implementation_status"] == "guarded_static_implementation_green"
    assert result["selected_next_package"] == "ETF-EU-MVP16"
    assert result["reference_architecture_repo"] == "market-predictions/weekly-etf"
    assert result["source_of_truth_repo"] == "market-predictions/weekly-etf-eu"
    assert result["us_assumptions_copied"] is False
