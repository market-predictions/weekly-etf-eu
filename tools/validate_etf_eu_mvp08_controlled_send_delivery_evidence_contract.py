from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CONTRACT = Path("control/ETF_EU_MVP08_CONTROLLED_SEND_DELIVERY_EVIDENCE_CONTRACT_V1.md")
ARTIFACT = Path("output/client_surface/etf_eu_mvp08_controlled_send_delivery_evidence_contract_20260708_000000.json")
NOTES = Path("output/client_surface/etf_eu_mvp08_controlled_send_delivery_evidence_contract_notes_20260708_000000.md")

REQUIRED_TRUE = [
    "controlled_send_delivery_evidence_contract_created",
    "controlled_send_delivery_evidence_contract_validated",
    "future_delivery_status_values_defined",
    "delivery_status_caveat_required",
    "recipient_redaction_policy_defined",
    "language_evidence_schema_defined",
    "pdf_evidence_rule_defined",
    "final_run_bundle_reference_required",
    "evidence_validator_required",
    "failure_closed_behavior_required",
    "success_claim_requires_validated_evidence",
    "sender_entrypoint_validated",
    "controlled_send_preflight_validated",
    "workflow_send_guard_present",
]

REQUIRED_FALSE = [
    "receipt_file_created",
    "delivery_enabled",
    "production_delivery",
    "email_delivery",
    "pdf_generation",
    "delivery_receipt",
    "send_performed",
    "send_enablement_allowed",
    "delivery_mode_send_unlocked",
    "workflow_send_guard_removed",
    "delivery_success_claimed",
    "delivery_success_claim_allowed",
    "secret_values_exposed",
    "recipient_plaintext_values_exposed",
    "portfolio_mutation",
    "candidate_promotion",
    "funding_authority",
    "valuation_grade",
    "pricing_evidence_changed",
    "source_pdf_replaced",
    "new_pdf_created",
    "renderer_changed",
]

CONTRACT_MARKERS = [
    "# ETF EU MVP08 controlled-send delivery evidence contract v1",
    "## Rolemodel alignment",
    "## Delivery evidence rule",
    "## Delivery status caveat rule",
    "## Recipient redaction rule",
    "## Language evidence rule",
    "## Final run-bundle evidence rule",
    "## Success claim rule",
]

