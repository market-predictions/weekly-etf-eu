from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PRICED_STATUSES = {"fresh_close", "fresh_fallback_source", "fresh_exact_close", "fresh_exact_unverified", "prior_valid_close"}
DEFAULT_OUTPUT_DIR = Path("output/runtime")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def _text(value: Any, fallback: str = "") -> str:
    raw = str(value or "").strip()
    return raw or fallback


def _ticker(value: Any) -> str:
    return _text(value).upper()


def _float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(str(value).replace(",", "").replace("%", ""))
    except (TypeError, ValueError):
        return default


def _round(value: Any, digits: int = 2) -> float:
    return round(_float(value), digits)


def _pricing_map(runtime_state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {_ticker(row.get("symbol")): dict(row) for row in runtime_state.get("pricing", []) or [] if _ticker(row.get("symbol"))}


def _position_map(runtime_state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {_ticker(row.get("ticker")): dict(row) for row in runtime_state.get("positions", []) or [] if _ticker(row.get("ticker"))}


def _target_weights(runtime_state: dict[str, Any]) -> dict[str, float]:
    rows = runtime_state.get("target_weights") or (runtime_state.get("rotation_plan") or {}).get("target_weights") or []
    out: dict[str, float] = {}
    for row in rows:
        ticker = _ticker(row.get("ticker"))
        if ticker:
            out[ticker] = _float(row.get("target_weight_pct"))
    return out


def _trade_intents(runtime_state: dict[str, Any]) -> list[dict[str, Any]]:
    rows = runtime_state.get("trade_intents") or (runtime_state.get("rotation_plan") or {}).get("trade_intents") or []
    return [dict(row) for row in rows if isinstance(row, dict)]


def _policy(runtime_state: dict[str, Any]) -> dict[str, Any]:
    return dict((runtime_state.get("rotation_plan") or {}).get("policy") or {})


def _nav(runtime_state: dict[str, Any]) -> float:
    return _float((runtime_state.get("portfolio") or {}).get("total_portfolio_value_eur"))


def _fx(runtime_state: dict[str, Any]) -> float:
    return _float((runtime_state.get("fx_basis") or {}).get("rate"), 1.0) or 1.0


def _market_value_eur(row: dict[str, Any]) -> float:
    return _float(row.get("previous_market_value_eur") or row.get("market_value_eur"))


def _price_local(row: dict[str, Any], price_map: dict[str, dict[str, Any]]) -> float:
    ticker = _ticker(row.get("ticker") or row.get("symbol"))
    price_row = price_map.get(ticker, {})
    return _float(price_row.get("selected_close") or price_row.get("price") or row.get("current_price_local") or row.get("previous_price_local"))


def _currency(row: dict[str, Any], price_map: dict[str, dict[str, Any]]) -> str:
    ticker = _ticker(row.get("ticker") or row.get("symbol"))
    price_row = price_map.get(ticker, {})
    return _text(price_row.get("currency") or row.get("currency") or "USD").upper()


def _valid_price_row(ticker: str, price_map: dict[str, dict[str, Any]]) -> tuple[bool, str]:
    row = price_map.get(_ticker(ticker), {})
    if not row:
        return False, "missing_price_row"
    if _text(row.get("status")) not in PRICED_STATUSES:
        return False, f"invalid_price_status:{row.get('status')}"
    if row.get("selected_close") is None and row.get("price") is None:
        return False, "missing_selected_close"
    if _text(row.get("pricing_tier")) != "valuation_grade":
        return False, f"not_valuation_grade:{row.get('pricing_tier')}"
    return True, "ok"


def _validate_inputs(runtime_state: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    price_map = _pricing_map(runtime_state)
    position_map = _position_map(runtime_state)
    nav = _nav(runtime_state)
    policy = _policy(runtime_state)
    intents = _trade_intents(runtime_state)
    min_trade = _float(policy.get("min_trade_size_pct_nav"), 2.0)
    max_source_reduction = _float(policy.get("max_single_source_reduction_pct_nav"), 5.0)
    max_major = int(_float(policy.get("max_major_rotations_per_run"), 1.0))

    if nav <= 0:
        errors.append("runtime_nav_missing_or_non_positive")
    if not intents:
        warnings.append("no_trade_intents")
    if len(intents) > max_major:
        errors.append(f"major_rotation_count_exceeds_policy:{len(intents)}>{max_major}")

    for position in runtime_state.get("positions", []) or []:
        ticker = _ticker(position.get("ticker"))
        if not ticker:
            continue
        ok, reason = _valid_price_row(ticker, price_map)
        if not ok:
            errors.append(f"holding_price_invalid:{ticker}:{reason}")

    for intent in intents:
        source = _ticker(intent.get("source_ticker"))
        destination = _ticker(intent.get("destination_ticker"))
        source_delta = _float(intent.get("delta_weight_pct"))
        destination_delta = _float(intent.get("destination_delta_weight_pct"))
        if not source or not destination:
            errors.append("trade_intent_missing_source_or_destination")
            continue
        if source not in position_map:
            errors.append(f"source_not_in_portfolio:{source}")
        for ticker in (source, destination):
            ok, reason = _valid_price_row(ticker, price_map)
            if not ok:
                errors.append(f"trade_price_invalid:{ticker}:{reason}")
        if source_delta >= 0:
            errors.append(f"source_delta_not_negative:{source}:{source_delta}")
        if destination_delta <= 0:
            errors.append(f"destination_delta_not_positive:{destination}:{destination_delta}")
        if abs(abs(source_delta) - abs(destination_delta)) > 0.05:
            errors.append(f"source_destination_delta_mismatch:{source_delta}:{destination_delta}")
        if abs(source_delta) < min_trade:
            errors.append(f"trade_below_min_size:{source}:{abs(source_delta):.2f}<{min_trade:.2f}")
        if abs(source_delta) - max_source_reduction > 0.05:
            errors.append(f"source_reduction_exceeds_policy:{source}:{abs(source_delta):.2f}>{max_source_reduction:.2f}")
        action = _text(intent.get("action_code"))
        if action not in {"replace_partial", "replace_full", "reduce", "close", "add_from_cash"}:
            errors.append(f"unsupported_action_code:{action}")
    return errors, warnings


def _shares_for_notional(notional_eur: float, price_local: float, currency: str, fx: float) -> float:
    if price_local <= 0:
        return 0.0
    local_notional = notional_eur if currency == "EUR" else notional_eur * fx
    return local_notional / price_local


def _build_shadow_positions(runtime_state: dict[str, Any]) -> list[dict[str, Any]]:
    price_map = _pricing_map(runtime_state)
    positions = {ticker: dict(row) for ticker, row in _position_map(runtime_state).items()}
    fx = _fx(runtime_state)
    nav = _nav(runtime_state)
    target_weights = _target_weights(runtime_state)

    for intent in _trade_intents(runtime_state):
        source = _ticker(intent.get("source_ticker"))
        destination = _ticker(intent.get("destination_ticker"))
        if not source or not destination or source not in positions:
            continue
        notional = abs(_float(intent.get("estimated_notional_eur")))
        if notional <= 0 and nav > 0:
            notional = abs(_float(intent.get("delta_weight_pct"))) / 100.0 * nav
        source_row = positions[source]
        source_price = _price_local(source_row, price_map)
        source_currency = _currency(source_row, price_map)
        source_shares_delta = -_shares_for_notional(notional, source_price, source_currency, fx)
        source_shares = max(0.0, _float(source_row.get("shares")) + source_shares_delta)
        source_value_eur = max(0.0, _market_value_eur(source_row) - notional)
        source_row.update({
            "shares": round(source_shares, 6),
            "market_value_eur": round(source_value_eur, 2),
            "previous_market_value_eur": round(source_value_eur, 2),
            "current_weight_pct": round(source_value_eur / nav * 100.0, 2) if nav else 0.0,
            "previous_weight_pct": round(source_value_eur / nav * 100.0, 2) if nav else 0.0,
            "target_weight_pct": round(target_weights.get(source, source_value_eur / nav * 100.0 if nav else 0.0), 2),
            "action_executed_this_run": "Shadow reduce",
        })
        positions[source] = source_row

        dest_price_row = price_map.get(destination, {})
        dest_price = _float(dest_price_row.get("selected_close") or dest_price_row.get("price"))
        dest_currency = _text(dest_price_row.get("currency") or "USD").upper()
        dest_shares_delta = _shares_for_notional(notional, dest_price, dest_currency, fx)
        dest_base = dict(positions.get(destination, {}))
        existing_value = _market_value_eur(dest_base)
        dest_value_eur = existing_value + notional
        dest_base.update({
            "ticker": destination,
            "shares": round(_float(dest_base.get("shares")) + dest_shares_delta, 6),
            "currency": dest_currency,
            "current_price_local": round(dest_price, 6),
            "previous_price_local": round(dest_price, 6),
            "selected_close": dest_price,
            "market_value_eur": round(dest_value_eur, 2),
            "previous_market_value_eur": round(dest_value_eur, 2),
            "current_weight_pct": round(dest_value_eur / nav * 100.0, 2) if nav else 0.0,
            "previous_weight_pct": round(dest_value_eur / nav * 100.0, 2) if nav else 0.0,
            "target_weight_pct": round(target_weights.get(destination, dest_value_eur / nav * 100.0 if nav else 0.0), 2),
            "suggested_action": "Add from rotation",
            "action_executed_this_run": "Shadow buy",
            "portfolio_role": dest_base.get("portfolio_role") or "Rotation destination",
            "pricing_source": dest_price_row.get("source"),
            "pricing_status": dest_price_row.get("status"),
            "pricing_tier": dest_price_row.get("pricing_tier"),
            "price_date": dest_price_row.get("returned_close_date"),
            "market_value_local": round(dest_value_eur if dest_currency == "EUR" else dest_value_eur * fx, 2),
            "previous_market_value_local": round(dest_value_eur if dest_currency == "EUR" else dest_value_eur * fx, 2),
        })
        positions[destination] = dest_base

    return sorted(positions.values(), key=lambda row: _ticker(row.get("ticker")))


def _build_ledger_rows(runtime_state: dict[str, Any], shadow_positions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    price_map = _pricing_map(runtime_state)
    position_map = _position_map(runtime_state)
    run_id = _text(runtime_state.get("run_id"), "unknown")
    trade_date = _text(runtime_state.get("requested_close_date") or runtime_state.get("report_date"))
    rows: list[dict[str, Any]] = []
    for index, intent in enumerate(_trade_intents(runtime_state), start=1):
        source = _ticker(intent.get("source_ticker"))
        destination = _ticker(intent.get("destination_ticker"))
        notional = abs(_float(intent.get("estimated_notional_eur")))
        source_weight = _float((position_map.get(source) or {}).get("current_weight_pct"))
        dest_weight = _float(intent.get("destination_delta_weight_pct"))
        rows.append({
            "trade_id": f"shadow-{trade_date}-{run_id}-{index:02d}-{source}-{destination}",
            "trade_date": trade_date,
            "execution_mode": "shadow",
            "source_ticker": source,
            "destination_ticker": destination,
            "action": _text(intent.get("action_code"), "unknown"),
            "source_delta_weight_pct": _round(intent.get("delta_weight_pct"), 4),
            "destination_delta_weight_pct": _round(intent.get("destination_delta_weight_pct"), 4),
            "estimated_notional_eur": round(notional, 2),
            "source_previous_weight_pct": round(source_weight, 4),
            "source_target_weight_pct": round(source_weight + _float(intent.get("delta_weight_pct")), 4),
            "destination_target_weight_pct": round(dest_weight, 4),
            "source_price_status": (price_map.get(source) or {}).get("status"),
            "destination_price_status": (price_map.get(destination) or {}).get("status"),
            "reason_codes": intent.get("reason_codes") or [],
        })
    return rows


def build_execution_artifact(runtime_state_path: Path, portfolio_state_path: Path, trade_ledger_path: Path, mode: str, output_dir: Path) -> dict[str, Any]:
    runtime_state = _read_json(runtime_state_path)
    errors, warnings = _validate_inputs(runtime_state)
    shadow_positions = _build_shadow_positions(runtime_state) if not errors else []
    nav = _nav(runtime_state)
    invested = round(sum(_market_value_eur(row) for row in shadow_positions), 2) if shadow_positions else 0.0
    cash = _float((runtime_state.get("portfolio") or {}).get("cash_eur"))
    artifact = {
        "schema_version": "1.0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "execution_mode": mode,
        "execution_status": "shadow_ready" if mode == "shadow" and not errors else "blocked" if errors else "ready_for_guarded_auto",
        "run_id": runtime_state.get("run_id"),
        "report_date": runtime_state.get("report_date"),
        "requested_close_date": runtime_state.get("requested_close_date"),
        "source_files": {
            "runtime_state": str(runtime_state_path),
            "portfolio_state": str(portfolio_state_path),
            "trade_ledger": str(trade_ledger_path),
            "pricing_audit": (runtime_state.get("source_files") or {}).get("pricing_audit"),
            "rotation_plan": (runtime_state.get("source_files") or {}).get("rotation_plan"),
        },
        "policy_checks": {
            "passed": not errors,
            "errors": errors,
            "warnings": warnings,
            "mode_note": "Shadow mode writes no official portfolio-state or trade-ledger changes." if mode == "shadow" else "Guarded auto-execution is not enabled by this script version.",
        },
        "pre_trade_portfolio": runtime_state.get("portfolio"),
        "post_trade_shadow_portfolio": {
            "cash_eur": round(cash, 2),
            "invested_market_value_eur": invested,
            "nav_eur": round(invested + cash, 2) if shadow_positions else None,
            "nav_drift_eur": round((invested + cash) - nav, 2) if shadow_positions else None,
        },
        "proposed_ledger_rows": _build_ledger_rows(runtime_state, shadow_positions) if not errors else [],
        "shadow_positions": shadow_positions,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    report_token = _text(runtime_state.get("report_date") or runtime_state.get("requested_close_date"), "unknown").replace("-", "")
    run_id = _text(runtime_state.get("run_id"), "unknown")
    out_path = output_dir / f"etf_model_execution_{report_token}_{run_id}.json"
    _write_json(out_path, artifact)
    (output_dir / "latest_etf_model_execution_path.txt").write_text(str(out_path) + "\n", encoding="utf-8")
    artifact["artifact_path"] = str(out_path)
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser(description="Build ETF model execution artifact from rotation trade intents.")
    parser.add_argument("--runtime-state", required=True)
    parser.add_argument("--portfolio-state", default="output/etf_portfolio_state.json")
    parser.add_argument("--trade-ledger", default="output/etf_trade_ledger.csv")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--mode", choices=["shadow", "guarded_auto"], default="shadow")
    args = parser.parse_args()

    artifact = build_execution_artifact(
        runtime_state_path=Path(args.runtime_state),
        portfolio_state_path=Path(args.portfolio_state),
        trade_ledger_path=Path(args.trade_ledger),
        mode=args.mode,
        output_dir=Path(args.output_dir),
    )
    if artifact["policy_checks"]["errors"]:
        print("ETF_MODEL_EXECUTION_BLOCKED | artifact=" + artifact["artifact_path"] + " | errors=" + ";".join(artifact["policy_checks"]["errors"]))
        raise SystemExit(1)
    print(
        "ETF_MODEL_EXECUTION_SHADOW_OK | "
        f"artifact={artifact['artifact_path']} | "
        f"trades={len(artifact.get('proposed_ledger_rows', []))} | "
        f"status={artifact.get('execution_status')}"
    )


if __name__ == "__main__":
    main()
