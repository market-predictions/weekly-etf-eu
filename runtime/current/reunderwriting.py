from __future__ import annotations

import copy
import csv
import json
from pathlib import Path
from typing import Any

_ALLOWED_MEMORY_ACTIONS = {"ADD", "HOLD", "REDUCE", "REPLACE", "CLOSE", "REVIEW"}


def _num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _bool(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _ticker(row: dict[str, Any]) -> str:
    value = str(row.get("exchange_ticker") or row.get("ticker") or "").strip().upper()
    return "L0CK" if value == "LOCK" else value


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object in {path}")
    return payload


def _latest_completed_memory(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    latest: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        if not _bool(row.get("reunderwriting_complete")):
            continue
        ticker = str(row.get("ticker") or "").strip().upper()
        isin = str(row.get("isin") or "").strip().upper()
        if not ticker or not isin:
            continue
        key = (isin, ticker)
        previous = latest.get(key)
        if previous is None or (str(row.get("report_date") or ""), str(row.get("run_id") or "")) > (
            str(previous.get("report_date") or ""), str(previous.get("run_id") or "")
        ):
            latest[key] = row
    return latest


def _memory_action(memory: dict[str, Any]) -> str:
    raw = str(memory.get("current_allocation_decision") or memory.get("fresh_cash_implication") or "REVIEW").strip().upper()
    aliases = {"INITIATE": "ADD", "BUY": "ADD", "TRIM": "REDUCE", "SELL": "CLOSE", "WATCH ONE MORE WEEK": "REVIEW"}
    action = aliases.get(raw, raw)
    return action if action in _ALLOWED_MEMORY_ACTIONS else "REVIEW"


def _macro_fresh(macro: dict[str, Any], report_date: str) -> tuple[bool, str | None]:
    provenance = macro.get("donor_provenance") if isinstance(macro.get("donor_provenance"), dict) else {}
    source_date = str(provenance.get("source_report_date") or macro.get("report_date") or "")
    if not source_date:
        return False, None
    return source_date == report_date, source_date


def _lane_evidence_for_position(bridge: dict[str, Any], isin: str, ticker: str) -> list[dict[str, Any]]:
    evidence = []
    for lane in bridge.get("assessed_lanes") or []:
        if not isinstance(lane, dict):
            continue
        for candidate in lane.get("ucits_candidates") or []:
            if not isinstance(candidate, dict):
                continue
            if str(candidate.get("isin") or "").strip().upper() == isin and str(candidate.get("exchange_ticker") or "").strip().upper() == ticker:
                evidence.append(lane)
    return evidence


def _same_exposure_challengers(bridge: dict[str, Any], lane_evidence: list[dict[str, Any]], funded_isin: str, funded_ticker: str) -> list[dict[str, Any]]:
    challengers: list[dict[str, Any]] = []
    lane_keys = {(lane.get("taxonomy_tag"), lane.get("bucket"), lane.get("lane_name")) for lane in lane_evidence}
    for lane in bridge.get("assessed_lanes") or []:
        if not isinstance(lane, dict) or (lane.get("taxonomy_tag"), lane.get("bucket"), lane.get("lane_name")) not in lane_keys:
            continue
        for candidate in lane.get("ucits_candidates") or []:
            if not isinstance(candidate, dict):
                continue
            isin = str(candidate.get("isin") or "").strip().upper()
            ticker = str(candidate.get("exchange_ticker") or "").strip().upper()
            if (isin, ticker) == (funded_isin, funded_ticker):
                continue
            if candidate.get("fundability_status") == "FUNDABLE_REQUIRES_ALLOCATION_DECISION":
                challengers.append({
                    "ticker": ticker,
                    "isin": isin,
                    "fund_name": candidate.get("fund_name"),
                    "pricing_verification_status": candidate.get("pricing_verification_status"),
                    "lane_name": lane.get("lane_name"),
                    "donor_total_score": lane.get("donor_total_score"),
                })
    return challengers


def apply_current_reunderwriting(
    normalized_state: dict[str, Any],
    *,
    recommendation_history_path: Path,
    macro_pack_path: Path,
    discovery_bridge: dict[str, Any],
    report_date: str,
    run_id: str,
    evidence_output_path: Path,
) -> dict[str, Any]:
    state = copy.deepcopy(normalized_state)
    memory = _latest_completed_memory(recommendation_history_path)
    macro = _load_json(macro_pack_path)
    macro_is_fresh, macro_source_date = _macro_fresh(macro, report_date)
    positions = state.get("portfolio", {}).get("positions") or []
    cash = _num(state.get("portfolio", {}).get("cash_eur"))
    nav = _num(state.get("portfolio", {}).get("nav_eur"))
    cash_weight = 100.0 * cash / nav if nav else 0.0
    evidence_rows: list[dict[str, Any]] = []

    for position in positions:
        ticker = _ticker(position)
        isin = str(position.get("isin") or "").strip().upper()
        prior = memory.get((isin, ticker))
        blockers: list[str] = []
        if prior is None:
            blockers.append("no_completed_reunderwriting_memory")
        if position.get("identity_binding_valid") is not True:
            blockers.append("identity_binding_invalid")
        if position.get("pricing_status") != "valuation_grade_exact_close" or str(position.get("price_date") or "") != report_date:
            blockers.append("current_exact_close_invalid")
        if not macro_is_fresh:
            blockers.append("macro_context_not_current_for_report_date")

        lane_evidence = _lane_evidence_for_position(discovery_bridge, isin, ticker)
        challengers = _same_exposure_challengers(discovery_bridge, lane_evidence, isin, ticker)
        prior_action = _memory_action(prior or {})
        prior_thesis_score = _num((prior or {}).get("thesis_score"), -1.0)
        prior_implementation_score = _num((prior or {}).get("implementation_score"), -1.0)
        if prior_thesis_score < 0 or prior_implementation_score < 0:
            blockers.append("prior_thesis_or_implementation_score_missing")

        pnl_pct = _num(position.get("unrealized_pnl_pct"))
        hard_review_trigger = pnl_pct < -10.0 and prior_implementation_score < 4.0
        if hard_review_trigger:
            blockers.append("loss_and_implementation_review_trigger")

        complete = not blockers
        # Historical recommendation memory is continuity evidence only. It may
        # never directly become the current action. With complete current-run
        # evidence and no machine-evidenced invalidation/superior replacement,
        # the current independent decision is HOLD; otherwise fail closed to REVIEW.
        current_action = "HOLD" if complete else "REVIEW"

        challenger_text = "No same-exposure fundable challenger established in current discovery evidence"
        if challengers:
            first = challengers[0]
            challenger_text = f"{first.get('ticker')} ({first.get('fund_name') or first.get('isin')}) is currently fundable for a separate allocation decision; no automatic superiority is inferred"
        elif prior and str(prior.get("best_alternative") or "").strip():
            challenger_text = str(prior.get("best_alternative")).strip() + " [historical comparison memory; not current funding authority]"

        thesis_memory = str((prior or {}).get("thesis_assessment") or "").strip()
        fresh_test = (
            f"Fresh {report_date} test: exact identity-bound close is current; macro evidence date={macro_source_date or 'missing'}; "
            f"same-exposure current fundable challengers={len(challengers)}; prior action={prior_action} is history only and is not reused as current authority."
        )
        assessment = (
            f"Prior thesis continuity: {thesis_memory} Current run found no machine-evidenced hard invalidation or superior replacement authority; current action is independently derived as HOLD."
            if complete else
            f"Current re-underwriting cannot close: {', '.join(blockers)}. Prior thesis and prior action are retained as history only, not current decision authority."
        )
        implementation_assessment = (
            f"Exact {report_date} valuation-grade close on the bound EU trading line; verification={position.get('verification_status')}."
        )
        position.update({
            "would_initiate_today": "Yes" if current_action == "HOLD" and complete else "Review",
            "would_initiate_at_current_weight": "Yes" if current_action == "HOLD" and complete else "Review",
            "fresh_cash_implication": current_action.title() if current_action != "REVIEW" else "Review",
            "fresh_cash_test": fresh_test,
            "reunderwriting_complete": complete,
            "reunderwriting_status": "COMPLETE" if complete else "UNRESOLVED",
            "thesis_score": prior_thesis_score if prior_thesis_score >= 0 else None,
            "thesis_assessment": assessment,
            "implementation_score": prior_implementation_score if prior_implementation_score >= 0 else None,
            "implementation_assessment": implementation_assessment,
            "best_alternative": challenger_text,
            "replacement_close_status": "Current exact-close evidence available for listed fundable challengers" if challengers else "No current same-exposure fundable replacement established",
            "replacement_duel_status": "Separate allocation decision required; discovery/pricing never auto-replaces a funded position",
            "factor_overlap_level": (prior or {}).get("factor_overlap_level") or "Unresolved",
            "factor_overlap_flag": (prior or {}).get("factor_overlap_flag") or "",
            "hedge_validity_status": (prior or {}).get("hedge_validity_status") or "Not designated as a guaranteed hedge",
            "current_allocation_decision": current_action.lower() if current_action != "REVIEW" else "review",
            "next_review_trigger": (prior or {}).get("next_review_trigger") or "Next weekly re-underwriting or material evidence change",
            "required_next_action": "Maintain current model shares pending next weekly re-underwriting" if current_action == "HOLD" else "Current decision: REVIEW",
            "source_run_id": run_id,
            "source_authority": "current_exact_pricing_plus_current_macro_plus_current_discovery_plus_historical_thesis_memory",
            "reunderwriting_memory_report_date": (prior or {}).get("report_date"),
            "reunderwriting_memory_run_id": (prior or {}).get("run_id"),
            "reunderwriting_memory_shares": _num((prior or {}).get("shares"), -1.0),
            "reunderwriting_memory_weight_pct": _num((prior or {}).get("current_weight_pct"), -1.0),
            "reunderwriting_memory_action": prior_action,
            "reunderwriting_blockers": blockers,
            "same_exposure_current_challengers": challengers,
        })
        evidence_rows.append({
            "ticker": ticker,
            "isin": isin,
            "complete": complete,
            "current_action": current_action,
            "memory_action": prior_action,
            "memory_report_date": (prior or {}).get("report_date"),
            "memory_shares": (prior or {}).get("shares"),
            "memory_weight_pct": (prior or {}).get("current_weight_pct"),
            "macro_source_date": macro_source_date,
            "exact_close_date": position.get("price_date"),
            "verification_status": position.get("verification_status"),
            "lane_evidence_count": len(lane_evidence),
            "same_exposure_fundable_challenger_count": len(challengers),
            "hard_review_trigger": hard_review_trigger,
            "blockers": blockers,
        })

    incomplete = [row for row in evidence_rows if not row["complete"]]
    best_challenger = discovery_bridge.get("best_fundable_challenger")
    cash_rationale = (
        "Cash remains a material tactical reserve. Current discovery has a fundable challenger, but fundability is not allocation authority; deployment requires an explicit model allocation decision."
        if best_challenger else
        "Cash remains a material tactical reserve because current discovery does not establish a fully fundable challenger with separate allocation authority."
    ) if cash_weight > 5.0 else "Residual cash remains below the material-cash threshold."

    state["cash_policy"] = {
        "cash_eur": round(cash, 2),
        "cash_weight_pct": round(cash_weight, 6),
        "cash_classification": "Tactical reserve" if cash_weight > 5.0 else "Uninvested residual",
        "cash_after_explanation": cash_rationale,
        "material_position": cash_weight > 5.0,
        "deploy_or_explain_review_required_if_actionable_fundable_lane_exists": cash_weight > 3.0,
        "automatic_trade_authority": False,
    }
    state["current_reunderwriting"] = {
        "schema_version": "etf_eu_current_reunderwriting_v1",
        "report_date": report_date,
        "run_id": run_id,
        "complete": not incomplete,
        "funded_position_count": len(evidence_rows),
        "completed_position_count": len(evidence_rows) - len(incomplete),
        "incomplete_tickers": [row["ticker"] for row in incomplete],
        "macro_source_date": macro_source_date,
        "macro_fresh": macro_is_fresh,
        "cash_after_explanation": cash_rationale,
        "best_fundable_challenger": best_challenger,
        "authority": {"portfolio_mutation": False, "funding_authority": False, "trade_authority": False},
    }
    state["donor_discovery_bridge"] = discovery_bridge
    state["macro"] = {
        "source_report_date": macro_source_date,
        "fresh_for_report": macro_is_fresh,
        "regime_label": macro.get("regime_label") or macro.get("legacy_regime_label"),
        "authority": "descriptive_context_only",
    }
    state["state_valid"] = state.get("state_valid") is True and not incomplete
    state["blockers"] = list(state.get("blockers") or []) + [f"reunderwriting_incomplete:{row['ticker']}:{','.join(row['blockers'])}" for row in incomplete]

    evidence = {
        "schema_version": "etf_eu_current_reunderwriting_evidence_v1",
        "report_date": report_date,
        "run_id": run_id,
        "complete": not incomplete,
        "rows": evidence_rows,
        "best_fundable_challenger": best_challenger,
        "cash_rationale": cash_rationale,
        "authority": {"funding_authority": False, "portfolio_mutation": False, "trade_authority": False},
    }
    evidence_output_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_output_path.write_text(json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    return state
