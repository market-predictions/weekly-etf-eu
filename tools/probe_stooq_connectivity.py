from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pricing.ucits_close_price_multi_source_v2 import STOOQ_API_KEY_ENV, try_stooq_close_detailed


DEFAULT_SYMBOLS = (
    ("positive_control_us_equity", "AAPL.US"),
    ("funded_vwce_xetra", "VWCE.DE"),
    ("funded_euna_xetra", "EUNA.DE"),
    ("funded_sxr8_xetra", "SXR8.DE"),
    ("cross_venue_iwda_london", "IWDA.UK"),
)


def probe(symbol: str, report_date: date) -> dict[str, Any]:
    result = try_stooq_close_detailed(
        {"provider_symbol_stooq": symbol, "instrument_type": "UCITS ETF"},
        report_date,
    )
    return {
        "symbol": symbol.lower(),
        "pricing_status": result["pricing_status"],
        "close_date": result["close_date"],
        "close_price": result["close_price"],
        "response_classification": result["response_classification"],
        "api_key_supplied": result["api_key_supplied"],
        "http_status": result["http_status"],
        "content_type": result["content_type"],
        "response_bytes": result["response_bytes"],
        "csv_fieldnames": result["csv_fieldnames"],
        "valid_csv": result["valid_csv"],
        "blockers": result["blockers"],
    }


def determine(rows: list[dict[str, Any]], key_present: bool) -> str:
    control = rows[0]
    classification = control["response_classification"]
    if classification == "api_key_required" and not key_present:
        return "api_key_required_confirmed_by_positive_control"
    if classification == "valid_completed_close" and not key_present:
        return "api_key_not_required_for_current_runner"
    if classification == "valid_completed_close" and key_present:
        return "api_key_present_and_accepted_by_positive_control"
    if classification == "daily_limit_exceeded":
        return "stooq_daily_limit_exceeded"
    if key_present:
        return "api_key_present_but_positive_control_not_validated"
    return "inconclusive_positive_control_failed_for_non_auth_reason"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-date", default="2026-07-31")
    parser.add_argument("--output", default="output/stooq_probe/stooq_connectivity_probe.json")
    args = parser.parse_args()

    report_date = date.fromisoformat(args.report_date)
    key_present = bool(os.environ.get(STOOQ_API_KEY_ENV, "").strip())
    rows = []
    for label, symbol in DEFAULT_SYMBOLS:
        row = probe(symbol, report_date)
        row["label"] = label
        rows.append(row)

    payload = {
        "schema_version": "stooq_connectivity_probe_v1",
        "report_date": report_date.isoformat(),
        "api_key_environment_variable": STOOQ_API_KEY_ENV,
        "api_key_present": key_present,
        "determination": determine(rows, key_present),
        "rows": rows,
        "secret_value_logged": False,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "STOOQ_CONNECTIVITY_PROBE_OK"
        f" | output={output}"
        f" | determination={payload['determination']}"
        f" | key_present={key_present}"
        f" | valid_csv={sum(1 for row in rows if row['valid_csv'])}"
    )


if __name__ == "__main__":
    main()
