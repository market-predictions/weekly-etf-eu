from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_mvp04_fix_weekly_etf_delivery_rolemodel_alignment import (
    ARTIFACT,
    CONTRACT,
    NOTES,
    SECRET_NAMES,
    WORKFLOW,
    validate,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_expected_files_exist() -> None:
    assert WORKFLOW.exists()
    assert CONTRACT.exists()
    assert ARTIFACT.exists()
    assert NOTES.exists()


def test_artifact_identity_and_manual_route_superseded() -> None:
    data = _artifact()
    assert data["work_package_id"] == "ETF-EU-MVP04-FIX"
    assert data["source_work_package"] == "ETF-EU-MVP04"
    assert data["manual_evidence_route_superseded"] is True
    assert data["operator_reference_template_required_for_delivery"] is False
    assert data["operator_hash_requirement_removed"] is True
    assert data["operator_action_required"] is False


def test_workflow_delivery_modes_are_declared() -> None:
    data = _artifact()
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert data["workflow_delivery_mode_input_created"] is True
    assert data["delivery_mode_default"] == "validate_only"
    assert set(data["delivery_mode_options"]) == {"validate_only", "dry_run", "send"}
    assert "delivery_mode:" in workflow
    assert "default: \"validate_only\"" in workflow
    assert "- validate_only" in workflow
    assert "- dry_run" in workflow
    assert "- send" in workflow
    assert "ETF_EU_DELIVERY_MODE" in workflow


def test_rolemodel_secret_names_are_declared_without_exposure() -> None:
    data = _artifact()
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert data["rolemodel_secret_names_declared"] is True
    for name in SECRET_NAMES:
        assert name in workflow
        assert name in data["rolemodel_secret_names"]
    assert data["secret_values_exposed"] is False
    assert data["recipient_plaintext_values_exposed"] is False


def test_send_and_delivery_boundaries_are_closed() -> None:
    data = _artifact()
    assert data["send_mode_declared"] is True
    assert data["send_mode_blocked_until_eu_sender_validated"] is True
    assert data["production_delivery"] is False
    assert data["send_performed"] is False
    assert data["email_delivery"] is False
    assert data["delivery_success_claimed"] is False
    assert data["delivery_success_claim_allowed"] is False
    assert data["manifest_required_for_success_claim"] is True


def test_next_step_is_workflow_run_not_mvp05_or_wp15() -> None:
    data = _artifact()
    assert data["selected_next_package"] == "RUN_WORKFLOW_VALIDATE_ONLY_OR_DRY_RUN"
    assert data["selected_next_package_is_mvp05"] is False
    assert data["selected_next_package_is_wp15"] is False
    assert not data["selected_next_package"].startswith("ETF-EU-MVP05")
    assert not data["selected_next_package"].startswith("ETF-EU-WP15")


def test_validator_passes() -> None:
    result = validate()
    assert result["status"] == "valid"
    assert result["work_package_id"] == "ETF-EU-MVP04-FIX"
    assert result["manual_evidence_route_superseded"] is True
    assert result["workflow_delivery_mode_input_created"] is True
    assert result["delivery_mode_default"] == "validate_only"
    assert result["dry_run_mode_declared"] is True
    assert result["send_mode_declared"] is True
    assert result["send_mode_blocked_until_eu_sender_validated"] is True
    assert result["rolemodel_secret_names_declared"] is True
    assert result["operator_action_required"] is False
    assert result["selected_next_package"] == "RUN_WORKFLOW_VALIDATE_ONLY_OR_DRY_RUN"
