from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

import requests

BASE_URL = "https://api.boerse-frankfurt.de"
TRACE_SALT = "w4icATTGtnjAQMbkL3kJwxLfEAKDa3VU"
BERLIN = ZoneInfo("Europe/Berlin")
TIMEOUT_SECONDS = 30
LINES = (
    {"ticker": "VVSM", "isin": "IE00BMC38736", "mic": "XETR"},
    {"ticker": "L0CK", "isin": "IE00BG0J4C88", "mic": "XETR"},
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_text(value: datetime | None = None) -> str:
    current = value or utc_now()
    return current.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def positive_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and number > 0 else None


def positive_int(value: Any) -> int | None:
    number = positive_float(value)
    return int(number) if number is not None else None


def headers(url: str) -> dict[str, str]:
    current = utc_now()
    client_date = current.isoformat(timespec="milliseconds").replace("+00:00", "Z")
    trace = hashlib.md5((client_date + url + TRACE_SALT).encode("utf-8")).hexdigest()
    security = hashlib.md5(datetime.now().astimezone().strftime("%Y%m%d%H%M").encode("utf-8")).hexdigest()
    return {
        "Accept": "application/json, text/plain, */*",
        "Client-Date": client_date,
        "X-Client-TraceId": trace,
        "X-Security": security,
        "Referer": "https://www.boerse-frankfurt.de/",
        "User-Agent": "Mozilla/5.0 Weekly-ETF-EU-Stage1-Quote/1.0",
    }


def parse_timestamp(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def fetch_line(line: dict[str, str], report_date: date) -> dict[str, Any]:
    params = urlencode({"isin": line["isin"], "mic": line["mic"]})
    url = f"{BASE_URL}/v1/data/quote_box/single?{params}"
    observed = utc_now()
    result: dict[str, Any] = {
        **line,
        "observed_at_utc": utc_text(observed),
        "source": "Deutsche Boerse Frankfurt/Xetra quote_box",
        "source_url_contract": "/v1/data/quote_box/single?isin=<ISIN>&mic=<MIC>",
        "status": "fetch_failed",
        "http_status": None,
        "quote_timestamp_utc": None,
        "quote_timestamp_berlin": None,
        "bid_eur": None,
        "ask_eur": None,
        "bid_size": None,
        "ask_size": None,
        "spread_absolute_eur": None,
        "spread_pct_mid": None,
        "last_price_eur": None,
        "trading_status": None,
        "blockers": [],
    }
    try:
        response = requests.get(url, headers=headers(url), timeout=TIMEOUT_SECONDS)
        result["http_status"] = response.status_code
        payload = response.json()
    except Exception as exc:
        result["blockers"] = [f"request_exception:{type(exc).__name__}"]
        return result
    if response.status_code != 200 or not isinstance(payload, dict):
        result["blockers"] = [f"provider_error:{response.status_code}"]
        return result

    returned_isin = str(payload.get("isin") or "").strip().upper()
    timestamp = parse_timestamp(payload.get("timestamp"))
    bid = positive_float(payload.get("bidLimit"))
    ask = positive_float(payload.get("askLimit"))
    bid_size = positive_int(payload.get("bidSize"))
    ask_size = positive_int(payload.get("askSize"))
    blockers: list[str] = []
    if returned_isin != line["isin"]:
        blockers.append("returned_isin_mismatch")
    if timestamp is None:
        blockers.append("quote_timestamp_missing")
    elif timestamp.astimezone(BERLIN).date() != report_date:
        blockers.append("quote_not_from_report_date")
    if bid is None or ask is None or ask < bid:
        blockers.append("invalid_bid_ask")
    if bid_size is None or ask_size is None:
        blockers.append("invalid_quote_size")

    spread_absolute = round(ask - bid, 8) if bid is not None and ask is not None else None
    midpoint = (ask + bid) / 2.0 if bid is not None and ask is not None else None
    spread_pct = round(spread_absolute / midpoint * 100.0, 8) if spread_absolute is not None and midpoint else None
    if spread_pct is not None and spread_pct > 1.0:
        blockers.append("spread_above_one_percent")

    result.update(
        {
            "returned_isin": returned_isin or None,
            "quote_timestamp_utc": utc_text(timestamp) if timestamp else None,
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
            "blockers": blockers,
            "status": "qualified_timestamped_exact_line_quote" if not blockers else "quote_rejected",
        }
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report_date = date.fromisoformat(args.report_date)
    rows = [fetch_line(dict(line), report_date) for line in LINES]
    payload = {
        "schema_version": "etf_eu_stage1_quote_evidence_v1",
        "artifact_type": "etf_eu_stage1_quote_evidence",
        "generated_at_utc": utc_text(),
        "run_id": args.run_id,
        "report_date": report_date.isoformat(),
        "line_count": len(rows),
        "qualified_line_count": sum(row["status"] == "qualified_timestamped_exact_line_quote" for row in rows),
        "portfolio_mutation": False,
        "funding_authority": False,
        "real_broker_execution": False,
        "rows": rows,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "ETF_EU_STAGE1_QUOTE_EVIDENCE_OK"
        f" | qualified={payload['qualified_line_count']}/{payload['line_count']}"
        f" | output={output}"
    )
    if payload["qualified_line_count"] != payload["line_count"]:
        raise SystemExit("Stage-1 quote evidence gate failed")


if __name__ == "__main__":
    main()
