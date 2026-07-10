from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_guarded_send_authorization_v1"
ARTIFACT_TYPE = "etf_eu_guarded_send_authorization"
SOURCE_OF_TRUTH_REPO = "market-predictions/weekly-etf-eu"
REFERENCE_ARCHITECTURE_REPO = "market-predictions/weekly-etf"
AUTHORIZED_NEXT_PACKAGE = "ETF-EU-MVP28_CONTROLLED_SEND_EXECUTION_OR_RUN_QUEUE"
BLOCKED_NEXT_PACKAGE = "ETF-EU-MVP27B_EXPLICIT_SEND_AUTHORIZATION_RETRY"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _path(value: Any, label: str) -> Path:
    raw = str(value or "").strip()
    _require(bool(raw), f"{label} missing")
    path = Path(raw)
    _require(path.exists(), f"{label} does not exist: {path}")
    return path


def _false(data: dict[str, Any], key: str) -> None:
    _require(data.get(key) is False, f"{key} must be false")


def validate(path: Path) -> dict[str, Any]:
    _require(path.exists(), f"authorization artifact missing: {path}")
    data = _load(path)

    _require(data.get("schema_version") == SCHEMA_VERSION, "schema_version mismatch")
    _require(data.get("artifact_type") == ARTIFACT_TYPE, "artifact_type mismatch")
    _require(data.get("source_of_truth_repo") == SOURCE_OF_TRUTH_REPO, "source_of_truth_repo mismatch")
    _require(data.get("reference_architecture_repo") == REFERENCE_ARCHITECTURE_REPO, "reference_architecture_repo mismatch")
    _require(bool(data.get("upstream_pattern_adapted")), "upstream_pattern_adapted missing")
    _require(data.get("ready_for_controlled_delivery") is True, "ready_for_controlled_delivery must be true")

    for label in ["delivery_prep_artifact", "package_manifest", "ready_artifact", "package_readiness_gate", "routine_run_manifest"]:
        _path(data.get(label), label)

    for key in [
        "workflow_dispatch_allowed",
        "run_queue_allowed",
        "transport_execution_allowed",
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
    ]:
        _false(data, key)

    status = str(data.get("authorization_status"))
    if status == "authorized_for_future_guarded_send":
        _require(data.get("delivery_authorized") is True, "authorized artifact must set delivery_authorized=true")
        _require(data.get("guarded_confirmation_phrase_matched") is True, "authorized artifact must match phrase")
        _require(data.get("explicit_user_authorization_present") is True, "authorized artifact must show explicit authorization")
        _require(data.get("send_command_allowed") is True, "authorized artifact may allow future send command")
        _require(data.get("next_package") == AUTHORIZED_NEXT_PACKAGE, "authorized next_package mismatch")
    elif status == "blocked_missing_guarded_confirmation_phrase":
        _require(data.get("delivery_authorized") is False, "blocked artifact must keep delivery_authorized=false")
        _require(data.get("guarded_confirmation_phrase_matched") is False, "blocked artifact must not match phrase")
        _require(data.get("explicit_user_authorization_present") is False, "blocked artifact must not show explicit authorization")
        _require(data.get("send_command_allowed") is False, "blocked artifact must keep send_command_allowed=false")
        _require(data.get("next_package") == BLOCKED_NEXT_PACKAGE, "blocked next_package mismatch")
        _require("missing_exact_guarded_confirmation_phrase" in (data.get("blockers") or []), "blocked artifact must name missing phrase blocker")
    else:
        raise AssertionError(f"unsupported authorization_status={status}")

    routine = _load(_path(data.get("routine_run_manifest"), "routine_run_manifest"))
    _require(routine.get("delivery_authorization_artifact") == str(path), "routine manifest must reference authorization artifact")
    _require(routine.get("transport_attempted") is False, "routine manifest must keep transport_attempted=false")
    _require(routine.get("transport_success") is False, "routine manifest must keep transport_success=false")
    _require(routine.get("receipt_confirmed") is False, "routine manifest must keep receipt_confirmed=false")

    return {
        "status": "valid",
        "authorization_status": status,
        "delivery_authorized": data.get("delivery_authorized"),
        "send_command_allowed": data.get("send_command_allowed"),
        "next_package": data.get("next_package"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate ETF EU guarded-send authorization artifact.")
    parser.add_argument("--authorization", required=True)
    args = parser.parse_args()
    print(json.dumps(validate(Path(args.authorization)), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
