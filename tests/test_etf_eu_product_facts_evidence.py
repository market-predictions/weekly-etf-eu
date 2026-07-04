from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_product_facts_evidence import NOTES, PRODUCT_FACTS, validate


def _artifact() -> dict:
    return json.loads(PRODUCT_FACTS.read_text(encoding="utf-8"))


def test_expected_files_exist() -> None:
    assert PRODUCT_FACTS.exists()
    assert NOTES.exists()


def test_artifact_identity_is_correct() -> None:
    data = _artifact()
    assert data["work_package_id"] == "ETF-EU-WP15AG"
    assert data["source_work_package"] == "ETF-EU-WP15AF"
    assert data["repository"] == "market-predictions/weekly-etf-eu"
    assert data["readiness_gate_status"] == "product_facts_acquired_not_client_grade"


def test_source_paths_are_correct() -> None:
    data = _artifact()
    assert data["source_acquisition_plan_artifact"] == "output/client_surface/etf_eu_cockpit_pdf_client_grade_evidence_acquisition_plan_20260703_000000.json"
    assert data["source_gap_audit_artifact"] == "output/client_surface/etf_eu_cockpit_pdf_client_grade_evidence_gap_audit_20260703_000000.json"
    assert data["source_review_only_pdf"] == "output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.pdf"


def test_product_facts_flags_are_true() -> None:
    data = _artifact()
    assert data["product_facts_evidence_acquired"] is True
    assert data["product_facts_evidence_validated"] is True
    assert data["accepted_review_only_foundation"] is True


def test_client_grade_and_delivery_claims_remain_false() -> None:
    data = _artifact()
    for key in [
        "client_grade_claim",
        "client_grade_enough_for_delivery_preflight_discussion",
        "delivery_ready",
        "delivery_preflight_allowed",
        "outbound_path_enabled",
        "production_delivery",
        "receipt_artifact_created",
        "production_manifest_created",
        "valuation_grade",
        "funding_authority",
        "portfolio_mutation",
        "pricing_evidence_for_client_grade",
        "pricing_evidence_for_delivery_preflight",
    ]:
        assert data[key] is False


def test_fund_product_facts_exist() -> None:
    fund = _artifact()["fund_product_facts"]
    assert fund
    assert fund["isin"] == "IE00B5BMR087"
    assert fund["fund_name"]
    assert fund["issuer"]


def test_required_product_facts_have_sources() -> None:
    fund = _artifact()["fund_product_facts"]
    for field in [
        "TER_or_ongoing_charge",
        "replication_method",
        "distribution_policy",
        "hedged_unhedged_status",
    ]:
        assert fund[field]
        assert fund[f"{field}_source"]
        assert fund[f"{field}_source_date"]
        assert fund["field_confidence"][field] in {"confirmed", "needs_cross_check", "not_found", "not_applicable"}


def test_trading_line_facts_include_sxr8_and_cspx() -> None:
    lines = {line["symbol"]: line for line in _artifact()["trading_line_facts"]}
    assert "SXR8.DE" in lines
    assert "CSPX.L" in lines
    assert lines["SXR8.DE"]["isin"] == "IE00B5BMR087"
    assert lines["CSPX.L"]["isin"] == "IE00B5BMR087"
    assert lines["SXR8.DE"]["maps_to_same_fund"] is True
    assert lines["CSPX.L"]["maps_to_same_fund"] is True


def test_resolved_product_fact_gaps_include_four_required_gaps() -> None:
    resolved = set(_artifact()["resolved_product_fact_gaps"])
    assert resolved == {
        "TER_or_ongoing_charge_evidence",
        "replication_method_evidence",
        "distribution_policy_evidence",
        "hedged_unhedged_status_evidence",
    }


def test_remaining_blockers_are_non_empty() -> None:
    data = _artifact()
    assert data["remaining_client_grade_blockers"]
    assert data["remaining_delivery_preflight_blockers"]


def test_source_manifest_is_valid() -> None:
    manifest = _artifact()["source_manifest"]
    assert manifest
    assert any(source["authority_level"] == "official_issuer" for source in manifest)
    for source in manifest:
        assert source["source_id"]
        assert source["source_reference"]
        assert source["retrieval_timestamp"]
        assert source["used_for_fields"]


def test_source_values_remain_fixed() -> None:
    data = _artifact()
    assert data["successful_rows_count"] == 2
    assert data["failed_rows_count"] == 0
    assert data["skipped_rows_count"] == 1
    assert data["first_successful_symbol"] == "SXR8.DE"
    assert data["first_successful_close_date"] == "2026-07-03"
    assert data["first_successful_close"] == 706.119995
    assert data["second_successful_symbol"] == "CSPX.L"
    assert data["second_successful_close_date"] == "2026-07-03"
    assert data["second_successful_close"] == 807.859985
    assert data["smh_status"] == "skipped_pending_registry_status"


def test_no_live_price_pdf_renderer_or_delivery_action_occurred() -> None:
    data = _artifact()
    for key in [
        "live_price_fetch_performed",
        "live_data_fetch_performed",
        "pricing_evidence_changed",
        "source_pdf_replaced",
        "new_pdf_created",
        "renderer_changed",
        "receipt_artifact_created",
        "production_manifest_created",
    ]:
        assert data[key] is False


def test_notes_contain_required_sections() -> None:
    text = NOTES.read_text(encoding="utf-8")
    for marker in [
        "# ETF-EU-WP15AG product facts evidence",
        "## Scope",
        "## Source artifacts",
        "## Source manifest",
        "## Fund-level evidence",
        "## Trading-line evidence",
        "## Resolved product-fact gaps",
        "## Remaining client-grade blockers",
        "## Remaining delivery-preflight blockers",
        "## Boundary checks",
        "## Decision",
        "## Next package",
    ]:
        assert marker in text


def test_validator_passes() -> None:
    result = validate()
    assert result["status"] == "valid"
    assert result["work_package_id"] == "ETF-EU-WP15AG"
    assert result["readiness_gate_status"] == "product_facts_acquired_not_client_grade"
    assert result["product_facts_evidence_acquired"] is True
    assert result["product_facts_evidence_validated"] is True
    assert result["resolved_product_fact_gaps_count"] == 4
    assert result["client_grade_claim"] is False
    assert result["delivery_preflight_allowed"] is False
    assert result["selected_next_package"] == "ETF-EU-WP15AH"
