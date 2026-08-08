from __future__ import annotations

import hashlib
import json
import sys
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlencode

import requests

from pricing import build_current_session_close_results as legacy
from pricing.yahoo_regular_market_fallback import report_date_regular_market_close


_original_fetch_yahoo = legacy.fetch_yahoo
_original_fetch_boerse = legacy.fetch_boerse
CORE_FUNDED_TICKERS = {"VWCE", "EUNA", "SXR8"}
ALLOWED_ACTIVATED_TICKERS = {"L0CK"}
BOERSE_HISTORY_TRACE_SALT = "w4ivc1ATTGta6njAZzMbkL3kJwxMfEAKDa3MNr"
BOERSE_HISTORY_LOOKBACK_DAYS = 4
BOERSE_HISTORY_LOOKAHEAD_DAYS = 1


def normalize_ticker(value: Any) -> str:
    ticker = str(value or "").strip().upper()
    return "L0CK" if ticker == "LOCK" else ticker


def funded_tickers_from_state(path: Path = Path("output/etf_eu_portfolio_state.json")) -> set[str]:
    if not path.exists():
        return set(CORE_FUNDED_TICKERS)
    payload = json.loads(path.read_text(encoding="utf-8"))
    positions = payload.get("positions") if isinstance(payload, dict) else []
    funded = {
        normalize_ticker(row.get("ticker") or row.get("exchange_ticker"))
        for row in positions or []
        if isinstance(row, dict) and normalize_ticker(row.get("ticker") or row.get("exchange_ticker"))
    }
    if not CORE_FUNDED_TICKERS.issubset(funded):
        raise RuntimeError(f"Core funded pricing scope is incomplete: {sorted(funded)}")
    extras = funded - CORE_FUNDED_TICKERS
    if not extras.issubset(ALLOWED_ACTIVATED_TICKERS):
        raise RuntimeError(f"Unexpected activated funded pricing scope: {sorted(extras)}")
    if extras:
        if payload.get("model_portfolio_only") is not True or payload.get("real_broker_execution") is not False:
            raise RuntimeError("Activated pricing scope lacks model-only authority boundary")
        activation = payload.get("last_model_capital_activation") or {}
        if not activation.get("activation_id"):
            raise RuntimeError("Activated pricing scope lacks activation provenance")
    return funded


def _historical_close_from_boerse_payload(payload: Any, report_date: date) -> tuple[float, dict[str, Any]] | None:
    if not isinstance(payload, dict):
        return None
    rows = payload.get("data") or []
    if not isinstance(rows, list):
        return None
    for row in rows:
        if not isinstance(row, dict):
            continue
        row_date_text = str(row.get("date") or "").strip()[:10]
        if row_date_text != report_date.isoformat():
            continue
        close = legacy.positive_float(row.get("close"))
        if close is None:
            continue
        return float(close), row
    return None


def boerse_history_headers(url: str) -> dict[str, str]:
    current = legacy.now_utc()
    client_date = current.isoformat(timespec="milliseconds").replace("+00:00", "Z")
    trace_id = hashlib.md5((client_date + url + BOERSE_HISTORY_TRACE_SALT).encode("utf-8")).hexdigest()
    return {
        "Accept": "application/json, text/plain, */*",
        "Client-Date": client_date,
        "X-Client-TraceId": trace_id,
        "Referer": "https://www.boerse-frankfurt.de/",
        "User-Agent": "Mozilla/5.0 Weekly-ETF-EU-Historical-Close/1.0",
    }


