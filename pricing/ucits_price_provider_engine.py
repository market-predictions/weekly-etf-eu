from __future__ import annotations

import json
import math
import os
import time
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from statistics import median
from typing import Any, Iterable, Mapping
from urllib.parse import quote

import requests
import yaml

USER_AGENT = "Weekly-ETF-EU-Price-Qualification/1.0"
DEFAULT_TIMEOUT_SECONDS = 25
DEFAULT_MAX_CLOSE_AGE_DAYS = 7
DEFAULT_AGREEMENT_TOLERANCE_PCT = 1.0

PROVIDER_SECRET_ENVS = {
    "leeway": "LEEWAY_API_TOKEN",
    "eodhd": "EODHD_API_TOKEN",
    "marketstack": "MARKETSTACK_ACCESS_KEY",
    "alpha_vantage": "ALPHA_VANTAGE_API_KEY",
    "yahoo_chart": None,
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _text(value: Any) -> str:
    return str(value or "").strip()


def _float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number) or number <= 0:
        return None
    return number


def _date(value: Any) -> date | None:
    raw = _text(value)
    if not raw:
        return None
    raw = raw[:10]
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def _records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [dict(row) for row in payload if isinstance(row, Mapping)]
    if not isinstance(payload, Mapping):
        return []
    for key in ("data", "values", "results", "historical", "historicalquotes", "eod"):
        value = payload.get(key)
        if isinstance(value, list):
            return [dict(row) for row in value if isinstance(row, Mapping)]
        if isinstance(value, Mapping):
            nested = _records(value)
            if nested:
                return nested
    dated: list[dict[str, Any]] = []
    for key, value in payload.items():
        if _date(key) and isinstance(value, Mapping):
            row = dict(value)
            row.setdefault("date", key)
            dated.append(row)
    return dated


def _latest_close(
    rows: Iterable[Mapping[str, Any]],
    report_date: date,
    *,
    date_fields: tuple[str, ...] = ("date", "datetime", "timestamp"),
    close_fields: tuple[str, ...] = ("close", "adjusted_close", "adjustedClose", "adj_close"),
) -> tuple[date, float, dict[str, Any]] | None:
    accepted: list[tuple[date, float, dict[str, Any]]] = []
    for source_row in rows:
        row = dict(source_row)
        row_date = next((_date(row.get(field)) for field in date_fields if _date(row.get(field))), None)
        if row_date is None or row_date > report_date:
            continue
        close_value = next((_float(row.get(field)) for field in close_fields if _float(row.get(field)) is not None), None)
        if close_value is None:
            continue
        accepted.append((row_date, close_value, row))
    return max(accepted, key=lambda item: item[0]) if accepted else None


@dataclass(frozen=True)
class InstrumentLine:
    basket_id: str
    fund_name: str
    isin: str
    instrument_type: str
    exchange: str
    venue_code: str
    ticker: str
    currency: str
    funded: bool
    provider_symbols: dict[str, str]
    provider_exchange_codes: dict[str, str]


@dataclass
class ProviderResult:
    basket_id: str
    provider: str
    configured: bool
    provider_symbol: str
    expected_isin: str
    expected_venue_code: str
    expected_currency: str
    requested_report_date: str
    pricing_status: str = "not_attempted"
    close_date: str | None = None
    close_price: float | None = None
    close_age_days: int | None = None
    identity_status: str = "not_checked"
    identity_evidence: list[dict[str, Any]] | None = None
    returned_symbol: str | None = None
    returned_exchange: str | None = None
    returned_mic: str | None = None
    returned_currency: str | None = None
    venue_match: bool | None = None
    currency_match: bool | None = None
    http_status: int | None = None
    observed_at_utc: str | None = None
    blockers: list[str] | None = None

    def __post_init__(self) -> None:
        if self.identity_evidence is None:
            self.identity_evidence = []
        if self.blockers is None:
            self.blockers = []
        if self.observed_at_utc is None:
            self.observed_at_utc = utc_now()


