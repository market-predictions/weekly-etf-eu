from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "ishares_endpoint_evidence_v1"
FORBIDDEN_TRUE_FIELDS = ["valuation_authority", "funding_authority", "portfolio_mutation", "production_delivery", "reference_price_extraction"]
ALLOWLIST = {"product-data.jsn", "product-screener-v3.jsn", "cwpScreenerApi", "productScreenerV3Api"}


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
    endpoints = payload.get("endpoints")
    if not isinstance(endpoints, list) or not endpoints:
        errors.append("endpoints_must_be_non_empty_list")
    for obj in walk_objects(payload):
        for field in FORBIDDEN_TRUE_FIELDS:
            if field in obj and obj.get(field) is not False:
                errors.append(f"{field}_must_be_false")
    seen: set[str] = set()
    if isinstance(endpoints, list):
        for idx, endpoint in enumerate(endpoints):
            if not isinstance(endpoint, dict):
                errors.append(f"endpoint_{idx}_must_be_object")
                continue
            token = str(endpoint.get("allowlist_token") or "")
            if token not in ALLOWLIST:
                errors.append(f"endpoint_{idx}_allowlist_token_invalid")
            if token in seen:
                errors.append(f"endpoint_{idx}_duplicate_allowlist_token")
            seen.add(token)
            if not endpoint.get("url"):
                errors.append(f"endpoint_{idx}_url_required")
            if endpoint.get("bytes_sampled") is None:
                errors.append(f"endpoint_{idx}_bytes_sampled_required")
            if "body_sample" in endpoint:
                errors.append(f"endpoint_{idx}_must_not_include_body_sample")
            fields = endpoint.get("field_groups_present") if isinstance(endpoint.get("field_groups_present"), dict) else {}
            for group in ["isin", "product_name", "ticker", "nav", "reference_date", "currency"]:
                if group not in fields:
                    errors.append(f"endpoint_{idx}_{group}_field_flag_missing")
            answers = endpoint.get("answers") if isinstance(endpoint.get("answers"), dict) else {}
            for answer in [
                "structured_data_observed",
                "isin_signal_observed",
                "product_or_ticker_signal_observed",
                "nav_date_or_currency_field_signal_observed",
            ]:
                if answer not in answers:
                    errors.append(f"endpoint_{idx}_{answer}_missing")
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    if int(summary.get("endpoint_count") or 0) != len(endpoints or []):
        errors.append("summary_endpoint_count_mismatch")
    if errors:
        raise RuntimeError("ISHARES_ENDPOINT_EVIDENCE_VALIDATION_FAILED: " + "; ".join(sorted(set(errors))))
    print(f"ISHARES_ENDPOINT_EVIDENCE_VALIDATION_OK | artifact={path} | endpoints={len(endpoints or [])}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    args = parser.parse_args()
    validate(Path(args.artifact))


if __name__ == "__main__":
    main()
