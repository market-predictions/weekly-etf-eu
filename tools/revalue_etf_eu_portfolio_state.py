from __future__ import annotations

import argparse
import json
from copy import deepcopy
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Required input not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Input must be a JSON object: {path}")
    return payload


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _ticker(row: dict[str, Any]) -> str:
    return str(row.get("exchange_ticker") or row.get("ticker") or "").strip().upper()


def _price_index(pricing: dict[str, Any], report_date: date) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in pricing.get("rows") or []:
        if not isinstance(row, dict):
            continue
        ticker = str(row.get("ticker") or "").strip().upper()
        close_date_raw = str(row.get("close_date") or "")
        try:
            close_date = date.fromisoformat(close_date_raw)
            close_price = float(row.get("close_price"))
        except (TypeError, ValueError):
            continue
        if (
            ticker
            and row.get("pricing_status") == "priced_non_authoritative"
            and row.get("verification_status") == "verified_ucits_trading_line"
            and row.get("completed_close") is True
            and close_date < report_date
            and close_price > 0
        ):
            result[ticker] = row
    return result


def revalue_state(
    *,
    state: dict[str, Any],
    pricing: dict[str, Any],
    run_id: str,
    report_date: date,
) -> tuple[dict[str, Any], dict[str, Any]]:
    output = deepcopy(state)
    positions = output.get("positions")
    if not isinstance(positions, list) or not positions:
        raise RuntimeError("Portfolio state has no funded positions to revalue")
    prices = _price_index(pricing, report_date)
    blockers: list[str] = []
    revalued: list[dict[str, Any]] = []
    for raw in positions:
        if not isinstance(raw, dict):
            blockers.append("non_object_position")
            continue
        row = dict(raw)
        ticker = _ticker(row)
        price_row = prices.get(ticker)
        if price_row is None:
            blockers.append(f"missing_verified_completed_close:{ticker or 'UNKNOWN'}")
            continue
        if str(price_row.get("currency") or "").upper() != str(row.get("trading_currency") or "").upper():
            blockers.append(f"currency_mismatch:{ticker}")
            continue
        shares = float(row.get("shares") or 0)
        if shares <= 0:
            blockers.append(f"invalid_share_count:{ticker}")
            continue
        previous_price = float(row.get("current_price_local") or row.get("avg_entry_local") or 0)
        previous_value = float(row.get("market_value_eur") or shares * previous_price)
        current_price = float(price_row["close_price"])
        current_value = round(shares * current_price, 2)
        average_entry = float(row.get("avg_entry_local") or current_price)
        unrealized = round((current_price - average_entry) * shares, 2)
        unrealized_pct = ((current_price / average_entry) - 1.0) * 100.0 if average_entry else 0.0
        row.update(
            {
                "previous_price_local": previous_price,
                "previous_market_value_local": previous_value,
                "previous_market_value_eur": previous_value,
                "current_price_local": current_price,
                "market_value_local": current_value,
                "market_value_eur": current_value,
                "price_date": price_row["close_date"],
                "pricing_status": price_row["pricing_status"],
                "pricing_source": price_row.get("source_name"),
                "pricing_source_quality": price_row.get("source_quality_status"),
                "pricing_completed_close": True,
                "model_execution_price_basis": "latest_exact_line_completed_close_model_valuation_only",
                "unrealized_pnl_eur": unrealized,
                "unrealized_pnl_pct": round(unrealized_pct, 6),
                "portfolio_contribution_eur": round(current_value - previous_value, 2),
                "last_action": "Hold",
                "shares_delta_this_run": 0,
                "action_executed_this_run": "Routine revaluation and hold",
                "review_run_id": run_id,
                "last_valuation_run_id": run_id,
                "last_valuation_report_date": report_date.isoformat(),
            }
        )
        revalued.append(row)
    if blockers:
        raise RuntimeError("ETF_EU_REVALUATION_BLOCKED:" + ",".join(sorted(blockers)))

    cash = float(output.get("cash_eur") or 0)
    invested = round(sum(float(row["market_value_eur"]) for row in revalued), 2)
    nav = round(cash + invested, 2)
    if nav <= 0:
        raise RuntimeError("Revalued NAV must be positive")
    for row in revalued:
        old_weight = float(row.get("current_weight_pct") or 0)
        row["previous_weight_pct"] = old_weight
        row["current_weight_pct"] = round(float(row["market_value_eur"]) / nav * 100.0, 6)
        row["weight_inherited_pct"] = old_weight

    output["positions"] = revalued
    output["invested_market_value_eur"] = invested
    output["nav_eur"] = nav
    output["valuation_source"] = "latest_verified_exact_line_completed_close_model_valuation"
    output["last_valuation_run_id"] = run_id
    output["last_valuation_report_date"] = report_date.isoformat()
    output["last_valuation_at_utc"] = _utc_now()
    output["last_routine_position_review"] = {
        "run_id": run_id,
        "report_date": report_date.isoformat(),
        "portfolio_action": "revalue_and_hold",
        "trade_intent_count": 0,
        "portfolio_mutation": False,
        "second_tranche_authorized": False,
        "reviewed_at_utc": _utc_now(),
    }
    summary = {
        "schema_version": "etf_eu_portfolio_revaluation_v1",
        "artifact_type": "etf_eu_portfolio_revaluation",
        "run_id": run_id,
        "report_date": report_date.isoformat(),
        "position_count": len(revalued),
        "tickers": [_ticker(row) for row in revalued],
        "cash_eur": cash,
        "invested_market_value_eur": invested,
        "nav_eur": nav,
        "quantity_mutation": False,
        "portfolio_mutation": False,
        "real_broker_execution": False,
        "completed_close_gate_passed": True,
        "price_dates": { _ticker(row): row.get("price_date") for row in revalued },
        "generated_at_utc": _utc_now(),
    }
    return output, summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Revalue funded ETF EU model positions from verified exact-line completed closes.")
    parser.add_argument("--portfolio-state", default="output/etf_eu_portfolio_state.json")
    parser.add_argument("--pricing-artifact", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--output", default="output/etf_eu_portfolio_state.json")
    parser.add_argument("--evidence-output", required=True)
    args = parser.parse_args()
    state, evidence = revalue_state(
        state=_load(Path(args.portfolio_state)),
        pricing=_load(Path(args.pricing_artifact)),
        run_id=args.run_id,
        report_date=date.fromisoformat(args.report_date),
    )
    output = Path(args.output)
    evidence_output = Path(args.evidence_output)
    output.parent.mkdir(parents=True, exist_ok=True)
    evidence_output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(state, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    evidence_output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
