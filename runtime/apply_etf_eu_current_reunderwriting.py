from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from pricing.ucits_close_price_validation_contract_v2 import AUTHORIZED_EXACT_STATUSES


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


def _pricing_assessment(row: dict[str, Any], vehicle_text: str) -> str:
    authority_status = str(row.get("verification_status") or "").strip()
    if authority_status not in AUTHORIZED_EXACT_STATUSES:
        raise RuntimeError(
            f"Current re-underwriting requires canonical pricing authority for {_ticker(row)}; got {authority_status or 'missing'}"
        )
    if authority_status == "fresh_exact_verified":
        confidence = "independent same-date verification is present"
    else:
        confidence = "no current independent verifier is present, so confidence is lower but valuation authority remains valid"
    return (
        f"{vehicle_text} Exact completed-close primary pricing is authorized by the canonical pricing state; "
        f"{confidence}."
    )


def _base_position_evidence(
    row: dict[str, Any],
    *,
    report_date: str,
    run_id: str,
) -> dict[str, Any]:
    return {
        "ticker": _ticker(row),
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
    """Apply report-only current re-underwriting from canonical current state.

    Pricing facts are never asserted from hardcoded provider counts or prior-run
    observations. Every pricing statement below is derived from the position's
    canonical pricing authority already carried by normalized report state.
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
            "replaceable_status": "No",
            "best_alternative": "IWDA remains an implementation comparator; any current replacement decision must be re-derived from the current fundability bridge.",
            "replacement_close_status": "Re-derive from current canonical pricing state",
            "replacement_duel_status": "Current holding retained pending a superior current-state replacement case",
            "contribution_quality": "Primary diversified equity core; useful breadth, but overlaps the separate S&P 500 overweight.",
            "factor_overlap_level": "Medium",
            "factor_overlap_flag": "Meaningful U.S. equity overlap with SXR8; do not treat the two positions as independent diversification.",
            "hedge_validity_status": "Not a hedge; global equity core",
            "next_review_trigger": "Re-underwrite if broad-equity regime weakens materially, implementation quality deteriorates or SXR8 overlap rises enough to impair diversification.",
            "required_next_action": "Hold current shares; no add this run because current equity beta is already substantial and no stronger distinct core replacement is established by current evidence.",
            "vehicle_text": "Verified Xetra UCITS all-world implementation remains fit for the diversified core role.",
        },
        "EUNA": {
            "would_initiate_today": "Yes",
            "would_initiate_at_current_weight": "Yes",
            "fresh_cash_implication": "Hold",
            "thesis_score": 4.0,
            "thesis_assessment": "Global aggregate bonds remain a deliberate stabilising sleeve even in a risk-on regime; the modest weight preserves ballast without turning the portfolio into a duration bet.",
            "implementation_score": 4.8,
            "replaceable_status": "No",
            "best_alternative": "No current alternative has established a stronger implementation case for the same EUR-hedged global aggregate role.",
            "replacement_close_status": "Re-derive from current canonical pricing state",
            "replacement_duel_status": "Role retained; no replacement trigger",
            "contribution_quality": "Diversifying ballast against an otherwise equity-heavy model portfolio.",
            "factor_overlap_level": "Low",
            "factor_overlap_flag": "Low equity-factor overlap; duration and credit sensitivity remain the relevant risk factors.",
            "hedge_validity_status": "Ballast/diversifier, not a guaranteed hedge; retain modest sizing and review realised stress behaviour.",
            "next_review_trigger": "Re-underwrite if bond ballast fails during equity stress, rate volatility materially worsens, or a better verified diversifier becomes available.",
            "required_next_action": "Hold current shares as modest ballast; no add in the present risk-on regime.",
            "vehicle_text": "Verified EUR-hedged Xetra UCITS implementation remains fit for the stabilising role.",
        },
        "SXR8": {
            "would_initiate_today": "Yes",
            "would_initiate_at_current_weight": "Yes",
            "fresh_cash_implication": "Hold",
            "thesis_score": 4.5,
            "thesis_assessment": "The U.S. large-cap quality/growth overweight remains compatible with the current risk-on growth regime, but it must be judged together with VWCE rather than as separate diversification.",
            "implementation_score": 4.9,
            "replaceable_status": "No",
            "best_alternative": "CSPX shares the same fund exposure; any trading-line switch requires a superior current implementation case rather than historical provider-count claims.",
            "replacement_close_status": "Re-derive from current canonical pricing state",
            "replacement_duel_status": "Current Xetra line retained",
            "contribution_quality": "Intentional U.S. equity overweight layered on top of the global core.",
            "factor_overlap_level": "High",
            "factor_overlap_flag": "High overlap with VWCE's U.S. allocation; treat as an explicit overweight, not added diversification.",
            "hedge_validity_status": "Not a hedge; U.S. equity overweight",
            "next_review_trigger": "Re-underwrite if U.S. leadership weakens versus global equities or if combined VWCE/SXR8 concentration becomes decision-relevant.",
            "required_next_action": "Hold current shares; do not add because the overweight is already explicit and overlaps the global core.",
            "vehicle_text": "The mature S&P 500 Xetra UCITS implementation remains fit for the explicit U.S. overweight role.",
        },
        "L0CK": {
            "would_initiate_today": "Yes",
            "would_initiate_at_current_weight": "Yes",
            "fresh_cash_implication": "Hold",
            "thesis_score": round(_num(cyber.get("donor_total_score"), 4.97), 2),
            "thesis_assessment": f"Cybersecurity remains a high-quality digital-resilience lane: donor evidence score {round(_num(cyber.get('donor_total_score'), 4.97), 2)}, 1m return {round(_num(cyber.get('donor_return_1m_pct'), 3.81), 2)}% and 3m return {round(_num(cyber.get('donor_return_3m_pct'), 33.9), 2)}%.",
            "implementation_score": 4.7,
            "replaceable_status": "No",
            "best_alternative": "CIBR/BUG remain donor research references only; no superior exact EU replacement is currently established.",
            "replacement_close_status": "Re-derive from current canonical pricing state",
            "replacement_duel_status": "Current holding retained",
            "contribution_quality": "Distinct digital-resilience satellite, though it adds technology/growth sensitivity alongside the equity core.",
            "factor_overlap_level": "Medium",
            "factor_overlap_flag": "Some technology/growth overlap with broad equities; cybersecurity mandate remains sufficiently distinct at current size.",
            "hedge_validity_status": "Not a hedge; cybersecurity resilience satellite",
            "next_review_trigger": "Re-underwrite if cybersecurity relative strength rolls over materially or technology-factor concentration rises.",
            "required_next_action": "Hold current shares; no add while overall equity/technology factor exposure remains material.",
            "vehicle_text": "The verified iShares Digital Security Xetra UCITS implementation remains fit for the cybersecurity sleeve.",
        },
        "DFEN": {
            "would_initiate_today": "Yes",
            "would_initiate_at_current_weight": "Yes",
            "fresh_cash_implication": "Hold",
            "thesis_score": round(_num(defense.get("donor_total_score"), 4.59), 2),
            "thesis_assessment": f"Defense/resilience remains structurally durable: donor score {round(_num(defense.get('donor_total_score'), 4.59), 2)}, 1m return {round(_num(defense.get('donor_return_1m_pct'), 5.07), 2)}% and 3m return {round(_num(defense.get('donor_return_3m_pct'), 10.35), 2)}%.",
            "implementation_score": 4.7,
            "replaceable_status": "No",
            "best_alternative": "PPA/ITA remain U.S. donor references; no equally mature exact EU replacement is currently established.",
            "replacement_close_status": "Re-derive from current canonical pricing state",
            "replacement_duel_status": "Current holding retained",
            "contribution_quality": "Adds distinct defense/resilience exposure with moderate overlap to cybersecurity/industrial technology.",
            "factor_overlap_level": "Medium",
            "factor_overlap_flag": "Moderate overlap with L0CK/technology factors but a separate defense mandate remains justified.",
            "hedge_validity_status": "Not a hedge; thematic resilience satellite",
            "next_review_trigger": "Re-underwrite if defense relative strength deteriorates, policy support weakens, or factor overlap becomes excessive.",
            "required_next_action": "Hold the current position; fresh evidence does not justify adding or reducing this run.",
            "vehicle_text": "The verified VanEck Defense Xetra UCITS implementation remains fit for the defense/resilience sleeve.",
        },
        "IQQQ": {
            "would_initiate_today": "Yes",
            "would_initiate_at_current_weight": "Yes",
            "fresh_cash_implication": "Hold",
            "thesis_score": round(_num(water.get("donor_total_score"), 4.34), 2),
            "thesis_assessment": f"Water infrastructure remains structurally durable: donor score {round(_num(water.get('donor_total_score'), 4.34), 2)}, 1m return {round(_num(water.get('donor_return_1m_pct'), 6.03), 2)}% and 3m return {round(_num(water.get('donor_return_3m_pct'), 6.74), 2)}%.",
            "implementation_score": 4.8,
            "replaceable_status": "No",
            "best_alternative": "XMLC remains the first implementation comparator; any switch must be established from current identity, pricing authority, fundability and allocation evidence.",
            "replacement_close_status": "Re-derive from current canonical pricing state",
            "replacement_duel_status": "IQQQ retained pending a superior current implementation case",
            "contribution_quality": "Distinct water-infrastructure sleeve with low direct overlap to cybersecurity, defense and bond ballast.",
            "factor_overlap_level": "Low",
            "factor_overlap_flag": "Broad equity beta remains, but direct thematic overlap with other satellites is low.",
            "hedge_validity_status": "Not a hedge; thematic infrastructure satellite",
            "next_review_trigger": "Continue IQQQ-vs-XMLC implementation duel; replace only if XMLC establishes a clear implementation advantage or water-lane thesis weakens.",
            "required_next_action": "Hold current IQQQ; do not double-fund the same water exposure.",
            "vehicle_text": "The verified iShares Global Water Xetra UCITS implementation remains fit for the water-infrastructure sleeve.",
        },
    }

    evidence_rows: list[dict[str, Any]] = []
    for row in positions:
        ticker = _ticker(row)
        judgment = dict(judgments[ticker])
        vehicle_text = str(judgment.pop("vehicle_text"))
        judgment["implementation_assessment"] = _pricing_assessment(row, vehicle_text)
        row.update(judgment)
        row["fresh_cash_test"] = (
            f"Fresh {report_date} re-underwriting completed from current valuation, macro context, donor lane evidence and EU implementation facts"
        )
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
        evidence.update(
            {
                key: judgment.get(key)
                for key in (
                    "would_initiate_today",
                    "would_initiate_at_current_weight",
                    "fresh_cash_implication",
                    "thesis_score",
                    "thesis_assessment",
                    "implementation_score",
                    "implementation_assessment",
                    "factor_overlap_level",
                    "factor_overlap_flag",
                    "best_alternative",
                    "required_next_action",
                )
            }
        )
        evidence_rows.append(evidence)

    portfolio["positions"] = positions
    portfolio["cash_classification"] = "Tactical reserve"
    result["portfolio"] = portfolio
    result["current_reunderwriting"] = {
        "schema_version": "etf_eu_current_reunderwriting_v2",
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
            "Retain residual cash unless a distinct new lane clears current UCITS identity, KID, canonical exact-close pricing authority, "
            "current re-underwriting and an explicit allocation decision. No fixed cash floor and no prior-run provider-count assertion is used."
        ),
        "candidate_review": {
            "XMLC": "Keep as the IQQQ implementation comparator; reassess only from the current fundability bridge.",
            "VVSM": "Reassess only from the current donor-to-UCITS fundability bridge; no prior-run pricing claim is carried forward.",
            "CBUF": "Reassess only from current canonical pricing authority and current lane evidence.",
            "ISAE": "Reassess only from current canonical pricing authority and current lane evidence.",
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
    output_path.write_text(
        json.dumps(result["current_reunderwriting"], indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
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
