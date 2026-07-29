from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


EXPECTED_SCENARIOS = {
    "policy_retained",
    "euna_to_cash",
    "euna_to_risky_pro_rata",
    "euna_doubled_from_cash",
}


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("EUNA review must be a JSON object")
    return payload


def num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def validate(payload: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if payload.get("schema_version") != "etf_eu_euna_risk_budget_review_v1":
        blockers.append("unexpected schema_version")
    if payload.get("artifact_type") != "etf_eu_euna_risk_budget_review":
        blockers.append("unexpected artifact_type")
    for key in (
        "portfolio_mutation",
        "funding_authority",
        "execution_authority",
        "activation_authority",
        "production_delivery_authority",
    ):
        if payload.get(key) is not False:
            blockers.append(f"{key} must be false")

    current_weight = num(payload.get("current_euna_weight_pct"))
    if not 5.0 <= current_weight <= 8.0:
        blockers.append("current EUNA weight is outside the governed role band")
    if num(payload.get("current_cash_weight_pct")) <= 25.0:
        blockers.append("cash is not above the no-add threshold")

    official = payload.get("official_fund_characteristics") if isinstance(payload.get("official_fund_characteristics"), dict) else {}
    if official.get("ucits") is not True:
        blockers.append("official UCITS evidence is missing")
    if num(official.get("effective_duration_years")) <= 0:
        blockers.append("official duration evidence is missing")
    if num(official.get("weighted_average_ytm_pct")) <= 0:
        blockers.append("official YTM evidence is missing")
    if num(official.get("standard_deviation_3y_pct")) <= 0:
        blockers.append("official volatility evidence is missing")

    observed = payload.get("euna_observed_metrics") if isinstance(payload.get("euna_observed_metrics"), dict) else {}
    if not -1.0 <= num(observed.get("correlation_with_risky_sleeve")) <= 1.0:
        blockers.append("invalid risky-sleeve correlation")
    if num(observed.get("annualized_volatility_pct")) <= 0:
        blockers.append("EUNA observed volatility is missing")
    if not 0.0 <= num(observed.get("positive_share_on_risky_down_days_pct")) <= 100.0:
        blockers.append("invalid positive-share metric")

    rows = payload.get("counterfactual_results") if isinstance(payload.get("counterfactual_results"), list) else []
    index = {
        str(row.get("scenario_id")): row
        for row in rows
        if isinstance(row, dict) and row.get("scenario_id")
    }
    if set(index) != EXPECTED_SCENARIOS:
        blockers.append("counterfactual scenario set mismatch")
    for scenario_id, row in index.items():
        if num(row.get("observation_count")) < 200:
            blockers.append(f"{scenario_id} has insufficient observations")
        if num(row.get("annualized_volatility_pct")) <= 0:
            blockers.append(f"{scenario_id} volatility is missing")
        if num(row.get("cash_weight_pct")) < 0:
            blockers.append(f"{scenario_id} cash is negative")
        total = num(row.get("cash_weight_pct")) + sum(num(value) for value in (row.get("composition_weights_pct") or {}).values())
        if abs(total - 100.0) > 0.01:
            blockers.append(f"{scenario_id} weights do not sum to 100")

    retained = index.get("policy_retained", {})
    cash_case = index.get("euna_to_cash", {})
    risky_case = index.get("euna_to_risky_pro_rata", {})
    if num(retained.get("annualized_volatility_pct")) < num(cash_case.get("annualized_volatility_pct")):
        blockers.append("review incorrectly suggests EUNA is lower risk than cash")
    if num(retained.get("annualized_volatility_pct")) >= num(risky_case.get("annualized_volatility_pct")):
        blockers.append("EUNA does not reduce volatility versus risky reallocation")
    if num(retained.get("maximum_drawdown_pct")) <= num(risky_case.get("maximum_drawdown_pct")):
        blockers.append("EUNA does not improve drawdown versus risky reallocation")

    classification = payload.get("classification") if isinstance(payload.get("classification"), dict) else {}
    if classification.get("crisis_hedge_pass") is not False:
        blockers.append("EUNA must not be labelled a reliable crisis hedge")
    if classification.get("low_volatility_diversifier_pass") is not True:
        blockers.append("EUNA must pass the low-volatility diversifier test")
    if classification.get("current_weight_within_role_band") is not True:
        blockers.append("current weight must be within the role band")
    if classification.get("cash_weight_above_addition_threshold") is not True:
        blockers.append("cash must block an EUNA addition")
    if classification.get("role") != "low_volatility_carry_diversifier_not_reliable_equity_hedge":
        blockers.append("EUNA role classification mismatch")

    decision = payload.get("decision") if isinstance(payload.get("decision"), dict) else {}
    if decision.get("stage_1") != "retain_capped_no_add":
        blockers.append("Stage-1 EUNA decision mismatch")
    if decision.get("stage_1_decision_valid") is not True:
        blockers.append("Stage-1 EUNA decision is not valid")
    if decision.get("stage_1_action") != "hold_current_position_no_add_no_sale":
        blockers.append("Stage-1 EUNA action mismatch")
    if decision.get("stage_2_funding_priority") != "third":
        blockers.append("EUNA Stage-2 funding priority mismatch")
    if decision.get("stage_2_automatic_sale") is not False:
        blockers.append("EUNA must not be sold automatically")

    return blockers


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate EUNA risk-budget review")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    payload = load(args.path)
    blockers = validate(payload)
    print(json.dumps({
        "artifact_type": "etf_eu_euna_risk_budget_review_validation",
        "valid": not blockers,
        "blockers": blockers,
        "decision": payload.get("decision"),
        "classification": payload.get("classification"),
    }, indent=2))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
