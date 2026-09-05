from __future__ import annotations

import copy
import csv
import json
from pathlib import Path
from typing import Any

import yaml

from runtime.current.pricing import find_exact_price_row, load_pricing_artifact, pricing_authority_summary

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


def _action(row: dict[str, Any]) -> str:
    raw = str(row.get("current_allocation_decision") or row.get("last_action") or "REVIEW").strip().upper()
    action = {"INITIATE": "ADD", "BUY": "ADD", "TRIM": "REDUCE", "SELL": "CLOSE", "NO CHANGE": "HOLD"}.get(raw, raw)
    return action if action in _ALLOWED_ACTIONS else "REVIEW"


def _position_decisions(state: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in (state.get("portfolio") or {}).get("positions") or []:
        if not isinstance(row, dict):
            continue
        unresolved: list[str] = []
        action = _action(row)
        if not row.get("isin"):
            unresolved.append("missing_isin")
        if row.get("identity_binding_valid") is not True:
            unresolved.append("identity_binding_invalid")
        if row.get("reunderwriting_complete") is not True:
            unresolved.append("current_reunderwriting_incomplete")
            action = "REVIEW"
        if not row.get("price_date"):
            unresolved.append("missing_price_date")
        verification = str(row.get("verification_status") or "").lower()
        confidence = "LOW" if unresolved else ("MEDIUM" if "primary_only" in verification or "not_recorded" in verification else "HIGH")
        rows.append({
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
            "contribution_eur": None,
            "best_alternative": row.get("best_alternative") or "No current alternative established",
            "invalidation_or_next_trigger": row.get("next_review_trigger") or row.get("required_next_action") or "Next scheduled re-underwriting",
            "pricing_status": row.get("pricing_status"),
            "verification_status": row.get("verification_status"),
            "price_date": row.get("price_date"),
            "confidence": confidence,
            "unresolved": unresolved,
            "evidence": {
                "pricing_source": row.get("pricing_source"),
                "pricing_source_quality": row.get("pricing_source_quality"),
                "agreeing_providers": row.get("pricing_agreeing_providers"),
                "source_run_id": row.get("source_run_id"),
                "memory_report_date": row.get("reunderwriting_memory_report_date"),
                "thesis_score": row.get("thesis_score"),
                "implementation_score": row.get("implementation_score"),
                "factor_overlap_level": row.get("factor_overlap_level"),
            },
        })
    return rows


def _period_position_contributions(state: dict[str, Any], *, prior_nav: float, baseline_date: str) -> tuple[list[dict[str, Any]], list[str]]:
    contributions: list[dict[str, Any]] = []
    unresolved: list[str] = []
    for row in (state.get("portfolio") or {}).get("positions") or []:
        if not isinstance(row, dict):
            continue
        ticker = _ticker(row)
        prior_date = str(row.get("reunderwriting_memory_report_date") or "")
        prior_shares = _num(row.get("reunderwriting_memory_shares"), -1.0)
        prior_weight = _num(row.get("reunderwriting_memory_weight_pct"), -1.0)
        current_shares = _num(row.get("shares"), -1.0)
        current_value = _num(row.get("market_value_eur"), -1.0)
        if prior_date != baseline_date:
            unresolved.append(f"position_prior_observation_date_mismatch:{ticker}")
            continue
        if min(prior_shares, prior_weight, current_shares, current_value) < 0:
            unresolved.append(f"position_prior_observation_missing:{ticker}")
            continue
        if abs(current_shares - prior_shares) > 1e-9:
            unresolved.append(f"position_flow_not_evidenced:{ticker}")
            continue
        prior_value = prior_nav * prior_weight / 100.0
        contributions.append({"ticker": ticker, "contribution_eur": round(current_value - prior_value, 2)})
    contributions.sort(key=lambda item: item["contribution_eur"])
    return contributions, unresolved


def _accountability(state: dict[str, Any], *, comparator: dict[str, Any], history_path: Path, pricing_path: Path, report_date: str) -> dict[str, Any]:
    portfolio = state.get("portfolio") or {}
    pricing = load_pricing_artifact(pricing_path)
    price = find_exact_price_row(
        pricing,
        isin=str(comparator.get("isin") or ""),
        ticker=str(comparator.get("ticker") or ""),
        venue_code=str(comparator.get("mic") or ""),
        currency=str(comparator.get("currency") or "EUR"),
        report_date=report_date,
    )
    current_close = _num(price.get("close_price"))
    nav = _num(portfolio.get("nav_eur"))
    cash = _num(portfolio.get("cash_eur"))
    if nav <= 0 or current_close <= 0:
        raise RuntimeError("Accountability requires positive NAV and comparator close")

    history = _read_csv(history_path)
    prior_rows = [row for row in history if str(row.get("date") or "") < report_date]
    prior = prior_rows[-1] if prior_rows else None
    if prior is None:
        return {
            "status": "BASELINE_REQUIRED",
            "comparator_id": comparator.get("comparator_id"),
            "comparator_ticker": comparator.get("ticker"),
            "comparator_isin": comparator.get("isin"),
            "current_comparator_close_eur": round(current_close, 8),
            "portfolio_nav_eur": round(nav, 2),
            "cash_eur": round(cash, 2),
            "cash_weight_pct": round(100.0 * cash / nav, 6),
            "period_return_supported": False,
            "comparator_pricing": pricing_authority_summary(price),
            "unresolved": ["no_prior_accountability_baseline"],
        }

    baseline_date = str(prior.get("date") or "")
    prior_nav = _num(prior.get("portfolio_nav_eur"))
    prior_close = _num(prior.get("comparator_close_eur"))
    prior_index = _num(prior.get("comparator_index"), 100.0)
    if min(prior_nav, prior_close, prior_index) <= 0:
        raise RuntimeError("Prior accountability baseline is invalid")
    portfolio_return = (nav / prior_nav - 1.0) * 100.0
    comparator_return = (current_close / prior_close - 1.0) * 100.0
    comparator_index = prior_index * current_close / prior_close
    historical_navs = [_num(row.get("portfolio_nav_eur")) for row in history if _num(row.get("portfolio_nav_eur")) > 0]
    historical_indices = [_num(row.get("comparator_index")) for row in history if _num(row.get("comparator_index")) > 0]
    portfolio_peak = max(historical_navs + [nav])
    comparator_peak = max(historical_indices + [comparator_index])
    contributions, contribution_unresolved = _period_position_contributions(state, prior_nav=prior_nav, baseline_date=baseline_date)
    cash_policy = state.get("cash_policy") or {}
    unresolved = ["cash_drag_not_yet_evidenced", "transaction_costs_not_evidenced", *contribution_unresolved]
    return {
        "status": "COMPLETE" if not contribution_unresolved else "INCOMPLETE",
        "baseline_date": baseline_date,
        "report_date": report_date,
        "comparator_id": comparator.get("comparator_id"),
        "comparator_ticker": comparator.get("ticker"),
        "comparator_isin": comparator.get("isin"),
        "comparator_purpose": comparator.get("purpose"),
        "comparator_contract_effective_date": comparator.get("effective_date"),
        "portfolio_nav_eur": round(nav, 2),
        "portfolio_period_return_pct": round(portfolio_return, 6),
        "portfolio_drawdown_pct": round((nav / portfolio_peak - 1.0) * 100.0, 6),
        "comparator_close_eur": round(current_close, 8),
        "comparator_period_return_pct": round(comparator_return, 6),
        "comparator_index": round(comparator_index, 6),
        "comparator_drawdown_pct": round((comparator_index / comparator_peak - 1.0) * 100.0, 6),
        "active_return_pp": round(portfolio_return - comparator_return, 6),
        "cash_eur": round(cash, 2),
        "cash_weight_pct": round(100.0 * cash / nav, 6),
        "cash_drag_eur": None,
        "cash_drag_status": "UNAVAILABLE_NOT_ESTIMATED",
        "cash_rationale": cash_policy.get("cash_after_explanation") or "Cash rationale unresolved",
        "top_contributor": contributions[-1] if contributions else None,
        "top_detractor": contributions[0] if contributions else None,
        "position_contributions": contributions,
        "position_contribution_method": "current_market_value_minus_prior_dated_position_value_when_shares_unchanged",
        "position_flows_require_explicit_evidence": True,
        "costs_status": "UNAVAILABLE_NOT_INVENTED",
        "comparator_pricing": pricing_authority_summary(price),
        "unresolved": unresolved,
    }


def _risk_summary(decisions: list[dict[str, Any]], accountability: dict[str, Any]) -> dict[str, Any]:
    confidence_rank = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
    if decisions:
        weakest = sorted(decisions, key=lambda row: (confidence_rank.get(str(row.get("confidence")), 9), _num(row.get("contribution_eur"))))[0]
        if weakest.get("confidence") != "HIGH":
            return {"ticker": weakest.get("ticker"), "type": "evidence_confidence", "summary": f"{weakest.get('ticker')} has {weakest.get('confidence')} confidence because current evidence/verification is less complete."}
    detractor = accountability.get("top_detractor") or {}
    return {"ticker": detractor.get("ticker"), "type": "current_contribution", "summary": f"{detractor.get('ticker') or 'Portfolio'} is the largest current contribution drag ({round(_num(detractor.get('contribution_eur')), 2):.2f} EUR)."}


def build_review_state(
    normalized_state: dict[str, Any], *, comparator_config_path: Path, accountability_history_path: Path,
    report_date: str, run_id: str, pricing_artifact: str, donor_lane_artifact: str | None = None,
    macro_pack: str | None = None,
) -> dict[str, Any]:
    state = copy.deepcopy(normalized_state)
    portfolio = state.get("portfolio") or {}
    decisions = _position_decisions(state)
    comparator_config = _load_yaml(comparator_config_path)
    comparator = comparator_config.get("primary_comparator") or {}
    accountability = _accountability(state, comparator=comparator, history_path=accountability_history_path, pricing_path=Path(pricing_artifact), report_date=report_date)
    contribution_by_ticker = {str(row.get("ticker")): row.get("contribution_eur") for row in accountability.get("position_contributions") or []}
    for decision in decisions:
        decision["contribution_eur"] = contribution_by_ticker.get(str(decision.get("ticker")))

    blockers: list[str] = []
    if state.get("state_valid") is not True:
        blockers.append("normalized_input_state_invalid")
    if not decisions:
        blockers.append("no_funded_position_decisions")
    blockers.extend(f"position_unresolved:{row['ticker']}:{','.join(row['unresolved'])}" for row in decisions if row.get("unresolved"))
    if accountability.get("status") != "COMPLETE":
        blockers.append("accountability_incomplete")

    actions = [row["action"] for row in decisions]
    weekly_action = "HOLD_ALL_FUNDED_POSITIONS" if actions and all(action == "HOLD" for action in actions) else (
        ", ".join(f"{row['ticker']} {row['action']}" for row in decisions if row["action"] != "HOLD") or "REVIEW"
    )
    bridge = state.get("donor_discovery_bridge") if isinstance(state.get("donor_discovery_bridge"), dict) else {}
    challengers = [dict(row, funding_authority=False) for row in bridge.get("fundable_challengers") or [] if isinstance(row, dict)]
    best_challenger = dict(bridge.get("best_fundable_challenger") or {}) or None
    if best_challenger is not None:
        best_challenger["funding_authority"] = False
    biggest_risk = _risk_summary(decisions, accountability)

    unresolved_claims = list(accountability.get("unresolved") or [])
    for row in decisions:
        unresolved_claims.extend(f"{row['ticker']}:{item}" for item in row.get("unresolved") or [])

    return {
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
            "funding_authority": False, "portfolio_mutation": False, "trade_ledger_write": False,
            "real_broker_execution": False, "delivery_authority": False, "client_text_creates_state_authority": False,
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
            "best_new_or_replace_candidate": best_challenger,
            "biggest_current_risk": biggest_risk,
        },
        "accountability": accountability,
        "funded_position_decisions": decisions,
        "challengers": challengers,
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


def write_accountability_observation(review_state: dict[str, Any], path: Path) -> None:
    account = review_state.get("accountability") or {}
    if account.get("status") != "COMPLETE":
        raise RuntimeError("Cannot persist incomplete accountability observation")
    fieldnames = [
        "date", "portfolio_nav_eur", "portfolio_period_return_pct", "portfolio_drawdown_pct", "comparator_id",
        "comparator_close_eur", "comparator_index", "comparator_period_return_pct", "comparator_drawdown_pct",
        "active_return_pp", "cash_eur", "cash_weight_pct", "source_portfolio", "source_comparator", "record_status",
    ]
    rows = [row for row in _read_csv(path) if row.get("date") != review_state.get("report_date")]
    rows.append({
        "date": review_state["report_date"],
        "portfolio_nav_eur": f"{_num(account.get('portfolio_nav_eur')):.2f}",
        "portfolio_period_return_pct": f"{_num(account.get('portfolio_period_return_pct')):.6f}",
        "portfolio_drawdown_pct": f"{_num(account.get('portfolio_drawdown_pct')):.6f}",
        "comparator_id": account.get("comparator_id"),
        "comparator_close_eur": f"{_num(account.get('comparator_close_eur')):.8f}",
        "comparator_index": f"{_num(account.get('comparator_index')):.6f}",
        "comparator_period_return_pct": f"{_num(account.get('comparator_period_return_pct')):.6f}",
        "comparator_drawdown_pct": f"{_num(account.get('comparator_drawdown_pct')):.6f}",
        "active_return_pp": f"{_num(account.get('active_return_pp')):.6f}",
        "cash_eur": f"{_num(account.get('cash_eur')):.2f}",
        "cash_weight_pct": f"{_num(account.get('cash_weight_pct')):.6f}",
        "source_portfolio": review_state.get("sources", {}).get("protected_portfolio_state") or "normalized_review_state",
        "source_comparator": review_state.get("sources", {}).get("pricing_artifact"),
        "record_status": "CURRENT_REVIEW_OBSERVATION",
    })
    rows.sort(key=lambda row: row.get("date") or "")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def dump_review_state(review_state: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(review_state, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
