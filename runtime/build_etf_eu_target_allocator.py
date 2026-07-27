from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


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


def _target_weights(shared_target: dict[str, Any]) -> dict[str, float]:
    result: dict[str, float] = {}
    for row in shared_target.get("exposure_targets") or []:
        if isinstance(row, dict) and row.get("exposure_id"):
            result[str(row["exposure_id"])] = _num(row.get("target_weight_pct"))
    return result


def _evidence_index(market_evidence: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("exposure_id")): row
        for row in (market_evidence.get("target_rows") or [])
        if isinstance(row, dict) and row.get("exposure_id")
    }


def _incumbent_evidence_index(market_evidence: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("ticker") or "").upper(): row
        for row in (market_evidence.get("incumbent_rows") or [])
        if isinstance(row, dict) and row.get("ticker")
    }


def _floor_units(value_eur: float, price_eur: float) -> int:
    if value_eur <= 0 or price_eur <= 0:
        return 0
    return max(0, int(math.floor(value_eur / price_eur + 1e-12)))


def _market_price(evidence_row: dict[str, Any]) -> float:
    return _num((evidence_row.get("market") or {}).get("completed_close_price_eur"))


def _spread_bps(evidence_row: dict[str, Any], missing_proxy: float) -> tuple[float, str]:
    spread = (evidence_row.get("market") or {}).get("quote_spread_bps")
    if spread is None:
        return missing_proxy, "policy_proxy_missing_quote"
    return max(0.0, _num(spread)), "observed_quote"


def _security_row(exposure_id: str, target_weight: float, nav: float, evidence: dict[str, Any]) -> dict[str, Any]:
    desired = nav * target_weight / 100.0
    price = _market_price(evidence)
    eligible_status = str(evidence.get("allocator_market_status") or "blocked")
    allocator_usable = eligible_status in {"eligible_shadow_allocator", "eligible_pending_spread_review"} and price > 0
    units = _floor_units(desired, price) if allocator_usable else 0
    allocated = round(units * price, 2)
    blockers = list(evidence.get("blockers") or [])
    if target_weight > 0 and allocator_usable and units == 0:
        blockers.append("whole_share_rounding_prevents_position")
    if target_weight > 0 and not allocator_usable:
        blockers.append("allocator_market_evidence_blocked")
    return {
        "exposure_id": exposure_id,
        "target_weight_pct": round(target_weight, 6),
        "desired_value_eur": round(desired, 2),
        "registry_id": evidence.get("registry_id"),
        "fund_name": evidence.get("fund_name"),
        "isin": evidence.get("isin"),
        "ticker": evidence.get("exchange_ticker"),
        "exchange": evidence.get("exchange"),
        "price_eur": round(price, 8) if price > 0 else None,
        "price_date": (evidence.get("market") or {}).get("completed_close_date"),
        "whole_share_units": units,
        "allocated_value_eur": allocated,
        "rounded_weight_pct": round(allocated / nav * 100.0, 6) if nav else 0.0,
        "rounding_residual_eur": round(desired - allocated, 2),
        "allocator_market_status": eligible_status,
        "median_daily_traded_value_eur": (evidence.get("market") or {}).get("median_daily_traded_value_eur"),
        "quote_spread_bps": (evidence.get("market") or {}).get("quote_spread_bps"),
        "annualized_volatility_pct": (evidence.get("market") or {}).get("annualized_volatility_pct"),
        "maximum_drawdown_pct": (evidence.get("market") or {}).get("maximum_drawdown_pct"),
        "blockers": sorted(set(blockers)),
        "portfolio_mutation": False,
        "allocation_authority": False,
    }


