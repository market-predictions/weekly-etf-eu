from __future__ import annotations

import json

from tools.validate_etf_eu_cockpit_pdf_client_grade_readiness_gate import (
    ARTIFACT,
    CONTRACT,
    NOTES,
    PRIOR_CONTENT_CONTRACT,
    SOURCE_VISUAL_REVIEW_ARTIFACT,
    SOURCE_VISUAL_REVIEW_NOTES,
    validate_readiness_gate,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_all_expected_wp15v_files_exist() -> None:
    assert CONTRACT.exists()
    assert ARTIFACT.exists()
    assert NOTES.exists()
    assert SOURCE_VISUAL_REVIEW_ARTIFACT.exists()
    assert SOURCE_VISUAL_REVIEW_NOTES.exists()
    assert PRIOR_CONTENT_CONTRACT.exists()


def test_contract_identity_and_purpose_are_correct() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    assert "ETF EU Cockpit PDF Client-Grade Readiness Contract V1" in text
    assert "client-grade readiness contract and evidence gate" in text
    assert "does **not** make any PDF client-grade" in text
    assert "delivery receipt" in text
    assert "production manifest" in text


def test_contract_has_all_four_layers() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    assert "decision framework readiness" in text
    assert "input/state contract readiness" in text
    assert "output contract readiness" in text
    assert "operational runbook readiness" in text


def test_contract_mentions_required_evidence_concepts() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    for marker in ["ISIN-first", "UCITS", "PRIIPs/KID", "pricing freshness", "Dutch-first", "proxy disclosure", "unresolved data"]:
        assert marker in text


def test_artifact_identity_and_paths() -> None:
    data = _artifact()
    assert data["repository"] == "market-predictions/weekly-etf-eu"
    assert data["work_package_id"] == "ETF-EU-WP15V"
    assert data["legacy_work_package_id"] == "WP15V"
    assert data["source_work_package"] == "ETF-EU-WP15U"
    assert data["readiness_contract_path"] == str(CONTRACT)
    assert data["readiness_gate_artifact"] == str(ARTIFACT)
    assert data["readiness_gate_notes"] == str(NOTES)


def test_evidence_gate_groups_are_present() -> None:
    data = _artifact()
    assert len(data["decision_framework_gates"]) >= 8
    assert len(data["input_state_contract_gates"]) >= 18
    assert len(data["output_contract_gates"]) >= 11
    assert len(data["operational_runbook_gates"]) >= 9
    assert len(data["blocking_gates_before_client_grade"]) >= 7
    assert len(data["blocking_gates_before_delivery_preflight"]) >= 6


def test_readiness_gate_status_is_defined_not_passed() -> None:
    data = _artifact()
    assert data["client_grade_readiness_contract_created"] is True
    assert data["evidence_gate_created"] is True
    assert data["readiness_gate_status"] == "contract_defined_not_passed"
    assert data["client_grade_claim"] is False
    assert data["client_grade_enough_for_delivery_preflight_discussion"] is False
    assert data["delivery_ready"] is False


def test_no_forbidden_authority_flags_changed() -> None:
    data = _artifact()
    assert data["production_delivery"] is False
    assert data["portfolio_mutation"] is False
    assert data["candidate_promotion"] is False
    assert data["funding_authority"] is False
    assert data["valuation_grade"] is False
    assert data["delivery_preflight_allowed"] is False
    assert data["outbound_path_enabled"] is False
    assert data["live_data_fetch_performed"] is False
    assert data["pricing_evidence_changed"] is False
    assert data["recommendation_logic_changed"] is False
    assert data["receipt_artifact_created"] is False
    assert data["production_manifest_created"] is False
    assert data["source_pdf_replaced"] is False
    assert data["new_pdf_created"] is False
    assert data["renderer_changed"] is False


def test_notes_record_contract_status_and_boundary() -> None:
    notes = NOTES.read_text(encoding="utf-8")
    assert "work_package_id=ETF-EU-WP15V" in notes
    assert "readiness_gate_status=contract_defined_not_passed" in notes
    assert "production_delivery=false" in notes
    assert "valuation_grade=false" in notes
    assert "ETF-EU-WP15W" in notes


def test_selected_next_package_is_wp15w() -> None:
    assert _artifact()["selected_next_package"] == "ETF-EU-WP15W"


def test_validator_passes() -> None:
    result = validate_readiness_gate(ARTIFACT)
    assert result["status"] == "valid"
    assert result["artifact"] == str(ARTIFACT)
    assert result["contract"] == str(CONTRACT)
    assert result["selected_next_package"] == "ETF-EU-WP15W"
