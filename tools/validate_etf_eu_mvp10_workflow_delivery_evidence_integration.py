from __future__ import annotations

import json
from pathlib import Path
from typing import Any

WORKFLOW = Path(".github/workflows/send-weekly-etf-eu-report.yml")
GATE_NAME = "Validate MVP09 delivery evidence integration gate"
RUN_BUNDLE_STEP = "Build and validate run bundle manifest"
INHERITED_DISABLED_STEP = "Validate inherited US production sender is disabled"


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _step_block(text: str, step_name: str) -> str:
    marker = f"- name: {step_name}"
    start = text.find(marker)
    _require(start >= 0, f"missing step: {step_name}")
    next_start = text.find("\n      - name:", start + len(marker))
    if next_start == -1:
        return text[start:]
    return text[start:next_start]


def validate(workflow_path: Path = WORKFLOW) -> dict[str, Any]:
    workflow_path = Path(workflow_path)
    _require(workflow_path.exists(), f"missing workflow: {workflow_path}")
    text = workflow_path.read_text(encoding="utf-8")

    for mode in ["validate_only", "dry_run", "send"]:
        _require(f"          - {mode}" in text, f"delivery_mode option missing: {mode}")

    _require("ETF_EU_SEND_MODE_REQUESTED" in text, "send guard marker missing")
    guard_block = _step_block(text, "Guard EU send mode until sender entrypoint is promoted")
    _require("exit 1" in guard_block, "send guard exit missing")
    _require("env.ETF_EU_DELIVERY_MODE == 'send'" in guard_block, "send guard condition missing")

    _require(GATE_NAME in text, "MVP10 evidence integration gate missing")
    run_bundle_index = text.find(RUN_BUNDLE_STEP)
    gate_index = text.find(GATE_NAME)
    _require(run_bundle_index >= 0, "run bundle manifest step missing")
    _require(gate_index > run_bundle_index, "evidence gate must appear after run bundle manifest step")

    gate_block = _step_block(text, GATE_NAME)
    _require("tools/validate_etf_eu_delivery_evidence.py" in gate_block, "delivery evidence validator not called")
    _require("tools/validate_etf_eu_run_bundle_delivery_evidence.py" in gate_block, "run-bundle delivery evidence validator not called")
    _require("tools/validate_etf_eu_mvp09_controlled_send_implementation_with_delivery_evidence.py" in gate_block, "MVP09 package validator not called")
    for prohibited in ["MRKT_RPRTS", "smtp", "sendmail", "send_report", "delivery_mode=send"]:
        _require(prohibited not in gate_block.lower(), f"prohibited token in evidence gate: {prohibited}")

    _require(INHERITED_DISABLED_STEP in text, "inherited send-disabled check removed")
    inherited_block = _step_block(text, INHERITED_DISABLED_STEP)
    _require("DISABLED_INHERITED_US_ETF_SEND_WORKFLOW" in inherited_block, "inherited disabled marker missing")
    _require("Validate EU output, pricing surface and fundability contracts" in text, "output/pricing/fundability validation missing")
    _require("Build and validate blocked delivery manifest" in text, "blocked delivery manifest step missing")
    _require("python -m runtime.build_etf_eu_delivery_manifest" in text, "blocked delivery manifest builder missing")
    _require("python -m runtime.build_etf_eu_run_bundle" in text, "run bundle builder missing")

    return {
        "status": "valid",
        "workflow": str(workflow_path),
        "workflow_integration_type": "fixture_validation_gate",
        "workflow_send_guard_present": True,
        "workflow_send_guard_removed": False,
        "workflow_send_guard_exit_present": True,
        "delivery_evidence_gate_added": True,
        "delivery_evidence_gate_after_run_bundle": True,
        "delivery_evidence_validator_called": True,
        "run_bundle_delivery_evidence_validator_called": True,
        "mvp09_package_validator_called": True,
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