def _trade_costs(trades: list[dict[str, Any]], policy: dict[str, Any]) -> dict[str, Any]:
    cost_policy = policy.get("cost_scenarios") if isinstance(policy.get("cost_scenarios"), dict) else {}
    commission = cost_policy.get("commission_slippage_bps") if isinstance(cost_policy.get("commission_slippage_bps"), dict) else {}
    missing_proxy = _num(cost_policy.get("missing_spread_proxy_bps"), 30.0)
    scenarios: dict[str, Any] = {}
    for name in ("low", "base", "stress"):
        extra_bps = _num(commission.get(name))
        total = 0.0
        observed_count = 0
        proxy_count = 0
        for trade in trades:
            spread, source = _spread_bps(trade.get("evidence") or {}, missing_proxy)
            observed_count += int(source == "observed_quote")
            proxy_count += int(source != "observed_quote")
            one_way_bps = spread / 2.0 + extra_bps
            total += _num(trade.get("notional_eur")) * one_way_bps / 10000.0
        scenarios[name] = {
            "commission_slippage_bps": extra_bps,
            "missing_spread_proxy_bps": missing_proxy,
            "estimated_cost_eur": round(total, 2),
            "observed_spread_trade_count": observed_count,
            "proxy_spread_trade_count": proxy_count,
        }
    return scenarios


def _build_trade_plan(
    target_rows: list[dict[str, Any]],
    portfolio: dict[str, Any],
    market_evidence: dict[str, Any],
    nav: float,
    policy: dict[str, Any],
    *,
    retain_incumbents: bool,
) -> dict[str, Any]:
    target_by_isin = {str(row.get("isin")): row for row in target_rows if row.get("isin") and int(row.get("whole_share_units") or 0) > 0}
    target_evidence = _evidence_index(market_evidence)
    incumbent_evidence = _incumbent_evidence_index(market_evidence)
    trades: list[dict[str, Any]] = []

    for row in target_rows:
        units = int(row.get("whole_share_units") or 0)
        if units <= 0:
            continue
        current_units = 0
        for position in portfolio.get("positions") or []:
            if isinstance(position, dict) and str(position.get("isin") or "") == str(row.get("isin") or ""):
                current_units = int(_num(position.get("shares")))
                break
        delta = units - current_units
        if delta == 0:
            continue
        evidence = target_evidence.get(str(row.get("exposure_id"))) or {}
        trades.append({
            "action": "buy" if delta > 0 else "sell",
            "exposure_id": row.get("exposure_id"),
            "ticker": row.get("ticker"),
            "isin": row.get("isin"),
            "units": abs(delta),
            "price_eur": row.get("price_eur"),
            "notional_eur": round(abs(delta) * _num(row.get("price_eur")), 2),
            "evidence": evidence,
            "portfolio_mutation": False,
        })

    if not retain_incumbents:
        for position in portfolio.get("positions") or []:
            if not isinstance(position, dict):
                continue
            isin = str(position.get("isin") or "")
            if isin in target_by_isin:
                continue
            ticker = str(position.get("ticker") or position.get("exchange_ticker") or "").upper()
            evidence = incumbent_evidence.get(ticker) or {}
            market_price = _num((evidence.get("market") or {}).get("completed_close_price_eur"))
            price = market_price or _num(position.get("current_price_local"))
            units = int(_num(position.get("shares")))
            trades.append({
                "action": "sell",
                "exposure_id": None,
                "ticker": ticker,
                "isin": isin,
                "units": units,
                "price_eur": round(price, 8),
                "notional_eur": round(units * price, 2),
                "evidence": evidence,
                "transition_reason": "incumbent_not_in_final_donor_exposure_target",
                "portfolio_mutation": False,
            })

    buys = round(sum(_num(row.get("notional_eur")) for row in trades if row.get("action") == "buy"), 2)
    sells = round(sum(_num(row.get("notional_eur")) for row in trades if row.get("action") == "sell"), 2)
    gross = round(buys + sells, 2)
    return {
        "trades": trades,
        "trade_count": len(trades),
        "buy_notional_eur": buys,
        "sell_notional_eur": sells,
        "gross_traded_notional_eur": gross,
        "gross_traded_notional_pct_nav": round(gross / nav * 100.0, 6) if nav else 0.0,
        "two_way_turnover_pct_nav": round(gross / (2.0 * nav) * 100.0, 6) if nav else 0.0,
        "cost_scenarios": _trade_costs(trades, policy),
        "execution_authority": False,
    }


