from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_mvp05_sender_entrypoint_validation_and_controlled_send_enablement import (
    ARTIFACT,
    CONTRACT,
    LATEST_DELIVERY_MANIFEST,
    LATEST_RUN_BUNDLE,
    NOTES,
    WORKFLOW,
    validate,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_expected_files_exist() -> None:
    assert CONTRACT.exists()
    assert ARTIFACT.exists()
    assert NOTES.exists()
    assert WORKFLOW.exists()


def test_artifact_identity_and_dry_run_evidence_are_correct() -> None:
    data = _artifact()
    assert data["work_package_id"] == "ETF-EU-MVP05"
    assert data["source_work_package"] == "ETF-EU-MVP04-FIX-VALIDATE-ONLY-02"
    assert data["latest_validated_workflow_mode"] == "dry_run"
    assert data["validate_only_status"] == "green"
    assert data["dry_run_status"] == "green"
    assert data["latest_delivery_manifest"] == LATEST_DELIVERY_MANIFEST
    assert data["latest_run_bundle"] == LATEST_RUN_BUNDLE
    assert data["delivery_manifest_validation"] == "passed"
    assert data["run_bundle_validation"] == "passed"
    assert data["delivery_manifest_status"] == "available"


def test_send_and_success_boundaries_remain_closed() -> None:
    data = _artifact()
    for key in [
        "delivery_enabled",
        "production_delivery",
        "email_delivery",
        "pdf_generation",
        "delivery_receipt",
        "sender_entrypoint_validated",
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


def test_sender_entrypoint_objects_are_present() -> None:
    data = _artifact()
    sender = data["sender_entrypoint_validation"]
    assert sender["sender_entrypoint_inventory_created"] is True
    assert sender["sender_entrypoint_candidates"] == ["send_report_runtime_html.py", "send_report.py"]
    assert sender["eu_sender_entrypoint_selected"] is False
    assert sender["sender_entrypoint_validated"] is False
    guard = data["send_guard_decision"]
    assert guard["workflow_send_guard_present"] is True
    assert guard["workflow_send_guard_removed"] is False
    assert guard["delivery_mode_send_unlocked"] is False
    assert guard["send_enablement_allowed"] is False


def test_manifest_and_receipt_boundaries_are_present() -> None:
    data = _artifact()
    manifest = data["manifest_transition_decision"]
    assert manifest["delivery_manifest_framework_exists"] is True
    assert manifest["run_bundle_manifest_framework_exists"] is True
    assert manifest["current_delivery_manifest_status"] == "available"
    assert manifest["manifest_transition_validated"] is False
    receipt = data["receipt_and_success_boundary"]
    assert receipt["receipt_required_for_delivery_success_claim"] is True
    assert receipt["delivery_receipt"] is False
    assert receipt["delivery_success_claimed"] is False
    assert receipt["delivery_success_claim_allowed"] is False


def test_next_package_is_mvp06_not_wp15_or_operator_action_required() -> None:
    data = _artifact()
    assert data["next_step_decision"]["recommended_next_package"] == "ETF-EU-MVP06"
    assert data["selected_next_package"] == "ETF-EU-MVP06"
    assert not data["selected_next_package"].startswith("ETF-EU-WP15")
    assert data["selected_next_package"] != "OPERATOR_ACTION_REQUIRED"


def test_validator_passes() -> None:
    result = validate()
    assert result["status"] == "valid"
    assert result["work_package_id"] == "ETF-EU-MVP05"
    assert result["latest_validated_workflow_mode"] == "dry_run"
    assert result["validate_only_status"] == "green"
    assert result["dry_run_status"] == "green"
    assert result["sender_entrypoint_validation_created"] is True
    assert result["sender_entrypoint_validated"] is False
    assert result["send_enablement_allowed"] is False
    assert result["delivery_mode_send_unlocked"] is False
    assert result["workflow_send_guard_present"] is True
    assert result["workflow_send_guard_removed"] is False
    assert result["production_delivery"] is False
    assert result["email_delivery"] is False
    assert result["delivery_receipt"] is False
    assert result["delivery_success_claimed"] is False
    assert result["selected_next_package"] == "ETF-EU-MVP06"
