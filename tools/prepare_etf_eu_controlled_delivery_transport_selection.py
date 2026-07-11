from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_controlled_delivery_transport_selection_v1"
ARTIFACT_TYPE = "etf_eu_controlled_delivery_transport_selection"
NEXT_PACKAGE = "ETF-EU-MVP28C_EU_DELIVERY_WORKFLOW_WIRING"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"missing required input: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _require(data: dict[str, Any], key: str, expected: Any) -> None:
    if data.get(key) != expected:
        raise RuntimeError(f"expected {key}={expected!r}, got {data.get(key)!r}")


def build(args: argparse.Namespace) -> dict[str, Any]:
    authorization_path = Path(args.authorization)
    decision_path = Path(args.controlled_delivery_decision)
    prep_path = Path(args.delivery_prep)
    package_path = Path(args.package_manifest)
    routine_path = Path(args.routine_manifest)

    authorization = _read_json(authorization_path)
    decision = _read_json(decision_path)
    _read_json(prep_path)
    _read_json(package_path)
    _read_json(routine_path)

    _require(authorization, "ready_for_controlled_delivery", True)
    _require(authorization, "delivery_authorized", True)
    _require(authorization, "send_command_allowed", True)
    _require(authorization, "workflow_dispatch_allowed", False)
    _require(authorization, "run_queue_allowed", False)
    _require(authorization, "transport_execution_allowed", False)
    _require(authorization, "send_executed", False)
    _require(authorization, "transport_attempted", False)
    _require(authorization, "receipt_confirmed", False)
    _require(decision, "controlled_delivery_decision_status", "blocked_no_transport_selected")

    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": ARTIFACT_TYPE,
        "generated_at_utc": args.generated_at_utc or _utc_now(),
        "run_id": args.run_id,
        "report_date": args.report_date,
        "report_suffix": args.report_suffix,
        "source_of_truth_repo": "market-predictions/weekly-etf-eu",
        "reference_architecture_repo": "market-predictions/weekly-etf",
        "upstream_pattern_adapted": "weekly-etf queue-triggered delivery and manifest-evidence concepts; adapted for EU package-bound authority",
        "ready_for_controlled_delivery": True,
        "delivery_authorized": True,
        "send_command_allowed": True,
        "controlled_delivery_decision_status": "blocked_no_transport_selected",
        "controlled_delivery_decision_artifact": str(decision_path),
        "authorization_artifact": str(authorization_path),
        "delivery_prep_artifact": str(prep_path),
        "package_manifest": str(package_path),
        "routine_run_manifest": str(routine_path),
        "transport_selection_status": "blocked_missing_eu_delivery_workflow_wiring",
        "selected_transport_mode": "none",
        "run_queue_created": False,
        "run_queue_allowed": False,
        "run_queue_artifact": None,
        "workflow_dispatch_allowed": False,
        "transport_execution_allowed": False,
        "send_executed": False,
        "transport_attempted": False,
        "transport_success": False,
        "receipt_confirmed": False,
        "delivery_evidence_artifact": None,
        "receipt_evidence_artifact": None,
        "recipient_plaintext_values_exposed": False,
        "secret_values_exposed": False,
        "raw_receipt_pdf_stored_in_github": False,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
        "next_package": NEXT_PACKAGE,
        "blockers": ["eu_workflow_targets_legacy_delivery_package_not_current_fresh_package_chain"],
        "warnings": ["Queue was not created because no compatible current-package workflow wiring was found."],
    }


def update_routine(path: Path, artifact: dict[str, Any], output_path: Path) -> None:
    routine = _read_json(path)
    routine.update({
        "controlled_delivery_transport_selection_artifact": str(output_path),
        "transport_selection_status": artifact["transport_selection_status"],
        "selected_transport_mode": artifact["selected_transport_mode"],
        "run_queue_created": False,
        "run_queue_allowed": False,
        "run_queue_artifact": None,
        "workflow_dispatch_allowed": False,
        "transport_execution_allowed": False,
        "send_executed": False,
        "transport_attempted": False,
        "transport_success": False,
        "receipt_confirmed": False,
        "next_package": NEXT_PACKAGE,
        "routine_stage": "blocked_missing_eu_delivery_workflow_wiring",
        "workflow_status": "blocked_missing_eu_delivery_workflow_wiring",
    })
    path.write_text(json.dumps(routine, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--report-suffix", required=True)
    parser.add_argument("--authorization", required=True)
    parser.add_argument("--controlled-delivery-decision", required=True)
    parser.add_argument("--delivery-prep", required=True)
    parser.add_argument("--package-manifest", required=True)
    parser.add_argument("--routine-manifest", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--generated-at-utc", default=None)
    args = parser.parse_args()

    artifact = build(args)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    update_routine(Path(args.routine_manifest), artifact, output)
    print(f"ETF_EU_TRANSPORT_SELECTION_OK | status={artifact['transport_selection_status']} | output={output}")


if __name__ == "__main__":
    main()
