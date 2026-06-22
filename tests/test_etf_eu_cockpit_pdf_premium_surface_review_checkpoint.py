from __future__ import annotations

import json

from tools.validate_etf_eu_cockpit_pdf_premium_surface_review_checkpoint import (
    ACCEPTABLE,
    ARTIFACT,
    CLOSEOUT_ARTIFACT,
    CLOSEOUT_NOTES,
    DECISION,
    NOTES,
    PLAN_MD,
    PREMIUM_NOTES,
    PREMIUM_PDF,
    validate_review_checkpoint,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_review_checkpoint_json_exists() -> None:
    assert ARTIFACT.exists()


def test_review_checkpoint_notes_exist() -> None:
    assert NOTES.exists()


def test_premium_pdf_exists_and_has_header_and_size() -> None:
    assert PREMIUM_PDF.exists()
    data = PREMIUM_PDF.read_bytes()
    assert data.startswith(b"%PDF")
    assert len(data) > 8500


def test_source_review_artifacts_exist() -> None:
    assert CLOSEOUT_ARTIFACT.exists()
    assert CLOSEOUT_NOTES.exists()
    assert PREMIUM_NOTES.exists()
    assert PLAN_MD.exists()


def test_json_records_package_identity() -> None:
    data = _artifact()
    assert data["work_package"] == "WP15H"
    assert data["source_work_package"] == "WP15G"
    assert data["status"] == "completed"


def test_review_checkpoint_decision_is_conservative() -> None:
    data = _artifact()
    assert data["review_checkpoint_decision"] == DECISION
    assert data["review_checkpoint_created"] is True
    assert data["review_only"] is True


def test_review_statuses_are_acceptable_for_checkpoint() -> None:
    data = _artifact()
    for key in [
        "client_readability_status",
        "governance_clarity_status",
        "ucits_proxy_separation_status",
        "validation_traceability_status",
    ]:
        assert data[key] == ACCEPTABLE


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


def test_selected_next_package_is_wp15i() -> None:
    data = _artifact()
    assert data["selected_next_package"] == "WP15I"


def test_validator_passes() -> None:
    result = validate_review_checkpoint(ARTIFACT)
    assert result["status"] == "valid"
    assert result["selected_next_package"] == "WP15I"
