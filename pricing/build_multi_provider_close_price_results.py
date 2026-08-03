from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import yaml

from pricing.provider_close_price_engine import PROVIDERS, qualify_line, utc_now


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--basket", default="config/ucits_close_price_validation_basket.yml")
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    basket = yaml.safe_load(Path(args.basket).read_text(encoding="utf-8")) or {}
    report_date = date.fromisoformat(args.report_date)
    lines = [dict(item) for item in basket.get("trading_lines", [])]
    rows = [qualify_line(line, report_date) for line in lines]
    funded_ids = {"vwce_xetra_eur", "euna_xetra_eur", "sxr8_xetra_eur"}
    funded = [row for row in rows if row.get("basket_id") in funded_ids]
    provider_summary = {}
    for provider_id, _ in PROVIDERS:
        attempts = [
            attempt
            for row in rows
            for attempt in row["provider_attempts"]
            if attempt["provider_id"] == provider_id
        ]
        provider_summary[provider_id] = {
            "attempted": sum(1 for item in attempts if item["pricing_status"] != "provider_skipped"),
            "priced": sum(1 for item in attempts if item["pricing_status"] == "priced_non_authoritative"),
            "skipped": sum(1 for item in attempts if item["pricing_status"] == "provider_skipped"),
            "rate_limited": sum(1 for item in attempts if item["response_classification"] == "rate_limited"),
        }
    payload = {
        "schema_version": "multi_provider_close_price_results_v1",
        "generated_at_utc": utc_now(),
        "report_date": report_date.isoformat(),
        "provider_order": [provider_id for provider_id, _ in PROVIDERS],
        "line_count": len(rows),
        "priced_line_count": sum(1 for row in rows if row["pricing_status"] == "priced_non_authoritative"),
        "funded_position_count": len(funded),
        "funded_position_priced_count": sum(1 for row in funded if row["pricing_status"] == "priced_non_authoritative"),
        "funded_position_coverage_complete": bool(funded) and all(row["pricing_status"] == "priced_non_authoritative" for row in funded),
        "provider_summary": provider_summary,
        "portfolio_mutation": False,
        "ledger_write": False,
        "delivery_authority": False,
        "rows": rows,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "MULTI_PROVIDER_CLOSE_PRICE_RESULTS_OK"
        f" | output={output}"
        f" | priced={payload['priced_line_count']}/{payload['line_count']}"
        f" | funded={payload['funded_position_priced_count']}/{payload['funded_position_count']}"
    )


if __name__ == "__main__":
    main()
