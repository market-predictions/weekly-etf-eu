from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_guarded_fresh_package_delivery_prep_v1"
ARTIFACT_TYPE = "etf_eu_guarded_fresh_package_delivery_prep"
SOURCE_OF_TRUTH_REPO = "market-predictions/weekly-etf-eu"
REFERENCE_ARCHITECTURE_REPO = "market-predictions/weekly-etf"

FALSE_FIELDS = [
    "delivery_authorized",
    "send_command_allowed",
    "workflow_dispatch_allowed",
    "run_queue_allowed",
    "send_executed",
    "transport_attempted",
    "transport_success",
    "receipt_confirmed",
    "valuation_grade",
    "funding_authority",
    "portfolio_mutation",
    "production_delivery_authority",
    "recipient_plaintext_values_exposed",
    "secret_values_exposed",
    "raw_receipt_pdf_stored_in_github",
]

TRUE_FIELDS = [
    "ready_for_controlled_delivery",
    "delivery_prep_created",
    "explicit_user_authorization_required",
    "guarded_send_confirmation_required",
]

PATH_FIELDS = [
    "package_manifest",
    "ready_artifact",
    "package_readiness_gate",
    "routine_run_manifest",
    "dutch_primary_markdown",
    "english_companion_markdown",
    "dutch_primary_html",
    "english_companion_html",
    "dutch_primary_pdf",
    "english_companion_pdf",
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _path(value: object, label: str) -> Path:
    raw = str(value or "").strip()
    _require(bool(raw), f"{label} missing")
    path = Path(raw)
    _require(path.exists(), f"{label} does not exist: {path}")
    return path


def validate(prep_path: Path) -> dict[str, Any]:
    prep_path = Path(prep_path)
    _require(prep_path.exists(), f"delivery-prep artifact missing: {prep_path}")
    data = _load(prep_path)

    _require(data.get("schema_version") == SCHEMA_VERSION, "schema_version mismatch")
    _require(data.get("artifact_type") == ARTIFACT_TYPE, "artifact_type mismatch")
    _require(data.get("source_of_truth_repo") == SOURCE_OF_TRUTH_REPO, "source_of_truth_repo mismatch")
    _require(data.get("reference_architecture_repo") == REFERENCE_ARCHITECTURE_REPO, "reference_architecture_repo mismatch")
    _require(bool(data.get("upstream_pattern_adapted")), "upstream_pattern_adapted missing")

    for field in TRUE_FIELDS:
        _require(data.get(field) is True, f"{field} must be true")
    for field in FALSE_FIELDS:
        _require(data.get(field) is False, f"{field} must be false")

    for field in PATH_FIELDS:
        _path(data.get(field), field)

    package = _load(Path(data["package_manifest"]))
    ready = _load(Path(data["ready_artifact"]))
    gate = _load(Path(data["package_readiness_gate"]))
    routine = _load(Path(data["routine_run_manifest"]))

    _require(package.get("ready_for_controlled_delivery") is True, "package manifest is not readiness-gated")
    _require(ready.get("ready_for_controlled_delivery") is True, "ready artifact is not readiness-gated")
    _require(ready.get("delivery_authorized") is False, "ready artifact must not authorize delivery")
    _require(gate.get("readiness_gate_passed") is True, "readiness gate has not passed")
    _require(gate.get("delivery_authorized") is False, "readiness gate must not authorize delivery")

    _require(routine.get("delivery_prep_artifact") == str(prep_path), "routine run manifest does not reference delivery-prep artifact")
    _require(routine.get("routine_stage") == "guarded_fresh_package_delivery_prep_created", "routine_stage mismatch")
    _require(routine.get("ready_for_controlled_delivery") is True, "routine manifest must preserve ready_for_controlled_delivery=true")
    _require(routine.get("delivery_authorized") is False, "routine manifest must keep delivery_authorized=false")
    _require(routine.get("transport_attempted") is False, "routine manifest must keep transport_attempted=false")
    _require(routine.get("transport_success") is False, "routine manifest must keep transport_success=false")
    _require(routine.get("receipt_confirmed") is False, "routine manifest must keep receipt_confirmed=false")

    return {
        "status": "valid",
        "prep": str(prep_path),
        "ready_for_controlled_delivery": data.get("ready_for_controlled_delivery"),
        "delivery_authorized": data.get("delivery_authorized"),
        "next_package": data.get("next_package"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate guarded ETF EU fresh-package delivery-prep artifact.")
    parser.add_argument("--prep", required=True)
    args = parser.parse_args()
    print(json.dumps(validate(Path(args.prep)), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
