from __future__ import annotations

import csv
import io
import json
import math
import os
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Any, Callable
from urllib.parse import quote

import requests


USER_AGENT = "Weekly-ETF-EU/1.0 completed-close qualification"
TIMEOUT_SECONDS = 30


@dataclass
class ProviderResult:
    provider_id: str
    provider_symbol: str
    requested_report_date: str
    pricing_status: str = "fetch_failed"
    close_date: str | None = None
    close_price: float | None = None
    currency: str | None = None
    exchange_or_mic: str | None = None
    http_status: int | None = None
    response_classification: str = "not_attempted"
    observed_at_utc: str | None = None
    blockers: list[str] | None = None
    secret_configured: bool = False

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["blockers"] = sorted(set(self.blockers or []))
        return payload


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def usable_close(value: Any) -> float | None:
    try:
        close = float(value)
    except (TypeError, ValueError):
        return None
    return close if math.isfinite(close) and close > 0 else None


def normalize_date(value: Any) -> date | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.isdigit() and len(text) >= 10:
        try:
            return datetime.fromtimestamp(int(text[:10]), tz=timezone.utc).date()
        except (OverflowError, OSError, ValueError):
            return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def latest_completed(rows: list[tuple[date, float]], report_date: date) -> tuple[date, float] | None:
    accepted = [(row_date, close) for row_date, close in rows if row_date <= report_date and close > 0]
    return max(accepted, key=lambda item: item[0]) if accepted else None


def result_base(provider_id: str, symbol: str, report_date: date, *, secret_configured: bool) -> ProviderResult:
    return ProviderResult(
        provider_id=provider_id,
        provider_symbol=symbol,
        requested_report_date=report_date.isoformat(),
        observed_at_utc=utc_now(),
        blockers=[],
        secret_configured=secret_configured,
    )


def request_json(
    url: str,
    *,
    params: dict[str, Any],
    session: requests.Session | None = None,
) -> tuple[requests.Response | None, Any, str | None]:
    client = session or requests
    try:
        response = client.get(
            url,
            params=params,
            timeout=TIMEOUT_SECONDS,
            headers={"User-Agent": USER_AGENT, "Accept": "application/json,text/csv,text/plain,*/*"},
        )
    except Exception as exc:  # pragma: no cover - network dependent
        return None, None, f"request_exception:{type(exc).__name__}"
    try:
        payload = response.json()
    except Exception:
        payload = None
    return response, payload, None


def mark_skip(result: ProviderResult, blocker: str) -> ProviderResult:
    result.pricing_status = "provider_skipped"
    result.response_classification = "missing_secret"
    result.blockers = [blocker]
    return result


def mark_http(result: ProviderResult, response: requests.Response | None, error: str | None) -> bool:
    if error:
        result.response_classification = "request_exception"
        result.blockers = [error]
        return False
    assert response is not None
    result.http_status = response.status_code
    if response.status_code != 200:
        result.response_classification = "http_error"
        result.blockers = [f"http_status:{response.status_code}"]
        return False
    return True


def finalize_rows(result: ProviderResult, rows: list[tuple[date, float]], report_date: date) -> ProviderResult:
    selected = latest_completed(rows, report_date)
    if selected is None:
        result.response_classification = "no_usable_completed_close"
        result.blockers = ["no_usable_completed_close_on_or_before_report_date"]
        return result
    close_date, close = selected
    result.pricing_status = "priced_non_authoritative"
    result.close_date = close_date.isoformat()
    result.close_price = close
    result.response_classification = "valid_completed_close"
    result.blockers = []
    return result


def fetch_leeway(line: dict[str, Any], report_date: date, session: requests.Session | None = None) -> ProviderResult:
    token = os.environ.get("LEEWAY_API_TOKEN", "").strip()
    symbol = str(line.get("provider_symbol_leeway") or "").strip()
    result = result_base("leeway", symbol, report_date, secret_configured=bool(token))
    if not token:
        return mark_skip(result, "missing_secret:LEEWAY_API_TOKEN")
    if not symbol:
        return mark_skip(result, "missing_provider_symbol_leeway")
    url = f"https://api.leeway.tech/api/v1/public/historicalquotes/{quote(symbol)}"
    response, payload, error = request_json(url, params={"apitoken": token}, session=session)
    if not mark_http(result, response, error):
        return result
    if isinstance(payload, dict) and any(key in payload for key in ("error", "message")) and not any(key in payload for key in ("data", "historical")):
        result.response_classification = "provider_error"
        result.blockers = ["leeway_provider_error"]
        return result
    candidates: Any = payload
    if isinstance(payload, dict):
        candidates = payload.get("data") or payload.get("historical") or payload.get("quotes") or []
        result.currency = payload.get("currency")
        result.exchange_or_mic = payload.get("exchange") or payload.get("mic")
    rows: list[tuple[date, float]] = []
    if isinstance(candidates, list):
        for item in candidates:
            if not isinstance(item, dict):
                continue
            row_date = normalize_date(item.get("date") or item.get("datetime") or item.get("timestamp"))
            close = usable_close(item.get("close") or item.get("Close") or item.get("adjusted_close"))
            if row_date and close:
                rows.append((row_date, close))
    return finalize_rows(result, rows, report_date)


