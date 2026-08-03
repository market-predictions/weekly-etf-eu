from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlencode
from zoneinfo import ZoneInfo

import requests

BASE_URL = "https://api.boerse-frankfurt.de"
TRACE_SALT = "w4icATTGtnjAQMbkL3kJwxLfEAKDa3VU"
TIMEOUT_SECONDS = 30
BERLIN = ZoneInfo("Europe/Berlin")
LINES = [
    {"ticker": "VWCE", "isin": "IE00BK5BQT80", "mic": "XETR", "currency": "EUR", "yahoo_symbol": "VWCE.DE"},
    {"ticker": "EUNA", "isin": "IE00BDBRDM35", "mic": "XETR", "currency": "EUR", "yahoo_symbol": "EUNA.DE"},
    {"ticker": "SXR8", "isin": "IE00B5BMR087", "mic": "XETR", "currency": "EUR", "yahoo_symbol": "SXR8.DE"},
    {"ticker": "VVSM", "isin": "IE00BMC38736", "mic": "XETR", "currency": "EUR", "yahoo_symbol": "VVSM.DE"},
    {"ticker": "L0CK", "isin": "IE00BG0J4C88", "mic": "XETR", "currency": "EUR", "yahoo_symbol": "L0CK.DE"},
]


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def positive_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def currency_code(value: Any) -> str | None:
    if isinstance(value, dict):
        value = value.get("originalValue")
    text = str(value or "").strip().upper()
    return text or None


def boerse_headers(url: str) -> dict[str, str]:
    current = now_utc()
    client_date = current.isoformat(timespec="milliseconds").replace("+00:00", "Z")
    trace_id = hashlib.md5((client_date + url + TRACE_SALT).encode("utf-8")).hexdigest()
    security = hashlib.md5(datetime.now().astimezone().strftime("%Y%m%d%H%M").encode("utf-8")).hexdigest()
    return {
        "Accept": "application/json, text/plain, */*",
        "Client-Date": client_date,
        "X-Client-TraceId": trace_id,
        "X-Security": security,
        "Referer": "https://www.boerse-frankfurt.de/",
        "User-Agent": "Mozilla/5.0 Weekly-ETF-EU-Close-Agreement-Probe/1.0",
    }


def fetch_boerse(line: dict[str, str], report_date: date) -> dict[str, Any]:
    url = f"{BASE_URL}/v1/data/price_information/single?{urlencode({'isin': line['isin'], 'mic': line['mic']})}"
    observed_at = now_utc()
    try:
        response = requests.get(url, headers=boerse_headers(url), timeout=TIMEOUT_SECONDS)
        payload = response.json()
    except Exception as exc:
        return {"status": "request_failed", "error_class": type(exc).__name__}
    if response.status_code != 200 or not isinstance(payload, dict):
        return {"status": "provider_error", "http_status": response.status_code}
    timestamp_text = str(payload.get("timestampLastPrice") or "").strip()
    try:
        last_timestamp = datetime.fromisoformat(timestamp_text.replace("Z", "+00:00"))
    except ValueError:
        last_timestamp = None
    end_text = str(payload.get("tradingTimeEnd") or "22:00:00")
    try:
        end_time = time.fromisoformat(end_text)
    except ValueError:
        end_time = time(22, 0)
    session_end = datetime.combine(report_date, end_time, tzinfo=BERLIN)
    after_session = observed_at >= session_end.astimezone(timezone.utc)
    last_date = last_timestamp.astimezone(BERLIN).date() if last_timestamp else None
    returned_currency = currency_code(payload.get("currency"))
    identity_match = (
        str(payload.get("isin") or "").upper() == line["isin"]
        and str(payload.get("mic") or "").upper() == line["mic"]
        and returned_currency == line["currency"]
    )
    last_price = positive_float(payload.get("lastPrice"))
    completed_session_candidate = bool(
        after_session and last_date == report_date and last_price is not None and identity_match
    )
    return {
        "status": "priced" if completed_session_candidate else "not_completed_or_identity_failed",
        "provider": "boerse_frankfurt_xetra",
        "provider_symbol": f"{line['mic']}:{line['isin']}",
        "returned_symbol": f"{payload.get('mic')}:{payload.get('isin')}",
        "returned_isin": payload.get("isin"),
        "returned_mic": payload.get("mic"),
        "returned_currency": returned_currency,
        "identity_match": identity_match,
        "close_date": last_date.isoformat() if last_date else None,
        "close_price": last_price,
        "last_price_indicator": payload.get("lastPriceIndicator"),
        "last_price_timestamp": timestamp_text or None,
        "observed_at_utc": observed_at.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "trading_time_end": end_text,
        "observed_after_session_end": after_session,
        "completed_session_candidate": completed_session_candidate,
        "turnover_eur": positive_float(payload.get("turnoverInEur")),
        "turnover_pieces": positive_float(payload.get("turnoverInPieces")),
        "price_fixings": payload.get("priceFixings"),
        "previous_trading_day_close": positive_float(payload.get("closingPricePrevTradingDay")),
    }


