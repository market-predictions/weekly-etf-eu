from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import requests

BASE_URL = "https://api.boerse-frankfurt.de"
TRACE_SALT = "w4icATTGtnjAQMbkL3kJwxLfEAKDa3VU"
TIMEOUT_SECONDS = 30
LINES = [
    {"ticker": "VWCE", "isin": "IE00BK5BQT80", "mic": "XETR", "currency": "EUR"},
    {"ticker": "EUNA", "isin": "IE00BDBRDM35", "mic": "XETR", "currency": "EUR"},
    {"ticker": "SXR8", "isin": "IE00B5BMR087", "mic": "XETR", "currency": "EUR"},
    {"ticker": "VVSM", "isin": "IE00BMC38736", "mic": "XETR", "currency": "EUR"},
    {"ticker": "L0CK", "isin": "IE00BG0J4C88", "mic": "XETR", "currency": "EUR"},
]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def headers_for(url: str) -> dict[str, str]:
    now_utc = utc_now()
    client_date = now_utc.isoformat(timespec="milliseconds").replace("+00:00", "Z")
    trace_id = hashlib.md5((client_date + url + TRACE_SALT).encode("utf-8")).hexdigest()
    now_local = datetime.now().astimezone()
    security = hashlib.md5(now_local.strftime("%Y%m%d%H%M").encode("utf-8")).hexdigest()
    return {
        "Accept": "application/json, text/plain, */*",
        "Client-Date": client_date,
        "X-Client-TraceId": trace_id,
        "X-Security": security,
        "Referer": "https://www.boerse-frankfurt.de/",
        "User-Agent": "Mozilla/5.0 Weekly-ETF-EU-Exchange-Probe/1.0",
    }


def get_json(path: str, params: dict[str, Any]) -> dict[str, Any]:
    url = f"{BASE_URL}{path}?{urlencode(params)}"
    observed_at = utc_now().replace(microsecond=0).isoformat().replace("+00:00", "Z")
    try:
        response = requests.get(url, headers=headers_for(url), timeout=TIMEOUT_SECONDS)
    except Exception as exc:
        return {
            "status": "request_exception",
            "exception_type": type(exc).__name__,
            "observed_at_utc": observed_at,
        }
    result: dict[str, Any] = {
        "http_status": response.status_code,
        "content_type": response.headers.get("content-type"),
        "response_bytes": len(response.content),
        "observed_at_utc": observed_at,
    }
    try:
        payload = response.json()
    except ValueError:
        result["status"] = "non_json_response"
        result["response_fingerprint"] = hashlib.sha256(response.content).hexdigest()
        return result
    result["status"] = "json_response" if response.status_code == 200 else "http_error"
    result["payload_type"] = type(payload).__name__
    if isinstance(payload, dict):
        result["top_level_keys"] = sorted(str(key) for key in payload.keys())[:30]
    elif isinstance(payload, list):
        result["list_length"] = len(payload)
    result["payload"] = payload
    return result


def normalize_price_history(payload: Any, report_date: date) -> list[dict[str, Any]]:
    candidates: Any = payload
    if isinstance(payload, dict):
        for key in ("data", "values", "results", "priceHistory"):
            if isinstance(payload.get(key), list):
                candidates = payload[key]
                break
    rows: list[dict[str, Any]] = []
    if not isinstance(candidates, list):
        return rows
    for item in candidates:
        if not isinstance(item, dict):
            continue
        raw_date = str(item.get("date") or item.get("timestamp") or item.get("time") or "")[:10]
        try:
            row_date = date.fromisoformat(raw_date)
        except ValueError:
            continue
        if row_date > report_date:
            continue
        raw_close = item.get("close") or item.get("closingPrice") or item.get("value")
        try:
            close = float(raw_close)
        except (TypeError, ValueError):
            continue
        if close > 0:
            rows.append({"date": row_date.isoformat(), "close": close})
    return sorted(rows, key=lambda row: row["date"])


def normalize_tradingview(payload: Any, report_date: date) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    items = payload if isinstance(payload, list) else []
    for item in items:
        if not isinstance(item, dict):
            continue
        quotes = item.get("quotes") or {}
        pairs = quotes.get("timeValuePairs") or []
        for pair in pairs:
            if not isinstance(pair, dict):
                continue
            stamp = pair.get("time") or pair.get("timestamp")
            value = pair.get("value")
            try:
                row_date = datetime.fromtimestamp(int(stamp), tz=timezone.utc).date()
                close = float(value)
            except (TypeError, ValueError, OSError):
                continue
            if row_date <= report_date and close > 0:
                rows.append({"date": row_date.isoformat(), "close": close})
    return sorted(rows, key=lambda row: row["date"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-date", default="2026-08-03")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report_date = date.fromisoformat(args.report_date)
    min_date = report_date - timedelta(days=10)
    period_from = int(datetime.combine(min_date, datetime.min.time(), tzinfo=timezone.utc).timestamp())
    period_to = int(datetime.combine(report_date + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc).timestamp())

    results: list[dict[str, Any]] = []
    for line in LINES:
        price_history = get_json(
            "/v1/data/price_history",
            {
                "limit": 50,
                "offset": 0,
                "isin": line["isin"],
                "mic": line["mic"],
                "minDate": min_date.isoformat(),
                "maxDate": report_date.isoformat(),
                "cleanSplit": "false",
                "cleanPayout": "false",
                "cleanSubscriptionRights": "false",
            },
        )
        tradingview = get_json(
            "/v1/tradingview/lightweight/history/single",
            {
                "resolution": "D",
                "isKeepResolutionForLatestWeeksIfPossible": "false",
                "from": period_from,
                "to": period_to,
                "isBidAskPrice": "false",
                "symbols": f"{line['mic']}:{line['isin']}",
            },
        )
        info = get_json(
            "/v1/data/price_information/single",
            {"isin": line["isin"], "mic": line["mic"]},
        )
        history_rows = normalize_price_history(price_history.get("payload"), report_date)
        tv_rows = normalize_tradingview(tradingview.get("payload"), report_date)
        selected_rows = history_rows or tv_rows
        selected = selected_rows[-1] if selected_rows else None
        for attempt in (price_history, tradingview, info):
            attempt.pop("payload", None)
        results.append(
            {
                **line,
                "requested_report_date": report_date.isoformat(),
                "price_history": price_history,
                "tradingview": tradingview,
                "price_information": info,
                "history_row_count": len(history_rows),
                "tradingview_row_count": len(tv_rows),
                "selected_completed_close": selected,
                "usable_completed_close": selected is not None,
            }
        )

    payload = {
        "schema_version": "boerse_frankfurt_connectivity_probe_v2",
        "generated_at_utc": utc_now().replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "report_date": report_date.isoformat(),
        "line_count": len(results),
        "usable_line_count": sum(bool(row["usable_completed_close"]) for row in results),
        "all_lines_usable": all(bool(row["usable_completed_close"]) for row in results),
        "portfolio_mutation": False,
        "funding_authority": False,
        "delivery_authority": False,
        "results": results,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "BOERSE_FRANKFURT_CONNECTIVITY_PROBE_OK"
        f" | usable={payload['usable_line_count']}/{payload['line_count']}"
        f" | output={output}"
    )


if __name__ == "__main__":
    main()
