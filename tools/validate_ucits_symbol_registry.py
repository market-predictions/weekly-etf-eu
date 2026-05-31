from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("PyYAML is required for UCITS registry validation") from exc

DEFAULT_REGISTRY = Path("config/ucits_symbol_registry.yml")
US_PROXY_TICKERS = {
    "SPY",
    "QQQ",
    "SMH",
    "GLD",
    "GSG",
    "PPA",
    "PAVE",
    "URNM",
    "IWM",
    "TLT",
    "KWEB",
    "ICLN",
    "SOXX",
    "ITA",
    "GRID",
    "URA",
    "NLR",
}
VERIFIED_STATUSES = {"verified_candidate_not_funded", "verified_fundable", "fundable"}
PENDING_VALUES = {"", "TBD", "pending_verification", "candidate_requires_verification", None}


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _as_str(value: Any) -> str:
    return str(value or "").strip()


def _is_pending(value: Any) -> bool:
    return value in PENDING_VALUES or _as_str(value) in PENDING_VALUES


def validate(path: Path) -> None:
    payload = _load_yaml(path)
    errors: list[str] = []
    if payload.get("schema_version") != "ucits_symbol_registry_v1":
        errors.append("schema_version_must_be_ucits_symbol_registry_v1")
    if payload.get("canonical_identity") != "isin_first":
        errors.append("canonical_identity_must_be_isin_first")
    funds = payload.get("funds") or []
    if not isinstance(funds, list) or not funds:
        errors.append("funds_must_be_non_empty_list")
    seen_registry_ids: set[str] = set()
    seen_isins: set[str] = set()
    verified_count = 0
    for fund in funds:
        rid = _as_str(fund.get("registry_id"))
        label = rid or _as_str(fund.get("fund_name")) or "unknown_fund"
        if not rid:
            errors.append("missing_registry_id")
        if rid in seen_registry_ids:
            errors.append(f"duplicate_registry_id:{rid}")
        seen_registry_ids.add(rid)
        status = _as_str(fund.get("investability_status"))
        isin = _as_str(fund.get("isin"))
        instrument_type = _as_str(fund.get("instrument_type"))
        us_proxy = _as_str(fund.get("us_research_proxy")).upper()
        if us_proxy in {"", "TBD"}:
            errors.append(f"{label}:missing_us_research_proxy")
        if us_proxy and us_proxy not in US_PROXY_TICKERS:
            errors.append(f"{label}:unexpected_us_proxy:{us_proxy}")
        if status in VERIFIED_STATUSES:
            verified_count += 1
            required_fields = [
                "isin",
                "fund_name",
                "provider",
                "instrument_type",
                "ucits_status",
                "priips_kid_status",
                "domicile",
                "base_currency",
                "distribution_policy",
                "replication_method",
                "benchmark_index",
                "ter_pct",
            ]
            for field in required_fields:
                if _is_pending(fund.get(field)):
                    errors.append(f"{label}:verified_candidate_missing_{field}")
            if isin:
                if isin in seen_isins:
                    errors.append(f"duplicate_isin:{isin}")
                seen_isins.add(isin)
            if instrument_type == "ETF" and _as_str(fund.get("ucits_status")) not in {"confirmed", "confirmed_by_fund_name"}:
                errors.append(f"{label}:verified_etf_requires_ucits_confirmation")
            if _as_str(fund.get("priips_kid_status")) != "available":
                errors.append(f"{label}:verified_candidate_requires_kid_available")
        trading_lines = fund.get("trading_lines") or []
        if not isinstance(trading_lines, list) or not trading_lines:
            errors.append(f"{label}:missing_trading_lines")
        for idx, line in enumerate(trading_lines):
            line_label = f"{label}:trading_line:{idx}"
            ticker = _as_str(line.get("exchange_ticker"))
            if not ticker or ticker == "TBD":
                errors.append(f"{line_label}:missing_exchange_ticker")
            if status in VERIFIED_STATUSES:
                for field in ["exchange", "trading_currency", "provider_symbol", "pricing_symbol_yahoo", "line_verification_status", "pricing_status"]:
                    if _is_pending(line.get(field)):
                        errors.append(f"{line_label}:verified_candidate_missing_{field}")
        proxies = fund.get("research_proxies") or []
        if not proxies:
            errors.append(f"{label}:missing_research_proxies")
        for proxy in proxies:
            proxy_ticker = _as_str(proxy.get("us_proxy")).upper()
            if proxy_ticker not in US_PROXY_TICKERS:
                errors.append(f"{label}:research_proxy_unexpected:{proxy_ticker}")
            if proxy.get("proxy_must_not_be_funded") is not True:
                errors.append(f"{label}:research_proxy_must_not_be_funded_flag_missing")
    if verified_count < 1:
        errors.append("at_least_one_verified_candidate_required_for_pricing_phase")
    if errors:
        raise RuntimeError("UCITS symbol registry validation failed: " + "; ".join(errors))
    print(f"UCITS_SYMBOL_REGISTRY_OK | funds={len(funds)} | verified_candidates={verified_count} | path={path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    args = parser.parse_args()
    validate(Path(args.registry))


if __name__ == "__main__":
    main()
