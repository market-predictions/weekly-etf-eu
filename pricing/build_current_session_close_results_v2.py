from __future__ import annotations

import json
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests

from pricing import build_current_session_close_results as legacy
from pricing.yahoo_regular_market_fallback import report_date_regular_market_close


_original_fetch_yahoo = legacy.fetch_yahoo
CORE_FUNDED_TICKERS = {"VWCE", "EUNA", "SXR8"}
ALLOWED_ACTIVATED_TICKERS = {"L0CK"}


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


def fetch_yahoo_with_regular_market_fallback(
    line: dict[str, Any],
    report_date: date,
) -> dict[str, Any]:
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
    params = {
        "period1": period1,
        "period2": period2,
        "interval": "1d",
        "events": "history",
        "includeAdjustedClose": "true",
    }
    observed_at = datetime.now(timezone.utc)
    try:
        response = requests.get(
            url,
            params=params,
            timeout=legacy.TIMEOUT_SECONDS,
            headers={"User-Agent": "Weekly-ETF-EU/1.0"},
        )
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
    fallback = report_date_regular_market_close(
        meta,
        report_date=report_date,
        observed_at_utc=observed_at,
    )
    if fallback is None:
        result.setdefault("blockers", []).append("report_date_regular_market_metadata_unavailable")
        return result

    returned_currency = str(meta.get("currency") or "").upper() or None
    returned_exchange = str(meta.get("exchangeName") or meta.get("fullExchangeName") or "") or None
    expected_venue = str(line.get("venue_code") or "").upper()
    venue_aliases = {
        "XETR": {"GER", "XETRA", "GERMANY", "DEX"},
        "XAMS": {"AMS", "AS", "AMSTERDAM", "EURONEXT AMSTERDAM"},
        "XLON": {"LSE", "LON", "LONDON", "LONDON STOCK EXCHANGE"},
    }
    venue_match = returned_exchange.upper() in venue_aliases.get(expected_venue, {expected_venue}) if returned_exchange else None
    currency_match = returned_currency == str(line.get("currency") or "").upper() if returned_currency else None
    if venue_match is not True or currency_match is not True:
        result.setdefault("blockers", []).append("regular_market_metadata_identity_mismatch")
        return result

    result.update(
        {
            "pricing_status": "priced",
            "close_date": report_date.isoformat(),
            "close_price": round(float(fallback["close_price"]), 8),
            "close_age_days": 0,
            "returned_symbol": str(meta.get("symbol") or symbol),
            "returned_exchange": returned_exchange,
            "returned_mic": None,
            "returned_currency": returned_currency,
            "venue_match": venue_match,
            "currency_match": currency_match,
            "identity_status": "metadata_matches_expected_line",
            "retrieval_mode": "live_regular_market_metadata_fallback",
            "regular_market_metadata_fallback": fallback,
            "blockers": [],
        }
    )
    evidence = list(result.get("identity_evidence") or [])
    evidence.append(
        {
            "returned_symbol": str(meta.get("symbol") or symbol),
            "returned_exchange": returned_exchange,
            "returned_currency": returned_currency,
            "regular_market_price": fallback["close_price"],
            "regular_market_time_berlin": fallback["regular_market_time_berlin"],
            "completion_mode": fallback["completion_mode"],
            "source_field": fallback["source_field"],
        }
    )
    result["identity_evidence"] = evidence
    return result


def main() -> None:
    legacy.fetch_yahoo = fetch_yahoo_with_regular_market_fallback
    legacy.FUNDED_TICKERS = funded_tickers_from_state()
    legacy.main()


if __name__ == "__main__":
    main()
