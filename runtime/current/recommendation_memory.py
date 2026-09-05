from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

FIELDNAMES = [
    "report_date", "run_id", "ticker", "isin", "shares", "current_weight_pct",
    "would_initiate_today", "would_initiate_today_detail", "would_initiate_at_current_weight",
    "would_initiate_at_current_weight_detail", "fresh_cash_implication", "fresh_cash_implication_detail",
    "fresh_cash_test", "reunderwriting_complete", "reunderwriting_status", "thesis_score", "thesis_assessment",
    "implementation_score", "implementation_assessment", "replaceable_status", "weeks_replaceable",
    "action_clock_status", "best_alternative", "replacement_close_status", "replacement_duel_status",
    "portfolio_contribution_eur", "unrealized_pnl_pct", "contribution_quality", "factor_overlap_level",
    "factor_overlap_flag", "hedge_validity_status", "cash_policy_flag", "override_reason", "next_review_trigger",
    "maximum_review_window_runs", "required_next_action", "current_allocation_decision", "action_executed_this_run",
    "source_run_id", "source_authority",
]


def _ticker(row: dict[str, Any]) -> str:
    value = str(row.get("exchange_ticker") or row.get("ticker") or "").strip().upper()
    return "L0CK" if value == "LOCK" else value


def write_recommendation_observation(state: dict[str, Any], path: Path, report_date: str, run_id: str) -> None:
    existing: list[dict[str, str]] = []
    if path.exists():
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if list(reader.fieldnames or []) != FIELDNAMES:
                raise RuntimeError("Recommendation history schema drift; explicit migration required")
            existing = list(reader)
    existing = [row for row in existing if not (row.get("report_date") == report_date and row.get("run_id") == run_id)]
    cash_policy = state.get("cash_policy") if isinstance(state.get("cash_policy"), dict) else {}
    cash_flag = "Material cash position; deploy-or-explain review applied" if cash_policy.get("material_position") else "Cash not material"
    for row in state.get("portfolio", {}).get("positions") or []:
        if not isinstance(row, dict):
            continue
        existing.append({
            "report_date": report_date,
            "run_id": run_id,
            "ticker": _ticker(row),
            "isin": row.get("isin"),
            "shares": row.get("shares"),
            "current_weight_pct": row.get("current_weight_pct"),
            "would_initiate_today": row.get("would_initiate_today"),
            "would_initiate_today_detail": row.get("would_initiate_today"),
            "would_initiate_at_current_weight": row.get("would_initiate_at_current_weight"),
            "would_initiate_at_current_weight_detail": row.get("would_initiate_at_current_weight"),
            "fresh_cash_implication": row.get("fresh_cash_implication"),
            "fresh_cash_implication_detail": row.get("fresh_cash_implication"),
            "fresh_cash_test": row.get("fresh_cash_test"),
            "reunderwriting_complete": str(row.get("reunderwriting_complete") is True),
            "reunderwriting_status": row.get("reunderwriting_status"),
            "thesis_score": row.get("thesis_score"),
            "thesis_assessment": row.get("thesis_assessment"),
            "implementation_score": row.get("implementation_score"),
            "implementation_assessment": row.get("implementation_assessment"),
            "replaceable_status": row.get("replaceable_status") or "No",
            "weeks_replaceable": row.get("weeks_replaceable") or 0,
            "action_clock_status": row.get("action_clock_status") or "MONITOR_CURRENT_DECISION",
            "best_alternative": row.get("best_alternative"),
            "replacement_close_status": row.get("replacement_close_status"),
            "replacement_duel_status": row.get("replacement_duel_status"),
            "portfolio_contribution_eur": row.get("portfolio_contribution_eur"),
            "unrealized_pnl_pct": row.get("unrealized_pnl_pct"),
            "contribution_quality": row.get("contribution_quality") or "Current mark-to-entry contribution only",
            "factor_overlap_level": row.get("factor_overlap_level"),
            "factor_overlap_flag": row.get("factor_overlap_flag"),
            "hedge_validity_status": row.get("hedge_validity_status"),
            "cash_policy_flag": cash_flag,
            "override_reason": row.get("override_reason"),
            "next_review_trigger": row.get("next_review_trigger"),
            "maximum_review_window_runs": row.get("maximum_review_window_runs") or 1,
            "required_next_action": row.get("required_next_action"),
            "current_allocation_decision": row.get("current_allocation_decision"),
            "action_executed_this_run": "No model trade — review decision only",
            "source_run_id": run_id,
            "source_authority": row.get("source_authority"),
        })
    existing.sort(key=lambda row: (row.get("report_date") or "", row.get("run_id") or "", row.get("ticker") or ""))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(existing)
