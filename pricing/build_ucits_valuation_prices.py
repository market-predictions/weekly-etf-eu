from __future__ import annotations

import argparse
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("PyYAML is required for UCITS valuation pricing") from exc

DEFAULT_REGISTRY = Path("config/ucits_symbol_registry.yml")
DEFAULT_SOURCE_POLICY = Path("config/ucits_pricing_source_policy.yml")
DEFAULT_OUTPUT_DIR = Path("output/pricing")
PENDING_STATUS = "valuation_grade_pending"
TWELVE_DATA_BASE_URL = "https://api.twelvedata.com"
ALLOWED_TWELVE_DATA_AUTHORITIES = {"candidate_valuation_source", "diagnostic_candidate_source"}


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _latest_file(output_dir: Path, pattern: str) -> Path:
    files = sorted(output_dir.glob(pattern))
    if not files:
        raise RuntimeError(f"No artifact found in {output_dir} matching {pattern}")
    return files[-1]


def _as_str(value: Any) -> str:
    return str(value or "").strip()


def _policy_key(row: dict[str, Any]) -> tuple[str, str, str, str, str]:
    return (
        _as_str(row.get("registry_id")),
        _as_str(row.get("isin")),
        _as_str(row.get("exchange")),
        _as_str(row.get("exchange_ticker")),
        _as_str(row.get("trading_currency")),
    )


def _build_policy_index(policy: dict[str, Any]) -> dict[tuple[str, str, str, str, str], dict[str, Any]]:
    index: dict[tuple[str, str, str, str, str], dict[str, Any]] = {}
    for line in policy.get("trading_line_policies") or []:
        key = _policy_key(line)
        if all(key):
            index[key] = line
    return index


def _validate_policy(policy: dict[str, Any], policy_path: Path) -> None:
    errors: list[str] = []
    if policy.get("schema_version") != "ucits_pricing_source_policy_v1":
        errors.append("schema_version_must_be_ucits_pricing_source_policy_v1")
    if policy.get("pricing_authority_mode") != "valuation_grade_pending":
        errors.append("pricing_authority_mode_must_be_valuation_grade_pending")

    rules = policy.get("rules") or {}
    for field in ["portfolio_mutation_from_pricing", "production_delivery_from_pricing", "funding_authority_from_pricing"]:
        if rules.get(field) is not False:
            errors.append(f"rules.{field}_must_be_false")
    if rules.get("yfinance_default_authority") != "non_authoritative_connectivity_only":
        errors.append("rules.yfinance_default_authority_must_remain_non_authoritative_connectivity_only")
    if rules.get("twelve_data_default_accept_as_valuation_grade") is not False:
        errors.append("rules.twelve_data_default_accept_as_valuation_grade_must_be_false")

    for idx, line in enumerate(policy.get("trading_line_policies") or []):
        label = f"trading_line_policy:{idx}:{line.get('registry_id') or 'unknown'}"
        for field in ["registry_id", "isin", "exchange", "exchange_ticker", "trading_currency", "provider_symbol"]:
            if not _as_str(line.get(field)):
                errors.append(f"{label}:missing_{field}")
        source_order = line.get("source_order") or []
        if not source_order:
            errors.append(f"{label}:source_order_required")
        for source in source_order:
            source_id = source.get("source_id")
            if source_id == "yahoo_yfinance":
                if source.get("authority") != "non_authoritative_connectivity_only":
                    errors.append(f"{label}:yahoo_yfinance_must_be_connectivity_only")
                if source.get("valuation_grade_eligible") is not False:
                    errors.append(f"{label}:yahoo_yfinance_must_not_be_valuation_grade_eligible")
            if source_id == "twelve_data":
                for field in ["symbol", "exchange", "expected_currency"]:
                    if not _as_str(source.get(field)):
                        errors.append(f"{label}:twelve_data_missing_{field}")
                if source.get("authority") not in ALLOWED_TWELVE_DATA_AUTHORITIES:
                    errors.append(f"{label}:unexpected_twelve_data_authority:{source.get('authority')}")
                if source.get("accept_as_valuation_grade") is not False:
                    errors.append(f"{label}:twelve_data_accept_as_valuation_grade_must_remain_false")
    if errors:
        raise RuntimeError("UCITS valuation pricing source policy invalid: " + "; ".join(errors))
    print(f"UCITS_VALUATION_PRICING_POLICY_OK | policy={policy_path}")


def _preflight_index(preflight_payload: dict[str, Any] | None) -> dict[tuple[str, str, str, str, str], dict[str, Any]]:
    if not preflight_payload:
        return {}
    return {_policy_key(row): row for row in preflight_payload.get("results") or []}


