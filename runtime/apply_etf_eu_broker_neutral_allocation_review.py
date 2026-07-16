from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

LEDGER_FIELDS = [
    "trade_id",
    "trade_date",
    "source_report",
    "isin",
    "exchange_ticker",
    "action",
    "shares_delta",
    "previous_weight_pct",
    "new_weight_pct",
    "weight_change_pct",
    "target_weight_pct",
    "conviction_tier",
    "portfolio_role",
    "funding_source_note",
]
CONFIRMATION = "CONFIRM_ETF_EU_BROKER_NEUTRAL_MODEL_ACTIVATION"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return value


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def f(value: Any, default: float = 0.0) -> float:
    try:
        return default if value in (None, "") else float(value)
    except (TypeError, ValueError):
        return default


def position_key(row: dict[str, Any]) -> tuple[str, str]:
    return (
        str(row.get("isin") or "").strip().upper(),
        str(row.get("exchange_ticker") or row.get("ticker") or "").strip().upper(),
    )


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
        writer.writerows({field: row.get(field, "") for field in LEDGER_FIELDS} for row in rows)


def apply_review(
    *,
    review_path: Path,
    validation_path: Path,
    portfolio_state_path: Path,
    trade_ledger_path: Path,
    policy_path: Path,
    confirmation: str,
    output_path: Path,
) -> dict[str, Any]:
    if confirmation != CONFIRMATION:
        raise RuntimeError("ETF_EU_BROKER_NEUTRAL_MODEL_ACTIVATION_CONFIRMATION_MISSING")

    review = load_json(review_path)
    validation = load_json(validation_path)
    state = load_json(portfolio_state_path)
    policy = load_yaml(policy_path)

    if validation.get("passed") is not True or validation.get("ready_for_guarded_model_activation") is not True:
        raise RuntimeError("ETF_EU_BROKER_NEUTRAL_REVIEW_VALIDATION_NOT_PASSED")
    allocation = review.get("allocation_decision") or {}
    if allocation.get("status") != "ready_for_guarded_model_activation":
        raise RuntimeError("ETF_EU_BROKER_NEUTRAL_REVIEW_NOT_READY")

    authority = review.get("authority") or {}
    expected_authority = {
        "model_portfolio_only": True,
        "real_broker_execution": False,
        "portfolio_mutation": False,
        "broker_specific_permission_required_for_model": False,
        "broker_permission_required_for_real_execution": True,
    }
    for key, expected in expected_authority.items():
        if authority.get(key) is not expected:
            raise RuntimeError(f"ETF_EU_BROKER_NEUTRAL_AUTHORITY_INVALID:{key}")

    run_id = str(review.get("run_id") or "")
    report_date = str(review.get("report_date") or "")
    activation_id = f"ETF-EU-BROKER-NEUTRAL-{run_id}"
    previous_activation = state.get("last_model_capital_activation") or {}
    if previous_activation.get("activation_id") == activation_id:
        result = {
            "schema_version": "etf_eu_broker_neutral_model_activation_result_v1",
            "activation_id": activation_id,
            "run_id": run_id,
            "status": "already_applied",
            "portfolio_state_written": False,
            "trade_ledger_written": False,
            "model_portfolio_only": True,
            "real_broker_execution": False,
            "portfolio_state": str(portfolio_state_path),
            "trade_ledger": str(trade_ledger_path),
            "post_activation_portfolio": {
                "cash_eur": state.get("cash_eur"),
                "invested_market_value_eur": state.get("invested_market_value_eur"),
                "nav_eur": state.get("nav_eur"),
                "position_count": len(state.get("positions") or []),
            },
            "ledger_rows_appended": [],
        }
        write_json(output_path, result)
        return result

    targets = {
        position_key(row): dict(row)
        for row in policy.get("strategic_targets") or []
        if isinstance(row, dict) and row.get("isin") and row.get("exchange_ticker") != "CASH"
    }
    positions = {
        position_key(row): dict(row)
        for row in state.get("positions") or []
        if isinstance(row, dict)
    }

    revaluation = review.get("portfolio_revaluation") or {}
    revaluation_rows = {
        position_key(row): dict(row)
        for row in revaluation.get("positions") or []
        if isinstance(row, dict)
    }
    pre_nav = round(f(revaluation.get("nav_eur")), 2)
    cash = round(f(state.get("cash_eur")), 2)
    if pre_nav <= 0 or cash < 0:
        raise RuntimeError("ETF_EU_BROKER_NEUTRAL_PRE_ACTIVATION_STATE_INVALID")

    for key, current in list(positions.items()):
        row = revaluation_rows.get(key)
        if row is None:
            raise RuntimeError(f"ETF_EU_INCUMBENT_REVALUATION_MISSING:{key[1]}")
        shares = int(f(current.get("shares")))
        price = f(row.get("review_price_eur"))
        if shares <= 0 or price <= 0:
            raise RuntimeError(f"ETF_EU_INCUMBENT_REVALUATION_INVALID:{key[1]}")

        previous_price = f(current.get("current_price_local"), f(current.get("avg_entry_local")))
        previous_value = f(current.get("market_value_eur"), shares * previous_price)
        market_value = round(shares * price, 2)
        avg_entry = f(current.get("avg_entry_local"))
        current.update(
            {
                "previous_price_local": previous_price,
                "current_price_local": price,
                "previous_market_value_local": round(previous_value, 2),
                "previous_market_value_eur": round(previous_value, 2),
                "market_value_local": market_value,
                "market_value_eur": market_value,
                "price_date": row.get("price_date"),
                "pricing_status": "priced_non_authoritative",
                "verification_status": "verified_ucits_trading_line",
                "model_execution_price_basis": "fresh_exact_line_completed_close_model_only",
                "unrealized_pnl_eur": round((price - avg_entry) * shares, 2),
                "unrealized_pnl_pct": round((price / avg_entry - 1.0) * 100.0, 6) if avg_entry > 0 else 0.0,
                "portfolio_contribution_eur": round(market_value - previous_value, 2),
                "portfolio_contribution_pct_nav": round((market_value - previous_value) / pre_nav * 100.0, 6),
                "last_action": "Hold",
                "shares_delta_this_run": 0,
                "action_executed_this_run": "Revalue and hold",
                "review_run_id": run_id,
                "second_tranche_authorized": False,
            }
        )
        positions[key] = current

    decision_rows = {
        position_key(row): dict(row)
        for row in review.get("decision_rows") or []
        if isinstance(row, dict) and row.get("isin") and row.get("exchange_ticker")
    }
    existing_ledger = read_ledger(trade_ledger_path)
    existing_ids = {row.get("trade_id") for row in existing_ledger}
    appended: list[dict[str, Any]] = []

    minimum_cash = round(f((review.get("policy") or {}).get("minimum_cash_reserve_eur")), 2)
    for index, intent in enumerate(review.get("trade_intents") or [], start=1):
        if intent.get("action") != "BUY" or int(intent.get("shares_delta") or 0) <= 0:
            raise RuntimeError("ETF_EU_UNSUPPORTED_OR_EMPTY_TRADE_INTENT")
        if intent.get("model_portfolio_only") is not True or intent.get("real_broker_execution") is not False:
            raise RuntimeError("ETF_EU_TRADE_INTENT_AUTHORITY_INVALID")

        key = position_key(intent)
        decision_row = decision_rows.get(key)
        target = targets.get(key)
        if decision_row is None or target is None:
            raise RuntimeError(f"ETF_EU_TRADE_INTENT_METADATA_MISSING:{key[1]}")
        if decision_row.get("action") != "buy" or decision_row.get("verification_status") != "verified_ucits_trading_line":
            raise RuntimeError(f"ETF_EU_TRADE_INTENT_DECISION_ROW_INVALID:{key[1]}")

        current = positions.get(key, {})
        old_shares = int(f(current.get("shares")))
        old_value = f(current.get("market_value_eur"))
        if old_shares != 0:
            raise RuntimeError(f"ETF_EU_NEW_POSITION_EXPECTED:{key[1]}")

        delta = int(intent.get("shares_delta") or 0)
        price = f(intent.get("model_price_eur"))
        trade_value = round(delta * price, 2)
        if price <= 0 or trade_value <= 0:
            raise RuntimeError(f"ETF_EU_TRADE_VALUE_INVALID:{key[1]}")
        if cash - trade_value < minimum_cash - 0.01:
            raise RuntimeError(f"ETF_EU_MINIMUM_CASH_RESERVE_BREACHED:{key[1]}")

        cash = round(cash - trade_value, 2)
        shares = old_shares + delta
        market_value = round(shares * price, 2)
        position = {
            **current,
            "isin": intent.get("isin"),
            "fund_name": target.get("fund_name"),
            "provider": target.get("provider"),
            "ucits_status": "confirmed",
            "priips_kid_status": "available",
            "investability_status": "funded_model_position",
            "primary_exchange": intent.get("exchange"),
            "exchange_ticker": intent.get("exchange_ticker"),
            "ticker": intent.get("exchange_ticker"),
            "trading_currency": intent.get("trading_currency"),
            "base_currency": "USD",
            "shares": shares,
            "avg_entry_local": price,
            "current_price_local": price,
            "previous_price_local": price,
            "market_value_local": market_value,
            "previous_market_value_local": market_value,
            "market_value_eur": market_value,
            "previous_market_value_eur": market_value,
            "unrealized_pnl_eur": 0.0,
            "unrealized_pnl_pct": 0.0,
            "portfolio_contribution_eur": 0.0,
            "portfolio_contribution_pct_nav": 0.0,
            "portfolio_role": target.get("portfolio_role"),
            "conviction_tier": target.get("conviction_tier"),
            "strategic_target_weight_pct": target.get("target_weight_pct"),
            "phase_target_weight_pct": intent.get("phase_target_weight_pct"),
            "target_weight_pct": intent.get("phase_target_weight_pct"),
            "price_date": intent.get("price_date"),
            "pricing_status": "priced_non_authoritative",
            "verification_status": "verified_ucits_trading_line",
            "model_execution_price_basis": "fresh_exact_line_completed_close_model_only",
            "model_portfolio_only": True,
            "real_broker_execution": False,
            "source_run_id": run_id,
            "last_action": "Buy",
            "shares_delta_this_run": delta,
            "action_executed_this_run": "Broker-neutral model buy",
            "ter_pct": target.get("ter_pct"),
            "distribution_policy": target.get("distribution_policy"),
            "replication_method": target.get("replication_method"),
            "domicile": target.get("domicile"),
            "benchmark_index": target.get("benchmark_index"),
        }
        positions[key] = position

        old_weight = round(old_value / pre_nav * 100.0, 6) if pre_nav else 0.0
        new_weight = round(market_value / pre_nav * 100.0, 6) if pre_nav else 0.0
        trade_id = f"model-eu-{report_date}-{run_id}-{index:02d}-{key[1]}-BUY"
        ledger_row = {
            "trade_id": trade_id,
            "trade_date": report_date,
            "source_report": f"broker-neutral-review:{review_path.name}",
            "isin": key[0],
            "exchange_ticker": key[1],
            "action": "Buy",
            "shares_delta": str(delta),
            "previous_weight_pct": f"{old_weight:.6f}",
            "new_weight_pct": f"{new_weight:.6f}",
            "weight_change_pct": f"{new_weight - old_weight:.6f}",
            "target_weight_pct": f"{f(intent.get('phase_target_weight_pct')):.6f}",
            "conviction_tier": target.get("conviction_tier") or "",
            "portfolio_role": target.get("portfolio_role") or "",
            "funding_source_note": (
                "Guarded broker-neutral Weekly ETF EU model activation funded from cash; "
                "no real broker order was placed."
            ),
        }
        if trade_id not in existing_ids:
            appended.append(ledger_row)
            existing_ids.add(trade_id)

    official_positions = sorted(
        positions.values(),
        key=lambda row: (str(row.get("portfolio_role") or ""), str(row.get("exchange_ticker") or "")),
    )
    invested = round(sum(f(row.get("market_value_eur")) for row in official_positions), 2)
    nav = round(cash + invested, 2)
    if abs(nav - pre_nav) > 0.01:
        raise RuntimeError(f"ETF_EU_BROKER_NEUTRAL_ACTIVATION_NAV_DRIFT:{nav}!={pre_nav}")

    for row in official_positions:
        weight = round(f(row.get("market_value_eur")) / nav * 100.0, 6) if nav else 0.0
        row["current_weight_pct"] = weight
        row["previous_weight_pct"] = weight
        row["weight_inherited_pct"] = weight

    state.update(
        {
            "schema_version": "etf_eu_portfolio_state_v2",
            "portfolio_mode": "dutch_eu_ucits_model_active",
            "base_currency": "EUR",
            "valuation_source": "broker_neutral_guarded_model_activation",
            "cash_eur": cash,
            "invested_market_value_eur": invested,
            "nav_eur": nav,
            "positions": official_positions,
            "model_portfolio_only": True,
            "real_broker_execution": False,
            "last_model_capital_activation": {
                "activation_id": activation_id,
                "run_id": run_id,
                "report_date": report_date,
                "decision": str(review_path),
                "validation": str(validation_path),
                "trade_count": len(appended),
                "applied_at_utc": datetime.now(timezone.utc)
                .replace(microsecond=0)
                .isoformat()
                .replace("+00:00", "Z"),
            },
            "last_broker_neutral_allocation_activation": {
                "activation_id": activation_id,
                "run_id": run_id,
                "review": str(review_path),
                "validation": str(validation_path),
                "portfolio_mutation": True,
                "real_broker_execution": False,
            },
            "notes": [
                "Repository model portfolio only; no real brokerage order was placed.",
                "Broker-specific account permission was not used as a model-investability gate.",
                "Blocked strategic target capacity remains cash.",
                "U.S.-listed ETFs remain research proxies only.",
            ],
        }
    )

    write_ledger(trade_ledger_path, existing_ledger + appended)
    write_json(portfolio_state_path, state)
    result = {
        "schema_version": "etf_eu_broker_neutral_model_activation_result_v1",
        "activation_id": activation_id,
        "run_id": run_id,
        "report_date": report_date,
        "status": "applied",
        "portfolio_state_written": True,
        "trade_ledger_written": True,
        "model_portfolio_only": True,
        "real_broker_execution": False,
        "portfolio_state": str(portfolio_state_path),
        "trade_ledger": str(trade_ledger_path),
        "post_activation_portfolio": {
            "cash_eur": cash,
            "invested_market_value_eur": invested,
            "nav_eur": nav,
            "position_count": len(official_positions),
        },
        "ledger_rows_appended": appended,
    }
    write_json(output_path, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review", required=True)
    parser.add_argument("--validation", required=True)
    parser.add_argument("--portfolio-state", default="output/etf_eu_portfolio_state.json")
    parser.add_argument("--trade-ledger", default="output/etf_eu_trade_ledger.csv")
    parser.add_argument("--policy", default="config/etf_eu_target_allocation.yml")
    parser.add_argument("--confirmation", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = apply_review(
        review_path=Path(args.review),
        validation_path=Path(args.validation),
        portfolio_state_path=Path(args.portfolio_state),
        trade_ledger_path=Path(args.trade_ledger),
        policy_path=Path(args.policy),
        confirmation=args.confirmation,
        output_path=Path(args.output),
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
