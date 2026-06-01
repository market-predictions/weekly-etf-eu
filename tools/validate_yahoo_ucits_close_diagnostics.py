from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "yahoo_ucits_close_diagnostics_v1"
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
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    if summary.get("unambiguous_mapping_count") not in (0, None):
        errors.append("unambiguous_mapping_count_must_remain_zero_in_diagnostic_phase")
    for obj in _walk_objects(payload):
        for field in FORBIDDEN_TRUE_FIELDS:
            if field in obj and obj.get(field) is not False:
                errors.append(f"{field}_must_be_false")
        if "valuation_grade" in obj and obj.get("valuation_grade") is True:
            errors.append("valuation_grade_must_not_be_true")
    if isinstance(rows, list):
        for idx, row in enumerate(rows):
            if not isinstance(row, dict):
                errors.append(f"row_{idx}_must_be_object")
                continue
            if row.get("source_id") != "yahoo_yfinance":
                errors.append(f"row_{idx}_source_id_must_be_yahoo_yfinance")
            if not row.get("yahoo_symbol"):
                errors.append(f"row_{idx}_yahoo_symbol_required")
            mapping = row.get("mapping_diagnostics") if isinstance(row.get("mapping_diagnostics"), dict) else {}
            if mapping.get("line_mapping_unambiguous") is not False:
                errors.append(f"row_{idx}_line_mapping_unambiguous_must_be_false")
            flags = mapping.get("ambiguity_flags") if isinstance(mapping.get("ambiguity_flags"), list) else []
            if "isin_not_verified_by_yahoo_diagnostic" not in flags:
                errors.append(f"row_{idx}_must_record_isin_not_verified")
            observed = row.get("observed") if isinstance(row.get("observed"), dict) else {}
            close = observed.get("observed_last_close")
            if close is not None:
                try:
                    if float(close) <= 0:
                        errors.append(f"row_{idx}_close_must_be_positive_if_present")
                except Exception:
                    errors.append(f"row_{idx}_close_must_be_numeric_if_present")
            if row.get("source_policy_authority") != "non_authoritative_connectivity_only":
                errors.append(f"row_{idx}_source_policy_authority_must_remain_connectivity_only")
    if errors:
        raise RuntimeError("YAHOO_UCITS_CLOSE_DIAGNOSTICS_VALIDATION_FAILED: " + "; ".join(sorted(set(errors))))
    print(f"YAHOO_UCITS_CLOSE_DIAGNOSTICS_VALIDATION_OK | artifact={path} | rows={len(rows or [])}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    args = parser.parse_args()
    validate(Path(args.artifact))


if __name__ == "__main__":
    main()
