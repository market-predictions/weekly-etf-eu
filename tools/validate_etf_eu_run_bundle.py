from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_run_bundle_manifest_v1"
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "run_id",
    "created_at_utc",
    "report_date",
    "dutch_report_path",
    "english_report_path",
    "valuation_artifact_path",
    "fundability_artifact_path",
    "validation_evidence_path",
    "delivery_manifest_status",
    "delivery_manifest_path_or_null",
    "production_delivery",
    "email_delivery",
    "pdf_generation",
    "delivery_receipt",
}
REQUIRED_NON_EMPTY_STRINGS = {
    "run_id",
    "created_at_utc",
    "report_date",
    "dutch_report_path",
    "english_report_path",
    "valuation_artifact_path",
    "fundability_artifact_path",
    "validation_evidence_path",
}
REQUIRED_FALSE_FLAGS = {
    "production_delivery",
    "email_delivery",
    "pdf_generation",
    "delivery_receipt",
}
ALLOWED_DELIVERY_MANIFEST_STATUS = {"available", "not_available"}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _missing(required: set[str], payload: dict[str, Any]) -> list[str]:
    return sorted(required - set(payload))


def validate_manifest(path: Path) -> None:
    payload = _load(path)
    missing_top = _missing(REQUIRED_TOP_LEVEL, payload)
    if missing_top:
        raise RuntimeError(f"run bundle manifest failed: missing top-level key(s): {', '.join(missing_top)}")

    if payload["schema_version"] != SCHEMA_VERSION:
        raise RuntimeError(f"run bundle manifest failed: unsupported schema_version={payload['schema_version']}")

    for key in REQUIRED_NON_EMPTY_STRINGS:
        value = payload[key]
        if not isinstance(value, str) or not value.strip():
            raise RuntimeError(f"run bundle manifest failed: {key} must be a non-empty string")

    status = payload["delivery_manifest_status"]
    if status not in ALLOWED_DELIVERY_MANIFEST_STATUS:
        raise RuntimeError(f"run bundle manifest failed: unsupported delivery_manifest_status={status}")

    delivery_manifest_path = payload["delivery_manifest_path_or_null"]
    if status == "not_available" and delivery_manifest_path is not None:
        raise RuntimeError("run bundle manifest failed: not_available requires delivery_manifest_path_or_null=null")
    if status == "available":
        if not isinstance(delivery_manifest_path, str) or not delivery_manifest_path.strip():
            raise RuntimeError("run bundle manifest failed: available requires a non-empty delivery_manifest_path_or_null")

    for key in REQUIRED_FALSE_FLAGS:
        if payload[key] is not False:
            raise RuntimeError(f"run bundle manifest failed: {key} must remain false")

    print(
        "ETF_EU_RUN_BUNDLE_MANIFEST_OK | "
        f"manifest={path} | delivery_manifest_status={status} | "
        "production_delivery=false | email_delivery=false | pdf_generation=false | delivery_receipt=false"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest")
    args = parser.parse_args()
    validate_manifest(Path(args.manifest))


if __name__ == "__main__":
    main()
