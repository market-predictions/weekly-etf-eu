from __future__ import annotations

import json
from pathlib import Path

from tools.validate_etf_eu_cockpit_pdf_premium_surface_review_checkpoint import (
    ARTIFACT,
    FALSE_BOUNDARY_FLAGS,
    NOTES,
    PREMIUM_PDF,
    SOURCE_CLOSEOUT_ARTIFACT,
    validate_premium_surface_review_checkpoint,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_review_checkpoint_json_exists() -> None:
    assert ARTIFACT.exists()


def test_review_checkpoint_notes_exist() -> None:
    assert NOTES.exists()


def test_reviewed_pdf_and_source_closeout_exist() -> None:
    assert PREMIUM_PDF.exists()
    assert SOURCE_CLOSEOUT_ARTIFACT.exists()
    assert PREMIUM_PDF.read_bytes().startswith(b"%PDF")


def test_review_checkpoint_records_package_identity() -> None:
    data = _artifact()
    assert data["work_package"] == "WP15H"
    assert data["source_work_package"] == "WP15G"
    assert data["status"] == "completed_accept_as_evidence_with_non_blocking_improvements"


def test_review_checkpoint_points_to_existing_premium_pdf() -> None:
    data = _artifact()
    assert data["reviewed_pdf_path"] == str(PREMIUM_PDF)
    assert data["source_closeout_artifact"] == str(SOURCE_CLOSEOUT_ARTIFACT)


def test_review_checkpoint_preserves_no_delivery_boundaries() -> None:
    data = _artifact()
    boundary_flags = data["boundary_flags"]
    for key in FALSE_BOUNDARY_FLAGS:
        assert boundary_flags[key] is False


def test_governance_assessment_passes_required_boundaries() -> None:
    governance = _artifact()["governance_assessment"]
    assert governance["avoids_valuation_grade_authority"] is True
    assert governance["avoids_funding_authority"] is True
    assert governance["avoids_candidate_promotion"] is True
    assert governance["avoids_portfolio_mutation"] is True
    assert governance["avoids_production_delivery_authority"] is True
    assert governance["preserves_eu_ucits_source_of_truth_boundary"] is True
    assert governance["keeps_us_etf_information_non_authoritative"] is True


def test_client_readability_assessment_is_present() -> None:
    readability = _artifact()["client_readability_assessment"]
    assert readability["first_page_understandable_for_dutch_eu_client"] is True
    assert readability["cockpit_first_structure_clear"] is True
    assert readability["answers_what_matters_now"] is True
    assert readability["signals_risk_state_and_next_actions_readable_without_developer_context"] == "partly"
    assert readability["unnecessary_technical_debug_language_on_client_surface"] == "present_but_controlled"


def test_product_checkpoint_selects_copy_governance_plan_next() -> None:
    data = _artifact()
    assert data["selected_next_package"] == "WP15I"
    assert data["selected_next_package_title"] == "ETF EU cockpit PDF premium surface copy/governance refinement plan, no delivery"
    assert data["product_checkpoint_assessment"]["recommended_next_step_type"] == "copy_governance_refinement_plan_no_delivery"


def test_validator_passes() -> None:
    result = validate_premium_surface_review_checkpoint(ARTIFACT)
    assert result["status"] == "valid"
    assert result["selected_next_package"] == "WP15I"
