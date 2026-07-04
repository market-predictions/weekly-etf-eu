from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_pricing_freshness_valuation_policy import (
    NOTES,
    POLICY_ARTIFACT,
    PRICING_POLICY,
    REQUIRED_FRESHNESS_CATEGORIES,
    REQUIRED_RECONCILIATION_RULES,
    REQUIRED_RESOLVED_POLICY_GAPS,
    VALUATION_POLICY,
    validate,
)


def _artifact() -> dict:
    return json.loads(POLICY_ARTIFACT.read_text(encoding="utf-8"))


def test_expected_files_exist() -> None:
    assert PRICING_POLICY.exists()
    assert VALUATION_POLICY.exists()
    assert POLICY_ARTIFACT.exists()
    assert NOTES.exists()


def test_artifact_identity_is_correct() -> None:
    data = _artifact()
    assert data["work_package_id"] == "ETF-EU-WP15AH"
    assert data["source_work_package"] == "ETF-EU-WP15AG"
    assert data["repository"] == "market-predictions/weekly-etf-eu"
    assert data["readiness_gate_status"] == "pricing_and_valuation_policy_defined_not_client_grade"


def test_source_paths_are_correct() -> None:
    data = _artifact()
    assert data["source_product_facts_artifact"] == "output/client_surface/etf_eu_product_facts_evidence_20260703_000000.json"
    assert data["source_product_facts_notes"] == "output/client_surface/etf_eu_product_facts_evidence_notes_20260703_000000.md"
    assert data["source_acquisition_plan_artifact"] == "output/client_surface/etf_eu_cockpit_pdf_client_grade_evidence_acquisition_plan_20260703_000000.json"
    assert data["source_gap_audit_artifact"] == "output/client_surface/etf_eu_cockpit_pdf_client_grade_evidence_gap_audit_20260703_000000.json"
    assert data["source_readiness_gate_artifact"] == "output/client_surface/etf_eu_cockpit_pdf_client_grade_readiness_gate_v2_20260703_000000.json"
    assert data["source_review_only_pdf"] == "output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.pdf"
    assert data["pricing_freshness_policy_path"] == "control/ETF_EU_PRICING_FRESHNESS_POLICY_V1.md"
    assert data["valuation_reconciliation_policy_path"] == "control/ETF_EU_VALUATION_RECONCILIATION_POLICY_V1.md"


def test_policy_flags_are_true() -> None:
    data = _artifact()
    assert data["pricing_freshness_policy_created"] is True
    assert data["valuation_reconciliation_policy_created"] is True
    assert data["pricing_freshness_policy_validated"] is True
    assert data["valuation_reconciliation_policy_validated"] is True
    assert data["accepted_review_only_foundation"] is True


def test_client_grade_delivery_and_valuation_claims_remain_false() -> None:
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


def test_freshness_classifications_are_expected() -> None:
    data = _artifact()
    assert data["first_successful_freshness_policy_status"] == "current_completed_session"
    assert data["second_successful_freshness_policy_status"] == "current_completed_session"
    assert data["smh_freshness_policy_status"] == "unpriced_or_pending_verification"


def test_pricing_freshness_categories_include_all_required_values() -> None:
    assert REQUIRED_FRESHNESS_CATEGORIES.issubset(set(_artifact()["pricing_freshness_categories"]))


def test_valuation_reconciliation_rules_include_all_required_values() -> None:
    assert REQUIRED_RECONCILIATION_RULES.issubset(set(_artifact()["valuation_reconciliation_rules"]))


def test_resolved_policy_gaps_are_exact() -> None:
    assert set(_artifact()["resolved_policy_gaps"]) == REQUIRED_RESOLVED_POLICY_GAPS


def test_remaining_blockers_are_non_empty() -> None:
    data = _artifact()
    assert data["remaining_client_grade_blockers"]
    assert data["remaining_delivery_preflight_blockers"]


def test_source_manifest_is_valid() -> None:
    manifest = _artifact()["source_manifest"]
    assert manifest
    internal_policy_refs = {
        source["source_reference"]
        for source in manifest
        if source["authority_level"] == "internal_policy"
    }
    assert "control/ETF_EU_PRICING_FRESHNESS_POLICY_V1.md" in internal_policy_refs
    assert "control/ETF_EU_VALUATION_RECONCILIATION_POLICY_V1.md" in internal_policy_refs
    for source in manifest:
        assert source["source_id"]
        assert source["source_reference"]
        assert source["retrieval_timestamp"]
        assert source["used_for_fields"]


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


def test_pricing_policy_contains_required_sections() -> None:
    text = PRICING_POLICY.read_text(encoding="utf-8")
    for marker in [
        "# ETF EU pricing freshness policy v1",
        "## Purpose",
        "## Scope",
        "## Authority boundary",
        "## Freshness categories",
        "## Completed-session rule",
        "## Weekend and exchange-holiday handling",
        "## Multi-line close-date handling",
        "## Stale-price handling",
        "## Review-only interpretation",
        "## Client-grade limitation",
        "## Delivery-preflight limitation",
        "## Non-authorized actions",
        "## Required future evidence before client-grade",
        "## Validation requirements",
    ]:
        assert marker in text


def test_valuation_policy_contains_required_sections() -> None:
    text = VALUATION_POLICY.read_text(encoding="utf-8")
    for marker in [
        "# ETF EU valuation reconciliation policy v1",
        "## Purpose",
        "## Scope",
        "## Authority boundary",
        "## ISIN-first reconciliation principle",
        "## Trading-line reconciliation",
        "## Currency-aware interpretation",
        "## Same-fund line mapping",
        "## Close-date mismatch handling",
        "## Price-source mismatch handling",
        "## Review-only valuation posture",
        "## Why this is not valuation-grade",
        "## Client-grade limitation",
        "## Delivery-preflight limitation",
        "## Non-authorized actions",
        "## Required future evidence before valuation-grade or client-grade",
        "## Validation requirements",
    ]:
        assert marker in text


def test_notes_contain_required_sections() -> None:
    text = NOTES.read_text(encoding="utf-8")
    for marker in [
        "# ETF-EU-WP15AH pricing freshness and valuation reconciliation policy",
        "## Scope",
        "## Source artifacts",
        "## Policy documents",
        "## Pricing freshness policy",
        "## Valuation reconciliation policy",
        "## Current line classifications",
        "## Resolved policy gaps",
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
    assert result["work_package_id"] == "ETF-EU-WP15AH"
    assert result["readiness_gate_status"] == "pricing_and_valuation_policy_defined_not_client_grade"
    assert result["pricing_freshness_policy_created"] is True
    assert result["valuation_reconciliation_policy_created"] is True
    assert result["pricing_freshness_policy_validated"] is True
    assert result["valuation_reconciliation_policy_validated"] is True
    assert result["resolved_policy_gaps_count"] == 2
    assert result["client_grade_claim"] is False
    assert result["delivery_preflight_allowed"] is False
    assert result["valuation_grade"] is False
    assert result["selected_next_package"] == "ETF-EU-WP15AI"
