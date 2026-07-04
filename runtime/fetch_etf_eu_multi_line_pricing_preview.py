from __future__ import annotations

import json
from pathlib import Path
from typing import Any

RUN_ID = "20260703_000000"
SOURCE = Path("output/client_surface/etf_eu_closing_price_poc_20260703_000000.json")
ARTIFACT = Path("output/client_surface/etf_eu_multi_line_pricing_preview_20260703_000000.json")


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sxr8_row(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "isin": source["isin"],
        "fund_name": source["fund_name"],
        "exchange": source["exchange"],
        "exchange_ticker": source["exchange_ticker"],
        "trading_currency": source["trading_currency"],
        "pricing_symbol": source["pricing_symbol"],
        "latest_close_date": source["latest_close_date"],
        "latest_close": source["latest_close"],
        "pricing_source": source["pricing_source"],
        "pricing_fetch_timestamp": source["pricing_fetch_timestamp"],
        "provider_status": source["provider_status"],
        "pricing_poc_status": source["pricing_poc_status"],
        "fake_price_used": False,
        "us_proxy_price_used": False,
        "line_status": "success",
        "line_reason": "successful_source_close_from_ETF_EU_WP15Y_FIX",
    }


def _skipped_row(
    *,
    isin: str,
    fund_name: str,
    exchange: str,
    exchange_ticker: str,
    trading_currency: str,
    pricing_symbol: str,
    reason: str,
) -> dict[str, Any]:
    return {
        "isin": isin,
        "fund_name": fund_name,
        "exchange": exchange,
        "exchange_ticker": exchange_ticker,
        "trading_currency": trading_currency,
        "pricing_symbol": pricing_symbol,
        "latest_close_date": None,
        "latest_close": None,
        "pricing_source": None,
        "pricing_fetch_timestamp": None,
        "provider_status": "skipped",
        "pricing_poc_status": "skipped_pending_registry_status",
        "fake_price_used": False,
        "us_proxy_price_used": False,
        "line_status": "skipped_pending_registry_status",
        "line_reason": reason,
    }


def build() -> dict[str, Any]:
    source = _load(SOURCE)
    rows = [
        _sxr8_row(source),
        _skipped_row(
            isin="IE00B5BMR087",
            fund_name="iShares Core S&P 500 UCITS ETF USD (Acc)",
            exchange="London Stock Exchange",
            exchange_ticker="CSPX",
            trading_currency="USD",
            pricing_symbol="CSPX.L",
            reason="registry line exists but pricing_status remains pending_pipeline_test; no committed provider close in this package",
        ),
        _skipped_row(
            isin="IE00BMC38736",
            fund_name="VanEck Semiconductor UCITS ETF",
            exchange="primary_line_pending_verification",
            exchange_ticker="SMH",
            trading_currency="USD",
            pricing_symbol="pending_verification",
            reason="pricing_symbol_yahoo is pending_verification and exchange line is not yet verified",
        ),
    ]
    success_count = sum(1 for row in rows if row["line_status"] == "success")
    failed_count = sum(1 for row in rows if row["line_status"] == "failed_provider_or_symbol_unavailable")
    skipped_count = sum(1 for row in rows if row["line_status"].startswith("skipped"))
    selected_next = "ETF-EU-WP15AA-FIX" if success_count < 2 else "ETF-EU-WP15AB"
    artifact = {
        "schema_version": "etf_eu_multi_line_pricing_preview_v1",
        "run_id": RUN_ID,
        "repository": "market-predictions/weekly-etf-eu",
        "work_package_id": "ETF-EU-WP15AA",
        "source_work_package": "ETF-EU-WP15Z",
        "source_single_line_preview_artifact": "output/client_surface/etf_eu_cockpit_closing_price_preview_20260703_000000.json",
        "source_single_line_pricing_artifact": str(SOURCE),
        "multi_line_pricing_created": True,
        "review_only": True,
        "pricing_rows": rows,
        "successful_rows_count": success_count,
        "failed_rows_count": failed_count,
        "skipped_rows_count": skipped_count,
        "mandatory_sxr8_success": True,
        "pdf_created": False,
        "pdf_reason": "binary_pdf_not_committed_or_not_rendered_in_this_package",
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
        "fake_price_used": False,
        "us_proxy_price_used": False,
        "selected_next_package": selected_next,
    }
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    return artifact


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
