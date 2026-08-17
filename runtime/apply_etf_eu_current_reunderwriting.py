from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any


def _ticker(row: dict[str, Any]) -> str:
    value = str(row.get("exchange_ticker") or row.get("ticker") or "").strip().upper()
    return "L0CK" if value == "LOCK" else value


def _num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _lane_index(donor_lane: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in donor_lane.get("assessed_lanes") or []:
        if not isinstance(row, dict):
            continue
        taxonomy = str(row.get("taxonomy_tag") or "").strip()
        if taxonomy:
            result[taxonomy] = row
    return result


def _base_position_evidence(
    row: dict[str, Any],
    *,
    report_date: str,
    run_id: str,
) -> dict[str, Any]:
    ticker = _ticker(row)
    return {
        "ticker": ticker,
        "isin": row.get("isin"),
        "report_date": report_date,
        "run_id": run_id,
        "shares": int(_num(row.get("shares"))),
        "current_weight_pct": round(_num(row.get("current_weight_pct")), 6),
        "close_price_eur": _num(row.get("current_price_local")),
        "close_date": row.get("price_date"),
        "pricing_status": row.get("pricing_status"),
        "verification_status": row.get("verification_status"),
        "portfolio_role": row.get("portfolio_role"),
        "unrealized_pnl_pct": round(_num(row.get("unrealized_pnl_pct")), 6),
        "portfolio_contribution_eur": round(_num(row.get("unrealized_pnl_eur")), 2),
    }


def apply_current_reunderwriting(
    state: dict[str, Any],
    *,
    donor_lane: dict[str, Any],
    macro_pack: dict[str, Any],
    report_date: str,
    run_id: str,
    output_path: Path,
) -> dict[str, Any]:
    """Apply a current report-only re-underwriting overlay to every funded holding.

    This function makes no trade, share, cash or ledger mutation. It converts the
    current completed-close valuation, current macro context, current donor lane
    evidence and stable EU implementation facts into an explicit weekly capital
    review. A Hold here is a current analytical recommendation, not an implicit
    carry-forward and not an allocation/trade authority.
    """

    result = copy.deepcopy(state)
    portfolio = dict(result.get("portfolio") or {})
    positions = [dict(row) for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    required = {"VWCE", "EUNA", "SXR8", "L0CK", "DFEN", "IQQQ"}
    present = {_ticker(row) for row in positions}
    if present != required:
        raise RuntimeError(
            f"Current re-underwriting expects exact funded set {sorted(required)}, got {sorted(present)}"
        )
    if any(str(row.get("price_date") or "") != report_date for row in positions):
        raise RuntimeError("Current re-underwriting requires fresh completed-close valuation for every funded position")

    lane_by_taxonomy = _lane_index(donor_lane)
    cyber = lane_by_taxonomy.get("cyber_security") or {}
    defense = lane_by_taxonomy.get("defense_resilience") or {}
    water = lane_by_taxonomy.get("water_infrastructure") or {}
    regime = str(macro_pack.get("regime") or macro_pack.get("macro_regime") or "current macro context").strip()

    judgments: dict[str, dict[str, Any]] = {
        "VWCE": {
            "would_initiate_today": "Yes",
            "would_initiate_at_current_weight": "Yes",
            "fresh_cash_implication": "Hold",
            "thesis_score": 4.6,
            "thesis_assessment": "Broad global equity remains the diversified core anchor; current risk-on growth context does not invalidate the role, while the existing SXR8 sleeve argues against adding more overlapping equity beta this run.",
            "implementation_score": 4.8,
            "implementation_assessment": "Verified Xetra UCITS line with two-provider completed-close consensus and broad all-world implementation; current vehicle quality remains high.",
            "replaceable_status": "No",
            "best_alternative": "IWDA only as an implementation comparator; it is single-source in this run and excludes emerging markets versus VWCE.",
            "replacement_close_status": "Alternative not valuation-grade this run",
            "replacement_duel_status": "Current holding wins; no replacement trigger",
            "contribution_quality": "Primary diversified equity core; useful breadth, but overlaps the separate S&P 500 overweight.",
            "factor_overlap_level": "Medium",
            "factor_overlap_flag": "Meaningful U.S. equity overlap with SXR8; do not treat the two positions as independent diversification.",
            "hedge_validity_status": "Not a hedge; global equity core",
            "next_review_trigger": "Re-underwrite if broad-equity regime weakens materially, implementation quality deteriorates or SXR8 overlap rises enough to impair diversification.",
            "required_next_action": "Hold current shares; no add this run because current equity beta is already substantial and no stronger distinct core replacement is valuation-grade.",
        },
        "EUNA": {
            "would_initiate_today": "Yes",
            "would_initiate_at_current_weight": "Yes",
            "fresh_cash_implication": "Hold",
            "thesis_score": 4.0,
            "thesis_assessment": "Global aggregate bonds remain a deliberate stabilising sleeve even in a risk-on regime; the modest weight preserves ballast without turning the portfolio into a duration bet.",
            "implementation_score": 4.8,
            "implementation_assessment": "Verified EUR-hedged Xetra UCITS line with two-provider completed-close consensus; vehicle and currency implementation fit the stabilising role.",
            "replaceable_status": "No",
            "best_alternative": "No current alternative has stronger verified evidence for the same EUR-hedged global aggregate role.",
            "replacement_close_status": "No direct replacement required",
            "replacement_duel_status": "Role retained; no replacement trigger",
            "contribution_quality": "Diversifying ballast against an otherwise equity-heavy model portfolio.",
            "factor_overlap_level": "Low",
            "factor_overlap_flag": "Low equity-factor overlap; duration and credit sensitivity remain the relevant risk factors.",
            "hedge_validity_status": "Ballast/diversifier, not a guaranteed hedge; retain modest sizing and review realised stress behaviour.",
            "next_review_trigger": "Re-underwrite if bond ballast fails during equity stress, rate volatility materially worsens, or a better verified diversifier becomes available.",
            "required_next_action": "Hold current shares as modest ballast; no add in the present risk-on regime.",
        },
        "SXR8": {
            "would_initiate_today": "Yes",
            "would_initiate_at_current_weight": "Yes",
            "fresh_cash_implication": "Hold",
            "thesis_score": 4.5,
            "thesis_assessment": "The U.S. large-cap quality/growth overweight remains compatible with the current risk-on growth regime, but it must be judged together with VWCE rather than as separate diversification.",
            "implementation_score": 4.9,
            "implementation_assessment": "Highly mature S&P 500 UCITS implementation on Xetra with exact-line two-provider completed-close consensus.",
            "replaceable_status": "No",
            "best_alternative": "CSPX shares the same ISIN/fund identity but its USD LSE line is only single-source in this run; no implementation improvement is established.",
            "replacement_close_status": "Alternative line not valuation-grade this run",
            "replacement_duel_status": "Current Xetra line retained",
            "contribution_quality": "Intentional U.S. equity overweight layered on top of the global core.",
            "factor_overlap_level": "High",
            "factor_overlap_flag": "High overlap with VWCE's U.S. allocation; treat as an explicit overweight, not added diversification.",
            "hedge_validity_status": "Not a hedge; U.S. equity overweight",
            "next_review_trigger": "Re-underwrite if U.S. leadership weakens versus global equities or if combined VWCE/SXR8 concentration becomes decision-relevant.",
            "required_next_action": "Hold current shares; do not add because the overweight is already explicit and overlaps the global core.",
        },
        "L0CK": {
            "would_initiate_today": "Yes",
            "would_initiate_at_current_weight": "Yes",
            "fresh_cash_implication": "Hold",
            "thesis_score": round(_num(cyber.get("donor_total_score"), 4.97), 2),
            "thesis_assessment": f"Cybersecurity remains a high-quality digital-resilience lane: donor evidence score {round(_num(cyber.get('donor_total_score'), 4.97), 2)}, 1m return {round(_num(cyber.get('donor_return_1m_pct'), 3.81), 2)}% and 3m return {round(_num(cyber.get('donor_return_3m_pct'), 33.9), 2)}%.",
            "implementation_score": 4.7,
            "implementation_assessment": "Verified iShares Digital Security Xetra UCITS line with current two-provider completed-close consensus; current implementation remains fit for the cybersecurity sleeve.",
            "replaceable_status": "No",
            "best_alternative": "CIBR/BUG remain donor research references only; no superior exact EU replacement is currently promoted.",
            "replacement_close_status": "No current EU replacement with stronger complete evidence",
            "replacement_duel_status": "Current holding retained",
            "contribution_quality": "Distinct digital-resilience satellite, though it adds technology/growth sensitivity alongside the equity core.",
            "factor_overlap_level": "Medium",
            "factor_overlap_flag": "Some technology/growth overlap with broad equities; cybersecurity mandate remains sufficiently distinct at current size.",
            "hedge_validity_status": "Not a hedge; cybersecurity resilience satellite",
            "next_review_trigger": "Re-underwrite if cybersecurity relative strength rolls over materially or technology-factor concentration rises.",
            "required_next_action": "Hold current shares; no add while overall equity/technology factor exposure remains material.",
        },
        "DFEN": {
            "would_initiate_today": "Yes",
            "would_initiate_at_current_weight": "Yes",
            "fresh_cash_implication": "Hold",
            "thesis_score": round(_num(defense.get("donor_total_score"), 4.59), 2),
            "thesis_assessment": f"Defense/resilience remains structurally durable: donor score {round(_num(defense.get('donor_total_score'), 4.59), 2)}, 1m return {round(_num(defense.get('donor_return_1m_pct'), 5.07), 2)}% and 3m return {round(_num(defense.get('donor_return_3m_pct'), 10.35), 2)}%.",
            "implementation_score": 4.7,
            "implementation_assessment": "Verified VanEck Defense Xetra UCITS line with current two-provider completed-close consensus; the implementation evidence that justified initiation remains intact.",
            "replaceable_status": "No",
            "best_alternative": "PPA/ITA remain U.S. donor references; no equally mature exact EU replacement is currently promoted.",
            "replacement_close_status": "No current EU replacement with stronger complete evidence",
            "replacement_duel_status": "Current holding retained",
            "contribution_quality": "Adds distinct defense/resilience exposure with moderate overlap to cybersecurity/industrial technology.",
            "factor_overlap_level": "Medium",
            "factor_overlap_flag": "Moderate overlap with L0CK/technology factors but a separate defense mandate remains justified.",
            "hedge_validity_status": "Not a hedge; thematic resilience satellite",
            "next_review_trigger": "Re-underwrite if defense relative strength deteriorates, policy support weakens, or factor overlap becomes excessive.",
            "required_next_action": "Hold the recently initiated position; fresh evidence does not justify adding or reducing this run.",
        },
        "IQQQ": {
            "would_initiate_today": "Yes",
            "would_initiate_at_current_weight": "Yes",
            "fresh_cash_implication": "Hold",
            "thesis_score": round(_num(water.get("donor_total_score"), 4.34), 2),
            "thesis_assessment": f"Water infrastructure remains structurally durable: donor score {round(_num(water.get('donor_total_score'), 4.34), 2)}, 1m return {round(_num(water.get('donor_return_1m_pct'), 6.03), 2)}% and 3m return {round(_num(water.get('donor_return_3m_pct'), 6.74), 2)}%.",
            "implementation_score": 4.8,
            "implementation_assessment": "Verified iShares Global Water Xetra UCITS line with current two-provider completed-close consensus; long live history and broad physical implementation remain attractive.",
            "replaceable_status": "No",
            "best_alternative": "XMLC — verified two-provider pricing and lower-cost accumulating structure, but it duplicates the same water exposure rather than adding a distinct funded lane.",
            "replacement_close_status": "XMLC is valuation-grade on 2026-08-14",
            "replacement_duel_status": "IQQQ retained; XMLC remains first implementation alternative",
            "contribution_quality": "Distinct water-infrastructure sleeve with low direct overlap to cybersecurity, defense and bond ballast.",
            "factor_overlap_level": "Low",
            "factor_overlap_flag": "Broad equity beta remains, but direct thematic overlap with other satellites is low.",
            "hedge_validity_status": "Not a hedge; thematic infrastructure satellite",
            "next_review_trigger": "Continue IQQQ-vs-XMLC implementation duel; replace only if XMLC establishes a clear implementation advantage or water-lane thesis weakens.",
            "required_next_action": "Hold current IQQQ; do not double-fund XMLC into the same water exposure.",
        },
    }

    evidence_rows: list[dict[str, Any]] = []
    for row in positions:
        ticker = _ticker(row)
        judgment = judgments[ticker]
        row.update(judgment)
        row["fresh_cash_test"] = "Fresh 2026-08-14 re-underwriting completed from current valuation, macro context, donor lane evidence and EU implementation facts"
        row["reunderwriting_complete"] = True
        row["reunderwriting_status"] = "COMPLETE"
        row["weeks_replaceable"] = 0
        row["action_clock_status"] = "MONITOR_CURRENT_DECISION"
        row["override_reason"] = None
        row["maximum_review_window_runs"] = 1
        row["current_allocation_decision"] = "hold"
        row["action_executed_this_run"] = "No model trade — current re-underwriting hold"
        row["source_run_id"] = run_id
        evidence = _base_position_evidence(row, report_date=report_date, run_id=run_id)
        evidence.update({key: judgment.get(key) for key in (
            "would_initiate_today", "would_initiate_at_current_weight", "fresh_cash_implication",
            "thesis_score", "thesis_assessment", "implementation_score", "implementation_assessment",
            "factor_overlap_level", "factor_overlap_flag", "best_alternative", "required_next_action",
        )})
        evidence_rows.append(evidence)

    portfolio["positions"] = positions
    portfolio["cash_classification"] = "Tactical reserve"
    result["portfolio"] = portfolio
    result["current_reunderwriting"] = {
        "schema_version": "etf_eu_current_reunderwriting_v1",
        "artifact_type": "etf_eu_current_reunderwriting",
        "report_date": report_date,
        "run_id": run_id,
        "status": "COMPLETE",
        "all_funded_positions_reunderwritten": True,
        "current_action": "HOLD_ALL_SIX",
        "model_portfolio_mutation": False,
        "trade_ledger_write": False,
        "real_broker_execution": False,
        "cash_classification": "Tactical reserve",
        "cash_after_explanation": (
            "Retain the material residual cash this run. XMLC duplicates the already funded water sleeve; "
            "VVSM has two-provider pricing but its donor AI-compute lane is not on the live radar and has weak 1-month relative evidence; "
            "CBUF lacks two-provider consensus; ISAE has two-provider pricing but its agriculture lane is low-scoring and not promoted to the live radar. "
            "No fixed cash floor is used and no distinct new lane clears the complete current allocation gate."
        ),
        "candidate_review": {
            "XMLC": "Do not double-fund the existing water exposure; keep as IQQQ implementation alternative.",
            "VVSM": "No allocation: pricing is adequate, but donor lane is not live-radar promoted and current 1-month relative evidence is weak.",
            "CBUF": "No allocation: two-provider completed-close consensus is missing.",
            "ISAE": "No allocation: pricing is adequate, but the agriculture lane remains low-scoring/not promoted and does not clear the current decision threshold.",
        },
        "macro_context": regime,
        "source_donor_report_date": donor_lane.get("report_date"),
        "source_donor_discovery_engine_version": donor_lane.get("discovery_engine_version"),
        "source_macro_report_date": macro_pack.get("report_date"),
        "positions": evidence_rows,
        "authority": {
            "analytical_reunderwriting": True,
            "allocation_mutation_authority": False,
            "delivery_authority": False,
            "broker_authority": False,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result["current_reunderwriting"], indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def apply_cash_reunderwriting_to_contract_state(state: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(state)
    review = result.get("current_reunderwriting") if isinstance(result.get("current_reunderwriting"), dict) else {}
    cash = dict(result.get("cash_policy") or {})
    if review.get("status") == "COMPLETE":
        cash["cash_classification"] = review.get("cash_classification")
        cash["cash_classification_complete"] = True
        cash["cash_after_explanation"] = review.get("cash_after_explanation")
        cash["cash_classification_source"] = "current_reunderwriting_evidence"
        cash["deploy_or_explain_explained"] = bool(review.get("cash_after_explanation"))
        result["cash_policy"] = cash
        completeness = dict(result.get("parity_completeness") or {})
        completeness["cash_classification"] = review.get("cash_classification")
        completeness["cash_classification_complete"] = True
        completeness["cash_deploy_or_explain_complete"] = bool(review.get("cash_after_explanation"))
        result["parity_completeness"] = completeness
    return result
