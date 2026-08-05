from __future__ import annotations

import argparse
import json
import math
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

BERLIN = ZoneInfo("Europe/Berlin")
EXPECTED = {
    "VVSM": {"isin": "IE00BMC38736", "mic": "XETR"},
    "L0CK": {"isin": "IE00BG0J4C88", "mic": "XETR"},
}


def load_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def positive_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and number > 0 else None


def positive_int(value: Any) -> int | None:
    number = positive_float(value)
    return int(number) if number is not None else None


def parse_timestamp(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--source-workflow-run", required=True)
    parser.add_argument("--source-artifact-id", required=True)
    parser.add_argument("--source-artifact-sha256", required=True)
    args = parser.parse_args()

    report_date = date.fromisoformat(args.report_date)
    source = load_object(Path(args.input))
    rows: list[dict[str, Any]] = []
    for raw in source.get("rows") or []:
        if not isinstance(raw, dict):
            continue
        ticker = str(raw.get("ticker") or "").strip().upper()
        expected = EXPECTED.get(ticker)
        if expected is None:
            continue
        exchange = raw.get("boerse_quote_box") if isinstance(raw.get("boerse_quote_box"), dict) else {}
        payload = exchange.get("payload") if isinstance(exchange.get("payload"), dict) else {}
        returned_isin = str(payload.get("isin") or raw.get("isin") or "").strip().upper()
        returned_mic = str(raw.get("mic") or "").strip().upper()
        timestamp = parse_timestamp(payload.get("timestamp") or raw.get("observed_at_utc"))
        bid = positive_float(payload.get("bidLimit"))
        ask = positive_float(payload.get("askLimit"))
        bid_size = positive_int(payload.get("bidSize"))
        ask_size = positive_int(payload.get("askSize"))
        blockers: list[str] = []
        if returned_isin != expected["isin"]:
            blockers.append("returned_isin_mismatch")
        if returned_mic != expected["mic"]:
            blockers.append("returned_mic_mismatch")
        if timestamp is None:
            blockers.append("quote_timestamp_missing")
        elif timestamp.astimezone(BERLIN).date() != report_date:
            blockers.append("quote_not_from_report_date")
        if bid is None or ask is None or ask < bid:
            blockers.append("invalid_bid_ask")
        if bid_size is None or ask_size is None:
            blockers.append("invalid_quote_size")
        spread_absolute = round(ask - bid, 8) if bid is not None and ask is not None else None
        midpoint = (ask + bid) / 2 if bid is not None and ask is not None else None
        spread_pct = round(spread_absolute / midpoint * 100, 8) if spread_absolute is not None and midpoint else None
        if spread_pct is not None and spread_pct > 1.0:
            blockers.append("spread_above_one_percent")
        rows.append(
            {
                "ticker": ticker,
                "isin": expected["isin"],
                "mic": expected["mic"],
                "observed_at_utc": raw.get("observed_at_utc"),
                "quote_timestamp_utc": timestamp.isoformat().replace("+00:00", "Z") if timestamp else None,
                "quote_timestamp_berlin": timestamp.astimezone(BERLIN).isoformat() if timestamp else None,
                "bid_eur": bid,
                "ask_eur": ask,
                "bid_size": bid_size,
                "ask_size": ask_size,
                "spread_absolute_eur": spread_absolute,
                "spread_pct_mid": spread_pct,
                "last_price_eur": positive_float(payload.get("lastPrice")),
                "last_price_timestamp": payload.get("timestampLastPrice"),
                "trading_status": payload.get("tradingStatus"),
                "instrument_status": payload.get("instrumentStatus"),
                "status": "qualified_timestamped_exact_line_quote" if not blockers else "quote_rejected",
                "blockers": blockers,
                "source": "immutable GitHub Actions Stage-1 quote probe artifact",
            }
        )

    tickers = {row["ticker"] for row in rows}
    if tickers != set(EXPECTED):
        raise RuntimeError(f"Quote artifact ticker set mismatch: {sorted(tickers)}")
    qualified = sum(row["status"] == "qualified_timestamped_exact_line_quote" for row in rows)
    payload = {
        "schema_version": "etf_eu_stage1_quote_evidence_v1",
        "artifact_type": "etf_eu_stage1_quote_evidence",
        "run_id": args.run_id,
        "report_date": report_date.isoformat(),
        "line_count": len(rows),
        "qualified_line_count": qualified,
        "source_provenance": {
            "workflow_run_id": str(args.source_workflow_run),
            "artifact_id": str(args.source_artifact_id),
            "artifact_sha256": str(args.source_artifact_sha256),
            "source_file": str(args.input),
            "immutable_capture": True,
        },
        "portfolio_mutation": False,
        "funding_authority": False,
        "real_broker_execution": False,
        "rows": rows,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"ETF_EU_STAGE1_IMMUTABLE_QUOTE_EVIDENCE_OK | qualified={qualified}/{len(rows)} | output={output}")
    if qualified != len(EXPECTED):
        raise SystemExit("Immutable Stage-1 quote evidence gate failed")


if __name__ == "__main__":
    main()
