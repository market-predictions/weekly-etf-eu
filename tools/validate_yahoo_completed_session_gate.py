from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "yahoo_completed_session_gate_v1"
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
            for gate in [
                "venue_policy_present",
                "observed_close_date_present",
                "regular_session_date",
                "session_close_time_elapsed",
                "staleness_within_limit",
            ]:
                if gate not in gates:
                    errors.append(f"row_{idx}_{gate}_missing")
            if row.get("completed_session_validated") is not True:
                errors.append(f"row_{idx}_completed_session_should_validate_for_current_test_case")
            if row.get("diagnostic_status") != "completed_session_validated":
                errors.append(f"row_{idx}_diagnostic_status_invalid")
            if not row.get("venue_mic"):
                errors.append(f"row_{idx}_venue_mic_required")
            if not row.get("session_close_ready_utc"):
                errors.append(f"row_{idx}_session_close_ready_utc_required")
            staleness = row.get("staleness_days")
            if not isinstance(staleness, int) or staleness < 0:
                errors.append(f"row_{idx}_staleness_days_invalid")
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    if summary.get("row_count") != summary.get("completed_session_validated_count"):
        errors.append("all_rows_should_validate_completed_session_for_current_test_case")
    if errors:
        raise RuntimeError("YAHOO_COMPLETED_SESSION_GATE_VALIDATION_FAILED: " + "; ".join(sorted(set(errors))))
    print(f"YAHOO_COMPLETED_SESSION_GATE_VALIDATION_OK | artifact={path} | rows={len(rows or [])}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    args = parser.parse_args()
    validate(Path(args.artifact))


if __name__ == "__main__":
    main()
