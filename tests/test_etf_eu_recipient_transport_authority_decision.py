from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_recipient_transport_authority_decision import (
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
    assert data["work_package_id"] == "ETF-EU-WP15AP"
    assert data["source_work_package"] == "ETF-EU-WP15AO"
    assert data["repository"] == "market-predictions/weekly-etf-eu"
    assert data["source_recipient_transport_authority_evidence_contract_artifact"] == "output/client_surface/etf_eu_recipient_transport_authority_evidence_contract_20260703_000000.json"
    assert data["source_delivery_preflight_authority_artifact"] == "output/client_surface/etf_eu_delivery_preflight_authority_decision_20260703_000000.json"
    assert data["recipient_transport_authority_decision_policy_path"] == "control/ETF_EU_RECIPIENT_TRANSPORT_AUTHORITY_DECISION_POLICY_V1.md"


def test_expected_negative_branch_is_internally_consistent() -> None:
    data = _artifact()
    assert data["recipient_transport_authority_decision_created"] is True
    assert data["recipient_transport_authority_decision_validated"] is True
    assert data["recipient_authority_created"] is False
    assert data["transport_authority_created"] is False
    assert data["recipient_transport_authority_status"] == "not_authorized"
    assert data["readiness_gate_status"] == "recipient_transport_authority_decision_not_created"
    assert data["delivery_authorization_decision"] == "remain_blocked"
    assert data["selected_next_package"] == "ETF-EU-WP15AQ"


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


def test_decision_object_is_valid() -> None:
    d = _artifact()["recipient_transport_authority_decision"]
    assert d["decision_status"] == "validated"
    assert d["decision_result"] == "not_authorized"
    assert d["decision_reason"] == "concrete_recipient_and_transport_evidence_missing"
    assert d["recipient_authority_created"] is False
    assert d["transport_authority_created"] is False
    assert d["recipient_scope"] == "blocked"
    assert d["transport_scope"] == "blocked"
    assert d["secret_scope"] == "not_exposed"
    assert d["recipient_plaintext_scope"] == "not_exposed"
    assert d["delivery_preflight_scope"] == "blocked"
    assert d["send_scope"] == "blocked"
    assert d["production_delivery_scope"] == "blocked"
    assert d["required_next_package"] == "ETF-EU-WP15AQ"


def test_recipient_evidence_sufficiency_is_valid() -> None:
    r = _artifact()["recipient_evidence_sufficiency"]
    assert r["recipient_authority_evidence_contract_defined"] is True
    assert r["recipient_set_reference_id_present"] is False
    assert r["recipient_set_hash_present"] is False
    assert r["recipient_owner_approval_reference_present"] is False
    assert r["recipient_rollback_reference_present"] is False
    assert r["recipient_plaintext_values_exposed"] is False
    assert r["recipient_config_changed"] is False
    assert r["recipient_authority_created"] is False
    assert r["recipient_evidence_status"] == "missing_concrete_evidence"
    assert r["blocking_status"] == "blocking_recipient_authority"


def test_transport_evidence_sufficiency_is_valid() -> None:
    t = _artifact()["transport_evidence_sufficiency"]
    assert t["transport_authority_evidence_contract_defined"] is True
    assert t["transport_reference_id_present"] is False
    assert t["transport_presence_check_reference_present"] is False
    assert t["transport_owner_approval_reference_present"] is False
    assert t["transport_rollback_reference_present"] is False
    assert t["secret_values_exposed"] is False
    assert t["smtp_or_secret_config_changed"] is False
    assert t["transport_authority_created"] is False
    assert t["transport_evidence_status"] == "missing_concrete_evidence"
    assert t["blocking_status"] == "blocking_transport_authority"


def test_handling_and_authority_sufficiency_are_valid() -> None:
    data = _artifact()
    assert data["secret_handling_sufficiency"]["secret_values_exposed"] is False
    assert data["secret_handling_sufficiency"]["secret_reference_names_only"] is True
    assert data["secret_handling_sufficiency"]["secret_handling_status"] == "passed_no_secret_exposure"
    assert data["recipient_handling_sufficiency"]["recipient_plaintext_values_exposed"] is False
    assert data["recipient_handling_sufficiency"]["recipient_reference_or_hash_only"] is True
    assert data["recipient_handling_sufficiency"]["recipient_handling_status"] == "passed_no_plaintext_exposure"
    assert data["authority_decision_sufficiency"]["recipient_authority_can_be_created"] is False
    assert data["authority_decision_sufficiency"]["transport_authority_can_be_created"] is False
    assert data["authority_decision_sufficiency"]["recipient_transport_authority_status"] == "not_authorized"
    assert data["authority_decision_sufficiency"]["delivery_preflight_can_be_opened"] is False
    assert data["authority_decision_sufficiency"]["production_delivery_can_be_created"] is False
    assert data["authority_decision_sufficiency"]["authority_status"] == "negative_authority_decision"


def test_remaining_blockers_are_exact() -> None:
    data = _artifact()
    assert data["remaining_client_grade_blockers"] == []
    assert set(data["remaining_delivery_preflight_blockers"]) == REMAINING_BLOCKERS


def test_source_manifest_is_valid() -> None:
    manifest = _artifact()["source_manifest"]
    assert manifest
    used = " ".join(" ".join(source["used_for_fields"]) for source in manifest)
    for required in [
        "recipient and transport authority decision",
        "recipient evidence sufficiency",
        "transport evidence sufficiency",
        "secret-handling sufficiency",
        "recipient-handling sufficiency",
        "authority decision sufficiency",
        "delivery-preflight blocker preservation",
    ]:
        assert required in used


def test_notes_contain_required_sections() -> None:
    text = NOTES.read_text(encoding="utf-8")
    for marker in [
        "# ETF-EU-WP15AP recipient and transport authority decision",
        "## Scope",
        "## Source artifacts",
        "## Authority decision policy",
        "## Recipient and transport authority decision",
        "## Recipient evidence sufficiency",
        "## Transport evidence sufficiency",
        "## Secret-handling sufficiency",
        "## Recipient-handling sufficiency",
        "## Authority decision sufficiency",
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
    assert result["work_package_id"] == "ETF-EU-WP15AP"
    assert result["recipient_transport_authority_decision_created"] is True
    assert result["recipient_transport_authority_decision_validated"] is True
    assert result["recipient_authority_created"] is False
    assert result["transport_authority_created"] is False
    assert result["recipient_transport_authority_status"] == "not_authorized"
    assert result["readiness_gate_status"] == "recipient_transport_authority_decision_not_created"
    assert result["delivery_authorization_decision"] == "remain_blocked"
    assert result["delivery_preflight_allowed"] is False
    assert result["production_delivery"] is False
    assert result["secret_values_exposed"] is False
    assert result["recipient_plaintext_values_exposed"] is False
    assert result["remaining_delivery_preflight_blockers_count"] == 3
    assert result["selected_next_package"] == "ETF-EU-WP15AQ"
