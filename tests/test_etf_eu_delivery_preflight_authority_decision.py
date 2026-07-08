from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_delivery_preflight_authority_decision import (
    ARTIFACT,
    NOTES,
    POLICY,
    REMAINING_BLOCKERS,
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
    assert data["work_package_id"] == "ETF-EU-WP15AN"
    assert data["source_work_package"] == "ETF-EU-WP15AM"
    assert data["repository"] == "market-predictions/weekly-etf-eu"
    assert data["source_delivery_preflight_contract_artifact"] == "output/client_surface/etf_eu_delivery_preflight_contract_runbook_20260703_000000.json"
    assert data["source_client_grade_authority_artifact"] == "output/client_surface/etf_eu_client_grade_authority_decision_20260703_000000.json"
    assert data["delivery_preflight_authority_policy_path"] == "control/ETF_EU_DELIVERY_PREFLIGHT_AUTHORITY_DECISION_POLICY_V1.md"


def test_expected_negative_branch_is_internally_consistent() -> None:
    data = _artifact()
    assert data["delivery_preflight_authority_decision_created"] is True
    assert data["delivery_preflight_authority_decision_validated"] is True
    assert data["delivery_preflight_authority_created"] is False
    assert data["delivery_preflight_allowed"] is False
    assert data["delivery_preflight_status"] == "not_authorized"
    assert data["readiness_gate_status"] == "delivery_preflight_authority_not_created"
    assert data["delivery_authorization_decision"] == "remain_blocked"
    assert data["outbound_path_enabled"] is False
    assert data["delivery_ready"] is False
    assert data["selected_next_package"] == "ETF-EU-WP15AO"


def test_non_authorized_boundaries_remain_false() -> None:
    data = _artifact()
    for key in [
        "delivery_ready",
        "delivery_preflight_authority_created",
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


def test_authority_decision_object_is_valid() -> None:
    d = _artifact()["delivery_preflight_authority_decision"]
    assert d["decision_status"] == "validated"
    assert d["decision_result"] == "not_authorized"
    assert d["decision_reason"] == "recipient_and_transport_authority_missing"
    assert d["delivery_preflight_authority_created"] is False
    assert d["delivery_preflight_allowed"] is False
    assert d["delivery_scope"] == "blocked"
    assert d["send_scope"] == "blocked"
    assert d["production_delivery_scope"] == "blocked"
    assert d["recipient_scope"] == "not_authorized"
    assert d["transport_scope"] == "not_authorized"
    assert d["required_next_package"] == "ETF-EU-WP15AO"


def test_sufficiency_objects_are_valid() -> None:
    data = _artifact()
    assert data["authority_input_sufficiency"]["overall_contract_input_status"] == "passed_for_decision_not_execution"
    assert data["recipient_authority_sufficiency"]["recipient_authority_gate_defined"] is True
    assert data["recipient_authority_sufficiency"]["recipient_config_changed"] is False
    assert data["recipient_authority_sufficiency"]["recipient_authority_created"] is False
    assert data["recipient_authority_sufficiency"]["recipient_authority_status"] == "missing"
    assert data["transport_authority_sufficiency"]["transport_authority_gate_defined"] is True
    assert data["transport_authority_sufficiency"]["smtp_or_secret_config_changed"] is False
    assert data["transport_authority_sufficiency"]["transport_authority_created"] is False
    assert data["transport_authority_sufficiency"]["transport_authority_status"] == "missing"
    assert data["explicit_delivery_preflight_authority_sufficiency"]["explicit_delivery_preflight_authority_decision_created"] is True
    assert data["explicit_delivery_preflight_authority_sufficiency"]["explicit_delivery_preflight_authority_created"] is False
    assert data["explicit_delivery_preflight_authority_sufficiency"]["delivery_preflight_allowed"] is False
    assert data["explicit_delivery_preflight_authority_sufficiency"]["authority_status"] == "not_authorized"


def test_remaining_blockers_are_exact() -> None:
    data = _artifact()
    assert data["remaining_client_grade_blockers"] == []
    assert set(data["remaining_delivery_preflight_blockers"]) == REMAINING_BLOCKERS


def test_source_manifest_is_valid() -> None:
    manifest = _artifact()["source_manifest"]
    assert manifest
    used = " ".join(" ".join(source["used_for_fields"]) for source in manifest)
    for required in [
        "delivery-preflight authority decision",
        "authority input sufficiency",
        "recipient authority sufficiency",
        "transport authority sufficiency",
        "explicit delivery-preflight authority sufficiency",
    ]:
        assert required in used


def test_notes_contain_required_sections() -> None:
    text = NOTES.read_text(encoding="utf-8")
    for marker in [
        "# ETF-EU-WP15AN delivery-preflight authority decision",
        "## Scope",
        "## Source artifacts",
        "## Delivery-preflight authority policy",
        "## Authority decision",
        "## Authority input sufficiency",
        "## Recipient authority sufficiency",
        "## Transport authority sufficiency",
        "## Explicit delivery-preflight authority sufficiency",
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
    assert result["work_package_id"] == "ETF-EU-WP15AN"
    assert result["delivery_preflight_authority_decision_created"] is True
    assert result["delivery_preflight_authority_decision_validated"] is True
    assert result["delivery_preflight_authority_created"] is False
    assert result["delivery_preflight_allowed"] is False
    assert result["delivery_preflight_status"] == "not_authorized"
    assert result["readiness_gate_status"] == "delivery_preflight_authority_not_created"
    assert result["delivery_authorization_decision"] == "remain_blocked"
    assert result["production_delivery"] is False
    assert result["receipt_artifact_created"] is False
    assert result["production_manifest_created"] is False
    assert result["recipient_authority_created"] is False
    assert result["transport_authority_created"] is False
    assert result["remaining_client_grade_blockers_count"] == 0
    assert result["remaining_delivery_preflight_blockers_count"] == 3
    assert result["selected_next_package"] == "ETF-EU-WP15AO"
