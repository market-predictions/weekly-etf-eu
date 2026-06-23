from __future__ import annotations

import json

from runtime.build_etf_eu_cockpit_pdf_premium_visual_refinement_candidate import OUTPUT as PREMIUM_PDF
from runtime.build_etf_eu_cockpit_pdf_premium_visual_refinement_candidate import main as build_premium_pdf
from tools.validate_etf_eu_cockpit_pdf_premium_visual_refinement_build import (
    ARTIFACT,
    NOTES,
    SOURCE_PDF,
    SOURCE_REVIEW,
    validate_premium_visual_refinement_build,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_build_json_and_notes_exist() -> None:
    assert ARTIFACT.exists()
    assert NOTES.exists()


def test_source_inputs_exist() -> None:
    assert SOURCE_PDF.exists()
    assert SOURCE_REVIEW.exists()
    assert SOURCE_PDF.read_bytes().startswith(b"%PDF")


def test_builder_produces_new_premium_pdf_candidate() -> None:
    build_premium_pdf()
    assert PREMIUM_PDF.exists()
    data = PREMIUM_PDF.read_bytes()
    assert data.startswith(b"%PDF")
    assert len(data) > 1800
    assert b"review-only" in data
    assert b"not delivered" in data
    assert b"no delivery receipt" in data
    assert b"no production manifest" in data
    assert b"delivery_authorization_decision=remain_blocked" in data
    assert b"ETF EU Cockpit" in data


def test_json_records_wp15o_identity_and_wp15n_source() -> None:
    data = _artifact()
    assert data["repository"] == "market-predictions/weekly-etf-eu"
    assert data["work_package_id"] == "ETF-EU-WP15O"
    assert data["legacy_work_package_id"] == "WP15O"
    assert data["source_work_package"] == "ETF-EU-WP15N"


def test_artifact_records_candidate_paths() -> None:
    data = _artifact()
    assert data["source_pdf_candidate_path"] == str(SOURCE_PDF)
    assert data["source_pdf_candidate_commit"] == "92c09a8"
    assert data["source_visual_review_artifact"] == str(SOURCE_REVIEW)
    assert data["premium_pdf_candidate_path"] == str(PREMIUM_PDF)
    assert data["premium_pdf_candidate_builder"] == "runtime/build_etf_eu_cockpit_pdf_premium_visual_refinement_candidate.py"


def test_premium_visual_refinement_flags_are_true() -> None:
    data = _artifact()
    assert data["premium_visual_refinement_build_created"] is True
    assert data["review_only_premium_pdf_candidate_required"] is True
    assert data["review_only_premium_pdf_candidate_created"] is True
    assert data["new_pdf_created"] is True
    assert data["renderer_changed"] is True
    assert data["premium_visual_refinement_candidate_created"] is True


def test_visual_improvements_and_preserved_constraints_are_present() -> None:
    data = _artifact()
    assert data["visual_improvements"]
    assert data["preserved_constraints"]
    assert "premium cockpit-first layout" in data["visual_improvements"]
    assert "review-only status preserved" in data["preserved_constraints"]


def test_review_only_not_delivery_ready() -> None:
    data = _artifact()
    assert data["client_grade_claim"] is False
    assert data["delivery_ready"] is False
    assert data["prior_wp15m_pdf_replaced"] is False


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


def test_selected_next_package_is_wp15p() -> None:
    assert _artifact()["selected_next_package"] == "ETF-EU-WP15P"


def test_validator_passes() -> None:
    result = validate_premium_visual_refinement_build(ARTIFACT)
    assert result["status"] == "valid"
    assert result["pdf"] == str(PREMIUM_PDF)
    assert result["selected_next_package"] == "ETF-EU-WP15P"
