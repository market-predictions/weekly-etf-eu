from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def normalize_ticker(value: Any) -> str:
    ticker = str(value or "").strip().upper()
    return "L0CK" if ticker == "LOCK" else ticker


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def panel_frame(panel: dict[str, Any]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for row in panel.get("rows") or []:
        if not isinstance(row, dict):
            continue
        values = row.get("adjusted_close_eur") if isinstance(row.get("adjusted_close_eur"), dict) else {}
        normalized: dict[str, float] = {}
        for key, value in values.items():
            ticker = normalize_ticker(key)
            if ticker in normalized:
                raise RuntimeError(f"Replay panel ticker alias collision: {ticker}")
            normalized[ticker] = num(value)
        rows.append({"date": row.get("date"), **normalized})
    frame = pd.DataFrame(rows)
    if frame.empty:
        raise RuntimeError("Replay panel has no rows")
    frame["date"] = pd.to_datetime(frame["date"])
    frame = frame.set_index("date").sort_index()
    return frame


def current_composition(portfolio: dict[str, Any]) -> dict[str, Any]:
    nav = num(portfolio.get("nav_eur"))
    assets: dict[str, float] = {}
    for row in portfolio.get("positions") or []:
        if not isinstance(row, dict):
            continue
        ticker = normalize_ticker(row.get("ticker") or row.get("exchange_ticker"))
        if ticker:
            assets[ticker] = assets.get(ticker, 0.0) + num(row.get("market_value_eur"))
    return {
        "variant_id": "current_eu_portfolio",
        "asset_values_eur": assets,
        "cash_eur_before_cost": num(portfolio.get("cash_eur")),
        "estimated_transaction_cost_eur": 0.0,
        "nav_eur": nav,
        "source": "current_portfolio_state",
    }


def allocator_composition(variant: dict[str, Any], nav: float) -> dict[str, Any]:
    assets: dict[str, float] = {}
    for row in variant.get("allocation_rows") or []:
        if not isinstance(row, dict):
            continue
        order = row.get("order") if isinstance(row.get("order"), dict) else {}
        candidate = row.get("candidate") if isinstance(row.get("candidate"), dict) else {}
        ticker = normalize_ticker(candidate.get("ticker"))
        value = num(order.get("target_market_value_eur"))
        if ticker and value > 0:
            assets[ticker] = assets.get(ticker, 0.0) + value
    for row in variant.get("legacy_rows") or []:
        if not isinstance(row, dict):
            continue
        ticker = normalize_ticker(row.get("ticker"))
        value = num(row.get("target_market_value_eur"))
        if ticker and value > 0:
            assets[ticker] = assets.get(ticker, 0.0) + value
    summary = variant.get("summary") if isinstance(variant.get("summary"), dict) else {}
    cost = num(summary.get("estimated_transaction_cost_eur"))
    projected_cash_after_cost = num(summary.get("projected_cash_eur"))
    return {
        "variant_id": variant.get("variant_id"),
        "asset_values_eur": assets,
        "cash_eur_before_cost": projected_cash_after_cost + cost,
        "estimated_transaction_cost_eur": cost,
        "nav_eur": nav,
        "source": "allocator_variant",
    }


def composition_weights(composition: dict[str, Any]) -> tuple[dict[str, float], float, float]:
    assets = composition.get("asset_values_eur") if isinstance(composition.get("asset_values_eur"), dict) else {}
    cash = num(composition.get("cash_eur_before_cost"))
    nav = num(composition.get("nav_eur"))
    cost = num(composition.get("estimated_transaction_cost_eur"))
    pre_cost_total = sum(num(value) for value in assets.values()) + cash
    if pre_cost_total <= 0 or nav <= 0:
        raise RuntimeError(f"Invalid composition totals for {composition.get('variant_id')}")
    weights = {normalize_ticker(ticker): num(value) / pre_cost_total for ticker, value in assets.items()}
    cash_weight = cash / pre_cost_total
    cost_pct_nav = cost / nav
    return weights, cash_weight, cost_pct_nav


def max_drawdown(wealth: pd.Series) -> float:
    running_max = wealth.cummax()
    drawdown = wealth / running_max - 1.0
    return float(drawdown.min())


def replay_composition(composition: dict[str, Any], returns: pd.DataFrame) -> dict[str, Any]:
    weights, cash_weight, cost_pct_nav = composition_weights(composition)
    missing = sorted(set(weights) - set(returns.columns))
    if missing:
        raise RuntimeError(f"Replay panel missing symbols for {composition.get('variant_id')}: {', '.join(missing)}")
    daily = pd.Series(0.0, index=returns.index)
    for ticker, weight in weights.items():
        daily = daily + returns[ticker] * weight
    wealth_gross = (1.0 + daily).cumprod()
    wealth_net = wealth_gross * (1.0 - cost_pct_nav)
    observations = len(daily)
    gross_cumulative = float(wealth_gross.iloc[-1] - 1.0)
    net_cumulative = float(wealth_net.iloc[-1] - 1.0)
    annualized_return = float(wealth_net.iloc[-1] ** (252.0 / observations) - 1.0) if observations else 0.0
    volatility = float(daily.std(ddof=1) * math.sqrt(252.0)) if observations > 1 else 0.0
    return {
        "variant_id": composition.get("variant_id"),
        "composition_weights_pct": {ticker: round(weight * 100.0, 6) for ticker, weight in sorted(weights.items())},
        "cash_weight_pct": round(cash_weight * 100.0, 6),
        "initial_cost_pct_nav": round(cost_pct_nav * 100.0, 6),
        "trading_day_count": observations,
        "gross_cumulative_return_pct": round(gross_cumulative * 100.0, 6),
        "net_cumulative_return_after_initial_cost_pct": round(net_cumulative * 100.0, 6),
        "annualized_return_pct": round(annualized_return * 100.0, 6),
        "annualized_volatility_pct": round(volatility * 100.0, 6),
        "maximum_drawdown_pct": round(max_drawdown(wealth_net) * 100.0, 6),
        "worst_daily_return_pct": round(float(daily.min()) * 100.0, 6),
        "best_daily_return_pct": round(float(daily.max()) * 100.0, 6),
        "positive_day_share_pct": round(float((daily > 0).mean()) * 100.0, 6),
        "daily_return_series": [
            {"date": index.date().isoformat(), "return_pct": round(float(value) * 100.0, 8)}
            for index, value in daily.items()
        ],
    }


def build(panel: dict[str, Any], allocator: dict[str, Any], portfolio: dict[str, Any], output: Path) -> None:
    if panel.get("schema_version") != "etf_eu_transition_replay_panel_v1":
        raise RuntimeError("Unsupported replay panel")
    if allocator.get("schema_version") != "etf_eu_target_allocator_shadow_v3":
        raise RuntimeError("Expected v3 allocator")
    if panel.get("optimization_authority") is not False:
        raise RuntimeError("Replay panel violates non-optimization boundary")

    closes = panel_frame(panel)
    returns = closes.pct_change().dropna()
    nav = num(portfolio.get("nav_eur"))
    variants = {str(row.get("variant_id")): row for row in allocator.get("variants") or [] if isinstance(row, dict)}
    selected_variant_ids = [
        "strict_mapped_replication",
        "staged_cash_first_50pct",
        "staged_policy_driven_v1",
    ]
    compositions = [current_composition(portfolio)] + [allocator_composition(variants[variant_id], nav) for variant_id in selected_variant_ids]
    results = [replay_composition(composition, returns) for composition in compositions]

    series = {
        row["variant_id"]: pd.Series(
            [num(item.get("return_pct")) / 100.0 for item in row.get("daily_return_series") or []],
            index=[item.get("date") for item in row.get("daily_return_series") or []],
        )
        for row in results
    }
    correlations: list[dict[str, Any]] = []
    keys = list(series)
    for left_index, left in enumerate(keys):
        for right in keys[left_index + 1:]:
            correlations.append({
                "left_variant": left,
                "right_variant": right,
                "daily_return_correlation": round(float(series[left].corr(series[right])), 6),
            })

    payload = {
        "schema_version": "etf_eu_transition_composition_replay_v1",
        "artifact_type": "etf_eu_transition_composition_replay",
        "generated_at_utc": utc_now(),
        "report_date": panel.get("report_date"),
        "common_start_date": panel.get("common_start_date"),
        "common_end_date": panel.get("common_end_date"),
        "price_observation_count": panel.get("common_trading_day_count"),
        "return_observation_count": len(returns),
        "methodology": {
            "type": "fixed_composition_historical_replay",
            "historical_decisions_reconstructed": False,
            "optimization_performed": False,
            "weights": "current_report_date_compositions_held_constant_over_common_history",
            "cash_daily_return": 0.0,
            "transaction_cost": "one_time_starting_nav_reduction_from_allocator_estimate",
            "purpose": "sanity_check_only_not_strategy_backtest_or_performance_proof",
            "ticker_identity_normalization": "LOCK_alias_normalized_to_L0CK",
        },
        "source_quality": panel.get("source_quality"),
        "variant_results": results,
        "pairwise_daily_return_correlations": correlations,
        "interpretation_boundary": (
            "Results show how today's fixed compositions would have behaved over the common historical window. "
            "They do not reconstruct information, selections or trades available at each historical date."
        ),
        "valuation_grade": False,
        "portfolio_mutation": False,
        "funding_authority": False,
        "execution_authority": False,
        "optimization_authority": False,
        "production_delivery_authority": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build non-optimizing EU transition composition replay")
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--allocator", type=Path, required=True)
    parser.add_argument("--portfolio-state", type=Path, default=Path("output/etf_eu_portfolio_state.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(load(args.panel), load(args.allocator), load(args.portfolio_state), args.output)


if __name__ == "__main__":
    main()