def fetch_boerse_with_historical_replay(line: dict[str, Any], report_date: date) -> dict[str, Any]:
    """Use live Börse identity, then replay the exact report-date close from a bounded history window."""

    result = _original_fetch_boerse(line, report_date)
    if result.get("pricing_status") == "priced" and result.get("close_date") == report_date.isoformat():
        return result
    if line.get("venue_code") != "XETR":
        return result
    if result.get("venue_match") is not True or result.get("currency_match") is not True:
        blockers = list(result.get("blockers") or [])
        if "historical_replay_identity_not_verified" not in blockers:
            blockers.append("historical_replay_identity_not_verified")
        result["blockers"] = blockers
        return result

    history_start = report_date - timedelta(days=BOERSE_HISTORY_LOOKBACK_DAYS)
    history_end = report_date + timedelta(days=BOERSE_HISTORY_LOOKAHEAD_DAYS)
    params = {
        "limit": 50,
        "offset": 0,
        "isin": line["isin"],
        "mic": line["venue_code"],
        "minDate": history_start.isoformat(),
        "maxDate": history_end.isoformat(),
        "cleanSplit": "false",
        "cleanPayout": "false",
        "cleanSubscriptionRights": "false",
    }
    url = f"{legacy.BASE_URL}/v1/data/price_history?{urlencode(params)}"
    try:
        response = requests.get(url, headers=boerse_history_headers(url), timeout=legacy.TIMEOUT_SECONDS)
        payload = response.json()
    except Exception as exc:
        blockers = list(result.get("blockers") or [])
        blockers.append(f"historical_replay_request_exception:{type(exc).__name__}")
        result["blockers"] = blockers
        return result

    if response.status_code != 200:
        blockers = list(result.get("blockers") or [])
        blockers.append(f"historical_replay_provider_error:{response.status_code}")
        result["blockers"] = blockers
        result["historical_replay_debug"] = {
            "url": url,
            "status_code": response.status_code,
            "window_start": history_start.isoformat(),
            "window_end": history_end.isoformat(),
        }
        return result

    historical = _historical_close_from_boerse_payload(payload, report_date)
    if historical is None:
        blockers = list(result.get("blockers") or [])
        blockers.append("historical_report_date_close_unavailable")
        result["blockers"] = blockers
        result["historical_replay_debug"] = {
            "url": url,
            "status_code": response.status_code,
            "window_start": history_start.isoformat(),
            "window_end": history_end.isoformat(),
            "payload_type": type(payload).__name__,
            "payload_keys": sorted(payload.keys()) if isinstance(payload, dict) else [],
            "total_count": payload.get("totalCount") if isinstance(payload, dict) else None,
            "sample_data": (payload.get("data") or [])[:2] if isinstance(payload, dict) and isinstance(payload.get("data"), list) else None,
        }
        return result

    close_price, row = historical
    evidence = list(result.get("identity_evidence") or [])
    evidence.append(
        {
            "query_mode": "exact_isin_plus_mic_historical_price_history",
            "queried_isin": str(line.get("isin") or "").upper(),
            "queried_mic": str(line.get("venue_code") or "").upper(),
            "history_window_start": history_start.isoformat(),
            "history_window_end": history_end.isoformat(),
            "historical_date": report_date.isoformat(),
            "historical_close": round(close_price, 8),
            "historical_open": legacy.positive_float(row.get("open")),
            "historical_high": legacy.positive_float(row.get("high")),
            "historical_low": legacy.positive_float(row.get("low")),
            "historical_turnover_pieces": legacy.positive_float(row.get("turnoverPieces")),
            "historical_turnover_eur": legacy.positive_float(row.get("turnoverEuro")),
            "endpoint": "boerse_frankfurt_price_history",
        }
    )
    result.update(
        {
            "pricing_status": "priced",
            "close_date": report_date.isoformat(),
            "close_price": round(close_price, 8),
            "close_age_days": 0,
            "identity_status": "verified_exact_isin_mic_currency_with_historical_close",
            "identity_evidence": evidence,
            "retrieval_mode": "historical_exact_isin_mic_replay",
            "blockers": [],
        }
    )
    return result


