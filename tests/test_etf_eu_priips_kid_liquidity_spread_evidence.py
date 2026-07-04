from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_priips_kid_liquidity_spread_evidence import (
    EVIDENCE_ARTIFACT,
    NOTES,
    REQUIRED_FUND_FIELDS,
    REQUIRED_LINE_FIELDS,
    REQUIRED_RESOLVED_INVESTABILITY_GAPS,
    VALID_AUTHORITY_LEVELS,
    VALID_EVIDENCE_STATUSES,
    VALID_SOURCE_TYPES,
    validate,
)


def _artifact() -> dict:
    return json.loads(EVIDENCE_ARTIFACT.read_text(encoding="utf-8"))


def test_expected_files_exist() -> None:
    assert EVIDENCE_ARTIFACT.exists()
    assert NOTES.exists()


def test_artifact_identity_and_paths_are_correct() -> None:
    data = _artifact()
    assert data["work_package_id"] == "ETF-EU-WP15AI"
    assert data["source_work_package"] == "ETF-EU-WP15AH"
    assert data["repository"] == "market-predictions/weekly-etf-eu"
    assert data["readiness_gate_status"] == "investability_evidence_acquired_not_client_grade"
    assert data["source_policy_artifact"] == "output/client_surface/etf_eu_pricing_freshness_valuation_policy_20260703_000000.json"
    assert data["source_product_facts_artifact"] == "output/client_surface/etf_eu_product_facts_evidence_20260703_000000.json"
    assert data["source_pricing_artifact"] == "output/client_surface/etf_eu_multi_line_pricing_preview_20260703_000000.json"
    assert data["source_registry"] == "config/ucits_symbol_registry.yml"


def test_investability_flags_are_true() -> None:
    data = _artifact()
    assert data["priips_kid_evidence_acquired"] is True
    assert data["liquidity_spread_evidence_acquired"] is True
    assert data["investability_evidence_validated"] is True
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


def test_fund_level_priips_kid_evidence_fields_exist() -> None:
    fund = _artifact()["fund_level_priips_kid_evidence"]
    assert REQUIRED_FUND_FIELDS.issubset(set(fund))
    assert fund["isin"] == "IE00B5BMR087"
    assert fund["fund_name"] == "iShares Core S&P 500 UCITS ETF USD (Acc)"
    assert fund["issuer"] == "iShares / BlackRock"
    assert fund["priips_kid_status"] == "available"
    assert fund["priips_kid_document_available"] is True
    assert fund["priips_kid_authority_level"] in VALID_AUTHORITY_LEVELS


def test_line_level_evidence_is_valid() -> None:
    lines = {line["symbol"]: line for line in _artifact()["line_level_liquidity_spread_evidence"]}
    assert set(lines) == {"SXR8.DE", "CSPX.L"}
    for symbol, line in lines.items():
        assert REQUIRED_LINE_FIELDS.issubset(set(line))
        assert line["isin"] == "IE00B5BMR087"
        assert line["line_status"] == "success"
        assert line["freshness_policy_status"] == "current_completed_session"
        assert line["liquidity_evidence_status"] in VALID_EVIDENCE_STATUSES
        assert line["spread_evidence_status"] in VALID_EVIDENCE_STATUSES
        assert line["liquidity_authority_level"] in VALID_AUTHORITY_LEVELS
        assert line["spread_authority_level"] in VALID_AUTHORITY_LEVELS


def test_resolved_gaps_and_blockers_are_valid() -> None:
    data = _artifact()
    assert set(data["resolved_investability_gaps"]) == REQUIRED_RESOLVED_INVESTABILITY_GAPS
    assert data["remaining_client_grade_blockers"]
    assert data["remaining_delivery_preflight_blockers"]


def test_source_manifest_is_valid() -> None:
    manifest = _artifact()["source_manifest"]
    assert manifest
    used = " ".join(" ".join(source["used_for_fields"]) for source in manifest)
    assert "PRIIPs" in used or "KID" in used
    assert "SXR8" in used
    assert "CSPX" in used
    for source in manifest:
        assert source["source_id"]
        assert source["source_reference"]
        assert source["source_type"] in VALID_SOURCE_TYPES
        assert source["authority_level"] in VALID_AUTHORITY_LEVELS
        assert source["retrieval_timestamp"]
        assert source["used_for_fields"]


def test_notes_contain_required_sections() -> None:
    text = NOTES.read_text(encoding="utf-8")
    for marker in [
        "# ETF-EU-WP15AI PRIIPs/KID and liquidity/spread investability evidence",
        "## Scope",
        "## Source artifacts",
        "## Source manifest",
        "## Fund-level PRIIPs/KID evidence",
        "## Line-level liquidity/spread evidence",
        "## Resolved investability gaps",
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
    assert result["work_package_id"] == "ETF-EU-WP15AI"
    assert result["readiness_gate_status"] == "investability_evidence_acquired_not_client_grade"
    assert result["priips_kid_evidence_acquired"] is True
    assert result["liquidity_spread_evidence_acquired"] is True
    assert result["investability_evidence_validated"] is True
    assert result["resolved_investability_gaps_count"] == 2
    assert result["client_grade_claim"] is False
    assert result["delivery_preflight_allowed"] is False
    assert result["valuation_grade"] is False
    assert result["selected_next_package"] == "ETF-EU-WP15AJ"
