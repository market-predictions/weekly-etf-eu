from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_OUTPUT_DIR = Path("output/pricing")
ALLOWED_DISCOVERY_STATUSES = {
    "candidate_time_series_resolved",
    "candidate_time_series_unresolved",
    "candidate_symbol_matches_found",
    "candidate_symbol_matches_not_found",
    "unresolved_dependency_missing",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _latest_file(output_dir: Path) -> Path:
    files = sorted(output_dir.glob("ucits_twelve_data_symbol_discovery_*.json"))
    if not files:
        raise RuntimeError(f"No Twelve Data symbol-discovery artifacts found in {output_dir}")
    return files[-1]


def _as_str(value: Any) -> str:
    return str(value or "").strip()


def validate(path: Path) -> None:
    payload = _load_json(path)
    errors: list[str] = []
    if payload.get("schema_version") != "ucits_twelve_data_symbol_discovery_v1":
        errors.append("schema_version_must_be_ucits_twelve_data_symbol_discovery_v1")
    for field in ["portfolio_mutation", "production_delivery", "funding_authority", "valuation_authority"]:
        if payload.get(field) is not False:
            errors.append(f"top_level_{field}_must_be_false")
    rows = payload.get("rows") or []
    if not isinstance(rows, list) or not rows:
        errors.append("at_least_one_symbol_discovery_row_required")
    resolved_time_series = 0
    matches_found = 0
    for idx, row in enumerate(rows):
        label = f"row:{idx}:{row.get('registry_id') or 'unknown'}"
        for field in ["registry_id", "isin", "exchange", "exchange_ticker", "trading_currency", "provider_symbol", "source_id", "authority", "expected_currency"]:
            if not _as_str(row.get(field)):
                errors.append(f"{label}:missing_{field}")
        if row.get("source_id") != "twelve_data":
            errors.append(f"{label}:source_id_must_be_twelve_data")
        if row.get("authority") != "candidate_valuation_source":
            errors.append(f"{label}:authority_must_be_candidate_valuation_source")
        if row.get("accept_as_valuation_grade") is not False:
            errors.append(f"{label}:accept_as_valuation_grade_must_be_false")
        attempts = row.get("attempts") or []
        if not isinstance(attempts, list) or not attempts:
            errors.append(f"{label}:at_least_one_attempt_required")
            continue
        for attempt_idx, attempt in enumerate(attempts):
            attempt_label = f"{label}:attempt:{attempt_idx}"
            if attempt.get("status") == "unresolved_dependency_missing":
                continue
            time_series = attempt.get("time_series") or {}
            symbol_search = attempt.get("symbol_search") or {}
            for sub_name, sub in [("time_series", time_series), ("symbol_search", symbol_search)]:
                if not isinstance(sub, dict):
                    errors.append(f"{attempt_label}:{sub_name}_must_be_object")
                    continue
                status = sub.get("status")
                if status not in ALLOWED_DISCOVERY_STATUSES:
                    errors.append(f"{attempt_label}:{sub_name}:unexpected_status:{status}")
                if not _as_str(sub.get("endpoint")):
                    errors.append(f"{attempt_label}:{sub_name}:missing_endpoint")
                if not _as_str(sub.get("symbol")):
                    errors.append(f"{attempt_label}:{sub_name}:missing_symbol")
            if time_series.get("status") == "candidate_time_series_resolved":
                resolved_time_series += 1
                if not time_series.get("latest_datetime"):
                    errors.append(f"{attempt_label}:resolved_time_series_missing_latest_datetime")
                if time_series.get("latest_close") in (None, ""):
                    errors.append(f"{attempt_label}:resolved_time_series_missing_latest_close")
            if symbol_search.get("status") == "candidate_symbol_matches_found":
                matches_found += 1
                if not symbol_search.get("matches"):
                    errors.append(f"{attempt_label}:symbol_search_matches_found_but_empty_matches")
    if errors:
        raise RuntimeError("UCITS Twelve Data symbol discovery validation failed: " + "; ".join(errors))
    print(
        "UCITS_TWELVE_DATA_SYMBOL_DISCOVERY_VALIDATION_OK"
        f" | artifact={path}"
        f" | rows={len(rows)}"
        f" | resolved_time_series_attempts={resolved_time_series}"
        f" | symbol_search_matches_found={matches_found}"
        " | portfolio_mutation=false | delivery=false"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", default=None)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()
    artifact = Path(args.artifact) if args.artifact else _latest_file(Path(args.output_dir))
    validate(artifact)


if __name__ == "__main__":
    main()
