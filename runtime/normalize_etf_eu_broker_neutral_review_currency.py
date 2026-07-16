from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def money(value: Any) -> float:
    return round(float(value or 0.0), 2)


def normalize(payload: dict[str, Any]) -> dict[str, Any]:
    policy = payload.get("policy") or {}
    if policy.get("minimum_cash_reserve_eur") is not None:
        policy["minimum_cash_reserve_eur"] = money(policy["minimum_cash_reserve_eur"])

    revaluation = payload.get("portfolio_revaluation") or {}
    for field in ("prior_nav_eur", "cash_eur", "invested_market_value_eur", "nav_eur", "nav_change_eur"):
        if revaluation.get(field) is not None:
            revaluation[field] = money(revaluation[field])
    for row in revaluation.get("positions") or []:
        if row.get("market_value_eur") is not None:
            row["market_value_eur"] = money(row["market_value_eur"])

    for row in payload.get("incumbent_reviews") or []:
        for field in ("market_value_eur", "unrealized_pnl_eur"):
            if row.get(field) is not None:
                row[field] = money(row[field])

    for row in payload.get("decision_rows") or []:
        for field in ("phase_target_value_eur", "trade_value_eur", "projected_market_value_eur"):
            if row.get(field) is not None:
                row[field] = money(row[field])

    for intent in payload.get("trade_intents") or []:
        if intent.get("trade_value_eur") is not None:
            intent["trade_value_eur"] = money(intent["trade_value_eur"])

    allocation = payload.get("allocation_decision") or {}
    for field in ("cash_after_decision_eur", "invested_after_decision_eur", "nav_after_decision_eur"):
        if allocation.get(field) is not None:
            allocation[field] = money(allocation[field])

    revalued_nav = money(revaluation.get("nav_eur"))
    projected_nav = money(allocation.get("nav_after_decision_eur"))
    allocation["nav_reconciliation_ok"] = abs(revalued_nav - projected_nav) <= 0.01
    payload["currency_normalization"] = {
        "base_currency": "EUR",
        "money_precision_decimals": 2,
        "price_precision_preserved": True,
        "normalized": True,
    }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()

    source = Path(args.review)
    output = Path(args.output) if args.output else source
    payload = json.loads(source.read_text(encoding="utf-8"))
    normalized = normalize(payload)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(normalized, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "normalized",
                "review": str(output),
                "nav_reconciliation_ok": normalized["allocation_decision"]["nav_reconciliation_ok"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
