from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SOURCE_PREFLIGHT_AUTHORITY = Path("output/client_surface/etf_eu_delivery_preflight_authority_decision_20260703_000000.json")
SOURCE_PREFLIGHT_CONTRACT = Path("output/client_surface/etf_eu_delivery_preflight_contract_runbook_20260703_000000.json")
SOURCE_CLIENT_GRADE = Path("output/client_surface/etf_eu_client_grade_authority_decision_20260703_000000.json")
SOURCE_PRICING = Path("output/client_surface/etf_eu_multi_line_pricing_preview_20260703_000000.json")
SOURCE_REGISTRY = Path("config/ucits_symbol_registry.yml")
SOURCE_PDF = Path("output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.pdf")
CONTRACT = Path("control/ETF_EU_RECIPIENT_TRANSPORT_AUTHORITY_EVIDENCE_CONTRACT_V1.md")
ARTIFACT = Path("output/client_surface/etf_eu_recipient_transport_authority_evidence_contract_20260703_000000.json")
NOTES = Path("output/client_surface/etf_eu_recipient_transport_authority_evidence_contract_notes_20260703_000000.md")

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
    "recipient_authority_created",
    "transport_authority_created",
    "secret_values_exposed",
    "recipient_plaintext_values_exposed",
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

REQUIRED_RECIPIENT_FIELDS = {
    "contract_status",
    "recipient_authority_evidence_status",
    "recipient_set_reference_id_required",
    "recipient_set_hash_required",
    "recipient_plaintext_values_allowed",
    "recipient_owner_approval_reference_required",
    "recipient_change_scope",
    "recipient_change_authority_required",
    "recipient_validation_method",
    "recipient_rollback_reference_required",
    "recipient_authority_created",
    "recipient_config_changed",
}
REQUIRED_TRANSPORT_FIELDS = {
    "contract_status",
    "transport_authority_evidence_status",
    "transport_reference_id_required",
    "transport_secret_reference_names_allowed",
    "transport_secret_values_allowed",
    "transport_presence_check_required",
    "transport_owner_approval_reference_required",
    "transport_change_scope",
    "transport_change_authority_required",
    "transport_validation_method",
    "transport_rollback_reference_required",
    "transport_authority_created",
    "smtp_or_secret_config_changed",
}
REQUIRED_SUFFICIENCY_FIELDS = {
    "recipient_authority_evidence_contract_defined",
    "transport_authority_evidence_contract_defined",
    "recipient_authority_created",
    "transport_authority_created",
    "recipient_config_changed",
    "smtp_or_secret_config_changed",
    "secret_values_exposed",
    "recipient_plaintext_values_exposed",
    "authority_status",
    "blocking_status",
}
VALID_SOURCE_TYPES = {
    "internal_artifact",
    "internal_policy",
    "decision_framework",
    "authority_decision",
    "delivery_preflight_contract",
    "recipient_transport_authority_evidence_contract",
}
VALID_AUTHORITY_LEVELS = VALID_SOURCE_TYPES

