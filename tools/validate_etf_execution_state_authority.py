from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DEFAULT_PORTFOLIO_STATE = Path("output/etf_portfolio_state.json")
DEFAULT_POINTER = Path("output/runtime/latest_etf_model_execution_path.txt")
SHARE_TOL = 0.0005
VALUE_TOL = 0.75
WEIGHT_TOL = 0.08


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def _positions(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [dict(row) for row in (payload.get("positions") or payload.get("shadow_positions") or []) if isinstance(row, dict)]


def _position_map(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {_ticker(row.get("ticker")): dict(row) for row in _positions(payload) if _ticker(row.get("ticker"))}


def _cash_eur(payload: dict[str, Any]) -> float:
    p = payload.get("portfolio") or payload
    return _float(p.get("cash_eur"))


def _nav_eur(payload: dict[str, Any]) -> float:
    p = payload.get("portfolio") or payload
    return _float(p.get("total_portfolio_value_eur") or p.get("nav_eur"))


def _fx_rate(payload: dict[str, Any]) -> float:
    fx = payload.get("fx_basis") or {}
    return _float(fx.get("rate"), 1.0) or 1.0


def _price_local(row: dict[str, Any]) -> float:
    return _float(row.get("selected_close") or row.get("current_price_local") or row.get("continuity_current_price_local") or row.get("previous_price_local"))


def _value_local(row: dict[str, Any]) -> float:
    return _float(row.get("market_value_local") if row.get("market_value_local") not in (None, "") else row.get("previous_market_value_local"))


def _value_eur(row: dict[str, Any]) -> float:
    return _float(row.get("market_value_eur") if row.get("market_value_eur") not in (None, "") else row.get("previous_market_value_eur"))


def _is_cash(row: dict[str, Any]) -> bool:
    return _ticker(row.get("ticker")) == "CASH"


def _arithmetic_errors(rows: list[dict[str, Any]], *, fx: float, nav: float, context: str) -> list[str]:
    errors: list[str] = []
    for row in rows:
        ticker = _ticker(row.get("ticker"))
        if not ticker or _is_cash(row):
            continue
        shares = _float(row.get("shares"))
        price = _price_local(row)
        currency = _text(row.get("currency"), "USD").upper()
        local = _value_local(row)
        eur = _value_eur(row)
        weight = _float(row.get("current_weight_pct") or row.get("weight_pct") or row.get("previous_weight_pct"))
        if shares > SHARE_TOL and price <= 0:
            errors.append(f"{context}:missing_price:{ticker}")
        if shares >= 0 and price > 0 and local > 0:
            expected_local = round(shares * price, 2)
            if abs(expected_local - local) > VALUE_TOL:
                errors.append(f"{context}:local_value_mismatch:{ticker}:expected={expected_local:.2f}:actual={local:.2f}")
        if local > 0 and eur > 0 and fx > 0:
            expected_eur = round(local if currency == "EUR" else local / fx, 2)
            if abs(expected_eur - eur) > VALUE_TOL:
                errors.append(f"{context}:eur_value_mismatch:{ticker}:expected={expected_eur:.2f}:actual={eur:.2f}")
        if eur > 0 and nav > 0 and weight > 0:
            expected_weight = round(eur / nav * 100.0, 2)
            if abs(expected_weight - weight) > WEIGHT_TOL:
                errors.append(f"{context}:weight_mismatch:{ticker}:expected={expected_weight:.2f}:actual={weight:.2f}")
    return errors


def _compare_to_official(ticker: str, actual: dict[str, Any], official: dict[str, Any], context: str) -> list[str]:
    errors: list[str] = []
    actual_shares = _float(actual.get("shares"))
    official_shares = _float(official.get("shares"))
    if abs(actual_shares - official_shares) > SHARE_TOL:
        errors.append(f"{context}:shares_authority_mismatch:{ticker}:expected={official_shares:.6f}:actual={actual_shares:.6f}")
    actual_currency = _text(actual.get("currency"), "USD").upper()
    official_currency = _text(official.get("currency"), "USD").upper()
    if actual_currency != official_currency:
        errors.append(f"{context}:currency_authority_mismatch:{ticker}:expected={official_currency}:actual={actual_currency}")
    actual_eur = _value_eur(actual)
    official_eur = _value_eur(official)
    if official_eur > 0 and abs(actual_eur - official_eur) > VALUE_TOL:
        errors.append(f"{context}:market_value_eur_authority_mismatch:{ticker}:expected={official_eur:.2f}:actual={actual_eur:.2f}")
    return errors


def validate_runtime_state_authority(runtime_state_path: Path, portfolio_state_path: Path = DEFAULT_PORTFOLIO_STATE, *, context: str = "runtime_state", raise_on_error: bool = True) -> list[str]:
    runtime_state = _read_json(runtime_state_path)
    portfolio_state = _read_json(portfolio_state_path)
    errors: list[str] = []
    runtime_positions = _position_map(runtime_state)
    official_positions = _position_map(portfolio_state)
    for ticker, official in official_positions.items():
        actual = runtime_positions.get(ticker)
        if not actual:
            errors.append(f"{context}:official_holding_missing_from_runtime:{ticker}")
            continue
        errors.extend(_compare_to_official(ticker, actual, official, context))
    for ticker, actual in runtime_positions.items():
        if ticker not in official_positions and _value_eur(actual) > VALUE_TOL:
            errors.append(f"{context}:runtime_has_unofficial_position:{ticker}:market_value_eur={_value_eur(actual):.2f}")
    if abs(_cash_eur(runtime_state) - _cash_eur(portfolio_state)) > VALUE_TOL:
        errors.append(f"{context}:cash_authority_mismatch:expected={_cash_eur(portfolio_state):.2f}:actual={_cash_eur(runtime_state):.2f}")
    if _nav_eur(portfolio_state) > 0 and abs(_nav_eur(runtime_state) - _nav_eur(portfolio_state)) > VALUE_TOL:
        errors.append(f"{context}:nav_authority_mismatch:expected={_nav_eur(portfolio_state):.2f}:actual={_nav_eur(runtime_state):.2f}")
    errors.extend(_arithmetic_errors(list(runtime_positions.values()), fx=_fx_rate(runtime_state), nav=_nav_eur(runtime_state), context=context))
    if errors and raise_on_error:
        raise RuntimeError("ETF execution-state authority validation failed: " + "; ".join(sorted(set(errors))))
    return errors


def _resolve_artifact(path_arg: str | None) -> Path:
    if path_arg:
        path = Path(path_arg)
        if path.exists():
            return path
        raise RuntimeError(f"Explicit ETF model-execution artifact does not exist: {path}")
    env = os.environ.get("ETF_MODEL_EXECUTION_PATH") or os.environ.get("MRKT_RPRTS_MODEL_EXECUTION_PATH")
    if env and Path(env).exists():
        return Path(env)
    if DEFAULT_POINTER.exists():
        raw = DEFAULT_POINTER.read_text(encoding="utf-8").strip()
        if raw and Path(raw).exists():
            return Path(raw)
    raise RuntimeError("No ETF model-execution artifact found.")


def _runtime_state_for_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    raw = (artifact.get("source_files") or {}).get("runtime_state")
    if raw and Path(raw).exists():
        return _read_json(Path(raw))
    return {}


def validate_execution_artifact(artifact_path: Path, *, expected_mode: str | None = None, portfolio_state_path: Path | None = None, raise_on_error: bool = True) -> list[str]:
    artifact = _read_json(artifact_path)
    mode = _text(artifact.get("execution_mode"))
    errors: list[str] = []
    if expected_mode and mode != expected_mode:
        errors.append(f"artifact:execution_mode_mismatch:{mode}!={expected_mode}")
    if portfolio_state_path is None:
        portfolio_state_path = Path((artifact.get("source_files") or {}).get("portfolio_state") or DEFAULT_PORTFOLIO_STATE)
    portfolio_state = _read_json(portfolio_state_path)
    official_positions = _position_map(portfolio_state)
    shadow_positions = _position_map({"positions": artifact.get("shadow_positions") or []})
    runtime_state = _runtime_state_for_artifact(artifact)
    nav = _float((artifact.get("post_trade_shadow_portfolio") or {}).get("nav_eur") or _nav_eur(portfolio_state))
    errors.extend(_arithmetic_errors(list(shadow_positions.values()), fx=_fx_rate(runtime_state), nav=nav, context=f"artifact_{mode or 'unknown'}"))
    for ticker, shadow in shadow_positions.items():
        official = official_positions.get(ticker)
        if mode == "guarded_auto":
            if not official:
                errors.append(f"artifact_guarded_auto:position_missing_from_official_state:{ticker}")
            else:
                errors.extend(_compare_to_official(ticker, shadow, official, "artifact_guarded_auto"))
        elif mode == "shadow" and official:
            delta = _float(shadow.get("shares_delta_this_run"))
            expected_after = _float(official.get("shares")) + delta
            actual_after = _float(shadow.get("shares"))
            if abs(expected_after - actual_after) > SHARE_TOL:
                errors.append(f"artifact_shadow:shares_delta_does_not_bridge_official_state:{ticker}:expected_after={expected_after:.6f}:actual_after={actual_after:.6f}")
    if mode == "guarded_auto":
        result = artifact.get("guarded_auto_result") or {}
        if result.get("portfolio_state_written") is not True:
            errors.append("artifact_guarded_auto:portfolio_state_not_written")
        if result.get("trade_ledger_written") is not True:
            errors.append("artifact_guarded_auto:trade_ledger_not_written")
    if errors and raise_on_error:
        raise RuntimeError("ETF execution artifact authority validation failed: " + "; ".join(sorted(set(errors))))
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate ETF execution-state authority and row-level valuation arithmetic.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--runtime-state")
    group.add_argument("--artifact")
    parser.add_argument("--portfolio-state", default=str(DEFAULT_PORTFOLIO_STATE))
    parser.add_argument("--expected-mode", choices=["shadow", "guarded_auto"], default=None)
    parser.add_argument("--context", default="manual")
    args = parser.parse_args()
    if args.runtime_state:
        errors = validate_runtime_state_authority(Path(args.runtime_state), Path(args.portfolio_state), context=args.context, raise_on_error=False)
        target = args.runtime_state
    else:
        artifact_path = _resolve_artifact(args.artifact)
        errors = validate_execution_artifact(artifact_path, expected_mode=args.expected_mode, portfolio_state_path=Path(args.portfolio_state), raise_on_error=False)
        target = str(artifact_path)
    if errors:
        raise RuntimeError("ETF execution-state authority validation failed for " + target + ": " + "; ".join(sorted(set(errors))))
    print(f"ETF_EXECUTION_STATE_AUTHORITY_OK | target={target} | context={args.context}")


if __name__ == "__main__":
    main()
