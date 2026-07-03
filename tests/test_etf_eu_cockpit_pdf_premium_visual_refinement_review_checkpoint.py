from __future__ import annotations

import json

from runtime.build_etf_eu_cockpit_pdf_premium_visual_refinement_candidate import OUTPUT as PREMIUM_PDF
from runtime.build_etf_eu_cockpit_pdf_premium_visual_refinement_candidate import main as build_premium_pdf
from tools.validate_etf_eu_cockpit_pdf_premium_visual_refinement_review_checkpoint import (
    ARTIFACT,
    NOTES,
    SOURCE_BUILD_ARTIFACT,
    SOURCE_BUILD_NOTES,
    validate_premium_visual_refinement_review_checkpoint,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_review_checkpoint_json_and_notes_exist() -> None:
    assert ARTIFACT.exists()
    assert NOTES.exists()


def test_source_wp15o_inputs_exist() -> None:
    build_premium_pdf()
    assert PREMIUM_PDF.exists()
    assert SOURCE_BUILD_ARTIFACT.exists()
    assert SOURCE_BUILD_NOTES.exists()
    assert PREMIUM_PDF.read_bytes().startswith(b"%PDF")


def test_source_premium_pdf_candidate_keeps_required_markers() -> None:
    build_premium_pdf()
    data = PREMIUM_PDF.read_bytes()
    assert len(data) > 1800
    assert b"ETF EU Cockpit" in data
    assert b"review-only" in data
    assert b"NOT DELIVERED" in data
    assert b"NO RECEIPT" in data
    assert b"AUTHORITY BLOCKED" in data
    assert b"delivery_authorization_decision=remain_blocked" in data


def test_review_checkpoint_records_identity_and_source() -> None:
    data = _artifact()
    assert data["repository"] == "market-predictions/weekly-etf-eu"
    assert data["work_package_id"] == "ETF-EU-WP15P"
    assert data["legacy_work_package_id"] == "WP15P"
    assert data["source_work_package"] == "ETF-EU-WP15O"
    assert data["source_premium_pdf_candidate_path"] == str(PREMIUM_PDF)
    assert data["source_premium_build_artifact"] == str(SOURCE_BUILD_ARTIFACT)
    assert data["source_premium_build_notes"] == str(SOURCE_BUILD_NOTES)


def test_review_checkpoint_flags_are_true() -> None:
    data = _artifact()
    assert data["visual_review_checkpoint_created"] is True
    assert data["actual_pdf_candidate_reviewed"] is True
    assert data["source_premium_pdf_candidate_reviewed"] is True
    assert data["review_only_status_confirmed"] is True
    assert data["no_delivery_boundary_confirmed"] is True
    assert data["validator_created"] is True
    assert data["tests_created"] is True


def test_review_decision_is_not_client_grade_or_delivery_preflight() -> None:
    data = _artifact()
    assert data["visual_review_decision"] == "accept_as_review_only_cockpit_surface_foundation_not_delivery_grade"
    assert data["client_grade_status"] == "not_yet_client_grade"
    assert data["client_grade_enough_for_delivery_preflight_discussion"] is False
    assert data["client_grade_claim"] is False
    assert data["delivery_ready"] is False
    assert data["delivery_preflight_allowed"] is False


def test_review_lists_strengths_gaps_and_required_followup() -> None:
    data = _artifact()
    assert data["premium_surface_strengths"]
    assert data["blocking_gaps_before_client_grade_or_delivery_preflight"]
    assert data["required_before_delivery_preflight_discussion"]
    assert "clear cockpit-first title and status header" in data["premium_surface_strengths"]
    assert "single-page cockpit shell does not yet contain enough actual ETF report content" in data["blocking_gaps_before_client_grade_or_delivery_preflight"]


def test_no_output_or_authority_boundary_changed() -> None:
    data = _artifact()
    assert data["source_pdf_replaced"] is False
    assert data["new_pdf_created"] is False
    assert data["renderer_changed"] is False
    assert data["production_delivery"] is False
    assert data["portfolio_mutation"] is False
    assert data["candidate_promotion"] is False
    assert data["funding_authority"] is False
    assert data["valuation_grade"] is False
    assert data["outbound_path_enabled"] is False
    assert data["client_distribution_claimed"] is False
    assert data["receipt_artifact_created"] is False
    assert data["production_manifest_created"] is False


def test_no_live_data_pricing_or_recommendation_change() -> None:
    data = _artifact()
    assert data["live_data_fetch_performed"] is False
    assert data["pricing_evidence_changed"] is False
    assert data["recommendation_logic_changed"] is False


def test_notes_record_review_decision_and_boundaries() -> None:
    notes = NOTES.read_text(encoding="utf-8")
    assert "work_package_id=ETF-EU-WP15P" in notes
    assert "visual_review_decision=accept_as_review_only_cockpit_surface_foundation_not_delivery_grade" in notes
    assert "client_grade_status=not_yet_client_grade" in notes
    assert "client_grade_enough_for_delivery_preflight_discussion=false" in notes
    assert "production_delivery=false" in notes
    assert "delivery_preflight_allowed=false" in notes
    assert "ETF-EU-WP15Q" in notes


def test_selected_next_package_is_wp15q() -> None:
    assert _artifact()["selected_next_package"] == "ETF-EU-WP15Q"


def test_validator_passes() -> None:
    result = validate_premium_visual_refinement_review_checkpoint(ARTIFACT)
    assert result["status"] == "valid"
    assert result["source_pdf"] == str(PREMIUM_PDF)
    assert result["selected_next_package"] == "ETF-EU-WP15Q"
