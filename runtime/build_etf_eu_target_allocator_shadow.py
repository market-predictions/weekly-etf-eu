from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


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


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def evidence_index(evidence: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(row.get("exposure_id")): row for row in (evidence.get("rows") or []) if isinstance(row, dict)}


def current_position_rows(portfolio: dict[str, Any]) -> list[dict[str, Any]]:
    return [dict(row) for row in (portfolio.get("positions") or []) if isinstance(row, dict)]


def target_rows(sync: dict[str, Any]) -> list[dict[str, Any]]:
    return [dict(row) for row in (sync.get("portfolio_alignment_rows") or []) if isinstance(row, dict) and row.get("exposure_id") != "cash" and num(row.get("donor_target_weight_pct")) > 0]


def candidate_line(row: dict[str, Any]) -> dict[str, Any] | None:
    candidate = row.get("preferred_ucits_candidate") if isinstance(row.get("preferred_ucits_candidate"), dict) else None
    if not candidate:
        return None
    lines = [line for line in (candidate.get("trading_lines") or []) if isinstance(line, dict)]
    lines.sort(key=lambda line: (str(line.get("trading_currency")) != "EUR", str(line.get("exchange")) != "Xetra"))
    return lines[0] if lines else None


def eligible_target(row: dict[str, Any], evidence: dict[str, Any]) -> tuple[bool, list[str]]:
    blockers = list(row.get("divergence_reason_codes") or [])
    candidate = row.get("preferred_ucits_candidate") if isinstance(row.get("preferred_ucits_candidate"), dict) else None
    if not candidate:
        blockers.append("no_ucits_equivalent")
    else:
        if candidate.get("instrument_type") != "UCITS ETF":
            blockers.append("product_type_blocked")
        if candidate.get("priips_kid_status") != "available":
            blockers.append("kid_missing")
        if not candidate_line(row):
            blockers.append("trading_line_unverified")
    if evidence.get("status") != "priced_non_authoritative" or evidence.get("completed_close") is not True:
        blockers.append("pricing_missing_or_stale")
    if num(evidence.get("close_price")) <= 0:
        blockers.append("pricing_missing_or_stale")
    return not blockers, sorted(set(blockers))


def estimate_order(current_shares: int, target_value: float, price: float, cost_bps: float) -> dict[str, Any]:
    target_shares = max(0, math.floor(target_value / price)) if price > 0 else 0
    share_delta = target_shares - current_shares
    gross = abs(share_delta) * price
    estimated_cost = gross * cost_bps / 10000.0
    return {
        "current_shares": current_shares,
        "target_shares": target_shares,
        "share_delta": share_delta,
        "side": "BUY" if share_delta > 0 else "SELL" if share_delta < 0 else "HOLD",
        "gross_trade_value_eur": round(gross, 2),
        "estimated_cost_eur": round(estimated_cost, 2),
        "target_market_value_eur": round(target_shares * price, 2),
        "rounding_residual_eur": round(max(target_value - target_shares * price, 0.0), 2),
    }


