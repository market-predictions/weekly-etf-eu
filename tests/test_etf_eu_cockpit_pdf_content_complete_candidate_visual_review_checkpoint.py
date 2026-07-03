from __future__ import annotations

import json

from runtime.build_etf_eu_cockpit_pdf_content_complete_candidate import OUTPUT as CONTENT_COMPLETE_PDF
from runtime.build_etf_eu_cockpit_pdf_content_complete_candidate import main as build_content_complete_pdf
from tools.validate_etf_eu_cockpit_pdf_content_complete_candidate_visual_review_checkpoint import (
    ARTIFACT,
    NOTES,
    SOURCE_BUILD_ARTIFACT,
    SOURCE_BUILD_NOTES,
    validate_visual_review_checkpoint,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_wp15s_files_exist() -> None:
    assert ARTIFACT.exists()
    assert NOTES.exists()
    assert SOURCE_BUILD_ARTIFACT.exists()
    assert SOURCE_BUILD_NOTES.exists()


def test_source_pdf_exists_and_preserves_review_markers() -> None:
    build_content_complete_pdf()
    data = CONTENT_COMPLETE_PDF.read_bytes()
    assert data.startswith(b"%PDF")
    assert b"ETF EU Cockpit Content-Complete Candidate" in data
    assert b"REVIEW-ONLY" in data
    assert b"NOT DELIVERED" in data
    assert b"NO RECEIPT" in data
    assert b"NO PRODUCTION MANIFEST" in data
    assert b"AUTHORITY BLOCKED" in data


def test_artifact_identity_and_source_paths() -> None:
    data = _artifact()
    assert data["repository"] == "market-predictions/weekly-etf-eu"
    assert data["work_package_id"] == "ETF-EU-WP15S"
    assert data["legacy_work_package_id"] == "WP15S"
    assert data["source_work_package"] == "ETF-EU-WP15R"
    assert data["source_pdf_candidate_path"] == str(CONTENT_COMPLETE_PDF)
    assert data["source_build_artifact"] == str(SOURCE_BUILD_ARTIFACT)
    assert data["source_build_notes"] == str(SOURCE_BUILD_NOTES)


def test_review_checkpoint_flags_are_true() -> None:
    data = _artifact()
    assert data["source_pdf_candidate_reviewed"] is True
    assert data["actual_pdf_candidate_reviewed"] is True
    assert data["visual_review_checkpoint_created"] is True
    assert data["validator_created"] is True
    assert data["tests_created"] is True


def test_review_decision_requires_refinement_not_delivery() -> None:
    data = _artifact()
    assert data["visual_review_decision"] == "accept_as_review_only_content_complete_foundation_request_premium_visual_and_language_refinement"
    assert data["content_completeness_status"] == "content_complete_for_review_only_candidate"
    assert data["client_grade_status_after_wp15s"] == "not_yet_client_grade_visual_language_refinement_required"
    assert data["client_grade_claim"] is False
    assert data["client_grade_enough_for_delivery_preflight_discussion"] is False
    assert data["delivery_ready"] is False


def test_strengths_and_gaps_are_recorded() -> None:
    data = _artifact()
    assert len(data["review_strengths"]) >= 7
    assert len(data["blocking_gaps_before_client_grade_or_delivery_preflight"]) >= 8
    assert len(data["required_before_client_grade_or_delivery_preflight"]) >= 8
    gaps = "\n".join(data["blocking_gaps_before_client_grade_or_delivery_preflight"])
    assert "visually dense" in gaps
    assert "Dutch-first" in gaps
    assert "pipe-delimited" in gaps
    assert "freshness badges" in gaps


def test_no_pdf_or_renderer_change_in_review_checkpoint() -> None:
    data = _artifact()
    assert data["source_pdf_replaced"] is False
    assert data["new_pdf_created"] is False
    assert data["renderer_changed"] is False


def test_no_delivery_or_authority_boundary_changed() -> None:
    data = _artifact()
    assert data["production_delivery"] is False
    assert data["portfolio_mutation"] is False
    assert data["candidate_promotion"] is False
    assert data["funding_authority"] is False
    assert data["valuation_grade"] is False
    assert data["delivery_preflight_allowed"] is False
    assert data["outbound_path_enabled"] is False
    assert data["receipt_artifact_created"] is False
    assert data["production_manifest_created"] is False


def test_no_live_data_pricing_or_recommendation_change() -> None:
    data = _artifact()
    assert data["live_data_fetch_performed"] is False
    assert data["pricing_evidence_changed"] is False
    assert data["recommendation_logic_changed"] is False


def test_notes_record_decision_and_boundaries() -> None:
    notes = NOTES.read_text(encoding="utf-8")
    assert "work_package_id=ETF-EU-WP15S" in notes
    assert "source_work_package=ETF-EU-WP15R" in notes
    assert "client_grade_status_after_wp15s=not_yet_client_grade_visual_language_refinement_required" in notes
    assert "production_delivery=false" in notes
    assert "valuation_grade=false" in notes
    assert "ETF-EU-WP15T" in notes


def test_selected_next_package_is_wp15t() -> None:
    assert _artifact()["selected_next_package"] == "ETF-EU-WP15T"


def test_validator_passes() -> None:
    result = validate_visual_review_checkpoint(ARTIFACT)
    assert result["status"] == "valid"
    assert result["source_pdf"] == str(CONTENT_COMPLETE_PDF)
    assert result["selected_next_package"] == "ETF-EU-WP15T"
