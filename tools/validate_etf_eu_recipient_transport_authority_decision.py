from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SOURCE_RT_EVIDENCE = Path("output/client_surface/etf_eu_recipient_transport_authority_evidence_contract_20260703_000000.json")
SOURCE_PREFLIGHT_AUTHORITY = Path("output/client_surface/etf_eu_delivery_preflight_authority_decision_20260703_000000.json")
SOURCE_PREFLIGHT_CONTRACT = Path("output/client_surface/etf_eu_delivery_preflight_contract_runbook_20260703_000000.json")
SOURCE_CLIENT_GRADE = Path("output/client_surface/etf_eu_client_grade_authority_decision_20260703_000000.json")
SOURCE_PRICING = Path("output/client_surface/etf_eu_multi_line_pricing_preview_20260703_000000.json")
SOURCE_REGISTRY = Path("config/ucits_symbol_registry.yml")
SOURCE_PDF = Path("output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.pdf")
POLICY = Path("control/ETF_EU_RECIPIENT_TRANSPORT_AUTHORITY_DECISION_POLICY_V1.md")
ARTIFACT = Path("output/client_surface/etf_eu_recipient_transport_authority_decision_20260703_000000.json")
NOTES = Path("output/client_surface/etf_eu_recipient_transport_authority_decision_notes_20260703_000000.md")

REMAINING_BLOCKERS = {
    "recipient_configuration_authority",
    "transport_configuration_authority",
    "explicit_delivery_preflight_authority",
}

REQUIRED_FALSE = [
    "delivery_ready",
    "delivery_preflight_authority_created",
    "delivery_preflight_allowed",
    "outbound_path_enabled",
    "production_delivery",
    "portfolio_mutation",
    "candidate_promotion",
    "funding_authority",
    "valuation_grade",
    "pricing_evidence_for_delivery_preflight",
    "receipt_artifact_created",
    "production_manifest_created",
    "recipient_config_changed",
    "smtp_or_secret_config_changed",
    "secret_values_exposed",
    "recipient_plaintext_values_exposed",
    "recipient_authority_created",
    "transport_authority_created",
    "fake_price_used",
    "us_proxy_price_used",
    "live_price_fetch_performed",
    "live_data_fetch_performed",
    "pricing_evidence_changed",
    "recommendation_logic_changed",
    "source_pdf_replaced",
    "new_pdf_created",
    "renderer_changed",
]

REQUIRED_DECISION_FIELDS = {
    "decision_status",
    "decision_result",
    "decision_reason",
    "recipient_authority_created",
    "transport_authority_created",
    "recipient_scope",
    "transport_scope",
    "secret_scope",
    "recipient_plaintext_scope",
    "delivery_preflight_scope",
    "send_scope",
    "production_delivery_scope",
    "required_next_package",
}
REQUIRED_RECIPIENT_FIELDS = {
    "recipient_authority_evidence_contract_defined",
    "recipient_set_reference_id_present",
    "recipient_set_hash_present",
    "recipient_owner_approval_reference_present",
    "recipient_rollback_reference_present",
    "recipient_plaintext_values_exposed",
    "recipient_config_changed",
    "recipient_authority_created",
    "recipient_evidence_status",
    "blocking_status",
}
REQUIRED_TRANSPORT_FIELDS = {
    "transport_authority_evidence_contract_defined",
    "transport_reference_id_present",
    "transport_presence_check_reference_present",
    "transport_owner_approval_reference_present",
    "transport_rollback_reference_present",
    "secret_values_exposed",
    "smtp_or_secret_config_changed",
    "transport_authority_created",
    "transport_evidence_status",
    "blocking_status",
}
REQUIRED_SECRET_FIELDS = {
    "secret_values_exposed",
    "secret_reference_names_only",
    "transport_config_changed",
    "secret_handling_status",
}
REQUIRED_RECIPIENT_HANDLING_FIELDS = {
    "recipient_plaintext_values_exposed",
    "recipient_reference_or_hash_only",
    "recipient_config_changed",
    "recipient_handling_status",
}
REQUIRED_AUTHORITY_FIELDS = {
    "recipient_authority_can_be_created",
    "transport_authority_can_be_created",
    "recipient_transport_authority_status",
    "delivery_preflight_can_be_opened",
    "production_delivery_can_be_created",
    "authority_status",
    "blocking_status",
}
VALID_SOURCE_TYPES = {
    "internal_artifact",
    "internal_policy",
    "decision_framework",
    "authority_decision",
    "recipient_transport_authority_evidence_contract",
    "recipient_transport_authority_decision",
}
VALID_AUTHORITY_LEVELS = VALID_SOURCE_TYPES

