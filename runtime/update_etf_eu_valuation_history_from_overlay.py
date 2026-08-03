from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


FIELDS = [
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


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = [dict(row) for row in csv.DictReader(handle)]
    for row in rows:
        for field in FIELDS:
            row.setdefault(field, "")
    return rows


def apply(history_path: Path, overlay_path: Path, source_report: str) -> None:
    overlay = load(overlay_path)
    if overlay.get("schema_version") != "etf_eu_routine_valuation_overlay_v1":
        raise RuntimeError("Unexpected valuation overlay schema")
    report_date = str(overlay.get("report_date") or "")
    if not report_date:
        raise RuntimeError("Valuation overlay report date is missing")

    rows = [row for row in read_rows(history_path) if str(row.get("date") or "") != report_date]
    rows.sort(key=lambda row: str(row.get("date") or ""))
    nav = float(overlay.get("nav_eur") or 0)
    starting = float(overlay.get("starting_capital_eur") or 0)
    prior_nav = float(rows[-1].get("nav_eur") or 0) if rows else 0.0
    daily_return = ((nav / prior_nav) - 1.0) * 100.0 if prior_nav else 0.0
    peak = max([float(row.get("nav_eur") or 0) for row in rows] + [nav])
    drawdown = ((nav / peak) - 1.0) * 100.0 if peak else 0.0
    since = ((nav / starting) - 1.0) * 100.0 if starting else 0.0

    rows.append(
        {
            "date": report_date,
            "nav_eur": f"{nav:.2f}",
            "cash_eur": f"{float(overlay.get('cash_eur') or 0):.2f}",
            "invested_market_value_eur": f"{float(overlay.get('invested_market_value_eur') or 0):.2f}",
            "daily_return_pct": f"{daily_return:.6f}",
            "since_inception_return_pct": f"{since:.6f}",
            "drawdown_pct": f"{drawdown:.6f}",
            "comment": "Fresh run-scoped valuation from completed EUR closes; official shares and cash unchanged.",
            "source_report": source_report,
        }
    )
    rows.sort(key=lambda row: str(row.get("date") or ""))
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with history_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(history_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--history", type=Path, default=Path("output/etf_eu_valuation_history.csv"))
    parser.add_argument("--overlay", type=Path, required=True)
    parser.add_argument("--source-report", required=True)
    args = parser.parse_args()
    apply(args.history, args.overlay, args.source_report)


if __name__ == "__main__":
    main()
