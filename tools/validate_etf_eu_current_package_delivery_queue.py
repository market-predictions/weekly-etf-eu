from __future__ import annotations

import argparse
import hashlib
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
    "accepted_package_lock",
    "authorization_artifact",
    "controlled_delivery_decision_artifact",
    "transport_selection_artifact",
    "routine_run_manifest",
    "recipient_plaintext_values_exposed",
    "secret_values_exposed",
    "raw_receipt_pdf_stored_in_github",
    "delivery_authorized",
    "send_command_allowed",
    "send_confirmation",
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


def _git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def _validate_lock(data: dict[str, str], lock: dict) -> None:
    if lock.get("schema_version") != "etf_eu_accepted_package_lock_v1":
        raise RuntimeError("accepted package lock schema mismatch")
    if lock.get("artifact_type") != "etf_eu_accepted_package_lock":
        raise RuntimeError("accepted package lock type mismatch")
    for key in ("run_id", "report_date", "report_suffix"):
        if str(lock.get(key)) != data[key]:
            raise RuntimeError(f"accepted package lock {key} mismatch")
    if lock.get("machine_validation_passed") is not True:
        raise RuntimeError("accepted package lock machine gate not passed")
    if lock.get("visual_review_passed") is not True:
        raise RuntimeError("accepted package lock visual gate not passed")
    if lock.get("ready_for_controlled_delivery") is not True:
        raise RuntimeError("accepted package lock is not delivery-ready")
    files = lock.get("files")
    if not isinstance(files, list) or len(files) != 4:
        raise RuntimeError("accepted package lock must contain exactly four client files")
    expected_roles = {
        "dutch_primary_html",
        "dutch_primary_pdf",
        "english_companion_html",
        "english_companion_pdf",
    }
    observed_roles: set[str] = set()
    for row in files:
        if not isinstance(row, dict):
            raise RuntimeError("accepted package lock file row invalid")
        role = str(row.get("role") or "")
        path = Path(str(row.get("path") or ""))
        expected_sha = str(row.get("git_blob_sha") or "")
        if role in observed_roles:
            raise RuntimeError(f"duplicate accepted package lock role: {role}")
        observed_roles.add(role)
        if not path.exists():
            raise RuntimeError(f"accepted package file missing: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise RuntimeError(f"accepted package byte lock mismatch: {role}")
    if observed_roles != expected_roles:
        raise RuntimeError("accepted package lock role set mismatch")


def validate(path: Path) -> dict[str, object]:
    data = _parse_queue(path)
    if data["schema_version"] != "etf_eu_current_package_delivery_queue_v1":
        raise RuntimeError("queue schema mismatch")
    if data["artifact_type"] != "etf_eu_current_package_delivery_queue":
        raise RuntimeError("queue artifact type mismatch")
    for key in ("delivery_authorized", "send_command_allowed"):
        if data[key] != "true":
            raise RuntimeError(f"{key} must be true")
    if data["send_confirmation"] != "confirm_guarded_send":
        raise RuntimeError("guarded send confirmation is missing")
    for key in ("recipient_plaintext_values_exposed", "secret_values_exposed", "raw_receipt_pdf_stored_in_github"):
        if data[key] != "false":
            raise RuntimeError(f"{key} must be false")
    if "20260709" in path.read_text(encoding="utf-8") or "MVP19" in path.read_text(encoding="utf-8"):
        raise RuntimeError("queue artifact must not reference legacy MVP19/FIX2 package chain")

    package = _read_json(data["package_manifest"])
    lock = _read_json(data["accepted_package_lock"])
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
    if authorization.get("send_confirmation_received") is not True:
        raise RuntimeError("authorization does not record explicit send confirmation")
    if decision.get("controlled_delivery_decision_status") != "routine_guarded_delivery_selected":
        raise RuntimeError("unexpected controlled delivery decision status")
    if selection.get("transport_selection_status") != "current_package_smtp_runner_selected":
        raise RuntimeError("unexpected transport selection status")
    for payload in (package, authorization, decision, selection, routine):
        for key in ("valuation_grade", "funding_authority", "portfolio_mutation", "production_delivery_authority"):
            if payload.get(key) is not False:
                raise RuntimeError(f"{key} must remain false")

    _validate_lock(data, lock)
    return {
        "status": "valid",
        "queue": str(path),
        "run_id": run_id,
        "accepted_package_lock": data["accepted_package_lock"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate ETF EU current-package delivery queue artifact.")
    parser.add_argument("--queue", required=True)
    args = parser.parse_args()
    print(json.dumps(validate(Path(args.queue)), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
