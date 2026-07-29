from __future__ import annotations

import argparse
import json
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

import pandas as pd
import requests
import yaml


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected YAML object: {path}")
    return payload


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_series(series: pd.Series, report_date: date) -> pd.Series:
    result = series.dropna().astype(float).copy()
    index = pd.to_datetime(result.index, utc=True).tz_convert(None)
    result.index = index
    return result[result.index.date < report_date]


def extract_close(download: pd.DataFrame, provider_symbol: str) -> pd.Series:
    if download is None or download.empty:
        raise RuntimeError("Yahoo/yfinance returned no replay history")
    columns = download.columns
    if isinstance(columns, pd.MultiIndex):
        if provider_symbol in columns.get_level_values(0):
            frame = download[provider_symbol]
            if "Close" in frame:
                return frame["Close"]
        if provider_symbol in columns.get_level_values(-1):
            try:
                return download["Close"][provider_symbol]
            except Exception:
                pass
    if "Close" in download:
        close = download["Close"]
        if isinstance(close, pd.DataFrame) and provider_symbol in close:
            return close[provider_symbol]
        if isinstance(close, pd.Series):
            return close
    raise RuntimeError(f"Could not resolve adjusted close for {provider_symbol}")


def fetch_chart_series(provider_symbol: str, report_date: date) -> pd.Series:
    start = report_date - timedelta(days=550)
    period1 = int(datetime.combine(start, datetime.min.time(), tzinfo=timezone.utc).timestamp())
    period2 = int(datetime.combine(report_date + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc).timestamp())
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/"
        + quote(provider_symbol, safe="")
        + f"?period1={period1}&period2={period2}&interval=1d&events=history&includeAdjustedClose=true"
    )
    response = requests.get(
        url,
        timeout=30,
        headers={"User-Agent": "Mozilla/5.0 ETF-EU-Shadow-Validation/1.0"},
    )
    response.raise_for_status()
    payload = response.json()
    chart = payload.get("chart") if isinstance(payload, dict) else None
    results = chart.get("result") if isinstance(chart, dict) else None
    if not results or not isinstance(results[0], dict):
        error = chart.get("error") if isinstance(chart, dict) else None
        raise RuntimeError(f"Yahoo chart returned no result: {error}")
    result = results[0]
    timestamps = result.get("timestamp") or []
    indicators = result.get("indicators") if isinstance(result.get("indicators"), dict) else {}
    adjusted_rows = indicators.get("adjclose") or []
    quote_rows = indicators.get("quote") or []
    values = []
    if adjusted_rows and isinstance(adjusted_rows[0], dict):
        values = adjusted_rows[0].get("adjclose") or []
    if not values and quote_rows and isinstance(quote_rows[0], dict):
        values = quote_rows[0].get("close") or []
    pairs = [
        (datetime.fromtimestamp(int(timestamp), tz=timezone.utc), value)
        for timestamp, value in zip(timestamps, values)
        if value is not None
    ]
    if not pairs:
        raise RuntimeError("Yahoo chart returned no adjusted-close observations")
    return pd.Series([float(value) for _, value in pairs], index=[stamp for stamp, _ in pairs])


def failure_payload(config: dict[str, Any], universe_path: Path, symbols: dict[str, Any], diagnostics: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "etf_eu_transition_replay_panel_v1",
        "artifact_type": "etf_eu_transition_replay_price_panel",
        "generated_at_utc": utc_now(),
        "source_universe": str(universe_path),
        "source": "Yahoo/yfinance and Yahoo chart adjusted-close connectivity evidence",
        "source_quality": "non_authoritative_connectivity_only",
        "base_currency": config.get("base_currency"),
        "report_date": str(config.get("report_date")),
        "valid": False,
        "symbols": symbols,
        "diagnostics": diagnostics,
        "rows": [],
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "execution_authority": False,
        "optimization_authority": False,
    }