NOTE_MARKERS = [
    "# ETF-EU-MVP08 controlled-send delivery evidence contract",
    "## Rolemodel alignment",
    "## Delivery evidence contract",
    "## Delivery status caveat",
    "## Recipient redaction",
    "## Language evidence",
    "## Final run-bundle evidence",
    "## Failure handling",
    "## Send guard decision",
    "## Boundaries preserved",
    "## Next package",
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate() -> dict[str, Any]:
    for path in [CONTRACT, ARTIFACT, NOTES]:
        _require(path.exists(), f"missing file: {path}")

    data = _load(ARTIFACT)
    contract_text = CONTRACT.read_text(encoding="utf-8")
    notes_text = NOTES.read_text(encoding="utf-8")

    _require(data.get("work_package_id") == "ETF-EU-MVP08", "wrong work package")
    _require(data.get("source_work_package") == "ETF-EU-MVP07", "wrong source package")
    _require(data.get("delivery_evidence_status") == "contract_defined_not_executed", "delivery evidence status mismatch")
    _require(data.get("recipient_data_policy") == "redacted_hash_only", "recipient policy mismatch")
    _require(data.get("required_languages") == ["nl", "en"], "required languages mismatch")
    _require(data.get("dutch_primary_language") == "nl", "Dutch primary language mismatch")
    _require(data.get("english_companion_language") == "en", "English companion language mismatch")
    _require(data.get("sender_entrypoint_validation_status") == "validated_no_send", "sender status mismatch")
    _require(data.get("controlled_send_preflight_status") == "ready_for_future_delivery", "preflight status mismatch")

    for key in REQUIRED_TRUE:
        _require(data.get(key) is True, f"expected true for {key}")
    for key in REQUIRED_FALSE:
        _require(data.get(key) is False, f"expected false for {key}")

    statuses = data.get("future_delivery_status_values")
    _require(statuses == ["not_attempted", "smtp_sendmail_returned_no_exception", "smtp_sendmail_failed", "evidence_invalid"], "future statuses mismatch")
    caveat = str(data.get("delivery_status_caveat_text") or "")
    _require("not an end-recipient inbox receipt" in caveat, "missing inbox receipt caveat")

    for obj in [
        "delivery_evidence_contract_decision",
        "recipient_redaction_decision",
        "language_evidence_decision",
        "failure_handling_decision",
        "send_guard_decision",
        "next_step_decision",
    ]:
        _require(isinstance(data.get(obj), dict), f"missing object: {obj}")

    delivery = data["delivery_evidence_contract_decision"]
    _require(delivery.get("controlled_send_delivery_evidence_contract_validated") is True, "delivery contract object not validated")
    _require(delivery.get("success_claim_requires_validated_evidence") is True, "success evidence rule missing")
    _require(delivery.get("send_performed") is False, "delivery contract object performed send")

    redaction = data["recipient_redaction_decision"]
    _require(redaction.get("recipient_data_policy") == "redacted_hash_only", "redaction object policy mismatch")
    _require(redaction.get("recipient_hash_required") is True, "recipient hash rule missing")
    _require(redaction.get("recipient_redacted_required") is True, "recipient redacted rule missing")

    language = data["language_evidence_decision"]
    _require(language.get("required_languages") == ["nl", "en"], "language object mismatch")
    _require(language.get("language_count_required") == 2, "language count mismatch")

    failure = data["failure_handling_decision"]
    for key in [
        "fail_closed_without_delivery_evidence",
        "fail_closed_without_status_caveat",
        "fail_closed_without_recipient_redaction",
        "fail_closed_without_language_pair",
        "fail_closed_without_run_bundle_reference",
        "fail_closed_on_secret_exposure",
        "fail_closed_on_recipient_exposure",
    ]:
        _require(failure.get(key) is True, f"failure object missing {key}")
    _require(failure.get("delivery_success_claimed") is False, "failure object success claimed")
    _require(failure.get("delivery_success_claim_allowed") is False, "failure object success allowed")

    guard = data["send_guard_decision"]
    _require(guard.get("workflow_send_guard_present") is True, "guard object missing")
    _require(guard.get("workflow_send_guard_removed") is False, "guard removed")
    _require(guard.get("delivery_mode_send_unlocked") is False, "protected mode unlocked")
    _require(guard.get("send_enablement_allowed") is False, "send enablement allowed")

    selected = data.get("selected_next_package")
    _require(selected == "ETF-EU-MVP09", "selected next package mismatch")
    _require(not selected.startswith("ETF-EU-WP15"), "must not select WP15")
    _require(selected != "OPERATOR_ACTION_REQUIRED", "must not return operator action required")

    for marker in CONTRACT_MARKERS:
        _require(marker in contract_text, f"contract missing marker: {marker}")
    for marker in NOTE_MARKERS:
        _require(marker in notes_text, f"notes missing marker: {marker}")

    return {
        "status": "valid",
        "work_package_id": data["work_package_id"],
        "delivery_evidence_status": data["delivery_evidence_status"],
        "recipient_data_policy": data["recipient_data_policy"],
        "required_languages": data["required_languages"],
        "delivery_status_caveat_required": data["delivery_status_caveat_required"],
        "final_run_bundle_reference_required": data["final_run_bundle_reference_required"],
        "evidence_validator_required": data["evidence_validator_required"],
        "receipt_file_created": data["receipt_file_created"],
        "delivery_enabled": data["delivery_enabled"],
        "send_performed": data["send_performed"],
        "delivery_mode_send_unlocked": data["delivery_mode_send_unlocked"],
        "workflow_send_guard_removed": data["workflow_send_guard_removed"],
        "delivery_success_claimed": data["delivery_success_claimed"],
        "selected_next_package": data["selected_next_package"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