def fetch_yahoo_with_regular_market_fallback(line: dict[str, Any], report_date: date) -> dict[str, Any]:
    result = _original_fetch_yahoo(line, report_date)
    if result.get("pricing_status") == "priced" and result.get("close_date") == report_date.isoformat():
        return result

    symbol = str(line.get("provider_symbol_yahoo") or "").strip()
    if not symbol:
        return result

    start = report_date - timedelta(days=10)
    period1 = int(datetime.combine(start, time.min, tzinfo=timezone.utc).timestamp())
    period2 = int(datetime.combine(report_date + timedelta(days=2), time.min, tzinfo=timezone.utc).timestamp())
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{quote(symbol)}"
    params = {"period1": period1, "period2": period2, "interval": "1d", "events": "history", "includeAdjustedClose": "true"}
    observed_at = datetime.now(timezone.utc)
    try:
        response = requests.get(url, params=params, timeout=legacy.TIMEOUT_SECONDS, headers={"User-Agent": "Weekly-ETF-EU/1.0"})
        payload = response.json()
    except Exception as exc:
        result.setdefault("blockers", []).append(f"regular_market_metadata_request_exception:{type(exc).__name__}")
        return result

    chart = payload.get("chart", {}) if isinstance(payload, dict) else {}
    data_rows = chart.get("result") or []
    if response.status_code != 200 or not data_rows:
        result.setdefault("blockers", []).append(f"regular_market_metadata_provider_error:{response.status_code}")
        return result

    meta = data_rows[0].get("meta") or {}
    fallback = report_date_regular_market_close(meta, report_date=report_date, observed_at_utc=observed_at)
    if fallback is None:
        result.setdefault("blockers", []).append("report_date_regular_market_metadata_unavailable")
        return result

    returned_currency = str(meta.get("currency") or "").upper() or None
    returned_exchange = str(meta.get("exchangeName") or meta.get("fullExchangeName") or "") or None
    expected_venue = str(line.get("venue_code") or "").upper()
    venue_aliases = {"XETR": {"GER", "XETRA", "GERMANY", "DEX"}, "XAMS": {"AMS", "AS", "AMSTERDAM", "EURONEXT AMSTERDAM"}, "XLON": {"LSE", "LON", "LONDON", "LONDON STOCK EXCHANGE"}}
    venue_match = returned_exchange.upper() in venue_aliases.get(expected_venue, {expected_venue}) if returned_exchange else None
    currency_match = returned_currency == str(line.get("currency") or "").upper() if returned_currency else None
    if venue_match is not True or currency_match is not True:
        result.setdefault("blockers", []).append("regular_market_metadata_identity_mismatch")
        return result

    result.update({"pricing_status": "priced", "close_date": report_date.isoformat(), "close_price": round(float(fallback["close_price"]), 8), "close_age_days": 0, "returned_symbol": str(meta.get("symbol") or symbol), "returned_exchange": returned_exchange, "returned_mic": None, "returned_currency": returned_currency, "venue_match": venue_match, "currency_match": currency_match, "identity_status": "metadata_matches_expected_line", "retrieval_mode": "live_regular_market_metadata_fallback", "regular_market_metadata_fallback": fallback, "blockers": []})
    evidence = list(result.get("identity_evidence") or [])
    evidence.append({"returned_symbol": str(meta.get("symbol") or symbol), "returned_exchange": returned_exchange, "returned_currency": returned_currency, "regular_market_price": fallback["close_price"], "regular_market_time_berlin": fallback["regular_market_time_berlin"], "completion_mode": fallback["completion_mode"], "source_field": fallback["source_field"]})
    result["identity_evidence"] = evidence
    return result


def _argument_value(flag: str) -> str | None:
    try:
        index = sys.argv.index(flag)
    except ValueError:
        return None
    return sys.argv[index + 1] if index + 1 < len(sys.argv) else None


def print_funded_failure_diagnostics() -> None:
    path_text = _argument_value("--qualification-output")
    if not path_text:
        return
    path = Path(path_text)
    if not path.is_file():
        return
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return
    funded = [row for row in payload.get("lines") or [] if isinstance(row, dict) and row.get("funded")]
    compact = []
    for row in funded:
        compact.append(
            {
                "ticker": row.get("ticker"),
                "qualification_status": row.get("qualification_status"),
                "selected_close_date": row.get("selected_close_date"),
                "same_date_provider_count": row.get("same_date_provider_count"),
                "providers": [
                    {
                        "provider": provider.get("provider"),
                        "status": provider.get("pricing_status"),
                        "close_date": provider.get("close_date"),
                        "close_price": provider.get("close_price"),
                        "venue_match": provider.get("venue_match"),
                        "currency_match": provider.get("currency_match"),
                        "retrieval_mode": provider.get("retrieval_mode"),
                        "blockers": provider.get("blockers"),
                        "historical_replay_debug": provider.get("historical_replay_debug"),
                    }
                    for provider in row.get("provider_results") or []
                    if isinstance(provider, dict)
                ],
            }
        )
    print("FUNDED_PRICING_FAILURE_DIAGNOSTICS=" + json.dumps(compact, sort_keys=True))


def main() -> None:
    legacy.fetch_boerse = fetch_boerse_with_historical_replay
    legacy.fetch_yahoo = fetch_yahoo_with_regular_market_fallback
    legacy.FUNDED_TICKERS = funded_tickers_from_state()
    try:
        legacy.main()
    except SystemExit:
        print_funded_failure_diagnostics()
        raise


if __name__ == "__main__":
    main()
