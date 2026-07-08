from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SOURCE_PREFLIGHT = Path("output/client_surface/etf_eu_delivery_preflight_contract_runbook_20260703_000000.json")
SOURCE_CLIENT_GRADE = Path("output/client_surface/etf_eu_client_grade_authority_decision_20260703_000000.json")
SOURCE_LANGUAGE = Path("output/client_surface/etf_eu_client_language_quality_readiness_synthesis_20260703_000000.json")
SOURCE_DECISION = Path("output/client_surface/etf_eu_investment_thesis_invalidation_funding_posture_framework_20260703_000000.json")
SOURCE_INVESTABILITY = Path("output/client_surface/etf_eu_priips_kid_liquidity_spread_evidence_20260703_000000.json")
SOURCE_POLICY = Path("output/client_surface/etf_eu_pricing_freshness_valuation_policy_20260703_000000.json")
SOURCE_PRODUCT_FACTS = Path("output/client_surface/etf_eu_product_facts_evidence_20260703_000000.json")
SOURCE_PRICING = Path("output/client_surface/etf_eu_multi_line_pricing_preview_20260703_000000.json")
SOURCE_REGISTRY = Path("config/ucits_symbol_registry.yml")
SOURCE_PDF = Path("output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.pdf")
POLICY = Path("control/ETF_EU_DELIVERY_PREFLIGHT_AUTHORITY_DECISION_POLICY_V1.md")
ARTIFACT = Path("output/client_surface/etf_eu_delivery_preflight_authority_decision_20260703_000000.json")
NOTES = Path("output/client_surface/etf_eu_delivery_preflight_authority_decision_notes_20260703_000000.md")

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
    "delivery_preflight_authority_created",
    "delivery_preflight_allowed",
    "delivery_scope",
    "send_scope",
    "production_delivery_scope",
    "recipient_scope",
    "transport_scope",
    "required_next_package",
}
REQUIRED_INPUT_FIELDS = {
    "client_grade_authority_decision",
    "delivery_preflight_contract",
    "production_manifest_contract",
    "delivery_receipt_contract",
    "outbound_runbook",
    "post_send_verification_loop",
    "rollback_abort_policy",
    "recipient_authority_gate",
    "transport_authority_gate",
    "overall_contract_input_status",
}
REQUIRED_RECIPIENT_FIELDS = {
    "recipient_authority_gate_defined",
    "recipient_config_changed",
    "recipient_authority_created",
    "recipient_authority_status",
    "blocking_status",
}
REQUIRED_TRANSPORT_FIELDS = {
    "transport_authority_gate_defined",
    "smtp_or_secret_config_changed",
    "transport_authority_created",
    "transport_authority_status",
    "blocking_status",
}
REQUIRED_EXPLICIT_FIELDS = {
    "explicit_delivery_preflight_authority_decision_created",
    "explicit_delivery_preflight_authority_created",
    "delivery_preflight_allowed",
    "authority_status",
    "blocking_status",
}

REMAINING_BLOCKERS = {
    "recipient_configuration_authority",
    "transport_configuration_authority",
    "explicit_delivery_preflight_authority",
}
VALID_SOURCE_TYPES = {
    "internal_artifact",
    "internal_policy",
    "decision_framework",
    "authority_decision",
    "delivery_preflight_contract",
    "delivery_preflight_authority_decision",
}
VALID_AUTHORITY_LEVELS = VALID_SOURCE_TYPES