POLICY_MARKERS = [
    "# ETF EU recipient and transport authority decision policy v1",
    "## Purpose",
    "## Scope",
    "## Authority boundary",
    "## Required recipient evidence",
    "## Required transport evidence",
    "## Secret-handling decision rule",
    "## Recipient-handling decision rule",
    "## Positive authority decision rule",
    "## Negative authority decision rule",
    "## What this policy does not authorize",
    "## Validation requirements",
]
NOTE_MARKERS = [
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
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _require_fields(obj: dict[str, Any], fields: set[str], label: str) -> None:
    for field in fields:
        _require(field in obj, f"{label} missing field: {field}")
        _require(obj[field] not in (None, "", []), f"{label} empty field: {field}")


def validate() -> dict[str, Any]:
    for path in [SOURCE_RT_EVIDENCE, SOURCE_PREFLIGHT_AUTHORITY, SOURCE_PREFLIGHT_CONTRACT, SOURCE_CLIENT_GRADE, SOURCE_PRICING, SOURCE_REGISTRY, SOURCE_PDF, POLICY, ARTIFACT, NOTES]:
        _require(path.exists(), f"missing file: {path}")

    rt_evidence = _load(SOURCE_RT_EVIDENCE)
    preflight_authority = _load(SOURCE_PREFLIGHT_AUTHORITY)
    preflight_contract = _load(SOURCE_PREFLIGHT_CONTRACT)
    client_grade = _load(SOURCE_CLIENT_GRADE)
    data = _load(ARTIFACT)

    _require(rt_evidence.get("work_package_id") == "ETF-EU-WP15AO", "source RT evidence mismatch")
    _require(preflight_authority.get("work_package_id") == "ETF-EU-WP15AN", "source preflight authority mismatch")
    _require(preflight_contract.get("work_package_id") == "ETF-EU-WP15AM", "source preflight contract mismatch")
    _require(client_grade.get("work_package_id") == "ETF-EU-WP15AL", "source client-grade mismatch")

    _require(data.get("work_package_id") == "ETF-EU-WP15AP", "wrong work package")
    _require(data.get("source_work_package") == "ETF-EU-WP15AO", "wrong source package")
    _require(data.get("source_recipient_transport_authority_evidence_contract_artifact") == str(SOURCE_RT_EVIDENCE), "source RT evidence path mismatch")
    _require(data.get("source_delivery_preflight_authority_artifact") == str(SOURCE_PREFLIGHT_AUTHORITY), "source preflight authority path mismatch")
    _require(data.get("source_delivery_preflight_contract_artifact") == str(SOURCE_PREFLIGHT_CONTRACT), "source preflight contract path mismatch")
    _require(data.get("source_client_grade_authority_artifact") == str(SOURCE_CLIENT_GRADE), "source client-grade path mismatch")
    _require(data.get("source_pricing_artifact") == str(SOURCE_PRICING), "source pricing path mismatch")
    _require(data.get("source_registry") == str(SOURCE_REGISTRY), "source registry mismatch")
    _require(data.get("source_client_grade_pdf") == str(SOURCE_PDF), "source PDF mismatch")
    _require(data.get("recipient_transport_authority_decision_policy_path") == str(POLICY), "policy path mismatch")

    for key in [
        "recipient_transport_authority_decision_created",
        "recipient_transport_authority_decision_validated",
        "client_grade_authority_created",
        "client_grade_claim",
        "pricing_evidence_for_client_grade",
    ]:
        _require(data.get(key) is True, f"expected true for {key}")

    _require(data.get("recipient_authority_created") is False, "recipient authority must be false")
    _require(data.get("transport_authority_created") is False, "transport authority must be false")
    _require(data.get("recipient_transport_authority_status") == "not_authorized", "RT authority status mismatch")
    _require(data.get("readiness_gate_status") == "recipient_transport_authority_decision_not_created", "readiness status mismatch")
    _require(data.get("delivery_authorization_decision") == "remain_blocked", "delivery authorization mismatch")
    _require(data.get("client_grade_status") == "authorized_no_delivery", "client-grade status mismatch")
    _require(data.get("delivery_preflight_status") == "not_authorized", "preflight status mismatch")

    _require(data.get("pdf_exists") is True, "pdf_exists must be true")
    _require(data.get("pdf_page_count") == 4, "PDF page count mismatch")
    _require(data.get("successful_rows_count") == 2, "successful rows mismatch")
    _require(data.get("failed_rows_count") == 0, "failed rows mismatch")
    _require(data.get("skipped_rows_count") == 1, "skipped rows mismatch")
    _require(data.get("first_successful_symbol") == "SXR8.DE", "SXR8 symbol mismatch")
    _require(data.get("first_successful_close_date") == "2026-07-03", "SXR8 date mismatch")
    _require(data.get("first_successful_close") == 706.119995, "SXR8 close mismatch")
    _require(data.get("second_successful_symbol") == "CSPX.L", "CSPX symbol mismatch")
    _require(data.get("second_successful_close_date") == "2026-07-03", "CSPX date mismatch")
    _require(data.get("second_successful_close") == 807.859985, "CSPX close mismatch")
    _require(data.get("smh_status") == "skipped_pending_registry_status", "SMH status mismatch")

    objects = {
        "recipient_transport_authority_decision": REQUIRED_DECISION_FIELDS,
        "recipient_evidence_sufficiency": REQUIRED_RECIPIENT_FIELDS,
        "transport_evidence_sufficiency": REQUIRED_TRANSPORT_FIELDS,
        "secret_handling_sufficiency": REQUIRED_SECRET_FIELDS,
        "recipient_handling_sufficiency": REQUIRED_RECIPIENT_HANDLING_FIELDS,
        "authority_decision_sufficiency": REQUIRED_AUTHORITY_FIELDS,
    }
    for name, fields in objects.items():
        obj = data.get(name)
        _require(isinstance(obj, dict), f"missing object: {name}")
        _require_fields(obj, fields, name)

    d = data["recipient_transport_authority_decision"]
    _require(d["decision_status"] == "validated", "decision status mismatch")
    _require(d["decision_result"] == "not_authorized", "decision result mismatch")
    _require(d["decision_reason"] == "concrete_recipient_and_transport_evidence_missing", "decision reason mismatch")
    _require(d["recipient_authority_created"] is False, "decision recipient authority mismatch")
    _require(d["transport_authority_created"] is False, "decision transport authority mismatch")
    _require(d["secret_scope"] == "not_exposed", "secret scope mismatch")
    _require(d["recipient_plaintext_scope"] == "not_exposed", "recipient plaintext scope mismatch")
    _require(d["required_next_package"] == "ETF-EU-WP15AQ", "decision next package mismatch")

    recipient = data["recipient_evidence_sufficiency"]
    _require(recipient["recipient_authority_evidence_contract_defined"] is True, "recipient contract not defined")
    _require(recipient["recipient_set_reference_id_present"] is False, "recipient reference should be missing")
    _require(recipient["recipient_set_hash_present"] is False, "recipient hash should be missing")
    _require(recipient["recipient_owner_approval_reference_present"] is False, "recipient approval should be missing")
    _require(recipient["recipient_rollback_reference_present"] is False, "recipient rollback should be missing")
    _require(recipient["recipient_evidence_status"] == "missing_concrete_evidence", "recipient evidence status mismatch")

    transport = data["transport_evidence_sufficiency"]
    _require(transport["transport_authority_evidence_contract_defined"] is True, "transport contract not defined")
    _require(transport["transport_reference_id_present"] is False, "transport reference should be missing")
    _require(transport["transport_presence_check_reference_present"] is False, "presence check should be missing")
    _require(transport["transport_owner_approval_reference_present"] is False, "transport approval should be missing")
    _require(transport["transport_rollback_reference_present"] is False, "transport rollback should be missing")
    _require(transport["transport_evidence_status"] == "missing_concrete_evidence", "transport evidence status mismatch")

    _require(data["secret_handling_sufficiency"]["secret_values_exposed"] is False, "secret values exposed")
    _require(data["secret_handling_sufficiency"]["secret_reference_names_only"] is True, "secret reference names rule mismatch")
    _require(data["secret_handling_sufficiency"]["secret_handling_status"] == "passed_no_secret_exposure", "secret handling status mismatch")
    _require(data["recipient_handling_sufficiency"]["recipient_plaintext_values_exposed"] is False, "recipient plaintext exposed")
    _require(data["recipient_handling_sufficiency"]["recipient_reference_or_hash_only"] is True, "recipient reference/hash rule mismatch")
    _require(data["recipient_handling_sufficiency"]["recipient_handling_status"] == "passed_no_plaintext_exposure", "recipient handling status mismatch")
    _require(data["authority_decision_sufficiency"]["authority_status"] == "negative_authority_decision", "authority status mismatch")
    _require(data["authority_decision_sufficiency"]["blocking_status"] == "blocking_delivery_preflight", "blocking status mismatch")

    _require(data.get("remaining_client_grade_blockers") == [], "client-grade blockers must be empty")
    _require(set(data.get("remaining_delivery_preflight_blockers", [])) == REMAINING_BLOCKERS, "remaining blockers mismatch")
    _require(data.get("selected_next_package") in {"ETF-EU-WP15AQ", "ETF-EU-WP15AP-FIX"}, "invalid next package")

    for key in REQUIRED_FALSE:
        _require(data.get(key) is False, f"expected false for {key}")
    _require(data.get("review_only") is False, "review_only must remain false")

    manifest = data.get("source_manifest")
    _require(isinstance(manifest, list) and manifest, "source manifest missing")
    used_fields = " ".join(" ".join(source.get("used_for_fields", [])) for source in manifest)
    for required in ["recipient and transport authority decision", "recipient evidence sufficiency", "transport evidence sufficiency", "secret-handling sufficiency", "recipient-handling sufficiency", "authority decision sufficiency", "delivery-preflight blocker preservation"]:
        _require(required in used_fields, f"source support missing: {required}")
    for source in manifest:
        _require(source.get("source_type") in VALID_SOURCE_TYPES, "invalid source type")
        _require(source.get("authority_level") in VALID_AUTHORITY_LEVELS, "invalid authority level")
        _require(source.get("source_reference"), "source reference missing")

    for path, markers in {POLICY: POLICY_MARKERS, NOTES: NOTE_MARKERS}.items():
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            _require(marker in text, f"{path} missing marker: {marker}")

    return {
        "status": "valid",
        "work_package_id": data["work_package_id"],
        "recipient_transport_authority_decision_created": data["recipient_transport_authority_decision_created"],
        "recipient_transport_authority_decision_validated": data["recipient_transport_authority_decision_validated"],
        "recipient_authority_created": data["recipient_authority_created"],
        "transport_authority_created": data["transport_authority_created"],
        "recipient_transport_authority_status": data["recipient_transport_authority_status"],
        "readiness_gate_status": data["readiness_gate_status"],
        "delivery_authorization_decision": data["delivery_authorization_decision"],
        "delivery_preflight_allowed": data["delivery_preflight_allowed"],
        "production_delivery": data["production_delivery"],
        "secret_values_exposed": data["secret_values_exposed"],
        "recipient_plaintext_values_exposed": data["recipient_plaintext_values_exposed"],
        "remaining_delivery_preflight_blockers_count": len(data["remaining_delivery_preflight_blockers"]),
        "selected_next_package": data["selected_next_package"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
