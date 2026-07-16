from __future__ import annotations

import argparse
import csv
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", required=True)
    parser.add_argument("--portfolio-state", required=True)
    parser.add_argument("--trade-ledger", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = load(Path(args.result))
    state = load(Path(args.portfolio_state))
    with Path(args.trade_ledger).open("r", encoding="utf-8", newline="") as handle:
        ledger = [dict(row) for row in csv.DictReader(handle)]
    errors: list[str] = []
    if result.get("status") not in {"applied", "already_applied"}:
        errors.append("activation_status_invalid")
    if result.get("model_portfolio_only") is not True or result.get("real_broker_execution") is not False:
        errors.append("result_authority_invalid")
    positions = state.get("positions") or []
    if not positions:
        errors.append("no_funded_model_position")
    if state.get("model_portfolio_only") is not True or state.get("real_broker_execution") is not False:
        errors.append("state_authority_invalid")
    cash = f(state.get("cash_eur"))
    invested = round(sum(f(row.get("market_value_eur")) for row in positions), 2)
    nav = f(state.get("nav_eur"))
    if abs(cash + invested - nav) > 0.01:
        errors.append("nav_reconciliation_failed")
    if abs(invested - f(state.get("invested_market_value_eur"))) > 0.01:
        errors.append("invested_reconciliation_failed")
    for row in positions:
        if not isinstance(row.get("shares"), int) or int(row.get("shares") or 0) <= 0:
            errors.append(f"position_not_whole_shares:{row.get('exchange_ticker')}")
        if not row.get("isin") or not row.get("exchange_ticker"):
            errors.append("position_identity_incomplete")
        if row.get("model_portfolio_only") is not True or row.get("real_broker_execution") is not False:
            errors.append(f"position_authority_invalid:{row.get('exchange_ticker')}")
    activation_id = result.get("activation_id")
    if (state.get("last_model_capital_activation") or {}).get("activation_id") != activation_id:
        errors.append("activation_id_not_persisted")
    appended_ids = {row.get("trade_id") for row in result.get("ledger_rows_appended") or []}
    ledger_ids = {row.get("trade_id") for row in ledger}
    if result.get("status") == "applied" and not appended_ids:
        errors.append("no_ledger_rows_appended")
    if not appended_ids.issubset(ledger_ids):
        errors.append("appended_trade_missing_from_ledger")
    payload = {
        "schema_version": "etf_eu_guarded_capital_activation_validation_v1", "passed": not errors, "errors": errors,
        "activation_id": activation_id, "position_count": len(positions), "cash_eur": cash, "invested_market_value_eur": invested, "nav_eur": nav,
        "whole_share_contract_passed": not any("whole_shares" in error for error in errors),
        "portfolio_reconciliation_passed": not any("reconciliation" in error for error in errors),
        "ledger_persistence_passed": not any("ledger" in error for error in errors),
        "model_only_authority_passed": not any("authority" in error for error in errors),
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