CONTRACT_MARKERS = [
    "# ETF EU recipient and transport authority evidence contract v1",
    "## Purpose",
    "## Scope",
    "## Authority boundary",
    "## Recipient authority evidence contract",
    "## Transport authority evidence contract",
    "## Secret-handling boundary",
    "## Recipient-handling boundary",
    "## Evidence sufficiency rules",
    "## Positive evidence contract rule",
    "## Negative authority rule",
    "## What this contract does not authorize",
    "## Validation requirements",
]
NOTE_MARKERS = [
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
    for path in [SOURCE_PREFLIGHT_AUTHORITY, SOURCE_PREFLIGHT_CONTRACT, SOURCE_CLIENT_GRADE, SOURCE_PRICING, SOURCE_REGISTRY, SOURCE_PDF, CONTRACT, ARTIFACT, NOTES]:
        _require(path.exists(), f"missing file: {path}")

    preflight_authority = _load(SOURCE_PREFLIGHT_AUTHORITY)
    preflight_contract = _load(SOURCE_PREFLIGHT_CONTRACT)
    client_grade = _load(SOURCE_CLIENT_GRADE)
    data = _load(ARTIFACT)

    _require(preflight_authority.get("work_package_id") == "ETF-EU-WP15AN", "source preflight authority mismatch")
    _require(preflight_contract.get("work_package_id") == "ETF-EU-WP15AM", "source preflight contract mismatch")
    _require(client_grade.get("work_package_id") == "ETF-EU-WP15AL", "source client-grade mismatch")

    _require(data.get("work_package_id") == "ETF-EU-WP15AO", "wrong work package")
    _require(data.get("source_work_package") == "ETF-EU-WP15AN", "wrong source package")
    _require(data.get("source_delivery_preflight_authority_artifact") == str(SOURCE_PREFLIGHT_AUTHORITY), "source preflight authority path mismatch")
    _require(data.get("source_delivery_preflight_contract_artifact") == str(SOURCE_PREFLIGHT_CONTRACT), "source preflight contract path mismatch")
    _require(data.get("source_client_grade_authority_artifact") == str(SOURCE_CLIENT_GRADE), "source client-grade path mismatch")
    _require(data.get("source_pricing_artifact") == str(SOURCE_PRICING), "source pricing path mismatch")
    _require(data.get("source_registry") == str(SOURCE_REGISTRY), "source registry mismatch")
    _require(data.get("source_client_grade_pdf") == str(SOURCE_PDF), "source PDF mismatch")
    _require(data.get("recipient_transport_authority_evidence_contract_path") == str(CONTRACT), "contract path mismatch")

    for key in [
        "recipient_transport_authority_evidence_contract_created",
        "recipient_transport_authority_evidence_contract_validated",
        "recipient_authority_evidence_contract_created",
        "recipient_authority_evidence_contract_validated",
        "transport_authority_evidence_contract_created",
        "transport_authority_evidence_contract_validated",
        "client_grade_authority_created",
        "client_grade_claim",
        "pricing_evidence_for_client_grade",
    ]:
        _require(data.get(key) is True, f"expected true for {key}")

    _require(data.get("readiness_gate_status") == "recipient_transport_authority_evidence_contract_defined_not_authorized", "readiness status mismatch")
    _require(data.get("client_grade_status") == "authorized_no_delivery", "client-grade status mismatch")
    _require(data.get("delivery_preflight_status") == "not_authorized", "preflight status mismatch")
    _require(data.get("delivery_authorization_decision") == "remain_blocked", "delivery authorization mismatch")

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

    recipient = data.get("recipient_authority_evidence_contract")
    transport = data.get("transport_authority_evidence_contract")
    sufficiency = data.get("authority_evidence_sufficiency")
    _require(isinstance(recipient, dict), "recipient evidence contract missing")
    _require(isinstance(transport, dict), "transport evidence contract missing")
    _require(isinstance(sufficiency, dict), "authority evidence sufficiency missing")
    _require_fields(recipient, REQUIRED_RECIPIENT_FIELDS, "recipient evidence contract")
    _require_fields(transport, REQUIRED_TRANSPORT_FIELDS, "transport evidence contract")
    _require_fields(sufficiency, REQUIRED_SUFFICIENCY_FIELDS, "authority evidence sufficiency")

    _require(recipient["contract_status"] == "defined_not_authorized", "recipient contract status mismatch")
    _require(recipient["recipient_plaintext_values_allowed"] is False, "plaintext recipients must not be allowed")
    _require(recipient["recipient_authority_created"] is False, "recipient authority must remain false")
    _require(recipient["recipient_config_changed"] is False, "recipient config must remain false")
    _require(transport["contract_status"] == "defined_not_authorized", "transport contract status mismatch")
    _require(transport["transport_secret_values_allowed"] is False, "secret values must not be allowed")
    _require(transport["transport_authority_created"] is False, "transport authority must remain false")
    _require(transport["smtp_or_secret_config_changed"] is False, "transport config must remain false")
    _require(sufficiency["authority_status"] == "evidence_contract_defined_not_authorized", "authority status mismatch")
    _require(sufficiency["blocking_status"] == "blocking_delivery_preflight", "blocking status mismatch")

    _require(data.get("remaining_client_grade_blockers") == [], "client-grade blockers must be empty")
    _require(set(data.get("remaining_delivery_preflight_blockers", [])) == REMAINING_BLOCKERS, "remaining blockers mismatch")
    _require(data.get("selected_next_package") in {"ETF-EU-WP15AP", "ETF-EU-WP15AO-FIX"}, "invalid next package")

    for key in REQUIRED_FALSE:
        _require(data.get(key) is False, f"expected false for {key}")
    _require(data.get("review_only") is False, "review_only must remain false")

    manifest = data.get("source_manifest")
    _require(isinstance(manifest, list) and manifest, "source manifest missing")
    used_fields = " ".join(" ".join(source.get("used_for_fields", [])) for source in manifest)
    for required in ["recipient authority evidence contract", "transport authority evidence contract", "authority evidence sufficiency", "delivery-preflight blocker preservation"]:
        _require(required in used_fields, f"source support missing: {required}")
    for source in manifest:
        _require(source.get("source_type") in VALID_SOURCE_TYPES, "invalid source type")
        _require(source.get("authority_level") in VALID_AUTHORITY_LEVELS, "invalid authority level")
        _require(source.get("source_reference"), "source reference missing")

    for path, markers in {CONTRACT: CONTRACT_MARKERS, NOTES: NOTE_MARKERS}.items():
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            _require(marker in text, f"{path} missing marker: {marker}")

    return {
        "status": "valid",
        "work_package_id": data["work_package_id"],
        "recipient_transport_authority_evidence_contract_created": data["recipient_transport_authority_evidence_contract_created"],
        "recipient_transport_authority_evidence_contract_validated": data["recipient_transport_authority_evidence_contract_validated"],
        "recipient_authority_evidence_contract_created": data["recipient_authority_evidence_contract_created"],
        "transport_authority_evidence_contract_created": data["transport_authority_evidence_contract_created"],
        "readiness_gate_status": data["readiness_gate_status"],
        "recipient_authority_created": data["recipient_authority_created"],
        "transport_authority_created": data["transport_authority_created"],
        "recipient_config_changed": data["recipient_config_changed"],
        "smtp_or_secret_config_changed": data["smtp_or_secret_config_changed"],
        "secret_values_exposed": data["secret_values_exposed"],
        "recipient_plaintext_values_exposed": data["recipient_plaintext_values_exposed"],
        "delivery_preflight_allowed": data["delivery_preflight_allowed"],
        "production_delivery": data["production_delivery"],
        "remaining_delivery_preflight_blockers_count": len(data["remaining_delivery_preflight_blockers"]),
        "selected_next_package": data["selected_next_package"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
