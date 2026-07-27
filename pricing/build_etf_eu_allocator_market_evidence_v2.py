from __future__ import annotations

import argparse
import csv
import io
import json
import math
import statistics
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests
import yaml


YAHOO_HOSTS = ("query2.finance.yahoo.com", "query1.finance.yahoo.com")
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36",
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "en-US,en;q=0.9",
}


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        result = float(value)
        return result if math.isfinite(result) else default
    except (TypeError, ValueError):
        return default


def _registry_index(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("registry_id")): row
        for row in (registry.get("funds") or [])
        if isinstance(row, dict) and row.get("registry_id")
    }


def _primary_line(fund: dict[str, Any]) -> dict[str, Any] | None:
    verified = [
        row
        for row in (fund.get("trading_lines") or [])
        if isinstance(row, dict)
        and str(row.get("line_verification_status") or "").startswith("verified_ucits_trading_line")
        and str(row.get("trading_currency") or "").upper() == "EUR"
    ]
    for row in verified:
        if row.get("primary_line") is True:
            return row
    return verified[0] if verified else None


def _provider_symbols(line: dict[str, Any]) -> list[str]:
    values: list[str] = []
    raw_many = line.get("provider_symbols_yahoo")
    if isinstance(raw_many, list):
        values.extend(str(item).strip() for item in raw_many if str(item).strip())
    for key in ("pricing_symbol_yahoo", "provider_symbol_yahoo"):
        value = str(line.get(key) or "").strip()
        if value:
            values.append(value)
    ticker = str(line.get("exchange_ticker") or "").strip()
    if ticker and str(line.get("venue_code") or "").upper() == "XETR":
        values.append(f"{ticker}.DE")
    result: list[str] = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def _mapping_candidate(mapping: dict[str, Any], registry: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    candidates = [row for row in (mapping.get("candidates") or []) if isinstance(row, dict)]
    candidates.sort(key=lambda row: row.get("preferred") is not True)
    for candidate in candidates:
        fund = registry.get(str(candidate.get("registry_id") or ""))
        if fund:
            return fund
    return None


def _identity_gate(fund: dict[str, Any] | None, line: dict[str, Any] | None) -> tuple[bool, list[str]]:
    blockers: list[str] = []
    if not fund:
        return False, ["fund_not_mapped"]
    if str(fund.get("instrument_type") or "") != "UCITS ETF":
        blockers.append("product_type_not_ucits_etf")
    if not str(fund.get("isin") or "").strip() or str(fund.get("isin") or "").upper() == "TBD":
        blockers.append("isin_missing")
    if str(fund.get("ucits_status") or "") not in {"confirmed", "confirmed_by_fund_name"}:
        blockers.append("ucits_status_unconfirmed")
    if str(fund.get("priips_kid_status") or "") != "available":
        blockers.append("priips_kid_unavailable")
    if not line:
        blockers.append("verified_eur_trading_line_missing")
    return not blockers, blockers


def _session_rows_from_yahoo(payload: dict[str, Any], report_date: date) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    chart = payload.get("chart") if isinstance(payload.get("chart"), dict) else {}
    results = chart.get("result") if isinstance(chart.get("result"), list) else []
    if not results or not isinstance(results[0], dict):
        error = chart.get("error")
        raise RuntimeError(f"yahoo_chart_no_result:{error}")
    result = results[0]
    timestamps = result.get("timestamp") if isinstance(result.get("timestamp"), list) else []
    indicators = result.get("indicators") if isinstance(result.get("indicators"), dict) else {}
    quote_rows = indicators.get("quote") if isinstance(indicators.get("quote"), list) else []
    quote_row = quote_rows[0] if quote_rows and isinstance(quote_rows[0], dict) else {}
    closes = quote_row.get("close") if isinstance(quote_row.get("close"), list) else []
    volumes = quote_row.get("volume") if isinstance(quote_row.get("volume"), list) else []
    rows: list[dict[str, Any]] = []
    for index, timestamp in enumerate(timestamps):
        try:
            session_date = datetime.fromtimestamp(int(timestamp), timezone.utc).date()
        except Exception:
            continue
        close_value = _num(closes[index] if index < len(closes) else None)
        volume_value = max(0.0, _num(volumes[index] if index < len(volumes) else None))
        if session_date < report_date and close_value > 0:
            rows.append({"date": session_date.isoformat(), "close": close_value, "volume": volume_value})
    meta = result.get("meta") if isinstance(result.get("meta"), dict) else {}
    return rows, meta


def _fetch_yahoo_chart(session: requests.Session, symbol: str, report_date: date) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    attempts: list[dict[str, Any]] = []
    for host_index, host in enumerate(YAHOO_HOSTS):
        url = f"https://{host}/v8/finance/chart/{quote(symbol, safe='')}"
        params = {"range": "6mo", "interval": "1d", "events": "history", "includeAdjustedClose": "true"}
        for attempt in range(1, 3):
            if host_index or attempt > 1:
                time.sleep(3.0 if attempt == 1 else 8.0)
            try:
                response = session.get(url, params=params, headers=REQUEST_HEADERS, timeout=30)
                attempts.append({"source": "yahoo_chart", "host": host, "symbol": symbol, "attempt": attempt, "http_status": response.status_code})
                if response.status_code == 429:
                    continue
                response.raise_for_status()
                rows, meta = _session_rows_from_yahoo(response.json(), report_date)
                if rows:
                    return rows, meta, attempts
                attempts[-1]["error"] = "no_eligible_rows"
            except Exception as exc:
                attempts.append({"source": "yahoo_chart", "host": host, "symbol": symbol, "attempt": attempt, "error": type(exc).__name__})
    raise RuntimeError("yahoo_chart_exhausted")


def _stooq_symbol_candidates(symbol: str) -> list[str]:
    stem = symbol.lower().replace(".de", "")
    return [f"{stem}.de", stem]


def _fetch_stooq(session: requests.Session, symbol: str, report_date: date) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    attempts: list[dict[str, Any]] = []
    start_date = (report_date - timedelta(days=220)).strftime("%Y%m%d")
    end_date = report_date.strftime("%Y%m%d")
    for candidate in _stooq_symbol_candidates(symbol):
        time.sleep(1.5)
        url = "https://stooq.com/q/d/l/"
        params = {"s": candidate, "i": "d", "d1": start_date, "d2": end_date}
        try:
            response = session.get(url, params=params, headers=REQUEST_HEADERS, timeout=30)
            attempts.append({"source": "stooq_csv", "symbol": candidate, "http_status": response.status_code})
            response.raise_for_status()
            reader = csv.DictReader(io.StringIO(response.text))
            rows: list[dict[str, Any]] = []
            for raw in reader:
                try:
                    session_date = date.fromisoformat(str(raw.get("Date") or ""))
                except ValueError:
                    continue
                close_value = _num(raw.get("Close"))
                volume_value = max(0.0, _num(raw.get("Volume")))
                if session_date < report_date and close_value > 0:
                    rows.append({"date": session_date.isoformat(), "close": close_value, "volume": volume_value})
            if rows:
                return rows, attempts
            attempts[-1]["error"] = "no_eligible_rows"
        except Exception as exc:
            attempts.append({"source": "stooq_csv", "symbol": candidate, "error": type(exc).__name__})
    raise RuntimeError("stooq_exhausted")


def _summarize_rows(
    rows: list[dict[str, Any]],
    *,
    liquidity_sessions: int,
    risk_sessions: int,
    selected_symbol: str,
    selected_source: str,
    attempts: list[dict[str, Any]],
    source_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rows = sorted(rows, key=lambda row: str(row.get("date")))
    latest = rows[-1]
    liquidity_rows = rows[-max(1, liquidity_sessions):]
    traded_values = [_num(row.get("close")) * _num(row.get("volume")) for row in liquidity_rows if _num(row.get("volume")) > 0]
    volumes = [_num(row.get("volume")) for row in liquidity_rows if _num(row.get("volume")) > 0]
    nonzero_ratio = len(traded_values) / len(liquidity_rows) if liquidity_rows else 0.0
    risk_rows = rows[-max(2, risk_sessions):]
    closes = [_num(row.get("close")) for row in risk_rows if _num(row.get("close")) > 0]
    log_returns = [math.log(closes[index] / closes[index - 1]) for index in range(1, len(closes)) if closes[index - 1] > 0]
    annualized_volatility = statistics.stdev(log_returns) * math.sqrt(252) * 100.0 if len(log_returns) >= 2 else None
    peak = 0.0
    drawdowns: list[float] = []
    for close_value in closes:
        peak = max(peak, close_value)
        if peak > 0:
            drawdowns.append((close_value / peak - 1.0) * 100.0)
    return {
        "status": "priced_completed_close",
        "selected_symbol": selected_symbol,
        "selected_source": selected_source,
        "source_quality": "non_authoritative_market_observation_only",
        "source_attempts": attempts,
        "source_meta": source_meta or {},
        "completed_close_date": latest["date"],
        "completed_close_price_eur": round(_num(latest["close"]), 8),
        "liquidity_session_count": len(liquidity_rows),
        "median_daily_volume_units": round(statistics.median(volumes), 4) if volumes else 0.0,
        "median_daily_traded_value_eur": round(statistics.median(traded_values), 2) if traded_values else 0.0,
        "nonzero_volume_session_ratio": round(nonzero_ratio, 6),
        "annualized_volatility_pct": round(annualized_volatility, 4) if annualized_volatility is not None else None,
        "maximum_drawdown_pct": round(min(drawdowns), 4) if drawdowns else None,
        "quote_bid_eur": None,
        "quote_ask_eur": None,
        "quote_spread_bps": None,
        "quote_observed_at_utc": None,
        "quote_errors": ["reliable_bid_ask_not_available_from_daily_history_adapter"],
        "blockers": [],
    }


def _fetch_symbol(
    session: requests.Session,
    symbols: list[str],
    report_date: date,
    liquidity_sessions: int,
    risk_sessions: int,
) -> dict[str, Any]:
    errors: list[str] = []
    all_attempts: list[dict[str, Any]] = []
    for symbol_index, symbol in enumerate(symbols):
        if symbol_index:
            time.sleep(2.0)
        try:
            rows, meta, attempts = _fetch_yahoo_chart(session, symbol, report_date)
            all_attempts.extend(attempts)
            return _summarize_rows(
                rows,
                liquidity_sessions=liquidity_sessions,
                risk_sessions=risk_sessions,
                selected_symbol=symbol,
                selected_source="yahoo_chart_api",
                attempts=all_attempts,
                source_meta={"exchange_name": meta.get("exchangeName"), "currency": meta.get("currency"), "instrument_type": meta.get("instrumentType")},
            )
        except Exception as exc:
            errors.append(f"{symbol}:yahoo:{type(exc).__name__}")
        try:
            rows, attempts = _fetch_stooq(session, symbol, report_date)
            all_attempts.extend(attempts)
            return _summarize_rows(
                rows,
                liquidity_sessions=liquidity_sessions,
                risk_sessions=risk_sessions,
                selected_symbol=symbol,
                selected_source="stooq_daily_csv",
                attempts=all_attempts,
            )
        except Exception as exc:
            errors.append(f"{symbol}:stooq:{type(exc).__name__}")
    return {"status": "fetch_failed", "blockers": errors or ["no_provider_symbols"], "attempted_symbols": symbols, "source_attempts": all_attempts}


def _liquidity_threshold(target_weight: float, policy: dict[str, Any]) -> float:
    thresholds = ((policy.get("liquidity") or {}).get("thresholds_eur_per_day") or {})
    if target_weight > 10.0:
        return _num(thresholds.get("above_10_pct"))
    if target_weight >= 3.0:
        return _num(thresholds.get("from_3_to_10_pct"))
    return _num(thresholds.get("below_3_pct"))


def build(
    shared_target: dict[str, Any],
    portfolio: dict[str, Any],
    registry_payload: dict[str, Any],
    mapping_payload: dict[str, Any],
    policy: dict[str, Any],
    report_date: date,
) -> dict[str, Any]:
    registry = _registry_index(registry_payload)
    mappings = mapping_payload.get("exposures") if isinstance(mapping_payload.get("exposures"), dict) else {}
    targets = {
        str(row.get("exposure_id")): _num(row.get("target_weight_pct"))
        for row in (shared_target.get("exposure_targets") or [])
        if isinstance(row, dict) and row.get("exposure_id")
    }
    liquidity_sessions = int(((policy.get("liquidity") or {}).get("lookback_sessions") or 20))
    risk_sessions = int(((policy.get("risk") or {}).get("volatility_lookback_sessions") or 60))
    maximum_spread = _num((policy.get("liquidity") or {}).get("maximum_quote_spread_bps"), 60.0)
    session = requests.Session()
    target_rows: list[dict[str, Any]] = []
    for row_index, (exposure_id, target_weight) in enumerate(targets.items()):
        if row_index:
            time.sleep(2.0)
        mapping = mappings.get(exposure_id) if isinstance(mappings.get(exposure_id), dict) else {}
        fund = _mapping_candidate(mapping, registry)
        line = _primary_line(fund or {})
        identity_ok, identity_blockers = _identity_gate(fund, line)
        symbols = _provider_symbols(line or {})
        market = _fetch_symbol(session, symbols, report_date, liquidity_sessions, risk_sessions) if identity_ok else {
            "status": "not_fetched_identity_blocked", "blockers": identity_blockers, "attempted_symbols": symbols
        }
        threshold = _liquidity_threshold(target_weight, policy)
        traded_value = _num(market.get("median_daily_traded_value_eur"))
        liquidity_pass = bool(market.get("status") == "priced_completed_close" and traded_value >= threshold)
        spread = market.get("quote_spread_bps")
        spread_status = "unavailable_review_required" if spread is None else ("pass" if _num(spread) <= maximum_spread else "fail")
        hard_blockers = list(identity_blockers) + list(market.get("blockers") or [])
        review_warnings: list[str] = []
        if market.get("status") != "priced_completed_close":
            hard_blockers.append("completed_close_missing")
        if market.get("status") == "priced_completed_close" and not liquidity_pass:
            hard_blockers.append("liquidity_below_threshold")
        if spread_status == "fail":
            hard_blockers.append("quote_spread_above_threshold")
        if spread_status == "unavailable_review_required":
            review_warnings.append("quote_spread_unavailable")
        status = "blocked"
        if identity_ok and market.get("status") == "priced_completed_close" and liquidity_pass and spread_status == "pass":
            status = "eligible_shadow_allocator"
        elif identity_ok and market.get("status") == "priced_completed_close" and liquidity_pass and spread_status == "unavailable_review_required":
            status = "eligible_pending_spread_review"
        target_rows.append({
            "exposure_id": exposure_id,
            "donor_target_weight_pct": target_weight,
            "registry_id": fund.get("registry_id") if fund else None,
            "fund_name": fund.get("fund_name") if fund else None,
            "isin": fund.get("isin") if fund else None,
            "ter_pct": fund.get("ter_pct") if fund else None,
            "replication_method": fund.get("replication_method") if fund else None,
            "exchange": line.get("exchange") if line else None,
            "venue_code": line.get("venue_code") if line else None,
            "exchange_ticker": line.get("exchange_ticker") if line else None,
            "trading_currency": line.get("trading_currency") if line else None,
            "identity_gate_passed": identity_ok,
            "liquidity_threshold_eur_per_day": threshold,
            "liquidity_gate_passed": liquidity_pass,
            "spread_status": spread_status,
            "allocator_market_status": status,
            "blockers": sorted(set(hard_blockers)),
            "review_warnings": sorted(set(review_warnings)),
            "market": market,
        })

    incumbent_rows: list[dict[str, Any]] = []
    for position in portfolio.get("positions") or []:
        if not isinstance(position, dict):
            continue
        isin = str(position.get("isin") or "")
        fund = next((row for row in registry.values() if str(row.get("isin") or "") == isin), None)
        line = None
        if fund:
            ticker = str(position.get("ticker") or position.get("exchange_ticker") or "").upper()
            lines = [row for row in (fund.get("trading_lines") or []) if isinstance(row, dict)]
            line = next((row for row in lines if str(row.get("exchange_ticker") or "").upper() == ticker), None) or _primary_line(fund)
        symbols = _provider_symbols(line or {})
        market = _fetch_symbol(session, symbols, report_date, liquidity_sessions, risk_sessions) if symbols else {
            "status": "fetch_failed", "blockers": ["provider_symbol_missing"], "attempted_symbols": []
        }
        incumbent_rows.append({
            "ticker": position.get("ticker") or position.get("exchange_ticker"),
            "isin": isin,
            "fund_name": position.get("fund_name"),
            "shares": position.get("shares"),
            "current_weight_pct": position.get("current_weight_pct"),
            "registry_id": fund.get("registry_id") if fund else None,
            "market": market,
        })

    return {
        "schema_version": "etf_eu_allocator_market_evidence_v1",
        "artifact_type": "etf_eu_allocator_market_evidence",
        "generated_at_utc": _utc_now(),
        "report_date": report_date.isoformat(),
        "completed_close_policy": "latest_daily_bar_strictly_before_report_date",
        "source_policy": ["yahoo_chart_api", "stooq_daily_csv_fallback"],
        "source_quality": "non_authoritative_connectivity_and_market_observation_only",
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "target_rows": target_rows,
        "incumbent_rows": incumbent_rows,
        "summary": {
            "target_count": len(target_rows),
            "priced_count": sum(1 for row in target_rows if (row.get("market") or {}).get("status") == "priced_completed_close"),
            "liquidity_pass_count": sum(1 for row in target_rows if row.get("liquidity_gate_passed") is True),
            "spread_pass_count": sum(1 for row in target_rows if row.get("spread_status") == "pass"),
            "eligible_count": sum(1 for row in target_rows if row.get("allocator_market_status") == "eligible_shadow_allocator"),
            "eligible_pending_spread_count": sum(1 for row in target_rows if row.get("allocator_market_status") == "eligible_pending_spread_review"),
            "blocked_count": sum(1 for row in target_rows if row.get("allocator_market_status") == "blocked"),
            "source_counts": {
                source: sum(1 for row in target_rows if (row.get("market") or {}).get("selected_source") == source)
                for source in ("yahoo_chart_api", "stooq_daily_csv")
            },
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build multi-source completed-close and liquidity evidence for the EU allocator")
    parser.add_argument("--shared-portfolio-target", type=Path, required=True)
    parser.add_argument("--portfolio-state", type=Path, default=Path("output/etf_eu_portfolio_state.json"))
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--mapping", type=Path, default=Path("config/shared_exposure_ucits_map.yml"))
    parser.add_argument("--policy", type=Path, default=Path("config/etf_eu_allocator_policy.yml"))
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build(
        shared_target=_load_json(args.shared_portfolio_target),
        portfolio=_load_json(args.portfolio_state),
        registry_payload=_load_yaml(args.registry),
        mapping_payload=_load_yaml(args.mapping),
        policy=_load_yaml(args.policy),
        report_date=date.fromisoformat(args.report_date),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], sort_keys=True))
    print(args.output)


if __name__ == "__main__":
    main()
