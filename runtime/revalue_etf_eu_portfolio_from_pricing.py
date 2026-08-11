from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any


def _identity(row: dict[str, Any]) -> tuple[str, str]:
    return (
        str(row.get("isin") or "").strip().upper(),
        str(row.get("exchange_ticker") or row.get("ticker") or "").strip().upper(),
    )


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def revalue_payload(
    portfolio_state: dict[str, Any],
    pricing_payload: dict[str, Any],
    *,
    pricing_artifact: str | None = None,
) -> dict[str, Any]:
    state = copy.deepcopy(portfolio_state)
    report_date = str(pricing_payload.get("report_date") or "").strip()
    if not report_date:
        raise RuntimeError("ETF_EU_REVALUATION_REPORT_DATE_MISSING")
    if pricing_payload.get("report_pricing_gate_passed") is not True:
        raise RuntimeError("ETF_EU_REVALUATION_PRICING_GATE_NOT_PASSED")

    pricing_rows = {
        _identity(row): row
        for row in pricing_payload.get("rows") or []
        if isinstance(row, dict) and all(_identity(row))
    }
    positions = [row for row in state.get("positions") or [] if isinstance(row, dict)]
    if not positions:
        raise RuntimeError("ETF_EU_REVALUATION_NO_FUNDED_POSITIONS")

    revalued: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    for original in positions:
        row = dict(original)
        identity = _identity(row)
        price_row = pricing_rows.get(identity)
        if price_row is None:
            raise RuntimeError(f"ETF_EU_REVALUATION_EXACT_LINE_MISSING:{identity[1] or identity[0]}")
        agreeing = sorted({str(value) for value in price_row.get("agreeing_providers") or [] if str(value).strip()})
        if (
            price_row.get("completed_close_on_or_before_report_date") is not True
            or price_row.get("source_agreement_status") != "qualified_development_consensus"
            or price_row.get("valuation_grade") is not True
            or len(agreeing) < 2
            or str(price_row.get("close_date") or "") != report_date
        ):
            raise RuntimeError(f"ETF_EU_REVALUATION_CONSENSUS_FAILED:{identity[1] or identity[0]}")
        price = float(price_row.get("close_price"))
        shares = float(row.get("shares") or 0.0)
        market_value = round(shares * price, 2)
        row.update(
            {
                "current_price_local": price,
                "previous_price_local": price,
                "market_value_local": market_value,
                "previous_market_value_local": market_value,
                "market_value_eur": market_value,
                "previous_market_value_eur": market_value,
                "price_date": report_date,
                "pricing_status": "qualified_two_provider_completed_close",
                "verification_status": "two_provider_consensus",
                "valuation_source": "canonical_v2_completed_close_contract",
            }
        )
        revalued.append(row)
        evidence.append(
            {
                "isin": identity[0],
                "ticker": identity[1],
                "close_price": price,
                "close_date": report_date,
                "agreeing_providers": agreeing,
                "market_value_eur": market_value,
            }
        )

    cash = round(float(state.get("cash_eur") or 0.0), 2)
    invested = round(sum(float(row.get("market_value_eur") or 0.0) for row in revalued), 2)
    nav = round(cash + invested, 2)
    for row in revalued:
        weight = round((float(row.get("market_value_eur") or 0.0) / nav * 100.0), 6) if nav else 0.0
        row["current_weight_pct"] = weight
        row["previous_weight_pct"] = weight
        row["weight_inherited_pct"] = weight

    state.update(
        {
            "positions": revalued,
            "invested_market_value_eur": invested,
            "nav_eur": nav,
            "valuation_source": "canonical_v2_completed_close_contract",
            "last_valuation_refresh": {
                "report_date": report_date,
                "pricing_artifact": pricing_artifact,
                "funded_position_count": len(revalued),
                "capital_mutation": False,
                "shares_changed": False,
                "cash_changed": False,
                "trade_ledger_write": False,
                "real_broker_execution": False,
                "evidence": evidence,
            },
        }
    )
    return state


def main() -> None:
    parser = argparse.ArgumentParser(description="Revalue the protected ETF EU model state from exact-line v2 completed-close consensus without changing shares or cash.")
    parser.add_argument("--portfolio-state", default="output/etf_eu_portfolio_state.json")
    parser.add_argument("--pricing-artifact", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    state_path = Path(args.portfolio_state)
    pricing_path = Path(args.pricing_artifact)
    before = _load(state_path)
    after = revalue_payload(before, _load(pricing_path), pricing_artifact=str(pricing_path))
    before_shares = {_identity(row): row.get("shares") for row in before.get("positions") or [] if isinstance(row, dict)}
    after_shares = {_identity(row): row.get("shares") for row in after.get("positions") or [] if isinstance(row, dict)}
    if before_shares != after_shares or round(float(before.get("cash_eur") or 0), 2) != round(float(after.get("cash_eur") or 0), 2):
        raise RuntimeError("ETF_EU_REVALUATION_CAPITAL_MUTATION_DETECTED")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(after, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        "ETF_EU_PORTFOLIO_REVALUATION_OK"
        f" | report_date={after['last_valuation_refresh']['report_date']}"
        f" | nav_eur={after['nav_eur']:.2f}"
        f" | invested_eur={after['invested_market_value_eur']:.2f}"
        f" | cash_eur={after['cash_eur']:.2f}"
        f" | positions={len(after['positions'])}"
        " | capital_mutation=false"
    )


if __name__ == "__main__":
    main()
