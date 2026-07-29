from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected YAML object: {path}")
    return payload


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def preferred_variant(allocator: dict[str, Any]) -> dict[str, Any]:
    preferred_id = str(allocator.get("preferred_shadow_variant") or "")
    for row in allocator.get("variants") or []:
        if isinstance(row, dict) and str(row.get("variant_id")) == preferred_id:
            return row
    raise RuntimeError("Preferred allocator variant not found")


def composition(preferred: dict[str, Any]) -> tuple[dict[str, float], float]:
    weights: dict[str, float] = {}
    for row in preferred.get("legacy_rows") or []:
        if not isinstance(row, dict):
            continue
        ticker = str(row.get("ticker") or "")
        market_value = num(row.get("target_market_value_eur"))
        if ticker and market_value > 0:
            weights[ticker] = market_value
    for row in preferred.get("allocation_rows") or []:
        if not isinstance(row, dict):
            continue
        candidate = row.get("candidate") if isinstance(row.get("candidate"), dict) else {}
        order = row.get("order") if isinstance(row.get("order"), dict) else {}
        ticker = str(candidate.get("ticker") or "")
        market_value = num(order.get("target_market_value_eur"))
        if ticker and market_value > 0:
            weights[ticker] = market_value
    summary = preferred.get("summary") if isinstance(preferred.get("summary"), dict) else {}
    cash_value = num(summary.get("projected_cash_eur"))
    total = cash_value + sum(weights.values())
    if total <= 0:
        raise RuntimeError("Allocator composition has no value")
    return ({ticker: value / total * 100.0 for ticker, value in weights.items()}, cash_value / total * 100.0)


def panel_returns(panel: dict[str, Any]) -> pd.DataFrame:
    rows = panel.get("rows") if isinstance(panel.get("rows"), list) else []
    records = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        prices = row.get("adjusted_close_eur") if isinstance(row.get("adjusted_close_eur"), dict) else {}
        records.append({"date": row.get("date"), **prices})
    frame = pd.DataFrame(records)
    if frame.empty or "date" not in frame:
        raise RuntimeError("Replay panel is empty")
    frame["date"] = pd.to_datetime(frame["date"])
    frame = frame.set_index("date").sort_index().astype(float)
    returns = frame.pct_change().dropna(how="any")
    if len(returns) < 60:
        raise RuntimeError("Insufficient common return observations")
    return returns


def metric_row(returns: pd.DataFrame, weights_pct: dict[str, float], cash_pct: float) -> tuple[dict[str, Any], pd.Series]:
    missing = sorted(set(weights_pct) - set(returns.columns))
    if missing:
        raise RuntimeError(f"Replay panel missing: {', '.join(missing)}")
    weights = pd.Series({ticker: weight / 100.0 for ticker, weight in weights_pct.items()})
    portfolio = (returns[weights.index] * weights).sum(axis=1)
    wealth = (1.0 + portfolio).cumprod()
    drawdown = wealth / wealth.cummax() - 1.0
    annualized_return = wealth.iloc[-1] ** (252.0 / len(portfolio)) - 1.0
    annualized_volatility = portfolio.std(ddof=1) * math.sqrt(252.0)
    negative = portfolio[portfolio < 0]
    downside = negative.std(ddof=1) * math.sqrt(252.0) if len(negative) > 1 else 0.0
    var95 = float(portfolio.quantile(0.05))
    es95 = float(portfolio[portfolio <= var95].mean())
    rolling20 = (1.0 + portfolio).rolling(20).apply(np.prod, raw=True) - 1.0
    result = {
        "composition_weights_pct": {key: round(value, 6) for key, value in sorted(weights_pct.items())},
        "cash_weight_pct": round(cash_pct, 6),
        "annualized_return_pct": round(annualized_return * 100.0, 6),
        "annualized_volatility_pct": round(annualized_volatility * 100.0, 6),
        "maximum_drawdown_pct": round(float(drawdown.min()) * 100.0, 6),
        "downside_volatility_pct": round(downside * 100.0, 6),
        "daily_var95_pct": round(var95 * 100.0, 6),
        "daily_expected_shortfall95_pct": round(es95 * 100.0, 6),
        "worst_20_trading_day_return_pct": round(float(rolling20.min()) * 100.0, 6),
        "observation_count": len(portfolio),
    }
    return result, portfolio


