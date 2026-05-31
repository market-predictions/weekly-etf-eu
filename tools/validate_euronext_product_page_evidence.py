from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "euronext_product_page_evidence_v1"
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
        if obj.get("candidate_close") is not None and "candidate_close" in obj:
            errors.append("candidate_close_must_not_have_value")
        if obj.get("valuation_grade") is True:
            errors.append("valuation_grade_must_not_be_true")
    if isinstance(rows, list):
        for idx, row in enumerate(rows):
            if not isinstance(row, dict):
                errors.append(f"row_{idx}_must_be_object")
                continue
            custom = row.get("custom_instrument_evidence") if isinstance(row.get("custom_instrument_evidence"), dict) else {}
            dynamic = row.get("dynamic_quotes_display_evidence") if isinstance(row.get("dynamic_quotes_display_evidence"), dict) else {}
            if custom.get("present") is not True:
                errors.append(f"row_{idx}_custom_instrument_missing")
            if dynamic.get("present") is not True:
                errors.append(f"row_{idx}_dynamic_quotes_display_missing")
            if custom.get("identity_usable_for_endpoint_design") is not True:
                errors.append(f"row_{idx}_identity_not_usable_for_endpoint_design")
            if dynamic.get("quote_response_fetch") is not False:
                errors.append(f"row_{idx}_quote_response_fetch_must_be_false")
            decision = row.get("decision") if isinstance(row.get("decision"), dict) else {}
            if decision.get("search_endpoint_path_disposition") != "stopped_after_loopback_evidence":
                errors.append(f"row_{idx}_search_endpoint_path_disposition_invalid")
    if errors:
        raise RuntimeError("EURONEXT_PRODUCT_PAGE_EVIDENCE_VALIDATION_FAILED: " + "; ".join(sorted(set(errors))))
    print(f"EURONEXT_PRODUCT_PAGE_EVIDENCE_VALIDATION_OK | artifact={path} | rows={len(rows or [])}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    args = parser.parse_args()
    validate(Path(args.artifact))


if __name__ == "__main__":
    main()
