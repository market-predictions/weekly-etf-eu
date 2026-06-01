from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "ishares_reference_endpoint_discovery_v1"
FORBIDDEN_TRUE_FIELDS = ["valuation_authority", "funding_authority", "portfolio_mutation", "production_delivery", "reference_price_extraction"]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def walk_objects(value: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, dict):
        found.append(value)
        for child in value.values():
            found.extend(walk_objects(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(walk_objects(child))
    return found


def validate(path: Path) -> None:
    payload = load_json(path)
    errors: list[str] = []
    if payload.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version_mismatch")
    if payload.get("diagnostic_only") is not True:
        errors.append("diagnostic_only_must_be_true")
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows:
        errors.append("rows_must_be_non_empty_list")
    for obj in walk_objects(payload):
        for field in FORBIDDEN_TRUE_FIELDS:
            if field in obj and obj.get(field) is not False:
                errors.append(f"{field}_must_be_false")
    if isinstance(rows, list):
        for idx, row in enumerate(rows):
            page_fetch = row.get("page_fetch") if isinstance(row.get("page_fetch"), dict) else {}
            if page_fetch.get("http_status") != 200:
                errors.append(f"row_{idx}_page_fetch_must_be_200")
            if not isinstance(row.get("endpoint_candidates"), list):
                errors.append(f"row_{idx}_endpoint_candidates_must_be_list")
            if len(row.get("endpoint_candidates") or []) > 80:
                errors.append(f"row_{idx}_too_many_endpoint_candidates")
            if len(row.get("context_samples") or []) > 20:
                errors.append(f"row_{idx}_too_many_context_samples")
            answers = row.get("answers") if isinstance(row.get("answers"), dict) else {}
            for key in ["stable_endpoint_found", "factsheet_or_document_candidate_found", "nav_or_price_related_candidate_found"]:
                if key not in answers:
                    errors.append(f"row_{idx}_{key}_missing")
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    if int(summary.get("row_count") or 0) < 1:
        errors.append("summary_row_count_required")
    if errors:
        raise RuntimeError("ISHARES_REFERENCE_ENDPOINT_DISCOVERY_VALIDATION_FAILED: " + "; ".join(sorted(set(errors))))
    print(f"ISHARES_REFERENCE_ENDPOINT_DISCOVERY_VALIDATION_OK | artifact={path} | rows={len(rows or [])}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    args = parser.parse_args()
    validate(Path(args.artifact))


if __name__ == "__main__":
    main()
