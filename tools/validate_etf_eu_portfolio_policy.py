#!/usr/bin/env python3
"""Validate an ETF EU portfolio or convergence state against release policy.

This is a decision/state gate. It does not mutate positions, create orders, render
reports, or authorize delivery. A PASS is required before a client artifact may be
packaged or independently assured.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected YAML mapping: {path}")
    return payload


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def ticker(value: Any) -> str:
    result = str(value or "").strip().upper()
    return "L0CK" if result == "LOCK" else result


def number(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def extract_portfolio(state: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    portfolio = state.get("official_portfolio")
    if isinstance(portfolio, dict):
        stage = state.get("stage_1_decision") if isinstance(state.get("stage_1_decision"), dict) else {}
        return portfolio, stage
    stage = state.get("stage_1_decision") if isinstance(state.get("stage_1_decision"), dict) else {}
    return state, stage


def validate(policy: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    checks: list[dict[str, Any]] = []

    def check(check_id: str, passed: bool, evidence: Any) -> None:
        checks.append({"id": check_id, "passed": bool(passed), "evidence": evidence})
        if not passed:
            blockers.append(check_id)

    mode = policy.get("active_release_mode") if isinstance(policy.get("active_release_mode"), dict) else {}
    rec = policy.get("reconciliation") if isinstance(policy.get("reconciliation"), dict) else {}
    portfolio, stage = extract_portfolio(state)
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    funded = sorted({ticker(row.get("exchange_ticker") or row.get("ticker")) for row in positions if ticker(row.get("exchange_ticker") or row.get("ticker"))})
    expected = sorted(ticker(value) for value in mode.get("expected_funded_tickers") or [])
    allowed = {ticker(value) for value in mode.get("allowed_funded_tickers") or []}

    check("policy_schema_valid", policy.get("schema_version") == "etf_eu_portfolio_policy_v2" and bool(policy.get("policy_id")), {"schema_version": policy.get("schema_version"), "policy_id": policy.get("policy_id")})
    check("release_roster_exact", funded == expected, {"funded": funded, "expected": expected})
    check("funded_tickers_allowed", set(funded).issubset(allowed), {"funded": funded, "allowed": sorted(allowed)})
    minimum_count = int(mode.get("minimum_position_count") or 0)
    maximum_count = int(mode.get("maximum_position_count") or 0)
    check("position_count_within_policy", minimum_count <= len(positions) <= maximum_count, {"actual": len(positions), "minimum": minimum_count, "maximum": maximum_count})

    nav = number(portfolio.get("nav_eur"))
    cash = number(portfolio.get("cash_eur"))
    stated_invested = number(portfolio.get("invested_market_value_eur"))
    market_values: dict[str, float] = {}
    missing_values: list[str] = []
    for row in positions:
        symbol = ticker(row.get("exchange_ticker") or row.get("ticker"))
        raw = row.get("market_value_eur")
        if raw is None and str(row.get("trading_currency") or "EUR").upper() == "EUR":
            raw = row.get("market_value_local")
        if raw is None:
            missing_values.append(symbol)
            continue
        market_values[symbol] = number(raw)
    computed_invested = sum(market_values.values())
    nav_tolerance = number(rec.get("nav_tolerance_eur") or 1.0)
    check("position_market_values_present", not missing_values, {"missing": missing_values})
    check("positive_nav", nav > 0, {"nav_eur": nav})
    check("invested_value_reconciles", abs(computed_invested - stated_invested) <= nav_tolerance, {"computed_invested_eur": round(computed_invested, 6), "stated_invested_eur": stated_invested, "tolerance_eur": nav_tolerance})
    check("cash_plus_positions_equals_nav", abs((computed_invested + cash) - nav) <= nav_tolerance, {"computed_total_eur": round(computed_invested + cash, 6), "nav_eur": nav, "tolerance_eur": nav_tolerance})

    computed_weights = {symbol: (value / nav * 100.0 if nav else 0.0) for symbol, value in market_values.items()}
    max_single = number(mode.get("maximum_single_position_weight_pct"))
    overweight = {symbol: round(weight, 6) for symbol, weight in computed_weights.items() if weight > max_single + 1e-9}
    check("maximum_single_position_weight", not overweight, {"maximum_pct": max_single, "violations": overweight, "computed_weights_pct": {k: round(v, 6) for k, v in computed_weights.items()}})

    max_by_ticker = mode.get("maximum_weight_by_ticker_pct") if isinstance(mode.get("maximum_weight_by_ticker_pct"), dict) else {}
    ticker_violations: dict[str, dict[str, float]] = {}
    for symbol, limit in max_by_ticker.items():
        normalized = ticker(symbol)
        actual = computed_weights.get(normalized, 0.0)
        if actual > number(limit) + 1e-9:
            ticker_violations[normalized] = {"actual_pct": round(actual, 6), "maximum_pct": number(limit)}
    check("ticker_weight_caps", not ticker_violations, ticker_violations)

    minimum_cash = number(mode.get("minimum_cash_weight_pct"))
    cash_weight = cash / nav * 100.0 if nav else 0.0
    check("minimum_cash_reserve", cash_weight + 1e-9 >= minimum_cash, {"cash_weight_pct": round(cash_weight, 6), "minimum_pct": minimum_cash})

    tolerance_pct = number(rec.get("weight_tolerance_pct") or 0.10)
    stated_weight_mismatches: dict[str, dict[str, float]] = {}
    for row in positions:
        symbol = ticker(row.get("exchange_ticker") or row.get("ticker"))
        stated = row.get("current_weight_pct")
        if stated is None:
            continue
        computed = computed_weights.get(symbol, 0.0)
        if abs(number(stated) - computed) > tolerance_pct:
            stated_weight_mismatches[symbol] = {"stated_pct": number(stated), "computed_pct": round(computed, 6), "tolerance_pct": tolerance_pct}
    check("stated_weights_reconcile", not stated_weight_mismatches, stated_weight_mismatches)

    required_activation = {ticker(value) for value in mode.get("required_activation_tickers") or []}
    activated = {ticker(value) for value in stage.get("activated_tickers") or []}
    if not activated:
        activation = portfolio.get("last_model_capital_activation")
        if isinstance(activation, dict) and activation.get("activation_id") and "L0CK" in funded:
            activated = {"L0CK"}
    check("required_activation_present", required_activation.issubset(activated), {"required": sorted(required_activation), "activated": sorted(activated)})

    intents = stage.get("executable_trade_intents", [])
    check("no_executable_trade_intents", intents == [], {"executable_trade_intents": intents})
    model_only = portfolio.get("model_portfolio_only") is True
    real_execution = portfolio.get("real_broker_execution") is True
    check("model_only_boundary", model_only and not real_execution, {"model_portfolio_only": portfolio.get("model_portfolio_only"), "real_broker_execution": portfolio.get("real_broker_execution")})

    return {
        "schema_version": "etf_eu_portfolio_policy_validation_v2",
        "artifact_type": "etf_eu_portfolio_policy_validation",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "policy_id": policy.get("policy_id"),
        "verdict": "PASS" if not blockers else "FAIL",
        "valid": not blockers,
        "blockers": blockers,
        "checks": checks,
        "portfolio": {
            "funded_tickers": funded,
            "position_count": len(positions),
            "nav_eur": nav,
            "cash_eur": cash,
            "cash_weight_pct": round(cash_weight, 6),
            "computed_weights_pct": {k: round(v, 6) for k, v in computed_weights.items()},
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    policy = load_yaml(args.policy)
    state = load_json(args.state)
    result = validate(policy, state)
    result["policy_path"] = str(args.policy)
    result["policy_sha256"] = sha256_file(args.policy)
    result["state_path"] = str(args.state)
    result["state_sha256"] = sha256_file(args.state)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": result["verdict"], "blockers": result["blockers"], "output": str(args.output)}, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
