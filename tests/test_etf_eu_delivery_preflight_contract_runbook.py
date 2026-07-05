from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_delivery_preflight_contract_runbook import (
    ARTIFACT,
    CONTRACT,
    NOTES,
    REMAINING_BLOCKERS,
    RESOLVED_GAPS,
    RUNBOOK,
    VERIFY_POLICY,
    validate,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_expected_files_exist() -> None:
    assert CONTRACT.exists()
    assert RUNBOOK.exists()
    assert VERIFY_POLICY.exists()
    assert ARTIFACT.exists()
    assert NOTES.exists()


def test_artifact_identity_and_sources_are_correct() -> None:
    data = _artifact()
    assert data["work_package_id"] == "ETF-EU-WP15AM"
    assert data["source_work_package"] == "ETF-EU-WP15AL"
    assert data["repository"] == "market-predictions/weekly-etf-eu"
    assert data["source_client_grade_authority_artifact"] == "output/client_surface/etf_eu_client_grade_authority_decision_20260703_000000.json"
    assert data["source_client_grade_pdf"] == "output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.pdf"
    assert data["delivery_preflight_contract_path"] == "control/ETF_EU_DELIVERY_PREFLIGHT_CONTRACT_V1.md"
    assert data["outbound_runbook_path"] == "control/ETF_EU_OUTBOUND_RUNBOOK_V1.md"
    assert data["post_send_verification_rollback_policy_path"] == "control/ETF_EU_POST_SEND_VERIFICATION_AND_ROLLBACK_POLICY_V1.md"


def test_created_and_validated_flags_are_true() -> None:
    data = _artifact()
    for key in [
        "delivery_preflight_contract_created",
        "delivery_preflight_contract_validated",
        "production_manifest_contract_created",
        "production_manifest_contract_validated",
        "delivery_receipt_contract_created",
        "delivery_receipt_contract_validated",
        "recipient_authority_gate_defined",
        "transport_authority_gate_defined",
        "outbound_runbook_created",
        "outbound_runbook_validated",
        "post_send_verification_loop_defined",
        "rollback_abort_policy_defined",
        "delivery_preflight_readiness_synthesis_created",
        "delivery_preflight_readiness_synthesis_validated",
    ]:
        assert data[key] is True
    assert data["readiness_gate_status"] == "delivery_preflight_contract_defined_not_authorized"


def test_non_authorized_boundaries_remain_false() -> None:
    data = _artifact()
    for key in [
        "delivery_ready",
        "delivery_preflight_allowed",
        "outbound_path_enabled",
        "production_delivery",
        "receipt_artifact_created",
        "production_manifest_created",
        "recipient_config_changed",
        "smtp_or_secret_config_changed",
        "recipient_authority_created",
        "transport_authority_created",
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


def test_contract_objects_are_valid() -> None:
    data = _artifact()
    assert data["delivery_preflight_contract"]["contract_status"] == "defined_not_authorized"
    assert data["delivery_preflight_contract"]["delivery_preflight_allowed"] is False
    assert data["delivery_preflight_contract"]["delivery_execution_allowed"] is False
    assert data["delivery_preflight_contract"]["next_required_package"] == "ETF-EU-WP15AN"
    assert data["production_manifest_contract"]["manifest_created"] is False
    assert data["production_manifest_contract"]["manifest_path_created"] is False
    assert data["delivery_receipt_contract"]["receipt_created"] is False
    assert data["recipient_authority_gate"]["recipient_authority_created"] is False
    assert data["transport_authority_gate"]["transport_authority_created"] is False
    assert data["outbound_runbook"]["execution_allowed"] is False
    assert data["post_send_verification_loop"]["verification_allowed"] is False
    assert data["rollback_abort_policy"]["rollback_allowed"] is False


def test_resolved_and_remaining_blockers_are_exact() -> None:
    data = _artifact()
    assert set(data["resolved_delivery_contract_gaps"]) == RESOLVED_GAPS
    assert set(data["remaining_delivery_preflight_blockers"]) == REMAINING_BLOCKERS


def test_source_manifest_is_valid() -> None:
    manifest = _artifact()["source_manifest"]
    assert manifest
    used = " ".join(" ".join(source["used_for_fields"]) for source in manifest)
    for required in [
        "delivery-preflight contract",
        "production manifest contract",
        "delivery receipt contract",
        "recipient authority gate",
        "transport authority gate",
        "outbound runbook",
        "post-send verification loop",
        "rollback abort policy",
    ]:
        assert required in used


def test_notes_contain_required_sections() -> None:
    text = NOTES.read_text(encoding="utf-8")
    for marker in [
        "# ETF-EU-WP15AM delivery-preflight contract and outbound runbook",
        "## Scope",
        "## Source artifacts",
        "## Delivery-preflight contract",
        "## Production manifest contract",
        "## Delivery receipt contract",
        "## Recipient authority gate",
        "## Transport authority gate",
        "## Outbound runbook",
        "## Post-send verification loop",
        "## Rollback and abort policy",
        "## Resolved delivery contract gaps",
        "## Remaining delivery-preflight blockers",
        "## Boundary checks",
        "## Decision",
        "## Next package",
    ]:
        assert marker in text


def test_validator_passes() -> None:
    result = validate()
    assert result["status"] == "valid"
    assert result["work_package_id"] == "ETF-EU-WP15AM"
    assert result["readiness_gate_status"] == "delivery_preflight_contract_defined_not_authorized"
    assert result["delivery_preflight_contract_created"] is True
    assert result["delivery_preflight_contract_validated"] is True
    assert result["outbound_runbook_created"] is True
    assert result["outbound_runbook_validated"] is True
    assert result["delivery_preflight_allowed"] is False
    assert result["production_delivery"] is False
    assert result["receipt_artifact_created"] is False
    assert result["production_manifest_created"] is False
    assert result["recipient_authority_created"] is False
    assert result["transport_authority_created"] is False
    assert result["resolved_delivery_contract_gaps_count"] == 5
    assert result["remaining_delivery_preflight_blockers_count"] == 3
    assert result["selected_next_package"] == "ETF-EU-WP15AN"
