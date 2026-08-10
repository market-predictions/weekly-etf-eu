from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

RETIRED_RULES = {
    "maximum_position_pct": 50.0,
    "minimum_cash_pct": 35.0,
    "maximum_new_etf_pct": 15.0,
}
RESEARCH_ONLY_RULES = {
    "maximum_gross_turnover_pct_nav": 25.0,
    "ai_compute_semiconductor_cap_pct_nav": 18.0,
}


def _num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _ticker(row: dict[str, Any]) -> str:
    ticker = str(row.get("ticker") or row.get("exchange_ticker") or "").strip().upper()
    return "L0CK" if ticker == "LOCK" else ticker


def _position_decision_memory(row: dict[str, Any], cash_material: bool) -> dict[str, Any]:
    action = str(row.get("suggested_action") or row.get("last_action") or "hold").strip().lower()
    if action in {"buy", "add", "add_from_cash"}:
        initiate = "Yes"
    elif action in {"reduce", "close", "replace", "replace_full"}:
        initiate = "No"
    else:
        initiate = "Unresolved"
    return {
        "ticker": _ticker(row),
        "isin": row.get("isin"),
        "shares": int(_num(row.get("shares"))),
        "current_weight_pct": round(_num(row.get("current_weight_pct")), 6),
        "would_initiate_today": row.get("would_initiate_today") or initiate,
        "would_initiate_at_current_weight": row.get("would_initiate_at_current_weight") or "Unresolved",
        "fresh_cash_test": row.get("fresh_cash_test") or "Re-underwrite from current evidence",
        "thesis_score": row.get("thesis_score"),
        "implementation_score": row.get("implementation_score"),
        "replaceable_status": row.get("replaceable_status") or "Unresolved",
        "weeks_replaceable": int(_num(row.get("weeks_replaceable"))),
        "best_alternative": row.get("best_alternative"),
        "replacement_duel_status": row.get("replacement_duel_status") or "Unresolved",
        "contribution_quality": row.get("contribution_quality") or "Review required",
        "factor_overlap_flag": row.get("factor_overlap_flag") or ("Core-equity overlap review" if _ticker(row) in {"VWCE", "SXR8"} else ""),
        "hedge_validity_status": row.get("hedge_validity_status") or ("Role review required" if _ticker(row) == "EUNA" else "Not hedge sleeve"),
        "cash_policy_flag": "Material cash requires deploy-or-explain review" if cash_material else "No material cash flag",
        "required_next_action": row.get("required_next_action") or "Re-underwrite role, current weight and best alternative on current evidence",
        "source_authority": "current_protected_portfolio_plus_current_run_evidence",
    }


def apply_contract(state: dict[str, Any]) -> dict[str, Any]:
    """Normalize generated EU report state against current donor-parity authority."""
    result = dict(state)
    portfolio = dict(result.get("portfolio") or {})
    positions = [dict(row) for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    nav = _num(portfolio.get("nav_eur"))
    cash = _num(portfolio.get("cash_eur"))
    cash_weight = round(cash / nav * 100.0, 6) if nav else 0.0

    allocation_map: list[dict[str, Any]] = [{
        "segment_nl": "Cash",
        "segment_en": "Cash",
        "stance_nl": f"Actueel {cash_weight:.2f}% · geen vaste cashvloer",
        "stance_en": f"Current {cash_weight:.2f}% · no fixed cash floor",
        "note_nl": "Cash is een actieve positie. Bij volledig fundable kansen vereist materiële cash een deploy-or-explain besluit; dit is geen automatische handelsopdracht.",
        "note_en": "Cash is an active position. When fully fundable opportunities exist, material cash requires a deploy-or-explain decision; this is not an automatic trade instruction.",
    }]
    for row in positions:
        ticker = _ticker(row)
        allocation_map.append({
            "segment_nl": row.get("portfolio_role") or ticker,
            "segment_en": row.get("portfolio_role") or ticker,
            "stance_nl": f"Actueel {_num(row.get('current_weight_pct')):.2f}% · {int(_num(row.get('shares')))} stuks",
            "stance_en": f"Current {_num(row.get('current_weight_pct')):.2f}% · {int(_num(row.get('shares')))} shares",
            "note_nl": "Huidige beschermde modelpositie. Extra inzet of reductie vereist actuele evidence en een afzonderlijk allocatiebesluit.",
            "note_en": "Current protected model position. Any add or reduction requires current evidence and a separate allocation decision.",
        })
    result["allocation_map"] = allocation_map

    cash_material = cash_weight > 5.0
    result["recommendation_memory"] = [_position_decision_memory(row, cash_material) for row in positions]
    result["cash_policy"] = {
        "cash_eur": round(cash, 2),
        "cash_weight_pct": cash_weight,
        "material_position": cash_weight > 5.0,
        "deploy_or_explain_review_required_if_actionable_fundable_lane_exists": cash_weight > 3.0,
        "fixed_minimum_cash_pct": None,
        "automatic_trade_authority": False,
    }

    authority = dict(result.get("authority") or {})
    authority.update({
        "allocation_authority_contract": "control/ETF_EU_ALLOCATION_AUTHORITY_V1.md",
        "retired_shadow_rules": RETIRED_RULES,
        "research_only_transition_values": RESEARCH_ONLY_RULES,
        "retired_shadow_rules_executable": False,
        "research_only_transition_values_executable": False,
        "embedded_exposure_semantics": "measured_lower_bound_descriptive_not_required_minimum",
        "broker_specific_permission_required_for_model": False,
        "broker_permission_required_for_real_execution": True,
        "portfolio_mutation": False,
        "trade_ledger_mutation": False,
        "real_broker_execution": False,
        "production_delivery_authority": False,
    })
    result["authority"] = authority

    funnel = dict(result.get("verification_funnel") or {})
    funnel.pop("minimum_cash_pct", None)
    funnel.pop("maximum_new_etf_pct", None)
    funnel["model_investability_requires_broker_permission"] = False
    funnel["real_execution_may_require_broker_permission"] = True
    result["verification_funnel"] = funnel

    result["donor_parity_contract"] = {
        "version": "v1",
        "fresh_cash_reunderwriting": True,
        "replacement_duel_memory": True,
        "action_clock_memory": True,
        "factor_overlap_review": True,
        "cash_policy_review": True,
        "shadow_allocation_caps_are_current_authority": False,
        "portfolio_mutation": False,
        "execution_authority": False,
    }
    return result


def write_recommendation_scorecard(state: dict[str, Any], path: Path, report_date: str, run_id: str) -> None:
    rows = list(state.get("recommendation_memory") or [])
    required_tickers = {
        _ticker(row)
        for row in (state.get("portfolio") or {}).get("positions") or []
        if isinstance(row, dict) and _ticker(row)
    }
    present = {str(row.get("ticker") or "").upper() for row in rows}
    if present != required_tickers:
        raise RuntimeError(f"Recommendation memory does not match funded holdings: expected={sorted(required_tickers)} present={sorted(present)}")
    fields = [
        "report_date", "run_id", "ticker", "isin", "shares", "current_weight_pct",
        "would_initiate_today", "would_initiate_at_current_weight", "fresh_cash_test",
        "thesis_score", "implementation_score", "replaceable_status", "weeks_replaceable",
        "best_alternative", "replacement_duel_status", "contribution_quality",
        "factor_overlap_flag", "hedge_validity_status", "cash_policy_flag",
        "required_next_action", "source_authority",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            payload = {field: row.get(field) for field in fields}
            payload["report_date"] = report_date
            payload["run_id"] = run_id
            writer.writerow(payload)