def build(universe_path: Path, output: Path) -> None:
    config = load_yaml(universe_path)
    if config.get("schema_version") != "etf_eu_transition_replay_universe_v1":
        raise RuntimeError("Unsupported replay-universe schema")
    symbols = config.get("symbols") if isinstance(config.get("symbols"), dict) else {}
    if not symbols:
        raise RuntimeError("Replay universe has no symbols")
    provider_symbols = [str(value) for value in symbols.values()]
    report_date = date.fromisoformat(str(config.get("report_date")))
    diagnostics: dict[str, Any] = {"batch": {}, "symbols": {}}
    series_by_ticker: dict[str, pd.Series] = {}

    history: pd.DataFrame | None = None
    try:
        import yfinance as yf

        history = yf.download(
            tickers=provider_symbols,
            period="18mo",
            interval="1d",
            auto_adjust=True,
            group_by="ticker",
            threads=False,
            progress=False,
        )
        diagnostics["batch"] = {"status": "completed", "empty": bool(history is None or history.empty)}
    except Exception as exc:
        diagnostics["batch"] = {"status": "failed", "error": f"{type(exc).__name__}: {exc}"}

    for index, (ticker, provider_symbol_value) in enumerate(symbols.items()):
        provider_symbol = str(provider_symbol_value)
        symbol_diagnostics: dict[str, Any] = {"provider_symbol": provider_symbol, "attempts": []}
        series: pd.Series | None = None
        if history is not None and not history.empty:
            try:
                candidate = normalize_series(extract_close(history, provider_symbol), report_date)
                if not candidate.empty:
                    series = candidate
                    symbol_diagnostics["attempts"].append({"source": "yfinance_batch", "status": "success", "rows": len(candidate)})
            except Exception as exc:
                symbol_diagnostics["attempts"].append({"source": "yfinance_batch", "status": "failed", "error": f"{type(exc).__name__}: {exc}"})
        if series is None:
            if index > 0:
                time.sleep(1.0)
            try:
                candidate = normalize_series(fetch_chart_series(provider_symbol, report_date), report_date)
                if candidate.empty:
                    raise RuntimeError("No completed observations before report date")
                series = candidate
                symbol_diagnostics["attempts"].append({"source": "yahoo_chart_json", "status": "success", "rows": len(candidate)})
            except Exception as exc:
                symbol_diagnostics["attempts"].append({"source": "yahoo_chart_json", "status": "failed", "error": f"{type(exc).__name__}: {exc}"})
        diagnostics["symbols"][str(ticker)] = symbol_diagnostics
        if series is not None:
            series_by_ticker[str(ticker)] = series

    missing = sorted(set(str(ticker) for ticker in symbols) - set(series_by_ticker))
    output.parent.mkdir(parents=True, exist_ok=True)
    if missing:
        payload = failure_payload(config, universe_path, symbols, diagnostics)
        payload["missing_tickers"] = missing
        output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        raise RuntimeError(f"Replay history unavailable for: {', '.join(missing)}")

    panel = pd.concat(series_by_ticker, axis=1, join="inner").dropna()
    maximum_days = int(config.get("maximum_common_trading_days") or 252)
    if len(panel) > maximum_days:
        panel = panel.tail(maximum_days)
    minimum_days = int(config.get("minimum_common_trading_days") or 60)
    if len(panel) < minimum_days:
        payload = failure_payload(config, universe_path, symbols, diagnostics)
        payload["common_trading_day_count"] = len(panel)
        payload["minimum_required_common_trading_days"] = minimum_days
        output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        raise RuntimeError(f"Only {len(panel)} common trading days; minimum is {minimum_days}")

    rows = [
        {
            "date": index.date().isoformat(),
            "adjusted_close_eur": {ticker: round(float(values[ticker]), 8) for ticker in panel.columns},
        }
        for index, values in panel.iterrows()
    ]
    payload = {
        "schema_version": "etf_eu_transition_replay_panel_v1",
        "artifact_type": "etf_eu_transition_replay_price_panel",
        "generated_at_utc": utc_now(),
        "source_universe": str(universe_path),
        "source": "Yahoo/yfinance and Yahoo chart adjusted-close connectivity evidence",
        "source_quality": "non_authoritative_connectivity_only",
        "base_currency": config.get("base_currency"),
        "report_date": str(config.get("report_date")),
        "valid": True,
        "close_selection_policy": "common_adjusted_daily_closes_strictly_before_report_date",
        "common_start_date": rows[0]["date"],
        "common_end_date": rows[-1]["date"],
        "common_trading_day_count": len(rows),
        "symbols": symbols,
        "diagnostics": diagnostics,
        "rows": rows,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "execution_authority": False,
        "optimization_authority": False,
    }
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build transition replay price panel")
    parser.add_argument("--universe", type=Path, default=Path("config/etf_eu_transition_replay_universe.yml"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.universe, args.output)


if __name__ == "__main__":
    main()
