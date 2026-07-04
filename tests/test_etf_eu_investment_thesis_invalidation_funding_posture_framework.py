from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_investment_thesis_invalidation_funding_posture_framework import (
    ARTIFACT,
    FRAMEWORK,
    NOTES,
    REQUIRED_FUND_FIELDS,
    REQUIRED_INVALIDATION_CATEGORIES,
    REQUIRED_LINE_FIELDS,
    REQUIRED_RESOLVED_GAPS,
    validate,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_expected_files_exist() -> None:
    assert FRAMEWORK.exists()
    assert ARTIFACT.exists()
    assert NOTES.exists()


def test_artifact_identity_and_sources_are_correct() -> None:
    data = _artifact()
    assert data["work_package_id"] == "ETF-EU-WP15AJ"
    assert data["source_work_package"] == "ETF-EU-WP15AI"
    assert data["repository"] == "market-predictions/weekly-etf-eu"
    assert data["readiness_gate_status"] == "decision_framework_defined_not_client_grade"
    assert data["source_investability_evidence_artifact"] == "output/client_surface/etf_eu_priips_kid_liquidity_spread_evidence_20260703_000000.json"
    assert data["source_policy_artifact"] == "output/client_surface/etf_eu_pricing_freshness_valuation_policy_20260703_000000.json"
    assert data["source_product_facts_artifact"] == "output/client_surface/etf_eu_product_facts_evidence_20260703_000000.json"
    assert data["framework_path"] == "control/ETF_EU_INVESTMENT_THESIS_INVALIDATION_FUNDING_POSTURE_FRAMEWORK_V1.md"


def test_framework_flags_are_true() -> None:
    data = _artifact()
    assert data["investment_thesis_framework_created"] is True
    assert data["invalidation_criteria_framework_created"] is True
    assert data["funding_posture_framework_created"] is True
    assert data["decision_framework_validated"] is True
    assert data["accepted_review_only_foundation"] is True


def test_authority_claims_remain_false() -> None:
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
        "candidate_promotion",
        "pricing_evidence_for_client_grade",
        "pricing_evidence_for_delivery_preflight",
        "live_price_fetch_performed",
        "live_data_fetch_performed",
        "pricing_evidence_changed",
        "source_pdf_replaced",
        "new_pdf_created",
        "renderer_changed",
    ]:
        assert data[key] is False


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


def test_fund_level_framework_fields_exist() -> None:
    fund = _artifact()["fund_level_decision_framework"]
    assert REQUIRED_FUND_FIELDS.issubset(set(fund))
    assert fund["isin"] == "IE00B5BMR087"
    assert fund["fund_name"] == "iShares Core S&P 500 UCITS ETF USD (Acc)"
    assert fund["issuer"] == "iShares / BlackRock"
    assert fund["review_only_candidate_status"] == "review_only_candidate_not_funded"
    assert fund["funding_posture_status"] == "not_funded_framework_only"
    assert fund["cash_posture_status"] == "not_set"
    assert fund["portfolio_action_status"] == "no_portfolio_action"
    assert fund["funding_decision_status"] == "no_funding_decision"


def test_line_level_framework_is_valid() -> None:
    lines = {line["symbol"]: line for line in _artifact()["line_level_decision_framework"]}
    assert set(lines) == {"SXR8.DE", "CSPX.L"}
    assert lines["SXR8.DE"]["line_selection_status"] == "needs_cross_check"
    assert lines["CSPX.L"]["line_selection_status"] == "review_only_line_candidate"
    for line in lines.values():
        assert REQUIRED_LINE_FIELDS.issubset(set(line))
        assert line["isin"] == "IE00B5BMR087"
        assert line["line_status"] == "success"
        assert line["freshness_policy_status"] == "current_completed_session"


def test_invalidation_criteria_are_complete() -> None:
    criteria = _artifact()["invalidation_criteria_framework"]
    assert {item["criterion_id"] for item in criteria} == REQUIRED_INVALIDATION_CATEGORIES


def test_resolved_gaps_and_blockers_are_valid() -> None:
    data = _artifact()
    assert set(data["resolved_decision_framework_gaps"]) == REQUIRED_RESOLVED_GAPS
    assert data["remaining_client_grade_blockers"] == ["client_language_quality_gate"]
    assert data["remaining_delivery_preflight_blockers"]


def test_source_manifest_is_valid() -> None:
    manifest = _artifact()["source_manifest"]
    assert manifest
    used = " ".join(" ".join(source["used_for_fields"]) for source in manifest)
    assert "investment thesis framework" in used
    assert "invalidation criteria framework" in used
    assert "funding posture framework" in used


def test_notes_contain_required_sections() -> None:
    text = NOTES.read_text(encoding="utf-8")
    for marker in [
        "# ETF-EU-WP15AJ investment thesis, invalidation criteria, and funding posture framework",
        "## Scope",
        "## Source artifacts",
        "## Framework document",
        "## Fund-level decision framework",
        "## Line-level decision framework",
        "## Invalidation criteria framework",
        "## Funding posture framework",
        "## Resolved decision-framework gaps",
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
    assert result["work_package_id"] == "ETF-EU-WP15AJ"
    assert result["readiness_gate_status"] == "decision_framework_defined_not_client_grade"
    assert result["investment_thesis_framework_created"] is True
    assert result["invalidation_criteria_framework_created"] is True
    assert result["funding_posture_framework_created"] is True
    assert result["decision_framework_validated"] is True
    assert result["resolved_decision_framework_gaps_count"] == 3
    assert result["client_grade_claim"] is False
    assert result["delivery_preflight_allowed"] is False
    assert result["valuation_grade"] is False
    assert result["funding_authority"] is False
    assert result["portfolio_mutation"] is False
    assert result["selected_next_package"] == "ETF-EU-WP15AK"
