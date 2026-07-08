from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_mvp12_next_decision_package import ARTIFACT, CONTRACT, NOTES, validate


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_expected_files_exist() -> None:
    assert CONTRACT.exists()
    assert ARTIFACT.exists()
    assert NOTES.exists()


def test_artifact_identity_is_correct() -> None:
    data = _artifact()
    assert data["work_package_id"] == "ETF-EU-MVP12"
    assert data["source_work_package"] == "ETF-EU-MVP11"
    assert data["source_mvp11_artifact"] == "output/client_surface/etf_eu_mvp11_workflow_dry_run_verification_with_integrated_evidence_gate_20260708_000000.json"


def test_mvp11_source_evidence_is_correct() -> None:
    data = _artifact()
    assert data["mvp11_workflow_run_id"] == "28963021481"
    assert data["mvp11_workflow_conclusion"] == "success"
    assert data["mvp11_run_mode"] == "dry_run"
    assert data["mvp11_gate_passed"] is True
    assert data["mvp11_guard_step_conclusion"] == "skipped"


def test_decision_framework_flags_are_true() -> None:
    data = _artifact()
    assert data["decision_framework_created"] is True
    assert data["decision_framework_validated"] is True
    assert data["input_state_contract_created"] is True
    assert data["output_contract_created"] is True
    assert data["operational_runbook_created"] is True


def test_selected_next_package_matches_decision_status() -> None:
    data = _artifact()
    if data["decision_status"] == "controlled_send_unlock_ready_for_implementation":
        assert data["selected_next_package"] == "ETF-EU-MVP13"
    elif data["decision_status"] == "additional_hardening_required":
        assert data["selected_next_package"] == "ETF-EU-MVP12A"
    else:
        raise AssertionError("invalid decision status")
    assert not data["selected_next_package"].startswith("ETF-EU-WP15")
    assert data["selected_next_package"] != "OPERATOR_ACTION_REQUIRED"


def test_boundary_flags_are_false() -> None:
    data = _artifact()
    for key in [
        "delivery_mode_send_used",
        "delivery_mode_send_unlocked",
        "workflow_guard_removed",
        "guard_replacement_created",
        "delivery_success",
        "delivery_success_claimed",
        "send_performed",
        "email_delivery",
        "production_delivery",
        "secret_values_exposed",
        "recipient_plaintext_values_exposed",
        "portfolio_mutation",
        "funding_authority",
        "valuation_grade",
    ]:
        assert data[key] is False


def test_decision_objects_are_valid() -> None:
    data = _artifact()
    assert data["decision_basis"]["mvp11_green"] is True
    assert data["decision_basis"]["workflow_run_id"] == "28963021481"
    assert data["decision_basis"]["workflow_conclusion"] == "success"
    assert data["boundary_decision"]["decision_package_only"] is True
    assert data["next_step_decision"]["recommended_next_package"] == data["selected_next_package"]
    assert data["next_step_decision"]["fallback_next_package"] == "ETF-EU-MVP12-FIX"


def test_validator_passes() -> None:
    result = validate()
    assert result["status"] == "valid"
    assert result["work_package_id"] == "ETF-EU-MVP12"
    assert result["decision_status"] == "controlled_send_unlock_ready_for_implementation"
    assert result["selected_next_package"] == "ETF-EU-MVP13"
    assert result["mvp11_workflow_run_id"] == "28963021481"
