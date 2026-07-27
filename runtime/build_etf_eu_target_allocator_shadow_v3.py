from __future__ import annotations

import argparse
import json
import math
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
        raise RuntimeError(f"Expected YAML object: {path}")
    return payload


def num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def evidence_index(evidence: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("exposure_id")): row
        for row in evidence.get("rows") or []
        if isinstance(row, dict)
    }


def target_rows(sync: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        dict(row)
        for row in sync.get("portfolio_alignment_rows") or []
        if isinstance(row, dict)
        and row.get("exposure_id") != "cash"
        and num(row.get("donor_target_weight_pct")) > 0
    ]
    return sorted(rows, key=lambda row: (-num(row.get("donor_target_weight_pct")), str(row.get("exposure_id"))))


def verified_candidate_line(row: dict[str, Any]) -> dict[str, Any] | None:
    candidate = row.get("preferred_ucits_candidate") if isinstance(row.get("preferred_ucits_candidate"), dict) else None
    if not candidate:
        return None
    lines = [
        line
        for line in candidate.get("trading_lines") or []
        if isinstance(line, dict)
        and str(line.get("verification_status") or "").startswith("verified_ucits_trading_line")
    ]
    lines.sort(key=lambda line: (str(line.get("trading_currency")) != "EUR", str(line.get("exchange")) != "Xetra"))
    return lines[0] if lines else None


def eligibility(row: dict[str, Any], evidence: dict[str, Any], stage_policy: dict[str, Any]) -> tuple[bool, list[str]]:
    blockers: list[str] = []
    candidate = row.get("preferred_ucits_candidate") if isinstance(row.get("preferred_ucits_candidate"), dict) else None
    if not candidate:
        blockers.append("no_ucits_equivalent")
    else:
        if candidate.get("instrument_type") != "UCITS ETF":
            blockers.append("product_type_blocked")
        if candidate.get("priips_kid_status") != "available":
            blockers.append("kid_missing")
        if not verified_candidate_line(row):
            blockers.append("trading_line_unverified")
    status = str(evidence.get("status") or "")
    if not status.startswith("priced_") or evidence.get("completed_close") is not True or num(evidence.get("close_price")) <= 0:
        blockers.append("pricing_missing_or_stale")
    if num(evidence.get("price_age_calendar_days"), 9999) > num(stage_policy.get("maximum_price_age_calendar_days"), 7):
        blockers.append("pricing_missing_or_stale")
    if num(evidence.get("median_daily_traded_value_eur_20d")) < num(stage_policy.get("minimum_median_daily_traded_value_eur_20d")):
        blockers.append("liquidity_below_threshold")
    if str(evidence.get("candidate_role") or "") == "donor_target_structure_review":
        blockers.append("product_structure_review_required")
    return not blockers, sorted(set(blockers))


def embedded_lower_bound(overlap: dict[str, Any], exposure_id: str) -> float:
    embedded = overlap.get("portfolio_embedded_exposure_lower_bounds") if isinstance(overlap.get("portfolio_embedded_exposure_lower_bounds"), dict) else {}
    if exposure_id == "ai_compute_infrastructure":
        return num(embedded.get("semiconductor_pct_nav"))
    if exposure_id == "cyber_security":
        return num(embedded.get("cybersecurity_pct_nav"))
    return 0.0


