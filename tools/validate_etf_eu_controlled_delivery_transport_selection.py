from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_controlled_delivery_transport_selection_v1"
ARTIFACT_TYPE = "etf_eu_controlled_delivery_transport_selection"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"missing file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _expect(data: dict[str, Any], key: str, expected: Any, errors: list[str]) -> None:
    if data.get(key) != expected:
        errors.append(f"{key}={data.get(key)!r}; expected {expected!r}")


def validate(path: Path) -> None:
    data = _read_json(path)
    errors: list[str] = []

    _expect(data, "schema_version", SCHEMA_VERSION, errors)
    _expect(data, "artifact_type", ARTIFACT_TYPE, errors)
    _expect(data, "source_of_truth_repo", "market-predictions/weekly-etf-eu", errors)
    _expect(data, "reference_architecture_repo", "market-predictions/weekly-etf", errors)
    _expect(data, "ready_for_controlled_delivery", True, errors)
    _expect(data, "delivery_authorized", True, errors)
    _expect(data, "send_command_allowed", True, errors)
    _expect(data, "controlled_delivery_decision_status", "blocked_no_transport_selected", errors)
    _expect(data, "transport_selection_status", "blocked_missing_eu_delivery_workflow_wiring", errors)
    _expect(data, "selected_transport_mode", "none", errors)
    _expect(data, "run_queue_created", False, errors)
    _expect(data, "run_queue_allowed", False, errors)
    _expect(data, "workflow_dispatch_allowed", False, errors)
    _expect(data, "transport_execution_allowed", False, errors)
    _expect(data, "send_executed", False, errors)
    _expect(data, "transport_attempted", False, errors)
    _expect(data, "transport_success", False, errors)
    _expect(data, "receipt_confirmed", False, errors)
    _expect(data, "recipient_plaintext_values_exposed", False, errors)
    _expect(data, "secret_values_exposed", False, errors)
    _expect(data, "raw_receipt_pdf_stored_in_github", False, errors)
    _expect(data, "valuation_grade", False, errors)
    _expect(data, "funding_authority", False, errors)
    _expect(data, "portfolio_mutation", False, errors)
    _expect(data, "production_delivery_authority", False, errors)
    _expect(data, "next_package", "ETF-EU-MVP28C_EU_DELIVERY_WORKFLOW_WIRING", errors)

    for key in [
        "authorization_artifact",
        "controlled_delivery_decision_artifact",
        "delivery_prep_artifact",
        "package_manifest",
        "routine_run_manifest",
    ]:
        value = data.get(key)
        if not value or not Path(str(value)).exists():
            errors.append(f"missing referenced path for {key}: {value}")

    if errors:
        raise RuntimeError("ETF EU transport selection validation failed: " + "; ".join(errors))
    print(f"ETF_EU_TRANSPORT_SELECTION_VALID | selection={path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selection", required=True)
    args = parser.parse_args()
    validate(Path(args.selection))


if __name__ == "__main__":
    main()
