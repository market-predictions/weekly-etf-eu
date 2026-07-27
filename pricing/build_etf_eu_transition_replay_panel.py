from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected YAML object: {path}")
    return payload


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def build(universe_path: Path, output: Path) -> None:
    config = load_yaml(universe_path)
    if config.get("schema_version") != "etf_eu_transition_replay_universe_v1":
        raise RuntimeError("Unsupported replay-universe schema")
    symbols = config.get("symbols") if isinstance(config.get("symbols"), dict) else {}
    if not symbols:
        raise RuntimeError("Replay universe has no symbols")
    provider_symbols = [str(value) for value in symbols.values()]

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
    report_date = date.fromisoformat(str(config.get("report_date")))
    series_by_ticker: dict[str, pd.Series] = {}
    for ticker, provider_symbol in symbols.items():
        series = extract_close(history, str(provider_symbol)).dropna().astype(float)
        normalized_index = pd.to_datetime(series.index).tz_localize(None)
        series.index = normalized_index
        series = series[series.index.date < report_date]
        if series.empty:
            raise RuntimeError(f"No completed adjusted closes for {ticker}")
        series_by_ticker[str(ticker)] = series

    panel = pd.concat(series_by_ticker, axis=1, join="inner").dropna()
    maximum_days = int(config.get("maximum_common_trading_days") or 252)
    if len(panel) > maximum_days:
        panel = panel.tail(maximum_days)
    minimum_days = int(config.get("minimum_common_trading_days") or 60)
    if len(panel) < minimum_days:
        raise RuntimeError(f"Only {len(panel)} common trading days; minimum is {minimum_days}")

    rows = []
    for index, values in panel.iterrows():
        rows.append({
            "date": index.date().isoformat(),
            "adjusted_close_eur": {ticker: round(float(values[ticker]), 8) for ticker in panel.columns},
        })
    payload = {
        "schema_version": "etf_eu_transition_replay_panel_v1",
        "artifact_type": "etf_eu_transition_replay_price_panel",
        "generated_at_utc": utc_now(),
        "source_universe": str(universe_path),
        "source": "Yahoo/yfinance adjusted-close connectivity evidence",
        "source_quality": "non_authoritative_connectivity_only",
        "base_currency": config.get("base_currency"),
        "report_date": str(config.get("report_date")),
        "close_selection_policy": "common_adjusted_daily_closes_strictly_before_report_date",
        "common_start_date": rows[0]["date"],
        "common_end_date": rows[-1]["date"],
        "common_trading_day_count": len(rows),
        "symbols": symbols,
        "rows": rows,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "execution_authority": False,
        "optimization_authority": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
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
