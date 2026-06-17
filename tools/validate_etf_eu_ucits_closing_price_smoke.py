from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_ucits_closing_price_smoke_v1"
PRICE_FIELDS = {
    "registry_id",
    "isin",
    "fund_name",
    "exchange",
    "exchange_ticker",
    "trading_currency",
    "provider_symbol",
    "pricing_symbol",
    "source",
    "close_date",
    "close",
    "status",
}
FAILURE_FIELDS = {"registry_id", "pricing_symbol", "status", "reason"}
SUMMARY_FIELDS = {
    "funds_seen",
    "trading_lines_seen",
    "pricing_symbols_attempted",
    "prices_found",
    "prices_missing",
    "symbols_skipped",
    "source_errors",
}
SOURCE_POLICY = {
    "primary_source",
    "fallback_source",
    "us_proxy_substitution_allowed",
    "paid_api_required",
    "secrets_required",
}
US_PROXY_SYMBOLS = {"SPY", "SMH", "GLD", "PAVE", "QQQ", "IWM", "DIA"}
ALLOWED_NEXT = {"WP14F", "WP14F_SOURCE_REVIEW"}


class ClosingPriceSmokeError(RuntimeError):
    pass


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ClosingPriceSmokeError("artifact root must be object")
    return payload


def _missing(required: set[str], payload: dict[str, Any]) -> list[str]:
    return sorted(required - set(payload))


def _validate_source_policy(policy: Any) -> None:
    if not isinstance(policy, dict):
        raise ClosingPriceSmokeError("source_policy missing")
    missing = _missing(SOURCE_POLICY, policy)
    if missing:
        raise ClosingPriceSmokeError("source_policy missing " + ", ".join(missing))
    for key in ("us_proxy_substitution_allowed", "paid_api_required", "secrets_required"):
        if policy.get(key) is not False:
            raise ClosingPriceSmokeError(f"source_policy.{key} must be false")


def _validate_summary(summary: Any, prices: list[dict[str, Any]], failures: list[dict[str, Any]]) -> None:
    if not isinstance(summary, dict):
        raise ClosingPriceSmokeError("summary missing")
    missing = _missing(SUMMARY_FIELDS, summary)
    if missing:
        raise ClosingPriceSmokeError("summary missing " + ", ".join(missing))
    price_found = len([row for row in prices if row.get("status") == "price_found"])
    skipped = len([row for row in failures if row.get("status") == "skipped_pending_symbol"])
    missing_prices = len([row for row in failures if row.get("status") == "price_unavailable"])
    source_errors = len([row for row in failures if row.get("status") == "source_error"])
    attempted = price_found + missing_prices + source_errors
    expected = {
        "prices_found": price_found,
        "symbols_skipped": skipped,
        "prices_missing": missing_prices,
        "source_errors": source_errors,
        "pricing_symbols_attempted": attempted,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            raise ClosingPriceSmokeError(f"summary count mismatch for {key}")
    if not prices and not failures:
        raise ClosingPriceSmokeError("prices and failures cannot both be empty")


def _validate_prices(prices: Any) -> list[dict[str, Any]]:
    if not isinstance(prices, list):
        raise ClosingPriceSmokeError("prices must be list")
    for row in prices:
        if not isinstance(row, dict):
            raise ClosingPriceSmokeError("price row must be object")
        missing = _missing(PRICE_FIELDS, row)
        if missing:
            raise ClosingPriceSmokeError("price row missing " + ", ".join(missing))
        if row.get("status") != "price_found":
            raise ClosingPriceSmokeError("price row status must be price_found")
        if not row.get("close_date"):
            raise ClosingPriceSmokeError("price row close_date missing")
        if float(row.get("close") or 0) <= 0:
            raise ClosingPriceSmokeError("price row close must be positive")
        if str(row.get("pricing_symbol", "")).upper() in US_PROXY_SYMBOLS:
            raise ClosingPriceSmokeError("U.S. proxy pricing substitution is not allowed")
    return prices


def _validate_failures(failures: Any) -> list[dict[str, Any]]:
    if not isinstance(failures, list):
        raise ClosingPriceSmokeError("failures must be list")
    for row in failures:
        if not isinstance(row, dict):
            raise ClosingPriceSmokeError("failure row must be object")
        missing = _missing(FAILURE_FIELDS, row)
        if missing:
            raise ClosingPriceSmokeError("failure row missing " + ", ".join(missing))
        if str(row.get("pricing_symbol", "")).upper() in US_PROXY_SYMBOLS and row.get("status") == "price_found":
            raise ClosingPriceSmokeError("U.S. proxy pricing substitution is not allowed")
    return failures


def _validate_authority(authority: Any) -> None:
    if not isinstance(authority, dict):
        raise ClosingPriceSmokeError("authority missing")
    for key, value in authority.items():
        if value is not False:
            raise ClosingPriceSmokeError(f"authority.{key} must be false")


def validate_closing_price_smoke(path: Path) -> dict[str, Any]:
    payload = _load(path)
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ClosingPriceSmokeError("bad schema_version")
    if payload.get("status") != "completed":
        raise ClosingPriceSmokeError("bad status")
    if payload.get("purpose") != "ucits_closing_price_source_smoke_test":
        raise ClosingPriceSmokeError("bad purpose")
    _validate_source_policy(payload.get("source_policy"))
    prices = _validate_prices(payload.get("prices"))
    failures = _validate_failures(payload.get("failures"))
    _validate_summary(payload.get("summary"), prices, failures)
    _validate_authority(payload.get("authority"))
    prices_found = int(payload["summary"]["prices_found"])
    selected_next = payload.get("selected_next_package")
    if selected_next not in ALLOWED_NEXT:
        raise ClosingPriceSmokeError("selected_next_package must be WP14F or WP14F_SOURCE_REVIEW")
    if prices_found >= 1 and selected_next != "WP14F":
        raise ClosingPriceSmokeError("selected_next_package must be WP14F when prices_found >= 1")
    if prices_found == 0 and selected_next != "WP14F_SOURCE_REVIEW":
        raise ClosingPriceSmokeError("selected_next_package must be WP14F_SOURCE_REVIEW when prices_found == 0")
    result = {
        "status": "valid",
        "prices_found": prices_found,
        "pricing_symbols_attempted": payload["summary"]["pricing_symbols_attempted"],
        "symbols_skipped": payload["summary"]["symbols_skipped"],
        "source_errors": payload["summary"]["source_errors"],
        "selected_next_package": selected_next,
    }
    print(
        "ETF_EU_UCITS_CLOSING_PRICE_SMOKE_OK | "
        f"artifact={path} | attempted={result['pricing_symbols_attempted']} | "
        f"prices_found={prices_found} | skipped={result['symbols_skipped']} | "
        f"source_errors={result['source_errors']} | selected_next_package={selected_next}"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_closing_price_smoke(Path(args.artifact))


if __name__ == "__main__":
    main()
