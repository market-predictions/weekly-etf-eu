from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("PyYAML is required for UCITS valuation price validation") from exc

DEFAULT_OUTPUT_DIR = Path("output/pricing")
DEFAULT_SOURCE_POLICY = Path("config/ucits_pricing_source_policy.yml")
ALLOWED_PENDING_STATUSES = {
    "valuation_grade_pending",
    "blocked_no_authoritative_source",
    "blocked_stale_price",
    "blocked_currency_mismatch",
}
VALUATION_GRADE_AUTHORITIES = {
    "preferred_valuation_source",
    "candidate_valuation_source",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _latest_valuation_file(output_dir: Path) -> Path:
    files = sorted(output_dir.glob("ucits_valuation_prices_*.json"))
    if not files:
        raise RuntimeError(f"No UCITS valuation price artifacts found in {output_dir}")
    return files[-1]


def _as_str(value: Any) -> str:
    return str(value or "").strip()


def _positive_number(value: Any) -> bool:
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False


def _valid_iso_date(value: Any) -> bool:
    try:
        date.fromisoformat(_as_str(value))
        return True
    except ValueError:
        return False


def _policy_source_authorities(policy: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for source in policy.get("source_authority_hierarchy") or []:
        source_id = _as_str(source.get("source_id"))
        if source_id:
            result[source_id] = source
    return result


def _validate_policy(policy: dict[str, Any], policy_path: Path) -> list[str]:
    errors: list[str] = []
    if policy.get("schema_version") != "ucits_pricing_source_policy_v1":
        errors.append("policy_schema_version_must_be_ucits_pricing_source_policy_v1")
    rules = policy.get("rules") or {}
    for field in [
        "portfolio_mutation_from_pricing",
        "production_delivery_from_pricing",
        "funding_authority_from_pricing",
    ]:
        if rules.get(field) is not False:
            errors.append(f"policy.rules.{field}_must_be_false")
    if rules.get("yfinance_default_authority") != "non_authoritative_connectivity_only":
        errors.append("policy.rules.yfinance_default_authority_must_be_non_authoritative_connectivity_only")
    if not _policy_source_authorities(policy):
        errors.append(f"policy_missing_source_authority_hierarchy:{policy_path}")
    return errors


def validate(path: Path, source_policy_path: Path) -> None:
    payload = _load_json(path)
    policy = _load_yaml(source_policy_path)
    errors = _validate_policy(policy, source_policy_path)
    source_authorities = _policy_source_authorities(policy)

    if payload.get("schema_version") != "ucits_valuation_prices_v1":
        errors.append("schema_version_must_be_ucits_valuation_prices_v1")
    if payload.get("pricing_authority_mode") != "valuation_grade_pending":
        errors.append("pricing_authority_mode_must_be_valuation_grade_pending")
    for field in ["portfolio_mutation", "production_delivery", "funding_authority"]:
        if payload.get(field) is not False:
            errors.append(f"top_level_{field}_must_be_false")

    rows = payload.get("rows") or []
    if not isinstance(rows, list) or not rows:
        errors.append("at_least_one_valuation_price_row_required")

    valuation_grade_count = 0
    for idx, row in enumerate(rows):
        label = f"row:{idx}:{row.get('registry_id') or 'unknown'}"
        for field in [
            "registry_id",
            "isin",
            "fund_name",
            "exchange",
            "exchange_ticker",
            "trading_currency",
            "provider_symbol",
            "valuation_status",
        ]:
            if not _as_str(row.get(field)):
                errors.append(f"{label}:missing_{field}")

        for field in ["portfolio_mutation", "production_delivery", "funding_authority"]:
            if row.get(field) is not False:
                errors.append(f"{label}:{field}_must_be_false")

        valuation_grade = row.get("valuation_grade")
        valuation_status = row.get("valuation_status")
        if valuation_grade is True:
            valuation_grade_count += 1
            if valuation_status != "valuation_grade":
                errors.append(f"{label}:valuation_grade_true_requires_status_valuation_grade")
            for field in ["pricing_source", "source_authority", "observed_date", "close", "currency", "source_lineage"]:
                if row.get(field) in (None, "", []):
                    errors.append(f"{label}:valuation_grade_missing_{field}")
            if row.get("completed_session") is not True:
                errors.append(f"{label}:valuation_grade_requires_completed_session_true")
            if not _positive_number(row.get("close")):
                errors.append(f"{label}:valuation_grade_close_must_be_positive")
            if not _valid_iso_date(row.get("observed_date")):
                errors.append(f"{label}:valuation_grade_observed_date_must_be_iso_date")
            if _as_str(row.get("currency")) != _as_str(row.get("trading_currency")):
                errors.append(f"{label}:valuation_grade_currency_must_match_trading_currency")
            source_id = _as_str(row.get("pricing_source"))
            source_policy = source_authorities.get(source_id)
            if not source_policy:
                errors.append(f"{label}:pricing_source_not_in_policy:{source_id}")
            else:
                if source_policy.get("valuation_grade_eligible") is not True:
                    errors.append(f"{label}:pricing_source_not_valuation_grade_eligible:{source_id}")
                if _as_str(source_policy.get("authority")) not in VALUATION_GRADE_AUTHORITIES:
                    errors.append(f"{label}:invalid_source_authority:{source_policy.get('authority')}")
            if source_id == "yahoo_yfinance":
                errors.append(f"{label}:yahoo_yfinance_cannot_be_valuation_grade_under_current_policy")
        else:
            if valuation_grade is not False:
                errors.append(f"{label}:valuation_grade_must_be_boolean")
            if valuation_status not in ALLOWED_PENDING_STATUSES:
                errors.append(f"{label}:unexpected_non_grade_status:{valuation_status}")
            if row.get("close") is not None or row.get("pricing_source") is not None:
                errors.append(f"{label}:non_grade_row_must_not_place_close_or_pricing_source_in_authority_fields")
            if row.get("completed_session") is not False:
                errors.append(f"{label}:non_grade_row_completed_session_must_be_false")
            if not row.get("valuation_blockers"):
                errors.append(f"{label}:non_grade_row_requires_valuation_blockers")

    declared_grade_count = payload.get("valuation_grade_row_count")
    if declared_grade_count != valuation_grade_count:
        errors.append(f"valuation_grade_row_count_mismatch:declared={declared_grade_count}:actual={valuation_grade_count}")

    if errors:
        raise RuntimeError("UCITS valuation price validation failed: " + "; ".join(errors))

    print(
        "UCITS_VALUATION_PRICES_VALIDATION_OK"
        f" | artifact={path}"
        f" | rows={len(rows)}"
        f" | valuation_grade_rows={valuation_grade_count}"
        " | portfolio_mutation=false | delivery=false"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", default=None)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--source-policy", default=str(DEFAULT_SOURCE_POLICY))
    args = parser.parse_args()
    artifact = Path(args.artifact) if args.artifact else _latest_valuation_file(Path(args.output_dir))
    validate(artifact, Path(args.source_policy))


if __name__ == "__main__":
    main()
