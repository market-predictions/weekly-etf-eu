from __future__ import annotations

import json

from tools.validate_etf_eu_cockpit_pdf_premium_surface_improvement_decision import (
    ARTIFACT,
    CLOSEOUT_ARTIFACT,
    CREATE_TARGETED,
    DECISION,
    LEGACY_WORK_PACKAGE_ID,
    NOTES,
    PREMIUM_PDF,
    REPOSITORY,
    REVIEW_ARTIFACT,
    REVIEW_NOTES,
    TARGETED_PACKAGE,
    WORK_PACKAGE_ID,
    validate_improvement_decision,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_decision_json_exists() -> None:
    assert ARTIFACT.exists()


def test_decision_notes_exist() -> None:
    assert NOTES.exists()


def test_premium_pdf_exists_and_has_header_and_size() -> None:
    assert PREMIUM_PDF.exists()
    data = PREMIUM_PDF.read_bytes()
    assert data.startswith(b"%PDF")
    assert len(data) > 8500


def test_source_decision_artifacts_exist() -> None:
    assert REVIEW_ARTIFACT.exists()
    assert REVIEW_NOTES.exists()
    assert CLOSEOUT_ARTIFACT.exists()


def test_json_records_namespaced_package_identity() -> None:
    data = _artifact()
    assert data["repository"] == REPOSITORY
    assert data["work_package_id"] == WORK_PACKAGE_ID
    assert data["legacy_work_package_id"] == LEGACY_WORK_PACKAGE_ID
    assert data["work_package"] == "WP15I"
    assert data["source_work_package"] == "WP15H"
    assert data["status"] == "completed"


def test_reconciled_decision_requires_targeted_refinement() -> None:
    data = _artifact()
    assert data["improvement_decision_created"] is True
    assert data["improvement_decision"] == CREATE_TARGETED
    assert data["decision"] == DECISION
    assert data["keep_as_current_review_artifact"] is True
    assert data["targeted_improvement_needed"] is True
    assert data["targeted_improvement_package_required"] is True
    assert data["targeted_improvement_package"] == TARGETED_PACKAGE
    assert data["delivery_preflight_allowed"] is False


def test_decision_dimensions_preserve_review_artifact_but_require_refinement() -> None:
    data = _artifact()
    assert data["client_readability_decision"] == "acceptable_for_review_artifact_targeted_copy_refinement_before_delivery_preflight"
    assert data["governance_clarity_decision"] == "acceptable_for_review_artifact_targeted_badge_refinement_before_delivery_preflight"
    assert data["ucits_proxy_separation_decision"] == "acceptable_for_review_artifact_preserve_and_polish_client_language"
    assert data["validation_traceability_decision"] == "preserve_machine_checkable_markers_while_reducing_visible_debug_language"


def test_recommended_scope_is_narrow_copy_governance_refinement() -> None:
    data = _artifact()
    scope = set(data["recommended_improvement_scope"])
    assert "client-facing copy refinement" in scope
    assert "visible marker/debug language reduction" in scope
    assert "clearer client-language badges while preserving raw validator markers" in scope
    assert "compact explanation of review evidence versus pricing evidence versus valuation-grade evidence" in scope
    assert "preserve machine-checkable raw markers for validators" in scope


def test_rejected_scopes_prevent_implementation_or_delivery_in_reconcile() -> None:
    data = _artifact()
    rejected = set(data["rejected_scopes"])
    assert "new PDF creation in ETF-EU-WP15I-RECONCILE" in rejected
    assert "renderer change in ETF-EU-WP15I-RECONCILE" in rejected
    assert "premium PDF replacement in ETF-EU-WP15I-RECONCILE" in rejected
    assert "delivery-preflight enablement in ETF-EU-WP15I-RECONCILE" in rejected
    assert "live data fetch or recommendation logic changes" in rejected


def test_no_new_pdf_or_renderer_change() -> None:
    data = _artifact()
    assert data["new_pdf_created"] is False
    assert data["renderer_changed"] is False
    assert data["premium_pdf_replaced"] is False


def test_no_distribution_claim_or_receipt() -> None:
    data = _artifact()
    assert data["outbound_path_enabled"] is False
    assert data["client_distribution_claimed"] is False
    assert data["receipt_artifact_created"] is False
    assert data["production_manifest_created"] is False


def test_authority_boundary_remains_blocked() -> None:
    data = _artifact()
    assert data["delivery_authorization_decision"] == "remain_blocked"
    for key in ["production_delivery", "portfolio_mutation", "candidate_promotion", "funding_authority", "valuation_grade"]:
        assert data[key] is False


def test_selected_next_package_is_namespaced_wp15j() -> None:
    data = _artifact()
    assert data["selected_next_package"] == TARGETED_PACKAGE
    assert data["selected_next_package_title"] == "ETF EU cockpit PDF premium surface targeted copy/governance refinement plan, no delivery"


def test_validator_passes() -> None:
    result = validate_improvement_decision(ARTIFACT)
    assert result["status"] == "valid"
    assert result["selected_next_package"] == TARGETED_PACKAGE