class ProviderAdapter:
    name = "base"
    secret_env: str | None = None

    def __init__(self, *, session: requests.Session | None = None) -> None:
        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json,text/plain,*/*"})
        self.api_key = _text(os.environ.get(self.secret_env)) if self.secret_env else ""

    @property
    def configured(self) -> bool:
        return self.secret_env is None or bool(self.api_key)

    def base_result(self, line: InstrumentLine, report_date: date) -> ProviderResult:
        return ProviderResult(
            basket_id=line.basket_id,
            provider=self.name,
            configured=self.configured,
            provider_symbol=line.provider_symbols.get(self.name, ""),
            expected_isin=line.isin,
            expected_venue_code=line.venue_code,
            expected_currency=line.currency,
            requested_report_date=report_date.isoformat(),
        )

    def discover(self, line: InstrumentLine, report_date: date) -> ProviderResult:
        result = self.base_result(line, report_date)
        if not self.configured:
            result.identity_status = "not_configured"
            result.blockers.append(f"missing_secret:{self.secret_env}")
        else:
            result.identity_status = "registry_declared_exact_line"
        return result

    def bulk_discover(self, lines: list[InstrumentLine], report_date: date) -> dict[str, ProviderResult]:
        return {line.basket_id: self.discover(line, report_date) for line in lines}

    def fetch_close(self, line: InstrumentLine, report_date: date) -> ProviderResult:
        raise NotImplementedError

    def _get_json(self, url: str, *, params: dict[str, Any]) -> tuple[int | None, Any, list[str]]:
        try:
            response = self.session.get(url, params=params, timeout=DEFAULT_TIMEOUT_SECONDS)
        except Exception as exc:
            return None, None, [f"request_exception:{type(exc).__name__}"]
        status = int(response.status_code)
        if status != 200:
            token = "rate_limited" if status == 429 else "http_error"
            return status, None, [f"{token}:{status}"]
        try:
            return status, response.json(), []
        except ValueError:
            return status, None, ["non_json_response"]

    def _finalize_close(
        self,
        result: ProviderResult,
        report_date: date,
        latest: tuple[date, float, dict[str, Any]] | None,
        *,
        source_row: dict[str, Any] | None = None,
    ) -> ProviderResult:
        if latest is None:
            result.pricing_status = "fetch_failed"
            result.blockers.append("no_usable_completed_close_on_or_before_report_date")
            return result
        close_date, close_price, raw_row = latest
        row = source_row or raw_row
        result.pricing_status = "priced"
        result.close_date = close_date.isoformat()
        result.close_price = round(close_price, 8)
        result.close_age_days = (report_date - close_date).days
        result.returned_symbol = _text(row.get("symbol") or row.get("code") or result.provider_symbol) or None
        result.returned_exchange = _text(row.get("exchange") or row.get("exchange_code") or row.get("exchange_short_name")) or None
        result.returned_mic = _text(row.get("mic") or row.get("mic_code")) or None
        result.returned_currency = _text(row.get("currency")) or None
        result.venue_match = _venue_match(result, line_expected=result.expected_venue_code)
        result.currency_match = (
            None if result.returned_currency is None else result.returned_currency.upper() == result.expected_currency.upper()
        )
        if result.venue_match is False:
            result.pricing_status = "identity_rejected"
            result.blockers.append("returned_venue_mismatch")
        if result.currency_match is False:
            result.pricing_status = "identity_rejected"
            result.blockers.append("returned_currency_mismatch")
        return result


def _venue_match(result: ProviderResult, *, line_expected: str) -> bool | None:
    observed = {_text(result.returned_mic).upper(), _text(result.returned_exchange).upper()}
    observed.discard("")
    if not observed:
        return None
    expected = line_expected.upper()
    aliases = {
        "XETR": {"XETR", "XETRA", "DEX", "GER", "GERMANY"},
        "XAMS": {"XAMS", "AS", "AMS", "AMSTERDAM", "EURONEXT AMSTERDAM"},
        "XLON": {"XLON", "LSE", "LON", "LONDON", "LONDON STOCK EXCHANGE"},
    }.get(expected, {expected})
    return bool(observed & aliases)


def _match_identity_records(line: InstrumentLine, provider: str, rows: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]]]:
    expected_symbol = line.provider_symbols.get(provider, "").upper()
    expected_exchange = line.provider_exchange_codes.get(provider, "").upper()
    matches: list[dict[str, Any]] = []
    for row in rows:
        blob = " ".join(_text(value) for value in row.values()).upper()
        isin_ok = line.isin.upper() in blob if line.isin else False
        symbol_ok = expected_symbol in blob or expected_symbol.split(".", 1)[0] in blob
        exchange_ok = not expected_exchange or expected_exchange in blob or line.venue_code.upper() in blob
        if isin_ok and symbol_ok and exchange_ok:
            matches.append({key: value for key, value in row.items() if key.lower() not in {"apikey", "api_token", "access_key"}})
    if matches:
        return "api_verified_exact_line", matches[:3]
    if rows:
        return "api_search_no_exact_line_match", rows[:3]
    return "api_search_no_results", []


class LeewayAdapter(ProviderAdapter):
    name = "leeway"
    secret_env = "LEEWAY_API_TOKEN"
    base_url = "https://api.leeway.tech/api/v1/public"

    def bulk_discover(self, lines: list[InstrumentLine], report_date: date) -> dict[str, ProviderResult]:
        if not self.configured:
            return super().bulk_discover(lines, report_date)
        records_by_exchange: dict[str, list[dict[str, Any]]] = {}
        failures: dict[str, list[str]] = {}
        for exchange_code in sorted({line.provider_exchange_codes.get(self.name, "") for line in lines} - {""}):
            status, payload, blockers = self._get_json(
                f"{self.base_url}/general/symbols/{quote(exchange_code)}",
                params={"apitoken": self.api_key},
            )
            records_by_exchange[exchange_code] = _records(payload) if not blockers else []
            failures[exchange_code] = blockers + ([] if status == 200 else [f"http_status:{status}"])
        results: dict[str, ProviderResult] = {}
        for line in lines:
            result = self.base_result(line, report_date)
            exchange_code = line.provider_exchange_codes.get(self.name, "")
            if failures.get(exchange_code):
                result.identity_status = "api_exchange_symbol_list_failed"
                result.blockers.extend(failures[exchange_code])
            else:
                result.identity_status, result.identity_evidence = _match_identity_records(
                    line, self.name, records_by_exchange.get(exchange_code, [])
                )
            results[line.basket_id] = result
        return results

    def discover(self, line: InstrumentLine, report_date: date) -> ProviderResult:
        result = super().discover(line, report_date)
        if not self.configured:
            return result
        status, payload, blockers = self._get_json(
            f"{self.base_url}/general/isin/{quote(line.isin)}", params={"apitoken": self.api_key}
        )
        result.http_status = status
        result.blockers.extend(blockers)
        if blockers:
            result.identity_status = "api_search_failed"
            return result
        identity_status, evidence = _match_identity_records(line, self.name, _records(payload))
        result.identity_status = identity_status
        result.identity_evidence = evidence
        return result

    def fetch_close(self, line: InstrumentLine, report_date: date) -> ProviderResult:
        result = self.base_result(line, report_date)
        if not self.configured:
            result.pricing_status = "not_configured"
            result.blockers.append(f"missing_secret:{self.secret_env}")
            return result
        if not result.provider_symbol:
            result.pricing_status = "not_configured"
            result.blockers.append("missing_provider_symbol")
            return result
        status, payload, blockers = self._get_json(
            f"{self.base_url}/historicalquotes/{quote(result.provider_symbol)}",
            params={
                "apitoken": self.api_key,
                "from": (report_date - timedelta(days=35)).isoformat(),
                "to": report_date.isoformat(),
            },
        )
        result.http_status = status
        result.blockers.extend(blockers)
        if blockers:
            result.pricing_status = "fetch_failed"
            return result
        return self._finalize_close(result, report_date, _latest_close(_records(payload), report_date))


class EodhdAdapter(ProviderAdapter):
    name = "eodhd"
    secret_env = "EODHD_API_TOKEN"
    base_url = "https://eodhd.com/api"

    def bulk_discover(self, lines: list[InstrumentLine], report_date: date) -> dict[str, ProviderResult]:
        if not self.configured:
            return super().bulk_discover(lines, report_date)
        records_by_exchange: dict[str, list[dict[str, Any]]] = {}
        failures: dict[str, list[str]] = {}
        for exchange_code in sorted({line.provider_exchange_codes.get(self.name, "") for line in lines} - {""}):
            status, payload, blockers = self._get_json(
                f"{self.base_url}/exchange-symbol-list/{quote(exchange_code)}",
                params={"api_token": self.api_key, "fmt": "json"},
            )
            records_by_exchange[exchange_code] = _records(payload) if not blockers else []
            failures[exchange_code] = blockers + ([] if status == 200 else [f"http_status:{status}"])
        results: dict[str, ProviderResult] = {}
        for line in lines:
            result = self.base_result(line, report_date)
            exchange_code = line.provider_exchange_codes.get(self.name, "")
            if failures.get(exchange_code):
                result.identity_status = "api_exchange_symbol_list_failed"
                result.blockers.extend(failures[exchange_code])
            else:
                result.identity_status, result.identity_evidence = _match_identity_records(
                    line, self.name, records_by_exchange.get(exchange_code, [])
                )
            results[line.basket_id] = result
        return results

    def discover(self, line: InstrumentLine, report_date: date) -> ProviderResult:
        result = super().discover(line, report_date)
        if not self.configured:
            return result
        status, payload, blockers = self._get_json(
            f"{self.base_url}/search/{quote(line.isin)}",
            params={"api_token": self.api_key, "fmt": "json", "limit": 50},
        )
        result.http_status = status
        result.blockers.extend(blockers)
        if blockers:
            result.identity_status = "api_search_failed"
            return result
        identity_status, evidence = _match_identity_records(line, self.name, _records(payload))
        result.identity_status = identity_status
        result.identity_evidence = evidence
        return result

    def fetch_close(self, line: InstrumentLine, report_date: date) -> ProviderResult:
        result = self.base_result(line, report_date)
        if not self.configured:
            result.pricing_status = "not_configured"
            result.blockers.append(f"missing_secret:{self.secret_env}")
            return result
        if not result.provider_symbol:
            result.pricing_status = "not_configured"
            result.blockers.append("missing_provider_symbol")
            return result
        status, payload, blockers = self._get_json(
            f"{self.base_url}/eod/{quote(result.provider_symbol)}",
            params={
                "api_token": self.api_key,
                "fmt": "json",
                "period": "d",
                "order": "d",
                "from": (report_date - timedelta(days=35)).isoformat(),
                "to": report_date.isoformat(),
            },
        )
        result.http_status = status
        result.blockers.extend(blockers)
        if blockers:
            result.pricing_status = "fetch_failed"
            return result
        return self._finalize_close(result, report_date, _latest_close(_records(payload), report_date))


class MarketstackAdapter(ProviderAdapter):
    name = "marketstack"
    secret_env = "MARKETSTACK_ACCESS_KEY"
    base_url = "https://api.marketstack.com/v2"

    def discover(self, line: InstrumentLine, report_date: date) -> ProviderResult:
        result = super().discover(line, report_date)
        if not self.configured:
            return result
        status, payload, blockers = self._get_json(
            f"{self.base_url}/tickers",
            params={"access_key": self.api_key, "search": line.isin, "limit": 100},
        )
        result.http_status = status
        result.blockers.extend(blockers)
        if blockers:
            result.identity_status = "api_search_failed"
            return result
        identity_status, evidence = _match_identity_records(line, self.name, _records(payload))
        result.identity_status = identity_status
        result.identity_evidence = evidence
        return result

    def fetch_close(self, line: InstrumentLine, report_date: date) -> ProviderResult:
        result = self.base_result(line, report_date)
        if not self.configured:
            result.pricing_status = "not_configured"
            result.blockers.append(f"missing_secret:{self.secret_env}")
            return result
        if not result.provider_symbol:
            result.pricing_status = "not_configured"
            result.blockers.append("missing_provider_symbol")
            return result
        params: dict[str, Any] = {
            "access_key": self.api_key,
            "symbols": result.provider_symbol,
            "date_from": (report_date - timedelta(days=35)).isoformat(),
            "date_to": report_date.isoformat(),
            "limit": 100,
        }
        exchange_code = line.provider_exchange_codes.get(self.name)
        if exchange_code:
            params["exchange"] = exchange_code
        status, payload, blockers = self._get_json(f"{self.base_url}/eod", params=params)
        result.http_status = status
        result.blockers.extend(blockers)
        if blockers:
            result.pricing_status = "fetch_failed"
            return result
        return self._finalize_close(result, report_date, _latest_close(_records(payload), report_date))


class AlphaVantageAdapter(ProviderAdapter):
    name = "alpha_vantage"
    secret_env = "ALPHA_VANTAGE_API_KEY"
    url = "https://www.alphavantage.co/query"

    def discover(self, line: InstrumentLine, report_date: date) -> ProviderResult:
        result = super().discover(line, report_date)
        if not self.configured:
            return result
        status, payload, blockers = self._get_json(
            self.url,
            params={"function": "SYMBOL_SEARCH", "keywords": line.isin, "apikey": self.api_key},
        )
        result.http_status = status
        result.blockers.extend(blockers)
        if isinstance(payload, Mapping) and any(key in payload for key in ("Note", "Information", "Error Message")):
            result.identity_status = "api_search_failed"
            result.blockers.append("provider_message:" + _text(next(iter(payload.values())))[:80])
            return result
        if blockers:
            result.identity_status = "api_search_failed"
            return result
        rows = [dict(row) for row in (payload or {}).get("bestMatches", []) if isinstance(row, Mapping)] if isinstance(payload, Mapping) else []
        identity_status, evidence = _match_identity_records(line, self.name, rows)
        result.identity_status = identity_status
        result.identity_evidence = evidence
        return result

    def fetch_close(self, line: InstrumentLine, report_date: date) -> ProviderResult:
        result = self.base_result(line, report_date)
        if not self.configured:
            result.pricing_status = "not_configured"
            result.blockers.append(f"missing_secret:{self.secret_env}")
            return result
        if not result.provider_symbol:
            result.pricing_status = "not_configured"
            result.blockers.append("missing_provider_symbol")
            return result
        status, payload, blockers = self._get_json(
            self.url,
            params={
                "function": "TIME_SERIES_DAILY",
                "symbol": result.provider_symbol,
                "outputsize": "compact",
                "apikey": self.api_key,
            },
        )
        result.http_status = status
        result.blockers.extend(blockers)
        if blockers:
            result.pricing_status = "fetch_failed"
            return result
        if isinstance(payload, Mapping) and any(key in payload for key in ("Note", "Information", "Error Message")):
            result.pricing_status = "fetch_failed"
            result.blockers.append("provider_message:" + _text(next(iter(payload.values())))[:80])
            return result
        series = payload.get("Time Series (Daily)", {}) if isinstance(payload, Mapping) else {}
        rows = []
        if isinstance(series, Mapping):
            for day, values in series.items():
                if isinstance(values, Mapping):
                    rows.append({"date": day, "close": values.get("4. close")})
        return self._finalize_close(result, report_date, _latest_close(rows, report_date))


class YahooChartAdapter(ProviderAdapter):
    name = "yahoo_chart"
    secret_env = None
    base_urls = (
        "https://query1.finance.yahoo.com/v8/finance/chart",
        "https://query2.finance.yahoo.com/v8/finance/chart",
    )

    def discover(self, line: InstrumentLine, report_date: date) -> ProviderResult:
        result = super().discover(line, report_date)
        result.identity_status = "registry_declared_exact_line_no_isin_search_endpoint"
        return result

    def fetch_close(self, line: InstrumentLine, report_date: date) -> ProviderResult:
        result = self.base_result(line, report_date)
        if not result.provider_symbol:
            result.pricing_status = "not_configured"
            result.blockers.append("missing_provider_symbol")
            return result
        period1 = int(datetime.combine(report_date - timedelta(days=35), datetime.min.time(), tzinfo=timezone.utc).timestamp())
        period2 = int(datetime.combine(report_date + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc).timestamp())
        payload = None
        for base_url in self.base_urls:
            status, candidate, blockers = self._get_json(
                f"{base_url}/{quote(result.provider_symbol)}",
                params={
                    "period1": period1,
                    "period2": period2,
                    "interval": "1d",
                    "events": "history",
                    "includeAdjustedClose": "true",
                },
            )
            result.http_status = status
            if not blockers:
                payload = candidate
                break
            result.blockers.extend(blockers)
            if status != 429:
                break
            time.sleep(1.0)
        if payload is None:
            result.pricing_status = "fetch_failed"
            return result
        chart = payload.get("chart", {}) if isinstance(payload, Mapping) else {}
        if chart.get("error"):
            result.pricing_status = "fetch_failed"
            result.blockers.append("provider_chart_error")
            return result
        results = chart.get("result") or []
        if not results:
            result.pricing_status = "fetch_failed"
            result.blockers.append("provider_chart_empty")
            return result
        chart_result = results[0]
        timestamps = chart_result.get("timestamp") or []
        quote_rows = (((chart_result.get("indicators") or {}).get("quote") or [{}])[0])
        closes = quote_rows.get("close") or []
        rows = []
        for stamp, close_value in zip(timestamps, closes):
            try:
                row_date = datetime.fromtimestamp(int(stamp), tz=timezone.utc).date().isoformat()
            except (TypeError, ValueError, OSError):
                continue
            rows.append({"date": row_date, "close": close_value})
        meta = chart_result.get("meta") or {}
        latest = _latest_close(rows, report_date)
        result.returned_symbol = _text(meta.get("symbol") or result.provider_symbol) or None
        result.returned_exchange = _text(meta.get("exchangeName") or meta.get("fullExchangeName")) or None
        result.returned_currency = _text(meta.get("currency")) or None
        return self._finalize_close(result, report_date, latest, source_row={
            "symbol": result.returned_symbol,
            "exchange": result.returned_exchange,
            "currency": result.returned_currency,
        })


ADAPTERS = {
    "leeway": LeewayAdapter,
    "eodhd": EodhdAdapter,
    "marketstack": MarketstackAdapter,
    "alpha_vantage": AlphaVantageAdapter,
    "yahoo_chart": YahooChartAdapter,
}


def load_registry(path: Path) -> tuple[dict[str, Any], list[InstrumentLine]]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    lines: list[InstrumentLine] = []
    for row in payload.get("trading_lines", []) or []:
        lines.append(
            InstrumentLine(
                basket_id=_text(row.get("basket_id")),
                fund_name=_text(row.get("fund_name")),
                isin=_text(row.get("isin")),
                instrument_type=_text(row.get("instrument_type")),
                exchange=_text(row.get("exchange")),
                venue_code=_text(row.get("venue_code")).upper(),
                ticker=_text(row.get("ticker")).upper(),
                currency=_text(row.get("currency")).upper(),
                funded=bool(row.get("funded")),
                provider_symbols={str(k): _text(v) for k, v in (row.get("provider_symbols") or {}).items()},
                provider_exchange_codes={str(k): _text(v).upper() for k, v in (row.get("provider_exchange_codes") or {}).items()},
            )
        )
    return payload, lines


def qualify_line(
    line: InstrumentLine,
    provider_results: list[dict[str, Any]],
    report_date: date,
    *,
    max_close_age_days: int,
    agreement_tolerance_pct: float,
) -> dict[str, Any]:
    accepted = [
        row for row in provider_results
        if row.get("pricing_status") == "priced"
        and row.get("close_price") is not None
        and row.get("close_date")
        and int(row.get("close_age_days") or 0) <= max_close_age_days
        and row.get("venue_match") is not False
        and row.get("currency_match") is not False
    ]
    by_date: dict[str, list[dict[str, Any]]] = {}
    for row in accepted:
        by_date.setdefault(str(row["close_date"]), []).append(row)
    selected_date = max(by_date, key=lambda item: (len(by_date[item]), item)) if by_date else None
    comparable = by_date.get(selected_date, []) if selected_date else []
    prices = [float(row["close_price"]) for row in comparable]
    consensus_price = median(prices) if prices else None
    spread_pct = None
    if prices and consensus_price:
        spread_pct = (max(prices) - min(prices)) / consensus_price * 100.0
    if len(comparable) >= 2 and spread_pct is not None and spread_pct <= agreement_tolerance_pct:
        status = "qualified_development_consensus"
    elif len(comparable) == 1:
        status = "single_source_only"
    elif len(comparable) >= 2:
        status = "provider_disagreement"
    else:
        status = "unpriced"
    return {
        "basket_id": line.basket_id,
        "funded": line.funded,
        "fund_name": line.fund_name,
        "instrument_type": line.instrument_type,
        "exchange": line.exchange,
        "ticker": line.ticker,
        "expected_isin": line.isin,
        "expected_venue_code": line.venue_code,
        "expected_currency": line.currency,
        "requested_report_date": report_date.isoformat(),
        "qualification_status": status,
        "selected_close_date": selected_date,
        "consensus_close_price": round(float(consensus_price), 8) if consensus_price is not None else None,
        "agreement_spread_pct": round(float(spread_pct), 6) if spread_pct is not None else None,
        "agreeing_providers": [row["provider"] for row in comparable],
        "accepted_provider_count": len(accepted),
        "same_date_provider_count": len(comparable),
        "provider_results": provider_results,
    }


def build_provider_qualification(
    *,
    registry_path: Path,
    report_date: date,
    output_path: Path,
    providers: list[str] | None = None,
    verify_identity: bool = False,
    pause_seconds: float = 1.0,
    max_close_age_days: int = DEFAULT_MAX_CLOSE_AGE_DAYS,
    agreement_tolerance_pct: float = DEFAULT_AGREEMENT_TOLERANCE_PCT,
) -> Path:
    registry, lines = load_registry(registry_path)
    selected_providers = providers or list(registry.get("provider_order") or ADAPTERS.keys())
    unknown = sorted(set(selected_providers) - set(ADAPTERS))
    if unknown:
        raise ValueError(f"Unknown providers: {','.join(unknown)}")
    adapters = {name: ADAPTERS[name]() for name in selected_providers}
    identity_cache: dict[str, dict[str, ProviderResult]] = {}
    if verify_identity:
        for provider_name, adapter in adapters.items():
            identity_cache[provider_name] = adapter.bulk_discover(lines, report_date)
    qualified_lines = []
    for line_index, line in enumerate(lines):
        results: list[dict[str, Any]] = []
        for provider_index, provider_name in enumerate(selected_providers):
            adapter = adapters[provider_name]
            identity = (
                identity_cache.get(provider_name, {}).get(line.basket_id)
                if verify_identity
                else adapter.base_result(line, report_date)
            ) or adapter.base_result(line, report_date)
            if not verify_identity:
                identity.identity_status = (
                    "registry_declared_exact_line" if identity.configured else "not_configured"
                )
                if not identity.configured and adapter.secret_env:
                    identity.blockers.append(f"missing_secret:{adapter.secret_env}")
            price = adapter.fetch_close(line, report_date)
            price.identity_status = identity.identity_status
            price.identity_evidence = identity.identity_evidence
            price.blockers = sorted(set((price.blockers or []) + (identity.blockers or [])))
            results.append(asdict(price))
            if pause_seconds > 0 and (provider_index < len(selected_providers) - 1 or line_index < len(lines) - 1):
                time.sleep(pause_seconds)
        qualified_lines.append(
            qualify_line(
                line,
                results,
                report_date,
                max_close_age_days=max_close_age_days,
                agreement_tolerance_pct=agreement_tolerance_pct,
            )
        )
    funded = [row for row in qualified_lines if row["funded"]]
    configured = {name: adapters[name].configured for name in selected_providers}
    payload = {
        "schema_version": "ucits_price_provider_qualification_v1",
        "generated_at_utc": utc_now(),
        "report_date": report_date.isoformat(),
        "registry_path": str(registry_path),
        "provider_order": selected_providers,
        "provider_configuration": {
            name: {"secret_env": PROVIDER_SECRET_ENVS[name], "configured": configured[name]}
            for name in selected_providers
        },
        "verify_identity": verify_identity,
        "max_close_age_days": max_close_age_days,
        "agreement_tolerance_pct": agreement_tolerance_pct,
        "line_count": len(qualified_lines),
        "funded_line_count": len(funded),
        "qualified_line_count": sum(row["qualification_status"] == "qualified_development_consensus" for row in qualified_lines),
        "funded_consensus_count": sum(row["qualification_status"] == "qualified_development_consensus" for row in funded),
        "report_pricing_gate_passed": bool(funded) and all(
            row["qualification_status"] == "qualified_development_consensus" for row in funded
        ),
        "development_only": True,
        "production_or_redistribution_authority": False,
        "portfolio_mutation": False,
        "delivery_authority": False,
        "lines": qualified_lines,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "UCITS_PRICE_PROVIDER_QUALIFICATION_OK"
        f" | output={output_path}"
        f" | lines={len(qualified_lines)}"
        f" | funded_consensus={payload['funded_consensus_count']}/{len(funded)}"
        f" | gate={payload['report_pricing_gate_passed']}"
    )
    return output_path


def build_legacy_validation_artifact(
    *,
    qualification_path: Path,
    output_path: Path,
    source_basket: str,
    run_id: str,
) -> Path:
    qualification = json.loads(qualification_path.read_text(encoding="utf-8"))
    rows = []
    for line in qualification.get("lines", []):
        selected = None
        selected_date = line.get("selected_close_date")
        for candidate in line.get("provider_results", []):
            if candidate.get("pricing_status") == "priced" and candidate.get("close_date") == selected_date:
                selected = candidate
                break
        provider_symbols = {row.get("provider"): row.get("provider_symbol") for row in line.get("provider_results", [])}
        blockers: list[str] = []
        for candidate in line.get("provider_results", []):
            blockers.extend(candidate.get("blockers") or [])
        status = "priced_non_authoritative" if line.get("consensus_close_price") is not None else "fetch_failed"
        rows.append({
            "basket_id": line.get("basket_id"),
            "fund_name": line.get("fund_name"),
            "instrument_type": line.get("instrument_type"),
            "exchange": line.get("exchange"),
            "ticker": line.get("ticker"),
            "isin": line.get("expected_isin"),
            "venue_code": line.get("expected_venue_code"),
            "currency": line.get("expected_currency"),
            "pricing_status": status,
            "close_date": line.get("selected_close_date"),
            "close_price": line.get("consensus_close_price"),
            "source_id": "provider_consensus" if line.get("same_date_provider_count", 0) >= 2 else (selected or {}).get("provider", "none"),
            "source_name": "Development provider consensus" if line.get("same_date_provider_count", 0) >= 2 else f"{(selected or {}).get('provider', 'No provider')} completed-close evidence",
            "source_quality_status": "development_consensus" if line.get("qualification_status") == "qualified_development_consensus" else "development_single_source",
            "source_agreement_status": line.get("qualification_status"),
            "observed_at_utc": (selected or {}).get("observed_at_utc") or qualification.get("generated_at_utc"),
            "requested_report_date": qualification.get("report_date"),
            "completed_close_on_or_before_report_date": line.get("selected_close_date") is not None,
            "valuation_grade": line.get("qualification_status") == "qualified_development_consensus",
            "fundable": False,
            "blockers": sorted(set(blockers)),
            "provider_symbols": provider_symbols,
            "agreeing_providers": line.get("agreeing_providers", []),
            "agreement_spread_pct": line.get("agreement_spread_pct"),
        })
    priced = [row for row in rows if row["pricing_status"] == "priced_non_authoritative"]
    payload = {
        "schema_version": "ucits_close_price_validation_basket_results_v2",
        "run_id": run_id,
        "report_date": qualification.get("report_date"),
        "source_basket": source_basket,
        "generated_at_utc": qualification.get("generated_at_utc"),
        "line_count": len(rows),
        "priced_line_count": len(priced),
        "failed_line_count": len(rows) - len(priced),
        "source_chain": qualification.get("provider_order", []),
        "provider_configuration": qualification.get("provider_configuration", {}),
        "report_pricing_gate_passed": qualification.get("report_pricing_gate_passed", False),
        "valuation_grade": qualification.get("report_pricing_gate_passed", False),
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
        "rows": rows,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path
