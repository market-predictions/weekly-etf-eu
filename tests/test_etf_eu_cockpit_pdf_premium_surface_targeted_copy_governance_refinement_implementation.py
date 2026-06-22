from __future__ import annotations

import json

from tools.validate_etf_eu_cockpit_pdf_premium_surface_targeted_copy_governance_refinement_implementation import (
    ARTIFACT,
    NOTES,
    PREMIUM_PDF,
    SOURCE_PLAN,
    SOURCE_PLAN_NOTES,
    validate_targeted_refinement_implementation,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_implementation_json_exists() -> None:
    assert ARTIFACT.exists()


def test_implementation_notes_exist() -> None:
    assert NOTES.exists()


def test_source_wp15j_plan_artifacts_exist() -> None:
    assert SOURCE_PLAN.exists()
    assert SOURCE_PLAN_NOTES.exists()


def test_premium_pdf_baseline_exists_and_has_header_and_size() -> None:
    assert PREMIUM_PDF.exists()
    data = PREMIUM_PDF.read_bytes()
    assert data.startswith(b"%PDF")
    assert len(data) > 8500


def test_json_records_wp15k_identity() -> None:
    data = _artifact()
    assert data["repository"] == "market-predictions/weekly-etf-eu"
    assert data["work_package_id"] == "ETF-EU-WP15K"
    assert data["legacy_work_package_id"] == "WP15K"
    assert data["status"] == "completed"


def test_json_records_wp15j_as_source_package() -> None:
    assert _artifact()["source_work_package"] == "ETF-EU-WP15J"


def test_implementation_created_and_not_delivery() -> None:
    data = _artifact()
    assert data["implementation_created"] is True
    assert data["implementation_decision"] == "implement_narrow_copy_governance_refinement"
    assert data["implementation_scope"] == "narrow_copy_governance_refinement"
    assert data["implementation_is_delivery"] is False


def test_refinement_contracts_are_present() -> None:
    data = _artifact()
    assert data["refinement_implemented"]
    assert data["client_facing_copy_contract"]
    assert data["governance_badge_contract"]


def test_validator_markers_ucits_and_review_status_preserved() -> None:
    data = _artifact()
    assert data["validator_marker_preservation"] is True
    assert data["ucits_proxy_separation_preserved"] is True
    assert data["review_only_status_preserved"] is True
    assert data["delivery_authority_preserved_as_blocked"] is True


def test_premium_pdf_baseline_preserved_and_not_replaced() -> None:
    data = _artifact()
    assert data["premium_pdf_baseline_path"] == str(PREMIUM_PDF)
    assert data["premium_pdf_baseline_commit"] == "fb7751026a70db355385946ee3882c68f9ec0e71"
    assert data["premium_pdf_baseline_preserved"] is True
    assert data["premium_pdf_replaced"] is False


def test_no_pdf_or_renderer_change() -> None:
    data = _artifact()
    assert data["new_pdf_created"] is False
    assert data["renderer_changed"] is False
    assert data["changed_source_paths"] == []


def test_no_distribution_receipt_or_manifest() -> None:
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
    for key in ["production_delivery", "portfolio_mutation", "candidate_promotion", "funding_authority", "valuation_grade"]:
        assert data[key] is False


def test_selected_next_package_is_wp15l() -> None:
    assert _artifact()["selected_next_package"] == "ETF-EU-WP15L"


def test_validator_passes() -> None:
    result = validate_targeted_refinement_implementation(ARTIFACT)
    assert result["status"] == "valid"
    assert result["selected_next_package"] == "ETF-EU-WP15L"
