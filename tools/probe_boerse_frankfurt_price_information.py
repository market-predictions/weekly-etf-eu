from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date, datetime, timezone
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
SAFE_FIELDS = (
    "isin",
    "mic",
    "currency",
    "lastPrice",
    "lastPriceIndicator",
    "timestampLastPrice",
    "closingPricePrevTradingDay",
    "changeToPrevDayAbsolute",
    "changeToPrevDayInPercent",
    "dayHigh",
    "dayLow",
    "turnoverInEur",
    "turnoverInPieces",
    "minimumTradableUnit",
    "tradingTimeStart",
    "tradingTimeEnd",
    "priceFixings",
)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def headers_for(url: str) -> dict[str, str]:
    current = now_utc()
    client_date = current.isoformat(timespec="milliseconds").replace("+00:00", "Z")
    trace_id = hashlib.md5((client_date + url + TRACE_SALT).encode("utf-8")).hexdigest()
    local_minute = datetime.now().astimezone().strftime("%Y%m%d%H%M")
    security = hashlib.md5(local_minute.encode("utf-8")).hexdigest()
    return {
        "Accept": "application/json, text/plain, */*",
        "Client-Date": client_date,
        "X-Client-TraceId": trace_id,
        "X-Security": security,
        "Referer": "https://www.boerse-frankfurt.de/",
        "User-Agent": "Mozilla/5.0 Weekly-ETF-EU-Exchange-Probe/1.0",
    }


def fetch_information(line: dict[str, str]) -> dict[str, Any]:
    params = {"isin": line["isin"], "mic": line["mic"]}
    url = f"{BASE_URL}/v1/data/price_information/single?{urlencode(params)}"
    observed = now_utc().replace(microsecond=0).isoformat().replace("+00:00", "Z")
    try:
        response = requests.get(url, headers=headers_for(url), timeout=TIMEOUT_SECONDS)
    except Exception as exc:
        return {"status": "request_exception", "exception_type": type(exc).__name__, "observed_at_utc": observed}
    result: dict[str, Any] = {
        "status": "http_error" if response.status_code != 200 else "json_response",
        "http_status": response.status_code,
        "content_type": response.headers.get("content-type"),
        "response_bytes": len(response.content),
        "observed_at_utc": observed,
    }
    try:
        payload = response.json()
    except ValueError:
        result["status"] = "non_json_response"
        result["response_sha256"] = hashlib.sha256(response.content).hexdigest()
        return result
    if not isinstance(payload, dict):
        result["status"] = "unexpected_payload_type"
        result["payload_type"] = type(payload).__name__
        return result
    result["data"] = {field: payload.get(field) for field in SAFE_FIELDS if field in payload}
    return result


def parse_timestamp_date(value: Any) -> date | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return date.fromisoformat(text[:10])
        except ValueError:
            return None


def positive_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-date", default="2026-08-03")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report_date = date.fromisoformat(args.report_date)

    rows: list[dict[str, Any]] = []
    for line in LINES:
        attempt = fetch_information(line)
        data = attempt.get("data") if isinstance(attempt.get("data"), dict) else {}
        returned_isin = str(data.get("isin") or "").upper()
        returned_mic = str(data.get("mic") or "").upper()
        returned_currency = str(data.get("currency") or "").upper()
        timestamp_date = parse_timestamp_date(data.get("timestampLastPrice"))
        last_price = positive_float(data.get("lastPrice"))
        identity_match = (
            returned_isin == line["isin"]
            and returned_mic == line["mic"]
            and returned_currency == line["currency"]
        )
        report_date_last_price = timestamp_date == report_date and last_price is not None
        rows.append(
            {
                **line,
                "attempt": attempt,
                "identity_match": identity_match,
                "last_price_date": timestamp_date.isoformat() if timestamp_date else None,
                "last_price": last_price,
                "last_price_indicator": data.get("lastPriceIndicator"),
                "closing_price_previous_trading_day": positive_float(data.get("closingPricePrevTradingDay")),
                "turnover_eur": positive_float(data.get("turnoverInEur")),
                "turnover_pieces": positive_float(data.get("turnoverInPieces")),
                "report_date_last_price_available": report_date_last_price,
                "post_close_qualification_pending": report_date_last_price,
            }
        )

    payload = {
        "schema_version": "boerse_frankfurt_price_information_probe_v1",
        "generated_at_utc": now_utc().replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "report_date": report_date.isoformat(),
        "line_count": len(rows),
        "identity_match_count": sum(bool(row["identity_match"]) for row in rows),
        "report_date_last_price_count": sum(bool(row["report_date_last_price_available"]) for row in rows),
        "portfolio_mutation": False,
        "funding_authority": False,
        "delivery_authority": False,
        "rows": rows,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "BOERSE_FRANKFURT_PRICE_INFORMATION_PROBE_OK"
        f" | identity={payload['identity_match_count']}/{payload['line_count']}"
        f" | report_date_prices={payload['report_date_last_price_count']}/{payload['line_count']}"
        f" | output={output}"
    )


if __name__ == "__main__":
    main()