def _variant(
    name: str,
    weights: dict[str, float],
    nav: float,
    evidence_index: dict[str, dict[str, Any]],
    portfolio: dict[str, Any],
    market_evidence: dict[str, Any],
    policy: dict[str, Any],
    donor_cash_weight: float,
    *,
    retain_incumbents: bool = False,
    combination_disclosures: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    rows = [_security_row(exposure_id, weight, nav, evidence_index.get(exposure_id, {})) for exposure_id, weight in weights.items() if weight > 0]
    rows.sort(key=lambda row: (-_num(row.get("target_weight_pct")), str(row.get("exposure_id"))))
    allocated = round(sum(_num(row.get("allocated_value_eur")) for row in rows), 2)
    cash = round(nav - allocated, 2)
    position_count = sum(1 for row in rows if int(row.get("whole_share_units") or 0) > 0)
    theoretical_position_count = sum(1 for weight in weights.values() if weight > 0)
    max_positions = int(((policy.get("portfolio") or {}).get("maximum_final_positions") or 8))
    max_weight = _num((policy.get("portfolio") or {}).get("maximum_single_exposure_weight_pct"), 30.0)
    blocked_rows = [row for row in rows if row.get("blockers")]
    high_concentration = [row.get("exposure_id") for row in rows if _num(row.get("target_weight_pct")) > max_weight]
    trade_plan = _build_trade_plan(rows, portfolio, market_evidence, nav, policy, retain_incumbents=retain_incumbents)
    return {
        "variant_id": name,
        "theoretical_target_weight_pct": round(sum(weights.values()), 6),
        "theoretical_cash_weight_pct": round(donor_cash_weight, 6),
        "theoretical_weight_total_pct": round(sum(weights.values()) + donor_cash_weight, 6),
        "theoretical_position_count": theoretical_position_count,
        "rounded_active_position_count": position_count,
        "maximum_positions": max_positions,
        "position_limit_status": "pass" if theoretical_position_count <= max_positions else "fail",
        "allocated_market_value_eur": allocated,
        "cash_after_whole_share_rounding_eur": cash,
        "cash_after_whole_share_rounding_pct": round(cash / nav * 100.0, 6) if nav else 0.0,
        "whole_share_weight_total_pct": round(allocated / nav * 100.0 + cash / nav * 100.0, 6) if nav else 0.0,
        "blocked_exposure_count": len(blocked_rows),
        "blocked_exposures": [row.get("exposure_id") for row in blocked_rows],
        "high_concentration_exposures": high_concentration,
        "combination_disclosures": combination_disclosures or [],
        "positions": rows,
        "transition_from_current": trade_plan,
        "authority": {
            "portfolio_mutation": False,
            "allocation_authority": False,
            "execution_authority": False,
        },
    }


def _build_stage_a(
    donor_weights: dict[str, float],
    nav: float,
    portfolio: dict[str, Any],
    evidence_index: dict[str, dict[str, Any]],
    market_evidence: dict[str, Any],
    policy: dict[str, Any],
) -> dict[str, Any]:
    staged = policy.get("staged_variant") if isinstance(policy.get("staged_variant"), dict) else {}
    requested_fraction = _num(staged.get("initial_new_position_fraction_of_donor_target"), 0.5)
    exposure_ids = [str(value) for value in (staged.get("stage_a_new_exposure_ids") or [])]
    current_cash = _num(portfolio.get("cash_eur"))
    minimum_cash_weight = _num((policy.get("portfolio") or {}).get("staged_minimum_cash_weight_pct"), 10.0)
    minimum_cash = nav * minimum_cash_weight / 100.0
    full_desired = nav * sum(donor_weights.get(exposure_id, 0.0) for exposure_id in exposure_ids) / 100.0
    available = max(0.0, current_cash - minimum_cash)
    affordable_fraction = available / full_desired if full_desired > 0 else 0.0
    applied_fraction = min(requested_fraction, affordable_fraction)

    new_weights = {exposure_id: donor_weights.get(exposure_id, 0.0) * applied_fraction for exposure_id in exposure_ids}
    new_rows = [_security_row(exposure_id, weight, nav, evidence_index.get(exposure_id, {})) for exposure_id, weight in new_weights.items()]
    new_rows.sort(key=lambda row: (-_num(row.get("target_weight_pct")), str(row.get("exposure_id"))))
    buys = round(sum(_num(row.get("allocated_value_eur")) for row in new_rows), 2)

    incumbent_rows: list[dict[str, Any]] = []
    for position in portfolio.get("positions") or []:
        if not isinstance(position, dict):
            continue
        incumbent_rows.append({
            "exposure_id": None,
            "transition_role": "retained_incumbent_stage_a",
            "ticker": position.get("ticker") or position.get("exchange_ticker"),
            "isin": position.get("isin"),
            "fund_name": position.get("fund_name"),
            "whole_share_units": int(_num(position.get("shares"))),
            "allocated_value_eur": round(_num(position.get("market_value_eur")), 2),
            "rounded_weight_pct": round(_num(position.get("market_value_eur")) / nav * 100.0, 6) if nav else 0.0,
            "portfolio_mutation": False,
        })

    cash = round(current_cash - buys, 2)
    all_rows = incumbent_rows + new_rows
    position_count = sum(1 for row in all_rows if int(row.get("whole_share_units") or 0) > 0)
    max_positions = int(((policy.get("portfolio") or {}).get("maximum_final_positions") or 8))
    stage_a_trades = _build_trade_plan(new_rows, {"positions": []}, market_evidence, nav, policy, retain_incumbents=True)
    stage_a_trades["sell_notional_eur"] = 0.0
    stage_a_trades["gross_traded_notional_eur"] = stage_a_trades["buy_notional_eur"]
    stage_a_trades["gross_traded_notional_pct_nav"] = round(stage_a_trades["buy_notional_eur"] / nav * 100.0, 6) if nav else 0.0
    stage_a_trades["two_way_turnover_pct_nav"] = round(stage_a_trades["buy_notional_eur"] / (2.0 * nav) * 100.0, 6) if nav else 0.0

    return {
        "stage_id": "stage_a_cash_led_top_five_half_size",
        "requested_fraction": requested_fraction,
        "applied_fraction": round(applied_fraction, 8),
        "minimum_cash_weight_pct": minimum_cash_weight,
        "sales_authorized": False,
        "position_count": position_count,
        "maximum_positions": max_positions,
        "position_limit_status": "pass" if position_count <= max_positions else "fail",
        "new_positions": new_rows,
        "retained_incumbents": incumbent_rows,
        "cash_after_allocations_eur": cash,
        "cash_after_allocations_pct": round(cash / nav * 100.0, 6) if nav else 0.0,
        "cash_floor_status": "pass" if cash + 0.01 >= minimum_cash else "fail",
        "trade_plan": stage_a_trades,
        "authority": {"portfolio_mutation": False, "execution_authority": False},
    }


def build(
    shared_target: dict[str, Any],
    market_evidence: dict[str, Any],
    portfolio: dict[str, Any],
    policy: dict[str, Any],
) -> dict[str, Any]:
    if shared_target.get("schema_version") != "etf_shared_portfolio_target_v1":
        raise RuntimeError("Unsupported shared target schema")
    if market_evidence.get("schema_version") != "etf_eu_allocator_market_evidence_v1":
        raise RuntimeError("Unsupported market evidence schema")
    for artifact in (shared_target, market_evidence):
        if artifact.get("portfolio_mutation") not in (False, None):
            raise RuntimeError("Input violates shadow authority boundary")

    nav = _num(portfolio.get("nav_eur"))
    if nav <= 0:
        raise RuntimeError("EU portfolio NAV must be positive")
    donor_cash_weight = _num((shared_target.get("portfolio_summary") or {}).get("cash_weight_pct"))
    donor_weights = _target_weights(shared_target)
    evidence = _evidence_index(market_evidence)

    strict = _variant(
        "strict_donor_replication",
        dict(donor_weights),
        nav,
        evidence,
        portfolio,
        market_evidence,
        policy,
        donor_cash_weight,
    )

    efficient_weights = dict(donor_weights)
    disclosures: list[dict[str, Any]] = []
    combinations = ((policy.get("efficient_variant") or {}).get("combine_exposures") or [])
    for combination in combinations:
        if not isinstance(combination, dict):
            continue
        destination = str(combination.get("destination_exposure_id") or "")
        sources = [str(value) for value in (combination.get("source_exposure_ids") or [])]
        combined_weight = sum(donor_weights.get(source, 0.0) for source in sources)
        for source in sources:
            if source != destination:
                efficient_weights.pop(source, None)
        efficient_weights[destination] = combined_weight
        disclosures.append({
            "destination_exposure_id": destination,
            "source_exposure_ids": sources,
            "combined_weight_pct": round(combined_weight, 6),
            "rationale": combination.get("rationale"),
            "exposure_purity_tradeoff": True,
        })

    efficient = _variant(
        "efficient_eight_position",
        efficient_weights,
        nav,
        evidence,
        portfolio,
        market_evidence,
        policy,
        donor_cash_weight,
        combination_disclosures=disclosures,
    )

    stage_a = _build_stage_a(donor_weights, nav, portfolio, evidence, market_evidence, policy)
    stage_b = {
        "stage_id": "stage_b_complete_efficient_target",
        "prerequisite": "separate transition authorization after repeated strategy confirmation and evidence review",
        "target_variant_id": efficient.get("variant_id"),
        "planned_final_position_count": efficient.get("rounded_active_position_count"),
        "planned_final_cash_pct": efficient.get("cash_after_whole_share_rounding_pct"),
        "current_incumbents_to_exit_or_reduce": [str(row.get("ticker") or row.get("exchange_ticker") or "") for row in portfolio.get("positions") or [] if isinstance(row, dict)],
        "transition_trade_plan": efficient.get("transition_from_current"),
        "portfolio_mutation": False,
        "execution_authority": False,
    }

    return {
        "schema_version": "etf_eu_target_allocator_shadow_v1",
        "artifact_type": "etf_eu_target_allocator_shadow",
        "generated_at_utc": _utc_now(),
        "report_date": market_evidence.get("report_date"),
        "source_run_id": shared_target.get("source_run_id"),
        "eu_nav_eur": nav,
        "eu_current_cash_eur": portfolio.get("cash_eur"),
        "donor_cash_weight_pct": donor_cash_weight,
        "donor_exposure_target_count": len(donor_weights),
        "market_evidence_summary": market_evidence.get("summary"),
        "variants": {
            "strict": strict,
            "efficient_eight_position": efficient,
            "staged_transition": {"stage_a": stage_a, "stage_b": stage_b},
        },
        "overlap_review": {
            "exact_donor_exposure_overlap_current_eu_pct": 0.0,
            "economic_overlap_status": "material_but_not_quantified_in_v1",
            "incumbent_notes": {
                "VWCE": "broad global equity overlaps economically with multiple donor equity sleeves but is not a pure substitute",
                "SXR8": "broad US equity overlaps economically with US sector sleeves but is not a pure substitute",
                "EUNA": "bond stabilizer has low direct overlap and represents a deliberate transition-role deviation from the donor target",
            },
            "next_required_analysis": "holdings-level overlap and factor-concentration matrix",
        },
        "authority": {
            "shadow_only": True,
            "portfolio_mutation": False,
            "funding_authority": False,
            "execution_authority": False,
            "production_delivery_authority": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build strict, efficient and staged EU allocator variants")
    parser.add_argument("--shared-portfolio-target", type=Path, required=True)
    parser.add_argument("--market-evidence", type=Path, required=True)
    parser.add_argument("--portfolio-state", type=Path, default=Path("output/etf_eu_portfolio_state.json"))
    parser.add_argument("--policy", type=Path, default=Path("config/etf_eu_allocator_policy.yml"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    result = build(
        shared_target=_load_json(args.shared_portfolio_target),
        market_evidence=_load_json(args.market_evidence),
        portfolio=_load_json(args.portfolio_state),
        policy=_load_yaml(args.policy),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
