from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "euronext_dynamic_quote_response_discovery_v1"
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
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows:
        errors.append("rows_must_be_non_empty_list")
    for obj in _walk_objects(payload):
        for field in FORBIDDEN_TRUE_FIELDS:
            if field in obj and obj.get(field) is not False:
                errors.append(f"{field}_must_be_false")
        if "candidate_close" in obj and obj.get("candidate_close") is not None:
            errors.append("candidate_close_must_not_have_value")
        if obj.get("valuation_grade") is True:
            errors.append("valuation_grade_must_not_be_true")
    if isinstance(rows, list):
        for idx, row in enumerate(rows):
            if not isinstance(row, dict):
                errors.append(f"row_{idx}_must_be_object")
                continue
            product_fetch = row.get("product_page_fetch") if isinstance(row.get("product_page_fetch"), dict) else {}
            dynamic = row.get("dynamic_quotes_display") if isinstance(row.get("dynamic_quotes_display"), dict) else {}
            answers = row.get("answers") if isinstance(row.get("answers"), dict) else {}
            sampled = row.get("sampled_response_evidence") if isinstance(row.get("sampled_response_evidence"), dict) else {}
            if product_fetch.get("http_status") != 200:
                errors.append(f"row_{idx}_product_page_fetch_must_be_200")
            if dynamic.get("present") is not True:
                errors.append(f"row_{idx}_dynamic_quotes_display_missing")
            if "which_endpoint_or_response_is_triggered" not in answers:
                errors.append(f"row_{idx}_answers_missing_endpoint_field")
            if sampled.get("body_sample") and len(str(sampled.get("body_sample"))) > 1200:
                errors.append(f"row_{idx}_sampled_body_too_long")
            if sampled.get("candidate_close_extraction") is not False and "candidate_close_extraction" in sampled:
                errors.append(f"row_{idx}_sampled_candidate_close_extraction_must_be_false")
            if sampled.get("completed_session_validation") is not False and "completed_session_validation" in sampled:
                errors.append(f"row_{idx}_sampled_completed_session_validation_must_be_false")
    if errors:
        raise RuntimeError("EURONEXT_DYNAMIC_QUOTE_RESPONSE_DISCOVERY_VALIDATION_FAILED: " + "; ".join(sorted(set(errors))))
    print(f"EURONEXT_DYNAMIC_QUOTE_RESPONSE_DISCOVERY_VALIDATION_OK | artifact={path} | rows={len(rows or [])}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    args = parser.parse_args()
    validate(Path(args.artifact))


if __name__ == "__main__":
    main()
