from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "yahoo_cross_source_gate_v1"
DEFAULT_TOLERANCE_PCT = 0.25


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def to_float(value: Any) -> float | None:
    try:
        result = float(value)
    except Exception:
        return None
    return result if result > 0 else None


def line_key(row: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(row.get("registry_id") or ""),
        str(row.get("exchange") or ""),
        str(row.get("exchange_ticker") or ""),
        str(row.get("trading_currency") or ""),
    )


def twelve_rows_by_key(twelve: dict[str, Any]) -> dict[tuple[str, str, str, str], dict[str, Any]]:
    rows: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for row in twelve.get("rows", []) or []:
        if not isinstance(row, dict):
            continue
        key = line_key(row)
        rows[key] = row
    return rows


def best_twelve_time_series(row: dict[str, Any]) -> dict[str, Any] | None:
    for attempt in row.get("attempts", []) or []:
        if not isinstance(attempt, dict):
            continue
        ts = attempt.get("time_series") if isinstance(attempt.get("time_series"), dict) else None
        if ts and ts.get("latest_close") is not None and ts.get("latest_datetime"):
            return ts
    for attempt in row.get("attempts", []) or []:
        if not isinstance(attempt, dict):
            continue
        ts = attempt.get("time_series") if isinstance(attempt.get("time_series"), dict) else None
        if ts:
            return ts
    return None


def evaluate_row(yahoo_row: dict[str, Any], completed_row: dict[str, Any] | None, twelve_row: dict[str, Any] | None) -> dict[str, Any]:
    observed = yahoo_row.get("observed") if isinstance(yahoo_row.get("observed"), dict) else {}
    yahoo_close = to_float(observed.get("observed_last_close"))
    yahoo_date = observed.get("observed_last_close_date")
    yahoo_currency = observed.get("observed_currency")
    td_series = best_twelve_time_series(twelve_row or {}) if twelve_row else None
    td_close = to_float(td_series.get("latest_close")) if td_series else None
    td_date = td_series.get("latest_datetime") if td_series else None
    td_status = td_series.get("status") if td_series else "no_twelve_data_row_for_trading_line"
    td_message = td_series.get("provider_message") if td_series else None
    td_currency = None
    if twelve_row:
        td_currency = twelve_row.get("expected_currency") or twelve_row.get("trading_currency")
    pct_diff = None
    if yahoo_close and td_close:
        pct_diff = abs(yahoo_close - td_close) / yahoo_close * 100.0
    gates = {
        "same_registry_line": bool(twelve_row and line_key(yahoo_row) == line_key(twelve_row)),
        "yahoo_close_present": yahoo_close is not None and bool(yahoo_date),
        "completed_session_validated": bool(completed_row and completed_row.get("completed_session_validated") is True),
        "independent_source_close_present": td_close is not None and bool(td_date),
        "independent_source_currency_matches": bool(td_currency and yahoo_currency and str(td_currency).upper() == str(yahoo_currency).upper()),
        "same_close_date": bool(td_date and yahoo_date and str(td_date)[:10] == str(yahoo_date)[:10]),
        "within_tolerance": pct_diff is not None and pct_diff <= DEFAULT_TOLERANCE_PCT,
    }
    failed = [key for key, passed in gates.items() if passed is not True]
    return {
        "registry_id": yahoo_row.get("registry_id"),
        "isin": yahoo_row.get("isin"),
        "exchange": yahoo_row.get("exchange"),
        "exchange_ticker": yahoo_row.get("exchange_ticker"),
        "trading_currency": yahoo_row.get("trading_currency"),
        "provider_symbol": yahoo_row.get("provider_symbol"),
        "yahoo_symbol": yahoo_row.get("yahoo_symbol"),
        "yahoo_close": yahoo_close,
        "yahoo_close_date": yahoo_date,
        "yahoo_currency": yahoo_currency,
        "independent_source_id": "twelve_data",
        "independent_source_available": twelve_row is not None,
        "independent_close": td_close,
        "independent_close_date": td_date,
        "independent_currency": td_currency,
        "independent_status": td_status,
        "independent_provider_message": td_message,
        "tolerance_pct": DEFAULT_TOLERANCE_PCT,
        "pct_difference": pct_diff,
        "gates": gates,
        "failed_gates": failed,
        "cross_source_check_passed": len(failed) == 0,
        "diagnostic_status": "cross_source_passed" if len(failed) == 0 else "cross_source_blocked",
        "diagnostic_only": True,
        "valuation_authority": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
    }


def build(yahoo_diagnostics: Path, completed_session_gate: Path, twelve_data_discovery: Path, output_dir: Path, run_id: str) -> Path:
    yahoo = load_json(yahoo_diagnostics)
    completed = load_json(completed_session_gate)
    twelve = load_json(twelve_data_discovery)
    completed_by_key = {line_key(row): row for row in completed.get("rows", []) if isinstance(row, dict)}
    twelve_by_key = twelve_rows_by_key(twelve)
    rows = []
    for row in yahoo.get("rows", []) or []:
        if not isinstance(row, dict):
            continue
        key = line_key(row)
        rows.append(evaluate_row(row, completed_by_key.get(key), twelve_by_key.get(key)))
    payload = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_yahoo_diagnostics": str(yahoo_diagnostics),
        "source_completed_session_gate": str(completed_session_gate),
        "source_twelve_data_discovery": str(twelve_data_discovery),
        "diagnostic_only": True,
        "valuation_authority": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "cross_source_passed_count": sum(1 for row in rows if row.get("cross_source_check_passed") is True),
            "cross_source_blocked_count": sum(1 for row in rows if row.get("cross_source_check_passed") is not True),
            "authority_note": "Cross-source check is diagnostic-only and does not create Yahoo valuation authority.",
        },
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"yahoo_cross_source_gate_{run_id}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"YAHOO_CROSS_SOURCE_GATE_OK | artifact={path} | rows={len(rows)}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--yahoo-diagnostics", required=True)
    parser.add_argument("--completed-session-gate", required=True)
    parser.add_argument("--twelve-data-discovery", required=True)
    parser.add_argument("--output-dir", default="output/pricing")
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    build(Path(args.yahoo_diagnostics), Path(args.completed_session_gate), Path(args.twelve_data_discovery), Path(args.output_dir), args.run_id)


if __name__ == "__main__":
    main()
