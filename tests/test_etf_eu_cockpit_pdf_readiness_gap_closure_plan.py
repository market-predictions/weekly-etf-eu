from __future__ import annotations

import json

from tools.validate_etf_eu_cockpit_pdf_readiness_gap_closure_plan import (
    ARTIFACT,
    NOTES,
    PLAN,
    PRIMARY_GAPS,
    READINESS_CONTRACT,
    SOURCE_AUDIT_ARTIFACT,
    SOURCE_AUDIT_NOTES,
    validate_gap_closure_plan,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _gap_rows(data: dict) -> list[dict]:
    return data["decision_framework_gap_closure_plan"] + data["input_state_contract_gap_closure_plan"]


def test_all_expected_wp15x_files_exist() -> None:
    assert PLAN.exists()
    assert ARTIFACT.exists()
    assert NOTES.exists()
    assert SOURCE_AUDIT_ARTIFACT.exists()
    assert SOURCE_AUDIT_NOTES.exists()
    assert READINESS_CONTRACT.exists()


def test_artifact_identity_and_source_paths_are_correct() -> None:
    data = _artifact()
    assert data["repository"] == "market-predictions/weekly-etf-eu"
    assert data["work_package_id"] == "ETF-EU-WP15X"
    assert data["legacy_work_package_id"] == "WP15X"
    assert data["source_work_package"] == "ETF-EU-WP15W"
    assert data["source_readiness_audit_artifact"] == str(SOURCE_AUDIT_ARTIFACT)
    assert data["source_readiness_audit_notes"] == str(SOURCE_AUDIT_NOTES)
    assert data["readiness_contract_path"] == str(READINESS_CONTRACT)
    assert data["gap_closure_plan_path"] == str(PLAN)
    assert data["gap_closure_artifact"] == str(ARTIFACT)
    assert data["gap_closure_notes"] == str(NOTES)


def test_all_primary_wp15w_gaps_are_represented() -> None:
    rows = _gap_rows(_artifact())
    assert {row["gap_id"] for row in rows} == PRIMARY_GAPS
    assert len(rows) == 12


def test_every_gap_row_has_required_fields() -> None:
    required = {
        "gap_id",
        "layer",
        "current_status",
        "why_it_blocks_client_grade",
        "required_evidence",
        "expected_source_contract_or_file",
        "future_validator_expectation",
        "future_package_type",
        "execution_authority_required",
        "closure_sequence",
        "risk_if_skipped",
    }
    for row in _gap_rows(_artifact()):
        assert required.issubset(row)
        for key in required:
            assert row[key]


def test_no_data_dependent_gap_uses_planning_only_authority() -> None:
    for row in _gap_rows(_artifact()):
        assert row["execution_authority_required"] == "explicit_later_authority_required"


def test_no_execution_was_performed() -> None:
    data = _artifact()
    assert data["gap_closure_plan_created"] is True
    assert data["gap_closure_plan_status"] == "non_executing_plan_created"
    assert data["execution_performed"] is False
    assert data["non_executing_plan_summary"]["evidence_collected"] is False
    assert data["non_executing_plan_summary"]["recommendation_changed"] is False
    assert data["non_executing_plan_summary"]["pdf_changed"] is False


def test_client_grade_and_delivery_preflight_claims_remain_false() -> None:
    data = _artifact()
    assert data["client_grade_claim"] is False
    assert data["client_grade_enough_for_delivery_preflight_discussion"] is False
    assert data["delivery_ready"] is False
    assert data["delivery_preflight_allowed"] is False


def test_no_forbidden_authority_flags_changed() -> None:
    data = _artifact()
    assert data["production_delivery"] is False
    assert data["portfolio_mutation"] is False
    assert data["candidate_promotion"] is False
    assert data["funding_authority"] is False
    assert data["valuation_grade"] is False
    assert data["outbound_path_enabled"] is False
    assert data["live_data_fetch_performed"] is False
    assert data["pricing_evidence_changed"] is False
    assert data["recommendation_logic_changed"] is False
    assert data["client_distribution_claimed"] is False
    assert data["receipt_artifact_created"] is False
    assert data["production_manifest_created"] is False
    assert data["source_pdf_replaced"] is False
    assert data["new_pdf_created"] is False
    assert data["renderer_changed"] is False


def test_no_output_or_operational_blocker_flags_are_recorded() -> None:
    data = _artifact()
    assert data["output_contract_gap_closure_plan"]["no_output_contract_gap_requiring_closure"] is True
    assert data["operational_runbook_gap_closure_plan"]["no_operational_runbook_gap_requiring_closure"] is True


def test_selected_next_package_is_wp15y() -> None:
    data = _artifact()
    assert data["selected_next_package"] == "ETF-EU-WP15Y"
    assert data["selected_next_package_title"] == "ETF EU cockpit PDF readiness evidence acquisition contract, no delivery"


def test_validator_passes() -> None:
    result = validate_gap_closure_plan(ARTIFACT)
    assert result["status"] == "valid"
    assert result["artifact"] == str(ARTIFACT)
    assert result["selected_next_package"] == "ETF-EU-WP15Y"
