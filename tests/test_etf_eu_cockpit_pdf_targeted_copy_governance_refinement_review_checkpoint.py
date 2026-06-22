from __future__ import annotations

import json

from tools.validate_etf_eu_cockpit_pdf_targeted_copy_governance_refinement_review_checkpoint import (
    ARTIFACT,
    NOTES,
    PREMIUM_PDF,
    SOURCE_IMPL,
    SOURCE_IMPL_NOTES,
    SOURCE_PLAN,
    validate_review_checkpoint,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_review_checkpoint_json_exists() -> None:
    assert ARTIFACT.exists()


def test_review_checkpoint_notes_exist() -> None:
    assert NOTES.exists()


def test_source_artifacts_exist() -> None:
    assert SOURCE_IMPL.exists()
    assert SOURCE_IMPL_NOTES.exists()
    assert SOURCE_PLAN.exists()


def test_premium_pdf_baseline_exists_and_has_header_and_size() -> None:
    assert PREMIUM_PDF.exists()
    data = PREMIUM_PDF.read_bytes()
    assert data.startswith(b"%PDF")
    assert len(data) > 8500


def test_json_records_wp15l_identity() -> None:
    data = _artifact()
    assert data["repository"] == "market-predictions/weekly-etf-eu"
    assert data["work_package_id"] == "ETF-EU-WP15L"
    assert data["legacy_work_package_id"] == "WP15L"
    assert data["status"] == "completed"


def test_json_records_wp15k_as_source_package() -> None:
    assert _artifact()["source_work_package"] == "ETF-EU-WP15K"


def test_review_checkpoint_created_and_decision_accepts_contract() -> None:
    data = _artifact()
    assert data["review_checkpoint_created"] is True
    assert data["review_checkpoint_decision"] == "accept_contract_refinement_and_request_scoped_renderer_pdf_candidate"
    assert data["implementation_review_status"] == "accepted_as_contract_layer"
    assert data["renderer_pdf_candidate_required"] is True


def test_implementation_remains_no_delivery() -> None:
    data = _artifact()
    assert data["implementation_is_delivery"] is False
    assert data["production_delivery"] is False


def test_preservation_flags_are_true() -> None:
    data = _artifact()
    assert data["validator_marker_preservation"] is True
    assert data["ucits_proxy_separation_preserved"] is True
    assert data["review_only_status_preserved"] is True
    assert data["delivery_authority_preserved_as_blocked"] is True
    assert data["premium_pdf_baseline_preserved"] is True


def test_review_lists_are_not_empty() -> None:
    data = _artifact()
    assert data["review_findings"]
    assert data["accepted_contract_elements"]
    assert data["remaining_gap"]


def test_no_pdf_renderer_or_premium_replacement() -> None:
    data = _artifact()
    assert data["new_pdf_created"] is False
    assert data["renderer_changed"] is False
    assert data["premium_pdf_replaced"] is False


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


def test_selected_next_package_is_wp15m() -> None:
    assert _artifact()["selected_next_package"] == "ETF-EU-WP15M"


def test_validator_passes() -> None:
    result = validate_review_checkpoint(ARTIFACT)
    assert result["status"] == "valid"
    assert result["selected_next_package"] == "ETF-EU-WP15M"
