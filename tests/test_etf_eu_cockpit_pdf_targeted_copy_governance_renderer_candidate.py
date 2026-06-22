from __future__ import annotations

import json

from runtime.build_etf_eu_cockpit_pdf_targeted_copy_governance_renderer_candidate import OUTPUT as PDF_CANDIDATE
from runtime.build_etf_eu_cockpit_pdf_targeted_copy_governance_renderer_candidate import main as build_pdf_candidate
from tools.validate_etf_eu_cockpit_pdf_targeted_copy_governance_renderer_candidate import (
    ARTIFACT,
    NOTES,
    PREMIUM_PDF,
    SOURCE_IMPL,
    SOURCE_REVIEW,
    validate_renderer_candidate,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_artifact_and_notes_exist() -> None:
    assert ARTIFACT.exists()
    assert NOTES.exists()


def test_source_artifacts_exist() -> None:
    assert SOURCE_REVIEW.exists()
    assert SOURCE_IMPL.exists()
    assert PREMIUM_PDF.exists()


def test_builder_produces_review_only_pdf_candidate() -> None:
    build_pdf_candidate()
    assert PDF_CANDIDATE.exists()
    data = PDF_CANDIDATE.read_bytes()
    assert data.startswith(b"%PDF")
    assert len(data) > 1000
    assert b"review-only" in data
    assert b"not delivered" in data
    assert b"delivery_authorization_decision=remain_blocked" in data


def test_json_records_wp15m_identity_and_source() -> None:
    data = _artifact()
    assert data["repository"] == "market-predictions/weekly-etf-eu"
    assert data["work_package_id"] == "ETF-EU-WP15M"
    assert data["legacy_work_package_id"] == "WP15M"
    assert data["source_work_package"] == "ETF-EU-WP15L"


def test_hard_build_requirement_is_recorded() -> None:
    data = _artifact()
    assert data["review_only_pdf_candidate_required"] is True
    assert data["review_only_pdf_candidate_created"] is True
    assert "must produce" in data["hard_build_requirement"]
    assert data["pdf_candidate_path"] == str(PDF_CANDIDATE)


def test_candidate_is_review_only_and_not_delivery() -> None:
    data = _artifact()
    assert data["pdf_candidate_is_delivery"] is False
    assert data["pdf_candidate_is_production_delivery"] is False
    assert data["pdf_candidate_is_review_only"] is True
    assert data["production_delivery"] is False


def test_renderer_and_pdf_candidate_flags() -> None:
    data = _artifact()
    assert data["new_pdf_created"] is True
    assert data["renderer_changed"] is True
    assert data["changed_source_paths"] == ["runtime/build_etf_eu_cockpit_pdf_targeted_copy_governance_renderer_candidate.py"]
    assert data["premium_pdf_replaced"] is False


def test_preservation_flags_are_true() -> None:
    data = _artifact()
    assert data["premium_pdf_baseline_preserved"] is True
    assert data["validator_marker_preservation"] is True
    assert data["ucits_proxy_separation_preserved"] is True
    assert data["review_only_status_preserved"] is True
    assert data["delivery_authority_preserved_as_blocked"] is True


def test_no_delivery_or_distribution_claim() -> None:
    data = _artifact()
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


def test_selected_next_package_is_wp15n() -> None:
    assert _artifact()["selected_next_package"] == "ETF-EU-WP15N"


def test_validator_passes() -> None:
    result = validate_renderer_candidate(ARTIFACT)
    assert result["status"] == "valid"
    assert result["pdf"] == str(PDF_CANDIDATE)
    assert result["selected_next_package"] == "ETF-EU-WP15N"