def fetch_eodhd(line: dict[str, Any], report_date: date, session: requests.Session | None = None) -> ProviderResult:
    token = os.environ.get("EODHD_API_TOKEN", "").strip()
    symbol = str(line.get("provider_symbol_eodhd") or "").strip()
    result = result_base("eodhd", symbol, report_date, secret_configured=bool(token))
    if not token:
        return mark_skip(result, "missing_secret:EODHD_API_TOKEN")
    if not symbol:
        return mark_skip(result, "missing_provider_symbol_eodhd")
    start = report_date - timedelta(days=40)
    url = f"https://eodhd.com/api/eod/{quote(symbol)}"
    params = {
        "api_token": token,
        "fmt": "json",
        "from": start.isoformat(),
        "to": report_date.isoformat(),
        "period": "d",
        "order": "a",
    }
    response, payload, error = request_json(url, params=params, session=session)
    if not mark_http(result, response, error):
        return result
    if isinstance(payload, dict):
        result.response_classification = "provider_error"
        result.blockers = ["eodhd_provider_error"]
        return result
    rows: list[tuple[date, float]] = []
    if isinstance(payload, list):
        for item in payload:
            if not isinstance(item, dict):
                continue
            row_date = normalize_date(item.get("date"))
            close = usable_close(item.get("close"))
            if row_date and close:
                rows.append((row_date, close))
    return finalize_rows(result, rows, report_date)


def fetch_marketstack(line: dict[str, Any], report_date: date, session: requests.Session | None = None) -> ProviderResult:
    key = os.environ.get("MARKETSTACK_API_KEY", "").strip()
    symbol = str(line.get("provider_symbol_marketstack") or "").strip()
    result = result_base("marketstack", symbol, report_date, secret_configured=bool(key))
    if not key:
        return mark_skip(result, "missing_secret:MARKETSTACK_API_KEY")
    if not symbol:
        return mark_skip(result, "missing_provider_symbol_marketstack")
    start = report_date - timedelta(days=40)
    response, payload, error = request_json(
        "https://api.marketstack.com/v2/eod",
        params={
            "access_key": key,
            "symbols": symbol,
            "date_from": start.isoformat(),
            "date_to": report_date.isoformat(),
            "limit": 100,
        },
        session=session,
    )
    if not mark_http(result, response, error):
        return result
    if isinstance(payload, dict) and payload.get("error"):
        result.response_classification = "provider_error"
        result.blockers = ["marketstack_provider_error"]
        return result
    candidates = payload.get("data", []) if isinstance(payload, dict) else []
    rows: list[tuple[date, float]] = []
    for item in candidates if isinstance(candidates, list) else []:
        if not isinstance(item, dict):
            continue
        row_date = normalize_date(item.get("date"))
        close = usable_close(item.get("close") or item.get("adj_close"))
        if row_date and close:
            rows.append((row_date, close))
        result.currency = result.currency or item.get("currency")
        result.exchange_or_mic = result.exchange_or_mic or item.get("exchange") or item.get("mic")
    return finalize_rows(result, rows, report_date)


def fetch_alpha_vantage(line: dict[str, Any], report_date: date, session: requests.Session | None = None) -> ProviderResult:
    key = os.environ.get("ALPHA_VANTAGE_API_KEY", "").strip()
    symbol = str(line.get("provider_symbol_alpha_vantage") or "").strip()
    result = result_base("alpha_vantage", symbol, report_date, secret_configured=bool(key))
    if not key:
        return mark_skip(result, "missing_secret:ALPHA_VANTAGE_API_KEY")
    if not symbol:
        return mark_skip(result, "missing_provider_symbol_alpha_vantage")
    client = session or requests
    try:
        response = client.get(
            "https://www.alphavantage.co/query",
            params={
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "outputsize": "compact",
                "datatype": "csv",
                "apikey": key,
            },
            timeout=TIMEOUT_SECONDS,
            headers={"User-Agent": USER_AGENT, "Accept": "text/csv,text/plain,*/*"},
        )
    except Exception as exc:  # pragma: no cover
        result.response_classification = "request_exception"
        result.blockers = [f"request_exception:{type(exc).__name__}"]
        return result
    result.http_status = response.status_code
    if response.status_code != 200:
        result.response_classification = "http_error"
        result.blockers = [f"http_status:{response.status_code}"]
        return result
    text = response.text.strip()
    if text.startswith("{"):
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            payload = {}
        result.response_classification = "provider_notice_or_error"
        result.blockers = ["alpha_vantage_notice_or_error"]
        if isinstance(payload, dict) and "Note" in payload:
            result.blockers.append("alpha_vantage_rate_limit")
        return result
    try:
        rows_csv = list(csv.DictReader(io.StringIO(text)))
    except Exception as exc:
        result.response_classification = "csv_parse_error"
        result.blockers = [f"csv_parse_error:{type(exc).__name__}"]
        return result
    rows: list[tuple[date, float]] = []
    for item in rows_csv:
        row_date = normalize_date(item.get("timestamp") or item.get("date"))
        close = usable_close(item.get("close"))
        if row_date and close:
            rows.append((row_date, close))
    return finalize_rows(result, rows, report_date)


