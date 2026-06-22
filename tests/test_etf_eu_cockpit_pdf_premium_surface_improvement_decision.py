from __future__ import annotations

import json

from tools.validate_etf_eu_cockpit_pdf_premium_surface_improvement_decision import (
    ARTIFACT,
    CLOSEOUT_ARTIFACT,
    KEEP,
    NOTES,
    PREMIUM_PDF,
    REVIEW_ARTIFACT,
    REVIEW_NOTES,
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


def test_json_records_package_identity() -> None:
    data = _artifact()
    assert data["work_package"] == "WP15I"
    assert data["source_work_package"] == "WP15H"
    assert data["status"] == "completed"


def test_improvement_decision_exists() -> None:
    data = _artifact()
    assert data["improvement_decision_created"] is True
    assert data["improvement_decision"] in {"keep_current_premium_surface", "create_targeted_improvement_package"}


def test_keep_current_surface_decision_consistency() -> None:
    data = _artifact()
    assert data["improvement_decision"] == KEEP
    assert data["targeted_improvement_package_required"] is False
    assert data["targeted_improvement_package"] is None


def test_decision_dimensions_are_acceptable_no_immediate_iteration() -> None:
    data = _artifact()
    for key in [
        "client_readability_decision",
        "governance_clarity_decision",
        "ucits_proxy_separation_decision",
        "validation_traceability_decision",
    ]:
        assert data[key] == "acceptable_no_immediate_iteration"


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


def test_selected_next_package_is_wp15j() -> None:
    data = _artifact()
    assert data["selected_next_package"] == "WP15J"


def test_validator_passes() -> None:
    result = validate_improvement_decision(ARTIFACT)
    assert result["status"] == "valid"
    assert result["selected_next_package"] == "WP15J"
