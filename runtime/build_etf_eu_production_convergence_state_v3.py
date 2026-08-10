from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from runtime import build_etf_eu_production_convergence_state_v2 as v2


HISTORICAL_STAGE1_BLOCKERS = {
    "stage_1_candidate_not_allowlisted",
    "liquidity_below_threshold",
}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _current_blockers(values: list[Any]) -> list[str]:
    return sorted({
        _text(value)
        for value in values
        if _text(value) and _text(value) not in HISTORICAL_STAGE1_BLOCKERS
    })


def _filter_client_blockers(values: list[Any], lang: str) -> list[str]:
    result: list[str] = []
    for value in values:
        text = _text(value)
        folded = text.casefold()
        historical = (
            "stage 1" in folded
            or "fase 1" in folded
            or "allowlist" in folded
            or "policy threshold" in folded
            or "beleidsdrempel" in folded
        )
        if not historical and text:
            result.append(text)
    return result


def _converge_promoted_exposures(state: dict[str, Any]) -> None:
    rows = [row for row in state.get("promoted_exposures") or [] if isinstance(row, dict)]
    for row in rows:
        original = list(row.get("blockers") or [])
        row["historical_transition_blockers"] = original
        row["blockers"] = _current_blockers(original)
        row["blockers_nl"] = _filter_client_blockers(list(row.get("blockers_nl") or []), "nl")
        row["blockers_en"] = _filter_client_blockers(list(row.get("blockers_en") or []), "en")
        row["historical_stage1_candidate_gate_authority"] = False
        row["historical_liquidity_threshold_authority"] = False
        row["current_reunderwriting_required"] = True
        row["allocation_authority"] = False
        row["portfolio_mutation"] = False
        if row["blockers"]:
            row["implementation_status"] = "mapped_pending_current_evidence_and_reunderwriting"
            row["client_action"] = "monitor_pending_current_evidence"
        elif float(row.get("current_eu_weight_pct") or 0.0) > 0:
            row["implementation_status"] = "funded_current_position_reunderwriting_required"
            row["client_action"] = "hold_current_position_pending_reunderwriting"
        else:
            row["implementation_status"] = "mapped_current_reunderwriting_required"
            row["client_action"] = "review_not_auto_fundable"


def _mark_historical_allocator(state: dict[str, Any]) -> None:
    allocator = state.get("allocator") if isinstance(state.get("allocator"), dict) else {}
    allocator.update({
        "historical_transition_scenario": True,
        "current_allocation_authority": False,
        "current_funding_authority": False,
        "client_control_authority": False,
        "real_execution_authority": False,
        "authority_contract": "control/ETF_EU_ALLOCATION_AUTHORITY_CONVERGENCE_V1.md",
        "preferred_variant_scope": "historical_shadow_comparison_only",
    })
    state["allocator"] = allocator

    reconciliation = state.get("current_evidence_reconciliation")
    if isinstance(reconciliation, dict):
        reconciliation["historical_stage1_evidence_only"] = True
        reconciliation["current_candidate_gate_authority"] = False
        reconciliation["current_allocation_authority"] = False

    stage = state.get("stage_1_decision")
    if isinstance(stage, dict):
        stage["historical_activation_provenance"] = True
        stage["current_candidate_gate_authority"] = False
        stage["current_allocation_authority"] = False
        stage["current_funding_authority"] = False
        stage["current_client_control_authority"] = False


