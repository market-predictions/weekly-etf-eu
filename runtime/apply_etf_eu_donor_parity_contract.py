from __future__ import annotations

import csv
from datetime import date
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
LEGACY_TARGET_FIELDS = (
    "strategic_target_weight_pct",
    "phase_target_weight_pct",
    "target_weight_pct",
)
FRESH_CASH_ACTIONS = {"Add", "Hold", "Reduce", "Replace", "Close", "Watch one more week"}
YES_NO_SMALLER = {"Yes", "No", "Smaller"}
YES_NO = {"Yes", "No"}


def _num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _ticker(row: dict[str, Any]) -> str:
    ticker = str(row.get("ticker") or row.get("exchange_ticker") or "").strip().upper()
    return "L0CK" if ticker == "LOCK" else ticker


def _parse_date(value: Any) -> date | None:
    try:
        return date.fromisoformat(str(value or "")[:10])
    except ValueError:
        return None


def _clean_choice(value: Any, allowed: set[str], unresolved: str = "Unresolved") -> str:
    raw = str(value or "").strip()
    return raw if raw in allowed else unresolved


def _sanitize_position(row: dict[str, Any]) -> dict[str, Any]:
    clean = dict(row)
    historical: dict[str, Any] = {}
    for field in LEGACY_TARGET_FIELDS:
        if field in clean:
            historical[field] = clean.pop(field)
    if historical:
        clean["historical_allocation_metadata"] = historical
        clean["historical_allocation_metadata_authority"] = "non_current_cap01_or_transition_context"
    clean["current_allocation_target_authority"] = "none_without_explicit_current_allocation_decision"
    return clean


def _position_decision_memory(row: dict[str, Any], cash_material: bool) -> dict[str, Any]:
    would_today = _clean_choice(row.get("would_initiate_today"), YES_NO_SMALLER)
    would_weight = _clean_choice(row.get("would_initiate_at_current_weight"), YES_NO)
    implication = _clean_choice(row.get("fresh_cash_implication"), FRESH_CASH_ACTIONS, "Review required")
    thesis_score = row.get("thesis_score")
    implementation_score = row.get("implementation_score")
    complete = (
        would_today != "Unresolved"
        and would_weight != "Unresolved"
        and implication != "Review required"
        and thesis_score is not None
        and implementation_score is not None
    )

    replaceable = str(row.get("replaceable_status") or "Unresolved").strip()
    weeks = int(_num(row.get("weeks_replaceable")))
    pnl_pct = _num(row.get("unrealized_pnl_pct"))
    implementation_num = _num(implementation_score, default=99.0) if implementation_score is not None else None
    replaceable_true = replaceable.lower() in {"yes", "true", "replaceable", "hold but replaceable"}
    if replaceable_true and weeks >= 2:
        action_clock = "DIRECT_DECISION_REQUIRED"
    elif pnl_pct < -10.0 and implementation_num is not None and implementation_num < 4.0:
        action_clock = "REUNDERWRITING_REQUIRED"
    elif complete:
        action_clock = "MONITOR_CURRENT_DECISION"
    else:
        action_clock = "UNRESOLVED_REUNDERWRITING_REQUIRED"

    factor_level = str(row.get("factor_overlap_level") or row.get("factor_overlap_status") or "Unresolved").strip()
    hedge_status = str(row.get("hedge_validity_status") or "").strip()
    if not hedge_status:
        hedge_status = "Unresolved — role/ballast review required" if _ticker(row) == "EUNA" else "Not a designated hedge sleeve"

    required_action = str(row.get("required_next_action") or "").strip()
    if not required_action:
        required_action = (
            "Complete fresh-cash, thesis/implementation and alternative review before treating Hold as current authority"
            if not complete
            else "Apply current re-underwriting decision and monitor its next-review trigger"
        )

    return {
        "ticker": _ticker(row),
        "isin": row.get("isin"),
        "shares": int(_num(row.get("shares"))),
        "current_weight_pct": round(_num(row.get("current_weight_pct")), 6),
        "would_initiate_today": would_today,
        "would_initiate_at_current_weight": would_weight,
        "fresh_cash_implication": implication,
        "fresh_cash_test": row.get("fresh_cash_test") or "Current-run re-underwriting evidence required",
        "reunderwriting_complete": complete,
        "reunderwriting_status": "COMPLETE" if complete else "UNRESOLVED",
        "thesis_score": thesis_score,
        "implementation_score": implementation_score,
        "replaceable_status": replaceable,
        "weeks_replaceable": weeks,
        "action_clock_status": action_clock,
        "best_alternative": row.get("best_alternative"),
        "replacement_close_status": row.get("replacement_close_status") or "Unresolved",
        "replacement_duel_status": row.get("replacement_duel_status") or "Unresolved",
        "portfolio_contribution_eur": row.get("portfolio_contribution_eur"),
        "unrealized_pnl_pct": row.get("unrealized_pnl_pct"),
        "contribution_quality": row.get("contribution_quality") or "Review required",
        "factor_overlap_level": factor_level,
        "factor_overlap_flag": row.get("factor_overlap_flag") or ("Core-equity overlap review" if _ticker(row) in {"VWCE", "SXR8"} else ""),
        "hedge_validity_status": hedge_status,
        "cash_policy_flag": "Material cash position; classification and deploy-or-explain test required" if cash_material else "No material-cash flag",
        "override_reason": row.get("override_reason"),
        "next_review_trigger": row.get("next_review_trigger") or ("Complete unresolved re-underwriting" if not complete else "Current decision trigger"),
        "maximum_review_window_runs": row.get("maximum_review_window_runs"),
        "required_next_action": required_action,
        "source_authority": "current_protected_portfolio_plus_current_run_evidence",
    }


