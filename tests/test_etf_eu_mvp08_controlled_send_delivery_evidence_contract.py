from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_mvp08_controlled_send_delivery_evidence_contract import (
    ARTIFACT,
    CONTRACT,
    NOTES,
    validate,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_expected_files_exist() -> None:
    assert CONTRACT.exists()
    assert ARTIFACT.exists()
    assert NOTES.exists()


def test_artifact_identity_and_source_paths_are_correct() -> None:
    data = _artifact()
    assert data["work_package_id"] == "ETF-EU-MVP08"
    assert data["source_work_package"] == "ETF-EU-MVP07"
    assert data["source_mvp07_artifact"] == "output/client_surface/etf_eu_mvp07_manifest_transition_and_controlled_send_preflight_20260708_000000.json"
    assert data["sender_preflight_artifact"] == "output/delivery/etf_eu_sender_preflight_20260708_000000.json"
    assert data["controlled_send_preflight_manifest"] == "output/delivery/etf_eu_controlled_send_preflight_manifest_20260708_000000.json"
    assert data["base_delivery_manifest"] == "output/delivery/etf_eu_delivery_manifest_20260708_142840.json"
    assert data["latest_run_bundle"] == "output/runs/20260708_142840/etf_eu_run_bundle_manifest.json"


def test_delivery_evidence_contract_is_defined_not_executed() -> None:
    data = _artifact()
    assert data["controlled_send_delivery_evidence_contract_created"] is True
    assert data["controlled_send_delivery_evidence_contract_validated"] is True
    assert data["delivery_evidence_status"] == "contract_defined_not_executed"
    assert data["future_delivery_status_values_defined"] is True
    assert data["delivery_status_caveat_required"] is True
    assert "not an end-recipient inbox receipt" in data["delivery_status_caveat_text"]
    assert data["final_run_bundle_reference_required"] is True
    assert data["evidence_validator_required"] is True
    assert data["success_claim_requires_validated_evidence"] is True


def test_recipient_and_language_contract_are_correct() -> None:
    data = _artifact()
    assert data["recipient_redaction_policy_defined"] is True
    assert data["recipient_data_policy"] == "redacted_hash_only"
    assert data["required_languages"] == ["nl", "en"]
    assert data["dutch_primary_language"] == "nl"
    assert data["english_companion_language"] == "en"
    assert data["language_evidence_schema_defined"] is True
    assert data["pdf_evidence_rule_defined"] is True
    language = data["language_evidence_decision"]
    assert language["language_count_required"] == 2
    assert language["required_languages"] == ["nl", "en"]


def test_delivery_execution_boundaries_remain_closed() -> None:
    data = _artifact()
    for key in [
        "receipt_file_created",
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
    ]:
        assert data[key] is False
    assert data["workflow_send_guard_present"] is True


def test_required_nested_objects_are_valid() -> None:
    data = _artifact()
    assert data["delivery_evidence_contract_decision"]["controlled_send_delivery_evidence_contract_validated"] is True
    assert data["recipient_redaction_decision"]["recipient_hash_required"] is True
    assert data["recipient_redaction_decision"]["recipient_redacted_required"] is True
    assert data["failure_handling_decision"]["fail_closed_without_delivery_evidence"] is True
    assert data["failure_handling_decision"]["fail_closed_without_run_bundle_reference"] is True
    assert data["send_guard_decision"]["workflow_send_guard_present"] is True
    assert data["send_guard_decision"]["workflow_send_guard_removed"] is False
    assert data["next_step_decision"]["recommended_next_package"] == "ETF-EU-MVP09"
    assert data["next_step_decision"]["no_return_to_wp15_gating"] is True


def test_next_package_is_mvp09_not_wp15_or_operator_action() -> None:
    data = _artifact()
    assert data["selected_next_package"] == "ETF-EU-MVP09"
    assert not data["selected_next_package"].startswith("ETF-EU-WP15")
    assert data["selected_next_package"] != "OPERATOR_ACTION_REQUIRED"


def test_validator_passes() -> None:
    result = validate()
    assert result["status"] == "valid"
    assert result["work_package_id"] == "ETF-EU-MVP08"
    assert result["delivery_evidence_status"] == "contract_defined_not_executed"
    assert result["recipient_data_policy"] == "redacted_hash_only"
    assert result["required_languages"] == ["nl", "en"]
    assert result["delivery_status_caveat_required"] is True
    assert result["final_run_bundle_reference_required"] is True
    assert result["evidence_validator_required"] is True
    assert result["receipt_file_created"] is False
    assert result["delivery_enabled"] is False
    assert result["send_performed"] is False
    assert result["delivery_mode_send_unlocked"] is False
    assert result["workflow_send_guard_removed"] is False
    assert result["delivery_success_claimed"] is False
    assert result["selected_next_package"] == "ETF-EU-MVP09"
