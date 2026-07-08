from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_mvp06_sender_entrypoint_implementation_or_validation import (
    ARTIFACT,
    CONTRACT,
    ENTRYPOINT,
    NOTES,
    SENDER_VALIDATOR,
    validate,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_expected_files_exist() -> None:
    assert CONTRACT.exists()
    assert ARTIFACT.exists()
    assert NOTES.exists()
    assert ENTRYPOINT.exists()
    assert SENDER_VALIDATOR.exists()


def test_artifact_identity_and_sender_status_are_correct() -> None:
    data = _artifact()
    assert data["work_package_id"] == "ETF-EU-MVP06"
    assert data["source_work_package"] == "ETF-EU-MVP05"
    assert data["eu_sender_entrypoint_path"] == "runtime/send_etf_eu_report_runtime_html.py"
    assert data["eu_sender_entrypoint_created"] is True
    assert data["eu_sender_entrypoint_selected"] is True
    assert data["sender_entrypoint_validated"] is True
    assert data["sender_entrypoint_validation_status"] == "validated_no_send"
    assert data["preflight_no_send_mode_supported"] is True
    assert data["dutch_primary_supported"] is True
    assert data["english_companion_supported"] is True
    assert data["us_report_name_assumption_detected"] is False
    assert data["non_canonical_artifacts_ignored"] is True


def test_dry_run_evidence_is_preserved() -> None:
    data = _artifact()
    assert data["latest_validated_workflow_mode"] == "dry_run"
    assert data["validate_only_status"] == "green"
    assert data["dry_run_status"] == "green"
    assert data["latest_delivery_manifest"] == "output/delivery/etf_eu_delivery_manifest_20260708_142840.json"
    assert data["latest_run_bundle"] == "output/runs/20260708_142840/etf_eu_run_bundle_manifest.json"
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
    sender = data["sender_entrypoint_validation"]
    assert sender["eu_sender_entrypoint_selected_path"] == "runtime/send_etf_eu_report_runtime_html.py"
    assert sender["sender_entrypoint_validated"] is True
    assert sender["preflight_no_send_mode_supported"] is True
    assert sender["us_report_name_assumption_detected"] is False
    guard = data["send_guard_decision"]
    assert guard["workflow_send_guard_present"] is True
    assert guard["workflow_send_guard_removed"] is False
    assert guard["delivery_mode_send_unlocked"] is False
    assert guard["send_enablement_allowed"] is False
    next_step = data["next_step_decision"]
    assert next_step["recommended_next_package"] == "ETF-EU-MVP07"
    assert next_step["no_return_to_wp15_gating"] is True


def test_next_package_is_mvp07_not_wp15_or_operator_action() -> None:
    data = _artifact()
    assert data["selected_next_package"] == "ETF-EU-MVP07"
    assert not data["selected_next_package"].startswith("ETF-EU-WP15")
    assert data["selected_next_package"] != "OPERATOR_ACTION_REQUIRED"


def test_validator_passes() -> None:
    result = validate()
    assert result["status"] == "valid"
    assert result["work_package_id"] == "ETF-EU-MVP06"
    assert result["eu_sender_entrypoint_created"] is True
    assert result["sender_entrypoint_validated"] is True
    assert result["preflight_no_send_mode_supported"] is True
    assert result["dutch_primary_supported"] is True
    assert result["english_companion_supported"] is True
    assert result["us_report_name_assumption_detected"] is False
    assert result["send_performed"] is False
    assert result["delivery_mode_send_unlocked"] is False
    assert result["workflow_send_guard_removed"] is False
    assert result["delivery_success_claimed"] is False
    assert result["selected_next_package"] == "ETF-EU-MVP07"
