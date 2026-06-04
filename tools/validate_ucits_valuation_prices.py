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
    "preferred_official_exchange_discovery",
    "official_exchange_discovery",
}
ALLOWED_TWELVE_DATA_AUTHORITIES = {
    "candidate_valuation_source",
    "diagnostic_candidate_source",
}
ALLOWED_TWELVE_DATA_STATUSES = {
    "candidate_price_observed",
    "unresolved_dependency_missing",
    "unresolved_provider_error",
    "unresolved_no_values",
    "unresolved_invalid_close",
    "unresolved_provider_exception",
}
ALLOWED_POLICY_MODES = {"valuation_grade_pending", "temporary_yahoo_verified_fallback"}
ALLOWED_YFINANCE_AUTHORITIES = {"non_authoritative_connectivity_only", "temporary_yahoo_verified_fallback"}


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
    if policy.get("pricing_authority_mode") not in ALLOWED_POLICY_MODES:
        errors.append("policy_pricing_authority_mode_must_be_known_conservative_mode")
    rules = policy.get("rules") or {}
    for field in ["portfolio_mutation_from_pricing", "production_delivery_from_pricing", "funding_authority_from_pricing"]:
        if rules.get(field) is not False:
            errors.append(f"policy.rules.{field}_must_be_false")
    if rules.get("yfinance_default_authority") not in ALLOWED_YFINANCE_AUTHORITIES:
        errors.append("policy.rules.yfinance_default_authority_must_be_known_conservative_mode")
    if rules.get("twelve_data_default_accept_as_valuation_grade") is not False:
        errors.append("policy.rules.twelve_data_default_accept_as_valuation_grade_must_be_false")
    if not _policy_source_authorities(policy):
        errors.append(f"policy_missing_source_authority_hierarchy:{policy_path}")
    return errors


def _validate_twelve_data_evidence(label: str, row: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    evidence = row.get("twelve_data_candidate_evidence")
    if evidence is None:
        return errors
    if not isinstance(evidence, dict):
        return [f"{label}:twelve_data_candidate_evidence_must_be_object"]
    if evidence.get("source_id") != "twelve_data":
        errors.append(f"{label}:twelve_data_evidence_source_id_must_be_twelve_data")
    if evidence.get("authority") not in ALLOWED_TWELVE_DATA_AUTHORITIES:
        errors.append(f"{label}:unexpected_twelve_data_evidence_authority:{evidence.get('authority')}")
    status = evidence.get("status")
    if status not in ALLOWED_TWELVE_DATA_STATUSES:
        errors.append(f"{label}:unexpected_twelve_data_status:{status}")
    for field in ["symbol", "exchange", "expected_currency", "endpoint", "interval"]:
        if not _as_str(evidence.get(field)):
            errors.append(f"{label}:twelve_data_evidence_missing_{field}")
    if evidence.get("accept_as_valuation_grade") is not False:
        errors.append(f"{label}:twelve_data_accept_as_valuation_grade_must_remain_false_until_policy_promotion")
    if status == "candidate_price_observed":
        for field in ["observed_date", "close", "currency"]:
            if evidence.get(field) in (None, ""):
                errors.append(f"{label}:twelve_data_observed_missing_{field}")
        if not _positive_number(evidence.get("close")):
            errors.append(f"{label}:twelve_data_close_must_be_positive")
        if not _valid_iso_date(evidence.get("observed_date")):
            errors.append(f"{label}:twelve_data_observed_date_must_be_iso_date")
        if evidence.get("completed_session") is not True:
            errors.append(f"{label}:twelve_data_completed_session_must_be_true_for_observed_candidate")
        if _as_str(evidence.get("currency")).upper() != _as_str(row.get("trading_currency")).upper():
            errors.append(f"{label}:twelve_data_currency_must_match_trading_currency_for_candidate_observed")
        if evidence.get("currency_matches_expected") is not True:
            errors.append(f"{label}:twelve_data_currency_matches_expected_must_be_true_for_candidate_observed")
        blockers = row.get("valuation_blockers") or []
        if "twelve_data_accept_as_valuation_grade_false" not in blockers:
            errors.append(f"{label}:observed_twelve_data_candidate_must_remain_blocked_by_accept_flag")
    return errors


def _validate_agreement_gate_evidence(label: str, row: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    evidence = row.get("agreement_gate_evidence")
    if evidence is None:
        return errors
    if not isinstance(evidence, dict):
        return [f"{label}:agreement_gate_evidence_must_be_object"]
    if evidence.get("funding_authority") is not False:
        errors.append(f"{label}:agreement_gate_funding_authority_must_be_false")
    if evidence.get("portfolio_mutation") is not False:
        errors.append(f"{label}:agreement_gate_portfolio_mutation_must_be_false")
    if evidence.get("production_delivery") is not False:
        errors.append(f"{label}:agreement_gate_production_delivery_must_be_false")
    if evidence.get("valuation_grade_promoted_by_artifact") is not False:
        errors.append(f"{label}:agreement_gate_must_not_promote_valuation_grade")
    return errors


def validate(path: Path, source_policy_path: Path) -> None:
    payload = _load_json(path)
    policy = _load_yaml(source_policy_path)
    errors = _validate_policy(policy, source_policy_path)
    source_authorities = _policy_source_authorities(policy)

    if payload.get("schema_version") != "ucits_valuation_prices_v1":
        errors.append("schema_version_must_be_ucits_valuation_prices_v1")
    if payload.get("pricing_authority_mode") not in ALLOWED_POLICY_MODES:
        errors.append("pricing_authority_mode_must_be_known_conservative_mode")
    for field in ["portfolio_mutation", "production_delivery", "funding_authority"]:
        if payload.get(field) is not False:
            errors.append(f"top_level_{field}_must_be_false")

    rows = payload.get("rows") or []
    if not isinstance(rows, list) or not rows:
        errors.append("at_least_one_valuation_price_row_required")

    valuation_grade_count = 0
    twelve_data_observed_count = 0
    for idx, row in enumerate(rows):
        label = f"row:{idx}:{row.get('registry_id') or 'unknown'}"
        for field in ["registry_id", "isin", "fund_name", "exchange", "exchange_ticker", "trading_currency", "provider_symbol", "valuation_status"]:
            if not _as_str(row.get(field)):
                errors.append(f"{label}:missing_{field}")
        for field in ["portfolio_mutation", "production_delivery", "funding_authority"]:
            if row.get(field) is not False:
                errors.append(f"{label}:{field}_must_be_false")

        evidence = row.get("twelve_data_candidate_evidence") or {}
        if evidence.get("status") == "candidate_price_observed":
            twelve_data_observed_count += 1
        errors.extend(_validate_twelve_data_evidence(label, row))
        errors.extend(_validate_agreement_gate_evidence(label, row))

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
            if source_id in {"yahoo_yfinance", "twelve_data"}:
                errors.append(f"{label}:{source_id}_cannot_be_valuation_grade_under_current_policy")
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
    print("UCITS_VALUATION_PRICES_VALIDATION_OK" f" | artifact={path}" f" | rows={len(rows)}" f" | twelve_data_candidate_observed={twelve_data_observed_count}" f" | valuation_grade_rows={valuation_grade_count}" " | portfolio_mutation=false | delivery=false")


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
