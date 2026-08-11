from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def _identity(row: dict[str, Any]) -> tuple[str, str]:
    return (
        str(row.get("isin") or "").strip().upper(),
        str(row.get("exchange_ticker") or row.get("ticker") or "").strip().upper(),
    )


def validate(
    decision: dict[str, Any],
    pricing: dict[str, Any],
    bridge: dict[str, Any],
    portfolio: dict[str, Any],
) -> dict[str, Any]:
    blockers: list[str] = []
    if decision.get("schema_version") != "etf_eu_current_allocation_decision_v1":
        blockers.append("allocation decision schema mismatch")
    if decision.get("allocation_status") != "ready_for_guarded_model_activation":
        blockers.append("allocation decision not ready")
    authority = decision.get("authority") or {}
    if authority.get("explicit_current_allocation_decision") is not True:
        blockers.append("explicit current allocation authority missing")
    if authority.get("model_portfolio_only") is not True or authority.get("real_broker_execution") is not False:
        blockers.append("model-only authority invalid")
    if authority.get("report_delivery_authority") is not False:
        blockers.append("allocation decision cannot grant delivery authority")
    if decision.get("report_date") != pricing.get("report_date"):
        blockers.append("allocation/pricing report date mismatch")
    if pricing.get("report_pricing_gate_passed") is not True:
        blockers.append("funded pricing gate is not passed")

    pricing_rows = {_identity(row): row for row in pricing.get("rows") or [] if isinstance(row, dict)}
    bridge_candidates: dict[tuple[str, str], dict[str, Any]] = {}
    for lane in bridge.get("assessed_lanes") or []:
        if not isinstance(lane, dict):
            continue
        for candidate in lane.get("ucits_candidates") or []:
            if isinstance(candidate, dict):
                bridge_candidates[_identity(candidate)] = candidate

    pre_nav = round(float(portfolio.get("nav_eur") or 0.0), 2)
    pre_cash = round(float(portfolio.get("cash_eur") or 0.0), 2)
    if abs(pre_nav - float(decision.get("pre_allocation_nav_eur") or 0.0)) > 0.01:
        blockers.append(f"decision pre-allocation NAV mismatch: state={pre_nav} decision={decision.get('pre_allocation_nav_eur')}")
    if abs(pre_cash - float(decision.get("pre_allocation_cash_eur") or 0.0)) > 0.01:
        blockers.append("decision pre-allocation cash mismatch")

    trade_value_total = 0.0
    exposures: set[str] = set()
    checked: list[dict[str, Any]] = []
    for row in decision.get("decisions") or []:
        if not isinstance(row, dict):
            continue
        ticker = str(row.get("exchange_ticker") or "").upper()
        identity = _identity(row)
        exposure = str(row.get("exposure_id") or "")
        row_blockers: list[str] = []
        if row.get("action") != "buy":
            row_blockers.append("only buy actions supported in this fresh-cash decision")
        shares = row.get("shares_delta")
        if not isinstance(shares, int) or shares <= 0:
            row_blockers.append("shares_delta must be positive whole shares")
        if not exposure or exposure in exposures:
            row_blockers.append("duplicate or missing exposure; one implementation per exposure required")
        exposures.add(exposure)
        price_row = pricing_rows.get(identity)
        if price_row is None:
            row_blockers.append("exact pricing line missing")
        else:
            agreeing = {str(value) for value in price_row.get("agreeing_providers") or [] if str(value).strip()}
            if (
                price_row.get("completed_close_on_or_before_report_date") is not True
                or price_row.get("source_agreement_status") != "qualified_development_consensus"
                or price_row.get("valuation_grade") is not True
                or len(agreeing) < 2
                or str(price_row.get("close_date") or "") != decision.get("report_date")
            ):
                row_blockers.append("exact line lacks two-provider completed-close valuation evidence")
            if abs(float(price_row.get("close_price") or 0) - float(row.get("close_price_eur") or 0)) > 0.0001:
                row_blockers.append("decision price differs from canonical pricing artifact")
        bridge_row = bridge_candidates.get(identity)
        if bridge_row is None or bridge_row.get("fundability_status") != "FUNDABLE_REQUIRES_ALLOCATION_DECISION":
            row_blockers.append("candidate is not fundable-requires-allocation-decision in EU bridge")
        metadata = row.get("instrument_metadata") or {}
        for key in (
            "would_initiate_today",
            "would_initiate_at_current_weight",
            "fresh_cash_implication",
            "thesis_assessment",
            "implementation_assessment",
            "best_alternative",
            "contribution_quality",
            "factor_overlap_level",
            "cash_policy_implication",
            "required_next_action",
        ):
            if not str(metadata.get(key) or "").strip():
                row_blockers.append(f"missing re-underwriting field:{key}")
        trade_value = round(int(shares or 0) * float(row.get("close_price_eur") or 0), 2)
        trade_value_total += trade_value
        actual_weight = (trade_value / pre_nav * 100.0) if pre_nav else 0.0
        if abs(actual_weight - float(row.get("allocation_weight_pct") or 0)) > 0.05:
            row_blockers.append("whole-share allocation weight does not match declared run-specific weight")
        checked.append({"ticker": ticker, "exposure_id": exposure, "trade_value_eur": trade_value, "passed": not row_blockers, "blockers": row_blockers})
        blockers.extend([f"{ticker}:{item}" for item in row_blockers])

    cash_after = round(pre_cash - trade_value_total, 2)
    nav_after = pre_nav
    cash_weight = cash_after / nav_after * 100.0 if nav_after else 0.0
    expected = decision.get("expected_post_allocation") or {}
    if abs(cash_after - float(expected.get("cash_eur") or 0)) > 0.02:
        blockers.append("expected post-allocation cash mismatch")
    if abs(cash_weight - float(expected.get("cash_weight_pct") or 0)) > 0.01:
        blockers.append("expected post-allocation cash weight mismatch")
    framework = decision.get("decision_framework") or {}
    if cash_weight > 3.0 and not str(framework.get("cash_after_explanation") or "").strip():
        blockers.append("material residual cash lacks deploy-or-explain rationale")
    if cash_weight > 5.0 and not str(framework.get("cash_after_classification") or "").strip():
        blockers.append("material residual cash lacks classification")
    if framework.get("retired_shadow_rules_used") is not False:
        blockers.append("retired shadow rules may not be used")
    if framework.get("position_count_target_used") is not False:
        blockers.append("position count target may not drive allocation")

    result = {
        "schema_version": "etf_eu_current_allocation_validation_v1",
        "allocation_decision_valid": not blockers,
        "passed": not blockers,
        "report_date": decision.get("report_date"),
        "activation_id": decision.get("activation_id"),
        "trade_count": len(checked),
        "checked_trades": checked,
        "pre_nav_eur": pre_nav,
        "pre_cash_eur": pre_cash,
        "trade_value_total_eur": round(trade_value_total, 2),
        "post_cash_eur": cash_after,
        "post_cash_weight_pct": round(cash_weight, 6),
        "blockers": blockers,
        "authority": {
            "model_portfolio_only": True,
            "real_broker_execution": False,
            "report_delivery_authority": False,
        },
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decision", required=True)
    parser.add_argument("--pricing-artifact", required=True)
    parser.add_argument("--discovery-bridge", required=True)
    parser.add_argument("--portfolio-state", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = validate(_load(Path(args.decision)), _load(Path(args.pricing_artifact)), _load(Path(args.discovery_bridge)), _load(Path(args.portfolio_state)))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result["passed"] is not True:
        raise SystemExit("ETF_EU_CURRENT_ALLOCATION_DECISION_INVALID")


if __name__ == "__main__":
    main()
