from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from statistics import median
from typing import Any
from urllib.parse import quote, urlencode
from zoneinfo import ZoneInfo

import requests
import yaml

BASE_URL = "https://api.boerse-frankfurt.de"
TRACE_SALT = "w4icATTGtnjAQMbkL3kJwxLfEAKDa3VU"
TIMEOUT_SECONDS = 30
BERLIN = ZoneInfo("Europe/Berlin")
FUNDED_TICKERS = {"VWCE", "EUNA", "SXR8"}


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def utc_text() -> str:
    return now_utc().replace(microsecond=0).isoformat().replace("+00:00", "Z")


def positive_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and number > 0 else None


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
        "User-Agent": "Mozilla/5.0 Weekly-ETF-EU-Current-Close/1.0",
    }


def fetch_boerse(line: dict[str, Any], report_date: date) -> dict[str, Any]:
    provider_symbol = f"{line['venue_code']}:{line['isin']}"
    result: dict[str, Any] = {
        "provider": "boerse_frankfurt_xetra",
        "configured": line.get("venue_code") == "XETR",
        "provider_symbol": provider_symbol,
        "expected_isin": line.get("isin"),
        "expected_venue_code": line.get("venue_code"),
        "expected_currency": line.get("currency"),
        "requested_report_date": report_date.isoformat(),
        "pricing_status": "not_configured",
        "close_date": None,
        "close_price": None,
        "close_age_days": None,
        "returned_symbol": None,
        "returned_exchange": None,
        "returned_mic": None,
        "returned_currency": None,
        "venue_match": None,
        "currency_match": None,
        "http_status": None,
        "observed_at_utc": utc_text(),
        "retrieval_mode": "live",
        "blockers": [],
    }
    if line.get("venue_code") != "XETR":
        result["blockers"] = ["boerse_frankfurt_xetra_only"]
        return result

    url = f"{BASE_URL}/v1/data/price_information/single?{urlencode({'isin': line['isin'], 'mic': line['venue_code']})}"
    observed_at = now_utc()
    try:
        response = requests.get(url, headers=boerse_headers(url), timeout=TIMEOUT_SECONDS)
        result["http_status"] = response.status_code
        payload = response.json()
    except Exception as exc:
        result["pricing_status"] = "fetch_failed"
        result["blockers"] = [f"request_exception:{type(exc).__name__}"]
        return result
    if response.status_code != 200 or not isinstance(payload, dict):
        result["pricing_status"] = "fetch_failed"
        result["blockers"] = [f"provider_error:{response.status_code}"]
        return result

    returned_isin = str(payload.get("isin") or "").upper()
    returned_mic = str(payload.get("mic") or "").upper()
    returned_currency = currency_code(payload.get("currency"))
    result.update(
        {
            "returned_symbol": f"{returned_mic}:{returned_isin}" if returned_isin and returned_mic else None,
            "returned_exchange": "Xetra" if returned_mic == "XETR" else returned_mic or None,
            "returned_mic": returned_mic or None,
            "returned_currency": returned_currency,
            "venue_match": returned_mic == str(line.get("venue_code") or "").upper(),
            "currency_match": returned_currency == str(line.get("currency") or "").upper(),
        }
    )
    timestamp_text = str(payload.get("timestampLastPrice") or "").strip()
    try:
        last_timestamp = datetime.fromisoformat(timestamp_text.replace("Z", "+00:00"))
    except ValueError:
        last_timestamp = None
    last_date = last_timestamp.astimezone(BERLIN).date() if last_timestamp else None
    try:
        session_end_time = time.fromisoformat(str(payload.get("tradingTimeEnd") or "22:00:00"))
    except ValueError:
        session_end_time = time(22, 0)
    session_end = datetime.combine(report_date, session_end_time, tzinfo=BERLIN).astimezone(timezone.utc)
    observed_after_session = observed_at >= session_end
    # The web endpoint exposes the completed Xetra session close in the field
    # named closingPricePrevTradingDay after the report-date session has ended.
    # The separate lastPrice can include the extended-hours final trade and is
    # retained only as supporting evidence, never as the report close.
    completed_close = positive_float(payload.get("closingPricePrevTradingDay"))
    identity_match = (
        returned_isin == str(line.get("isin") or "").upper()
        and bool(result["venue_match"])
        and bool(result["currency_match"])
    )
    completed = bool(last_date == report_date and observed_after_session and completed_close is not None and identity_match)
    result["identity_status"] = "verified_exact_isin_mic_currency" if identity_match else "identity_mismatch"
    result["identity_evidence"] = [
        {
            "query_mode": "exact_isin_plus_mic",
            "returned_isin": returned_isin,
            "returned_mic": returned_mic,
            "returned_currency": returned_currency,
            "session_close_field": "closingPricePrevTradingDay",
            "last_trade_field": "lastPrice",
            "last_trade_price": positive_float(payload.get("lastPrice")),
            "last_trade_timestamp": timestamp_text or None,
            "trading_time_end": str(payload.get("tradingTimeEnd") or ""),
            "observed_after_session_end": observed_after_session,
            "change_to_previous_day_absolute": payload.get("changeToPrevDayAbsolute"),
            "change_to_previous_day_pct": payload.get("changeToPrevDayInPercent"),
            "turnover_eur": positive_float(payload.get("turnoverInEur")),
            "turnover_pieces": positive_float(payload.get("turnoverInPieces")),
            "price_fixings": payload.get("priceFixings"),
        }
    ]
    if not completed:
        result["pricing_status"] = "fetch_failed"
        result["blockers"] = ["completed_report_date_session_close_unavailable"]
        return result
    result.update(
        {
            "pricing_status": "priced",
            "close_date": report_date.isoformat(),
            "close_price": round(float(completed_close), 8),
            "close_age_days": 0,
            "blockers": [],
        }
    )
    return result


