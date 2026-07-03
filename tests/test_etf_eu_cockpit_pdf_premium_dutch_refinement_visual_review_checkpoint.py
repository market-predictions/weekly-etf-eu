from __future__ import annotations

import json

from runtime.build_etf_eu_cockpit_pdf_premium_dutch_refinement_candidate import OUTPUT as SOURCE_PDF
from runtime.build_etf_eu_cockpit_pdf_premium_dutch_refinement_candidate import main as build_source_pdf
from tools.validate_etf_eu_cockpit_pdf_premium_dutch_refinement_visual_review_checkpoint import (
    ARTIFACT,
    NOTES,
    SOURCE_BUILD_ARTIFACT,
    SOURCE_BUILD_NOTES,
    validate_premium_dutch_refinement_visual_review_checkpoint,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_wp15u_files_exist() -> None:
    assert ARTIFACT.exists()
    assert NOTES.exists()
    assert SOURCE_BUILD_ARTIFACT.exists()
    assert SOURCE_BUILD_NOTES.exists()


def test_source_pdf_materializes_and_has_review_markers() -> None:
    build_source_pdf()
    data = SOURCE_PDF.read_bytes()
    assert data.startswith(b"%PDF")
    assert b"Beslissing nu" in data
    assert b"Actiekaart" in data
    assert b"UCITS-kandidaten" in data
    assert b"Proxy-disclosure" in data
    assert b"Governance footer" in data
    assert b"REVIEW-ONLY" in data
    assert b"NIET GELEVERD" in data


def test_artifact_identity_and_source_paths() -> None:
    data = _artifact()
    assert data["repository"] == "market-predictions/weekly-etf-eu"
    assert data["work_package_id"] == "ETF-EU-WP15U"
    assert data["legacy_work_package_id"] == "WP15U"
    assert data["source_work_package"] == "ETF-EU-WP15T"
    assert data["source_pdf_candidate_path"] == str(SOURCE_PDF)
    assert data["visual_review_checkpoint_artifact"] == str(ARTIFACT)
    assert data["visual_review_checkpoint_notes"] == str(NOTES)


def test_review_expectation_flags_are_true() -> None:
    data = _artifact()
    assert data["source_pdf_candidate_reviewed"] is True
    assert data["actual_render_review_performed"] is True
    assert data["visual_review_checkpoint_created"] is True
    assert data["dutch_first_language_reviewed"] is True
    assert data["cards_and_tables_reviewed"] is True
    assert data["evidence_badges_reviewed"] is True
    assert data["proxy_disclosure_reviewed"] is True
    assert data["delivery_boundary_markers_reviewed"] is True
    assert data["no_us_etf_as_eu_holding"] is True


def test_review_decision_accepts_foundation_not_delivery_grade() -> None:
    data = _artifact()
    assert data["visual_review_decision"] == "accept_as_review_only_premium_dutch_cockpit_foundation_not_delivery_grade"
    assert data["client_grade_status_after_wp15u"] == "not_yet_client_grade_review_only_foundation_accepted_for_readiness_contract"
    assert data["client_grade_claim"] is False
    assert data["client_grade_enough_for_delivery_preflight_discussion"] is False
    assert data["delivery_ready"] is False


def test_render_observations_cover_decision_evidence_proxy_and_layout() -> None:
    data = _artifact()
    observations = "\n".join(data["render_review_observations"])
    assert data["review_page_count"] == 4
    assert "Beslissing nu" in observations
    assert "cash, review, watchlist and blocked" in observations
    assert "ISIN-first" in observations
    assert "proxy disclosure" in observations
    assert "no material clipping" in observations


def test_minor_observations_are_non_blocking() -> None:
    data = _artifact()
    observations = "\n".join(data["minor_non_blocking_observations"])
    assert "English governance labels" in observations
    assert "live data refresh is outside authority" in observations
    assert "readiness contract" in observations


def test_no_forbidden_authority_changes() -> None:
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


def test_no_source_pdf_or_renderer_changes_in_review_checkpoint() -> None:
    data = _artifact()
    assert data["source_pdf_replaced"] is False
    assert data["new_pdf_created"] is False
    assert data["renderer_changed"] is False


def test_notes_record_decision_boundary_and_next_package() -> None:
    notes = NOTES.read_text(encoding="utf-8")
    assert "work_package_id=ETF-EU-WP15U" in notes
    assert "visual_review_decision=accept_as_review_only_premium_dutch_cockpit_foundation_not_delivery_grade" in notes
    assert "client_grade_claim=false" in notes
    assert "production_delivery=false" in notes
    assert "valuation_grade=false" in notes
    assert "ETF-EU-WP15V" in notes


def test_selected_next_package_is_wp15v() -> None:
    assert _artifact()["selected_next_package"] == "ETF-EU-WP15V"


def test_validator_passes() -> None:
    result = validate_premium_dutch_refinement_visual_review_checkpoint(ARTIFACT)
    assert result["status"] == "valid"
    assert result["source_pdf"] == str(SOURCE_PDF)
    assert result["selected_next_package"] == "ETF-EU-WP15V"
