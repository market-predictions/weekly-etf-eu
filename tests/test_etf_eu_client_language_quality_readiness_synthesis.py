from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_client_language_quality_readiness_synthesis import (
    ARTIFACT,
    LANGUAGE_POLICY,
    NOTES,
    REQUIRED_DELIVERY_BLOCKERS,
    REQUIRED_GATE_FIELDS,
    REQUIRED_SYNTHESIS_FIELDS,
    validate,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_expected_files_exist() -> None:
    assert LANGUAGE_POLICY.exists()
    assert ARTIFACT.exists()
    assert NOTES.exists()


def test_artifact_identity_and_sources_are_correct() -> None:
    data = _artifact()
    assert data["work_package_id"] == "ETF-EU-WP15AK"
    assert data["source_work_package"] == "ETF-EU-WP15AJ"
    assert data["repository"] == "market-predictions/weekly-etf-eu"
    assert data["readiness_gate_status"] == "client_language_gate_passed_not_delivery_ready"
    assert data["source_decision_framework_artifact"] == "output/client_surface/etf_eu_investment_thesis_invalidation_funding_posture_framework_20260703_000000.json"
    assert data["source_investability_evidence_artifact"] == "output/client_surface/etf_eu_priips_kid_liquidity_spread_evidence_20260703_000000.json"
    assert data["language_quality_policy_path"] == "control/ETF_EU_CLIENT_LANGUAGE_QUALITY_GATE_V1.md"


def test_language_and_readiness_flags_are_true() -> None:
    data = _artifact()
    assert data["client_language_quality_gate_created"] is True
    assert data["client_language_quality_gate_validated"] is True
    assert data["source_authority_wording_validated"] is True
    assert data["residual_blocker_disclosure_validated"] is True
    assert data["readiness_synthesis_created"] is True
    assert data["readiness_synthesis_validated"] is True
    assert data["client_language_quality_gate_passed"] is True
    assert data["accepted_review_only_foundation"] is True


def test_authority_claims_remain_false() -> None:
    data = _artifact()
    for key in [
        "client_grade_claim",
        "client_grade_authority_created",
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


def test_client_language_quality_gate_fields_exist() -> None:
    gate = _artifact()["client_language_quality_gate"]
    assert REQUIRED_GATE_FIELDS.issubset(set(gate))
    assert gate["gate_status"] == "passed_review_only_language_gate"
    assert gate["dutch_first_required"] is True
    assert gate["review_only_disclosure_status"] == "passed"
    assert gate["source_authority_wording_status"] == "passed"
    assert gate["residual_blocker_disclosure_status"] == "passed"
    assert gate["transaction_language_status"] == "blocked"
    assert gate["funding_language_status"] == "blocked"
    assert gate["delivery_language_status"] == "blocked"
    assert gate["valuation_language_status"] == "blocked"
    assert "onder beoordeling" in gate["allowed_client_surface_terms"]
    assert "koopadvies" in gate["prohibited_client_surface_terms"]


def test_readiness_synthesis_fields_exist() -> None:
    synthesis = _artifact()["readiness_synthesis"]
    assert REQUIRED_SYNTHESIS_FIELDS.issubset(set(synthesis))
    assert synthesis["review_only_readiness_status"] == "review_only_language_gate_passed"
    assert synthesis["client_grade_status"] == "not_authorized"
    assert synthesis["delivery_preflight_status"] == "blocked"
    assert synthesis["production_delivery_status"] == "blocked"
    assert synthesis["funding_status"] == "not_authorized"
    assert synthesis["valuation_status"] == "not_authorized"
    assert synthesis["portfolio_status"] == "no_mutation"
    assert synthesis["final_authority_position"] == "review_only_not_delivery_ready"
    assert synthesis["next_required_package"] == "ETF-EU-WP15AL"


def test_resolved_gaps_and_remaining_blockers_are_valid() -> None:
    data = _artifact()
    assert data["resolved_client_language_gaps"] == ["client_language_quality_gate"]
    assert data["remaining_client_grade_blockers"] == []
    assert REQUIRED_DELIVERY_BLOCKERS.issubset(set(data["remaining_delivery_preflight_blockers"]))


def test_source_manifest_is_valid() -> None:
    manifest = _artifact()["source_manifest"]
    assert manifest
    used = " ".join(" ".join(source["used_for_fields"]) for source in manifest)
    assert "client language quality gate" in used
    assert "source-authority wording" in used
    assert "residual blocker disclosure" in used
    assert "readiness synthesis" in used


def test_notes_contain_required_sections() -> None:
    text = NOTES.read_text(encoding="utf-8")
    for marker in [
        "# ETF-EU-WP15AK client language quality gate and readiness synthesis",
        "## Scope",
        "## Source artifacts",
        "## Language quality policy",
        "## Client-language quality gate",
        "## Readiness synthesis",
        "## Resolved client-language gaps",
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
    assert result["work_package_id"] == "ETF-EU-WP15AK"
    assert result["readiness_gate_status"] == "client_language_gate_passed_not_delivery_ready"
    assert result["client_language_quality_gate_created"] is True
    assert result["client_language_quality_gate_validated"] is True
    assert result["readiness_synthesis_created"] is True
    assert result["readiness_synthesis_validated"] is True
    assert result["client_language_quality_gate_passed"] is True
    assert result["resolved_client_language_gaps_count"] == 1
    assert result["remaining_client_grade_blockers_count"] == 0
    assert result["client_grade_claim"] is False
    assert result["client_grade_authority_created"] is False
    assert result["delivery_preflight_allowed"] is False
    assert result["valuation_grade"] is False
    assert result["funding_authority"] is False
    assert result["portfolio_mutation"] is False
    assert result["selected_next_package"] == "ETF-EU-WP15AL"