def apply_contract(state: dict[str, Any], macro_pack: dict[str, Any] | None = None) -> dict[str, Any]:
    result = dict(state)
    portfolio = dict(result.get("portfolio") or {})
    positions = [_sanitize_position(dict(row)) for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    portfolio["positions"] = positions
    result["portfolio"] = portfolio

    nav, cash = _num(portfolio.get("nav_eur")), _num(portfolio.get("cash_eur"))
    cash_weight = round(cash / nav * 100.0, 6) if nav else 0.0
    raw_cash_classification = str(
        portfolio.get("cash_classification")
        or result.get("cash_classification")
        or ""
    ).strip()
    allowed_cash_classes = {"Tactical reserve", "Uninvested residual", "Risk reserve", "Deployment candidate"}
    cash_classification = raw_cash_classification if raw_cash_classification in allowed_cash_classes else "Unresolved — explicit classification required"
    cash_classification_complete = cash_classification in allowed_cash_classes

    allocation_map: list[dict[str, Any]] = [{
        "segment_nl": "Cash",
        "segment_en": "Cash",
        "stance_nl": f"Actueel {cash_weight:.2f}% · geen vaste cashvloer",
        "stance_en": f"Current {cash_weight:.2f}% · no fixed cash floor",
        "note_nl": "Cash is een actieve positie. Boven 3% vereist een volledig fundable en actionable kans een expliciete deploy-or-explain review; boven 5% is cash materieel. Dit zijn reviewregels, geen vaste cashdoelen.",
        "note_en": "Cash is an active position. Above 3%, a fully fundable actionable opportunity requires an explicit deploy-or-explain review; above 5%, cash is material. These are review rules, not fixed cash targets.",
    }]
    for row in positions:
        ticker = _ticker(row)
        allocation_map.append({
            "segment_nl": row.get("portfolio_role") or ticker,
            "segment_en": row.get("portfolio_role") or ticker,
            "stance_nl": f"Actueel {_num(row.get('current_weight_pct')):.2f}% · {int(_num(row.get('shares')))} stuks",
            "stance_en": f"Current {_num(row.get('current_weight_pct')):.2f}% · {int(_num(row.get('shares')))} shares",
            "note_nl": "Huidige beschermde modelpositie. Extra inzet of reductie vereist actuele re-underwriting evidence en een afzonderlijk allocatiebesluit.",
            "note_en": "Current protected model position. Any add or reduction requires current re-underwriting evidence and a separate allocation decision.",
        })
    result["allocation_map"] = allocation_map

    memory = [_position_decision_memory(row, cash_weight > 5.0) for row in positions]
    result["recommendation_memory"] = memory
    unresolved_count = sum(1 for row in memory if row["reunderwriting_complete"] is not True)
    result["cash_policy"] = {
        "cash_eur": round(cash, 2),
        "cash_weight_pct": cash_weight,
        "cash_classification": cash_classification,
        "cash_classification_complete": cash_classification_complete,
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
        "legacy_target_fields_current_authority": False,
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

    if macro_pack:
        provenance = macro_pack.get("donor_provenance") if isinstance(macro_pack.get("donor_provenance"), dict) else {}
        source_date = _parse_date(provenance.get("source_report_date"))
        report_date = _parse_date(result.get("report_date") or macro_pack.get("report_date"))
        age_days = (report_date - source_date).days if source_date and report_date else None
        macro = dict(result.get("macro") or {})
        macro["source_report_date"] = provenance.get("source_report_date")
        macro["source_generated_at_utc"] = provenance.get("source_generated_at_utc")
        macro["age_days"] = age_days
        macro["fresh_for_report"] = age_days is not None and 0 <= age_days <= 3
        macro["freshness_status"] = "current" if macro["fresh_for_report"] else "historical_context_refresh_required"
        macro["freshness_authority"] = "donor_provenance.source_report_date"
        result["macro"] = macro

    result["donor_parity_contract"] = {
        "version": "v1.1",
        "fresh_cash_reunderwriting": True,
        "replacement_duel_memory": True,
        "action_clock_memory": True,
        "factor_overlap_review": True,
        "hedge_validity_review": True,
        "cash_policy_review": True,
        "donor_cash_thresholds_are_review_rules_not_allocation_caps": True,
        "donor_factor_40pct_is_concentration_disclosure_not_position_cap": True,
        "shadow_allocation_caps_are_current_authority": False,
        "legacy_allocation_target_metadata_current_authority": False,
        "portfolio_mutation": False,
        "execution_authority": False,
    }
    result["parity_completeness"] = {
        "funded_position_count": len(positions),
        "unresolved_reunderwriting_count": unresolved_count,
        "all_funded_positions_have_current_reunderwriting": unresolved_count == 0,
        "cash_classification": cash_classification,
        "cash_classification_complete": cash_classification_complete,
        "allocation_target_metadata_sanitized": all(
            all(field not in row for field in LEGACY_TARGET_FIELDS) for row in positions
        ),
        "historical_target_metadata_preserved_non_authoritatively": all(
            ("historical_allocation_metadata" in row) or not any(field in source for field in LEGACY_TARGET_FIELDS)
            for row, source in zip(positions, [dict(r) for r in (state.get("portfolio") or {}).get("positions") or [] if isinstance(r, dict)])
        ),
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
        raise RuntimeError(
            f"Recommendation memory does not match funded holdings: expected={sorted(required_tickers)} present={sorted(present)}"
        )
    fields = [
        "report_date", "run_id", "ticker", "isin", "shares", "current_weight_pct",
        "would_initiate_today", "would_initiate_at_current_weight", "fresh_cash_implication", "fresh_cash_test",
        "reunderwriting_complete", "reunderwriting_status", "thesis_score", "implementation_score",
        "replaceable_status", "weeks_replaceable", "action_clock_status", "best_alternative",
        "replacement_close_status", "replacement_duel_status", "portfolio_contribution_eur", "unrealized_pnl_pct",
        "contribution_quality", "factor_overlap_level", "factor_overlap_flag", "hedge_validity_status",
        "cash_policy_flag", "override_reason", "next_review_trigger", "maximum_review_window_runs",
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
