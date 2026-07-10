from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Missing JSON file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _assert(data: dict[str, Any], key: str, expected: Any) -> list[str]:
    if data.get(key) != expected:
        return [f"{key}={data.get(key)!r}, expected={expected!r}"]
    return []


def validate(path: Path) -> None:
    data = _read_json(path)
    errors: list[str] = []

    for key, expected in {
        "schema_version": "etf_eu_controlled_delivery_decision_v1",
        "artifact_type": "etf_eu_controlled_delivery_decision",
        "source_of_truth_repo": "market-predictions/weekly-etf-eu",
        "reference_architecture_repo": "market-predictions/weekly-etf",
        "ready_for_controlled_delivery": True,
        "delivery_authorized": True,
        "send_command_allowed": True,
        "recipient_plaintext_values_exposed": False,
        "secret_values_exposed": False,
        "raw_receipt_pdf_stored_in_github": False,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
    }.items():
        errors.extend(_assert(data, key, expected))

    for label in ["authorization_artifact", "delivery_prep_artifact", "package_manifest", "routine_run_manifest"]:
        value = data.get(label)
        if not value or not Path(str(value)).exists():
            errors.append(f"{label}_missing_or_not_found:{value}")

    status = data.get("controlled_delivery_decision_status")
    if status == "blocked_no_transport_selected":
        for key in [
            "workflow_dispatch_allowed",
            "run_queue_allowed",
            "run_queue_created",
            "transport_execution_allowed",
            "send_executed",
            "transport_attempted",
            "transport_success",
            "receipt_confirmed",
        ]:
            errors.extend(_assert(data, key, False))
    elif status == "run_queue_artifact_created":
        for key, expected in {
            "workflow_dispatch_allowed": False,
            "run_queue_allowed": True,
            "run_queue_created": True,
            "transport_execution_allowed": False,
            "send_executed": False,
            "transport_attempted": False,
            "transport_success": False,
            "receipt_confirmed": False,
        }.items():
            errors.extend(_assert(data, key, expected))
        queue = data.get("run_queue_artifact")
        if not queue or not Path(str(queue)).exists():
            errors.append(f"run_queue_artifact_missing:{queue}")
        elif "@" in Path(str(queue)).read_text(encoding="utf-8"):
            errors.append("run_queue_artifact_may_contain_plaintext_recipient")
    elif status == "transport_execution_recorded":
        if data.get("transport_attempted") is not True:
            errors.append("transport_executed mode requires transport_attempted=true")
        if data.get("transport_success") is True and not data.get("delivery_evidence_artifact"):
            errors.append("transport_success=true requires delivery_evidence_artifact")
        if data.get("receipt_confirmed") is True and not data.get("receipt_evidence_artifact"):
            errors.append("receipt_confirmed=true requires receipt_evidence_artifact")
    else:
        errors.append(f"unknown controlled_delivery_decision_status={status}")

    routine_path = Path(str(data.get("routine_run_manifest") or ""))
    if routine_path.exists():
        routine = _read_json(routine_path)
        if routine.get("controlled_delivery_decision_artifact") != str(path):
            errors.append("routine manifest does not reference controlled delivery decision artifact")
    else:
        errors.append("routine run manifest does not exist")

    if errors:
        raise SystemExit("ETF EU controlled delivery decision validation failed: " + "; ".join(sorted(set(errors))))

    print(f"ETF_EU_CONTROLLED_DELIVERY_DECISION_VALID | decision={path} | status={status}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate ETF EU controlled delivery decision or run queue artifact.")
    parser.add_argument("--decision", type=Path, required=True)
    args = parser.parse_args()
    validate(args.decision)


if __name__ == "__main__":
    main()