def candidate_descriptor(row: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    candidate = row.get("preferred_ucits_candidate") if isinstance(row.get("preferred_ucits_candidate"), dict) else {}
    line = candidate_line(row) or {}
    return {
        "fund_name": candidate.get("fund_name"),
        "isin": candidate.get("isin"),
        "ticker": line.get("exchange_ticker") or evidence.get("ticker"),
        "exchange": line.get("exchange") or evidence.get("exchange"),
        "currency": line.get("trading_currency") or evidence.get("currency"),
        "price_eur": num(evidence.get("close_price")),
        "price_date": evidence.get("close_date"),
        "median_daily_traded_value_eur_20d": evidence.get("median_daily_traded_value_eur_20d"),
    }


def build_variant(
    *,
    name: str,
    nav: float,
    cash: float,
    current_positions: list[dict[str, Any]],
    targets: list[dict[str, Any]],
    evidence_by_exposure: dict[str, dict[str, Any]],
    position_limit: int,
    cost_bps: float,
    progress_factor: float,
    retain_legacy: bool,
) -> dict[str, Any]:
    evaluated: list[dict[str, Any]] = []
    for row in sorted(targets, key=lambda item: -num(item.get("donor_target_weight_pct"))):
        exposure_id = str(row.get("exposure_id"))
        evidence = evidence_by_exposure.get(exposure_id, {})
        eligible, blockers = eligible_target(row, evidence)
        evaluated.append({"row": row, "evidence": evidence, "eligible": eligible, "blockers": blockers})

    selected = [item for item in evaluated if item["eligible"]][:position_limit]
    selected_ids = {str(item["row"].get("exposure_id")) for item in selected}
    allocation_rows: list[dict[str, Any]] = []
    total_buy = 0.0
    total_sell = 0.0
    total_cost = 0.0

    for item in evaluated:
        row = item["row"]
        evidence = item["evidence"]
        exposure_id = str(row.get("exposure_id"))
        donor_weight = num(row.get("donor_target_weight_pct"))
        selected_flag = exposure_id in selected_ids
        target_weight = donor_weight * progress_factor if selected_flag else 0.0
        target_value = nav * target_weight / 100.0
        order = estimate_order(0, target_value, num(evidence.get("close_price")), cost_bps) if selected_flag else {
            "current_shares": 0, "target_shares": 0, "share_delta": 0, "side": "BLOCKED" if item["blockers"] else "DEFERRED",
            "gross_trade_value_eur": 0.0, "estimated_cost_eur": 0.0, "target_market_value_eur": 0.0,
            "rounding_residual_eur": round(target_value, 2),
        }
        total_buy += order["gross_trade_value_eur"] if order["share_delta"] > 0 else 0.0
        total_cost += order["estimated_cost_eur"]
        allocation_rows.append({
            "exposure_id": exposure_id,
            "donor_target_weight_pct": round(donor_weight, 6),
            "variant_target_weight_pct": round(target_weight, 6),
            "selected": selected_flag,
            "eligible": item["eligible"],
            "blockers": item["blockers"] if not selected_flag else [],
            "candidate": candidate_descriptor(row, evidence),
            "order": order,
        })

    legacy_rows: list[dict[str, Any]] = []
    for position in current_positions:
        price = num(position.get("current_price_local"))
        shares = int(num(position.get("shares")))
        target_shares = shares if retain_legacy else 0
        share_delta = target_shares - shares
        gross = abs(share_delta) * price
        cost = gross * cost_bps / 10000.0
        total_sell += gross if share_delta < 0 else 0.0
        total_cost += cost
        legacy_rows.append({
            "ticker": position.get("ticker") or position.get("exchange_ticker"),
            "isin": position.get("isin"),
            "fund_name": position.get("fund_name"),
            "current_shares": shares,
            "target_shares": target_shares,
            "share_delta": share_delta,
            "side": "SELL" if share_delta < 0 else "HOLD",
            "gross_trade_value_eur": round(gross, 2),
            "estimated_cost_eur": round(cost, 2),
            "target_market_value_eur": round(target_shares * price, 2),
            "transition_role": "temporary_legacy_retention" if retain_legacy else "legacy_exit",
        })

    projected_cash = cash + total_sell - total_buy - total_cost
    target_positions = sum(1 for row in allocation_rows if num((row.get("order") or {}).get("target_shares")) > 0) + sum(1 for row in legacy_rows if num(row.get("target_shares")) > 0)
    target_invested = sum(num((row.get("order") or {}).get("target_market_value_eur")) for row in allocation_rows) + sum(num(row.get("target_market_value_eur")) for row in legacy_rows)
    unresolved_weight = sum(num(row.get("donor_target_weight_pct")) for row in allocation_rows if not row.get("selected"))
    return {
        "variant_id": name,
        "progress_factor": progress_factor,
        "retain_legacy_positions": retain_legacy,
        "position_limit": position_limit,
        "allocation_rows": allocation_rows,
        "legacy_rows": legacy_rows,
        "summary": {
            "position_count": target_positions,
            "projected_invested_market_value_eur": round(target_invested, 2),
            "projected_cash_eur": round(projected_cash, 2),
            "projected_cash_weight_pct": round(projected_cash / nav * 100.0, 6) if nav else 0.0,
            "gross_buy_value_eur": round(total_buy, 2),
            "gross_sell_value_eur": round(total_sell, 2),
            "gross_turnover_eur": round(total_buy + total_sell, 2),
            "gross_turnover_pct_nav": round((total_buy + total_sell) / nav * 100.0, 6) if nav else 0.0,
            "estimated_transaction_cost_eur": round(total_cost, 2),
            "unimplemented_donor_target_weight_pct": round(unresolved_weight, 6),
            "within_position_limit": target_positions <= position_limit,
            "cash_nonnegative": projected_cash >= -0.01,
        },
    }


def build(sync: dict[str, Any], portfolio: dict[str, Any], evidence: dict[str, Any], output: Path, cost_bps: float, position_limit: int) -> None:
    authority = sync.get("authority") if isinstance(sync.get("authority"), dict) else {}
    if authority.get("portfolio_mutation") is not False or authority.get("execution_authority") is not False:
        raise RuntimeError("Synchronization input violates shadow authority")
    nav = num(portfolio.get("nav_eur"))
    cash = num(portfolio.get("cash_eur"))
    positions = current_position_rows(portfolio)
    targets = target_rows(sync)
    evidence_by_exposure = evidence_index(evidence)
    variants = [
        build_variant(name="strict_mapped_replication", nav=nav, cash=cash, current_positions=positions, targets=targets, evidence_by_exposure=evidence_by_exposure, position_limit=99, cost_bps=cost_bps, progress_factor=1.0, retain_legacy=False),
        build_variant(name="efficient_max_eight_positions", nav=nav, cash=cash, current_positions=positions, targets=targets, evidence_by_exposure=evidence_by_exposure, position_limit=position_limit, cost_bps=cost_bps, progress_factor=1.0, retain_legacy=False),
        build_variant(name="staged_cash_first_50pct", nav=nav, cash=cash, current_positions=positions, targets=targets, evidence_by_exposure=evidence_by_exposure, position_limit=position_limit, cost_bps=cost_bps, progress_factor=0.5, retain_legacy=True),
    ]
    payload = {
        "schema_version": "etf_eu_target_allocator_shadow_v1",
        "artifact_type": "etf_eu_target_allocator_shadow",
        "generated_at_utc": utc_now(),
        "report_date": evidence.get("report_date"),
        "source_run_id": (sync.get("shared_strategy") or {}).get("source_run_id"),
        "authority": {
            "shadow_only": True,
            "portfolio_mutation": False,
            "funding_authority": False,
            "execution_authority": False,
            "production_delivery_authority": False,
        },
        "assumptions": {
            "transaction_cost_bps_each_trade": cost_bps,
            "maximum_positions": position_limit,
            "whole_shares_only": True,
            "prices_non_authoritative_connectivity_only": True,
            "taxes_not_modelled": True,
            "bid_ask_spread_not_directly_observed": True,
            "market_impact_not_modelled": True,
        },
        "current_portfolio": {
            "nav_eur": nav,
            "cash_eur": cash,
            "position_count": len(positions),
        },
        "variants": variants,
        "preferred_shadow_variant": "staged_cash_first_50pct",
        "preferred_reason": "Uses existing cash first, limits immediate turnover, preserves incumbents pending overlap and exit review, and remains within the position cap.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync-shadow", type=Path, required=True)
    parser.add_argument("--portfolio-state", type=Path, default=Path("output/etf_eu_portfolio_state.json"))
    parser.add_argument("--transition-evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cost-bps", type=float, default=10.0)
    parser.add_argument("--position-limit", type=int, default=8)
    args = parser.parse_args()
    build(load(args.sync_shadow), load(args.portfolio_state), load(args.transition_evidence), args.output, args.cost_bps, args.position_limit)


if __name__ == "__main__":
    main()
