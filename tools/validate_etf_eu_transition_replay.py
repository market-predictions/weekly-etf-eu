from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Replay artifact must be a JSON object")
    return payload


def num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def validate(payload: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if payload.get("schema_version") != "etf_eu_transition_composition_replay_v1":
        blockers.append("unexpected schema_version")
    for key in (
        "valuation_grade",
        "portfolio_mutation",
        "funding_authority",
        "execution_authority",
        "optimization_authority",
        "production_delivery_authority",
    ):
        if payload.get(key) is not False:
            blockers.append(f"{key} must be false")
    methodology = payload.get("methodology") if isinstance(payload.get("methodology"), dict) else {}
    if methodology.get("type") != "fixed_composition_historical_replay":
        blockers.append("fixed-composition methodology missing")
    if methodology.get("historical_decisions_reconstructed") is not False:
        blockers.append("replay may not claim historical decision reconstruction")
    if methodology.get("optimization_performed") is not False:
        blockers.append("replay may not optimize variants")
    if "sanity_check_only" not in str(methodology.get("purpose") or ""):
        blockers.append("sanity-check interpretation boundary missing")
    if int(num(payload.get("return_observation_count"))) < 59:
        blockers.append("insufficient common return observations")
    if "do not reconstruct" not in str(payload.get("interpretation_boundary") or "").lower():
        blockers.append("historical-information boundary missing")

    results = {str(row.get("variant_id")): row for row in payload.get("variant_results") or [] if isinstance(row, dict)}
    required = {
        "current_eu_portfolio",
        "strict_mapped_replication",
        "staged_cash_first_50pct",
        "staged_policy_driven_v1",
    }
    if set(results) != required:
        blockers.append("replay variant set is incomplete")
    metric_fields = (
        "gross_cumulative_return_pct",
        "net_cumulative_return_after_initial_cost_pct",
        "annualized_return_pct",
        "annualized_volatility_pct",
        "maximum_drawdown_pct",
        "worst_daily_return_pct",
        "best_daily_return_pct",
        "positive_day_share_pct",
    )
    for variant_id, row in results.items():
        weights = row.get("composition_weights_pct") if isinstance(row.get("composition_weights_pct"), dict) else {}
        total = sum(num(value) for value in weights.values()) + num(row.get("cash_weight_pct"))
        if abs(total - 100.0) > 0.02:
            blockers.append(f"{variant_id} weights plus cash do not reconcile to 100%: {total}")
        if int(num(row.get("trading_day_count"))) != int(num(payload.get("return_observation_count"))):
            blockers.append(f"{variant_id} replay observation count mismatch")
        for field in metric_fields:
            value = num(row.get(field), float("nan"))
            if not math.isfinite(value):
                blockers.append(f"{variant_id} non-finite metric: {field}")
        if len(row.get("daily_return_series") or []) != int(num(payload.get("return_observation_count"))):
            blockers.append(f"{variant_id} daily return series length mismatch")
    if num(results.get("current_eu_portfolio", {}).get("initial_cost_pct_nav")) != 0:
        blockers.append("current portfolio must have zero modeled transition cost")
    if num(results.get("staged_policy_driven_v1", {}).get("initial_cost_pct_nav")) <= 0:
        blockers.append("policy-driven variant initial cost is missing")
    if not payload.get("pairwise_daily_return_correlations"):
        blockers.append("pairwise replay correlations missing")
    return blockers


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args()
    blockers = validate(load(args.artifact))
    print(json.dumps({"valid": not blockers, "blockers": blockers}, indent=2))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
