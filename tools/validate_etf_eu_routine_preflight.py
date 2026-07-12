from __future__ import annotations

import argparse
from pathlib import Path
from types import SimpleNamespace

from tools.build_etf_eu_routine_report_package import _markdown_en, _markdown_nl
from tools.write_etf_eu_routine_run_manifest import build_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate routine report imports and initial manifest contract.")
    parser.add_argument("--request", required=True)
    args = parser.parse_args()

    request = Path(args.request)
    if not request.exists():
        raise SystemExit(f"routine request missing: {request}")

    manifest = build_manifest(
        SimpleNamespace(
            run_id="preflight",
            report_date="2026-07-12",
            report_suffix="260712",
            routine_stage="preflight",
            workflow_status="preflight",
            workflow_conclusion=None,
            previous_delivery_closeout_manifest=None,
            portfolio_state="output/etf_eu_portfolio_state.json",
            valuation_history="output/etf_eu_valuation_history.csv",
            trade_ledger="output/etf_eu_trade_ledger.csv",
            recommendation_scorecard="output/etf_eu_recommendation_scorecard.csv",
            pricing_artifact=None,
            delivery_package_manifest=None,
            ready_artifact=None,
            delivery_closeout_manifest=None,
            dutch_primary_markdown=None,
            english_companion_markdown=None,
            dutch_primary_html=None,
            english_companion_html=None,
            dutch_primary_pdf=None,
            english_companion_pdf=None,
            send_executed="false",
            transport_attempted="false",
            transport_success="false",
            receipt_confirmed="false",
            valuation_grade="false",
            funding_authority="false",
            portfolio_mutation="false",
            production_delivery_authority="false",
            next_package=None,
        )
    )

    required_false = [
        "send_executed",
        "transport_attempted",
        "transport_success",
        "receipt_confirmed",
        "valuation_grade",
        "funding_authority",
        "portfolio_mutation",
        "production_delivery_authority",
    ]
    for key in required_false:
        if manifest.get(key) is not False:
            raise SystemExit(f"routine manifest preflight failed: {key} must be false")

    state = {
        "starting_capital_eur": 100000.0,
        "cash_eur": 100000.0,
        "invested_market_value_eur": 0.0,
        "nav_eur": 100000.0,
        "positions": [],
    }
    pricing = {"rows": []}
    if "send_executed=false" not in _markdown_nl("2026-07-12", state, pricing):
        raise SystemExit("Dutch report preflight missing send_executed=false")
    if "send_executed=false" not in _markdown_en("2026-07-12", state, pricing):
        raise SystemExit("English report preflight missing send_executed=false")

    print("ETF_EU_ROUTINE_PREFLIGHT_OK")


if __name__ == "__main__":
    main()
