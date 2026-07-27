from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Expected JSON object")
    return payload


def _num(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
        return result if math.isfinite(result) else default
    except (TypeError, ValueError):
        return default


def _check_variant(name: str, variant: dict[str, Any], blockers: list[str]) -> None:
    if abs(_num(variant.get("theoretical_weight_total_pct")) - 100.0) > 0.1:
        blockers.append(f"{name}: theoretical weights do not reconcile to 100%")
    if abs(_num(variant.get("whole_share_weight_total_pct")) - 100.0) > 0.01:
        blockers.append(f"{name}: whole-share weights do not reconcile to 100%")
    if _num(variant.get("cash_after_whole_share_rounding_eur")) < -0.01:
        blockers.append(f"{name}: negative cash")
    positions = [row for row in (variant.get("positions") or []) if isinstance(row, dict)]
    active_count = sum(1 for row in positions if int(_num(row.get("whole_share_units"))) > 0)
    if active_count != int(_num(variant.get("rounded_active_position_count"))):
        blockers.append(f"{name}: active position count mismatch")
    for row in positions:
        if row.get("portfolio_mutation") is not False or row.get("allocation_authority") is not False:
            blockers.append(f"{name}: position authority boundary violated")
        price = _num(row.get("price_eur"))
        units = int(_num(row.get("whole_share_units")))
        allocated = _num(row.get("allocated_value_eur"))
        if units > 0 and price <= 0:
            blockers.append(f"{name}:{row.get('exposure_id')}: units without price")
        if abs(allocated - units * price) > 0.02:
            blockers.append(f"{name}:{row.get('exposure_id')}: whole-share value mismatch")
    trade_plan = variant.get("transition_from_current") if isinstance(variant.get("transition_from_current"), dict) else {}
    if trade_plan.get("execution_authority") is not False:
        blockers.append(f"{name}: trade plan has execution authority")
    if abs(_num(trade_plan.get("gross_traded_notional_eur")) - _num(trade_plan.get("buy_notional_eur")) - _num(trade_plan.get("sell_notional_eur"))) > 0.02:
        blockers.append(f"{name}: traded notional does not reconcile")
    costs = trade_plan.get("cost_scenarios") if isinstance(trade_plan.get("cost_scenarios"), dict) else {}
    if set(costs) != {"low", "base", "stress"}:
        blockers.append(f"{name}: cost scenarios incomplete")
    elif not (_num(costs["low"].get("estimated_cost_eur")) <= _num(costs["base"].get("estimated_cost_eur")) <= _num(costs["stress"].get("estimated_cost_eur"))):
        blockers.append(f"{name}: cost scenarios not monotonic")


def validate(payload: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if payload.get("schema_version") != "etf_eu_target_allocator_shadow_v1":
        blockers.append("unexpected schema_version")
    authority = payload.get("authority") if isinstance(payload.get("authority"), dict) else {}
    for key in ("portfolio_mutation", "funding_authority", "execution_authority", "production_delivery_authority"):
        if authority.get(key) is not False:
            blockers.append(f"authority {key} must be false")
    if authority.get("shadow_only") is not True:
        blockers.append("shadow_only authority flag missing")

    variants = payload.get("variants") if isinstance(payload.get("variants"), dict) else {}
    strict = variants.get("strict") if isinstance(variants.get("strict"), dict) else {}
    efficient = variants.get("efficient_eight_position") if isinstance(variants.get("efficient_eight_position"), dict) else {}
    staged = variants.get("staged_transition") if isinstance(variants.get("staged_transition"), dict) else {}
    if not strict or not efficient or not staged:
        blockers.append("all three allocator variants are required")
        return blockers

    _check_variant("strict", strict, blockers)
    _check_variant("efficient", efficient, blockers)

    if int(_num(strict.get("theoretical_position_count"))) != 9:
        blockers.append("strict variant must preserve nine donor exposures")
    if strict.get("position_limit_status") != "fail":
        blockers.append("strict variant must expose the eight-position policy failure")
    if int(_num(efficient.get("theoretical_position_count"))) > 8:
        blockers.append("efficient variant has more than eight theoretical positions")
    if efficient.get("position_limit_status") != "pass":
        blockers.append("efficient variant does not pass position limit")
    disclosures = [row for row in (efficient.get("combination_disclosures") or []) if isinstance(row, dict)]
    if len(disclosures) != 1:
        blockers.append("efficient variant requires one grid/utilities combination disclosure")
    elif set(disclosures[0].get("source_exposure_ids") or []) != {"grid_power", "power_utilities_capex"}:
        blockers.append("efficient combination sources are incorrect")

    stage_a = staged.get("stage_a") if isinstance(staged.get("stage_a"), dict) else {}
    stage_b = staged.get("stage_b") if isinstance(staged.get("stage_b"), dict) else {}
    if int(_num(stage_a.get("position_count"))) > int(_num(stage_a.get("maximum_positions"), 8)):
        blockers.append("Stage A exceeds position limit")
    if stage_a.get("position_limit_status") != "pass":
        blockers.append("Stage A position-limit status is not pass")
    if stage_a.get("cash_floor_status") != "pass":
        blockers.append("Stage A cash floor failed")
    if _num(stage_a.get("cash_after_allocations_pct")) + 0.001 < _num(stage_a.get("minimum_cash_weight_pct")):
        blockers.append("Stage A cash below minimum")
    if stage_a.get("sales_authorized") is not False:
        blockers.append("Stage A must not authorize sales")
    retained = [row for row in (stage_a.get("retained_incumbents") or []) if isinstance(row, dict)]
    if {str(row.get("ticker")) for row in retained} != {"VWCE", "EUNA", "SXR8"}:
        blockers.append("Stage A does not retain the three incumbents")
    new_rows = [row for row in (stage_a.get("new_positions") or []) if isinstance(row, dict)]
    if len(new_rows) != 5:
        blockers.append("Stage A must model five new exposures")
    if stage_b.get("target_variant_id") != "efficient_eight_position":
        blockers.append("Stage B must target efficient variant")
    if stage_b.get("portfolio_mutation") is not False or stage_b.get("execution_authority") is not False:
        blockers.append("Stage B authority boundary violated")

    return blockers


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate EU target allocator shadow")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    payload = _load(args.path)
    blockers = validate(payload)
    result = {
        "artifact_type": "etf_eu_target_allocator_validation",
        "path": str(args.path),
        "valid": not blockers,
        "blockers": blockers,
        "variant_ids": list((payload.get("variants") or {}).keys()),
    }
    print(json.dumps(result, indent=2))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
