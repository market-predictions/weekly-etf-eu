from __future__ import annotations

import argparse
import json
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote
from zoneinfo import ZoneInfo

import requests

BERLIN = ZoneInfo("Europe/Berlin")
TIMEOUT_SECONDS = 30
LINES = [
    {"ticker": "VWCE", "symbol": "VWCE.DE", "currency": "EUR"},
    {"ticker": "EUNA", "symbol": "EUNA.DE", "currency": "EUR"},
    {"ticker": "SXR8", "symbol": "SXR8.DE", "currency": "EUR"},
    {"ticker": "VVSM", "symbol": "VVSM.DE", "currency": "EUR"},
    {"ticker": "L0CK", "symbol": "L0CK.DE", "currency": "EUR"},
]
SAFE_META_FIELDS = (
    "currency",
    "symbol",
    "exchangeName",
    "fullExchangeName",
    "instrumentType",
    "firstTradeDate",
    "regularMarketTime",
    "regularMarketPrice",
    "chartPreviousClose",
    "previousClose",
    "marketState",
    "exchangeTimezoneName",
    "gmtoffset",
    "dataGranularity",
    "range",
    "validRanges",
    "currentTradingPeriod",
)


def positive_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def timestamp_date(value: Any) -> str | None:
    try:
        stamp = int(value)
    except (TypeError, ValueError):
        return None
    return datetime.fromtimestamp(stamp, tz=timezone.utc).astimezone(BERLIN).date().isoformat()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-date", default="2026-08-03")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report_date = date.fromisoformat(args.report_date)
    start = report_date - timedelta(days=10)
    period1 = int(datetime.combine(start, time.min, tzinfo=timezone.utc).timestamp())
    period2 = int(datetime.combine(report_date + timedelta(days=2), time.min, tzinfo=timezone.utc).timestamp())

    rows: list[dict[str, Any]] = []
    for line in LINES:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{quote(line['symbol'])}"
        params = {
            "period1": period1,
            "period2": period2,
            "interval": "1d",
            "events": "history",
            "includeAdjustedClose": "true",
        }
        try:
            response = requests.get(
                url,
                params=params,
                timeout=TIMEOUT_SECONDS,
                headers={"User-Agent": "Weekly-ETF-EU/1.0"},
            )
            payload = response.json()
        except Exception as exc:
            rows.append({**line, "status": "request_failed", "error_class": type(exc).__name__})
            continue
        chart = payload.get("chart", {}) if isinstance(payload, dict) else {}
        results = chart.get("result") or []
        if response.status_code != 200 or not results:
            rows.append({**line, "status": "provider_error", "http_status": response.status_code})
            continue
        data = results[0]
        meta = data.get("meta") or {}
        timestamps = data.get("timestamp") or []
        quote_rows = (data.get("indicators") or {}).get("quote") or []
        closes = quote_rows[0].get("close", []) if quote_rows else []
        daily_rows: list[dict[str, Any]] = []
        for stamp, raw_close in zip(timestamps, closes):
            close = positive_float(raw_close)
            if close is None:
                continue
            row_date = datetime.fromtimestamp(int(stamp), tz=timezone.utc).astimezone(BERLIN).date()
            daily_rows.append({"date": row_date.isoformat(), "close": close, "timestamp": int(stamp)})
        safe_meta = {field: meta.get(field) for field in SAFE_META_FIELDS if field in meta}
        regular_time = meta.get("regularMarketTime")
        regular_price = positive_float(meta.get("regularMarketPrice"))
        regular_date = timestamp_date(regular_time)
        current_period = meta.get("currentTradingPeriod") if isinstance(meta.get("currentTradingPeriod"), dict) else {}
        regular_period = current_period.get("regular") if isinstance(current_period.get("regular"), dict) else {}
        regular_end = regular_period.get("end")
        observed_at = datetime.now(timezone.utc)
        observed_after_regular_end = False
        try:
            observed_after_regular_end = observed_at.timestamp() >= int(regular_end)
        except (TypeError, ValueError):
            pass
        rows.append(
            {
                **line,
                "status": "json_response",
                "http_status": response.status_code,
                "meta": safe_meta,
                "daily_rows": daily_rows,
                "latest_daily_row": daily_rows[-1] if daily_rows else None,
                "regular_market_date": regular_date,
                "regular_market_price": regular_price,
                "market_state": meta.get("marketState"),
                "regular_period_end": regular_end,
                "observed_after_regular_end": observed_after_regular_end,
                "report_date_regular_market_candidate": bool(
                    regular_date == report_date.isoformat()
                    and regular_price is not None
                    and observed_after_regular_end
                ),
            }
        )

    payload = {
        "schema_version": "yahoo_regular_market_metadata_probe_v1",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "report_date": report_date.isoformat(),
        "line_count": len(rows),
        "report_date_candidate_count": sum(bool(row.get("report_date_regular_market_candidate")) for row in rows),
        "portfolio_mutation": False,
        "funding_authority": False,
        "delivery_authority": False,
        "rows": rows,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "YAHOO_REGULAR_MARKET_METADATA_PROBE_OK"
        f" | candidates={payload['report_date_candidate_count']}/{payload['line_count']}"
        f" | output={output}"
    )


if __name__ == "__main__":
    main()
