from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_mvp10_controlled_send_workflow_integration_or_guard_replacement import (
    ARTIFACT,
    CONTRACT,
    NOTES,
    WORKFLOW_VALIDATOR,
    validate,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_expected_files_exist() -> None:
    assert CONTRACT.exists()
    assert ARTIFACT.exists()
    assert NOTES.exists()
    assert WORKFLOW_VALIDATOR.exists()


def test_artifact_identity_is_correct() -> None:
    data = _artifact()
    assert data["work_package_id"] == "ETF-EU-MVP10"
    assert data["source_work_package"] == "ETF-EU-MVP09"
    assert data["source_mvp09_artifact"] == "output/client_surface/etf_eu_mvp09_controlled_send_implementation_with_delivery_evidence_20260708_000000.json"
    assert data["workflow_file"] == ".github/workflows/send-weekly-etf-eu-report.yml"


def test_workflow_integration_fields_are_correct() -> None:
    data = _artifact()
    assert data["workflow_integration_created"] is True
    assert data["workflow_integration_validated"] is True
    assert data["workflow_integration_type"] == "fixture_validation_gate"
    assert data["guard_replacement_created"] is False
    assert data["existing_workflow_guard_preserved"] is True
    assert data["workflow_send_guard_present"] is True
    assert data["workflow_send_guard_removed"] is False
    assert data["workflow_send_guard_exit_present"] is True
    assert data["delivery_mode_send_unlocked"] is False
    assert data["delivery_evidence_gate_added"] is True
    assert data["delivery_evidence_gate_after_run_bundle"] is True
    assert data["delivery_evidence_validator_called"] is True
    assert data["run_bundle_delivery_evidence_validator_called"] is True
    assert data["mvp09_package_validator_called"] is True


def test_evidence_and_boundary_fields_are_correct() -> None:
    data = _artifact()
    assert data["delivery_evidence_status"] == "not_attempted"
    assert data["recipient_data_policy"] == "redacted_hash_only"
    assert data["required_languages"] == ["nl", "en"]
    for key in [
        "delivery_success",
        "receipt_file_created",
        "delivery_enabled",
        "production_delivery",
        "email_delivery",
        "delivery_receipt",
        "send_performed",
        "send_enablement_allowed",
        "delivery_success_claimed",
        "delivery_success_claim_allowed",
        "secret_values_exposed",
        "recipient_plaintext_values_exposed",
    ]:
        assert data[key] is False


def test_required_nested_objects_are_valid() -> None:
    data = _artifact()
    assert data["workflow_integration_decision"]["workflow_integration_validated"] is True
    assert data["workflow_integration_decision"]["delivery_evidence_gate_after_run_bundle"] is True
    assert data["workflow_integration_decision"]["guard_replacement_created"] is False
    assert data["send_guard_decision"]["existing_workflow_guard_preserved"] is True
    assert data["send_guard_decision"]["workflow_send_guard_removed"] is False
    assert data["send_guard_decision"]["delivery_mode_send_unlocked"] is False
    assert data["failure_handling_decision"]["fail_closed_without_delivery_evidence_gate"] is True
    assert data["failure_handling_decision"]["fail_closed_without_mvp09_validator"] is True
    assert data["next_step_decision"]["recommended_next_package"] == "ETF-EU-MVP11"


def test_next_package_is_mvp11_not_wp15_or_operator_action() -> None:
    data = _artifact()
    assert data["selected_next_package"] == "ETF-EU-MVP11"
    assert not data["selected_next_package"].startswith("ETF-EU-WP15")
    assert data["selected_next_package"] != "OPERATOR_ACTION_REQUIRED"


def test_mvp10_package_validator_passes() -> None:
    result = validate()
    assert result["status"] == "valid"
    assert result["work_package_id"] == "ETF-EU-MVP10"
    assert result["workflow_integration_type"] == "fixture_validation_gate"
    assert result["delivery_evidence_gate_added"] is True
    assert result["delivery_evidence_gate_after_run_bundle"] is True
    assert result["workflow_send_guard_present"] is True
    assert result["workflow_send_guard_removed"] is False
    assert result["delivery_mode_send_unlocked"] is False
    assert result["delivery_evidence_status"] == "not_attempted"
    assert result["delivery_success"] is False
    assert result["delivery_success_claimed"] is False
    assert result["selected_next_package"] == "ETF-EU-MVP11"
