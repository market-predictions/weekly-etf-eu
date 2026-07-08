from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_mvp07_manifest_transition_and_controlled_send_preflight import (
    ARTIFACT,
    CONTRACT,
    NOTES,
    PREFLIGHT_MANIFEST,
    PREFLIGHT_VALIDATOR,
    SENDER_PREFLIGHT,
    validate,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_expected_files_exist() -> None:
    assert CONTRACT.exists()
    assert ARTIFACT.exists()
    assert NOTES.exists()
    assert SENDER_PREFLIGHT.exists()
    assert PREFLIGHT_MANIFEST.exists()
    assert PREFLIGHT_VALIDATOR.exists()


def test_artifact_identity_and_paths_are_correct() -> None:
    data = _artifact()
    assert data["work_package_id"] == "ETF-EU-MVP07"
    assert data["source_work_package"] == "ETF-EU-MVP06"
    assert data["sender_preflight_artifact"] == "output/delivery/etf_eu_sender_preflight_20260708_000000.json"
    assert data["controlled_send_preflight_manifest"] == "output/delivery/etf_eu_controlled_send_preflight_manifest_20260708_000000.json"
    assert data["base_delivery_manifest"] == "output/delivery/etf_eu_delivery_manifest_20260708_142840.json"
    assert data["latest_run_bundle"] == "output/runs/20260708_142840/etf_eu_run_bundle_manifest.json"


def test_manifest_transition_and_receipt_boundary_are_correct() -> None:
    data = _artifact()
    assert data["manifest_transition_status"] == "ready_for_future_delivery"
    assert data["controlled_send_preflight_status"] == "ready_for_future_delivery"
    assert data["receipt_path_reserved"] is True
    assert data["receipt_file_created"] is False
    assert data["receipt_status"] == "pending"
    transition = data["manifest_transition_decision"]
    assert transition["base_manifest_status"] == "blocked_design_only"
    assert transition["target_preflight_status"] == "ready_for_future_delivery"
    assert transition["delivery_enabled"] is False
    assert transition["receipt_file_created"] is False
    assert transition["delivery_authority_created"] is False


def test_send_and_delivery_boundaries_remain_closed() -> None:
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
    guard = data["send_guard_decision"]
    assert guard["workflow_send_guard_present"] is True
    assert guard["workflow_send_guard_removed"] is False
    assert guard["delivery_mode_send_unlocked"] is False
    assert guard["send_enablement_allowed"] is False
    receipt = data["receipt_and_success_boundary"]
    assert receipt["receipt_path_reserved"] is True
    assert receipt["receipt_file_created"] is False
    assert receipt["delivery_success_claimed"] is False
    assert receipt["delivery_success_claim_allowed"] is False
    next_step = data["next_step_decision"]
    assert next_step["recommended_next_package"] == "ETF-EU-MVP08"
    assert next_step["no_return_to_wp15_gating"] is True


def test_next_package_is_mvp08_not_wp15_or_operator_action() -> None:
    data = _artifact()
    assert data["selected_next_package"] == "ETF-EU-MVP08"
    assert not data["selected_next_package"].startswith("ETF-EU-WP15")
    assert data["selected_next_package"] != "OPERATOR_ACTION_REQUIRED"


def test_validator_passes() -> None:
    result = validate()
    assert result["status"] == "valid"
    assert result["work_package_id"] == "ETF-EU-MVP07"
    assert result["manifest_transition_status"] == "ready_for_future_delivery"
    assert result["controlled_send_preflight_status"] == "ready_for_future_delivery"
    assert result["receipt_path_reserved"] is True
    assert result["receipt_file_created"] is False
    assert result["receipt_status"] == "pending"
    assert result["delivery_enabled"] is False
    assert result["send_performed"] is False
    assert result["delivery_mode_send_unlocked"] is False
    assert result["workflow_send_guard_removed"] is False
    assert result["delivery_success_claimed"] is False
    assert result["selected_next_package"] == "ETF-EU-MVP08"
