from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "yahoo_cross_source_gate_v1"
FORBIDDEN_TRUE_FIELDS = ["valuation_authority", "funding_authority", "portfolio_mutation", "production_delivery"]


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
            gates = row.get("gates") if isinstance(row.get("gates"), dict) else {}
            if row.get("cross_source_check_passed") is not False:
                errors.append(f"row_{idx}_cross_source_must_remain_blocked_currently")
            if row.get("diagnostic_status") != "cross_source_blocked":
                errors.append(f"row_{idx}_diagnostic_status_must_be_blocked")
            if gates.get("yahoo_close_present") is not True:
                errors.append(f"row_{idx}_yahoo_close_present_required")
            if gates.get("completed_session_validated") is not True:
                errors.append(f"row_{idx}_completed_session_validated_required")
            if gates.get("independent_source_close_present") is not False:
                errors.append(f"row_{idx}_independent_close_must_be_absent_currently")
            failed = row.get("failed_gates") if isinstance(row.get("failed_gates"), list) else []
            if "independent_source_close_present" not in failed:
                errors.append(f"row_{idx}_independent_close_failed_gate_required")
            if row.get("pct_difference") is not None:
                errors.append(f"row_{idx}_pct_difference_must_be_null_without_independent_close")
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    if summary.get("cross_source_passed_count") not in (0, None):
        errors.append("cross_source_passed_count_must_be_zero_currently")
    if errors:
        raise RuntimeError("YAHOO_CROSS_SOURCE_GATE_VALIDATION_FAILED: " + "; ".join(sorted(set(errors))))
    print(f"YAHOO_CROSS_SOURCE_GATE_VALIDATION_OK | artifact={path} | rows={len(rows or [])}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    args = parser.parse_args()
    validate(Path(args.artifact))


if __name__ == "__main__":
    main()
