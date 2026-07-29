from __future__ import annotations

import argparse
import json
import math
from datetime import date, datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any

import yaml


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def usable_number(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def completed_rows(history: Any, report_date: date) -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    if history is None or getattr(history, "empty", True):
        return rows
    for index, item in history.iterrows():
        observed_date = date.fromisoformat(str(index)[:10])
        if observed_date >= report_date:
            continue
        close = usable_number(item.get("Close"))
        volume = usable_number(item.get("Volume"))
        if close is None or close <= 0:
            continue
        rows.append({
            "date": observed_date.isoformat(),
            "close": close,
            "volume": max(volume or 0.0, 0.0),
            "traded_value": close * max(volume or 0.0, 0.0),
        })
    rows.sort(key=lambda row: str(row["date"]))
    return rows


def build_row(line: dict[str, Any], report_date: date) -> dict[str, Any]:
    base = {
        "exposure_id": line.get("exposure_id"),
        "registry_id": line.get("registry_id"),
        "ticker": line.get("ticker"),
        "isin": line.get("isin"),
        "exchange": line.get("exchange"),
        "venue_code": line.get("venue_code"),
        "currency": line.get("currency"),
        "provider_symbol_yahoo": line.get("provider_symbol_yahoo"),
        "candidate_role": line.get("candidate_role"),
        "source": "Yahoo/yfinance connectivity evidence",
        "source_quality": "non_authoritative_connectivity_only",
        "valuation_grade": False,
        "funding_authority": False,
    }
    try:
        import yfinance as yf
        history = yf.Ticker(str(line.get("provider_symbol_yahoo") or "")).history(
            period="3mo", interval="1d", auto_adjust=False
        )
        eligible = completed_rows(history, report_date)
    except Exception as exc:
        return {
            **base,
            "status": "fetch_failed",
            "blockers": [f"yfinance_exception:{type(exc).__name__}"],
            "completed_close": False,
        }
    if not eligible:
        return {
            **base,
            "status": "fetch_failed",
            "blockers": ["no_completed_daily_rows_before_report_date"],
            "completed_close": False,
        }
    latest = eligible[-1]
    recent = eligible[-20:]
    closes = [float(row["close"]) for row in recent]
    traded_values = [float(row["traded_value"]) for row in recent if float(row["traded_value"]) > 0]
    returns: list[float] = []
    for prior, current in zip(closes, closes[1:]):
        if prior > 0:
            returns.append(current / prior - 1.0)
    volatility = None
    if len(returns) >= 2:
        mean = sum(returns) / len(returns)
        variance = sum((value - mean) ** 2 for value in returns) / (len(returns) - 1)
        volatility = math.sqrt(variance) * math.sqrt(252.0) * 100.0
    close_date = date.fromisoformat(str(latest["date"]))
    age_days = (report_date - close_date).days
    median_traded_value = median(traded_values) if traded_values else 0.0
    return {
        **base,
        "status": "priced_non_authoritative",
        "completed_close": close_date < report_date,
        "close_date": close_date.isoformat(),
        "close_price": round(float(latest["close"]), 8),
        "price_age_calendar_days": age_days,
        "observed_daily_rows": len(eligible),
        "liquidity_window_rows": len(recent),
        "median_daily_volume_20d": round(median([float(row["volume"]) for row in recent]), 2),
        "median_daily_traded_value_eur_20d": round(median_traded_value, 2),
        "annualized_close_volatility_pct_20d": round(volatility, 4) if volatility is not None else None,
        "whole_share_price_eur": round(float(latest["close"]), 8),
        "blockers": [],
    }


def build(basket: Path, report_date: date, output: Path) -> None:
    config = load_yaml(basket)
    rows = [build_row(dict(line), report_date) for line in (config.get("lines") or []) if isinstance(line, dict)]
    priced = [row for row in rows if row.get("status") == "priced_non_authoritative"]
    payload = {
        "schema_version": "etf_eu_transition_evidence_v1",
        "artifact_type": "etf_eu_transition_pricing_liquidity_shadow",
        "report_date": report_date.isoformat(),
        "generated_at_utc": utc_now(),
        "source_basket": str(basket),
        "authority": {
            "shadow_only": True,
            "portfolio_mutation": False,
            "funding_authority": False,
            "execution_authority": False,
            "production_delivery_authority": False,
        },
        "methodology": {
            "close_policy": "latest_daily_bar_strictly_before_report_date",
            "liquidity_proxy": "median_close_times_volume_over_latest_20_completed_daily_rows",
            "liquidity_is_not_spread_or_market_impact_evidence": True,
            "source_quality": "non_authoritative_connectivity_only",
        },
        "line_count": len(rows),
        "priced_line_count": len(priced),
        "completed_close_gate_passed": bool(priced and all(row.get("completed_close") is True for row in priced)),
        "rows": rows,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--basket", type=Path, default=Path("config/etf_eu_transition_evidence_basket.yml"))
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.basket, date.fromisoformat(args.report_date), args.output)


if __name__ == "__main__":
    main()
