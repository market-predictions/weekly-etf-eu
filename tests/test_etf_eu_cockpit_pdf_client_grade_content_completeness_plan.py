from __future__ import annotations

import json

from tools.validate_etf_eu_cockpit_pdf_client_grade_content_completeness_plan import (
    ARTIFACT,
    CONTRACT,
    NOTES,
    SOURCE_PDF,
    SOURCE_REVIEW_ARTIFACT,
    SOURCE_REVIEW_NOTES,
    validate_client_grade_content_completeness_plan,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_wp15q_files_exist() -> None:
    assert ARTIFACT.exists()
    assert NOTES.exists()
    assert CONTRACT.exists()


def test_source_wp15p_and_pdf_inputs_exist() -> None:
    assert SOURCE_REVIEW_ARTIFACT.exists()
    assert SOURCE_REVIEW_NOTES.exists()
    assert SOURCE_PDF.exists()
    assert SOURCE_PDF.read_bytes().startswith(b"%PDF")


def test_artifact_identity_and_paths() -> None:
    data = _artifact()
    assert data["repository"] == "market-predictions/weekly-etf-eu"
    assert data["work_package_id"] == "ETF-EU-WP15Q"
    assert data["legacy_work_package_id"] == "WP15Q"
    assert data["source_work_package"] == "ETF-EU-WP15P"
    assert data["content_contract_path"] == str(CONTRACT)
    assert data["content_plan_artifact"] == str(ARTIFACT)
    assert data["content_plan_notes"] == str(NOTES)


def test_contract_and_plan_flags_are_true() -> None:
    data = _artifact()
    assert data["client_grade_content_contract_created"] is True
    assert data["content_completeness_plan_created"] is True
    assert data["content_completeness_validation_required"] is True
    assert data["actual_pdf_candidate_reviewed_in_source_package"] is True
    assert data["validator_created"] is True
    assert data["tests_created"] is True


def test_wp15q_does_not_claim_client_grade_or_delivery_ready() -> None:
    data = _artifact()
    assert data["client_grade_status_after_wp15q"] == "not_yet_client_grade_contract_defined_only"
    assert data["client_grade_claim"] is False
    assert data["client_grade_enough_for_delivery_preflight_discussion"] is False
    assert data["delivery_ready"] is False
    assert data["delivery_preflight_allowed"] is False


def test_required_content_sections_are_complete() -> None:
    data = _artifact()
    assert len(data["required_decision_framework_sections"]) >= 7
    assert len(data["required_input_state_sections"]) >= 10
    assert len(data["required_output_sections"]) >= 12
    assert "portfolio holdings and cash snapshot" in data["required_output_sections"]
    assert "pricing and freshness evidence table" in data["required_output_sections"]
    assert "proxy and benchmark disclosure" in data["required_output_sections"]


def test_minimum_visible_fields_include_ucits_and_pricing_fields() -> None:
    fields = set(_artifact()["minimum_visible_fields_for_funded_or_investable_rows"])
    for field in [
        "isin",
        "ucits_status",
        "priips_kid_status",
        "exchange_ticker",
        "trading_currency",
        "latest_close_date",
        "latest_close",
        "pricing_source",
        "pricing_freshness_status",
    ]:
        assert field in fields


def test_required_operational_validators_include_core_safety_gates() -> None:
    validators = set(_artifact()["required_operational_validators"])
    for validator in [
        "content_completeness",
        "no_us_etf_as_eu_holding",
        "isin_first_holdings",
        "ucits_status_present",
        "priips_kid_status_present",
        "pricing_source_and_freshness_present",
        "proxy_disclosure_present",
        "delivery_boundary_markers_present",
    ]:
        assert validator in validators


def test_no_authority_or_output_mutation_boundary_changed() -> None:
    data = _artifact()
    assert data["new_pdf_created"] is False
    assert data["renderer_changed"] is False
    assert data["source_pdf_replaced"] is False
    assert data["production_delivery"] is False
    assert data["portfolio_mutation"] is False
    assert data["candidate_promotion"] is False
    assert data["funding_authority"] is False
    assert data["valuation_grade"] is False
    assert data["outbound_path_enabled"] is False
    assert data["receipt_artifact_created"] is False
    assert data["production_manifest_created"] is False


def test_no_live_data_pricing_or_recommendation_change() -> None:
    data = _artifact()
    assert data["live_data_fetch_performed"] is False
    assert data["pricing_evidence_changed"] is False
    assert data["recommendation_logic_changed"] is False


def test_contract_records_four_layers_and_no_delivery_boundary() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    assert "Decision framework layer" in text
    assert "Input/state contract layer" in text
    assert "Output contract layer" in text
    assert "Operational runbook layer" in text
    assert "production_delivery=false" in text
    assert "ETF-EU-WP15R" in text


def test_notes_record_next_package_and_boundaries() -> None:
    text = NOTES.read_text(encoding="utf-8")
    assert "work_package_id=ETF-EU-WP15Q" in text
    assert "selected_next_package=ETF-EU-WP15R" in text
    assert "production_delivery=false" in text
    assert "valuation_grade=false" in text
    assert "new_pdf_created=false" in text


def test_selected_next_package_is_wp15r() -> None:
    assert _artifact()["selected_next_package"] == "ETF-EU-WP15R"


def test_validator_passes() -> None:
    result = validate_client_grade_content_completeness_plan(ARTIFACT)
    assert result["status"] == "valid"
    assert result["contract"] == str(CONTRACT)
    assert result["selected_next_package"] == "ETF-EU-WP15R"
