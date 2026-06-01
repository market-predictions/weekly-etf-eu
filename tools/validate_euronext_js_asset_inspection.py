from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "euronext_js_asset_inspection_v1"
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
            if int(row.get("inspected_asset_count") or 0) < 1:
                errors.append(f"row_{idx}_must_inspect_at_least_one_asset")
            answers = row.get("answers") if isinstance(row.get("answers"), dict) else {}
            if answers.get("route_sampled") is not False:
                errors.append(f"row_{idx}_route_sampled_must_be_false")
            for asset_idx, asset in enumerate(row.get("assets") or []):
                if not isinstance(asset, dict):
                    errors.append(f"row_{idx}_asset_{asset_idx}_must_be_object")
                    continue
                if asset.get("body_sample"):
                    errors.append(f"row_{idx}_asset_{asset_idx}_must_not_include_body_sample")
                if len(asset.get("context_samples") or []) > 20:
                    errors.append(f"row_{idx}_asset_{asset_idx}_too_many_context_samples")
                if len(asset.get("route_candidates") or []) > 40:
                    errors.append(f"row_{idx}_asset_{asset_idx}_too_many_route_candidates")
    if errors:
        raise RuntimeError("EURONEXT_JS_ASSET_INSPECTION_VALIDATION_FAILED: " + "; ".join(sorted(set(errors))))
    print(f"EURONEXT_JS_ASSET_INSPECTION_VALIDATION_OK | artifact={path} | rows={len(rows or [])}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    args = parser.parse_args()
    validate(Path(args.artifact))


if __name__ == "__main__":
    main()
