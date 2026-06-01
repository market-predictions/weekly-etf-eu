from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "issuer_reference_sanity_gate_v1"
FORBIDDEN_TRUE_FIELDS = ["valuation_authority", "funding_authority", "portfolio_mutation", "production_delivery"]
REQUIRED_GATE_FIELDS = [
    "issuer_policy_present",
    "issuer_page_fetch_ok",
    "issuer_identity_match",
    "reference_price_found",
    "broad_tolerance_check_passed",
    "cross_source_gate_already_passed",
]


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
            if row.get("issuer_reference_sanity_passed") is not False:
                errors.append(f"row_{idx}_issuer_reference_must_remain_blocked_currently")
            if row.get("diagnostic_status") != "issuer_reference_blocked":
                errors.append(f"row_{idx}_diagnostic_status_must_be_blocked")
            for gate in REQUIRED_GATE_FIELDS:
                if gate not in gates:
                    errors.append(f"row_{idx}_{gate}_missing")
            if gates.get("issuer_policy_present") is not True:
                errors.append(f"row_{idx}_issuer_policy_present_required")
            if gates.get("reference_price_found") is not False:
                errors.append(f"row_{idx}_reference_price_found_must_be_false_in_current_gate")
            if gates.get("broad_tolerance_check_passed") is not False:
                errors.append(f"row_{idx}_broad_tolerance_must_be_false_without_reference_price")
            if "reference_price_found" not in failed:
                errors.append(f"row_{idx}_reference_price_failed_gate_required")
            fetch = row.get("issuer_fetch") if isinstance(row.get("issuer_fetch"), dict) else {}
            sample = str(fetch.get("body_sample") or "")
            if len(sample) > 1200:
                errors.append(f"row_{idx}_body_sample_too_long")
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    if summary.get("issuer_reference_sanity_passed_count") not in (0, None):
        errors.append("issuer_reference_sanity_passed_count_must_be_zero_currently")
    if errors:
        raise RuntimeError("ISSUER_REFERENCE_SANITY_GATE_VALIDATION_FAILED: " + "; ".join(sorted(set(errors))))
    print(f"ISSUER_REFERENCE_SANITY_GATE_VALIDATION_OK | artifact={path} | rows={len(rows or [])}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    args = parser.parse_args()
    validate(Path(args.artifact))


if __name__ == "__main__":
    main()
