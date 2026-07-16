from __future__ import annotations

import argparse
import json
import math
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import yaml


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Required JSON not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Required YAML not found: {path}")
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}


def f(value: Any, default: float = 0.0) -> float:
    try:
        return default if value in (None, "") else float(value)
    except (TypeError, ValueError):
        return default


def text(value: Any) -> str:
    return str(value or "").strip()


def iso_date(value: Any) -> date | None:
    try:
        return date.fromisoformat(text(value)[:10])
    except (TypeError, ValueError):
        return None


def price_index(payload: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for row in payload.get("rows") or []:
        if isinstance(row, dict):
            key = (text(row.get("isin")).upper(), text(row.get("ticker")).upper())
            if all(key):
                result[key] = dict(row)
    return result


def position_index(payload: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for row in payload.get("positions") or []:
        if isinstance(row, dict):
            key = (text(row.get("isin")).upper(), text(row.get("exchange_ticker") or row.get("ticker")).upper())
            if all(key):
                result[key] = dict(row)
    return result


def eligibility(target: dict[str, Any], row: dict[str, Any] | None, policy: dict[str, Any], report_date: date) -> tuple[bool, list[str], float | None]:
    if row is None:
        return False, ["exact_isin_trading_line_price_row_missing"], None
    blockers: list[str] = []
    if text(row.get("instrument_type")) not in set(policy.get("accepted_instrument_types") or []):
        blockers.append("instrument_type_not_accepted")
    if text(row.get("verification_status")) not in set(policy.get("accepted_verification_statuses") or []):
        blockers.append("trading_line_not_verified")
    if text(row.get("pricing_status")) not in set(policy.get("accepted_pricing_statuses") or []):
        blockers.append("pricing_status_not_accepted")
    currency = text(row.get("currency") or target.get("trading_currency")).upper()
    if currency not in {text(x).upper() for x in policy.get("cap01_currency_scope") or []}:
        blockers.append("currency_outside_cap01_scope")
    close = f(row.get("close_price"))
    if close <= 0:
        blockers.append("usable_close_missing")
    close_date = iso_date(row.get("close_date"))
    if close_date is None:
        blockers.append("close_date_missing")
    else:
        age = (report_date - close_date).days
        maximum = int(f(policy.get("max_price_age_days"), 3))
        if age < 0:
            blockers.append("close_after_report_date")
        elif age > maximum:
            blockers.append(f"close_too_old:{age}>{maximum}")
    if text(row.get("isin")).upper() != text(target.get("isin")).upper():
        blockers.append("isin_mismatch")
    if text(row.get("ticker")).upper() != text(target.get("exchange_ticker")).upper():
        blockers.append("trading_line_mismatch")
    return not blockers, blockers, close if close > 0 else None


def build_decision(*, policy_path: Path, portfolio_state_path: Path, pricing_artifact_path: Path, run_id: str, report_date_raw: str, output_path: Path) -> dict[str, Any]:
    config = load_yaml(policy_path)
    state = load_json(portfolio_state_path)
    pricing = load_json(pricing_artifact_path)
    report_date = iso_date(report_date_raw)
    if report_date is None:
        raise RuntimeError("Invalid report date")
    activation = dict(config.get("activation") or {})
    nav = f(state.get("nav_eur"), f(state.get("cash_eur")) + f(state.get("invested_market_value_eur")))
    cash = f(state.get("cash_eur"))
    if nav <= 0 or cash < 0:
        raise RuntimeError("Invalid portfolio state")
    phase_fraction = f(activation.get("phase_fraction"), 1.0)
    min_cash_pct = f(activation.get("minimum_cash_reserve_pct"))
    min_cash_eur = round(nav * min_cash_pct / 100.0, 2)
    targets = [dict(row) for row in config.get("strategic_targets") or [] if isinstance(row, dict)]
    target_total = round(sum(f(row.get("target_weight_pct")) for row in targets), 8)
    prices = price_index(pricing)
    positions = position_index(state)
    decisions: list[dict[str, Any]] = []
    executable_isins: set[str] = set()
    remaining_cash = cash
    total_trade = 0.0

    for target in sorted(targets, key=lambda row: int(f(row.get("priority"), 999))):
        ticker = text(target.get("exchange_ticker")).upper()
        strategic = f(target.get("target_weight_pct"))
        if ticker == "CASH":
            decisions.append({"allocation_id": target.get("allocation_id"), "portfolio_role": target.get("portfolio_role"), "exchange_ticker": "CASH", "strategic_target_weight_pct": strategic, "phase_target_weight_pct": strategic, "eligibility_status": "cash_reserve", "action": "retain_cash", "shares_delta": 0, "trade_value_eur": 0.0, "blockers": [], "reason_codes": ["strategic_cash_reserve", "whole_share_residual_cash"]})
            continue
        isin = text(target.get("isin")).upper()
        key = (isin, ticker)
        row = prices.get(key)
        eligible, blockers, price = eligibility(target, row, activation, report_date)
        current = positions.get(key, {})
        current_shares = int(math.floor(f(current.get("shares")) + 1e-9))
        phase_weight = round(strategic * phase_fraction, 6)
        phase_value = round(nav * phase_weight / 100.0, 2)
        target_shares = math.floor(phase_value / price) if eligible and price else current_shares
        delta = target_shares - current_shares
        trade_value = round(max(delta, 0) * (price or 0.0), 2)
        if eligible and delta < 0:
            eligible = False
            blockers.append("cap01_does_not_sell")
        if eligible and isin in executable_isins:
            eligible = False
            blockers.append("duplicate_executable_isin")
        if eligible and remaining_cash - trade_value < min_cash_eur - 0.01:
            eligible = False
            blockers.append("minimum_cash_reserve_breached")
        action = "buy" if eligible and delta > 0 else "hold_existing" if eligible else "blocked"
        if eligible:
            executable_isins.add(isin)
            remaining_cash = round(remaining_cash - trade_value, 2)
            total_trade = round(total_trade + trade_value, 2)
        projected_value = round(target_shares * (price or 0.0), 2) if eligible else round(current_shares * f(current.get("current_price_local")), 2)
        decisions.append({
            "priority": target.get("priority"), "allocation_id": target.get("allocation_id"), "portfolio_role": target.get("portfolio_role"),
            "isin": isin, "exchange_ticker": ticker, "fund_name": target.get("fund_name"), "provider": target.get("provider"),
            "primary_exchange": target.get("primary_exchange"), "trading_currency": target.get("trading_currency"),
            "strategic_target_weight_pct": strategic, "phase_target_weight_pct": phase_weight, "phase_target_value_eur": phase_value,
            "current_shares": current_shares, "target_whole_shares": target_shares, "shares_delta": delta if eligible else 0,
            "close_price_eur": round(price, 6) if price else None, "close_date": row.get("close_date") if row else None,
            "pricing_status": row.get("pricing_status") if row else None, "verification_status": row.get("verification_status") if row else None,
            "model_execution_price_basis": "verified_line_public_close_model_only" if eligible else None,
            "trade_value_eur": trade_value if eligible else 0.0, "projected_market_value_eur": projected_value,
            "projected_weight_pct": round(projected_value / nav * 100.0, 6) if nav else 0.0,
            "eligibility_status": "eligible_for_model_activation" if eligible else "blocked", "action": action, "blockers": blockers,
            "reason_codes": ["first_tranche", "whole_shares_only", "blocked_capacity_not_reallocated"] + (["exact_isin_and_line_verified", "current_public_close_available", "broker_permission_not_required_for_model"] if eligible else []),
            "conviction_tier": target.get("conviction_tier"), "rationale": target.get("rationale"),
            "instrument_metadata": {name: target.get(name) for name in ("ter_pct", "distribution_policy", "replication_method", "domicile", "benchmark_index") if target.get(name) is not None},
        })

    projected_invested = round(f(state.get("invested_market_value_eur")) + total_trade, 2)
    projected_nav = round(remaining_cash + projected_invested, 2)
    buys = [row for row in decisions if row.get("action") == "buy" and int(row.get("shares_delta") or 0) > 0]
    blocked = [row for row in decisions if row.get("eligibility_status") == "blocked"]
    hard_blockers: list[str] = []
    if abs(target_total - 100.0) > 0.0001:
        hard_blockers.append(f"strategic_targets_not_100:{target_total}")
    if not buys:
        hard_blockers.append("no_executable_model_allocation")
    if abs(projected_nav - nav) > 0.01:
        hard_blockers.append(f"nav_drift:{projected_nav}!={nav}")
    payload = {
        "schema_version": "etf_eu_allocation_decision_v1", "artifact_type": "etf_eu_allocation_decision",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "activation_id": f"ETF-EU-CAP01-{run_id}", "run_id": run_id, "report_date": report_date_raw,
        "source_files": {"target_allocation": str(policy_path), "portfolio_state": str(portfolio_state_path), "pricing_artifact": str(pricing_artifact_path)},
        "authority": {"model_portfolio_only": True, "real_broker_execution": False, "personal_investment_advice": False, "canonical_identity": "isin_plus_exact_trading_line", "whole_shares_only": True, "blocked_capacity_reallocated": False, "valuation_grade": False, "model_capital_activation_authority": True, "broker_specific_permission_required_for_model": False, "broker_permission_required_for_real_execution": True},
        "policy": {"allocation_style": config.get("allocation_style"), "phase_id": activation.get("phase_id"), "phase_fraction": phase_fraction, "minimum_cash_reserve_pct": min_cash_pct, "minimum_cash_reserve_eur": min_cash_eur, "blocked_capacity_policy": activation.get("blocked_capacity_policy"), "strategic_target_weight_total_pct": target_total},
        "pre_activation_portfolio": {"cash_eur": round(cash, 2), "invested_market_value_eur": round(f(state.get("invested_market_value_eur")), 2), "nav_eur": round(nav, 2), "position_count": len(state.get("positions") or [])},
        "decisions": decisions,
        "summary": {"executable_position_count": len(buys), "blocked_target_count": len(blocked), "executable_trade_value_eur": total_trade, "projected_cash_eur": remaining_cash, "projected_invested_market_value_eur": projected_invested, "projected_nav_eur": projected_nav, "projected_cash_weight_pct": round(remaining_cash / nav * 100.0, 6), "nav_reconciliation_ok": abs(projected_nav - nav) <= 0.01, "blocked_target_capacity_retained_as_cash": True},
        "allocation_status": "ready_for_guarded_model_activation" if not hard_blockers else "blocked", "hard_blockers": hard_blockers,
        "warnings": ["Public close supports only the repository model portfolio, not a brokerage execution.", "Broker-specific account permissions are outside the model-allocation gate and must be checked only before real execution.", "Blocked strategic capacity remains cash and is not redistributed."],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", "--targets", dest="policy", default="config/etf_eu_target_allocation.yml")
    parser.add_argument("--portfolio-state", default="output/etf_eu_portfolio_state.json")
    parser.add_argument("--pricing-artifact", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    payload = build_decision(policy_path=Path(args.policy), portfolio_state_path=Path(args.portfolio_state), pricing_artifact_path=Path(args.pricing_artifact), run_id=args.run_id, report_date_raw=args.report_date, output_path=Path(args.output))
    print(json.dumps({"status": payload["allocation_status"], "summary": payload["summary"], "hard_blockers": payload["hard_blockers"]}, indent=2))
    if payload["allocation_status"] != "ready_for_guarded_model_activation":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
