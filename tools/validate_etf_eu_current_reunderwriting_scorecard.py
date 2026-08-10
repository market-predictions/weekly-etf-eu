from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


REQUIRED_COLUMNS = {
    "report_date", "isin", "exchange_ticker", "fund_name", "weight_pct", "shares",
    "current_price_status", "suggested_action", "fresh_cash_test", "would_initiate_today",
    "would_initiate_at_current_weight", "replaceable_status", "weeks_replaceable",
    "factor_overlap_flag", "cash_policy_flag", "required_next_action",
    "ucits_status", "priips_kid_status", "investability_status",
    "reunderwriting_status", "source_report",
}

FORBIDDEN_AUTHORITY_TOKENS = {
    "35% minimum cash",
    "15% maximum new",
    "50% cash-first",
    "25% turnover ceiling",
    "18% semiconductor cap",
    "stage_1_candidate_not_allowlisted",
}


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def ticker(value: Any) -> str:
    text = str(value or "").strip().upper()
    return "L0CK" if text == "LOCK" else text


def funded_tickers(portfolio: dict[str, Any]) -> set[str]:
    return {
        ticker(row.get("ticker") or row.get("exchange_ticker"))
        for row in portfolio.get("positions") or []
        if isinstance(row, dict) and float(row.get("shares") or 0) > 0
    }


def validate(scorecard: Path, portfolio_path: Path, report_date: str) -> dict[str, Any]:
    portfolio = load_json(portfolio_path)
    expected = funded_tickers(portfolio)
    with scorecard.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        missing_columns = sorted(REQUIRED_COLUMNS - fields)
        if missing_columns:
            raise RuntimeError(f"Scorecard missing required columns: {missing_columns}")
        rows = list(reader)

    actual = [ticker(row.get("exchange_ticker")) for row in rows]
    if len(actual) != len(set(actual)):
        raise RuntimeError(f"Duplicate current scorecard tickers: {actual}")
    if set(actual) != expected:
        raise RuntimeError(f"Current scorecard funded ticker mismatch: expected={sorted(expected)} actual={sorted(actual)}")

    blockers: list[str] = []
    for row in rows:
        if row.get("report_date") != report_date:
            blockers.append(f"{row.get('exchange_ticker')}:wrong_report_date")
        if not row.get("fresh_cash_test"):
            blockers.append(f"{row.get('exchange_ticker')}:fresh_cash_test_missing")
        if not row.get("would_initiate_today"):
            blockers.append(f"{row.get('exchange_ticker')}:would_initiate_today_missing")
        if not row.get("cash_policy_flag"):
            blockers.append(f"{row.get('exchange_ticker')}:cash_policy_missing")
        if not row.get("required_next_action"):
            blockers.append(f"{row.get('exchange_ticker')}:required_next_action_missing")
        if not row.get("isin"):
            blockers.append(f"{row.get('exchange_ticker')}:isin_missing")
        if row.get("ucits_status") not in {"confirmed", "confirmed_by_fund_name"}:
            blockers.append(f"{row.get('exchange_ticker')}:ucits_status_not_confirmed")
        if row.get("priips_kid_status") != "available":
            blockers.append(f"{row.get('exchange_ticker')}:kid_not_available")

    rendered = scorecard.read_text(encoding="utf-8").casefold()
    leaked = sorted(token for token in FORBIDDEN_AUTHORITY_TOKENS if token.casefold() in rendered)
    if leaked:
        blockers.append(f"retired_or_shadow_authority_leak:{leaked}")

    result = {
        "schema_version": "etf_eu_current_reunderwriting_validation_v1",
        "report_date": report_date,
        "funded_tickers": sorted(expected),
        "scorecard_tickers": sorted(actual),
        "funded_position_count": len(expected),
        "scorecard_row_count": len(rows),
        "all_funded_positions_covered": set(actual) == expected,
        "retired_or_shadow_authority_leak": leaked,
        "portfolio_mutation": False,
        "blockers": blockers,
        "valid": not blockers,
    }
    if blockers:
        raise RuntimeError(json.dumps(result, indent=2, sort_keys=True))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate current ETF EU re-underwriting scorecard")
    parser.add_argument("--scorecard", type=Path, required=True)
    parser.add_argument("--portfolio-state", type=Path, default=Path("output/etf_eu_portfolio_state.json"))
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = validate(args.scorecard, args.portfolio_state, args.report_date)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "ETF_EU_CURRENT_REUNDERWRITING_VALID"
        f" | funded={result['funded_position_count']} | tickers={','.join(result['funded_tickers'])}"
    )


if __name__ == "__main__":
    main()
