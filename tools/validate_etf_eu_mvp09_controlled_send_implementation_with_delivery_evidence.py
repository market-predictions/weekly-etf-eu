from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_delivery_evidence import validate as validate_delivery_evidence
from tools.validate_etf_eu_run_bundle_delivery_evidence import validate as validate_run_bundle_delivery_evidence

CONTRACT = Path("control/ETF_EU_MVP09_CONTROLLED_SEND_IMPLEMENTATION_WITH_DELIVERY_EVIDENCE_V1.md")
ARTIFACT = Path("output/client_surface/etf_eu_mvp09_controlled_send_implementation_with_delivery_evidence_20260708_000000.json")
NOTES = Path("output/client_surface/etf_eu_mvp09_controlled_send_implementation_with_delivery_evidence_notes_20260708_000000.md")
WRITER = Path("runtime/write_etf_eu_delivery_evidence.py")
EVIDENCE_VALIDATOR = Path("tools/validate_etf_eu_delivery_evidence.py")
RUN_BUNDLE_VALIDATOR = Path("tools/validate_etf_eu_run_bundle_delivery_evidence.py")
EVIDENCE_FIXTURE = Path("output/delivery/etf_eu_delivery_evidence_20260708_000000.json")
RUN_BUNDLE_FIXTURE = Path("output/runs/20260708_000000/etf_eu_run_bundle_delivery_evidence_fixture.json")

REQUIRED_TRUE = [
    "delivery_evidence_writer_created",
    "delivery_evidence_validator_created",
    "run_bundle_delivery_evidence_validator_created",
    "delivery_evidence_fixture_created",
    "delivery_evidence_fixture_validated",
    "run_bundle_delivery_evidence_fixture_created",
    "run_bundle_delivery_evidence_fixture_validated",
    "delivery_status_caveat_supported",
    "future_success_status_supported",
    "future_success_status_requires_caveat",
    "final_run_bundle_reference_required",
    "evidence_validator_required",
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
    "delivery_success",
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


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate() -> dict[str, Any]:
    for path in [CONTRACT, ARTIFACT, NOTES, WRITER, EVIDENCE_VALIDATOR, RUN_BUNDLE_VALIDATOR, EVIDENCE_FIXTURE, RUN_BUNDLE_FIXTURE]:
        _require(path.exists(), f"missing file: {path}")

    data = _load(ARTIFACT)
    _require(data.get("work_package_id") == "ETF-EU-MVP09", "wrong work package")
    _require(data.get("source_work_package") == "ETF-EU-MVP08", "wrong source package")
    _require(data.get("source_mvp08_artifact") == "output/client_surface/etf_eu_mvp08_controlled_send_delivery_evidence_contract_20260708_000000.json", "MVP08 source path mismatch")
    _require(data.get("delivery_evidence_path") == str(EVIDENCE_FIXTURE), "evidence path mismatch")
    _require(data.get("run_bundle_delivery_evidence_fixture") == str(RUN_BUNDLE_FIXTURE), "run-bundle fixture path mismatch")
    _require(data.get("delivery_evidence_status") == "not_attempted", "delivery evidence status mismatch")
    _require(data.get("recipient_data_policy") == "redacted_hash_only", "recipient policy mismatch")
    _require(data.get("required_languages") == ["nl", "en"], "required languages mismatch")
    _require(data.get("dutch_primary_language") == "nl", "Dutch primary language mismatch")
    _require(data.get("english_companion_language") == "en", "English companion language mismatch")
    _require(data.get("controlled_send_preflight_status") == "ready_for_future_delivery", "preflight status mismatch")

    for key in REQUIRED_TRUE:
        _require(data.get(key) is True, f"expected true for {key}")
    for key in REQUIRED_FALSE:
        _require(data.get(key) is False, f"expected false for {key}")

    for obj in [
        "delivery_evidence_implementation_decision",
        "run_bundle_reference_decision",
        "failure_handling_decision",
        "send_guard_decision",
        "next_step_decision",
    ]:
        _require(isinstance(data.get(obj), dict), f"missing object: {obj}")

    implementation = data["delivery_evidence_implementation_decision"]
    _require(implementation.get("delivery_evidence_writer_created") is True, "writer decision mismatch")
    _require(implementation.get("delivery_evidence_validator_created") is True, "validator decision mismatch")
    _require(implementation.get("delivery_evidence_status") == "not_attempted", "implementation status mismatch")
    _require(implementation.get("delivery_success") is False, "implementation must not mark success")

    run_bundle = data["run_bundle_reference_decision"]
    _require(run_bundle.get("run_bundle_delivery_evidence_validator_created") is True, "run-bundle validator decision mismatch")
    _require(run_bundle.get("run_bundle_delivery_evidence_fixture_validated") is True, "run-bundle fixture decision mismatch")
    _require(run_bundle.get("delivery_success") is False, "run-bundle fixture must not mark success")

    failure = data["failure_handling_decision"]
    for key in [
        "fail_closed_without_delivery_evidence",
        "fail_closed_without_status_caveat_for_success",
        "fail_closed_without_recipient_redaction",
        "fail_closed_without_language_pair",
        "fail_closed_without_run_bundle_reference",
        "fail_closed_on_secret_exposure",
        "fail_closed_on_recipient_exposure",
    ]:
        _require(failure.get(key) is True, f"failure rule missing: {key}")
    _require(failure.get("delivery_success") is False, "failure object must not mark success")
    _require(failure.get("delivery_success_claimed") is False, "failure object must not claim success")
    _require(failure.get("delivery_success_claim_allowed") is False, "failure object must not allow success claim")

    guard = data["send_guard_decision"]
    _require(guard.get("workflow_send_guard_present") is True, "guard missing")
    _require(guard.get("workflow_send_guard_removed") is False, "guard removed")
    _require(guard.get("delivery_mode_send_unlocked") is False, "protected mode unlocked")
    _require(guard.get("send_enablement_allowed") is False, "send enablement allowed")

    selected = data.get("selected_next_package")
    _require(selected == "ETF-EU-MVP10", "selected next package mismatch")
    _require(not selected.startswith("ETF-EU-WP15"), "must not select WP15")
    _require(selected != "OPERATOR_ACTION_REQUIRED", "must not return to operator action required")

    evidence_result = validate_delivery_evidence(EVIDENCE_FIXTURE)
    run_bundle_result = validate_run_bundle_delivery_evidence(RUN_BUNDLE_FIXTURE)
    _require(evidence_result["delivery_status"] == "not_attempted", "evidence validator status mismatch")
    _require(run_bundle_result["delivery_evidence_status"] == "not_attempted", "run-bundle validator status mismatch")

    return {
        "status": "valid",
        "work_package_id": data["work_package_id"],
        "delivery_evidence_status": data["delivery_evidence_status"],
        "recipient_data_policy": data["recipient_data_policy"],
        "required_languages": data["required_languages"],
        "delivery_success": data["delivery_success"],
        "delivery_enabled": data["delivery_enabled"],
        "send_performed": data["send_performed"],
        "delivery_mode_send_unlocked": data["delivery_mode_send_unlocked"],
        "workflow_send_guard_removed": data["workflow_send_guard_removed"],
        "delivery_success_claimed": data["delivery_success_claimed"],
        "selected_next_package": data["selected_next_package"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
