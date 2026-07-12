from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REQUIRED = {
    "schema_version",
    "artifact_type",
    "run_id",
    "report_date",
    "report_suffix",
    "package_manifest",
    "authorization_artifact",
    "controlled_delivery_decision_artifact",
    "transport_selection_artifact",
    "routine_run_manifest",
    "delivery_authorized",
    "send_command_allowed",
    "recipient_plaintext_values_exposed",
    "secret_values_exposed",
    "raw_receipt_pdf_stored_in_github",
}
FORBIDDEN = [
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    re.compile(r"SMTP_PASS", re.IGNORECASE),
    re.compile(r"MRKT_RPRTS_SMTP", re.IGNORECASE),
]


def _load(path: Path) -> dict:
    if not path.exists():
        raise AssertionError(f"referenced artifact missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _parse(path: Path) -> dict[str, str]:
    if not path.exists():
        raise AssertionError(f"queue missing: {path}")
    raw = path.read_text(encoding="utf-8")
    for pattern in FORBIDDEN:
        if pattern.search(raw):
            raise AssertionError(f"queue contains forbidden pattern: {pattern.pattern}")
    data: dict[str, str] = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    missing = REQUIRED - set(data)
    if missing:
        raise AssertionError(f"queue missing keys: {sorted(missing)}")
    return data


def validate(path: Path) -> dict[str, object]:
    data = _parse(path)
    if data["schema_version"] != "etf_eu_current_package_delivery_queue_v1":
        raise AssertionError("queue schema mismatch")
    if data["artifact_type"] != "etf_eu_current_package_delivery_queue":
        raise AssertionError("queue type mismatch")
    for key in ["delivery_authorized", "send_command_allowed"]:
        if data[key] != "true":
            raise AssertionError(f"{key} must be true")
    for key in ["recipient_plaintext_values_exposed", "secret_values_exposed", "raw_receipt_pdf_stored_in_github"]:
        if data[key] != "false":
            raise AssertionError(f"{key} must be false")

    package = _load(Path(data["package_manifest"]))
    authorization = _load(Path(data["authorization_artifact"]))
    decision = _load(Path(data["controlled_delivery_decision_artifact"]))
    selection = _load(Path(data["transport_selection_artifact"]))
    routine = _load(Path(data["routine_run_manifest"]))
    run_id = data["run_id"]
    for label, payload in [("package", package), ("authorization", authorization), ("decision", decision), ("selection", selection), ("routine", routine)]:
        if str(payload.get("run_id")) != run_id:
            raise AssertionError(f"{label} run id mismatch")
    if package.get("schema_version") != "etf_eu_fresh_generation_package_v1":
        raise AssertionError("fresh package schema mismatch")
    if package.get("ready_for_controlled_delivery") is not True:
        raise AssertionError("package is not ready")
    if authorization.get("delivery_authorized") is not True or authorization.get("send_command_allowed") is not True:
        raise AssertionError("authorization flags are not true")
    if decision.get("controlled_delivery_decision_status") != "routine_guarded_delivery_selected":
        raise AssertionError("routine delivery decision mismatch")
    if selection.get("transport_selection_status") != "current_package_smtp_runner_selected":
        raise AssertionError("routine transport selection mismatch")
    for payload in [package, authorization, decision, selection, routine]:
        for key in ["valuation_grade", "funding_authority", "portfolio_mutation", "production_delivery_authority"]:
            if payload.get(key) is not False:
                raise AssertionError(f"{key} must remain false")
    return {"status": "valid", "queue": str(path), "run_id": run_id}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", required=True)
    args = parser.parse_args()
    print(json.dumps(validate(Path(args.queue)), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
