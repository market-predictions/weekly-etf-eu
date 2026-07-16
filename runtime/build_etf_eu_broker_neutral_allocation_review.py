from __future__ import annotations

import argparse
import json
import math
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import yaml


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected object in {path}")
    return value


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}


def f(value: Any, default: float = 0.0) -> float:
    try:
        return default if value in (None, "") else float(value)
    except (TypeError, ValueError):
        return default


def text(value: Any) -> str:
    return str(value or "").strip()


def iso_date(value: Any) -> date | None:
    try:
        return date.fromisoformat(text(value)[:10])
    except (TypeError, ValueError):
        return None


def price_index(payload: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for row in payload.get("rows") or []:
        if not isinstance(row, dict):
            continue
        key = (
            text(row.get("isin")).upper(),
            text(row.get("ticker") or row.get("exchange_ticker")).upper(),
        )
        if all(key):
            result[key] = dict(row)
    return result


def position_index(payload: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for row in payload.get("positions") or []:
        if not isinstance(row, dict):
            continue
        key = (
            text(row.get("isin")).upper(),
            text(row.get("exchange_ticker") or row.get("ticker")).upper(),
        )
        if all(key):
            result[key] = dict(row)
    return result


def price_eligibility(
    target: dict[str, Any],
    row: dict[str, Any] | None,
    activation: dict[str, Any],
    report_date: date,
) -> tuple[bool, list[str], float | None, str | None]:
    if row is None:
        return False, ["exact_isin_trading_line_price_row_missing"], None, None

    blockers: list[str] = []
    if text(row.get("instrument_type")) not in set(activation.get("accepted_instrument_types") or []):
        blockers.append("instrument_type_not_accepted")
    if text(row.get("verification_status")) not in set(activation.get("accepted_verification_statuses") or []):
        blockers.append("trading_line_not_verified")
    if text(row.get("pricing_status")) not in set(activation.get("accepted_pricing_statuses") or []):
        blockers.append("pricing_status_not_accepted")

    currency = text(row.get("currency") or target.get("trading_currency")).upper()
    accepted_currencies = {text(item).upper() for item in activation.get("cap01_currency_scope") or []}
    if currency not in accepted_currencies:
        blockers.append("currency_outside_model_scope")

    close = f(row.get("close_price"))
    if close <= 0:
        blockers.append("usable_close_missing")

    close_date = iso_date(row.get("close_date"))
    if close_date is None:
        blockers.append("close_date_missing")
    else:
        age = (report_date - close_date).days
        maximum = int(f(activation.get("max_price_age_days"), 3))
        if age < 0:
            blockers.append("close_after_report_date")
        elif age > maximum:
            blockers.append(f"close_too_old:{age}>{maximum}")

    if text(row.get("isin")).upper() != text(target.get("isin")).upper():
        blockers.append("isin_mismatch")
    row_ticker = text(row.get("ticker") or row.get("exchange_ticker")).upper()
    if row_ticker != text(target.get("exchange_ticker")).upper():
        blockers.append("trading_line_mismatch")

    if any("broker" in blocker.lower() for blocker in blockers):
        raise RuntimeError("Broker-specific blocker leaked into broker-neutral model review")

    return not blockers, blockers, close if close > 0 else None, text(row.get("close_date")) or None


def build_review(
    *,
    policy_path: Path,
    portfolio_state_path: Path,
    pricing_artifact_path: Path,
    run_id: str,
    report_date_raw: str,
    output_path: Path,
) -> dict[str, Any]:
    config = load_yaml(policy_path)
    state = load_json(portfolio_state_path)
    pricing = load_json(pricing_artifact_path)
    report_date = iso_date(report_date_raw)
    if report_date is None:
        raise RuntimeError("Invalid report date")

    activation = dict(config.get("activation") or {})
    if activation.get("broker_specific_permission_required_for_model") is not False:
        raise RuntimeError("Model allocation policy is not broker-neutral")

    cash = f(state.get("cash_eur"))
    if cash < 0:
        raise RuntimeError("Invalid portfolio cash")

    targets = [dict(row) for row in config.get("strategic_targets") or [] if isinstance(row, dict)]
    target_total = round(sum(f(row.get("target_weight_pct")) for row in targets), 8)
    prices = price_index(pricing)
    positions = position_index(state)
    target_by_key = {
        (text(row.get("isin")).upper(), text(row.get("exchange_ticker")).upper()): row
        for row in targets
        if text(row.get("isin")) and text(row.get("exchange_ticker")).upper() != "CASH"
    }

    revalued_positions: list[dict[str, Any]] = []
    incumbent_reviews: list[dict[str, Any]] = []
    revalued_invested = 0.0
    warnings: list[str] = []

    for key, position in positions.items():
        target = target_by_key.get(
            key,
            {
                "isin": key[0],
                "exchange_ticker": key[1],
                "trading_currency": position.get("trading_currency"),
            },
        )
        row = prices.get(key)
        eligible, blockers, close, close_date = price_eligibility(target, row, activation, report_date)
        retained_price = f(position.get("current_price_local"), f(position.get("avg_entry_local")))
        review_price = close if eligible and close else retained_price
        if not eligible:
            warnings.append(f"incumbent_price_retained:{key[1]}:{','.join(blockers)}")

        shares = int(math.floor(f(position.get("shares")) + 1e-9))
        market_value = round(shares * review_price, 6)
        entry_price = f(position.get("avg_entry_local"))
        unrealized = round((review_price - entry_price) * shares, 6)
        unrealized_pct = round((review_price / entry_price - 1.0) * 100.0, 6) if entry_price > 0 else 0.0
        revalued_invested = round(revalued_invested + market_value, 6)

        revalued_positions.append(
            {
                "isin": key[0],
                "exchange_ticker": key[1],
                "shares": shares,
                "review_price_eur": round(review_price, 6),
                "price_date": close_date if eligible else position.get("price_date"),
                "market_value_eur": market_value,
                "price_status": "fresh_exact_line_close" if eligible else "retained_prior_validated_close",
                "blockers": blockers,
            }
        )
        incumbent_reviews.append(
            {
                "isin": key[0],
                "exchange_ticker": key[1],
                "shares": shares,
                "entry_price_eur": round(entry_price, 6),
                "review_price_eur": round(review_price, 6),
                "price_date": close_date if eligible else position.get("price_date"),
                "market_value_eur": market_value,
                "unrealized_pnl_eur": unrealized,
                "unrealized_pnl_pct": unrealized_pct,
                "action_code": "hold",
                "trade_intent": None,
                "reason_codes": (
                    ["fresh_exact_line_close_obtained", "existing_position_revalued", "no_automatic_second_tranche"]
                    if eligible
                    else ["prior_validated_close_retained", "no_automatic_second_tranche"]
                ),
                "second_tranche_authorized": False,
            }
        )

    revalued_nav = round(cash + revalued_invested, 6)
    prior_nav = f(state.get("nav_eur"), cash + f(state.get("invested_market_value_eur")))
    if revalued_nav <= 0:
        raise RuntimeError("Invalid revalued NAV")

    phase_fraction = f(activation.get("phase_fraction"), 1.0)
    minimum_cash_pct = f(activation.get("minimum_cash_reserve_pct"))
    minimum_cash_eur = round(revalued_nav * minimum_cash_pct / 100.0, 6)
    remaining_cash = cash
    trade_intents: list[dict[str, Any]] = []
    decision_rows: list[dict[str, Any]] = []

    for target in sorted(targets, key=lambda row: int(f(row.get("priority"), 999))):
        ticker = text(target.get("exchange_ticker")).upper()
        strategic_weight = f(target.get("target_weight_pct"))
        if ticker == "CASH":
            decision_rows.append(
                {
                    "allocation_id": target.get("allocation_id"),
                    "portfolio_role": target.get("portfolio_role"),
                    "exchange_ticker": "CASH",
                    "strategic_target_weight_pct": strategic_weight,
                    "phase_target_weight_pct": strategic_weight,
                    "eligibility_status": "cash_reserve",
                    "action": "retain_cash",
                    "shares_delta": 0,
                    "trade_value_eur": 0.0,
                    "blockers": [],
                    "reason_codes": ["strategic_cash_reserve", "whole_share_residual_cash"],
                }
            )
            continue

        isin = text(target.get("isin")).upper()
        key = (isin, ticker)
        row = prices.get(key)
        eligible, blockers, close, close_date = price_eligibility(target, row, activation, report_date)
        current = positions.get(key, {})
        current_shares = int(math.floor(f(current.get("shares")) + 1e-9))
        current_revalued = next(
            (
                item
                for item in revalued_positions
                if item["isin"] == isin and item["exchange_ticker"] == ticker
            ),
            None,
        )
        current_value = f((current_revalued or {}).get("market_value_eur"))
        phase_weight = round(strategic_weight * phase_fraction, 6)
        phase_value = round(revalued_nav * phase_weight / 100.0, 6)
        target_shares = math.floor(phase_value / close) if eligible and close else current_shares
        raw_delta = target_shares - current_shares
        shares_delta = 0
        action = "blocked"
        trade_value = 0.0
        reason_codes = [
            "broker_permission_not_required_for_model",
            "whole_shares_only",
            "blocked_capacity_not_reallocated",
        ]

        if eligible and raw_delta > 0 and current_shares > 0:
            blockers = blockers + ["second_tranche_requires_separate_signal_authorization"]
            action = "hold_existing"
            reason_codes += ["existing_position", "no_automatic_second_tranche"]
        elif eligible and raw_delta > 0:
            candidate_trade = round(raw_delta * (close or 0.0), 6)
            if remaining_cash - candidate_trade < minimum_cash_eur - 0.01:
                blockers = blockers + ["minimum_cash_reserve_breached"]
                action = "blocked"
            else:
                shares_delta = raw_delta
                trade_value = candidate_trade
                remaining_cash = round(remaining_cash - trade_value, 6)
                action = "buy"
                reason_codes += ["fresh_exact_line_close_obtained", "new_position_first_tranche"]
                trade_intents.append(
                    {
                        "trade_intent_id": f"model-eu-review-{run_id}-{ticker}-BUY",
                        "action": "BUY",
                        "isin": isin,
                        "exchange_ticker": ticker,
                        "exchange": target.get("primary_exchange"),
                        "trading_currency": target.get("trading_currency"),
                        "shares_delta": shares_delta,
                        "model_price_eur": round(close or 0.0, 6),
                        "price_date": close_date,
                        "trade_value_eur": trade_value,
                        "portfolio_role": target.get("portfolio_role"),
                        "phase_target_weight_pct": phase_weight,
                        "model_portfolio_only": True,
                        "real_broker_execution": False,
                    }
                )
        elif eligible and raw_delta == 0:
            action = "hold_existing" if current_shares > 0 else "no_trade_whole_share_rounding"
            reason_codes += ["phase_target_satisfied_or_rounding_residual"]
        elif eligible and raw_delta < 0:
            action = "hold_pending_reduce_review"
            blockers = blockers + ["automatic_reduction_not_authorized"]
            reason_codes += ["separate_reduce_or_exit_review_required"]

        projected_value = round(current_value + trade_value, 6)
        decision_rows.append(
            {
                "priority": target.get("priority"),
                "allocation_id": target.get("allocation_id"),
                "portfolio_role": target.get("portfolio_role"),
                "isin": isin,
                "exchange_ticker": ticker,
                "fund_name": target.get("fund_name"),
                "provider": target.get("provider"),
                "primary_exchange": target.get("primary_exchange"),
                "trading_currency": target.get("trading_currency"),
                "strategic_target_weight_pct": strategic_weight,
                "phase_target_weight_pct": phase_weight,
                "phase_target_value_eur": phase_value,
                "current_shares": current_shares,
                "target_whole_shares": target_shares,
                "raw_shares_delta": raw_delta,
                "shares_delta": shares_delta,
                "close_price_eur": round(close, 6) if close else None,
                "close_date": close_date,
                "pricing_status": row.get("pricing_status") if row else None,
                "verification_status": row.get("verification_status") if row else None,
                "trade_value_eur": trade_value,
                "projected_market_value_eur": projected_value,
                "projected_weight_pct": round(projected_value / revalued_nav * 100.0, 6),
                "eligibility_status": (
                    "eligible_trade_intent"
                    if action == "buy"
                    else "eligible_no_trade"
                    if eligible
                    else "blocked"
                ),
                "action": action,
                "blockers": blockers,
                "reason_codes": reason_codes,
            }
        )

    new_trade_value = round(sum(f(row.get("trade_value_eur")) for row in trade_intents), 6)
    projected_invested = round(revalued_invested + new_trade_value, 6)
    projected_nav = round(remaining_cash + projected_invested, 6)
    hard_blockers: list[str] = []
    if abs(target_total - 100.0) > 0.0001:
        hard_blockers.append(f"strategic_targets_not_100:{target_total}")
    if abs(projected_nav - revalued_nav) > 0.01:
        hard_blockers.append(f"projected_nav_drift:{projected_nav}!={revalued_nav}")

    status = (
        "ready_for_guarded_model_activation"
        if trade_intents and not hard_blockers
        else "review_complete_no_trade"
        if not hard_blockers
        else "blocked"
    )
    payload = {
        "schema_version": "etf_eu_broker_neutral_allocation_review_v1",
        "artifact_type": "etf_eu_broker_neutral_allocation_review",
        "generated_at_utc": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "run_id": run_id,
        "report_date": report_date_raw,
        "source_files": {
            "target_allocation": str(policy_path),
            "portfolio_state": str(portfolio_state_path),
            "pricing_artifact": str(pricing_artifact_path),
        },
        "authority": {
            "model_portfolio_only": True,
            "real_broker_execution": False,
            "portfolio_mutation": False,
            "production_delivery_authority": False,
            "broker_specific_permission_required_for_model": False,
            "broker_permission_required_for_real_execution": True,
            "whole_shares_only": True,
            "blocked_capacity_reallocated": False,
        },
        "policy": {
            "allocation_style": config.get("allocation_style"),
            "phase_id": activation.get("phase_id"),
            "phase_fraction": phase_fraction,
            "minimum_cash_reserve_pct": minimum_cash_pct,
            "minimum_cash_reserve_eur": minimum_cash_eur,
            "strategic_target_weight_total_pct": target_total,
        },
        "portfolio_revaluation": {
            "prior_nav_eur": round(prior_nav, 6),
            "cash_eur": round(cash, 6),
            "invested_market_value_eur": round(revalued_invested, 6),
            "nav_eur": round(revalued_nav, 6),
            "nav_change_eur": round(revalued_nav - prior_nav, 6),
            "positions": revalued_positions,
        },
        "incumbent_reviews": incumbent_reviews,
        "decision_rows": decision_rows,
        "trade_intents": trade_intents,
        "allocation_decision": {
            "status": status,
            "portfolio_action": (
                "add_verified_first_tranches_from_cash" if trade_intents else "hold_and_retain_cash"
            ),
            "trade_intent_count": len(trade_intents),
            "new_position_authorized": bool(trade_intents),
            "second_tranche_authorized": False,
            "portfolio_mutation": False,
            "cash_after_decision_eur": round(remaining_cash, 6),
            "invested_after_decision_eur": projected_invested,
            "nav_after_decision_eur": projected_nav,
            "nav_reconciliation_ok": abs(projected_nav - revalued_nav) <= 0.01,
        },
        "hard_blockers": hard_blockers,
        "warnings": warnings
        + [
            "Public completed-close observations support only the repository model review, not real brokerage execution.",
            "Broker-specific account permission remains outside the model-investability gate.",
            "Blocked strategic capacity remains cash and is not redistributed.",
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", default="config/etf_eu_target_allocation.yml")
    parser.add_argument("--portfolio-state", default="output/etf_eu_portfolio_state.json")
    parser.add_argument("--pricing-artifact", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    payload = build_review(
        policy_path=Path(args.policy),
        portfolio_state_path=Path(args.portfolio_state),
        pricing_artifact_path=Path(args.pricing_artifact),
        run_id=args.run_id,
        report_date_raw=args.report_date,
        output_path=Path(args.output),
    )
    print(
        json.dumps(
            {
                "status": payload["allocation_decision"]["status"],
                "trade_intent_count": len(payload["trade_intents"]),
                "hard_blockers": payload["hard_blockers"],
            },
            indent=2,
        )
    )
    if payload["hard_blockers"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
