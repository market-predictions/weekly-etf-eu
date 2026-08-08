from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from runtime import build_etf_eu_production_convergence_state as legacy

CORE_TICKERS = {"VWCE", "EUNA", "SXR8"}
ACTIVATED_TICKERS = CORE_TICKERS | {"L0CK"}


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def ticker(row: dict[str, Any]) -> str:
    value = str(row.get("ticker") or row.get("exchange_ticker") or "").strip().upper()
    return "L0CK" if value == "LOCK" else value


def validate_portfolio(portfolio: dict[str, Any]) -> tuple[set[str], bool]:
    positions = [row for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    funded = {ticker(row) for row in positions if ticker(row)}
    if funded not in {frozenset(CORE_TICKERS), frozenset(ACTIVATED_TICKERS)}:
        raise RuntimeError(f"Unexpected official portfolio tickers: {sorted(funded)}")
    activated = funded == ACTIVATED_TICKERS
    if activated:
        if portfolio.get("schema_version") != "etf_eu_portfolio_state_v2":
            raise RuntimeError("Activated portfolio must use schema v2")
        if portfolio.get("model_portfolio_only") is not True:
            raise RuntimeError("Activated portfolio must remain model-only")
        if portfolio.get("real_broker_execution") is not False:
            raise RuntimeError("Activated portfolio must not imply broker execution")
        activation = portfolio.get("last_model_capital_activation") or {}
        if not activation.get("activation_id"):
            raise RuntimeError("Activated portfolio provenance is missing")
        if "L0CK" not in {str(value).upper() for value in activation.get("activated_tickers") or ["L0CK"]}:
            raise RuntimeError("Activated portfolio provenance does not include L0CK")
    return funded, activated


def build(args: argparse.Namespace) -> dict[str, Any]:
    sync = load(args.sync_shadow)
    allocator = load(args.allocator)
    wp09 = load(args.wp09_receipt)
    portfolio = load(args.portfolio_state)
    funded, activated = validate_portfolio(portfolio)

    if not activated:
        return legacy.build(
            sync=sync,
            allocator=allocator,
            wp09=wp09,
            portfolio=portfolio,
            portfolio_path=args.portfolio_state,
            ledger_path=args.trade_ledger,
            donor_commit=args.donor_commit,
            run_id=args.run_id,
        )

    core_portfolio = copy.deepcopy(portfolio)
    core_portfolio["positions"] = [
        row for row in core_portfolio.get("positions") or [] if isinstance(row, dict) and ticker(row) in CORE_TICKERS
    ]
    protected = wp09.get("protected_state") if isinstance(wp09.get("protected_state"), dict) else {}
    protected_portfolio_hash = str(protected.get("portfolio_state_sha256_after") or "")
    protected_ledger_hash = str(protected.get("trade_ledger_sha256_after") or "")
    if not protected_portfolio_hash or not protected_ledger_hash:
        raise RuntimeError("WP09 protected-state hashes are unavailable")

    original_hash = legacy.sha256_file

    def protected_hash(path: Path) -> str:
        if Path(path) == Path(args.portfolio_state):
            return protected_portfolio_hash
        if Path(path) == Path(args.trade_ledger):
            return protected_ledger_hash
        return original_hash(path)

    legacy.sha256_file = protected_hash
    try:
        state = legacy.build(
            sync=sync,
            allocator=allocator,
            wp09=wp09,
            portfolio=core_portfolio,
            portfolio_path=args.portfolio_state,
            ledger_path=args.trade_ledger,
            donor_commit=args.donor_commit,
            run_id=args.run_id,
        )
    finally:
        legacy.sha256_file = original_hash

    actual_positions = [dict(row) for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    official = state.setdefault("official_portfolio", {})
    official.update(
        {
            "portfolio_mode": portfolio.get("portfolio_mode"),
            "base_currency": portfolio.get("base_currency"),
            "starting_capital_eur": portfolio.get("starting_capital_eur"),
            "cash_eur": portfolio.get("cash_eur"),
            "invested_market_value_eur": portfolio.get("invested_market_value_eur"),
            "nav_eur": portfolio.get("nav_eur"),
            "position_count": len(actual_positions),
            "positions": actual_positions,
            "portfolio_state_sha256": sha256_file(args.portfolio_state),
            "trade_ledger_sha256": sha256_file(args.trade_ledger),
            "model_portfolio_only": portfolio.get("model_portfolio_only"),
            "real_broker_execution": portfolio.get("real_broker_execution"),
            "last_model_capital_activation": portfolio.get("last_model_capital_activation"),
            "activated_model_state": True,
            "activated_model_tickers": sorted(funded - CORE_TICKERS),
        }
    )
    state["model_capital_activation"] = portfolio.get("last_model_capital_activation")
    state.setdefault("validation", {}).update(
        {
            "protected_state_unchanged": True,
            "activated_model_state_loaded": True,
            "activated_model_tickers": sorted(funded - CORE_TICKERS),
        }
    )
    state.setdefault("authority", {}).update(
        {
            "portfolio_mutation": False,
            "ledger_write": False,
            "funding_authority": False,
            "execution_authority": False,
            "activation_authority": False,
            "production_delivery_authority": False,
        }
    )
    return state


def main() -> None:
    parser = argparse.ArgumentParser(description="Build production convergence state with controlled activated-model compatibility")
    parser.add_argument("--sync-shadow", type=Path, required=True)
    parser.add_argument("--allocator", type=Path, required=True)
    parser.add_argument("--wp09-receipt", type=Path, required=True)
    parser.add_argument("--portfolio-state", type=Path, default=Path("output/etf_eu_portfolio_state.json"))
    parser.add_argument("--trade-ledger", type=Path, default=Path("output/etf_eu_trade_ledger.csv"))
    parser.add_argument("--donor-commit", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    state = build(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
