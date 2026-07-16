from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LEDGER_FIELDS = [
    "trade_id", "trade_date", "source_report", "isin", "exchange_ticker", "action",
    "shares_delta", "previous_weight_pct", "new_weight_pct", "weight_change_pct",
    "target_weight_pct", "conviction_tier", "portfolio_role", "funding_source_note",
]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def f(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def key(row: dict[str, Any]) -> tuple[str, str]:
    return (str(row.get("isin") or "").strip().upper(), str(row.get("exchange_ticker") or row.get("ticker") or "").strip().upper())


def read_ledger(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def write_ledger(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LEDGER_FIELDS)
        writer.writeheader()
        writer.writerows({name: row.get(name, "") for name in LEDGER_FIELDS} for row in rows)


def apply(*, decision_path: Path, validation_path: Path, portfolio_state_path: Path, trade_ledger_path: Path, confirmation: str, output_path: Path) -> dict[str, Any]:
    decision = load(decision_path)
    validation = load(validation_path)
    state = load(portfolio_state_path)
    if confirmation != "CONFIRM_ETF_EU_MODEL_CAPITAL_ACTIVATION":
        raise RuntimeError("ETF_EU_MODEL_CAPITAL_ACTIVATION_CONFIRMATION_MISSING")
    if validation.get("passed") is not True or validation.get("allocation_decision_valid") is not True:
        raise RuntimeError("ETF_EU_ALLOCATION_DECISION_VALIDATION_NOT_PASSED")
    if decision.get("allocation_status") != "ready_for_guarded_model_activation":
        raise RuntimeError("ETF_EU_ALLOCATION_DECISION_NOT_READY")
    authority = decision.get("authority") or {}
    if authority.get("model_portfolio_only") is not True or authority.get("real_broker_execution") is not False:
        raise RuntimeError("ETF_EU_MODEL_ONLY_AUTHORITY_INVALID")
    activation_id = str(decision.get("activation_id") or "")
    if (state.get("last_model_capital_activation") or {}).get("activation_id") == activation_id:
        result = {
            "schema_version": "etf_eu_guarded_capital_activation_result_v1", "activation_id": activation_id,
            "status": "already_applied", "portfolio_state_written": False, "trade_ledger_written": False,
            "model_portfolio_only": True, "real_broker_execution": False,
            "portfolio_state": str(portfolio_state_path), "trade_ledger": str(trade_ledger_path),
            "post_activation_portfolio": {"cash_eur": state.get("cash_eur"), "invested_market_value_eur": state.get("invested_market_value_eur"), "nav_eur": state.get("nav_eur"), "position_count": len(state.get("positions") or [])},
            "ledger_rows_appended": [],
        }
        write(output_path, result)
        return result

    positions = {key(row): dict(row) for row in state.get("positions") or [] if isinstance(row, dict)}
    pre_nav = f(state.get("nav_eur")) or (f(state.get("cash_eur")) + f(state.get("invested_market_value_eur")))
    cash = f(state.get("cash_eur"))
    appended: list[dict[str, Any]] = []
    trade_date = str(decision.get("report_date") or "")
    for index, row in enumerate(decision.get("decisions") or [], start=1):
        if row.get("action") != "buy" or int(row.get("shares_delta") or 0) <= 0:
            continue
        position_key = key(row)
        current = positions.get(position_key, {})
        old_shares = int(f(current.get("shares")))
        old_value = f(current.get("market_value_eur"))
        old_weight = round(old_value / pre_nav * 100.0, 6) if pre_nav else 0.0
        delta = int(row.get("shares_delta") or 0)
        price = f(row.get("close_price_eur"))
        trade_value = round(delta * price, 2)
        if trade_value <= 0 or trade_value > cash + 0.01:
            raise RuntimeError(f"ETF_EU_CAPITAL_ACTIVATION_CASH_CHECK_FAILED:{row.get('exchange_ticker')}")
        shares = old_shares + delta
        market_value = round(shares * price, 2)
        cash = round(cash - trade_value, 2)
        metadata = dict(row.get("instrument_metadata") or {})
        position = {
            **current,
            "isin": row.get("isin"), "fund_name": row.get("fund_name"), "provider": row.get("provider"),
            "ucits_status": "confirmed", "priips_kid_status": "available", "investability_status": "funded_model_position",
            "primary_exchange": row.get("primary_exchange"), "exchange_ticker": row.get("exchange_ticker"), "ticker": row.get("exchange_ticker"),
            "trading_currency": "EUR", "base_currency": "USD", "shares": shares,
            "avg_entry_local": round((old_value + trade_value) / shares, 6), "current_price_local": price, "previous_price_local": price,
            "market_value_local": market_value, "previous_market_value_local": market_value, "market_value_eur": market_value, "previous_market_value_eur": market_value,
            "portfolio_role": row.get("portfolio_role"), "conviction_tier": row.get("conviction_tier"),
            "strategic_target_weight_pct": row.get("strategic_target_weight_pct"), "phase_target_weight_pct": row.get("phase_target_weight_pct"), "target_weight_pct": row.get("phase_target_weight_pct"),
            "price_date": row.get("close_date"), "pricing_status": row.get("pricing_status"), "verification_status": row.get("verification_status"),
            "model_execution_price_basis": row.get("model_execution_price_basis"), "model_portfolio_only": True, "real_broker_execution": False,
            "source_run_id": decision.get("run_id"), "last_action": "Buy", "shares_delta_this_run": delta, "action_executed_this_run": "Model buy",
            **metadata,
        }
        positions[position_key] = position
        new_weight = round(market_value / pre_nav * 100.0, 6) if pre_nav else 0.0
        appended.append({
            "trade_id": f"model-eu-{trade_date}-{decision.get('run_id')}-{index:02d}-{row.get('exchange_ticker')}-BUY",
            "trade_date": trade_date, "source_report": f"allocation:{decision_path.name}", "isin": row.get("isin"), "exchange_ticker": row.get("exchange_ticker"),
            "action": "Buy", "shares_delta": str(delta), "previous_weight_pct": f"{old_weight:.6f}", "new_weight_pct": f"{new_weight:.6f}",
            "weight_change_pct": f"{new_weight - old_weight:.6f}", "target_weight_pct": f"{f(row.get('phase_target_weight_pct')):.6f}",
            "conviction_tier": row.get("conviction_tier") or "", "portfolio_role": row.get("portfolio_role") or "",
            "funding_source_note": "Guarded Weekly ETF EU model activation funded from cash; no real broker order was placed.",
        })

    official_positions = sorted(positions.values(), key=lambda row: (str(row.get("portfolio_role") or ""), str(row.get("exchange_ticker") or "")))
    invested = round(sum(f(row.get("market_value_eur")) for row in official_positions), 2)
    nav = round(cash + invested, 2)
    if abs(nav - pre_nav) > 0.01:
        raise RuntimeError(f"ETF_EU_CAPITAL_ACTIVATION_NAV_DRIFT:{nav}!={pre_nav}")
    for row in official_positions:
        weight = round(f(row.get("market_value_eur")) / nav * 100.0, 6) if nav else 0.0
        row["current_weight_pct"] = weight
        row["previous_weight_pct"] = weight
        row["weight_inherited_pct"] = weight
    state.update({
        "schema_version": "etf_eu_portfolio_state_v2", "portfolio_mode": "dutch_eu_ucits_model_active", "base_currency": "EUR",
        "valuation_source": "guarded_model_capital_activation_v1", "cash_eur": cash, "invested_market_value_eur": invested, "nav_eur": nav,
        "positions": official_positions, "model_portfolio_only": True, "real_broker_execution": False,
        "last_model_capital_activation": {"activation_id": activation_id, "run_id": decision.get("run_id"), "report_date": trade_date, "decision": str(decision_path), "validation": str(validation_path), "trade_count": len(appended), "applied_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")},
        "notes": ["Repository model portfolio only; no real brokerage order was placed.", "Blocked strategic target capacity remains cash.", "U.S.-listed ETFs remain research proxies only."],
    })
    existing = read_ledger(trade_ledger_path)
    ids = {row.get("trade_id") for row in existing}
    rows_to_append = [row for row in appended if row.get("trade_id") not in ids]
    write_ledger(trade_ledger_path, existing + rows_to_append)
    write(portfolio_state_path, state)
    result = {
        "schema_version": "etf_eu_guarded_capital_activation_result_v1", "activation_id": activation_id, "status": "applied",
        "portfolio_state_written": True, "trade_ledger_written": True, "model_portfolio_only": True, "real_broker_execution": False,
        "portfolio_state": str(portfolio_state_path), "trade_ledger": str(trade_ledger_path),
        "post_activation_portfolio": {"cash_eur": cash, "invested_market_value_eur": invested, "nav_eur": nav, "position_count": len(official_positions)},
        "ledger_rows_appended": rows_to_append,
    }
    write(output_path, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decision", required=True)
    parser.add_argument("--validation", required=True)
    parser.add_argument("--portfolio-state", default="output/etf_eu_portfolio_state.json")
    parser.add_argument("--trade-ledger", default="output/etf_eu_trade_ledger.csv")
    parser.add_argument("--confirmation", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = apply(decision_path=Path(args.decision), validation_path=Path(args.validation), portfolio_state_path=Path(args.portfolio_state), trade_ledger_path=Path(args.trade_ledger), confirmation=args.confirmation, output_path=Path(args.output))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
