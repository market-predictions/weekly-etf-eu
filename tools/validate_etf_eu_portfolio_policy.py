#!/usr/bin/env python3
"""Validate ETF EU release state against protected allocation lineage.

The Weekly ETF donor does not define a universal maximum position weight or a
mandatory cash floor. This gate therefore proves that a valuation-only report
preserves the protected ticker/share/cash state and that any prior mutation is
bound to an explicit allocation decision. It does not make investment decisions,
render reports, send mail, or authorize broker execution.
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


def position_map(portfolio: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], list[str]]:
    result: dict[str, dict[str, Any]] = {}
    duplicates: list[str] = []
    for row in portfolio.get("positions") or []:
        if not isinstance(row, dict):
            continue
        symbol = ticker(row.get("exchange_ticker") or row.get("ticker"))
        if not symbol:
            continue
        if symbol in result:
            duplicates.append(symbol)
        result[symbol] = row
    return result, sorted(set(duplicates))


def validate(
    policy: dict[str, Any],
    state: dict[str, Any],
    authoritative_state: dict[str, Any],
    decision: dict[str, Any],
) -> dict[str, Any]:
    blockers: list[str] = []
    checks: list[dict[str, Any]] = []

    def check(check_id: str, passed: bool, evidence: Any) -> None:
        checks.append({"id": check_id, "passed": bool(passed), "evidence": evidence})
        if not passed:
            blockers.append(check_id)

    lineage = policy.get("allocation_lineage") if isinstance(policy.get("allocation_lineage"), dict) else {}
    rec = policy.get("reconciliation") if isinstance(policy.get("reconciliation"), dict) else {}
    portfolio, stage = extract_portfolio(state)
    authoritative, _ = extract_portfolio(authoritative_state)
    positions, duplicates = position_map(portfolio)
    protected_positions, protected_duplicates = position_map(authoritative)
    funded = sorted(positions)
    protected_funded = sorted(protected_positions)

    check(
        "policy_schema_valid",
        policy.get("schema_version") == "etf_eu_portfolio_policy_v2" and bool(policy.get("policy_id")),
        {"schema_version": policy.get("schema_version"), "policy_id": policy.get("policy_id")},
    )
    check(
        "lineage_method_valid",
        lineage.get("method") == "protected_state_plus_explicit_authorized_mutation",
        {"method": lineage.get("method")},
    )
    check("unique_position_identity", not duplicates and not protected_duplicates, {"candidate_duplicates": duplicates, "protected_duplicates": protected_duplicates})
    check("protected_ticker_roster_preserved", funded == protected_funded, {"candidate": funded, "protected": protected_funded})

    share_mismatches: dict[str, dict[str, float]] = {}
    for symbol in sorted(set(funded) | set(protected_funded)):
        candidate_shares = number(positions.get(symbol, {}).get("shares"))
        protected_shares = number(protected_positions.get(symbol, {}).get("shares"))
        if abs(candidate_shares - protected_shares) > 1e-9:
            share_mismatches[symbol] = {"candidate_shares": candidate_shares, "protected_shares": protected_shares}
    check("protected_share_identity_preserved", not share_mismatches, share_mismatches)

    cash_tolerance = number(rec.get("cash_tolerance_eur") or 0.01)
    candidate_cash = number(portfolio.get("cash_eur"))
    protected_cash = number(authoritative.get("cash_eur"))
    check(
        "protected_cash_preserved",
        abs(candidate_cash - protected_cash) <= cash_tolerance,
        {"candidate_cash_eur": candidate_cash, "protected_cash_eur": protected_cash, "tolerance_eur": cash_tolerance},
    )
    check("no_leverage_or_negative_cash", candidate_cash >= -cash_tolerance, {"cash_eur": candidate_cash})

    expected_activation_id = str(lineage.get("current_activation_id") or "")
    protected_activation = authoritative.get("last_model_capital_activation") if isinstance(authoritative.get("last_model_capital_activation"), dict) else {}
    candidate_activation = portfolio.get("last_model_capital_activation") if isinstance(portfolio.get("last_model_capital_activation"), dict) else {}
    decision_activation_id = str(decision.get("activation_id") or "")
    check(
        "activation_identity_bound",
        bool(expected_activation_id)
        and expected_activation_id == str(protected_activation.get("activation_id") or "")
        and expected_activation_id == str(candidate_activation.get("activation_id") or "")
        and expected_activation_id == decision_activation_id,
        {
            "policy_activation_id": expected_activation_id,
            "protected_activation_id": protected_activation.get("activation_id"),
            "candidate_activation_id": candidate_activation.get("activation_id"),
            "decision_activation_id": decision_activation_id,
        },
    )
    check(
        "allocation_decision_schema_valid",
        decision.get("schema_version") == "etf_eu_stage1_allocation_decision_v1"
        and decision.get("allocation_status") == "ready_for_guarded_model_activation",
        {"schema_version": decision.get("schema_version"), "allocation_status": decision.get("allocation_status")},
    )
    decision_rows = [row for row in decision.get("decisions") or [] if isinstance(row, dict)]
    decision_buys = {ticker(row.get("exchange_ticker")) for row in decision_rows if str(row.get("action") or "").lower() == "buy"}
    required_activated = {ticker(value) for value in lineage.get("required_activated_tickers") or []}
    check("required_activation_decision_present", required_activated.issubset(decision_buys), {"required": sorted(required_activated), "decision_buys": sorted(decision_buys)})
    decision_share_mismatches: dict[str, dict[str, float]] = {}
    for row in decision_rows:
        symbol = ticker(row.get("exchange_ticker"))
        if not symbol or str(row.get("action") or "").lower() != "buy":
            continue
        authorized_delta = number(row.get("shares_delta"))
        protected_shares = number(protected_positions.get(symbol, {}).get("shares"))
        if authorized_delta <= 0 or abs(authorized_delta - protected_shares) > 1e-9:
            decision_share_mismatches[symbol] = {"authorized_buy_shares": authorized_delta, "protected_shares": protected_shares}
    check("activation_share_delta_bound", not decision_share_mismatches, decision_share_mismatches)

    nav = number(portfolio.get("nav_eur"))
    stated_invested = number(portfolio.get("invested_market_value_eur"))
    market_values: dict[str, float] = {}
    missing_values: list[str] = []
    market_value_mismatches: dict[str, dict[str, float]] = {}
    mv_tolerance = number(rec.get("market_value_tolerance_eur") or 1.0)
    for symbol, row in positions.items():
        raw = row.get("market_value_eur")
        if raw is None and str(row.get("trading_currency") or "EUR").upper() == "EUR":
            raw = row.get("market_value_local")
        if raw is None:
            missing_values.append(symbol)
            continue
        market_value = number(raw)
        market_values[symbol] = market_value
        shares = number(row.get("shares"))
        price = number(row.get("current_price_local"))
        if shares > 0 and price > 0 and abs((shares * price) - market_value) > mv_tolerance:
            market_value_mismatches[symbol] = {
                "shares_times_price_eur": round(shares * price, 6),
                "market_value_eur": market_value,
                "tolerance_eur": mv_tolerance,
            }
    computed_invested = sum(market_values.values())
    nav_tolerance = number(rec.get("nav_tolerance_eur") or 1.0)
    check("position_market_values_present", not missing_values, {"missing": missing_values})
    check("market_value_matches_shares_times_price", not market_value_mismatches, market_value_mismatches)
    check("positive_nav", nav > 0, {"nav_eur": nav})
    check(
        "invested_value_reconciles",
        abs(computed_invested - stated_invested) <= nav_tolerance,
        {"computed_invested_eur": round(computed_invested, 6), "stated_invested_eur": stated_invested, "tolerance_eur": nav_tolerance},
    )
    check(
        "cash_plus_positions_equals_nav",
        abs((computed_invested + candidate_cash) - nav) <= nav_tolerance,
        {"computed_total_eur": round(computed_invested + candidate_cash, 6), "nav_eur": nav, "tolerance_eur": nav_tolerance},
    )

    computed_weights = {symbol: (value / nav * 100.0 if nav else 0.0) for symbol, value in market_values.items()}
    tolerance_pct = number(rec.get("weight_tolerance_pct") or 0.10)
    stated_weight_mismatches: dict[str, dict[str, float]] = {}
    for symbol, row in positions.items():
        stated = row.get("current_weight_pct")
        if stated is None:
            continue
        computed = computed_weights.get(symbol, 0.0)
        if abs(number(stated) - computed) > tolerance_pct:
            stated_weight_mismatches[symbol] = {"stated_pct": number(stated), "computed_pct": round(computed, 6), "tolerance_pct": tolerance_pct}
    check("stated_weights_reconcile", not stated_weight_mismatches, stated_weight_mismatches)

    activated = {ticker(value) for value in stage.get("activated_tickers") or []}
    if not activated and candidate_activation.get("activation_id"):
        activated = required_activated & set(funded)
    check("required_activation_present", required_activated.issubset(activated), {"required": sorted(required_activated), "activated": sorted(activated)})
    intents = stage.get("executable_trade_intents", [])
    check("no_executable_trade_intents", intents == [], {"executable_trade_intents": intents})
    check(
        "model_only_boundary",
        portfolio.get("model_portfolio_only") is True and portfolio.get("real_broker_execution") is False,
        {"model_portfolio_only": portfolio.get("model_portfolio_only"), "real_broker_execution": portfolio.get("real_broker_execution")},
    )

    largest = max(computed_weights.items(), key=lambda item: item[1], default=(None, 0.0))
    cash_weight = candidate_cash / nav * 100.0 if nav else 0.0
    return {
        "schema_version": "etf_eu_portfolio_policy_validation_v2",
        "artifact_type": "etf_eu_portfolio_policy_validation",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "policy_id": policy.get("policy_id"),
        "verdict": "PASS" if not blockers else "FAIL",
        "valid": not blockers,
        "blockers": blockers,
        "checks": checks,
        "allocation_lineage": {
            "method": lineage.get("method"),
            "activation_id": expected_activation_id,
            "decision_schema_version": decision.get("schema_version"),
            "share_or_cash_mutation_detected": bool(share_mismatches) or abs(candidate_cash - protected_cash) > cash_tolerance,
        },
        "portfolio": {
            "funded_tickers": funded,
            "position_count": len(positions),
            "nav_eur": nav,
            "cash_eur": candidate_cash,
            "cash_weight_pct": round(cash_weight, 6),
            "computed_weights_pct": {key: round(value, 6) for key, value in computed_weights.items()},
            "largest_position_ticker": largest[0],
            "largest_position_weight_pct": round(largest[1], 6),
            "concentration_is_observation_not_hard_cap": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--authoritative-state", type=Path)
    parser.add_argument("--decision", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    policy = load_yaml(args.policy)
    lineage = policy.get("allocation_lineage") if isinstance(policy.get("allocation_lineage"), dict) else {}
    authoritative_path = args.authoritative_state or Path(str(lineage.get("authoritative_portfolio_state") or ""))
    decision_path = args.decision or Path(str(lineage.get("current_authorized_decision") or ""))
    if not authoritative_path.is_file():
        raise RuntimeError(f"Authoritative portfolio state missing: {authoritative_path}")
    if not decision_path.is_file():
        raise RuntimeError(f"Allocation decision missing: {decision_path}")
    state = load_json(args.state)
    authoritative = load_json(authoritative_path)
    decision = load_json(decision_path)
    result = validate(policy, state, authoritative, decision)
    result["policy_path"] = str(args.policy)
    result["policy_sha256"] = sha256_file(args.policy)
    result["state_path"] = str(args.state)
    result["state_sha256"] = sha256_file(args.state)
    result["authoritative_state_path"] = str(authoritative_path)
    result["authoritative_state_sha256"] = sha256_file(authoritative_path)
    result["decision_path"] = str(decision_path)
    result["decision_sha256"] = sha256_file(decision_path)
    candidate_portfolio, _ = extract_portfolio(state)
    embedded_hash = str(candidate_portfolio.get("portfolio_state_sha256") or "")
    if embedded_hash and embedded_hash != result["authoritative_state_sha256"]:
        result["checks"].append({
            "id": "embedded_authoritative_state_hash_bound",
            "passed": False,
            "evidence": {"embedded": embedded_hash, "actual": result["authoritative_state_sha256"]},
        })
        result["blockers"].append("embedded_authoritative_state_hash_bound")
        result["valid"] = False
        result["verdict"] = "FAIL"
    else:
        result["checks"].append({
            "id": "embedded_authoritative_state_hash_bound",
            "passed": True,
            "evidence": {"embedded": embedded_hash or None, "actual": result["authoritative_state_sha256"]},
        })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": result["verdict"], "blockers": result["blockers"], "output": str(args.output)}, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