def fetch_yahoo(line: dict[str, Any], report_date: date) -> dict[str, Any]:
    symbol = str(line.get("provider_symbol_yahoo") or "").strip()
    result: dict[str, Any] = {
        "provider": "yahoo_chart",
        "configured": bool(symbol),
        "provider_symbol": symbol,
        "expected_isin": line.get("isin"),
        "expected_venue_code": line.get("venue_code"),
        "expected_currency": line.get("currency"),
        "requested_report_date": report_date.isoformat(),
        "pricing_status": "not_configured" if not symbol else "not_attempted",
        "close_date": None,
        "close_price": None,
        "close_age_days": None,
        "returned_symbol": None,
        "returned_exchange": None,
        "returned_mic": None,
        "returned_currency": None,
        "venue_match": None,
        "currency_match": None,
        "http_status": None,
        "observed_at_utc": utc_text(),
        "retrieval_mode": "live",
        "blockers": [] if symbol else ["missing_provider_symbol_yahoo"],
    }
    if not symbol:
        return result
    start = report_date - timedelta(days=10)
    period1 = int(datetime.combine(start, time.min, tzinfo=timezone.utc).timestamp())
    period2 = int(datetime.combine(report_date + timedelta(days=1), time.min, tzinfo=timezone.utc).timestamp())
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{quote(symbol)}"
    params = {"period1": period1, "period2": period2, "interval": "1d", "events": "history", "includeAdjustedClose": "true"}
    try:
        response = requests.get(url, params=params, timeout=TIMEOUT_SECONDS, headers={"User-Agent": "Weekly-ETF-EU/1.0"})
        result["http_status"] = response.status_code
        payload = response.json()
    except Exception as exc:
        result["pricing_status"] = "fetch_failed"
        result["blockers"] = [f"request_exception:{type(exc).__name__}"]
        return result
    chart = payload.get("chart", {}) if isinstance(payload, dict) else {}
    data_rows = chart.get("result") or []
    if response.status_code != 200 or not data_rows:
        result["pricing_status"] = "fetch_failed"
        result["blockers"] = [f"provider_error:{response.status_code}"]
        return result
    data = data_rows[0]
    meta = data.get("meta") or {}
    timestamps = data.get("timestamp") or []
    quote_rows = (data.get("indicators") or {}).get("quote") or []
    closes = quote_rows[0].get("close", []) if quote_rows else []
    accepted: list[tuple[date, float]] = []
    for stamp, raw_close in zip(timestamps, closes):
        try:
            row_date = datetime.fromtimestamp(int(stamp), tz=timezone.utc).astimezone(BERLIN).date()
        except (TypeError, ValueError, OSError):
            continue
        close = positive_float(raw_close)
        if close is not None and row_date <= report_date:
            accepted.append((row_date, close))
    if not accepted:
        result["pricing_status"] = "fetch_failed"
        result["blockers"] = ["no_usable_completed_close_on_or_before_report_date"]
        return result
    close_date, close_price = max(accepted, key=lambda item: item[0])
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
    result.update(
        {
            "pricing_status": "priced",
            "close_date": close_date.isoformat(),
            "close_price": round(close_price, 8),
            "close_age_days": (report_date - close_date).days,
            "returned_symbol": str(meta.get("symbol") or symbol),
            "returned_exchange": returned_exchange,
            "returned_mic": None,
            "returned_currency": returned_currency,
            "venue_match": venue_match,
            "currency_match": currency_match,
            "identity_status": "metadata_matches_expected_line" if venue_match and currency_match else "metadata_incomplete_or_mismatch",
            "identity_evidence": [{"returned_symbol": str(meta.get("symbol") or symbol), "returned_exchange": returned_exchange, "returned_currency": returned_currency}],
        }
    )
    if venue_match is False or currency_match is False:
        result["pricing_status"] = "identity_rejected"
        result["blockers"] = ["returned_identity_mismatch"]
    return result


