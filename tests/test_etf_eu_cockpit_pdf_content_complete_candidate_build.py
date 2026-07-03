from __future__ import annotations

import json

from runtime.build_etf_eu_cockpit_pdf_content_complete_candidate import OUTPUT as CONTENT_COMPLETE_PDF
from runtime.build_etf_eu_cockpit_pdf_content_complete_candidate import main as build_content_complete_pdf
from tools.validate_etf_eu_cockpit_pdf_content_complete_candidate_build import (
    ARTIFACT,
    CONTRACT,
    NOTES,
    SOURCE_PLAN,
    SOURCE_PLAN_NOTES,
    validate_content_complete_candidate_build,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_wp15r_files_exist() -> None:
    assert ARTIFACT.exists()
    assert NOTES.exists()
    assert CONTRACT.exists()
    assert SOURCE_PLAN.exists()
    assert SOURCE_PLAN_NOTES.exists()


def test_builder_produces_content_complete_pdf_candidate() -> None:
    build_content_complete_pdf()
    assert CONTENT_COMPLETE_PDF.exists()
    data = CONTENT_COMPLETE_PDF.read_bytes()
    assert data.startswith(b"%PDF")
    assert len(data) > 9000
    assert b"ETF EU Cockpit Content-Complete Candidate" in data


def test_pdf_contains_all_required_visible_sections() -> None:
    build_content_complete_pdf()
    data = CONTENT_COMPLETE_PDF.read_bytes()
    for marker in [
        b"1. Cockpit header with report date and authority markers",
        b"2. Executive read and action summary",
        b"3. Portfolio holdings and cash snapshot",
        b"4. Allocation and concentration summary",
        b"5. UCITS investability table",
        b"6. Pricing and freshness evidence table",
        b"7. Holding-level decision table",
        b"8. Watchlist and candidate pipeline with promotion status",
        b"9. Risk, regime and event context",
        b"10. Proxy and benchmark disclosure",
        b"11. Unresolved-data and limitation block",
        b"12. Validation and governance footer",
    ]:
        assert marker in data


def test_pdf_preserves_delivery_and_authority_markers() -> None:
    build_content_complete_pdf()
    data = CONTENT_COMPLETE_PDF.read_bytes()
    for marker in [
        b"REVIEW-ONLY",
        b"NOT DELIVERED",
        b"NO RECEIPT",
        b"NO PRODUCTION MANIFEST",
        b"AUTHORITY BLOCKED",
        b"production_delivery=false",
        b"valuation_grade=false",
        b"funding_authority=false",
        b"portfolio_mutation=false",
        b"delivery_authorization_decision=remain_blocked",
    ]:
        assert marker in data


def test_artifact_identity_and_paths() -> None:
    data = _artifact()
    assert data["repository"] == "market-predictions/weekly-etf-eu"
    assert data["work_package_id"] == "ETF-EU-WP15R"
    assert data["legacy_work_package_id"] == "WP15R"
    assert data["source_work_package"] == "ETF-EU-WP15Q"
    assert data["content_contract_path"] == str(CONTRACT)
    assert data["source_content_plan_artifact"] == str(SOURCE_PLAN)
    assert data["source_content_plan_notes"] == str(SOURCE_PLAN_NOTES)
    assert data["content_complete_pdf_candidate_path"] == str(CONTENT_COMPLETE_PDF)


def test_build_flags_are_true() -> None:
    data = _artifact()
    assert data["content_complete_pdf_candidate_created"] is True
    assert data["review_only_content_complete_candidate_created"] is True
    assert data["builder_created"] is True
    assert data["new_pdf_created"] is True
    assert data["renderer_changed"] is True
    assert data["content_contract_followed"] is True
    assert data["content_completeness_candidate"] is True
    assert data["validator_created"] is True
    assert data["tests_created"] is True


def test_candidate_includes_contract_sections_and_fields() -> None:
    data = _artifact()
    assert data["visible_page_count"] == 3
    assert len(data["visible_sections_present"]) >= 12
    assert len(data["minimum_visible_fields_for_funded_or_investable_rows_included"]) >= 17
    assert "UCITS investability table" in data["visible_sections_present"]
    assert "pricing and freshness evidence table" in data["visible_sections_present"]
    assert "unresolved-data and limitation block" in data["visible_sections_present"]


def test_candidate_represents_static_ucits_rows_without_funding() -> None:
    data = _artifact()
    assert data["funded_holdings_status"] == "none_cash_only_review_surface"
    assert data["funded_etf_holdings_count"] == 0
    assert data["cash_snapshot_included"] is True
    assert data["candidate_pipeline_included"] is True
    assert len(data["candidate_rows_represented"]) >= 4
    assert "IE00B5BMR087 iShares Core S&P 500 UCITS ETF SXR8.DE verified_candidate_not_funded" in data["candidate_rows_represented"]


def test_proxy_and_pricing_disclosures_are_present() -> None:
    data = _artifact()
    assert data["proxy_disclosure_included"] is True
    assert data["unresolved_data_block_included"] is True
    assert "SPY SMH GLD PAVE" in data["us_proxy_disclosure"]
    assert data["pricing_surface_status"] == "not_refreshed_in_wp15r_unresolved_for_review_candidate"
    assert data["portfolio_reconciliation_status"] == "not_applicable_no_valuation_surface_promoted_and_no_funded_holdings"


def test_no_client_grade_or_delivery_preflight_claim() -> None:
    data = _artifact()
    assert data["client_grade_status_after_wp15r"] == "not_yet_client_grade_review_only_candidate_built"
    assert data["client_grade_claim"] is False
    assert data["client_grade_enough_for_delivery_preflight_discussion"] is False
    assert data["delivery_ready"] is False
    assert data["delivery_preflight_allowed"] is False


def test_no_forbidden_authority_or_state_changes() -> None:
    data = _artifact()
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


def test_notes_record_candidate_and_boundaries() -> None:
    notes = NOTES.read_text(encoding="utf-8")
    assert "work_package_id=ETF-EU-WP15R" in notes
    assert "content_complete_pdf_candidate_path=output/client_surface/etf_eu_cockpit_pdf_content_complete_candidate_20260703_000000.pdf" in notes
    assert "production_delivery=false" in notes
    assert "valuation_grade=false" in notes
    assert "live_data_fetch_performed=false" in notes
    assert "ETF-EU-WP15S" in notes


def test_selected_next_package_is_wp15s() -> None:
    assert _artifact()["selected_next_package"] == "ETF-EU-WP15S"


def test_validator_passes() -> None:
    result = validate_content_complete_candidate_build(ARTIFACT)
    assert result["status"] == "valid"
    assert result["pdf"] == str(CONTENT_COMPLETE_PDF)
    assert result["selected_next_package"] == "ETF-EU-WP15S"
