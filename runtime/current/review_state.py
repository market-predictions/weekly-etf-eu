from __future__ import annotations

import copy
import csv
import json
from pathlib import Path
from typing import Any

import yaml

SCHEMA_VERSION = "etf_eu_review_state_v1"
_ALLOWED_ACTIONS = {"ADD", "HOLD", "REDUCE", "REPLACE", "CLOSE", "REVIEW"}


def _num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _ticker(row: dict[str, Any]) -> str:
    value = str(row.get("exchange_ticker") or row.get("ticker") or "").strip().upper()
    return "L0CK" if value == "LOCK" else value


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected mapping in {path}")
    return payload


def _normalize_action(row: dict[str, Any]) -> str:
    raw = str(
        row.get("current_allocation_decision")
        or row.get("fresh_cash_implication")
        or row.get("last_action")
        or "REVIEW"
    ).strip().upper()
    aliases = {
        "INITIATE": "ADD",
        "BUY": "ADD",
        "TRIM": "REDUCE",
        "SELL": "CLOSE",
        "NO CHANGE": "HOLD",
    }
    action = aliases.get(raw, raw)
    return action if action in _ALLOWED_ACTIONS else "REVIEW"


def _position_decisions(state: dict[str, Any]) -> list[dict[str, Any]]:
    portfolio = state.get("portfolio") if isinstance(state.get("portfolio"), dict) else {}
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    decisions: list[dict[str, Any]] = []
    for row in positions:
        action = _normalize_action(row)
        unresolved: list[str] = []
        if not row.get("isin"):
            unresolved.append("missing_isin")
        if row.get("reunderwriting_complete") is not True:
            unresolved.append("current_reunderwriting_incomplete")
            action = "REVIEW"
        if not row.get("price_date"):
            unresolved.append("missing_price_date")
        confidence = "HIGH"
        verification = str(row.get("verification_status") or "").lower()
        if unresolved:
            confidence = "LOW"
        elif "unverified" in verification or "single" in verification:
            confidence = "MEDIUM"
        decisions.append(
            {
                "ticker": _ticker(row),
                "isin": row.get("isin"),
                "fund_name": row.get("fund_name"),
                "portfolio_role": row.get("portfolio_role"),
                "action": action,
                "shares": int(_num(row.get("shares"))),
                "value_eur": round(_num(row.get("market_value_eur")), 2),
                "weight_pct": round(_num(row.get("current_weight_pct")), 6),
                "fresh_cash_view": row.get("fresh_cash_implication") or "Review",
                "rationale": row.get("thesis_assessment") or row.get("required_next_action") or "Current review evidence unresolved.",
                "contribution_eur": round(_num(row.get("portfolio_contribution_eur", row.get("unrealized_pnl_eur"))), 2),
                "best_alternative": row.get("best_alternative") or "No current alternative established",
                "invalidation_or_next_trigger": row.get("next_review_trigger") or row.get("required_next_action") or "Next scheduled re-underwriting",
                "pricing_status": row.get("pricing_status"),
                "verification_status": row.get("verification_status"),
                "price_date": row.get("price_date"),
                "confidence": confidence,
                "unresolved": unresolved,
                "evidence": {
                    "source_run_id": row.get("source_run_id"),
                    "thesis_score": row.get("thesis_score"),
                    "implementation_score": row.get("implementation_score"),
                    "factor_overlap_level": row.get("factor_overlap_level"),
                },
            }
        )
    return decisions


