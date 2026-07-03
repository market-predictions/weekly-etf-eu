from __future__ import annotations

import json

from tools.validate_etf_eu_cockpit_pdf_readiness_gate_implementation_audit import (
    ALLOWED_STATUSES,
    ARTIFACT,
    AUDIT_GROUPS,
    NOTES,
    READINESS_CONTRACT,
    SOURCE_READINESS_GATE_ARTIFACT,
    SOURCE_READINESS_GATE_NOTES,
    SOURCE_REFINEMENT_ARTIFACT,
    SOURCE_REFINEMENT_NOTES,
    SOURCE_VISUAL_REVIEW_ARTIFACT,
    SOURCE_VISUAL_REVIEW_NOTES,
    validate_readiness_gate_implementation_audit,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_all_expected_wp15w_files_exist() -> None:
    assert READINESS_CONTRACT.exists()
    assert SOURCE_READINESS_GATE_ARTIFACT.exists()
    assert SOURCE_READINESS_GATE_NOTES.exists()
    assert SOURCE_VISUAL_REVIEW_ARTIFACT.exists()
    assert SOURCE_VISUAL_REVIEW_NOTES.exists()
    assert SOURCE_REFINEMENT_ARTIFACT.exists()
    assert SOURCE_REFINEMENT_NOTES.exists()
    assert ARTIFACT.exists()
    assert NOTES.exists()


def test_audit_artifact_identity_and_source_paths_are_correct() -> None:
    data = _artifact()
    assert data["repository"] == "market-predictions/weekly-etf-eu"
    assert data["work_package_id"] == "ETF-EU-WP15W"
    assert data["legacy_work_package_id"] == "WP15W"
    assert data["source_work_package"] == "ETF-EU-WP15V"
    assert data["readiness_contract_path"] == str(READINESS_CONTRACT)
    assert data["source_readiness_gate_artifact"] == str(SOURCE_READINESS_GATE_ARTIFACT)
    assert data["source_visual_review_artifact"] == str(SOURCE_VISUAL_REVIEW_ARTIFACT)
    assert data["readiness_audit_artifact"] == str(ARTIFACT)
    assert data["readiness_audit_notes"] == str(NOTES)


def test_all_four_audit_groups_are_present() -> None:
    data = _artifact()
    assert data["decision_framework_audit"]
    assert data["input_state_contract_audit"]
    assert data["output_contract_audit"]
    assert data["operational_runbook_audit"]
    assert data["blocking_gates_before_client_grade"]
    assert data["blocking_gates_before_delivery_preflight"]
    assert isinstance(data["summary"], dict)


def test_every_audit_row_has_required_fields() -> None:
    data = _artifact()
    for group_name in AUDIT_GROUPS:
        for row in data[group_name]:
            assert row["gate"]
            assert row["status"]
            assert row["rationale"]
            assert row["evidence_reference"]


def test_statuses_are_limited_to_allowed_values() -> None:
    data = _artifact()
    for group_name in AUDIT_GROUPS:
        for row in data[group_name]:
            assert row["status"] in ALLOWED_STATUSES


def test_readiness_audit_result_remains_non_client_grade() -> None:
    data = _artifact()
    assert data["readiness_audit_created"] is True
    assert data["readiness_audit_status"] == "completed_with_blocking_gaps"
    assert data["client_grade_readiness_audit_result"] == "fail_blocked_by_missing_evidence"
    assert data["client_grade_claim"] is False
    assert data["client_grade_enough_for_delivery_preflight_discussion"] is False
    assert data["delivery_ready"] is False


def test_blocking_gap_exists_for_failed_readiness_result() -> None:
    data = _artifact()
    assert data["summary"]["primary_blocking_gaps"]
    statuses = [row["status"] for group in AUDIT_GROUPS for row in data[group]]
    assert "fail" in statuses or "blocked" in statuses


def test_delivery_preflight_claim_remains_false() -> None:
    data = _artifact()
    assert data["delivery_preflight_allowed"] is False
    assert data["delivery_ready"] is False
    assert data["production_delivery"] is False
    assert data["receipt_artifact_created"] is False
    assert data["production_manifest_created"] is False


def test_no_forbidden_authority_flags_changed() -> None:
    data = _artifact()
    assert data["portfolio_mutation"] is False
    assert data["candidate_promotion"] is False
    assert data["funding_authority"] is False
    assert data["valuation_grade"] is False
    assert data["outbound_path_enabled"] is False
    assert data["live_data_fetch_performed"] is False
    assert data["pricing_evidence_changed"] is False
    assert data["recommendation_logic_changed"] is False
    assert data["client_distribution_claimed"] is False
    assert data["source_pdf_replaced"] is False
    assert data["new_pdf_created"] is False
    assert data["renderer_changed"] is False


def test_selected_next_package_is_wp15x() -> None:
    data = _artifact()
    assert data["selected_next_package"] == "ETF-EU-WP15X"
    assert data["selected_next_package_title"] == "ETF EU cockpit PDF readiness gap closure plan, no delivery"


def test_validator_passes() -> None:
    result = validate_readiness_gate_implementation_audit(ARTIFACT)
    assert result["status"] == "valid"
    assert result["artifact"] == str(ARTIFACT)
    assert result["result"] == "fail_blocked_by_missing_evidence"
    assert result["selected_next_package"] == "ETF-EU-WP15X"
