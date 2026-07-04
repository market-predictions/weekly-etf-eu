from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RUN_ID = "20260703_000000"
BASE = Path("output/client_surface/etf_eu_multi_line_pricing_preview_20260703_000000.json")
OUT = Path("output/client_surface/etf_eu_multi_line_pricing_universe_repair_20260703_000000.json")
TARGET = "CSPX.L"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _fetch(symbol: str) -> dict[str, Any]:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=10d&interval=1d"
    req = urllib.request.Request(url, headers={"User-Agent": "weekly-etf-eu/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    result = payload.get("chart", {}).get("result") or []
    if not result:
        raise RuntimeError("no chart result")
    series = result[0]
    timestamps = series.get("timestamp") or []
    quote = (((series.get("indicators") or {}).get("quote") or [{}])[0])
    closes = quote.get("close") or []
    valid = [(ts, close) for ts, close in zip(timestamps, closes) if close is not None]
    if not valid:
        raise RuntimeError("no non-null close")
    ts, close = valid[-1]
    return {
        "latest_close_date": datetime.fromtimestamp(int(ts), tz=timezone.utc).date().isoformat(),
        "latest_close": round(float(close), 6),
        "pricing_source": "yahoo_chart_v8",
        "pricing_fetch_timestamp": _now(),
    }


def run() -> dict[str, Any]:
    base = json.loads(BASE.read_text(encoding="utf-8"))
    attempts = []
    try:
        close = _fetch(TARGET)
        attempts.append({"provider": "yahoo_chart_v8", "symbol": TARGET, "status": "success", **close})
        data = {
            "schema_version": "etf_eu_multi_line_pricing_universe_repair_v1",
            "run_id": RUN_ID,
            "repository": "market-predictions/weekly-etf-eu",
            "work_package_id": "ETF-EU-WP15AA-FIX",
            "source_work_package": "ETF-EU-WP15AA",
            "repair_status": "success",
            "repair_target": TARGET,
            "provider_attempts": attempts,
            "successful_provider": "yahoo_chart_v8",
            "successful_second_line_symbol": TARGET,
            "successful_second_line_isin": "IE00B5BMR087",
            "successful_second_line_close_date": close["latest_close_date"],
            "successful_second_line_close": close["latest_close"],
            "successful_second_line_pricing_source": close["pricing_source"],
            "successful_rows_count": 2,
            "failed_rows_count": 0,
            "skipped_rows_count": 1,
            "mandatory_sxr8_success": True,
            "at_least_one_additional_verified_eu_line_success": True,
            "fake_price_used": False,
            "us_proxy_price_used": False,
            "review_only": True,
            "valuation_grade": False,
            "pricing_evidence_for_client_grade": False,
            "pricing_evidence_for_delivery_preflight": False,
            "production_delivery": False,
            "portfolio_mutation": False,
            "candidate_promotion": False,
            "funding_authority": False,
            "client_grade_claim": False,
            "delivery_ready": False,
            "delivery_preflight_allowed": False,
            "receipt_artifact_created": False,
            "production_manifest_created": False,
            "selected_next_package": "ETF-EU-WP15AB",
        }
    except Exception as exc:
        attempts.append({"provider": "yahoo_chart_v8", "symbol": TARGET, "status": "failed", "error": f"{type(exc).__name__}: {exc}"})
        data = {
            "schema_version": "etf_eu_multi_line_pricing_universe_repair_v1",
            "run_id": RUN_ID,
            "repository": "market-predictions/weekly-etf-eu",
            "work_package_id": "ETF-EU-WP15AA-FIX",
            "source_work_package": "ETF-EU-WP15AA",
            "repair_status": "failed_second_line_not_obtained",
            "repair_target": TARGET,
            "provider_attempts": attempts,
            "successful_provider": None,
            "successful_second_line_symbol": None,
            "successful_second_line_isin": None,
            "successful_second_line_close_date": None,
            "successful_second_line_close": None,
            "successful_second_line_pricing_source": None,
            "successful_rows_count": base.get("successful_rows_count", 1),
            "failed_rows_count": 1,
            "skipped_rows_count": base.get("skipped_rows_count", 2),
            "mandatory_sxr8_success": True,
            "at_least_one_additional_verified_eu_line_success": False,
            "fake_price_used": False,
            "us_proxy_price_used": False,
            "review_only": True,
            "valuation_grade": False,
            "pricing_evidence_for_client_grade": False,
            "pricing_evidence_for_delivery_preflight": False,
            "production_delivery": False,
            "portfolio_mutation": False,
            "candidate_promotion": False,
            "funding_authority": False,
            "client_grade_claim": False,
            "delivery_ready": False,
            "delivery_preflight_allowed": False,
            "receipt_artifact_created": False,
            "production_manifest_created": False,
            "selected_next_package": "ETF-EU-WP15AA-FIX-2",
        }
    OUT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
