from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


FIELDNAMES = [
    "date",
    "nav_eur",
    "cash_eur",
    "invested_market_value_eur",
    "daily_return_pct",
    "since_inception_return_pct",
    "drawdown_pct",
    "comment",
    "source_report",
]


def _load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Portfolio state not found: {path}")
    state = json.loads(path.read_text(encoding="utf-8"))
    for field in ["starting_capital_eur", "cash_eur", "invested_market_value_eur", "nav_eur"]:
        try:
            float(state[field])
        except (KeyError, TypeError, ValueError) as exc:
            raise RuntimeError(f"Portfolio state has invalid {field}") from exc
    return state


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _f(value: Any) -> float:
    return float(value or 0)


def build_row(
    *,
    state: dict[str, Any],
    report_date: str,
    source_report: str,
    comment: str,
    prior_rows: list[dict[str, str]],
) -> dict[str, str]:
    nav = _f(state["nav_eur"])
    cash = _f(state["cash_eur"])
    invested = _f(state["invested_market_value_eur"])
    starting = _f(state["starting_capital_eur"])
    if nav <= 0 or starting <= 0:
        raise RuntimeError("NAV and starting capital must be positive")
    if abs((cash + invested) - nav) > 0.05:
        raise RuntimeError("Cash plus invested market value does not reconcile to NAV")

    previous_nav = _f(prior_rows[-1].get("nav_eur")) if prior_rows else nav
    peak = max([_f(row.get("nav_eur")) for row in prior_rows] + [nav])
    daily_return = ((nav / previous_nav) - 1.0) * 100.0 if previous_nav else 0.0
    since_inception = ((nav / starting) - 1.0) * 100.0
    drawdown = ((nav / peak) - 1.0) * 100.0 if peak else 0.0
    return {
        "date": report_date,
        "nav_eur": f"{nav:.2f}",
        "cash_eur": f"{cash:.2f}",
        "invested_market_value_eur": f"{invested:.2f}",
        "daily_return_pct": f"{daily_return:.6f}",
        "since_inception_return_pct": f"{since_inception:.6f}",
        "drawdown_pct": f"{drawdown:.6f}",
        "comment": comment,
        "source_report": source_report,
    }


def update_history(
    *,
    state_path: Path,
    history_path: Path,
    report_date: str,
    source_report: str,
    comment: str,
    output_path: Path,
) -> dict[str, Any]:
    state = _load_state(state_path)
    rows = _read_rows(history_path)
    existing = [row for row in rows if row.get("date") == report_date]
    new_row = build_row(
        state=state,
        report_date=report_date,
        source_report=source_report,
        comment=comment,
        prior_rows=[row for row in rows if row.get("date") != report_date],
    )
    if existing:
        rows = [new_row if row.get("date") == report_date else row for row in rows]
        action = "replaced_existing_date"
    else:
        rows.append(new_row)
        action = "appended"
    rows.sort(key=lambda row: row.get("date") or "")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    return {
        "history_path": str(output_path),
        "action": action,
        "row_count": len(rows),
        "report_date": report_date,
        "latest_nav_eur": float(new_row["nav_eur"]),
        "latest_cash_eur": float(new_row["cash_eur"]),
        "latest_invested_market_value_eur": float(new_row["invested_market_value_eur"]),
        "equity_curve_meaningful": len(rows) >= 2 and (
            bool(state.get("positions")) or len({round(_f(row.get("nav_eur")), 2) for row in rows}) > 1
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Append or replace a validated Weekly ETF EU valuation-history observation.")
    parser.add_argument("--portfolio-state", default="output/etf_eu_portfolio_state.json")
    parser.add_argument("--history", default="output/etf_eu_valuation_history.csv")
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--source-report", required=True)
    parser.add_argument("--comment", default="Validated routine Weekly ETF EU valuation observation")
    parser.add_argument("--output", default="output/etf_eu_valuation_history.csv")
    args = parser.parse_args()
    result = update_history(
        state_path=Path(args.portfolio_state),
        history_path=Path(args.history),
        report_date=args.report_date,
        source_report=args.source_report,
        comment=args.comment,
        output_path=Path(args.output),
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