def _non_authoritative_evidence(preflight_row: dict[str, Any] | None) -> dict[str, Any] | None:
    if not preflight_row:
        return None
    result = preflight_row.get("preflight_result") or {}
    evidence: dict[str, Any] = {
        "source_id": "yahoo_yfinance",
        "authority": "non_authoritative_connectivity_only",
        "status": result.get("status"),
        "excluded_from_valuation_authority_reason": "source_policy_marks_yahoo_yfinance_as_non_authoritative_connectivity_only",
    }
    for field in ["observed_date", "close", "source", "error", "currency_warning"]:
        if field in result:
            evidence[field] = result.get(field)
    return evidence


def _query(params: dict[str, Any]) -> str:
    return urllib.parse.urlencode({k: v for k, v in params.items() if v is not None and v != ""})


def _twelve_data_api_key() -> str | None:
    return os.environ.get("TWELVE_DATA_API_KEY") or os.environ.get("TWELVEDATA_API_KEY")


def _http_get_json(url: str, timeout: int = 20) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - controlled provider URL
        return json.loads(resp.read().decode("utf-8"))


def _fetch_twelve_data_evidence(source_policy: dict[str, Any]) -> dict[str, Any]:
    symbol = _as_str(source_policy.get("symbol"))
    exchange = _as_str(source_policy.get("exchange"))
    expected_currency = _as_str(source_policy.get("expected_currency"))
    authority = source_policy.get("authority") or "diagnostic_candidate_source"
    api_key = _twelve_data_api_key()

    base_evidence: dict[str, Any] = {
        "source_id": "twelve_data",
        "authority": authority,
        "symbol": symbol,
        "exchange": exchange,
        "expected_currency": expected_currency,
        "accept_as_valuation_grade": False,
        "endpoint": "time_series",
        "interval": source_policy.get("interval") or "1day",
        "outputsize": source_policy.get("outputsize") or 5,
    }

    if not api_key:
        return {**base_evidence, "status": "unresolved_dependency_missing", "error": "Missing TWELVE_DATA_API_KEY or TWELVEDATA_API_KEY"}

    try:
        url = f"{TWELVE_DATA_BASE_URL}/time_series?" + _query({
            "symbol": symbol,
            "exchange": exchange,
            "interval": source_policy.get("interval") or "1day",
            "outputsize": source_policy.get("outputsize") or 5,
            "format": "JSON",
            "apikey": api_key,
        })
        data = _http_get_json(url)
        if data.get("status") == "error" or data.get("code"):
            return {**base_evidence, "status": "unresolved_provider_error", "error": data.get("message") or data.get("status"), "provider_code": data.get("code")}
        values = data.get("values") or []
        meta = data.get("meta") or {}
        if not values:
            return {**base_evidence, "status": "unresolved_no_values", "provider_currency": meta.get("currency"), "provider_exchange": meta.get("exchange") or meta.get("mic_code")}
        latest = values[0]
        close = float(latest.get("close"))
        currency = _as_str(meta.get("currency")) or None
        return {
            **base_evidence,
            "status": "candidate_price_observed",
            "observed_date": _as_str(latest.get("datetime"))[:10],
            "close": close,
            "currency": currency,
            "provider_exchange": meta.get("exchange") or meta.get("mic_code"),
            "currency_matches_expected": bool(currency and expected_currency and currency.upper() == expected_currency.upper()),
            "completed_session": True,
            "raw_meta": {"symbol": meta.get("symbol"), "exchange": meta.get("exchange"), "mic_code": meta.get("mic_code"), "currency": meta.get("currency")},
        }
    except Exception as exc:  # pragma: no cover
        return {**base_evidence, "status": "unresolved_provider_exception", "error": str(exc)}


def _source_by_id(line_policy: dict[str, Any] | None, source_id: str) -> dict[str, Any] | None:
    for source in (line_policy or {}).get("source_order") or []:
        if source.get("source_id") == source_id:
            return source
    return None


def _line_source_lineage(line_policy: dict[str, Any] | None) -> list[dict[str, Any]]:
    return list((line_policy or {}).get("source_order") or [])


