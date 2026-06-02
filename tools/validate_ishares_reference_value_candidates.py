from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "ishares_reference_value_candidates_v1"
REQUIRED_TARGETS = {"cwpScreenerApi", "productScreenerV3Api"}
FORBIDDEN_TRUE_FIELDS = ["valuation_authority", "funding_authority", "portfolio_mutation", "production_delivery", "value_extraction"]
FORBIDDEN_KEYS = {"body_sample", "raw_html", "extracted_nav", "extracted_price", "extracted_date", "extracted_currency", "reference_price"}
REQUIRED_CANDIDATE_KEYS = {
    "candidate_term",
    "candidate_kind",
    "context_sha256",
    "nearby_tag_sample",
    "nearby_attribute_name_sample",
    "confidence",
    "raw_value_extracted",
    "candidate_value",
}


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
    if payload.get("reference_price_extraction") != "diagnostic_candidate_only_no_values":
        errors.append("reference_price_extraction_must_be_candidate_only_no_values")
    rows = payload.get("rows")
    if not isinstance(rows, list) or len(rows) != 2:
        errors.append("rows_must_have_two_target_endpoints")
    for obj in walk_objects(payload):
        for field in FORBIDDEN_TRUE_FIELDS:
            if field in obj and obj.get(field) is not False:
                errors.append(f"{field}_must_be_false")
        for key in FORBIDDEN_KEYS:
            if key in obj:
                errors.append(f"{key}_must_not_be_present")
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
            if not row.get("text_sha256") or len(str(row.get("text_sha256"))) != 64:
                errors.append(f"row_{idx}_text_sha256_required")
            candidates = row.get("candidates") if isinstance(row.get("candidates"), list) else []
            if not candidates:
                errors.append(f"row_{idx}_candidates_required")
            if len(candidates) > 42:
                errors.append(f"row_{idx}_candidate_limit_exceeded")
            for cidx, candidate in enumerate(candidates):
                if not isinstance(candidate, dict):
                    errors.append(f"row_{idx}_candidate_{cidx}_must_be_object")
                    continue
                missing = REQUIRED_CANDIDATE_KEYS - set(candidate.keys())
                if missing:
                    errors.append(f"row_{idx}_candidate_{cidx}_missing_keys:{','.join(sorted(missing))}")
                if candidate.get("raw_value_extracted") is not False:
                    errors.append(f"row_{idx}_candidate_{cidx}_raw_value_extracted_must_be_false")
                if candidate.get("candidate_value") is not None:
                    errors.append(f"row_{idx}_candidate_{cidx}_candidate_value_must_be_null")
                if not candidate.get("context_sha256") or len(str(candidate.get("context_sha256"))) != 64:
                    errors.append(f"row_{idx}_candidate_{cidx}_context_sha256_required")
                if candidate.get("confidence") not in {"low", "low_medium", "medium"}:
                    errors.append(f"row_{idx}_candidate_{cidx}_confidence_invalid")
            answers = row.get("answers") if isinstance(row.get("answers"), dict) else {}
            for key in [
                "has_nav_or_price_label_candidates",
                "has_date_or_currency_label_candidates",
                "has_identity_label_candidates",
                "safe_value_extraction_candidate_next_step",
            ]:
                if key not in answers:
                    errors.append(f"row_{idx}_{key}_missing")
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    if int(summary.get("row_count") or 0) != len(rows or []):
        errors.append("summary_row_count_mismatch")
    if errors:
        raise RuntimeError("ISHARES_REFERENCE_VALUE_CANDIDATES_VALIDATION_FAILED: " + "; ".join(sorted(set(errors))))
    print(f"ISHARES_REFERENCE_VALUE_CANDIDATES_VALIDATION_OK | artifact={path} | rows={len(rows or [])}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    args = parser.parse_args()
    validate(Path(args.artifact))


if __name__ == "__main__":
    main()
