from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "ishares_endpoint_structure_probe_v1"
FORBIDDEN_TRUE_FIELDS = ["valuation_authority", "funding_authority", "portfolio_mutation", "production_delivery", "reference_price_extraction"]
REQUIRED_TARGETS = {"cwpScreenerApi", "productScreenerV3Api"}
REQUIRED_SIGNAL_KEYS = [
    "has_embedded_json_like_blocks",
    "has_table_like_structure",
    "has_data_attributes",
    "has_nav_or_price_label_signal",
    "has_date_or_currency_label_signal",
    "has_identity_label_signal",
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
    if not isinstance(rows, list) or len(rows) != 2:
        errors.append("rows_must_have_two_target_endpoints")
    for obj in walk_objects(payload):
        for field in FORBIDDEN_TRUE_FIELDS:
            if field in obj and obj.get(field) is not False:
                errors.append(f"{field}_must_be_false")
        if "body_sample" in obj:
            errors.append("body_sample_must_not_be_present")
    tokens = {str(row.get("allowlist_token")) for row in rows or [] if isinstance(row, dict)}
    if tokens != REQUIRED_TARGETS:
        errors.append("target_tokens_must_be_cwp_and_product_screener")
    if isinstance(rows, list):
        for idx, row in enumerate(rows):
            if not isinstance(row, dict):
                errors.append(f"row_{idx}_must_be_object")
                continue
            if row.get("http_status") != 200:
                errors.append(f"row_{idx}_http_status_must_be_200")
            if not row.get("url"):
                errors.append(f"row_{idx}_url_required")
            if int(row.get("bytes_sampled") or 0) <= 0:
                errors.append(f"row_{idx}_bytes_sampled_positive_required")
            signals = row.get("signals") if isinstance(row.get("signals"), dict) else {}
            for key in REQUIRED_SIGNAL_KEYS:
                if key not in signals:
                    errors.append(f"row_{idx}_{key}_missing")
            counts = row.get("structure_counts") if isinstance(row.get("structure_counts"), dict) else {}
            for key in ["script_tag_count", "table_tag_count", "brace_pairs_approx", "data_attribute_count"]:
                if key not in counts:
                    errors.append(f"row_{idx}_{key}_count_missing")
            answers = row.get("answers") if isinstance(row.get("answers"), dict) else {}
            for key in ["worth_controlled_parser_followup", "issuer_reference_structure_observed"]:
                if key not in answers:
                    errors.append(f"row_{idx}_{key}_answer_missing")
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    if int(summary.get("row_count") or 0) != len(rows or []):
        errors.append("summary_row_count_mismatch")
    if errors:
        raise RuntimeError("ISHARES_ENDPOINT_STRUCTURE_PROBE_VALIDATION_FAILED: " + "; ".join(sorted(set(errors))))
    print(f"ISHARES_ENDPOINT_STRUCTURE_PROBE_VALIDATION_OK | artifact={path} | rows={len(rows or [])}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    args = parser.parse_args()
    validate(Path(args.artifact))


if __name__ == "__main__":
    main()