def candidate_descriptor(row: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    candidate = row.get("preferred_ucits_candidate") if isinstance(row.get("preferred_ucits_candidate"), dict) else {}
    line = verified_candidate_line(row) or {}
    return {
        "fund_name": candidate.get("fund_name"),
        "isin": candidate.get("isin"),
        "ticker": line.get("exchange_ticker") or evidence.get("ticker"),
        "exchange": line.get("exchange") or evidence.get("exchange"),
        "currency": line.get("trading_currency") or evidence.get("currency"),
        "price_eur": num(evidence.get("close_price")),
        "price_date": evidence.get("close_date"),
        "price_age_calendar_days": evidence.get("price_age_calendar_days"),
        "median_daily_traded_value_eur_20d": evidence.get("median_daily_traded_value_eur_20d"),
        "evidence_status": evidence.get("status"),
        "evidence_source_quality": evidence.get("source_quality"),
    }


def build_policy_variant(
    sync: dict[str, Any],
    portfolio: dict[str, Any],
    evidence: dict[str, Any],
    overlap: dict[str, Any],
    policy: dict[str, Any],
) -> dict[str, Any]:
    stage = policy.get("stage_1") if isinstance(policy.get("stage_1"), dict) else {}
    nav = num(portfolio.get("nav_eur"))
    cash = num(portfolio.get("cash_eur"))
    current_positions = [dict(row) for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    evidence_by_exposure = evidence_index(evidence)
    targets = target_rows(sync)

    max_positions = int(num(stage.get("maximum_positions"), 8))
    available_slots = max(0, max_positions - len(current_positions))
    turnover_cap_eur = nav * num(stage.get("maximum_gross_turnover_pct_nav")) / 100.0
    reserve_cash_eur = nav * num(stage.get("minimum_post_stage_cash_pct_nav")) / 100.0
    cost_rate = num(stage.get("transaction_cost_bps")) / 10000.0
    cash_gross_capacity = max(0.0, cash - reserve_cash_eur) / (1.0 + cost_rate)
    initial_gross_budget = min(turnover_cap_eur, cash_gross_capacity)
    remaining_gross_budget = initial_gross_budget
    direct_cap = num(stage.get("maximum_new_direct_position_pct_nav"))
    min_trade = num(stage.get("minimum_new_trade_pct_nav"))
    effective_caps = stage.get("effective_theme_caps_pct_nav") if isinstance(stage.get("effective_theme_caps_pct_nav"), dict) else {}

    allocation_rows: list[dict[str, Any]] = []
    selected_count = 0
    total_buy = 0.0
    total_cost = 0.0

    for row in targets:
        exposure_id = str(row.get("exposure_id") or "")
        donor_weight = num(row.get("donor_target_weight_pct"))
        evidence_row = evidence_by_exposure.get(exposure_id, {})
        eligible, blockers = eligibility(row, evidence_row, stage)
        embedded = embedded_lower_bound(overlap, exposure_id)
        effective_cap = num(effective_caps.get(exposure_id), donor_weight)
        effective_direct_capacity = max(0.0, effective_cap - embedded)
        requested_weight = min(donor_weight, direct_cap, effective_direct_capacity)
        price = num(evidence_row.get("close_price"))
        order: dict[str, Any]
        selected = False

        if eligible and selected_count >= available_slots:
            blockers.append("position_limit")
        if eligible and remaining_gross_budget <= 0:
            blockers.append("stage_turnover_or_cash_budget")

        max_target_value = min(nav * requested_weight / 100.0, remaining_gross_budget)
        shares = math.floor(max_target_value / price) if eligible and price > 0 and not blockers else 0
        gross = shares * price
        actual_weight = gross / nav * 100.0 if nav else 0.0
        if shares > 0 and actual_weight < min_trade:
            blockers.append("minimum_trade_size")
            shares = 0
            gross = 0.0
            actual_weight = 0.0
        if shares > 0 and not blockers:
            selected = True
            selected_count += 1
            cost = gross * cost_rate
            total_buy += gross
            total_cost += cost
            remaining_gross_budget -= gross
            order = {
                "current_shares": 0,
                "target_shares": shares,
                "share_delta": shares,
                "side": "BUY",
                "gross_trade_value_eur": round(gross, 2),
                "estimated_cost_eur": round(cost, 2),
                "target_market_value_eur": round(gross, 2),
                "rounding_residual_eur": round(max(nav * requested_weight / 100.0 - gross, 0.0), 2),
            }
        else:
            order = {
                "current_shares": 0,
                "target_shares": 0,
                "share_delta": 0,
                "side": "BLOCKED" if blockers else "DEFERRED",
                "gross_trade_value_eur": 0.0,
                "estimated_cost_eur": 0.0,
                "target_market_value_eur": 0.0,
                "rounding_residual_eur": round(nav * requested_weight / 100.0, 2),
            }

        allocation_rows.append({
            "exposure_id": exposure_id,
            "donor_target_weight_pct": round(donor_weight, 6),
            "policy_requested_direct_weight_pct": round(requested_weight, 6),
            "variant_target_weight_pct": round(actual_weight, 6),
            "embedded_incumbent_exposure_lower_bound_pct_nav": round(embedded, 6),
            "effective_post_stage_exposure_lower_bound_pct_nav": round(embedded + actual_weight, 6),
            "effective_theme_cap_pct_nav": round(effective_cap, 6),
            "selected": selected,
            "eligible": eligible,
            "blockers": sorted(set(blockers)),
            "candidate": candidate_descriptor(row, evidence_row),
            "order": order,
        })

    legacy_rows: list[dict[str, Any]] = []
    legacy_value = 0.0
    for position in current_positions:
        shares = int(num(position.get("shares")))
        value = num(position.get("market_value_eur"))
        legacy_value += value
        legacy_rows.append({
            "ticker": position.get("ticker") or position.get("exchange_ticker"),
            "isin": position.get("isin"),
            "fund_name": position.get("fund_name"),
            "current_shares": shares,
            "target_shares": shares,
            "share_delta": 0,
            "side": "HOLD",
            "gross_trade_value_eur": 0.0,
            "estimated_cost_eur": 0.0,
            "target_market_value_eur": round(value, 2),
            "transition_role": "policy_governed_stage_1_retention",
        })

    projected_cash = cash - total_buy - total_cost
    target_invested = legacy_value + total_buy
    direct_implemented = sum(num(row.get("variant_target_weight_pct")) for row in allocation_rows)
    donor_target_total = sum(num(row.get("donor_target_weight_pct")) for row in allocation_rows)
    policy_checks = {
        "within_position_limit": len(current_positions) + selected_count <= max_positions,
        "within_turnover_cap": total_buy <= turnover_cap_eur + 0.01,
        "minimum_cash_reserve_met": projected_cash >= reserve_cash_eur - 0.01,
        "new_position_caps_met": all(
            num(row.get("variant_target_weight_pct")) <= direct_cap + 0.0001
            for row in allocation_rows
        ),
        "effective_theme_caps_met": all(
            num(row.get("effective_post_stage_exposure_lower_bound_pct_nav")) <= num(row.get("effective_theme_cap_pct_nav")) + 0.0001
            for row in allocation_rows
        ),
        "incumbents_retained": all(row.get("side") == "HOLD" for row in legacy_rows),
        "cash_nonnegative": projected_cash >= -0.01,
    }

    return {
        "variant_id": "staged_policy_driven_v1",
        "allocation_method": stage.get("allocation_method"),
        "progress_factor": None,
        "retain_legacy_positions": True,
        "position_limit": max_positions,
        "allocation_rows": allocation_rows,
        "legacy_rows": legacy_rows,
        "policy_checks": policy_checks,
        "summary": {
            "position_count": len(current_positions) + selected_count,
            "projected_invested_market_value_eur": round(target_invested, 2),
            "projected_cash_eur": round(projected_cash, 2),
            "projected_cash_weight_pct": round(projected_cash / nav * 100.0, 6) if nav else 0.0,
            "gross_buy_value_eur": round(total_buy, 2),
            "gross_sell_value_eur": 0.0,
            "gross_turnover_eur": round(total_buy, 2),
            "gross_turnover_pct_nav": round(total_buy / nav * 100.0, 6) if nav else 0.0,
            "estimated_transaction_cost_eur": round(total_cost, 2),
            "direct_donor_target_weight_implemented_pct": round(direct_implemented, 6),
            "unimplemented_donor_target_weight_pct": round(max(donor_target_total - direct_implemented, 0.0), 6),
            "within_position_limit": policy_checks["within_position_limit"],
            "cash_nonnegative": policy_checks["cash_nonnegative"],
        },
        "stage_2_entry_conditions": list(policy.get("stage_2_entry_conditions") or []),
        "stage_2_source_priority": list(policy.get("stage_2_source_priority") or []),
    }


def build(
    base_allocator: dict[str, Any],
    sync: dict[str, Any],
    portfolio: dict[str, Any],
    evidence: dict[str, Any],
    overlap: dict[str, Any],
    policy: dict[str, Any],
    output: Path,
) -> None:
    if base_allocator.get("schema_version") != "etf_eu_target_allocator_shadow_v2":
        raise RuntimeError("Expected v2 base allocator")
    for source in (base_allocator.get("authority") or {}, overlap):
        if source.get("portfolio_mutation") is not False or source.get("execution_authority") is not False:
            raise RuntimeError("Source artifact violates shadow boundary")
    policy_variant = build_policy_variant(sync, portfolio, evidence, overlap, policy)
    variants = [dict(row) for row in base_allocator.get("variants") or [] if isinstance(row, dict)]
    variants.append(policy_variant)
    payload = dict(base_allocator)
    payload["schema_version"] = "etf_eu_target_allocator_shadow_v3"
    payload["generated_at_utc"] = utc_now()
    payload["variants"] = variants
    payload["preferred_shadow_variant"] = "staged_policy_driven_v1"
    payload["preferred_reason"] = (
        "Derives stage-one sizes from turnover, cash, position, liquidity and effective-theme caps; "
        "retains incumbents pending governed stage-two overlap reduction."
    )
    payload["policy_contract"] = {
        "schema_version": policy.get("schema_version"),
        "source": "config/etf_eu_transition_policy_v1.yml",
        "stage_1": policy.get("stage_1"),
        "hard_boundaries": policy.get("hard_boundaries"),
    }
    payload["incumbent_overlap_review"] = {
        "schema_version": overlap.get("schema_version"),
        "source": "output/sync_shadow/etf_eu_incumbent_overlap_review.json",
        "embedded_exposure_lower_bounds": overlap.get("portfolio_embedded_exposure_lower_bounds"),
        "incumbent_dispositions": overlap.get("incumbent_dispositions"),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build policy-driven EU target allocator shadow")
    parser.add_argument("--base-allocator", type=Path, required=True)
    parser.add_argument("--sync-shadow", type=Path, required=True)
    parser.add_argument("--portfolio-state", type=Path, default=Path("output/etf_eu_portfolio_state.json"))
    parser.add_argument("--transition-evidence", type=Path, required=True)
    parser.add_argument("--overlap-review", type=Path, required=True)
    parser.add_argument("--policy", type=Path, default=Path("config/etf_eu_transition_policy_v1.yml"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(
        load_json(args.base_allocator),
        load_json(args.sync_shadow),
        load_json(args.portfolio_state),
        load_json(args.transition_evidence),
        load_json(args.overlap_review),
        load_yaml(args.policy),
        args.output,
    )


if __name__ == "__main__":
    main()
