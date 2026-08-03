from __future__ import annotations

import csv
import io
import os
from datetime import date, timedelta
from typing import Any

import requests

from pricing import ucits_close_price_multi_source as legacy


STOOQ_API_KEY_ENV = "STOOQ_API_KEY"
STOOQ_URL = legacy.STOOQ_URL


def _base_result(symbol: str, *, api_key_supplied: bool) -> dict[str, Any]:
    return {
        "pricing_status": "fetch_failed",
        "close_price": None,
        "close_date": None,
        "observed_at_utc": legacy.utc_now(),
        "blockers": [],
        "provider_symbol": symbol,
        "response_classification": "not_attempted",
        "api_key_supplied": api_key_supplied,
        "http_status": None,
        "content_type": None,
        "response_bytes": None,
        "csv_fieldnames": [],
        "valid_csv": False,
    }


def classify_stooq_response(
    *,
    symbol: str,
    response: requests.Response,
    report_date: date,
    api_key_supplied: bool,
) -> dict[str, Any]:
    result = _base_result(symbol, api_key_supplied=api_key_supplied)
    result["http_status"] = response.status_code
    result["content_type"] = str(response.headers.get("content-type") or "").split(";", 1)[0].strip().lower()
    result["response_bytes"] = len(response.content or b"")

    if response.status_code != 200:
        result["response_classification"] = "http_error"
        result["blockers"] = [f"stooq_http_status:{response.status_code}"]
        return result

    text = response.text.strip()
    folded = text.casefold()
    if not text:
        result["response_classification"] = "empty_response"
        result["blockers"] = ["stooq_empty_response"]
        return result
    if "get your apikey" in folded or ("apikey" in folded and "captcha" in folded):
        result["response_classification"] = "api_key_required"
        result["blockers"] = ["stooq_api_key_required"]
        return result
    if "exceeded" in folded and ("limit" in folded or "download" in folded):
        result["response_classification"] = "daily_limit_exceeded"
        result["blockers"] = ["stooq_daily_limit_exceeded"]
        return result
    if folded.startswith("no data"):
        result["response_classification"] = "symbol_not_found_or_no_data"
        result["blockers"] = ["stooq_symbol_not_found_or_no_data"]
        return result

    try:
        reader = csv.DictReader(io.StringIO(text))
        fieldnames = [str(name or "").strip() for name in (reader.fieldnames or [])]
        rows = list(reader)
    except Exception as exc:
        result["response_classification"] = "csv_parse_error"
        result["blockers"] = [f"stooq_csv_parse:{type(exc).__name__}"]
        return result

    result["csv_fieldnames"] = fieldnames
    if not {"Date", "Close"}.issubset(set(fieldnames)):
        result["response_classification"] = "non_csv_or_unexpected_schema"
        result["blockers"] = ["stooq_non_csv_or_unexpected_schema"]
        return result

    result["valid_csv"] = True
    accepted: list[tuple[date, float]] = []
    for row in rows:
        try:
            row_date = date.fromisoformat(str(row.get("Date") or ""))
        except ValueError:
            continue
        close = legacy.usable_close(row.get("Close"))
        if close is not None and row_date <= report_date:
            accepted.append((row_date, close))

    if not accepted:
        result["response_classification"] = "valid_csv_without_completed_close"
        result["blockers"] = ["stooq_valid_csv_without_completed_close_on_or_before_report_date"]
        return result

    close_date, close_value = max(accepted, key=lambda item: item[0])
    result.update(
        {
            "pricing_status": "priced_non_authoritative",
            "close_price": close_value,
            "close_date": close_date.isoformat(),
            "response_classification": "valid_completed_close",
            "blockers": [],
        }
    )
    return result


def try_stooq_close_detailed(
    line: dict[str, Any],
    report_date: date,
    *,
    api_key: str | None = None,
    session: requests.Session | None = None,
) -> dict[str, Any]:
    symbol = legacy.stooq_symbol(line)
    resolved_key = str(api_key if api_key is not None else os.environ.get(STOOQ_API_KEY_ENV, "")).strip()
    result = _base_result(symbol, api_key_supplied=bool(resolved_key))
    if not symbol:
        result["response_classification"] = "missing_symbol"
        result["blockers"] = ["missing_provider_symbol_stooq"]
        return result

    start = report_date - timedelta(days=35)
    params = {
        "s": symbol,
        "i": "d",
        "d1": start.strftime("%Y%m%d"),
        "d2": report_date.strftime("%Y%m%d"),
    }
    if resolved_key:
        params["apikey"] = resolved_key

    client = session or requests
    try:
        response = client.get(
            STOOQ_URL,
            params=params,
            timeout=25,
            headers={
                "User-Agent": "Mozilla/5.0 ETF-EU-Routine/1.1",
                "Accept": "text/csv,text/plain,*/*",
            },
        )
    except Exception as exc:
        result["response_classification"] = "request_exception"
        result["blockers"] = [f"stooq_exception:{type(exc).__name__}"]
        return result

    return classify_stooq_response(
        symbol=symbol,
        response=response,
        report_date=report_date,
        api_key_supplied=bool(resolved_key),
    )


def try_stooq_close_compat(
    line: dict[str, Any],
    report_date: date,
) -> tuple[str, float | None, str | None, str | None, list[str], str]:
    result = try_stooq_close_detailed(line, report_date)
    return (
        str(result["pricing_status"]),
        result["close_price"],
        result["close_date"],
        result["observed_at_utc"],
        list(result["blockers"]),
        str(result["provider_symbol"]),
    )


def build_results(**kwargs: Any):
    """Preserve the legacy output contract while replacing Stooq handling."""
    original = legacy.try_stooq_close
    legacy.try_stooq_close = try_stooq_close_compat
    try:
        return legacy.build_results(**kwargs)
    finally:
        legacy.try_stooq_close = original
