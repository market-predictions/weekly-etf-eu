from __future__ import annotations

import json

from tools.validate_etf_eu_cockpit_pdf_renderer_candidate_visual_review_checkpoint import (
    ARTIFACT,
    NOTES,
    PDF_CANDIDATE,
    SOURCE_RENDERER_ARTIFACT,
    validate_visual_review_checkpoint,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_visual_review_json_exists() -> None:
    assert ARTIFACT.exists()


def test_visual_review_notes_exist() -> None:
    assert NOTES.exists()


def test_source_pdf_candidate_exists_and_is_non_trivial_pdf() -> None:
    assert PDF_CANDIDATE.exists()
    pdf = PDF_CANDIDATE.read_bytes()
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 1000
    assert b"Review-only PDF Candidate" in pdf
    assert b"not delivered" in pdf
    assert b"delivery_authorization_decision=remain_blocked" in pdf


def test_source_renderer_candidate_artifact_exists() -> None:
    assert SOURCE_RENDERER_ARTIFACT.exists()


def test_json_records_wp15n_identity_and_wp15m_source() -> None:
    data = _artifact()
    assert data["repository"] == "market-predictions/weekly-etf-eu"
    assert data["work_package_id"] == "ETF-EU-WP15N"
    assert data["legacy_work_package_id"] == "WP15N"
    assert data["source_work_package"] == "ETF-EU-WP15M"


def test_actual_pdf_candidate_reviewed() -> None:
    data = _artifact()
    assert data["actual_pdf_candidate_reviewed"] is True
    assert data["visual_review_checkpoint_created"] is True
    assert data["pdf_candidate_path"] == str(PDF_CANDIDATE)
    assert data["pdf_candidate_commit"] == "92c09a8"
    assert data["pdf_candidate_exists"] is True
    assert data["pdf_candidate_is_review_only"] is True


def test_visual_review_decision_requests_refinement() -> None:
    data = _artifact()
    assert data["visual_review_decision"] == "request_concrete_visual_refinement_build_package"
    assert data["client_grade_status"] == "not_yet_client_grade"
    assert data["visual_refinement_required"] is True


def test_review_lists_are_present() -> None:
    data = _artifact()
    assert data["review_findings"]
    assert data["accepted_elements"]
    assert data["required_refinements"]


def test_no_new_pdf_or_renderer_change_in_review_package() -> None:
    data = _artifact()
    assert data["new_pdf_created"] is False
    assert data["renderer_changed"] is False
    assert data["premium_pdf_replaced"] is False


def test_no_delivery_or_distribution_claim() -> None:
    data = _artifact()
    assert data["production_delivery"] is False
    assert data["outbound_path_enabled"] is False
    assert data["client_distribution_claimed"] is False
    assert data["receipt_artifact_created"] is False
    assert data["production_manifest_created"] is False


def test_no_live_data_pricing_or_recommendation_change() -> None:
    data = _artifact()
    assert data["live_data_fetch_performed"] is False
    assert data["pricing_evidence_changed"] is False
    assert data["recommendation_logic_changed"] is False


def test_authority_boundary_remains_blocked() -> None:
    data = _artifact()
    assert data["delivery_authorization_decision"] == "remain_blocked"
    assert data["delivery_preflight_allowed"] is False
    for key in ["portfolio_mutation", "candidate_promotion", "funding_authority", "valuation_grade"]:
        assert data[key] is False


def test_selected_next_package_is_wp15o() -> None:
    assert _artifact()["selected_next_package"] == "ETF-EU-WP15O"


def test_validator_passes() -> None:
    result = validate_visual_review_checkpoint(ARTIFACT)
    assert result["status"] == "valid"
    assert result["selected_next_package"] == "ETF-EU-WP15O"