def _accountability(
    state: dict[str, Any],
    *,
    comparator_config: dict[str, Any],
    accountability_history: Path,
    report_date: str,
) -> dict[str, Any]:
    portfolio = state.get("portfolio") if isinstance(state.get("portfolio"), dict) else {}
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    comparator = comparator_config.get("primary_comparator") or {}
    comparator_ticker = str(comparator.get("ticker") or "").upper()
    comparator_isin = str(comparator.get("isin") or "")
    comparator_row = next(
        (
            row
            for row in positions
            if _ticker(row) == comparator_ticker and str(row.get("isin") or "") == comparator_isin
        ),
        None,
    )
    if comparator_row is None:
        raise RuntimeError("Primary comparator exact identity is not present in current priced portfolio state")
    if str(comparator_row.get("price_date") or "") != report_date:
        raise RuntimeError("Primary comparator does not have an exact close on the report date")

    current_nav = _num(portfolio.get("nav_eur"))
    current_cash = _num(portfolio.get("cash_eur"))
    current_close = _num(comparator_row.get("current_price_local"))
    if current_nav <= 0 or current_close <= 0:
        raise RuntimeError("Accountability requires positive portfolio NAV and comparator close")

    history = _read_csv(accountability_history)
    prior = None
    for row in history:
        if str(row.get("date") or "") < report_date:
            prior = row
    if prior is None:
        return {
            "status": "BASELINE_REQUIRED",
            "comparator_id": comparator.get("comparator_id"),
            "comparator_ticker": comparator_ticker,
            "comparator_isin": comparator_isin,
            "current_comparator_close_eur": round(current_close, 8),
            "portfolio_nav_eur": round(current_nav, 2),
            "cash_eur": round(current_cash, 2),
            "cash_weight_pct": round(100.0 * current_cash / current_nav, 6),
            "period_return_supported": False,
            "unresolved": ["no_prior_accountability_baseline"],
        }

    prior_nav = _num(prior.get("portfolio_nav_eur"))
    prior_close = _num(prior.get("comparator_close_eur"))
    prior_index = _num(prior.get("comparator_index"), 100.0)
    if prior_nav <= 0 or prior_close <= 0 or prior_index <= 0:
        raise RuntimeError("Prior accountability baseline is invalid")

    portfolio_return = (current_nav / prior_nav - 1.0) * 100.0
    comparator_return = (current_close / prior_close - 1.0) * 100.0
    active_return = portfolio_return - comparator_return
    comparator_index = prior_index * (current_close / prior_close)

    historical_navs = [_num(row.get("portfolio_nav_eur")) for row in history if _num(row.get("portfolio_nav_eur")) > 0]
    portfolio_peak = max(historical_navs + [current_nav])
    portfolio_drawdown = (current_nav / portfolio_peak - 1.0) * 100.0 if portfolio_peak else 0.0
    historical_indices = [_num(row.get("comparator_index")) for row in history if _num(row.get("comparator_index")) > 0]
    comparator_peak = max(historical_indices + [comparator_index])
    comparator_drawdown = (comparator_index / comparator_peak - 1.0) * 100.0 if comparator_peak else 0.0

    contributions = sorted(
        (
            {
                "ticker": _ticker(row),
                "contribution_eur": round(_num(row.get("portfolio_contribution_eur", row.get("unrealized_pnl_eur"))), 2),
            }
            for row in positions
        ),
        key=lambda item: item["contribution_eur"],
    )
    top_detractor = contributions[0] if contributions else None
    top_contributor = contributions[-1] if contributions else None

    cash_weight = 100.0 * current_cash / current_nav
    cash_policy = state.get("cash_policy") if isinstance(state.get("cash_policy"), dict) else {}
    cash_explained = cash_policy.get("cash_after_explanation") or (
        state.get("current_reunderwriting") or {}
    ).get("cash_after_explanation")

    return {
        "status": "COMPLETE",
        "baseline_date": prior.get("date"),
        "report_date": report_date,
        "comparator_id": comparator.get("comparator_id"),
        "comparator_ticker": comparator_ticker,
        "comparator_isin": comparator_isin,
        "comparator_purpose": comparator.get("purpose"),
        "portfolio_nav_eur": round(current_nav, 2),
        "portfolio_period_return_pct": round(portfolio_return, 6),
        "portfolio_drawdown_pct": round(portfolio_drawdown, 6),
        "comparator_close_eur": round(current_close, 8),
        "comparator_period_return_pct": round(comparator_return, 6),
        "comparator_index": round(comparator_index, 6),
        "comparator_drawdown_pct": round(comparator_drawdown, 6),
        "active_return_pp": round(active_return, 6),
        "cash_eur": round(current_cash, 2),
        "cash_weight_pct": round(cash_weight, 6),
        "cash_drag_eur": None,
        "cash_drag_status": "UNAVAILABLE_NOT_ESTIMATED",
        "cash_rationale": cash_explained or "Cash rationale unresolved",
        "top_contributor": top_contributor,
        "top_detractor": top_detractor,
        "position_contributions": contributions,
        "costs_status": "UNAVAILABLE_NOT_INVENTED",
        "unresolved": ["cash_drag_not_yet_evidenced", "transaction_costs_not_evidenced"],
    }