def _install_current_authority(state: dict[str, Any]) -> None:
    promoted = [row for row in state.get("promoted_exposures") or [] if isinstance(row, dict)]
    official = state.get("official_portfolio") if isinstance(state.get("official_portfolio"), dict) else {}
    cash = float(official.get("cash_eur") or 0.0)
    nav = float(official.get("nav_eur") or 0.0)
    cash_pct = round(cash / nav * 100.0, 6) if nav else None
    state["current_allocation_authority"] = {
        "schema_version": "etf_eu_current_allocation_authority_v1",
        "authority_contract": "control/ETF_EU_ALLOCATION_AUTHORITY_CONVERGENCE_V1.md",
        "authority_order": [
            "explicit_current_allocation_decision",
            "protected_portfolio_state_and_trade_ledger",
            "current_completed_close_and_exact_line_identity",
            "current_reunderwriting_overlap_and_fundability_evidence",
            "current_donor_opportunity_state_after_eu_mapping",
            "historical_strategy_and_shadow_scenarios",
        ],
        "retired_or_non_authoritative_fixed_rules": {
            "minimum_cash_35_pct": False,
            "maximum_new_position_15_pct": False,
            "cash_first_50_pct": False,
            "turnover_25_pct": False,
            "semiconductor_cap_18_pct": False,
            "historical_position_limit": False,
            "pricing_coverage_75_as_position_cap": False,
        },
        "historical_stage1_candidate_gate_applied": False,
        "candidate_review_scope": "all_currently_promoted_mapped_exposures",
        "candidate_review_count": len(promoted),
        "cash_eur": round(cash, 2),
        "cash_weight_pct": cash_pct,
        "cash_discipline": "deploy_or_explain_against_current_fundable_opportunities_no_fixed_minimum",
        "broker_specific_permission_required_for_model": False,
        "broker_permission_required_for_real_execution": True,
        "embedded_exposure_semantics": "measured_lower_bound_not_target_or_control",
        "portfolio_mutation": False,
        "funding_authority": False,
        "real_broker_execution": False,
    }
    state.setdefault("authority", {}).update({
        "allocation_authority_contract": "control/ETF_EU_ALLOCATION_AUTHORITY_CONVERGENCE_V1.md",
        "shadow_policy_used_for_current_allocation": False,
        "retired_fixed_percentage_used_for_current_allocation": False,
        "historical_stage1_used_as_current_candidate_gate": False,
        "historical_target_used_for_current_trade": False,
        "broker_specific_permission_required_for_model": False,
    })
    state.setdefault("validation", {}).update({
        "shadow_policy_used_for_current_allocation": False,
        "retired_fixed_percentage_used": False,
        "historical_stage1_candidate_gate_applied": False,
        "current_candidate_review_count": len(promoted),
    })


def build(args: argparse.Namespace) -> dict[str, Any]:
    state = v2.build(args)
    _mark_historical_allocator(state)
    _converge_promoted_exposures(state)
    _install_current_authority(state)
    state["schema_version"] = "etf_eu_production_convergence_state_v3_donor_convergence"
    state["client_contract"] = dict(state.get("client_contract") or {})
    state["client_contract"].update({
        "historical_transition_allocator_client_authority": False,
        "current_allocation_authority_surface": "run_scoped_decision_plus_protected_state",
        "embedded_semiconductor_semantics": "measured_lower_bound_not_minimum_target",
    })
    return state


def main() -> None:
    parser = argparse.ArgumentParser(description="Build ETF EU convergence state with current allocation authority separated from historical Stage-1 shadow evidence")
    parser.add_argument("--sync-shadow", type=Path, required=True)
    parser.add_argument("--allocator", type=Path, required=True)
    parser.add_argument("--wp09-receipt", type=Path, required=True)
    parser.add_argument("--portfolio-state", type=Path, default=Path("output/etf_eu_portfolio_state.json"))
    parser.add_argument("--trade-ledger", type=Path, default=Path("output/etf_eu_trade_ledger.csv"))
    parser.add_argument("--donor-commit", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    state = build(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        "ETF_EU_CURRENT_ALLOCATION_AUTHORITY_V1_OK"
        f" | candidates={state['current_allocation_authority']['candidate_review_count']}"
        " | historical_stage1_gate=false | shadow_fixed_caps=false | portfolio_mutation=false"
    )


if __name__ == "__main__":
    main()
