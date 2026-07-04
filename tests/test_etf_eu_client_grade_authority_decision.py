from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_client_grade_authority_decision import (
    ARTIFACT,
    NOTES,
    POLICY,
    REQUIRED_DECISION_FIELDS,
    REQUIRED_DELIVERY_BLOCKERS,
    REQUIRED_EVIDENCE_FIELDS,
    REQUIRED_LANGUAGE_FIELDS,
    REQUIRED_PRICING_FIELDS,
    REQUIRED_SOURCE_AUTHORITY_FIELDS,
    validate,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_expected_files_exist() -> None:
    assert POLICY.exists()
    assert ARTIFACT.exists()
    assert NOTES.exists()


def test_artifact_identity_and_sources_are_correct() -> None:
    data = _artifact()
    assert data["work_package_id"] == "ETF-EU-WP15AL"
    assert data["source_work_package"] == "ETF-EU-WP15AK"
    assert data["repository"] == "market-predictions/weekly-etf-eu"
    assert data["source_language_quality_artifact"] == "output/client_surface/etf_eu_client_language_quality_readiness_synthesis_20260703_000000.json"
    assert data["source_decision_framework_artifact"] == "output/client_surface/etf_eu_investment_thesis_invalidation_funding_posture_framework_20260703_000000.json"
    assert data["source_investability_evidence_artifact"] == "output/client_surface/etf_eu_priips_kid_liquidity_spread_evidence_20260703_000000.json"
    assert data["client_grade_authority_policy_path"] == "control/ETF_EU_CLIENT_GRADE_AUTHORITY_DECISION_POLICY_V1.md"


def test_authority_decision_flags_are_valid() -> None:
    data = _artifact()
    assert data["client_grade_authority_decision_created"] is True
    assert data["client_grade_authority_decision_validated"] is True
    assert data["client_grade_authority_created"] is True
    assert data["client_grade_claim"] is True
    assert data["client_grade_status"] == "authorized_no_delivery"
    assert data["client_grade_enough_for_delivery_preflight_discussion"] is True
    assert data["readiness_gate_status"] == "client_grade_authority_created_delivery_blocked"
    assert data["review_only"] is False
    assert data["selected_next_package"] == "ETF-EU-WP15AM"


def test_non_authorized_boundaries_remain_false() -> None:
    data = _artifact()
    for key in [
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


def test_decision_object_fields_exist() -> None:
    decision = _artifact()["client_grade_authority_decision"]
    assert REQUIRED_DECISION_FIELDS.issubset(set(decision))
    assert decision["decision_status"] == "validated"
    assert decision["decision_result"] == "authorized_no_delivery"
    assert decision["client_grade_authority_created"] is True
    assert decision["client_grade_claim"] is True
    assert decision["client_grade_scope"] == "client_grade_report_state_only"
    assert decision["delivery_scope"] == "blocked"
    assert decision["valuation_scope"] == "not_authorized"
    assert decision["funding_scope"] == "not_authorized"
    assert decision["portfolio_scope"] == "no_mutation"
    assert decision["required_next_package"] == "ETF-EU-WP15AM"


def test_sufficiency_objects_are_valid() -> None:
    data = _artifact()
    assert REQUIRED_EVIDENCE_FIELDS.issubset(set(data["evidence_chain_sufficiency"]))
    assert REQUIRED_SOURCE_AUTHORITY_FIELDS.issubset(set(data["source_authority_sufficiency"]))
    assert REQUIRED_LANGUAGE_FIELDS.issubset(set(data["client_language_sufficiency"]))
    assert REQUIRED_PRICING_FIELDS.issubset(set(data["pricing_evidence_sufficiency"]))
    assert data["evidence_chain_sufficiency"]["overall_evidence_chain_status"] == "passed"
    assert data["source_authority_sufficiency"]["overall_source_authority_status"] == "passed"
    assert data["client_language_sufficiency"]["overall_client_language_status"] == "passed"
    assert data["pricing_evidence_sufficiency"]["overall_pricing_evidence_status"] == "passed_for_client_grade_only"


def test_blocker_lists_are_valid() -> None:
    data = _artifact()
    assert data["remaining_client_grade_blockers"] == []
    assert REQUIRED_DELIVERY_BLOCKERS.issubset(set(data["remaining_delivery_preflight_blockers"]))
    assert "all_client_grade_gates_passed" not in data["remaining_delivery_preflight_blockers"]


def test_source_manifest_is_valid() -> None:
    manifest = _artifact()["source_manifest"]
    assert manifest
    used = " ".join(" ".join(source["used_for_fields"]) for source in manifest)
    assert "client-grade authority decision" in used
    assert "evidence-chain sufficiency" in used
    assert "source-authority sufficiency" in used
    assert "client-language sufficiency" in used
    assert "pricing evidence sufficiency" in used


def test_notes_contain_required_sections() -> None:
    text = NOTES.read_text(encoding="utf-8")
    for marker in [
        "# ETF-EU-WP15AL client-grade authority decision",
        "## Scope",
        "## Source artifacts",
        "## Client-grade authority policy",
        "## Authority decision",
        "## Evidence-chain sufficiency",
        "## Source-authority sufficiency",
        "## Client-language sufficiency",
        "## Pricing evidence sufficiency",
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
    assert result["work_package_id"] == "ETF-EU-WP15AL"
    assert result["readiness_gate_status"] == "client_grade_authority_created_delivery_blocked"
    assert result["client_grade_authority_decision_created"] is True
    assert result["client_grade_authority_decision_validated"] is True
    assert result["client_grade_authority_created"] is True
    assert result["client_grade_claim"] is True
    assert result["client_grade_status"] == "authorized_no_delivery"
    assert result["remaining_client_grade_blockers_count"] == 0
    assert result["remaining_delivery_preflight_blockers_count"] == 7
    assert result["delivery_preflight_allowed"] is False
    assert result["production_delivery"] is False
    assert result["valuation_grade"] is False
    assert result["funding_authority"] is False
    assert result["portfolio_mutation"] is False
    assert result["selected_next_package"] == "ETF-EU-WP15AM"