def fetch_yahoo_chart(line: dict[str, Any], report_date: date, session: requests.Session | None = None) -> ProviderResult:
    symbol = str(line.get("provider_symbol_yahoo") or "").strip()
    result = result_base("yahoo_chart", symbol, report_date, secret_configured=True)
    if not symbol:
        return mark_skip(result, "missing_provider_symbol_yahoo")
    start = report_date - timedelta(days=45)
    period1 = int(datetime.combine(start, datetime.min.time(), tzinfo=timezone.utc).timestamp())
    period2 = int(datetime.combine(report_date + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc).timestamp())
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{quote(symbol)}"
    response, payload, error = request_json(
        url,
        params={
            "period1": period1,
            "period2": period2,
            "interval": "1d",
            "events": "history",
            "includeAdjustedClose": "true",
        },
        session=session,
    )
    if not mark_http(result, response, error):
        if result.http_status == 429:
            result.response_classification = "rate_limited"
            result.blockers = ["yahoo_chart_rate_limited"]
        return result
    chart = payload.get("chart", {}) if isinstance(payload, dict) else {}
    if chart.get("error"):
        result.response_classification = "provider_error"
        result.blockers = ["yahoo_chart_provider_error"]
        return result
    results = chart.get("result") or []
    if not results:
        result.response_classification = "empty_result"
        result.blockers = ["yahoo_chart_empty_result"]
        return result
    data = results[0]
    meta = data.get("meta") or {}
    result.currency = meta.get("currency")
    result.exchange_or_mic = meta.get("exchangeName") or meta.get("fullExchangeName")
    timestamps = data.get("timestamp") or []
    indicators = data.get("indicators") or {}
    quote_rows = indicators.get("quote") or []
    closes = quote_rows[0].get("close", []) if quote_rows else []
    rows: list[tuple[date, float]] = []
    for stamp, raw_close in zip(timestamps, closes):
        row_date = normalize_date(stamp)
        close = usable_close(raw_close)
        if row_date and close:
            rows.append((row_date, close))
    return finalize_rows(result, rows, report_date)


PROVIDERS: tuple[tuple[str, Callable[[dict[str, Any], date, requests.Session | None], ProviderResult]], ...] = (
    ("leeway", fetch_leeway),
    ("eodhd", fetch_eodhd),
    ("marketstack", fetch_marketstack),
    ("alpha_vantage", fetch_alpha_vantage),
    ("yahoo_chart", fetch_yahoo_chart),
)


def qualify_line(line: dict[str, Any], report_date: date, session: requests.Session | None = None) -> dict[str, Any]:
    attempts = [fetcher(line, report_date, session) for _, fetcher in PROVIDERS]
    priced = [attempt for attempt in attempts if attempt.pricing_status == "priced_non_authoritative"]
    selected = priced[0] if priced else None
    agreement: dict[str, Any] = {
        "successful_provider_count": len(priced),
        "comparison_available": len(priced) >= 2,
        "max_close_spread_pct": None,
    }
    if len(priced) >= 2:
        values = [float(item.close_price) for item in priced if item.close_price is not None]
        if values and min(values) > 0:
            agreement["max_close_spread_pct"] = round((max(values) - min(values)) / min(values) * 100.0, 6)
    return {
        "basket_id": line.get("basket_id"),
        "fund_name": line.get("fund_name"),
        "isin": line.get("isin"),
        "ticker": line.get("ticker"),
        "exchange": line.get("exchange"),
        "venue_code": line.get("venue_code"),
        "expected_currency": line.get("currency"),
        "verification_status": line.get("verification_status"),
        "selected_provider": selected.provider_id if selected else None,
        "selected_symbol": selected.provider_symbol if selected else None,
        "selected_close_date": selected.close_date if selected else None,
        "selected_close_price": selected.close_price if selected else None,
        "pricing_status": "priced_non_authoritative" if selected else "fetch_failed",
        "agreement": agreement,
        "provider_attempts": [attempt.to_dict() for attempt in attempts],
        "valuation_grade": False,
        "funding_authority": False,
    }
