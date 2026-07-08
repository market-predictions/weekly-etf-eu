from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_mvp09_controlled_send_implementation_with_delivery_evidence import (
    ARTIFACT,
    CONTRACT,
    EVIDENCE_FIXTURE,
    EVIDENCE_VALIDATOR,
    NOTES,
    RUN_BUNDLE_FIXTURE,
    RUN_BUNDLE_VALIDATOR,
    WRITER,
    validate,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_expected_files_exist() -> None:
    assert CONTRACT.exists()
    assert ARTIFACT.exists()
    assert NOTES.exists()
    assert WRITER.exists()
    assert EVIDENCE_VALIDATOR.exists()
    assert RUN_BUNDLE_VALIDATOR.exists()
    assert EVIDENCE_FIXTURE.exists()
    assert RUN_BUNDLE_FIXTURE.exists()


def test_artifact_identity_is_correct() -> None:
    data = _artifact()
    assert data["work_package_id"] == "ETF-EU-MVP09"
    assert data["source_work_package"] == "ETF-EU-MVP08"
    assert data["source_mvp08_artifact"] == "output/client_surface/etf_eu_mvp08_controlled_send_delivery_evidence_contract_20260708_000000.json"
    assert data["delivery_evidence_path"] == "output/delivery/etf_eu_delivery_evidence_20260708_000000.json"
    assert data["run_bundle_delivery_evidence_fixture"] == "output/runs/20260708_000000/etf_eu_run_bundle_delivery_evidence_fixture.json"


def test_delivery_evidence_implementation_flags_are_correct() -> None:
    data = _artifact()
    assert data["delivery_evidence_writer_created"] is True
    assert data["delivery_evidence_validator_created"] is True
    assert data["run_bundle_delivery_evidence_validator_created"] is True
    assert data["delivery_evidence_fixture_created"] is True
    assert data["delivery_evidence_fixture_validated"] is True
    assert data["run_bundle_delivery_evidence_fixture_created"] is True
    assert data["run_bundle_delivery_evidence_fixture_validated"] is True
    assert data["delivery_evidence_status"] == "not_attempted"
    assert data["recipient_data_policy"] == "redacted_hash_only"
    assert data["required_languages"] == ["nl", "en"]
    assert data["future_success_status_supported"] is True
    assert data["future_success_status_requires_caveat"] is True


def test_execution_boundaries_remain_closed() -> None:
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
        "delivery_success",
        "delivery_success_claimed",
        "delivery_success_claim_allowed",
        "secret_values_exposed",
        "recipient_plaintext_values_exposed",
    ]:
        assert data[key] is False
    assert data["workflow_send_guard_present"] is True


def test_required_nested_objects_are_valid() -> None:
    data = _artifact()
    implementation = data["delivery_evidence_implementation_decision"]
    assert implementation["delivery_evidence_writer_created"] is True
    assert implementation["delivery_evidence_validator_created"] is True
    assert implementation["delivery_evidence_status"] == "not_attempted"
    assert implementation["delivery_success"] is False
    run_bundle = data["run_bundle_reference_decision"]
    assert run_bundle["run_bundle_delivery_evidence_validator_created"] is True
    assert run_bundle["run_bundle_delivery_evidence_fixture_validated"] is True
    assert run_bundle["delivery_success"] is False
    guard = data["send_guard_decision"]
    assert guard["workflow_send_guard_present"] is True
    assert guard["workflow_send_guard_removed"] is False
    assert guard["delivery_mode_send_unlocked"] is False
    assert guard["send_enablement_allowed"] is False


def test_next_package_is_mvp10_not_wp15_or_operator_action() -> None:
    data = _artifact()
    assert data["selected_next_package"] == "ETF-EU-MVP10"
    assert not data["selected_next_package"].startswith("ETF-EU-WP15")
    assert data["selected_next_package"] != "OPERATOR_ACTION_REQUIRED"


def test_validator_passes() -> None:
    result = validate()
    assert result["status"] == "valid"
    assert result["work_package_id"] == "ETF-EU-MVP09"
    assert result["delivery_evidence_status"] == "not_attempted"
    assert result["recipient_data_policy"] == "redacted_hash_only"
    assert result["required_languages"] == ["nl", "en"]
    assert result["delivery_success"] is False
    assert result["delivery_enabled"] is False
    assert result["send_performed"] is False
    assert result["delivery_mode_send_unlocked"] is False
    assert result["workflow_send_guard_removed"] is False
    assert result["delivery_success_claimed"] is False
    assert result["selected_next_package"] == "ETF-EU-MVP10"
