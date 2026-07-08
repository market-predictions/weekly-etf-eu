from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_mvp09_controlled_send_implementation_with_delivery_evidence import validate as validate_mvp09
from tools.validate_etf_eu_mvp10_controlled_send_workflow_integration_or_guard_replacement import validate as validate_mvp10
from tools.validate_etf_eu_mvp11_workflow_dry_run_verification_with_integrated_evidence_gate import validate as validate_mvp11

CONTRACT = Path("control/ETF_EU_MVP12_NEXT_DECISION_PACKAGE_V1.md")
ARTIFACT = Path("output/client_surface/etf_eu_mvp12_next_decision_package_20260708_000000.json")
NOTES = Path("output/client_surface/etf_eu_mvp12_next_decision_package_notes_20260708_000000.md")

ALLOWED_DECISIONS = {
    "controlled_send_unlock_ready_for_implementation": "ETF-EU-MVP13",
    "additional_hardening_required": "ETF-EU-MVP12A",
}

REQUIRED_TRUE = [
    "decision_framework_created",
    "decision_framework_validated",
    "input_state_contract_created",
    "output_contract_created",
    "operational_runbook_created",
    "mvp11_gate_passed",
    "mvp11_validator_passed",
    "mvp10_workflow_integration_validator_passed",
    "mvp10_package_validator_passed",
    "mvp09_package_validator_passed",
]

REQUIRED_FALSE = [
    "delivery_mode_send_used",
    "delivery_mode_send_unlocked",
    "workflow_guard_removed",
    "guard_replacement_created",
    "delivery_success",
    "delivery_success_claimed",
    "send_performed",
    "email_delivery",
    "production_delivery",
    "secret_values_exposed",
    "recipient_plaintext_values_exposed",
    "portfolio_mutation",
    "funding_authority",
    "valuation_grade",
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
    _require(data.get("work_package_id") == "ETF-EU-MVP12", "wrong work package")
    _require(data.get("source_work_package") == "ETF-EU-MVP11", "wrong source package")
    _require(data.get("mvp11_workflow_run_id") == "28963021481", "wrong MVP11 run id")
    _require(data.get("mvp11_workflow_conclusion") == "success", "wrong MVP11 conclusion")
    _require(data.get("mvp11_run_mode") == "dry_run", "wrong MVP11 run mode")
    _require(data.get("mvp11_guard_step_conclusion") == "skipped", "wrong MVP11 guard conclusion")

    for key in REQUIRED_TRUE:
        _require(data.get(key) is True, f"expected true for {key}")
    for key in REQUIRED_FALSE:
        _require(data.get(key) is False, f"expected false for {key}")

    decision_status = data.get("decision_status")
    selected = data.get("selected_next_package")
    _require(decision_status in ALLOWED_DECISIONS, "invalid decision status")
    _require(selected == ALLOWED_DECISIONS[decision_status], "selected package mismatch")
    _require(selected in {"ETF-EU-MVP13", "ETF-EU-MVP12A"}, "selected package not allowed")
    _require(not selected.startswith("ETF-EU-WP15"), "must not select WP15")
    _require(selected != "OPERATOR_ACTION_REQUIRED", "must not select operator action required")

    for obj in ["decision_basis", "boundary_decision", "next_step_decision"]:
        _require(isinstance(data.get(obj), dict), f"missing object: {obj}")

    basis = data["decision_basis"]
    _require(basis.get("mvp11_green") is True, "MVP11 not green in decision basis")
    _require(basis.get("workflow_run_id") == "28963021481", "basis run id mismatch")
    _require(basis.get("workflow_conclusion") == "success", "basis conclusion mismatch")
    _require(basis.get("run_mode") == "dry_run", "basis run mode mismatch")
    _require(basis.get("gate_passed") is True, "basis gate mismatch")

    boundary = data["boundary_decision"]
    _require(boundary.get("decision_package_only") is True, "decision package flag missing")
    for key in REQUIRED_FALSE:
        if key in boundary:
            _require(boundary.get(key) is False, f"boundary expected false for {key}")

    next_step = data["next_step_decision"]
    _require(next_step.get("recommended_next_package") == selected, "next-step package mismatch")
    _require(next_step.get("fallback_next_package") == "ETF-EU-MVP12-FIX", "fallback mismatch")

    mvp11_result = validate_mvp11()
    mvp10_result = validate_mvp10()
    mvp09_result = validate_mvp09()
    _require(mvp11_result["status"] == "valid", "MVP11 validator failed")
    _require(mvp10_result["status"] == "valid", "MVP10 validator failed")
    _require(mvp09_result["status"] == "valid", "MVP09 validator failed")

    return {
        "status": "valid",
        "work_package_id": data["work_package_id"],
        "decision_status": decision_status,
        "selected_next_package": selected,
        "mvp11_workflow_run_id": data["mvp11_workflow_run_id"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
