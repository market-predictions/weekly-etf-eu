from __future__ import annotations

import json

from tools.validate_etf_eu_cockpit_pdf_premium_surface_improvement_decision import (
    ARTIFACT,
    DECISION,
    NOTES,
    PREMIUM_PDF,
    REVIEW_CHECKPOINT_ARTIFACT,
    REVIEW_CHECKPOINT_NOTES,
    SELECTED_NEXT_PACKAGE,
    validate_improvement_decision,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _review_checkpoint() -> dict:
    return json.loads(REVIEW_CHECKPOINT_ARTIFACT.read_text(encoding="utf-8"))


def test_improvement_decision_json_exists() -> None:
    assert ARTIFACT.exists()


def test_improvement_decision_notes_exist() -> None:
    assert NOTES.exists()


def test_premium_pdf_is_existing_review_artifact() -> None:
    assert PREMIUM_PDF.exists()
    data = PREMIUM_PDF.read_bytes()
    assert data.startswith(b"%PDF")
    assert len(data) > 8500


def test_source_review_checkpoint_artifacts_exist() -> None:
    assert REVIEW_CHECKPOINT_ARTIFACT.exists()
    assert REVIEW_CHECKPOINT_NOTES.exists()


def test_json_records_wp15i_identity() -> None:
    data = _artifact()
    assert data["work_package"] == "WP15I"
    assert data["source_work_package"] == "WP15H"
    assert data["status"] == "completed"


def test_decision_keeps_pdf_but_requires_targeted_refinement() -> None:
    data = _artifact()
    assert data["decision"] == DECISION
    assert data["keep_as_current_review_artifact"] is True
    assert data["targeted_improvement_needed"] is True
    assert data["delivery_preflight_allowed"] is False


def test_selected_next_package_is_wp15j() -> None:
    data = _artifact()
    assert data["selected_next_package"] == SELECTED_NEXT_PACKAGE
    assert data["selected_next_package_title"] == "ETF EU cockpit PDF premium surface targeted copy/governance refinement plan, no delivery"


def test_review_checkpoint_is_wp15h_source_and_selected_wp15i() -> None:
    data = _artifact()
    review_checkpoint = _review_checkpoint()
    assert data["source_review_checkpoint_artifact"] == str(REVIEW_CHECKPOINT_ARTIFACT)
    assert review_checkpoint["work_package"] == "WP15H"
    assert review_checkpoint["selected_next_package"] == "WP15I"
    assert review_checkpoint["review_checkpoint_decision"] == "keep_premium_pdf_as_current_review_artifact"


def test_no_new_pdf_renderer_or_replacement() -> None:
    data = _artifact()
    assert data["new_pdf_created"] is False
    assert data["renderer_changed"] is False
    assert data["premium_pdf_replaced"] is False


def test_no_delivery_or_authority_created() -> None:
    data = _artifact()
    assert data["delivery_authorization_decision"] == "remain_blocked"
    for key in [
        "production_delivery",
        "portfolio_mutation",
        "candidate_promotion",
        "funding_authority",
        "valuation_grade",
        "outbound_path_enabled",
        "receipt_artifact_created",
        "production_manifest_created",
        "client_distribution_claimed",
    ]:
        assert data[key] is False


def test_no_live_data_or_recommendation_change() -> None:
    data = _artifact()
    assert data["live_data_fetch_performed"] is False
    assert data["recommendation_logic_changed"] is False


def test_recommended_scope_is_narrow_copy_governance_refinement() -> None:
    data = _artifact()
    scope = set(data["recommended_improvement_scope"])
    assert "client-facing copy refinement" in scope
    assert "visible marker/debug language reduction" in scope
    assert "preserve machine-checkable raw markers for validators" in scope
    assert "compact explanation of review evidence versus pricing evidence versus valuation-grade evidence" in scope


def test_rejected_scopes_block_delivery_and_broad_redesign() -> None:
    data = _artifact()
    rejected = set(data["rejected_scopes"])
    assert "broad renderer redesign in WP15I" in rejected
    assert "new PDF creation in WP15I" in rejected
    assert "delivery-preflight enablement in WP15I" in rejected
    assert "live data fetch or recommendation logic changes" in rejected


def test_validator_passes() -> None:
    result = validate_improvement_decision(ARTIFACT)
    assert result["status"] == "valid"
    assert result["selected_next_package"] == SELECTED_NEXT_PACKAGE
