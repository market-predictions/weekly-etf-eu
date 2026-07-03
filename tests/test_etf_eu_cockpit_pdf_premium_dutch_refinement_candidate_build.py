from __future__ import annotations

import json

from runtime.build_etf_eu_cockpit_pdf_premium_dutch_refinement_candidate import OUTPUT as REFINED_PDF
from runtime.build_etf_eu_cockpit_pdf_premium_dutch_refinement_candidate import main as build_refined_pdf
from tools.validate_etf_eu_cockpit_pdf_premium_dutch_refinement_candidate_build import (
    ARTIFACT,
    NOTES,
    SOURCE_PDF,
    SOURCE_REVIEW_ARTIFACT,
    SOURCE_REVIEW_NOTES,
    validate_premium_dutch_refinement_candidate_build,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_wp15t_files_exist() -> None:
    assert ARTIFACT.exists()
    assert NOTES.exists()
    assert SOURCE_REVIEW_ARTIFACT.exists()
    assert SOURCE_REVIEW_NOTES.exists()
    assert SOURCE_PDF.exists()


def test_builder_produces_refined_pdf() -> None:
    build_refined_pdf()
    data = REFINED_PDF.read_bytes()
    assert data.startswith(b"%PDF")
    assert len(data) > 15000
    assert b"ETF EU Cockpit" in data
    assert b"Nederlandse reviewkandidaat" in data


def test_pdf_is_dutch_first_and_card_table_based() -> None:
    build_refined_pdf()
    data = REFINED_PDF.read_bytes()
    for marker in [b"Beslissing nu", b"Actiekaart", b"Kwaliteitsbadges", b"UCITS-kandidaten", b"Bewijs en versheid", b"Klantgrade status", b"Governance footer"]:
        assert marker in data


def test_pdf_preserves_no_delivery_boundary() -> None:
    build_refined_pdf()
    data = REFINED_PDF.read_bytes()
    for marker in [b"REVIEW-ONLY", b"NIET GELEVERD", b"Geen live prijsupdate", b"Geen e-mail of klantdistributie", b"Geen delivery", b"geen receipt", b"geen productie-manifest"]:
        assert marker in data


def test_artifact_identity_and_flags() -> None:
    data = _artifact()
    assert data["repository"] == "market-predictions/weekly-etf-eu"
    assert data["work_package_id"] == "ETF-EU-WP15T"
    assert data["legacy_work_package_id"] == "WP15T"
    assert data["source_work_package"] == "ETF-EU-WP15S"
    assert data["refined_pdf_candidate_path"] == str(REFINED_PDF)
    assert data["premium_visual_refinement_candidate_created"] is True
    assert data["dutch_first_language_refinement_candidate_created"] is True
    assert data["cards_and_tables_used"] is True
    assert data["evidence_badges_used"] is True


def test_wp15s_gaps_are_addressed_without_delivery() -> None:
    data = _artifact()
    gaps = "\n".join(data["wp15s_gaps_addressed"])
    assert "visually dense" in gaps
    assert "Dutch-first" in gaps
    assert "pipe-delimited" in gaps
    assert "evidence badges" in gaps
    assert data["client_grade_status_after_wp15t"] == "not_yet_client_grade_refined_review_only_candidate_built"
    assert data["client_grade_claim"] is False
    assert data["client_grade_enough_for_delivery_preflight_discussion"] is False


def test_no_forbidden_authority_changes() -> None:
    data = _artifact()
    assert data["source_pdf_replaced"] is False
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


def test_visible_sections_and_candidates_are_recorded() -> None:
    data = _artifact()
    assert data["visible_page_count"] == 4
    assert len(data["visible_sections_present"]) >= 16
    assert any("IE00B5BMR087" in row for row in data["candidate_rows_represented"])
    assert any("IE00BMC38736" in row for row in data["candidate_rows_represented"])
    assert any("INFR" in row for row in data["candidate_rows_represented"])


def test_notes_record_boundary_and_next_package() -> None:
    notes = NOTES.read_text(encoding="utf-8")
    assert "work_package_id=ETF-EU-WP15T" in notes
    assert "Dutch-first client language" in notes
    assert "production_delivery=false" in notes
    assert "valuation_grade=false" in notes
    assert "ETF-EU-WP15U" in notes


def test_selected_next_package_is_wp15u() -> None:
    assert _artifact()["selected_next_package"] == "ETF-EU-WP15U"


def test_validator_passes() -> None:
    result = validate_premium_dutch_refinement_candidate_build(ARTIFACT)
    assert result["status"] == "valid"
    assert result["pdf"] == str(REFINED_PDF)
    assert result["selected_next_package"] == "ETF-EU-WP15U"
