from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_recipient_transport_authority_evidence_contract import (
    ARTIFACT,
    CONTRACT,
    NOTES,
    REMAINING_BLOCKERS,
    validate,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_expected_files_exist() -> None:
    assert CONTRACT.exists()
    assert ARTIFACT.exists()
    assert NOTES.exists()


def test_artifact_identity_and_sources_are_correct() -> None:
    data = _artifact()
    assert data["work_package_id"] == "ETF-EU-WP15AO"
    assert data["source_work_package"] == "ETF-EU-WP15AN"
    assert data["repository"] == "market-predictions/weekly-etf-eu"
    assert data["source_delivery_preflight_authority_artifact"] == "output/client_surface/etf_eu_delivery_preflight_authority_decision_20260703_000000.json"
    assert data["source_delivery_preflight_contract_artifact"] == "output/client_surface/etf_eu_delivery_preflight_contract_runbook_20260703_000000.json"
    assert data["source_client_grade_authority_artifact"] == "output/client_surface/etf_eu_client_grade_authority_decision_20260703_000000.json"
    assert data["recipient_transport_authority_evidence_contract_path"] == "control/ETF_EU_RECIPIENT_TRANSPORT_AUTHORITY_EVIDENCE_CONTRACT_V1.md"


def test_created_and_validated_flags_are_true() -> None:
    data = _artifact()
    for key in [
        "recipient_transport_authority_evidence_contract_created",
        "recipient_transport_authority_evidence_contract_validated",
        "recipient_authority_evidence_contract_created",
        "recipient_authority_evidence_contract_validated",
        "transport_authority_evidence_contract_created",
        "transport_authority_evidence_contract_validated",
    ]:
        assert data[key] is True
    assert data["readiness_gate_status"] == "recipient_transport_authority_evidence_contract_defined_not_authorized"


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
        "secret_values_exposed",
        "recipient_plaintext_values_exposed",
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


def test_recipient_authority_evidence_contract_is_valid() -> None:
    r = _artifact()["recipient_authority_evidence_contract"]
    assert r["contract_status"] == "defined_not_authorized"
    assert r["recipient_authority_evidence_status"] == "contract_defined"
    assert r["recipient_set_reference_id_required"] is True
    assert r["recipient_set_hash_required"] is True
    assert r["recipient_plaintext_values_allowed"] is False
    assert r["recipient_owner_approval_reference_required"] is True
    assert r["recipient_change_scope"] == "no_change_in_this_package"
    assert r["recipient_change_authority_required"] is True
    assert r["recipient_validation_method"] == "reference_and_hash_only"
    assert r["recipient_rollback_reference_required"] is True
    assert r["recipient_authority_created"] is False
    assert r["recipient_config_changed"] is False


def test_transport_authority_evidence_contract_is_valid() -> None:
    t = _artifact()["transport_authority_evidence_contract"]
    assert t["contract_status"] == "defined_not_authorized"
    assert t["transport_authority_evidence_status"] == "contract_defined"
    assert t["transport_reference_id_required"] is True
    assert t["transport_secret_reference_names_allowed"] is True
    assert t["transport_secret_values_allowed"] is False
    assert t["transport_presence_check_required"] is True
    assert t["transport_owner_approval_reference_required"] is True
    assert t["transport_change_scope"] == "no_change_in_this_package"
    assert t["transport_change_authority_required"] is True
    assert t["transport_validation_method"] == "reference_names_and_presence_checks_only"
    assert t["transport_rollback_reference_required"] is True
    assert t["transport_authority_created"] is False
    assert t["smtp_or_secret_config_changed"] is False


def test_authority_evidence_sufficiency_is_valid() -> None:
    s = _artifact()["authority_evidence_sufficiency"]
    assert s["recipient_authority_evidence_contract_defined"] is True
    assert s["transport_authority_evidence_contract_defined"] is True
    assert s["recipient_authority_created"] is False
    assert s["transport_authority_created"] is False
    assert s["recipient_config_changed"] is False
    assert s["smtp_or_secret_config_changed"] is False
    assert s["secret_values_exposed"] is False
    assert s["recipient_plaintext_values_exposed"] is False
    assert s["authority_status"] == "evidence_contract_defined_not_authorized"
    assert s["blocking_status"] == "blocking_delivery_preflight"


def test_remaining_blockers_are_exact() -> None:
    data = _artifact()
    assert data["remaining_client_grade_blockers"] == []
    assert set(data["remaining_delivery_preflight_blockers"]) == REMAINING_BLOCKERS


def test_source_manifest_is_valid() -> None:
    manifest = _artifact()["source_manifest"]
    assert manifest
    used = " ".join(" ".join(source["used_for_fields"]) for source in manifest)
    for required in [
        "recipient authority evidence contract",
        "transport authority evidence contract",
        "authority evidence sufficiency",
        "delivery-preflight blocker preservation",
    ]:
        assert required in used


def test_notes_contain_required_sections() -> None:
    text = NOTES.read_text(encoding="utf-8")
    for marker in [
        "# ETF-EU-WP15AO recipient and transport authority evidence contract",
        "## Scope",
        "## Source artifacts",
        "## Recipient authority evidence contract",
        "## Transport authority evidence contract",
        "## Authority evidence sufficiency",
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
    assert result["work_package_id"] == "ETF-EU-WP15AO"
    assert result["recipient_transport_authority_evidence_contract_created"] is True
    assert result["recipient_transport_authority_evidence_contract_validated"] is True
    assert result["recipient_authority_evidence_contract_created"] is True
    assert result["transport_authority_evidence_contract_created"] is True
    assert result["readiness_gate_status"] == "recipient_transport_authority_evidence_contract_defined_not_authorized"
    assert result["recipient_authority_created"] is False
    assert result["transport_authority_created"] is False
    assert result["recipient_config_changed"] is False
    assert result["smtp_or_secret_config_changed"] is False
    assert result["secret_values_exposed"] is False
    assert result["recipient_plaintext_values_exposed"] is False
    assert result["delivery_preflight_allowed"] is False
    assert result["production_delivery"] is False
    assert result["remaining_delivery_preflight_blockers_count"] == 3
    assert result["selected_next_package"] == "ETF-EU-WP15AP"
