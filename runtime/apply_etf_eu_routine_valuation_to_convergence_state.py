from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def ticker(row: dict[str, Any]) -> str:
    return str(row.get("ticker") or row.get("exchange_ticker") or "").strip().upper()


def apply(state_path: Path, overlay_path: Path, report_date: str) -> None:
    state = load(state_path)
    overlay = load(overlay_path)
    if state.get("schema_version") != "etf_eu_production_convergence_state_v1":
        raise RuntimeError("Unexpected convergence state schema")
    if overlay.get("schema_version") != "etf_eu_routine_valuation_overlay_v1":
        raise RuntimeError("Unexpected valuation overlay schema")
    if overlay.get("portfolio_mutation") is not False or overlay.get("ledger_write") is not False:
        raise RuntimeError("Valuation overlay violates protected-state boundary")

    official = state.get("official_portfolio") if isinstance(state.get("official_portfolio"), dict) else {}
    prior_positions = {ticker(row): row for row in official.get("positions") or [] if isinstance(row, dict)}
    overlay_positions = {ticker(row): row for row in overlay.get("positions") or [] if isinstance(row, dict)}
    if set(prior_positions) != set(overlay_positions):
        raise RuntimeError("Valuation overlay funded ticker set differs")
    for symbol, current in overlay_positions.items():
        prior_shares = float(prior_positions[symbol].get("shares") or 0)
        current_shares = float(current.get("shares") or 0)
        if prior_shares != current_shares:
            raise RuntimeError(f"Valuation overlay changes official shares for {symbol}")

    official.update(
        {
            "starting_capital_eur": overlay.get("starting_capital_eur"),
            "nav_eur": overlay.get("nav_eur"),
            "cash_eur": overlay.get("cash_eur"),
            "invested_market_value_eur": overlay.get("invested_market_value_eur"),
            "since_inception_return_pct": overlay.get("since_inception_return_pct"),
            "position_count": overlay.get("position_count"),
            "positions": list(overlay_positions.values()),
            "valuation_role": overlay.get("valuation_role"),
            "pricing_close_dates": overlay.get("pricing_close_dates"),
            "valuation_overlay_path": str(overlay_path),
        }
    )
    state["report_date"] = report_date
    state["valuation_overlay"] = {
        "applied": True,
        "path": str(overlay_path),
        "pricing_close_dates": overlay.get("pricing_close_dates"),
        "official_portfolio_state_sha256": overlay.get("official_portfolio_state_sha256"),
        "official_trade_ledger_sha256": overlay.get("official_trade_ledger_sha256"),
        "portfolio_mutation": False,
        "ledger_write": False,
    }
    state.setdefault("validation", {})["fresh_run_valuation_applied"] = True
    state["validation"]["valuation_position_count"] = len(overlay_positions)
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(state_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("state", type=Path)
    parser.add_argument("--overlay", type=Path, required=True)
    parser.add_argument("--report-date", required=True)
    args = parser.parse_args()
    apply(args.state, args.overlay, args.report_date)


if __name__ == "__main__":
    main()
