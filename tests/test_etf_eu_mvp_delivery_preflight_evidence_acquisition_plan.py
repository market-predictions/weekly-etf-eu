from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_mvp_delivery_preflight_evidence_acquisition_plan import (
    ARTIFACT,
    NOTES,
    PLAN,
    REMAINING_BLOCKERS,
    validate,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_expected_files_exist() -> None:
    assert PLAN.exists()
    assert ARTIFACT.exists()
    assert NOTES.exists()


def test_artifact_identity_and_sources_are_correct() -> None:
    data = _artifact()
    assert data["work_package_id"] == "ETF-EU-WP15AQ"
    assert data["source_work_package"] == "ETF-EU-WP15AP"
    assert data["repository"] == "market-predictions/weekly-etf-eu"
    assert data["source_recipient_transport_authority_decision_artifact"] == "output/client_surface/etf_eu_recipient_transport_authority_decision_20260703_000000.json"
    assert data["mvp_evidence_acquisition_plan_path"] == "control/ETF_EU_MVP_DELIVERY_PREFLIGHT_EVIDENCE_ACQUISITION_PLAN_V1.md"


def test_mvp_handoff_flags_are_true() -> None:
    data = _artifact()
    assert data["mvp_evidence_acquisition_plan_created"] is True
    assert data["mvp_evidence_acquisition_plan_validated"] is True
    assert data["final_evidence_plan_before_mvp_execution"] is True
    assert data["stop_recursive_gating"] is True
    assert data["selected_next_package"] == "ETF-EU-MVP01"


def test_mvp_handoff_object_is_valid() -> None:
    handoff = _artifact()["mvp_handoff"]
    assert handoff["mvp_handoff_created"] is True
    assert handoff["mvp_handoff_status"] == "ready_for_evidence_collection_not_execution"
    assert handoff["next_package_type"] == "mvp_delivery_preflight_execution"
    assert handoff["recommended_next_package"] == "ETF-EU-MVP01"
    assert handoff["fallback_next_package"] == "ETF-EU-WP15AQ-FIX"
    assert handoff["no_more_abstract_gates"] is True
    assert handoff["execution_allowed_now"] is False
    assert handoff["requires_operator_evidence_before_execution"] is True


def test_non_authorized_boundaries_remain_false() -> None:
    data = _artifact()
    for key in [
        "delivery_ready",
        "delivery_preflight_authority_created",
        "delivery_preflight_allowed",
        "outbound_path_enabled",
        "production_delivery",
        "receipt_artifact_created",
        "production_manifest_created",
        "recipient_config_changed",
        "smtp_or_secret_config_changed",
        "recipient_authority_created",
        "transport_authority_created",
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


def test_required_evidence_fields_are_present() -> None:
    evidence = _artifact()["evidence_required"]
    for key in [
        "recipient_set_reference_id_required",
        "recipient_set_hash_required",
        "recipient_owner_approval_reference_required",
        "recipient_rollback_reference_required",
        "transport_reference_id_required",
        "transport_presence_check_reference_required",
        "transport_owner_approval_reference_required",
        "transport_rollback_reference_required",
        "explicit_mvp_preflight_authority_reference_required",
    ]:
        assert evidence[key] is True
    assert evidence["secret_values_allowed"] is False
    assert evidence["plaintext_recipient_values_allowed"] is False


def test_evidence_acquisition_objects_are_missing_by_design() -> None:
    data = _artifact()
    recipient = data["recipient_evidence_acquisition"]
    transport = data["transport_evidence_acquisition"]
    approval = data["approval_evidence_acquisition"]
    rollback = data["rollback_evidence_acquisition"]
    assert recipient["recipient_evidence_status"] == "missing_required_for_mvp_execution"
    assert recipient["recipient_set_reference_id_present"] is False
    assert recipient["recipient_set_hash_present"] is False
    assert recipient["recipient_authority_created"] is False
    assert transport["transport_evidence_status"] == "missing_required_for_mvp_execution"
    assert transport["transport_reference_id_present"] is False
    assert transport["transport_presence_check_reference_present"] is False
    assert transport["transport_authority_created"] is False
    assert approval["approval_status"] == "missing_required_for_mvp_execution"
    assert approval["explicit_mvp_preflight_authority_reference_present"] is False
    assert rollback["rollback_status"] == "missing_required_for_mvp_execution"


def test_remaining_blockers_are_exact() -> None:
    data = _artifact()
    assert data["remaining_client_grade_blockers"] == []
    assert set(data["remaining_delivery_preflight_blockers"]) == REMAINING_BLOCKERS


def test_source_manifest_supports_mvp_handoff() -> None:
    manifest = _artifact()["source_manifest"]
    assert manifest
    used = " ".join(" ".join(source["used_for_fields"]) for source in manifest)
    for required in ["final evidence acquisition plan", "mvp handoff", "stop recursive gating", "delivery-preflight blocker preservation"]:
        assert required in used


def test_notes_contain_required_sections() -> None:
    text = NOTES.read_text(encoding="utf-8")
    for marker in [
        "# ETF-EU-WP15AQ MVP delivery-preflight evidence acquisition plan",
        "## Scope",
        "## Source artifacts",
        "## Evidence required",
        "## Recipient evidence acquisition",
        "## Transport evidence acquisition",
        "## Approval evidence acquisition",
        "## Rollback evidence acquisition",
        "## MVP handoff",
        "## Stop recursive gating",
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
    assert result["work_package_id"] == "ETF-EU-WP15AQ"
    assert result["mvp_evidence_acquisition_plan_created"] is True
    assert result["mvp_evidence_acquisition_plan_validated"] is True
    assert result["final_evidence_plan_before_mvp_execution"] is True
    assert result["stop_recursive_gating"] is True
    assert result["no_more_abstract_gates"] is True
    assert result["execution_allowed_now"] is False
    assert result["recommended_next_package"] == "ETF-EU-MVP01"
    assert result["recipient_authority_created"] is False
    assert result["transport_authority_created"] is False
    assert result["delivery_preflight_allowed"] is False
    assert result["production_delivery"] is False
    assert result["remaining_delivery_preflight_blockers_count"] == 3
    assert result["selected_next_package"] == "ETF-EU-MVP01"
