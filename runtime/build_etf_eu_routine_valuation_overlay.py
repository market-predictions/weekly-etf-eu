from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


FUNDED_TICKERS = ("VWCE", "EUNA", "SXR8")


def load_json(path: Path) -> dict[str, Any]:
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


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ticker(position: dict[str, Any]) -> str:
    return str(position.get("ticker") or position.get("exchange_ticker") or "").strip().upper()


def build(portfolio: dict[str, Any], pricing: dict[str, Any], portfolio_path: Path, ledger_path: Path, report_date: str, run_id: str) -> dict[str, Any]:
    positions = [dict(row) for row in portfolio.get("positions") or [] if isinstance(row, dict)]
    by_ticker = {ticker(row): row for row in positions if ticker(row)}
    if set(by_ticker) != set(FUNDED_TICKERS):
        raise RuntimeError(f"Official funded ticker set differs: {sorted(by_ticker)}")

    pricing_rows = [row for row in pricing.get("rows") or [] if isinstance(row, dict)]
    priced_by_ticker = {
        str(row.get("ticker") or "").strip().upper(): row
        for row in pricing_rows
        if row.get("pricing_status") == "priced_non_authoritative"
        and row.get("close_price") is not None
        and str(row.get("currency") or "").upper() == "EUR"
    }

    valued_positions: list[dict[str, Any]] = []
    missing: list[str] = []
    close_dates: set[str] = set()
    invested = 0.0
    for symbol in FUNDED_TICKERS:
        official = by_ticker[symbol]
        price_row = priced_by_ticker.get(symbol)
        if not price_row:
            missing.append(symbol)
            continue
        shares = float(official.get("shares") or official.get("quantity") or 0)
        price = float(price_row["close_price"])
        market_value = round(shares * price, 2)
        invested += market_value
        close_date = str(price_row.get("close_date") or "")
        if close_date:
            close_dates.add(close_date)
        valued_positions.append(
            {
                **official,
                "ticker": symbol,
                "shares": shares,
                "model_price": official.get("model_price") or official.get("current_price") or official.get("price"),
                "current_price": price,
                "current_price_eur": price,
                "pricing_currency": "EUR",
                "pricing_close_date": close_date,
                "market_value_eur": market_value,
                "pricing_status": price_row.get("pricing_status"),
                "pricing_source": price_row.get("source_name"),
                "pricing_source_quality": price_row.get("source_quality_status"),
                "valuation_grade": False,
                "portfolio_mutation": False,
            }
        )
    if missing:
        raise RuntimeError("Missing fresh EUR close for official funded lines: " + ", ".join(missing))

    cash = float(portfolio.get("cash_eur") or 0)
    nav = round(cash + invested, 2)
    for row in valued_positions:
        row["weight_pct"] = round(float(row["market_value_eur"]) / nav * 100.0, 6) if nav else 0.0
    starting = float(portfolio.get("starting_capital_eur") or 0)
    since_inception = round(((nav / starting) - 1.0) * 100.0, 6) if starting else 0.0

    result = {
        "schema_version": "etf_eu_routine_valuation_overlay_v1",
        "artifact_type": "etf_eu_routine_valuation_overlay",
        "generated_at_utc": utc_now(),
        "run_id": run_id,
        "report_date": report_date,
        "valuation_role": "run_scoped_report_valuation_not_official_state_mutation",
        "portfolio_mode": portfolio.get("portfolio_mode"),
        "base_currency": "EUR",
        "inception_date": portfolio.get("inception_date"),
        "starting_capital_eur": starting,
        "cash_eur": cash,
        "invested_market_value_eur": round(invested, 2),
        "nav_eur": nav,
        "since_inception_return_pct": since_inception,
        "position_count": len(valued_positions),
        "positions": valued_positions,
        "pricing_close_dates": sorted(close_dates),
        "pricing_artifact_run_id": pricing.get("run_id"),
        "pricing_artifact_report_date": pricing.get("report_date"),
        "pricing_line_count": pricing.get("line_count"),
        "priced_line_count": pricing.get("priced_line_count"),
        "official_portfolio_state_sha256": sha256_file(portfolio_path),
        "official_trade_ledger_sha256": sha256_file(ledger_path),
        "protected_official_shares": {symbol: by_ticker[symbol].get("shares") for symbol in FUNDED_TICKERS},
        "portfolio_mutation": False,
        "ledger_write": False,
        "funding_authority": False,
        "execution_authority": False,
        "production_delivery_authority": False,
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Build run-scoped ETF EU report valuation from fresh EUR closes")
    parser.add_argument("--portfolio-state", type=Path, default=Path("output/etf_eu_portfolio_state.json"))
    parser.add_argument("--trade-ledger", type=Path, default=Path("output/etf_eu_trade_ledger.csv"))
    parser.add_argument("--pricing-artifact", type=Path, required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    payload = build(
        portfolio=load_json(args.portfolio_state),
        pricing=load_json(args.pricing_artifact),
        portfolio_path=args.portfolio_state,
        ledger_path=args.trade_ledger,
        report_date=args.report_date,
        run_id=args.run_id,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
