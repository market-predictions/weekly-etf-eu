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
from tools.validate_etf_eu_mvp10_workflow_delivery_evidence_integration import validate as validate_mvp10_workflow

CONTRACT = Path("control/ETF_EU_MVP11_WORKFLOW_DRY_RUN_VERIFICATION_WITH_INTEGRATED_EVIDENCE_GATE_V1.md")
ARTIFACT = Path("output/client_surface/etf_eu_mvp11_workflow_dry_run_verification_with_integrated_evidence_gate_20260708_000000.json")
NOTES = Path("output/client_surface/etf_eu_mvp11_workflow_dry_run_verification_with_integrated_evidence_gate_notes_20260708_000000.md")


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate() -> dict[str, Any]:
    for path in [CONTRACT, ARTIFACT, NOTES]:
        _require(path.exists(), f"missing file: {path}")
    data = _load(ARTIFACT)
    _require(data.get("work_package_id") == "ETF-EU-MVP11", "wrong work package")
    _require(data.get("source_work_package") == "ETF-EU-MVP10", "wrong source package")
    _require(str(data.get("workflow_run_id")) == "28963021481", "wrong run id")
    _require(data.get("workflow_status") == "completed", "workflow status mismatch")
    _require(data.get("workflow_conclusion") == "success", "workflow conclusion mismatch")
    _require(data.get("run_mode") == "dry_run", "run mode mismatch")
    _require(data.get("gate_passed") is True, "gate not passed")
    _require(data.get("selected_next_package") == "ETF-EU-MVP12", "next package mismatch")

    workflow_result = validate_mvp10_workflow()
    mvp10_result = validate_mvp10()
    mvp09_result = validate_mvp09()
    _require(workflow_result["status"] == "valid", "MVP10 workflow validator failed")
    _require(mvp10_result["status"] == "valid", "MVP10 package validator failed")
    _require(mvp09_result["status"] == "valid", "MVP09 package validator failed")

    return {
        "status": "valid",
        "work_package_id": data["work_package_id"],
        "workflow_run_id": data["workflow_run_id"],
        "workflow_conclusion": data["workflow_conclusion"],
        "run_mode": data["run_mode"],
        "gate_passed": data["gate_passed"],
        "selected_next_package": data["selected_next_package"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
