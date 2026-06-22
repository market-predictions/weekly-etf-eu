from __future__ import annotations

import json

from tools.validate_etf_eu_cockpit_pdf_premium_surface_targeted_copy_governance_refinement_plan import (
    ARTIFACT,
    NOTES,
    PREMIUM_PDF,
    SOURCE_DECISION,
    validate_targeted_refinement_plan,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_plan_json_exists() -> None:
    assert ARTIFACT.exists()


def test_plan_notes_exist() -> None:
    assert NOTES.exists()


def test_premium_pdf_exists_and_has_header_and_size() -> None:
    assert PREMIUM_PDF.exists()
    data = PREMIUM_PDF.read_bytes()
    assert data.startswith(b"%PDF")
    assert len(data) > 8500


def test_source_improvement_decision_artifact_exists() -> None:
    assert SOURCE_DECISION.exists()


def test_json_records_namespaced_wp15j_identity() -> None:
    data = _artifact()
    assert data["repository"] == "market-predictions/weekly-etf-eu"
    assert data["work_package_id"] == "ETF-EU-WP15J"
    assert data["legacy_work_package_id"] == "WP15J"
    assert data["status"] == "completed"


def test_json_records_reconcile_as_source_package() -> None:
    data = _artifact()
    assert data["source_work_package"] == "ETF-EU-WP15I-RECONCILE"


def test_targeted_refinement_plan_created_without_implementation() -> None:
    data = _artifact()
    assert data["targeted_refinement_plan_created"] is True
    assert data["targeted_refinement_plan_decision"] == "plan_future_copy_governance_refinement"
    assert data["implementation_in_this_package"] is False


def test_premium_pdf_is_preserved() -> None:
    data = _artifact()
    assert data["premium_pdf_path"] == str(PREMIUM_PDF)
    assert data["premium_pdf_commit"] == "fb7751026a70db355385946ee3882c68f9ec0e71"
    assert data["premium_pdf_preserved"] is True


def test_improvement_decision_remains_targeted_package() -> None:
    data = _artifact()
    assert data["improvement_decision"] == "create_targeted_improvement_package"
    assert data["keep_as_current_review_artifact"] is True
    assert data["targeted_improvement_needed"] is True
    assert data["targeted_improvement_package_required"] is True
    assert data["targeted_improvement_package"] == "ETF-EU-WP15J"


def test_refinement_scope_and_out_of_scope_are_not_empty() -> None:
    data = _artifact()
    assert data["refinement_scope"]
    assert data["out_of_scope"]


def test_no_pdf_or_renderer_change() -> None:
    data = _artifact()
    assert data["new_pdf_created"] is False
    assert data["renderer_changed"] is False
    assert data["premium_pdf_replaced"] is False


def test_no_distribution_or_delivery_artifacts() -> None:
    data = _artifact()
    assert data["outbound_path_enabled"] is False
    assert data["client_distribution_claimed"] is False
    assert data["receipt_artifact_created"] is False
    assert data["production_manifest_created"] is False


def test_authority_boundary_remains_blocked() -> None:
    data = _artifact()
    assert data["delivery_authorization_decision"] == "remain_blocked"
    assert data["delivery_preflight_allowed"] is False
    for key in ["production_delivery", "portfolio_mutation", "candidate_promotion", "funding_authority", "valuation_grade"]:
        assert data[key] is False


def test_selected_next_package_is_wp15k() -> None:
    data = _artifact()
    assert data["selected_next_package"] == "ETF-EU-WP15K"


def test_validator_passes() -> None:
    result = validate_targeted_refinement_plan(ARTIFACT)
    assert result["status"] == "valid"
    assert result["selected_next_package"] == "ETF-EU-WP15K"
