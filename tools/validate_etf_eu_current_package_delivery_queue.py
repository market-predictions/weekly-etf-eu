from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REQUIRED_KEYS = {
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
    "recipient_plaintext_values_exposed",
    "secret_values_exposed",
    "raw_receipt_pdf_stored_in_github",
    "delivery_authorized",
    "send_command_allowed",
}

FORBIDDEN_PATTERNS = [
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    re.compile(r"MRKT_RPRTS_SMTP", re.IGNORECASE),
    re.compile(r"SMTP_PASS", re.IGNORECASE),
    re.compile(r"Gmail message", re.IGNORECASE),
]


def _parse_queue(path: Path) -> dict[str, str]:
    if not path.exists():
        raise RuntimeError(f"queue artifact missing: {path}")
    data: dict[str, str] = {}
    raw = path.read_text(encoding="utf-8")
    for pattern in FORBIDDEN_PATTERNS:
        if pattern.search(raw):
            raise RuntimeError(f"queue artifact contains forbidden pattern: {pattern.pattern}")
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    missing = REQUIRED_KEYS - set(data)
    if missing:
        raise RuntimeError(f"queue artifact missing keys: {sorted(missing)}")
    return data


def _read_json(path_value: str) -> dict:
    path = Path(path_value)
    if not path.exists():
        raise RuntimeError(f"referenced artifact missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate(path: Path) -> dict[str, object]:
    data = _parse_queue(path)
    if data["schema_version"] != "etf_eu_current_package_delivery_queue_v1":
        raise RuntimeError("queue schema mismatch")
    if data["artifact_type"] != "etf_eu_current_package_delivery_queue":
        raise RuntimeError("queue artifact type mismatch")
    for key in ("delivery_authorized", "send_command_allowed"):
        if data[key] != "true":
            raise RuntimeError(f"{key} must be true")
    for key in ("recipient_plaintext_values_exposed", "secret_values_exposed", "raw_receipt_pdf_stored_in_github"):
        if data[key] != "false":
            raise RuntimeError(f"{key} must be false")
    if "20260709" in path.read_text(encoding="utf-8") or "MVP19" in path.read_text(encoding="utf-8"):
        raise RuntimeError("queue artifact must not reference legacy MVP19/FIX2 package chain")

    package = _read_json(data["package_manifest"])
    authorization = _read_json(data["authorization_artifact"])
    decision = _read_json(data["controlled_delivery_decision_artifact"])
    selection = _read_json(data["transport_selection_artifact"])
    routine = _read_json(data["routine_run_manifest"])

    run_id = data["run_id"]
    for label, payload in (
        ("package", package),
        ("authorization", authorization),
        ("decision", decision),
        ("selection", selection),
        ("routine", routine),
    ):
        if str(payload.get("run_id")) != run_id:
            raise RuntimeError(f"{label} run id mismatch")

    if package.get("schema_version") != "etf_eu_fresh_generation_package_v1":
        raise RuntimeError("fresh package schema mismatch")
    if package.get("ready_for_controlled_delivery") is not True:
        raise RuntimeError("fresh package is not ready")
    if authorization.get("delivery_authorized") is not True or authorization.get("send_command_allowed") is not True:
        raise RuntimeError("guarded delivery authorization is incomplete")
    if decision.get("controlled_delivery_decision_status") != "routine_guarded_delivery_selected":
        raise RuntimeError("unexpected controlled delivery decision status")
    if selection.get("transport_selection_status") != "current_package_smtp_runner_selected":
        raise RuntimeError("unexpected transport selection status")
    for payload in (package, authorization, decision, selection, routine):
        for key in ("valuation_grade", "funding_authority", "portfolio_mutation", "production_delivery_authority"):
            if payload.get(key) is not False:
                raise RuntimeError(f"{key} must remain false")

    return {"status": "valid", "queue": str(path), "run_id": run_id}


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate ETF EU current-package delivery queue artifact.")
    parser.add_argument("--queue", required=True)
    args = parser.parse_args()
    print(json.dumps(validate(Path(args.queue)), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
