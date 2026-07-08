from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_controlled_send_preflight_manifest import validate as validate_preflight_manifest

CONTRACT = Path("control/ETF_EU_MVP07_MANIFEST_TRANSITION_AND_CONTROLLED_SEND_PREFLIGHT_V1.md")
ARTIFACT = Path("output/client_surface/etf_eu_mvp07_manifest_transition_and_controlled_send_preflight_20260708_000000.json")
NOTES = Path("output/client_surface/etf_eu_mvp07_manifest_transition_and_controlled_send_preflight_notes_20260708_000000.md")
SENDER_PREFLIGHT = Path("output/delivery/etf_eu_sender_preflight_20260708_000000.json")
PREFLIGHT_MANIFEST = Path("output/delivery/etf_eu_controlled_send_preflight_manifest_20260708_000000.json")
PREFLIGHT_VALIDATOR = Path("tools/validate_etf_eu_controlled_send_preflight_manifest.py")
WORKFLOW = Path(".github/workflows/send-weekly-etf-eu-report.yml")

REQUIRED_TRUE = [
    "sender_entrypoint_validated",
    "manifest_transition_created",
    "manifest_transition_validated",
    "controlled_send_preflight_created",
    "controlled_send_preflight_validated",
    "receipt_path_reserved",
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

NOTE_MARKERS = [
    "# ETF-EU-MVP07 manifest transition and controlled-send preflight",
    "## Source evidence",
    "## Sender preflight evidence",
    "## Manifest transition",
    "## Controlled-send preflight manifest",
    "## Receipt reservation",
    "## Send guard decision",
    "## Boundaries preserved",
    "## Decision",
    "## Next package",
]

CONTRACT_MARKERS = [
    "# ETF EU MVP07 manifest transition and controlled-send preflight v1",
    "## Manifest transition rule",
    "## Controlled-send preflight rule",
    "## Sender preflight evidence rule",
    "## Receipt reservation rule",
    "## Send guard rule",
    "## Success claim rule",
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate() -> dict[str, Any]:
    for path in [CONTRACT, ARTIFACT, NOTES, SENDER_PREFLIGHT, PREFLIGHT_MANIFEST, PREFLIGHT_VALIDATOR, WORKFLOW]:
        _require(path.exists(), f"missing file: {path}")

    data = _load(ARTIFACT)
    preflight = _load(PREFLIGHT_MANIFEST)
    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    notes_text = NOTES.read_text(encoding="utf-8")
    contract_text = CONTRACT.read_text(encoding="utf-8")

    _require(data.get("work_package_id") == "ETF-EU-MVP07", "wrong work package")
    _require(data.get("source_work_package") == "ETF-EU-MVP06", "wrong source package")
    _require(data.get("sender_preflight_artifact") == str(SENDER_PREFLIGHT), "sender preflight path mismatch")
    _require(data.get("controlled_send_preflight_manifest") == str(PREFLIGHT_MANIFEST), "preflight manifest path mismatch")
    _require(data.get("source_mvp06_artifact") == "output/client_surface/etf_eu_mvp06_sender_entrypoint_implementation_or_validation_20260708_000000.json", "MVP06 source mismatch")

    for key in REQUIRED_TRUE:
        _require(data.get(key) is True, f"expected true for {key}")
    for key in REQUIRED_FALSE:
        _require(data.get(key) is False, f"expected false for {key}")

    _require(data.get("sender_entrypoint_validation_status") == "validated_no_send", "sender status mismatch")
    _require(data.get("manifest_transition_status") == "ready_for_future_delivery", "manifest transition status mismatch")
    _require(data.get("controlled_send_preflight_status") == "ready_for_future_delivery", "controlled preflight status mismatch")
    _require(data.get("receipt_status") == "pending", "receipt status mismatch")
    _require(data.get("selected_next_package") == "ETF-EU-MVP08", "selected next package mismatch")
    _require(not data["selected_next_package"].startswith("ETF-EU-WP15"), "must not select WP15")
    _require(data["selected_next_package"] != "OPERATOR_ACTION_REQUIRED", "must not return to operator action")

    transition = data.get("manifest_transition_decision")
    _require(isinstance(transition, dict), "missing transition object")
    _require(transition.get("base_manifest_status") == "blocked_design_only", "base status mismatch")
    _require(transition.get("target_preflight_status") == "ready_for_future_delivery", "target status mismatch")
    _require(transition.get("receipt_file_created") is False, "receipt file must not be created")
    _require(transition.get("delivery_authority_created") is False, "delivery authority must not be created")

    guard = data.get("send_guard_decision")
    _require(isinstance(guard, dict), "missing guard object")
    _require(guard.get("workflow_send_guard_present") is True, "workflow guard missing")
    _require(guard.get("workflow_send_guard_removed") is False, "workflow guard removed")
    _require(guard.get("delivery_mode_send_unlocked") is False, "protected mode unlocked")
    _require(guard.get("send_enablement_allowed") is False, "send enablement allowed")

    receipt = data.get("receipt_and_success_boundary")
    _require(isinstance(receipt, dict), "missing receipt object")
    _require(receipt.get("receipt_path_reserved") is True, "receipt path not reserved")
    _require(receipt.get("receipt_file_created") is False, "receipt file created")
    _require(receipt.get("delivery_success_claimed") is False, "success claimed")
    _require(receipt.get("delivery_success_claim_allowed") is False, "success claim allowed")

    _require(preflight.get("status") == "ready_for_future_delivery", "preflight manifest status mismatch")
    _require(preflight.get("delivery_enabled") is False, "preflight delivery_enabled mismatch")
    _require(preflight.get("receipt", {}).get("receipt_status") == "pending", "preflight receipt status mismatch")
    _require(not Path(preflight["receipt"]["receipt_path"]).exists(), "reserved receipt file exists")

    _require("Guard EU send mode until sender entrypoint is promoted" in workflow_text, "workflow guard marker missing")
    _require("ETF_EU_SEND_MODE_REQUESTED" in workflow_text, "workflow protected-mode marker missing")
    _require("exit 1" in workflow_text, "workflow guard must remain blocking")

    for marker in CONTRACT_MARKERS:
        _require(marker in contract_text, f"contract missing marker: {marker}")
    for marker in NOTE_MARKERS:
        _require(marker in notes_text, f"notes missing marker: {marker}")

    preflight_result = validate_preflight_manifest(PREFLIGHT_MANIFEST, SENDER_PREFLIGHT)
    _require(preflight_result.get("status") == "valid", "preflight validator failed")

    return {
        "status": "valid",
        "work_package_id": data["work_package_id"],
        "manifest_transition_status": data["manifest_transition_status"],
        "controlled_send_preflight_status": data["controlled_send_preflight_status"],
        "receipt_path_reserved": data["receipt_path_reserved"],
        "receipt_file_created": data["receipt_file_created"],
        "receipt_status": data["receipt_status"],
        "delivery_enabled": data["delivery_enabled"],
        "send_performed": data["send_performed"],
        "delivery_mode_send_unlocked": data["delivery_mode_send_unlocked"],
        "workflow_send_guard_removed": data["workflow_send_guard_removed"],
        "delivery_success_claimed": data["delivery_success_claimed"],
        "selected_next_package": data["selected_next_package"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
