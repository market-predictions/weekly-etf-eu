from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "yahoo_fallback_gate_evaluation_v1"
FORBIDDEN_TRUE_FIELDS = ["valuation_authority", "funding_authority", "portfolio_mutation", "production_delivery"]
REQUIRED_BLOCKED_GATES = ["fallback_policy_enabled", "completed_session_validated", "cross_source_check_passed"]


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
            failed = row.get("failed_gates") if isinstance(row.get("failed_gates"), list) else []
            if row.get("eligible_for_fallback_review") is not False:
                errors.append(f"row_{idx}_must_not_be_eligible_yet")
            if row.get("status") != "blocked":
                errors.append(f"row_{idx}_status_must_be_blocked")
            for gate in REQUIRED_BLOCKED_GATES:
                if gates.get(gate) is not False:
                    errors.append(f"row_{idx}_{gate}_must_be_false")
                if gate not in failed:
                    errors.append(f"row_{idx}_{gate}_must_be_failed")
            if gates.get("registry_symbol_present") is not True:
                errors.append(f"row_{idx}_registry_symbol_present_must_be_true")
            if gates.get("currency_matches_registry") is not True:
                errors.append(f"row_{idx}_currency_matches_registry_must_be_true")
            if gates.get("fresh_close_present") is not True:
                errors.append(f"row_{idx}_fresh_close_present_must_be_true")
            if gates.get("lineage_recorded") is not True:
                errors.append(f"row_{idx}_lineage_recorded_must_be_true")
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    if summary.get("eligible_for_fallback_review_count") not in (0, None):
        errors.append("eligible_for_fallback_review_count_must_be_zero")
    if errors:
        raise RuntimeError("YAHOO_FALLBACK_GATE_EVALUATION_VALIDATION_FAILED: " + "; ".join(sorted(set(errors))))
    print(f"YAHOO_FALLBACK_GATE_EVALUATION_VALIDATION_OK | artifact={path} | rows={len(rows or [])}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    args = parser.parse_args()
    validate(Path(args.artifact))


if __name__ == "__main__":
    main()