def build_valuation_artifact(registry_path: Path, source_policy_path: Path, candidate_artifact_path: Path, output_dir: Path, run_id: str, preflight_artifact_path: Path | None = None) -> dict[str, Any]:
    registry = _load_yaml(registry_path)
    policy = _load_yaml(source_policy_path)
    _validate_policy(policy, source_policy_path)
    candidates_payload = _load_json(candidate_artifact_path)
    preflight_payload = _load_json(preflight_artifact_path) if preflight_artifact_path else None
    policy_index = _build_policy_index(policy)
    preflight_rows = _preflight_index(preflight_payload)

    rows: list[dict[str, Any]] = []
    missing_policy: list[dict[str, Any]] = []
    for candidate in candidates_payload.get("candidates") or []:
        key = _policy_key(candidate)
        line_policy = policy_index.get(key)
        blockers = [] if line_policy else ["missing_trading_line_policy"]
        if not line_policy:
            missing_policy.append({"registry_id": candidate.get("registry_id"), "isin": candidate.get("isin"), "exchange": candidate.get("exchange"), "exchange_ticker": candidate.get("exchange_ticker"), "trading_currency": candidate.get("trading_currency")})
        else:
            blockers.append("no_integrated_preferred_exchange_official_close")

        non_authoritative = _non_authoritative_evidence(preflight_rows.get(key))
        if non_authoritative and non_authoritative.get("status") == "priced_non_authoritative":
            blockers.append("non_authoritative_preflight_price_excluded_from_valuation_grade")

        twelve_source_policy = _source_by_id(line_policy, "twelve_data")
        twelve_data_evidence = _fetch_twelve_data_evidence(twelve_source_policy) if twelve_source_policy else None
        if twelve_data_evidence:
            status = twelve_data_evidence.get("status")
            if status == "candidate_price_observed":
                blockers.append("twelve_data_candidate_price_observed_but_not_accepted_as_valuation_grade")
                blockers.append("twelve_data_accept_as_valuation_grade_false")
                if twelve_data_evidence.get("currency_matches_expected") is not True:
                    blockers.append("twelve_data_currency_mismatch_or_unverified")
            else:
                blockers.append(f"twelve_data_{status or 'unresolved'}")

        rows.append({
            "registry_id": candidate.get("registry_id"),
            "isin": candidate.get("isin"),
            "fund_name": candidate.get("fund_name"),
            "provider": candidate.get("provider"),
            "instrument_type": candidate.get("instrument_type"),
            "ucits_status": candidate.get("ucits_status"),
            "priips_kid_status": candidate.get("priips_kid_status"),
            "investability_status": candidate.get("investability_status"),
            "fundable_status": candidate.get("fundable_status"),
            "exchange": candidate.get("exchange"),
            "exchange_ticker": candidate.get("exchange_ticker"),
            "trading_currency": candidate.get("trading_currency"),
            "provider_symbol": candidate.get("provider_symbol"),
            "pricing_symbol_yahoo": candidate.get("pricing_symbol_yahoo"),
            "valuation_status": PENDING_STATUS,
            "valuation_grade": False,
            "pricing_source": None,
            "source_authority": None,
            "observed_date": None,
            "close": None,
            "currency": None,
            "completed_session": False,
            "session_rule": "completed_regular_session_required_before_valuation_grade",
            "source_lineage": _line_source_lineage(line_policy),
            "twelve_data_candidate_evidence": twelve_data_evidence,
            "non_authoritative_preflight_evidence": non_authoritative,
            "valuation_blockers": blockers,
            "portfolio_mutation": False,
            "production_delivery": False,
            "funding_authority": False,
        })

    return {
        "schema_version": "ucits_valuation_prices_v1",
        "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_registry": str(registry_path),
        "source_policy": str(source_policy_path),
        "source_candidate_artifact": str(candidate_artifact_path),
        "source_preflight_artifact": str(preflight_artifact_path) if preflight_artifact_path else None,
        "registry_schema_version": registry.get("schema_version"),
        "pricing_authority_mode": policy.get("pricing_authority_mode"),
        "portfolio_mutation": False,
        "production_delivery": False,
        "funding_authority": False,
        "valuation_grade_row_count": 0,
        "valuation_pending_row_count": len(rows),
        "missing_policy_rows": missing_policy,
        "rows": rows,
    }


def write_valuation_artifact(registry_path: Path, source_policy_path: Path, candidate_artifact_path: Path, output_dir: Path, run_id: str, preflight_artifact_path: Path | None = None) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact = build_valuation_artifact(registry_path, source_policy_path, candidate_artifact_path, output_dir, run_id, preflight_artifact_path)
    path = output_dir / f"ucits_valuation_prices_{run_id}.json"
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    observed = sum(1 for row in artifact["rows"] if (row.get("twelve_data_candidate_evidence") or {}).get("status") == "candidate_price_observed")
    print("UCITS_VALUATION_PRICES_OK" f" | artifact={path}" f" | rows={len(artifact['rows'])}" f" | twelve_data_candidate_observed={observed}" f" | valuation_grade_rows={artifact['valuation_grade_row_count']}" " | portfolio_mutation=false | delivery=false")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--source-policy", default=str(DEFAULT_SOURCE_POLICY))
    parser.add_argument("--candidate-artifact", default=None)
    parser.add_argument("--preflight-artifact", default=None)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    run_id = args.run_id or _run_id()
    candidate_artifact = Path(args.candidate_artifact) if args.candidate_artifact else _latest_file(output_dir, "ucits_pricing_candidates_*.json")
    preflight_artifact = Path(args.preflight_artifact) if args.preflight_artifact else None
    write_valuation_artifact(Path(args.registry), Path(args.source_policy), candidate_artifact, output_dir, run_id, preflight_artifact)


if __name__ == "__main__":
    main()
