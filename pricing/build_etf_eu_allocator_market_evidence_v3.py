from __future__ import annotations

import argparse
import csv
import io
import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests

from pricing import build_etf_eu_allocator_market_evidence_v2 as base


def _fetch_yahoo_chart_fast(
    session: requests.Session,
    symbol: str,
    report_date: date,
) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    attempts: list[dict[str, Any]] = []
    for host in base.YAHOO_HOSTS:
        url = f"https://{host}/v8/finance/chart/{quote(symbol, safe='')}"
        params = {"range": "6mo", "interval": "1d", "events": "history", "includeAdjustedClose": "true"}
        try:
            response = session.get(url, params=params, headers=base.REQUEST_HEADERS, timeout=7)
            attempt = {"source": "yahoo_chart", "host": host, "symbol": symbol, "attempt": 1, "http_status": response.status_code}
            attempts.append(attempt)
            if response.status_code == 429:
                attempt["error"] = "rate_limited"
                continue
            response.raise_for_status()
            rows, meta = base._session_rows_from_yahoo(response.json(), report_date)
            if rows:
                return rows, meta, attempts
            attempt["error"] = "no_eligible_rows"
        except Exception as exc:
            attempts.append({"source": "yahoo_chart", "host": host, "symbol": symbol, "attempt": 1, "error": type(exc).__name__})
    raise RuntimeError("yahoo_chart_fast_exhausted")


def _fetch_stooq_fast(
    session: requests.Session,
    symbol: str,
    report_date: date,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    attempts: list[dict[str, Any]] = []
    start_date = (report_date - timedelta(days=220)).strftime("%Y%m%d")
    end_date = report_date.strftime("%Y%m%d")
    candidates = base._stooq_symbol_candidates(symbol)
    for candidate in candidates[:1]:
        try:
            response = session.get(
                "https://stooq.com/q/d/l/",
                params={"s": candidate, "i": "d", "d1": start_date, "d2": end_date},
                headers=base.REQUEST_HEADERS,
                timeout=7,
            )
            attempt = {"source": "stooq_csv", "symbol": candidate, "http_status": response.status_code}
            attempts.append(attempt)
            response.raise_for_status()
            rows: list[dict[str, Any]] = []
            for raw in csv.DictReader(io.StringIO(response.text)):
                try:
                    session_date = date.fromisoformat(str(raw.get("Date") or ""))
                except ValueError:
                    continue
                close_value = base._num(raw.get("Close"))
                volume_value = max(0.0, base._num(raw.get("Volume")))
                if session_date < report_date and close_value > 0:
                    rows.append({"date": session_date.isoformat(), "close": close_value, "volume": volume_value})
            if rows:
                return rows, attempts
            attempt["error"] = "no_eligible_rows"
        except Exception as exc:
            attempts.append({"source": "stooq_csv", "symbol": candidate, "error": type(exc).__name__})
    raise RuntimeError("stooq_fast_exhausted")


def _reuse_incumbent_completed_close(
    portfolio: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for position in portfolio.get("positions") or []:
        if not isinstance(position, dict):
            continue
        price = base._num(position.get("current_price_local"))
        price_date = position.get("price_date")
        rows.append({
            "ticker": position.get("ticker") or position.get("exchange_ticker"),
            "isin": position.get("isin"),
            "fund_name": position.get("fund_name"),
            "shares": position.get("shares"),
            "current_weight_pct": position.get("current_weight_pct"),
            "registry_id": None,
            "market": {
                "status": "priced_completed_close" if price > 0 and price_date else "fetch_failed",
                "selected_source": "existing_verified_portfolio_completed_close",
                "completed_close_date": price_date,
                "completed_close_price_eur": price if price > 0 else None,
                "liquidity_session_count": 0,
                "median_daily_volume_units": 0.0,
                "median_daily_traded_value_eur": 0.0,
                "nonzero_volume_session_ratio": 0.0,
                "quote_spread_bps": None,
                "blockers": [] if price > 0 and price_date else ["incumbent_completed_close_missing"],
            },
        })
    return rows


def build_fast(
    shared_target: dict[str, Any],
    portfolio: dict[str, Any],
    registry_payload: dict[str, Any],
    mapping_payload: dict[str, Any],
    policy: dict[str, Any],
    report_date: date,
) -> dict[str, Any]:
    original_yahoo = base._fetch_yahoo_chart
    original_stooq = base._fetch_stooq
    try:
        base._fetch_yahoo_chart = _fetch_yahoo_chart_fast
        base._fetch_stooq = _fetch_stooq_fast
        result = base.build(
            shared_target=shared_target,
            portfolio={**portfolio, "positions": []},
            registry_payload=registry_payload,
            mapping_payload=mapping_payload,
            policy=policy,
            report_date=report_date,
        )
    finally:
        base._fetch_yahoo_chart = original_yahoo
        base._fetch_stooq = original_stooq
    result["incumbent_rows"] = _reuse_incumbent_completed_close(portfolio)
    result["market_adapter_version"] = "bounded_multi_source_v3"
    result["incumbent_price_policy"] = "reuse_existing_verified_completed_close_no_redundant_network_fetch"
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Build bounded-time multi-source EU allocator market evidence")
    parser.add_argument("--shared-portfolio-target", type=Path, required=True)
    parser.add_argument("--portfolio-state", type=Path, default=Path("output/etf_eu_portfolio_state.json"))
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--mapping", type=Path, default=Path("config/shared_exposure_ucits_map.yml"))
    parser.add_argument("--policy", type=Path, default=Path("config/etf_eu_allocator_policy.yml"))
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build_fast(
        shared_target=base._load_json(args.shared_portfolio_target),
        portfolio=base._load_json(args.portfolio_state),
        registry_payload=base._load_yaml(args.registry),
        mapping_payload=base._load_yaml(args.mapping),
        policy=base._load_yaml(args.policy),
        report_date=date.fromisoformat(args.report_date),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], sort_keys=True))
    print(args.output)


if __name__ == "__main__":
    main()