def build(panel: dict[str, Any], allocator: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    authority = allocator.get("authority") if isinstance(allocator.get("authority"), dict) else {}
    if authority.get("portfolio_mutation") is not False or authority.get("execution_authority") is not False:
        raise RuntimeError("Allocator violates shadow authority")
    preferred = preferred_variant(allocator)
    weights, cash_pct = composition(preferred)
    if "EUNA" not in weights:
        raise RuntimeError("EUNA is missing from the preferred composition")
    returns = panel_returns(panel)
    euna_weight = weights["EUNA"]
    risky = {ticker: weight for ticker, weight in weights.items() if ticker != "EUNA"}
    risky_total = sum(risky.values())

    scenarios: dict[str, tuple[dict[str, float], float]] = {}
    scenarios["policy_retained"] = (dict(weights), cash_pct)
    scenarios["euna_to_cash"] = (dict(risky), cash_pct + euna_weight)
    scenarios["euna_to_risky_pro_rata"] = (
        {ticker: weight + euna_weight * weight / risky_total for ticker, weight in risky.items()},
        cash_pct,
    )
    doubled = dict(weights)
    doubled["EUNA"] = euna_weight * 2.0
    scenarios["euna_doubled_from_cash"] = (doubled, cash_pct - euna_weight)

    scenario_results: dict[str, dict[str, Any]] = {}
    scenario_returns: dict[str, pd.Series] = {}
    for scenario_id, (scenario_weights, scenario_cash) in scenarios.items():
        result, series = metric_row(returns, scenario_weights, scenario_cash)
        result["scenario_id"] = scenario_id
        scenario_results[scenario_id] = result
        scenario_returns[scenario_id] = series

    risky_weights = pd.Series({ticker: weight / risky_total for ticker, weight in risky.items()})
    risky_series = (returns[risky_weights.index] * risky_weights).sum(axis=1)
    euna_series = returns["EUNA"]
    euna_wealth = (1.0 + euna_series).cumprod()
    worst_decile = risky_series <= risky_series.quantile(0.10)
    risky_down = risky_series < 0
    euna_metrics = {
        "correlation_with_risky_sleeve": round(float(euna_series.corr(risky_series)), 6),
        "annualized_return_pct": round(float(euna_wealth.iloc[-1] ** (252.0 / len(euna_series)) - 1.0) * 100.0, 6),
        "annualized_volatility_pct": round(float(euna_series.std(ddof=1) * math.sqrt(252.0)) * 100.0, 6),
        "maximum_drawdown_pct": round(float((euna_wealth / euna_wealth.cummax() - 1.0).min()) * 100.0, 6),
        "average_return_on_risky_down_days_pct": round(float(euna_series[risky_down].mean()) * 100.0, 6),
        "positive_share_on_risky_down_days_pct": round(float((euna_series[risky_down] > 0).mean()) * 100.0, 6),
        "average_return_on_worst_risky_decile_days_pct": round(float(euna_series[worst_decile].mean()) * 100.0, 6),
        "positive_share_on_worst_risky_decile_days_pct": round(float((euna_series[worst_decile] > 0).mean()) * 100.0, 6),
    }

    retained = scenario_results["policy_retained"]
    cash_case = scenario_results["euna_to_cash"]
    risky_case = scenario_results["euna_to_risky_pro_rata"]
    effects = {
        "versus_cash": {
            "annualized_return_difference_pct_points": round(retained["annualized_return_pct"] - cash_case["annualized_return_pct"], 6),
            "annualized_volatility_difference_pct_points": round(retained["annualized_volatility_pct"] - cash_case["annualized_volatility_pct"], 6),
            "maximum_drawdown_difference_pct_points": round(retained["maximum_drawdown_pct"] - cash_case["maximum_drawdown_pct"], 6),
        },
        "versus_risky_reallocation": {
            "annualized_return_difference_pct_points": round(retained["annualized_return_pct"] - risky_case["annualized_return_pct"], 6),
            "annualized_volatility_reduction_pct_points": round(risky_case["annualized_volatility_pct"] - retained["annualized_volatility_pct"], 6),
            "maximum_drawdown_improvement_pct_points": round(retained["maximum_drawdown_pct"] - risky_case["maximum_drawdown_pct"], 6),
        },
    }

    rules = policy.get("interpretation_rules") if isinstance(policy.get("interpretation_rules"), dict) else {}
    hedge_rules = rules.get("crisis_hedge_pass_requires") if isinstance(rules.get("crisis_hedge_pass_requires"), dict) else {}
    diversifier_rules = rules.get("low_volatility_diversifier_pass_requires") if isinstance(rules.get("low_volatility_diversifier_pass_requires"), dict) else {}
    crisis_hedge_pass = (
        euna_metrics["correlation_with_risky_sleeve"] <= num(hedge_rules.get("maximum_correlation_with_risky_sleeve"))
        and euna_metrics["positive_share_on_risky_down_days_pct"] >= num(hedge_rules.get("minimum_positive_share_on_risky_down_days_pct"))
    )
    low_volatility_diversifier_pass = (
        euna_metrics["annualized_volatility_pct"] <= num(diversifier_rules.get("maximum_annualized_volatility_pct"))
        and effects["versus_risky_reallocation"]["annualized_volatility_reduction_pct_points"] >= num(diversifier_rules.get("minimum_volatility_reduction_vs_risky_reallocation_pct_points"))
    )
    stage_1 = policy.get("stage_1_policy") if isinstance(policy.get("stage_1_policy"), dict) else {}
    within_band = num(stage_1.get("minimum_role_weight_pct_nav")) <= euna_weight <= num(stage_1.get("maximum_role_weight_pct_nav"))
    cash_above_threshold = cash_pct > num(rules.get("cash_weight_addition_threshold_pct"))
    decision_valid = within_band and low_volatility_diversifier_pass and cash_above_threshold and not crisis_hedge_pass

    return {
        "schema_version": "etf_eu_euna_risk_budget_review_v1",
        "artifact_type": "etf_eu_euna_risk_budget_review",
        "generated_at_utc": utc_now(),
        "report_date": panel.get("report_date"),
        "common_start_date": panel.get("common_start_date"),
        "common_end_date": panel.get("common_end_date"),
        "source_quality": panel.get("source_quality"),
        "source_policy": "config/etf_eu_euna_risk_budget_policy_v1.yml",
        "current_euna_weight_pct": round(euna_weight, 6),
        "current_cash_weight_pct": round(cash_pct, 6),
        "official_fund_characteristics": policy.get("official_fund_characteristics"),
        "euna_observed_metrics": euna_metrics,
        "counterfactual_results": [scenario_results[key] for key in policy.get("counterfactuals") or []],
        "marginal_effects": effects,
        "classification": {
            "crisis_hedge_pass": crisis_hedge_pass,
            "low_volatility_diversifier_pass": low_volatility_diversifier_pass,
            "current_weight_within_role_band": within_band,
            "cash_weight_above_addition_threshold": cash_above_threshold,
            "role": "low_volatility_carry_diversifier_not_reliable_equity_hedge",
        },
        "decision": {
            "stage_1": stage_1.get("decision"),
            "stage_1_decision_valid": decision_valid,
            "stage_1_action": "hold_current_position_no_add_no_sale",
            "stage_2_funding_priority": (policy.get("stage_2_policy") or {}).get("euna_funding_priority"),
            "stage_2_automatic_sale": False,
            "reason_codes": [
                "current_weight_within_5_to_8_pct_role_band",
                "reduces_risk_versus_risky_asset_reallocation",
                "does_not_qualify_as_reliable_equity_crisis_hedge",
                "cash_above_threshold_blocks_addition",
            ],
        },
        "interpretation_boundary": "Fixed-composition replay; no historical decision reconstruction, optimization or forecast authority.",
        "portfolio_mutation": False,
        "funding_authority": False,
        "execution_authority": False,
        "activation_authority": False,
        "production_delivery_authority": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build EUNA risk-budget counterfactual review")
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--allocator", type=Path, required=True)
    parser.add_argument("--policy", type=Path, default=Path("config/etf_eu_euna_risk_budget_policy_v1.yml"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build(load_json(args.panel), load_json(args.allocator), load_yaml(args.policy))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
