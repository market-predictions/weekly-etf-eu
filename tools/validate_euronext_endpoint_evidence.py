from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "euronext_endpoint_evidence_v1"
FORBIDDEN_TRUE_FIELDS = [
    "authority",
    "candidate_close_extraction",
    "completed_session_validation",
    "valuation_authority",
    "funding_authority",
    "portfolio_mutation",
    "production_delivery",
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _walk_objects(value: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, dict):
        found.append(value)
        for child in value.values():
            found.extend(_walk_objects(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(_walk_objects(child))
    return found


def validate(path: Path) -> None:
    payload = _load_json(path)
    errors: list[str] = []
    if payload.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version_mismatch")
    if payload.get("diagnostic_only") is not True:
        errors.append("diagnostic_only_must_be_true")
    if payload.get("target_candidate_name") != "settings_search_product_data":
        errors.append("target_candidate_name_must_be_settings_search_product_data")
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows:
        errors.append("rows_must_be_non_empty_list")
    for obj in _walk_objects(payload):
        for field in FORBIDDEN_TRUE_FIELDS:
            if obj.get(field) is not False and field in obj:
                errors.append(f"{field}_must_be_false")
        if obj.get("candidate_close") is not None and "candidate_close" in obj:
            errors.append("candidate_close_must_not_be_present_as_value")
        if obj.get("valuation_grade") is True:
            errors.append("valuation_grade_must_not_be_true")
    if isinstance(rows, list):
        for idx, row in enumerate(rows):
            if not isinstance(row, dict):
                errors.append(f"row_{idx}_must_be_object")
                continue
            if row.get("target_candidate_name") != "settings_search_product_data":
                errors.append(f"row_{idx}_target_candidate_name_invalid")
            if not row.get("target_url") and row.get("evidence_status") != "target_candidate_missing":
                errors.append(f"row_{idx}_target_url_required")
            if row.get("fetch", {}).get("body_sample") and len(row.get("fetch", {}).get("body_sample")) > 1200:
                errors.append(f"row_{idx}_body_sample_too_long")
    if errors:
        raise RuntimeError("EURONEXT_ENDPOINT_EVIDENCE_VALIDATION_FAILED: " + "; ".join(sorted(set(errors))))
    print(f"EURONEXT_ENDPOINT_EVIDENCE_VALIDATION_OK | artifact={path} | rows={len(rows or [])}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    args = parser.parse_args()
    validate(Path(args.artifact))


if __name__ == "__main__":
    main()
