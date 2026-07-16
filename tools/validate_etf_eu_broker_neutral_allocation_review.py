from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def f(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def validate(payload: dict[str, Any]) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    authority = payload.get("authority") or {}
    revaluation = payload.get("portfolio_revaluation") or {}
    allocation = payload.get("allocation_decision") or {}
    intents = payload.get("trade_intents") or []
    rows = payload.get("decision_rows") or []

    if payload.get("schema_version") != "etf_eu_broker_neutral_allocation_review_v1":
        errors.append("schema_version_invalid")

    expected_authority = {
        "model_portfolio_only": True,
        "real_broker_execution": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
        "broker_specific_permission_required_for_model": False,
        "broker_permission_required_for_real_execution": True,
        "whole_shares_only": True,
        "blocked_capacity_reallocated": False,
    }
    for key, expected in expected_authority.items():
        if authority.get(key) is not expected:
            errors.append(f"authority_invalid:{key}")

    if payload.get("hard_blockers"):
        errors.append("hard_blockers_present")
    if allocation.get("portfolio_mutation") is not False:
        errors.append("review_mutation_not_false")
    if allocation.get("second_tranche_authorized") is not False:
        errors.append("automatic_second_tranche_detected")
    if allocation.get("nav_reconciliation_ok") is not True:
        errors.append("nav_reconciliation_not_true")

    revalued_nav = f(revaluation.get("nav_eur"))
    projected_nav = f(allocation.get("nav_after_decision_eur"))
    if abs(revalued_nav - projected_nav) > 0.01:
        errors.append("projected_nav_drift")

    intent_ids: set[str] = set()
    intent_lines: set[tuple[str, str]] = set()
    for intent in intents:
        intent_id = str(intent.get("trade_intent_id") or "")
        if not intent_id or intent_id in intent_ids:
            errors.append("trade_intent_id_missing_or_duplicate")
        intent_ids.add(intent_id)
        if intent.get("action") != "BUY":
            errors.append(f"unsupported_trade_action:{intent_id}")
        shares = intent.get("shares_delta")
        if not isinstance(shares, int) or shares <= 0:
            errors.append(f"shares_not_positive_integer:{intent_id}")
        if f(intent.get("model_price_eur")) <= 0 or f(intent.get("trade_value_eur")) <= 0:
            errors.append(f"trade_value_invalid:{intent_id}")
        if intent.get("model_portfolio_only") is not True or intent.get("real_broker_execution") is not False:
            errors.append(f"intent_authority_invalid:{intent_id}")
        line = (str(intent.get("isin") or ""), str(intent.get("exchange_ticker") or ""))
        if not all(line) or line in intent_lines:
            errors.append(f"intent_identity_invalid_or_duplicate:{intent_id}")
        intent_lines.add(line)

    if allocation.get("trade_intent_count") != len(intents):
        errors.append("trade_intent_count_mismatch")
    status = allocation.get("status")
    if intents and status != "ready_for_guarded_model_activation":
        errors.append("ready_status_missing")
    if not intents and status != "review_complete_no_trade":
        errors.append("no_trade_status_invalid")
    if allocation.get("new_position_authorized") is not bool(intents):
        errors.append("new_position_authority_mismatch")

    row_lines = {
        (str(row.get("isin") or ""), str(row.get("exchange_ticker") or "")): row
        for row in rows
        if row.get("isin") and row.get("exchange_ticker")
    }
    for line in intent_lines:
        row = row_lines.get(line)
        if row is None:
            errors.append(f"intent_decision_row_missing:{line[1]}")
            continue
        if row.get("action") != "buy":
            errors.append(f"intent_row_action_mismatch:{line[1]}")
        if int(row.get("shares_delta") or 0) <= 0:
            errors.append(f"intent_row_shares_invalid:{line[1]}")

    broker_text = json.dumps(
        {
            "rows": [{"blockers": row.get("blockers") or []} for row in rows],
            "intents": intents,
        },
        sort_keys=True,
    ).lower()
    if "broker_account" in broker_text or "broker_permission_required" in broker_text:
        errors.append("broker_specific_model_blocker_present")

    minimum_cash = f((payload.get("policy") or {}).get("minimum_cash_reserve_eur"))
    projected_cash = f(allocation.get("cash_after_decision_eur"))
    if projected_cash + 0.01 < minimum_cash:
        errors.append("minimum_cash_reserve_breached")

    incumbent_count = len(payload.get("incumbent_reviews") or [])
    if incumbent_count == 0:
        warnings.append("no_incumbent_positions_reviewed")

    evidence = {
        "review_valid": not errors,
        "broker_neutral_model_authority_passed": not any("broker" in error for error in errors),
        "active_portfolio_revaluation_passed": not any("nav" in error for error in errors),
        "whole_share_contract_passed": not any("integer" in error for error in errors),
        "cash_policy_passed": not any("cash" in error for error in errors),
        "trade_intent_count": len(intents),
        "incumbent_review_count": incumbent_count,
        "ready_for_guarded_model_activation": status == "ready_for_guarded_model_activation" and not errors,
        "portfolio_mutation": False,
    }
    return errors, warnings, evidence


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    payload = json.loads(Path(args.review).read_text(encoding="utf-8"))
    errors, warnings, evidence = validate(payload)
    result = {
        "schema_version": "etf_eu_broker_neutral_allocation_review_validation_v1",
        "review": args.review,
        "passed": not errors,
        "errors": errors,
        "warnings": warnings,
        **evidence,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