def load_lines(path: Path) -> list[dict[str, Any]]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    lines = [dict(row) for row in payload.get("trading_lines", []) if isinstance(row, dict)]
    if not any(str(row.get("ticker") or "").upper() == "VVSM" for row in lines):
        lines.insert(
            4,
            {
                "basket_id": "vvsm_xetra_eur",
                "role": "Retained Stage-1 semiconductor watchlist candidate",
                "fund_name": "VanEck Semiconductor UCITS ETF",
                "isin": "IE00BMC38736",
                "instrument_type": "UCITS ETF",
                "exchange": "Xetra",
                "venue_code": "XETR",
                "ticker": "VVSM",
                "provider_symbol_yahoo": "VVSM.DE",
                "currency": "EUR",
                "valuation_grade": False,
                "fundable": False,
            },
        )
    return lines


def summarize_line(line: dict[str, Any], report_date: date) -> tuple[dict[str, Any], dict[str, Any]]:
    yahoo = fetch_yahoo(line, report_date)
    boerse = fetch_boerse(line, report_date)
    provider_results = [boerse, yahoo]
    accepted = [row for row in provider_results if row.get("pricing_status") == "priced" and row.get("close_price") is not None]
    by_date: dict[str, list[dict[str, Any]]] = {}
    for row in accepted:
        by_date.setdefault(str(row.get("close_date")), []).append(row)
    selected_date = max(by_date, key=lambda item: (len(by_date[item]), item)) if by_date else None
    comparable = by_date.get(selected_date, []) if selected_date else []
    values = [float(row["close_price"]) for row in comparable]
    consensus = median(values) if values else None
    spread_pct = ((max(values) - min(values)) / consensus * 100.0) if len(values) >= 2 and consensus else (0.0 if len(values) == 1 else None)
    exact_identity_anchor = any(
        row.get("provider") == "boerse_frankfurt_xetra"
        and row.get("pricing_status") == "priced"
        and row.get("venue_match") is True
        and row.get("currency_match") is True
        for row in comparable
    ) or any(
        row.get("provider") == "yahoo_chart"
        and row.get("pricing_status") == "priced"
        and row.get("venue_match") is True
        and row.get("currency_match") is True
        and str(line.get("ticker") or "").upper() != "CBUF"
        for row in comparable
    )
    qualified = len(comparable) >= 2 and spread_pct is not None and spread_pct <= 1.0 and exact_identity_anchor
    status = "qualified_development_consensus" if qualified else ("single_source_only" if len(comparable) == 1 else ("provider_disagreement" if len(comparable) >= 2 else "unpriced"))
    ticker = str(line.get("ticker") or "").upper()
    legacy = {
        "basket_id": line.get("basket_id"),
        "fund_name": line.get("fund_name"),
        "isin": line.get("isin"),
        "instrument_type": line.get("instrument_type"),
        "exchange": line.get("exchange"),
        "venue_code": line.get("venue_code"),
        "ticker": ticker,
        "currency": line.get("currency"),
        "requested_report_date": report_date.isoformat(),
        "pricing_status": "priced_non_authoritative" if consensus is not None else "fetch_failed",
        "close_date": selected_date,
        "close_price": round(float(consensus), 8) if consensus is not None else None,
        "completed_close_on_or_before_report_date": bool(selected_date and selected_date <= report_date.isoformat()),
        "source_id": "provider_consensus" if qualified else (comparable[0]["provider"] if comparable else "none"),
        "source_name": "Development provider consensus" if qualified else (f"{comparable[0]['provider']} completed-close evidence" if comparable else "No provider completed-close evidence"),
        "source_quality_status": "development_consensus" if qualified else ("development_single_source" if comparable else "unpriced"),
        "source_agreement_status": status,
        "agreeing_providers": [str(row.get("provider")) for row in comparable],
        "agreement_spread_pct": round(float(spread_pct), 6) if spread_pct is not None else None,
        "provider_symbols": {
            "boerse_frankfurt_xetra": f"{line.get('venue_code')}:{line.get('isin')}",
            "yahoo_chart": line.get("provider_symbol_yahoo"),
        },
        "observed_at_utc": utc_text(),
        "blockers": sorted({blocker for row in provider_results for blocker in (row.get("blockers") or [])}),
        "valuation_grade": qualified,
        "fundable": False,
    }
    qualification = {
        "basket_id": line.get("basket_id"),
        "role": line.get("role"),
        "fund_name": line.get("fund_name"),
        "ticker": ticker,
        "isin": line.get("isin"),
        "instrument_type": line.get("instrument_type"),
        "exchange": line.get("exchange"),
        "venue_code": line.get("venue_code"),
        "currency": line.get("currency"),
        "funded": ticker in FUNDED_TICKERS,
        "provider_results": provider_results,
        "qualification_status": status,
        "selected_close_date": selected_date,
        "consensus_close_price": legacy["close_price"],
        "agreement_spread_pct": legacy["agreement_spread_pct"],
        "agreeing_providers": legacy["agreeing_providers"],
        "accepted_provider_count": len(accepted),
        "same_date_provider_count": len(comparable),
        "identity_anchor_passed": exact_identity_anchor,
        "identity_anchor_providers": [row["provider"] for row in comparable if row.get("venue_match") is True and row.get("currency_match") is True],
    }
    return legacy, qualification


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--basket", default="config/ucits_close_price_validation_basket.yml")
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--qualification-output", required=True)
    args = parser.parse_args()
    report_date = date.fromisoformat(args.report_date)
    lines = load_lines(Path(args.basket))
    legacy_rows: list[dict[str, Any]] = []
    qualification_lines: list[dict[str, Any]] = []
    for line in lines:
        legacy, qualification = summarize_line(line, report_date)
        legacy_rows.append(legacy)
        qualification_lines.append(qualification)
    funded = [line for line in qualification_lines if line.get("funded")]
    funded_pass = all(line.get("qualification_status") == "qualified_development_consensus" and line.get("identity_anchor_passed") for line in funded)
    qualification_payload = {
        "schema_version": "ucits_price_provider_qualification_v2",
        "generated_at_utc": utc_text(),
        "report_date": report_date.isoformat(),
        "provider_order": ["boerse_frankfurt_xetra", "yahoo_chart"],
        "agreement_tolerance_pct": 1.0,
        "line_count": len(qualification_lines),
        "funded_line_count": len(funded),
        "funded_consensus_count": sum(line.get("qualification_status") == "qualified_development_consensus" for line in funded),
        "funded_identity_anchor_count": sum(bool(line.get("identity_anchor_passed")) for line in funded),
        "report_pricing_gate_passed": funded_pass,
        "authority": "development_technical_evidence_only",
        "commercial_redistribution_authority": False,
        "portfolio_mutation": False,
        "delivery_authority": False,
        "lines": qualification_lines,
    }
    legacy_payload = {
        "schema_version": "ucits_close_price_validation_basket_results_v3",
        "generated_at_utc": utc_text(),
        "run_id": args.run_id,
        "report_date": report_date.isoformat(),
        "source_basket": args.basket,
        "source_chain": ["boerse_frankfurt_xetra", "yahoo_chart"],
        "line_count": len(legacy_rows),
        "priced_line_count": sum(row.get("close_price") is not None for row in legacy_rows),
        "failed_line_count": sum(row.get("close_price") is None for row in legacy_rows),
        "report_pricing_gate_passed": funded_pass,
        "valuation_grade": funded_pass,
        "provider_configuration": {
            "boerse_frankfurt_xetra": {"configured": True, "secret_env": None, "authority": "development_technical_only"},
            "yahoo_chart": {"configured": True, "secret_env": None},
        },
        "portfolio_mutation": False,
        "funding_authority": False,
        "production_delivery_authority": False,
        "rows": legacy_rows,
    }
    output = Path(args.output)
    qualification_output = Path(args.qualification_output)
    output.parent.mkdir(parents=True, exist_ok=True)
    qualification_output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(legacy_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    qualification_output.write_text(json.dumps(qualification_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "CURRENT_SESSION_CLOSE_RESULTS_OK"
        f" | output={output}"
        f" | qualification={qualification_output}"
        f" | priced={legacy_payload['priced_line_count']}/{legacy_payload['line_count']}"
        f" | funded={qualification_payload['funded_consensus_count']}/{qualification_payload['funded_line_count']}"
        f" | gate={funded_pass}"
    )
    if not funded_pass:
        raise SystemExit("Funded-position current-session close gate failed")


if __name__ == "__main__":
    main()
