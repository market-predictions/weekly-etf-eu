from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

try:
    from tools.validate_etf_eu_corrected_resend_package import validate_package
except ModuleNotFoundError:
    from validate_etf_eu_corrected_resend_package import validate_package

QUEUE_SCHEMA = "etf_eu_corrected_resend_queue_v1"
REQUIRED_KEYS = {
    "schema_version",
    "artifact_type",
    "correction_control_id",
    "source_run_id",
    "repair_run_id",
    "report_date",
    "report_suffix",
    "corrected_package_manifest",
    "combined_machine_gate_artifact",
    "visual_review_artifact",
    "original_transport_result",
    "original_delivery_evidence",
    "routine_run_manifest",
    "correction_label_nl",
    "correction_label_en",
    "recipient_plaintext_values_exposed",
    "secret_values_exposed",
    "raw_receipt_pdf_stored_in_github",
    "corrected_resend_prepared",
    "corrected_resend_executed",
}
FORBIDDEN = [
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    re.compile(r"SMTP_PASS", re.IGNORECASE),
    re.compile(r"MRKT_RPRTS_SMTP", re.IGNORECASE),
    re.compile(r"output/fresh_generation/weekly_etf_eu_review(?:_nl)?_260712\.pdf"),
]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _load_json(path: Path) -> dict[str, Any]:
    _require(path.exists(), f"missing referenced artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _parse(path: Path) -> tuple[dict[str, str], str]:
    _require(path.exists(), f"corrected resend queue missing: {path}")
    raw = path.read_text(encoding="utf-8")
    for pattern in FORBIDDEN:
        _require(pattern.search(raw) is None, f"queue contains forbidden pattern: {pattern.pattern}")
    data: dict[str, str] = {}
    for raw_line in raw.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    missing = REQUIRED_KEYS - set(data)
    _require(not missing, f"queue missing keys: {sorted(missing)}")
    return data, raw


def validate_queue(path: Path) -> dict[str, Any]:
    data, _raw = _parse(path)
    _require(data["schema_version"] == QUEUE_SCHEMA, "corrected resend queue schema mismatch")
    _require(data["artifact_type"] == "etf_eu_corrected_resend_queue", "corrected resend queue type mismatch")
    _require(data["correction_control_id"] == "20260713_000000", "correction_control_id mismatch")
    _require(data["source_run_id"] == "20260712_125000", "source_run_id mismatch")
    _require(data["repair_run_id"] == "20260712_200000", "repair_run_id mismatch")
    _require(data["report_date"] == "2026-07-12", "report_date mismatch")
    _require(data["report_suffix"] == "260712", "report_suffix mismatch")
    _require(data["correction_label_nl"] == "Gecorrigeerde versie", "Dutch correction label mismatch")
    _require(data["correction_label_en"] == "Corrected version", "English correction label mismatch")
    _require(data["recipient_plaintext_values_exposed"] == "false", "recipient exposure flag must be false")
    _require(data["secret_values_exposed"] == "false", "secret exposure flag must be false")
    _require(data["raw_receipt_pdf_stored_in_github"] == "false", "raw receipt flag must be false")
    _require(data["corrected_resend_prepared"] == "true", "corrected resend must be prepared")
    _require(data["corrected_resend_executed"] == "false", "corrected resend must not already be executed")

    package_path = Path(data["corrected_package_manifest"])
    package_validation = validate_package(package_path)
    package = _load_json(package_path)
    combined = _load_json(Path(data["combined_machine_gate_artifact"]))
    visual = _load_json(Path(data["visual_review_artifact"]))
    original_result = _load_json(Path(data["original_transport_result"]))
    original_evidence = _load_json(Path(data["original_delivery_evidence"]))
    routine = _load_json(Path(data["routine_run_manifest"]))

    _require(package["correction_control_id"] == data["correction_control_id"], "package/queue control id mismatch")
    _require(package["source_run_id"] == data["source_run_id"], "package/queue source run mismatch")
    _require(package["repair_run_id"] == data["repair_run_id"], "package/queue repair run mismatch")
    _require(combined.get("pdf_client_grade_passed") is True, "combined machine gate failed")
    _require(not combined.get("blockers"), "combined machine gate contains blockers")
    _require(visual.get("visual_review_passed") is True, "visual review failed")
    _require(not visual.get("blockers"), "visual review contains blockers")
    _require(original_result.get("transport_success") is True, "original transport evidence is not successful")
    _require(original_result.get("receipt_confirmed") is False, "original receipt state changed")
    _require(original_evidence.get("transport_success") is True, "original delivery evidence missing")
    _require(original_evidence.get("receipt_confirmed") is False, "original delivery receipt state changed")
    _require(routine.get("run_id") == data["source_run_id"], "routine manifest source run mismatch")

    return {
        "status": "valid",
        "queue": str(path),
        "correction_control_id": data["correction_control_id"],
        "package_validation": package_validation,
        "machine_gate_passed": True,
        "visual_gate_passed": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the Weekly ETF EU corrected-resend queue.")
    parser.add_argument("--queue", required=True)
    args = parser.parse_args()
    print(json.dumps(validate_queue(Path(args.queue)), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