def build_review_state(
    normalized_state: dict[str, Any],
    *,
    comparator_config_path: Path,
    accountability_history_path: Path,
    report_date: str,
    run_id: str,
    pricing_artifact: str,
    donor_lane_artifact: str | None = None,
    macro_pack: str | None = None,
) -> dict[str, Any]:
    state = copy.deepcopy(normalized_state)
    portfolio = state.get("portfolio") if isinstance(state.get("portfolio"), dict) else {}
    decisions = _position_decisions(state)
    comparator_config = _load_yaml(comparator_config_path)
    accountability = _accountability(
        state,
        comparator_config=comparator_config,
        accountability_history=accountability_history_path,
        report_date=report_date,
    )

    blockers: list[str] = []
    if state.get("state_valid") is not True:
        blockers.append("normalized_input_state_invalid")
    if not decisions:
        blockers.append("no_funded_position_decisions")
    blockers.extend(
        f"position_unresolved:{row['ticker']}:{','.join(row['unresolved'])}"
        for row in decisions
        if row.get("unresolved")
    )
    if accountability.get("status") != "COMPLETE":
        blockers.append("accountability_incomplete")

    actions = [row["action"] for row in decisions]
    if all(action == "HOLD" for action in actions):
        weekly_action = "HOLD_ALL_FUNDED_POSITIONS"
    else:
        weekly_action = ", ".join(f"{row['ticker']} {row['action']}" for row in decisions if row["action"] != "HOLD") or "REVIEW"

    bridge = state.get("donor_discovery_bridge") if isinstance(state.get("donor_discovery_bridge"), dict) else {}
    candidates = []
    for row in bridge.get("rows") or bridge.get("candidates") or []:
        if not isinstance(row, dict):
            continue
        candidates.append(
            {
                "ticker": row.get("ticker") or row.get("eu_ticker") or row.get("mapped_ticker"),
                "lane": row.get("taxonomy_tag") or row.get("lane"),
                "status": row.get("fundability_status") or row.get("status"),
                "funding_authority": False,
            }
        )

    unresolved_claims = sorted(set(accountability.get("unresolved") or []))
    for row in decisions:
        unresolved_claims.extend(f"{row['ticker']}:{item}" for item in row.get("unresolved") or [])

    review_state = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "weekly_etf_eu_review_state",
        "run_id": run_id,
        "report_date": report_date,
        "completed_close_date": report_date,
        "semantic_state_frozen": True,
        "semantic_mutation_allowed_downstream": False,
        "state_valid": not blockers,
        "blockers": blockers,
        "authority": {
            "funding_authority": False,
            "portfolio_mutation": False,
            "trade_ledger_write": False,
            "real_broker_execution": False,
            "delivery_authority": False,
            "client_text_creates_state_authority": False,
        },
        "sources": {
            "normalized_state_schema": state.get("schema_version"),
            "protected_portfolio_state": (state.get("sources") or {}).get("protected_portfolio_state"),
            "pricing_artifact": pricing_artifact,
            "comparator_contract": str(comparator_config_path),
            "accountability_history": str(accountability_history_path),
            "donor_lane_artifact": donor_lane_artifact,
            "macro_pack": macro_pack,
        },
        "portfolio": {
            "nav_eur": round(_num(portfolio.get("nav_eur")), 2),
            "cash_eur": round(_num(portfolio.get("cash_eur")), 2),
            "invested_market_value_eur": round(_num(portfolio.get("invested_market_value_eur")), 2),
            "position_count": len(decisions),
        },
        "weekly_decision": {
            "action": weekly_action,
            "model_portfolio_mutation": False,
            "allocation_decision_present": all(row["action"] != "REVIEW" for row in decisions),
            "cash_rationale": accountability.get("cash_rationale"),
        },
        "accountability": accountability,
        "funded_position_decisions": decisions,
        "challengers": candidates,
        "macro_context": state.get("macro") or state.get("macro_context"),
        "pricing_contract": state.get("pricing_contract") or state.get("pricing"),
        "epistemics": {
            "claim_provenance_present": True,
            "confidence_scale": ["HIGH", "MEDIUM", "LOW"],
            "unresolved": sorted(set(unresolved_claims)),
            "missing_evidence_is_explicit": True,
            "no_silent_interpolation": True,
        },
    }
    return review_state


def write_accountability_observation(review_state: dict[str, Any], path: Path) -> None:
    accountability = review_state.get("accountability") or {}
    if accountability.get("status") != "COMPLETE":
        raise RuntimeError("Cannot persist incomplete accountability observation")
    fieldnames = [
        "date", "portfolio_nav_eur", "portfolio_period_return_pct", "portfolio_drawdown_pct",
        "comparator_id", "comparator_close_eur", "comparator_index", "comparator_period_return_pct",
        "comparator_drawdown_pct", "active_return_pp", "cash_eur", "cash_weight_pct",
        "source_portfolio", "source_comparator", "record_status",
    ]
    rows = _read_csv(path)
    rows = [row for row in rows if row.get("date") != review_state.get("report_date")]
    rows.append(
        {
            "date": review_state["report_date"],
            "portfolio_nav_eur": f"{_num(accountability.get('portfolio_nav_eur')):.2f}",
            "portfolio_period_return_pct": f"{_num(accountability.get('portfolio_period_return_pct')):.6f}",
            "portfolio_drawdown_pct": f"{_num(accountability.get('portfolio_drawdown_pct')):.6f}",
            "comparator_id": accountability.get("comparator_id"),
            "comparator_close_eur": f"{_num(accountability.get('comparator_close_eur')):.8f}",
            "comparator_index": f"{_num(accountability.get('comparator_index')):.6f}",
            "comparator_period_return_pct": f"{_num(accountability.get('comparator_period_return_pct')):.6f}",
            "comparator_drawdown_pct": f"{_num(accountability.get('comparator_drawdown_pct')):.6f}",
            "active_return_pp": f"{_num(accountability.get('active_return_pp')):.6f}",
            "cash_eur": f"{_num(accountability.get('cash_eur')):.2f}",
            "cash_weight_pct": f"{_num(accountability.get('cash_weight_pct')):.6f}",
            "source_portfolio": review_state.get("sources", {}).get("protected_portfolio_state") or "normalized_review_state",
            "source_comparator": review_state.get("sources", {}).get("pricing_artifact"),
            "record_status": "CURRENT_REVIEW_OBSERVATION",
        }
    )
    rows.sort(key=lambda row: row.get("date") or "")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def dump_review_state(review_state: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(review_state, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
