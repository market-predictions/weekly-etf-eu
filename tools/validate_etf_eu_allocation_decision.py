from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def f(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def validate(payload: dict[str, Any]) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    authority = payload.get("authority") or {}
    policy = payload.get("policy") or {}
    summary = payload.get("summary") or {}
    decisions = payload.get("decisions") or []
    if payload.get("schema_version") != "etf_eu_allocation_decision_v1":
        errors.append("schema_version_invalid")
    if payload.get("allocation_status") != "ready_for_guarded_model_activation":
        errors.append("allocation_not_ready")
    if payload.get("hard_blockers"):
        errors.append("hard_blockers_present")
    expected = {"model_portfolio_only": True, "real_broker_execution": False, "whole_shares_only": True, "blocked_capacity_reallocated": False}
    for key, value in expected.items():
        if authority.get(key) is not value:
            errors.append(f"authority_invalid:{key}")
    if abs(f(policy.get("strategic_target_weight_total_pct")) - 100.0) > 0.0001:
        errors.append("strategic_targets_not_100")
    if summary.get("blocked_target_capacity_retained_as_cash") is not True:
        errors.append("blocked_capacity_not_retained_as_cash")
    if summary.get("nav_reconciliation_ok") is not True:
        errors.append("nav_reconciliation_not_true")
    minimum_cash = f(policy.get("minimum_cash_reserve_eur"))
    projected_cash = f(summary.get("projected_cash_eur"))
    if projected_cash + 0.01 < minimum_cash:
        errors.append("minimum_cash_reserve_breached")

    executable = [row for row in decisions if row.get("action") == "buy"]
    if not executable:
        errors.append("no_executable_buy")
    seen_isins: set[str] = set()
    seen_lines: set[tuple[str, str]] = set()
    for row in executable:
        shares = row.get("shares_delta")
        if not isinstance(shares, int) or shares <= 0:
            errors.append(f"shares_not_positive_integer:{row.get('exchange_ticker')}")
        if row.get("verification_status") != "verified_ucits_trading_line":
            errors.append(f"line_not_verified:{row.get('exchange_ticker')}")
        if row.get("pricing_status") != "priced_non_authoritative":
            errors.append(f"price_status_invalid:{row.get('exchange_ticker')}")
        if row.get("trading_currency") != "EUR":
            errors.append(f"currency_not_eur:{row.get('exchange_ticker')}")
        isin = str(row.get("isin") or "")
        line = (isin, str(row.get("exchange_ticker") or ""))
        if not all(line):
            errors.append("identity_incomplete")
        if isin in seen_isins:
            errors.append(f"duplicate_executable_isin:{isin}")
        if line in seen_lines:
            errors.append(f"duplicate_executable_line:{line[1]}")
        seen_isins.add(isin)
        seen_lines.add(line)
    buy_total = round(sum(f(row.get("trade_value_eur")) for row in executable), 2)
    if abs(buy_total - f(summary.get("executable_trade_value_eur"))) > 0.01:
        errors.append("trade_total_mismatch")
    pre = payload.get("pre_activation_portfolio") or {}
    if abs(round(f(pre.get("cash_eur")) - buy_total, 2) - projected_cash) > 0.01:
        errors.append("projected_cash_mismatch")
    if abs(f(summary.get("projected_nav_eur")) - f(pre.get("nav_eur"))) > 0.01:
        errors.append("projected_nav_drift")
    blocked = [row for row in decisions if row.get("eligibility_status") == "blocked"]
    for row in blocked:
        if f(row.get("trade_value_eur")) != 0.0 or int(row.get("shares_delta") or 0) != 0:
            errors.append(f"blocked_row_has_trade:{row.get('exchange_ticker')}")
    if blocked:
        warnings.append(f"blocked_targets_present:{len(blocked)}")
    evidence = {
        "allocation_decision_valid": not errors,
        "executable_position_count": len(executable),
        "blocked_target_count": len(blocked),
        "whole_share_contract_passed": not any("integer" in error for error in errors),
        "cash_reconciliation_passed": not any("cash" in error or "nav" in error for error in errors),
        "exact_line_identity_passed": not any("identity" in error or "duplicate" in error or "verified" in error for error in errors),
        "model_only_authority_passed": not any("authority" in error for error in errors),
    }
    return errors, warnings, evidence


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decision", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    payload = load(Path(args.decision))
    errors, warnings, evidence = validate(payload)
    result = {"schema_version": "etf_eu_allocation_decision_validation_v1", "decision": args.decision, "passed": not errors, "errors": errors, "warnings": warnings, **evidence}
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
