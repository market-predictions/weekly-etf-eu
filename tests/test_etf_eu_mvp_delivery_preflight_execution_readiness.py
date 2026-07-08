from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_mvp_delivery_preflight_execution_readiness import (
    ARTIFACT,
    NOTES,
    REMAINING_BLOCKERS,
    RUNBOOK,
    validate,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_expected_files_exist() -> None:
    assert RUNBOOK.exists()
    assert ARTIFACT.exists()
    assert NOTES.exists()


def test_artifact_identity_and_sources_are_correct() -> None:
    data = _artifact()
    assert data["work_package_id"] == "ETF-EU-MVP01"
    assert data["source_work_package"] == "ETF-EU-WP15AQ"
    assert data["repository"] == "market-predictions/weekly-etf-eu"
    assert data["source_mvp_evidence_acquisition_plan_artifact"] == "output/client_surface/etf_eu_mvp_delivery_preflight_evidence_acquisition_plan_20260703_000000.json"
    assert data["mvp_delivery_preflight_execution_readiness_path"] == "control/ETF_EU_MVP_DELIVERY_PREFLIGHT_EXECUTION_READINESS_V1.md"


def test_mvp_readiness_flags_are_correct() -> None:
    data = _artifact()
    assert data["mvp_delivery_preflight_execution_readiness_created"] is True
    assert data["mvp_delivery_preflight_execution_readiness_validated"] is True
    assert data["mvp_series_started"] is True
    assert data["no_more_abstract_gates"] is True
    assert data["operator_evidence_required"] is True
    assert data["operator_evidence_present"] is False
    assert data["operator_evidence_status"] == "missing_required_for_execution"


def test_execution_and_success_claim_boundaries_remain_closed() -> None:
    data = _artifact()
    for key in [
        "execution_allowed_now",
        "dry_run_preflight_allowed",
        "delivery_preflight_allowed",
        "send_allowed",
        "production_delivery",
        "manifest_created",
        "receipt_artifact_created",
        "production_manifest_created",
    ]:
        assert data[key] is False
    assert data["manifest_required_for_success_claim"] is True
    assert data["receipt_required_for_delivery_success_claim"] is True


def test_non_authorized_boundaries_remain_false() -> None:
    data = _artifact()
    for key in [
        "recipient_authority_created",
        "transport_authority_created",
        "recipient_config_changed",
        "smtp_or_secret_config_changed",
        "secret_values_exposed",
        "recipient_plaintext_values_exposed",
        "valuation_grade",
        "funding_authority",
        "portfolio_mutation",
        "candidate_promotion",
        "pricing_evidence_for_delivery_preflight",
        "live_price_fetch_performed",
        "live_data_fetch_performed",
        "pricing_evidence_changed",
        "source_pdf_replaced",
        "new_pdf_created",
        "renderer_changed",
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


def test_operator_evidence_checklist_is_missing_by_design() -> None:
    checklist = _artifact()["operator_evidence_checklist"]
    assert checklist["operator_evidence_complete"] is False
    assert checklist["operator_evidence_status"] == "missing_required_for_execution"
    for key in [
        "recipient_set_reference_id_present",
        "recipient_set_hash_present",
        "recipient_owner_approval_reference_present",
        "recipient_rollback_reference_present",
        "transport_reference_id_present",
        "transport_presence_check_reference_present",
        "transport_owner_approval_reference_present",
        "transport_rollback_reference_present",
        "explicit_mvp_preflight_authority_reference_present",
    ]:
        assert checklist[key] is False


def test_execution_readiness_decision_is_valid() -> None:
    decision = _artifact()["execution_readiness_decision"]
    assert decision["decision_status"] == "validated"
    assert decision["decision_result"] == "not_ready_for_execution"
    assert decision["decision_reason"] == "operator_evidence_missing"
    assert decision["required_next_step"] == "operator_evidence_intake"
    assert decision["execution_allowed_now"] is False
    assert decision["dry_run_preflight_allowed"] is False
    assert decision["delivery_preflight_allowed"] is False
    assert decision["send_allowed"] is False
    assert decision["production_delivery"] is False


def test_preflight_and_success_boundaries_are_valid() -> None:
    data = _artifact()
    boundary = data["preflight_execution_boundary"]
    assert boundary["preflight_execution_prepared"] is True
    assert boundary["preflight_execution_performed"] is False
    assert boundary["dry_run_performed"] is False
    assert boundary["send_performed"] is False
    assert boundary["production_delivery"] is False
    assert boundary["execution_boundary_status"] == "prepared_not_executed"
    success = data["success_claim_boundary"]
    assert success["manifest_required_for_success_claim"] is True
    assert success["receipt_required_for_delivery_success_claim"] is True
    assert success["manifest_created"] is False
    assert success["receipt_artifact_created"] is False
    assert success["production_manifest_created"] is False
    assert success["delivery_success_claimed"] is False
    assert success["delivery_success_claim_allowed"] is False


def test_mvp_next_step_is_valid_and_not_wp15() -> None:
    data = _artifact()
    next_step = data["mvp_next_step"]
    assert next_step["mvp_next_step_created"] is True
    assert next_step["mvp_next_step_status"] == "operator_evidence_required"
    assert next_step["recommended_next_package"] == "ETF-EU-MVP02"
    assert next_step["fallback_next_package"] == "ETF-EU-MVP01-FIX"
    assert next_step["no_more_abstract_gates"] is True
    assert data["selected_next_package"] == "ETF-EU-MVP02"
    assert not data["selected_next_package"].startswith("ETF-EU-WP15")


def test_remaining_blockers_are_exact() -> None:
    data = _artifact()
    assert data["remaining_client_grade_blockers"] == []
    assert set(data["remaining_delivery_preflight_blockers"]) == REMAINING_BLOCKERS


def test_notes_contain_required_sections() -> None:
    text = NOTES.read_text(encoding="utf-8")
    for marker in [
        "# ETF-EU-MVP01 MVP delivery-preflight execution readiness",
        "## Scope",
        "## Source artifacts",
        "## Operator evidence status",
        "## Execution readiness decision",
        "## Preflight execution boundary",
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
    assert result["work_package_id"] == "ETF-EU-MVP01"
    assert result["mvp_delivery_preflight_execution_readiness_created"] is True
    assert result["mvp_delivery_preflight_execution_readiness_validated"] is True
    assert result["mvp_series_started"] is True
    assert result["no_more_abstract_gates"] is True
    assert result["operator_evidence_required"] is True
    assert result["operator_evidence_present"] is False
    assert result["execution_allowed_now"] is False
    assert result["dry_run_preflight_allowed"] is False
    assert result["delivery_preflight_allowed"] is False
    assert result["send_allowed"] is False
    assert result["production_delivery"] is False
    assert result["manifest_created"] is False
    assert result["receipt_artifact_created"] is False
    assert result["selected_next_package"] == "ETF-EU-MVP02"
