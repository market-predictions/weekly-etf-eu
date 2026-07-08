from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_mvp_operator_evidence_intake_and_dry_run import (
    ARTIFACT,
    INTAKE,
    NOTES,
    REMAINING_BLOCKERS,
    TEMPLATE,
    validate,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_expected_files_exist() -> None:
    assert INTAKE.exists()
    assert TEMPLATE.exists()
    assert ARTIFACT.exists()
    assert NOTES.exists()


def test_artifact_identity_and_sources_are_correct() -> None:
    data = _artifact()
    assert data["work_package_id"] == "ETF-EU-MVP02"
    assert data["source_work_package"] == "ETF-EU-MVP01"
    assert data["repository"] == "market-predictions/weekly-etf-eu"
    assert data["source_mvp_execution_readiness_artifact"] == "output/client_surface/etf_eu_mvp_delivery_preflight_execution_readiness_20260703_000000.json"
    assert data["operator_evidence_intake_path"] == "control/ETF_EU_MVP_OPERATOR_EVIDENCE_INTAKE_AND_DRY_RUN_V1.md"
    assert data["operator_evidence_reference_template_path"] == "control/runtime_reference_templates/ETF_EU_MVP_OPERATOR_EVIDENCE_REFERENCE_TEMPLATE.md"


def test_intake_and_mvp_flags_are_correct() -> None:
    data = _artifact()
    assert data["operator_evidence_intake_created"] is True
    assert data["operator_evidence_intake_validated"] is True
    assert data["mvp_series_continued"] is True
    assert data["no_more_abstract_gates"] is True
    assert data["operator_evidence_required"] is True
    assert data["operator_evidence_present"] is False
    assert data["operator_evidence_complete"] is False
    assert data["operator_evidence_status"] == "missing_required_for_dry_run"


def test_execution_and_delivery_outputs_remain_closed() -> None:
    data = _artifact()
    for key in [
        "dry_run_preflight_allowed",
        "dry_run_preflight_performed",
        "delivery_preflight_allowed",
        "execution_allowed_now",
        "send_allowed",
        "production_delivery",
        "dry_run_manifest_created",
        "manifest_created",
        "receipt_artifact_created",
        "production_manifest_created",
        "delivery_success_claimed",
        "delivery_success_claim_allowed",
        "recipient_authority_created",
        "transport_authority_created",
        "recipient_config_changed",
        "smtp_or_secret_config_changed",
        "secret_values_exposed",
        "recipient_plaintext_values_exposed",
    ]:
        assert data[key] is False


def test_source_values_remain_fixed() -> None:
    data = _artifact()
    assert data["successful_rows_count"] == 2
    assert data["failed_rows_count"] == 0
    assert data["skipped_rows_count"] == 1
    assert data["first_successful_symbol"] == "SXR8.DE"
    assert data["first_successful_close_date"] == "2026-07-03"
    assert data["first_successful_close"] == 706.119995
    assert data["second_successful_symbol"] == "CSPX.L"
    assert data["second_successful_close_date"] == "2026-07-03"
    assert data["second_successful_close"] == 807.859985
    assert data["smh_status"] == "skipped_pending_registry_status"


def test_required_objects_and_next_step_are_valid() -> None:
    data = _artifact()
    assert data["operator_evidence_intake_checklist"]["operator_evidence_status"] == "missing_required_for_dry_run"
    assert data["dry_run_eligibility_decision"]["decision_result"] == "not_eligible_for_dry_run"
    assert data["dry_run_execution_boundary"]["execution_boundary_status"] == "intake_created_not_executed"
    assert data["success_claim_boundary"]["delivery_success_claimed"] is False
    assert data["mvp_next_step"]["recommended_next_package"] == "ETF-EU-MVP03"
    assert data["selected_next_package"] == "ETF-EU-MVP03"
    assert not data["selected_next_package"].startswith("ETF-EU-WP15")


def test_remaining_blockers_and_template_are_valid() -> None:
    data = _artifact()
    assert data["remaining_client_grade_blockers"] == []
    assert set(data["remaining_delivery_preflight_blockers"]) == REMAINING_BLOCKERS
    template = TEMPLATE.read_text(encoding="utf-8")
    assert "<operator supplied reference>" in template
    assert "<operator supplied hash>" in template
    assert "Use references and hashes only." in template


def test_notes_contain_required_sections() -> None:
    text = NOTES.read_text(encoding="utf-8")
    for marker in [
        "# ETF-EU-MVP02 operator evidence intake and delivery-preflight dry-run",
        "## Scope",
        "## Source artifacts",
        "## Operator evidence intake",
        "## Dry-run eligibility decision",
        "## Dry-run execution boundary",
        "## Success claim boundary",
        "## Remaining client-grade blockers",
        "## Remaining delivery-preflight blockers",
        "## Boundary checks",
        "## Decision",
        "## Next package",
    ]:
        assert marker in text


def test_validator_passes() -> None:
    result = validate()
    assert result["status"] == "valid"
    assert result["work_package_id"] == "ETF-EU-MVP02"
    assert result["operator_evidence_intake_created"] is True
    assert result["operator_evidence_intake_validated"] is True
    assert result["mvp_series_continued"] is True
    assert result["no_more_abstract_gates"] is True
    assert result["operator_evidence_present"] is False
    assert result["dry_run_preflight_allowed"] is False
    assert result["send_allowed"] is False
    assert result["production_delivery"] is False
    assert result["delivery_success_claimed"] is False
    assert result["selected_next_package"] == "ETF-EU-MVP03"
