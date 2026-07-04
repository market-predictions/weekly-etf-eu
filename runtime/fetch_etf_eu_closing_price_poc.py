from __future__ import annotations

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RUN_ID = "20260703_000000"
REGISTRY = Path("config/ucits_symbol_registry.yml")
ARTIFACT = Path("output/client_surface/etf_eu_closing_price_poc_20260703_000000.json")
PREVIEW = Path("output/client_surface/etf_eu_closing_price_poc_preview_20260703_000000.md")
TARGET_ISIN = "IE00B5BMR087"
TARGET_SYMBOL = "SXR8.DE"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _extract_target_from_registry(text: str) -> dict[str, str]:
    if TARGET_ISIN not in text or TARGET_SYMBOL not in text:
        raise RuntimeError("target SXR8.DE / IE00B5BMR087 not found in registry")
    return {
        "isin": TARGET_ISIN,
        "fund_name": "iShares Core S&P 500 UCITS ETF USD (Acc)",
        "exchange": "Xetra",
        "exchange_ticker": "SXR8",
        "trading_currency": "EUR",
        "pricing_symbol": TARGET_SYMBOL,
        "symbol": TARGET_SYMBOL,
    }


def _fetch_yahoo_chart_close(symbol: str) -> dict[str, Any]:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=10d&interval=1d"
    request = urllib.request.Request(url, headers={"User-Agent": "weekly-etf-eu-pricing-poc/1.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))
    result = payload.get("chart", {}).get("result") or []
    if not result:
        raise RuntimeError("provider returned no chart result")
    series = result[0]
    timestamps = series.get("timestamp") or []
    quote = (((series.get("indicators") or {}).get("quote") or [{}])[0])
    closes = quote.get("close") or []
    valid = [(ts, close) for ts, close in zip(timestamps, closes) if close is not None]
    if not valid:
        raise RuntimeError("provider returned no non-null close values")
    ts, close = valid[-1]
    close_date = datetime.fromtimestamp(int(ts), tz=timezone.utc).date().isoformat()
    return {
        "latest_close_date": close_date,
        "latest_close": round(float(close), 6),
        "pricing_source": "yahoo_chart_v8",
        "pricing_freshness_status": "latest_available_daily_close_from_provider",
    }


def _base_artifact(target: dict[str, str]) -> dict[str, Any]:
    return {
        "schema_version": "etf_eu_closing_price_poc_v1",
        "run_id": RUN_ID,
        "repository": "market-predictions/weekly-etf-eu",
        "work_package_id": "ETF-EU-WP15Y",
        "legacy_work_package_id": "WP15Y",
        "status": "completed_after_closing_price_poc_attempt",
        "symbol": TARGET_SYMBOL,
        "isin": target["isin"],
        "fund_name": target["fund_name"],
        "exchange": target["exchange"],
        "exchange_ticker": target["exchange_ticker"],
        "trading_currency": target["trading_currency"],
        "pricing_symbol": target["pricing_symbol"],
        "pricing_fetch_timestamp": _utc_now(),
        "latest_close_date": None,
        "latest_close": None,
        "pricing_source": None,
        "pricing_freshness_status": None,
        "provider_status": "failed",
        "provider_error": None,
        "pricing_poc_status": "failed_provider_or_symbol_unavailable",
        "limited_pricing_poc_performed": True,
        "valuation_grade": False,
        "pricing_evidence_for_client_grade": False,
        "pricing_evidence_for_delivery_preflight": False,
        "production_delivery": False,
        "portfolio_mutation": False,
        "candidate_promotion": False,
        "funding_authority": False,
        "client_grade_claim": False,
        "client_grade_enough_for_delivery_preflight_discussion": False,
        "delivery_ready": False,
        "delivery_authorization_decision": "remain_blocked",
        "delivery_preflight_allowed": False,
        "outbound_path_enabled": False,
        "recommendation_logic_changed": False,
        "client_distribution_claimed": False,
        "receipt_artifact_created": False,
        "production_manifest_created": False,
        "source_pdf_replaced": False,
        "renderer_changed": False,
        "fake_price_used": False,
        "us_proxy_price_used": False,
        "selected_next_package": "ETF-EU-WP15Y-FIX",
        "selected_next_package_title": "ETF EU closing-price POC provider/symbol repair, no delivery",
    }


def _preview(data: dict[str, Any]) -> str:
    close_date = data.get("latest_close_date") or "—"
    close = data.get("latest_close")
    close_text = "—" if close is None else str(close)
    source = data.get("pricing_source") or "—"
    status = data.get("provider_status") or "failed"
    next_step = "Render this successful close into a cockpit PDF preview surface." if status == "success" else "Repair provider access or symbol mapping until one real SXR8.DE closing-price POC succeeds."
    return f"""# ETF EU Closing Price POC

## What this proves

This proof-of-concept attempts to connect one ISIN-first EU UCITS registry line to a provider close: **SXR8.DE / IE00B5BMR087**.

## Closing price result

| ISIN | Fund | Trading line | Currency | Latest close date | Latest close | Source | Status |
|---|---|---|---|---:|---:|---|---|
| {data['isin']} | {data['fund_name']} | {data['pricing_symbol']} | {data['trading_currency']} | {close_date} | {close_text} | {source} | {status} |

## What this does not prove

This is a limited proof-of-concept, not valuation-grade pricing and not delivery-ready evidence.

It does not create a funded holding, portfolio valuation, recommendation change, client-grade claim, or delivery-preflight authority.

## Next step

{next_step}
"""


def run() -> dict[str, Any]:
    target = _extract_target_from_registry(REGISTRY.read_text(encoding="utf-8"))
    data = _base_artifact(target)
    try:
        close = _fetch_yahoo_chart_close(TARGET_SYMBOL)
        data.update(close)
        data["provider_status"] = "success"
        data["provider_error"] = None
        data["pricing_poc_status"] = "success_non_valuation_grade_close_obtained"
        data["selected_next_package"] = "ETF-EU-WP15Z"
        data["selected_next_package_title"] = "ETF EU cockpit PDF closing-price preview surface, no delivery"
    except Exception as exc:
        data["provider_status"] = "failed"
        data["provider_error"] = f"{type(exc).__name__}: {exc}"
        data["pricing_poc_status"] = "failed_provider_or_symbol_unavailable"
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    PREVIEW.write_text(_preview(data), encoding="utf-8")
    return data


if __name__ == "__main__":
    result = run()
    print(json.dumps({"provider_status": result["provider_status"], "pricing_poc_status": result["pricing_poc_status"]}, indent=2))
    sys.exit(0)