def fetch_yahoo(line: dict[str, str], report_date: date) -> dict[str, Any]:
    start = report_date - timedelta(days=10)
    period1 = int(datetime.combine(start, time.min, tzinfo=timezone.utc).timestamp())
    period2 = int(datetime.combine(report_date + timedelta(days=1), time.min, tzinfo=timezone.utc).timestamp())
    symbol = line["yahoo_symbol"]
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{quote(symbol)}"
    params = {
        "period1": period1,
        "period2": period2,
        "interval": "1d",
        "events": "history",
        "includeAdjustedClose": "true",
    }
    try:
        response = requests.get(url, params=params, timeout=TIMEOUT_SECONDS, headers={"User-Agent": "Weekly-ETF-EU/1.0"})
        payload = response.json()
    except Exception as exc:
        return {"status": "request_failed", "error_class": type(exc).__name__}
    chart = payload.get("chart", {}) if isinstance(payload, dict) else {}
    results = chart.get("result") or []
    if response.status_code != 200 or not results:
        return {"status": "provider_error", "http_status": response.status_code}
    data = results[0]
    meta = data.get("meta") or {}
    timestamps = data.get("timestamp") or []
    quote_rows = (data.get("indicators") or {}).get("quote") or []
    closes = quote_rows[0].get("close", []) if quote_rows else []
    candidates: list[tuple[date, float]] = []
    for stamp, raw_close in zip(timestamps, closes):
        try:
            row_date = datetime.fromtimestamp(int(stamp), tz=timezone.utc).astimezone(BERLIN).date()
        except (TypeError, ValueError, OSError):
            continue
        close = positive_float(raw_close)
        if close is not None and row_date <= report_date:
            candidates.append((row_date, close))
    if not candidates:
        return {"status": "no_close"}
    close_date, close_price = max(candidates, key=lambda item: item[0])
    returned_currency = str(meta.get("currency") or "").upper() or None
    venue = str(meta.get("exchangeName") or meta.get("fullExchangeName") or "")
    identity_match = returned_currency == line["currency"] and "GER" in venue.upper()
    return {
        "status": "priced",
        "provider": "yahoo_chart",
        "provider_symbol": symbol,
        "returned_symbol": meta.get("symbol") or symbol,
        "returned_currency": returned_currency,
        "returned_venue": venue,
        "identity_match": identity_match,
        "close_date": close_date.isoformat(),
        "close_price": close_price,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-date", default="2026-08-03")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report_date = date.fromisoformat(args.report_date)
    rows: list[dict[str, Any]] = []
    for line in LINES:
        boerse = fetch_boerse(line, report_date)
        yahoo = fetch_yahoo(line, report_date)
        same_date = boerse.get("close_date") == yahoo.get("close_date") == report_date.isoformat()
        values = [positive_float(boerse.get("close_price")), positive_float(yahoo.get("close_price"))]
        spread_pct = None
        if same_date and all(value is not None for value in values):
            low, high = min(values), max(values)
            spread_pct = ((high - low) / low) * 100 if low else None
        agreement_pass = bool(
            boerse.get("status") == "priced"
            and yahoo.get("status") == "priced"
            and same_date
            and spread_pct is not None
            and spread_pct <= 1.0
            and boerse.get("identity_match")
            and yahoo.get("identity_match")
        )
        consensus = sum(values) / 2 if agreement_pass else None
        rows.append(
            {
                **line,
                "boerse_frankfurt": boerse,
                "yahoo_chart": yahoo,
                "same_report_date": same_date,
                "spread_pct": spread_pct,
                "agreement_pass": agreement_pass,
                "consensus_close": consensus,
            }
        )
    payload = {
        "schema_version": "yahoo_boerse_close_agreement_probe_v1",
        "generated_at_utc": now_utc().replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "report_date": report_date.isoformat(),
        "line_count": len(rows),
        "agreement_pass_count": sum(bool(row["agreement_pass"]) for row in rows),
        "all_lines_pass": all(bool(row["agreement_pass"]) for row in rows),
        "authority": "development_technical_probe_only",
        "commercial_redistribution_authority": False,
        "portfolio_mutation": False,
        "delivery_authority": False,
        "rows": rows,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "YAHOO_BOERSE_CLOSE_AGREEMENT_PROBE_OK"
        f" | passed={payload['agreement_pass_count']}/{payload['line_count']}"
        f" | output={output}"
    )


if __name__ == "__main__":
    main()