POLICY_MARKERS = [
    "# ETF EU delivery-preflight authority decision policy v1",
    "## Purpose",
    "## Scope",
    "## Authority boundary",
    "## Required authority inputs",
    "## Recipient authority sufficiency rule",
    "## Transport authority sufficiency rule",
    "## Explicit delivery-preflight authority rule",
    "## Positive authority decision rule",
    "## Negative authority decision rule",
    "## What this policy does not authorize",
    "## Validation requirements",
]
NOTE_MARKERS = [
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
    for path in [SOURCE_PREFLIGHT, SOURCE_CLIENT_GRADE, SOURCE_LANGUAGE, SOURCE_DECISION, SOURCE_INVESTABILITY, SOURCE_POLICY, SOURCE_PRODUCT_FACTS, SOURCE_PRICING, SOURCE_REGISTRY, SOURCE_PDF, POLICY, ARTIFACT, NOTES]:
        _require(path.exists(), f"missing file: {path}")

    preflight = _load(SOURCE_PREFLIGHT)
    client_grade = _load(SOURCE_CLIENT_GRADE)
    language = _load(SOURCE_LANGUAGE)
    decision = _load(SOURCE_DECISION)
    investability = _load(SOURCE_INVESTABILITY)
    policy_source = _load(SOURCE_POLICY)
    product_facts = _load(SOURCE_PRODUCT_FACTS)
    data = _load(ARTIFACT)

    _require(preflight.get("work_package_id") == "ETF-EU-WP15AM", "source preflight mismatch")
    _require(client_grade.get("work_package_id") == "ETF-EU-WP15AL", "source client-grade mismatch")
    _require(language.get("work_package_id") == "ETF-EU-WP15AK", "source language mismatch")
    _require(decision.get("work_package_id") == "ETF-EU-WP15AJ", "source decision mismatch")
    _require(investability.get("work_package_id") == "ETF-EU-WP15AI", "source investability mismatch")
    _require(policy_source.get("work_package_id") == "ETF-EU-WP15AH", "source policy mismatch")
    _require(product_facts.get("work_package_id") == "ETF-EU-WP15AG", "source product facts mismatch")

    _require(data.get("work_package_id") == "ETF-EU-WP15AN", "wrong work package")
    _require(data.get("source_work_package") == "ETF-EU-WP15AM", "wrong source package")
    _require(data.get("source_delivery_preflight_contract_artifact") == str(SOURCE_PREFLIGHT), "source preflight path mismatch")
    _require(data.get("source_client_grade_authority_artifact") == str(SOURCE_CLIENT_GRADE), "source client-grade path mismatch")
    _require(data.get("source_client_grade_pdf") == str(SOURCE_PDF), "source PDF mismatch")
    _require(data.get("delivery_preflight_authority_policy_path") == str(POLICY), "policy path mismatch")

    _require(data.get("delivery_preflight_authority_decision_created") is True, "decision not created")
    _require(data.get("delivery_preflight_authority_decision_validated") is True, "decision not validated")
    _require(data.get("client_grade_authority_created") is True, "client-grade authority missing")
    _require(data.get("client_grade_claim") is True, "client-grade claim missing")
    _require(data.get("client_grade_status") == "authorized_no_delivery", "client-grade status mismatch")

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
        "delivery_preflight_authority_decision": REQUIRED_DECISION_FIELDS,
        "authority_input_sufficiency": REQUIRED_INPUT_FIELDS,
        "recipient_authority_sufficiency": REQUIRED_RECIPIENT_FIELDS,
        "transport_authority_sufficiency": REQUIRED_TRANSPORT_FIELDS,
        "explicit_delivery_preflight_authority_sufficiency": REQUIRED_EXPLICIT_FIELDS,
    }
    for name, fields in objects.items():
        obj = data.get(name)
        _require(isinstance(obj, dict), f"missing object: {name}")
        _require_fields(obj, fields, name)

    _require(data.get("delivery_preflight_authority_created") is False, "authority must not be created")
    _require(data.get("delivery_preflight_allowed") is False, "preflight must not be allowed")
    _require(data.get("delivery_preflight_status") == "not_authorized", "preflight status mismatch")
    _require(data.get("readiness_gate_status") == "delivery_preflight_authority_not_created", "readiness status mismatch")
    _require(data.get("delivery_authorization_decision") == "remain_blocked", "delivery authorization mismatch")
    _require(data.get("outbound_path_enabled") is False, "outbound path must be false")
    _require(data.get("remaining_client_grade_blockers") == [], "client-grade blockers must be empty")
    _require(set(data.get("remaining_delivery_preflight_blockers", [])) == REMAINING_BLOCKERS, "remaining blockers mismatch")
    _require(data.get("selected_next_package") == "ETF-EU-WP15AO", "next package mismatch")

    d = data["delivery_preflight_authority_decision"]
    _require(d["decision_status"] == "validated", "decision status mismatch")
    _require(d["decision_result"] == "not_authorized", "decision result mismatch")
    _require(d["decision_reason"] == "recipient_and_transport_authority_missing", "decision reason mismatch")
    _require(d["delivery_preflight_authority_created"] is False, "decision authority mismatch")
    _require(d["delivery_preflight_allowed"] is False, "decision allowed mismatch")
    _require(d["required_next_package"] == "ETF-EU-WP15AO", "decision next package mismatch")

    _require(data["authority_input_sufficiency"]["overall_contract_input_status"] == "passed_for_decision_not_execution", "input status mismatch")
    _require(data["recipient_authority_sufficiency"]["recipient_authority_created"] is False, "recipient authority mismatch")
    _require(data["recipient_authority_sufficiency"]["recipient_authority_status"] == "missing", "recipient status mismatch")
    _require(data["transport_authority_sufficiency"]["transport_authority_created"] is False, "transport authority mismatch")
    _require(data["transport_authority_sufficiency"]["transport_authority_status"] == "missing", "transport status mismatch")
    _require(data["explicit_delivery_preflight_authority_sufficiency"]["explicit_delivery_preflight_authority_created"] is False, "explicit authority mismatch")
    _require(data["explicit_delivery_preflight_authority_sufficiency"]["delivery_preflight_allowed"] is False, "explicit allowed mismatch")

    manifest = data.get("source_manifest")
    _require(isinstance(manifest, list) and manifest, "source manifest missing")
    used_fields = " ".join(" ".join(source.get("used_for_fields", [])) for source in manifest)
    for required in ["delivery-preflight authority decision", "authority input sufficiency", "recipient authority sufficiency", "transport authority sufficiency", "explicit delivery-preflight authority sufficiency"]:
        _require(required in used_fields, f"source support missing: {required}")
    for source in manifest:
        _require(source.get("source_type") in VALID_SOURCE_TYPES, "invalid source type")
        _require(source.get("authority_level") in VALID_AUTHORITY_LEVELS, "invalid authority level")
        _require(source.get("source_reference"), "source reference missing")

    for key in REQUIRED_FALSE:
        _require(data.get(key) is False, f"expected false for {key}")
    _require(data.get("review_only") is False, "review_only must remain false")
    _require(data.get("pricing_evidence_for_client_grade") is True, "client-grade pricing evidence must remain true")

    for path, markers in {POLICY: POLICY_MARKERS, NOTES: NOTE_MARKERS}.items():
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            _require(marker in text, f"{path} missing marker: {marker}")

    return {
        "status": "valid",
        "work_package_id": data["work_package_id"],
        "delivery_preflight_authority_decision_created": data["delivery_preflight_authority_decision_created"],
        "delivery_preflight_authority_decision_validated": data["delivery_preflight_authority_decision_validated"],
        "delivery_preflight_authority_created": data["delivery_preflight_authority_created"],
        "delivery_preflight_allowed": data["delivery_preflight_allowed"],
        "delivery_preflight_status": data["delivery_preflight_status"],
        "readiness_gate_status": data["readiness_gate_status"],
        "delivery_authorization_decision": data["delivery_authorization_decision"],
        "production_delivery": data["production_delivery"],
        "receipt_artifact_created": data["receipt_artifact_created"],
        "production_manifest_created": data["production_manifest_created"],
        "recipient_authority_created": data["recipient_authority_created"],
        "transport_authority_created": data["transport_authority_created"],
        "remaining_client_grade_blockers_count": len(data["remaining_client_grade_blockers"]),
        "remaining_delivery_preflight_blockers_count": len(data["remaining_delivery_preflight_blockers"]),
        "selected_next_package": data["selected_next_package"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
