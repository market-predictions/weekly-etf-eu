from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from runtime.build_etf_eu_routine_valuation_overlay import build


class RoutineValuationOverlayTests(unittest.TestCase):
    def test_fresh_close_reconciles_all_current_position_fields(self):
        portfolio = {
            "portfolio_mode": "dutch_eu_ucits_model_active",
            "inception_date": "2026-05-30",
            "starting_capital_eur": 100000.0,
            "cash_eur": 60439.44,
            "positions": [
                {
                    "ticker": "VWCE", "shares": 151, "avg_entry_local": 165.32,
                    "current_price_local": 164.28, "market_value_local": 24806.28,
                    "market_value_eur": 24806.28, "current_weight_pct": 24.866766,
                    "price_date": "2026-07-24", "last_valuation_report_date": "2026-07-27",
                    "last_valuation_run_id": "old-run", "trading_currency": "EUR",
                },
                {
                    "ticker": "EUNA", "shares": 1526, "avg_entry_local": 4.913,
                    "current_price_local": 4.8919, "market_value_local": 7465.04,
                    "market_value_eur": 7465.04, "current_weight_pct": 7.483242,
                    "price_date": "2026-07-24", "last_valuation_report_date": "2026-07-27",
                    "last_valuation_run_id": "old-run", "trading_currency": "EUR",
                },
                {
                    "ticker": "SXR8", "shares": 10, "avg_entry_local": 710.0,
                    "current_price_local": 704.6, "market_value_local": 7046.0,
                    "market_value_eur": 7046.0, "current_weight_pct": 7.06318,
                    "price_date": "2026-07-24", "last_valuation_report_date": "2026-07-27",
                    "last_valuation_run_id": "old-run", "trading_currency": "EUR",
                },
            ],
        }
        pricing = {
            "run_id": "pricing-run",
            "report_date": "2026-07-31",
            "line_count": 12,
            "priced_line_count": 12,
            "rows": [
                {"ticker": "VWCE", "pricing_status": "priced_non_authoritative", "close_price": 162.96000335, "close_date": "2026-07-31", "currency": "EUR", "source_name": "Development provider consensus", "source_quality_status": "development_consensus"},
                {"ticker": "EUNA", "pricing_status": "priced_non_authoritative", "close_price": 4.88000006, "close_date": "2026-07-31", "currency": "EUR", "source_name": "Development provider consensus", "source_quality_status": "development_consensus"},
                {"ticker": "SXR8", "pricing_status": "priced_non_authoritative", "close_price": 696.23999512, "close_date": "2026-07-31", "currency": "EUR", "source_name": "Development provider consensus", "source_quality_status": "development_consensus"},
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            portfolio_path = Path(tmp) / "portfolio.json"
            ledger_path = Path(tmp) / "ledger.csv"
            portfolio_path.write_text(json.dumps(portfolio), encoding="utf-8")
            ledger_path.write_text("trade_id\n", encoding="utf-8")
            result = build(portfolio, pricing, portfolio_path, ledger_path, "2026-07-31", "new-run")

        self.assertEqual(result["nav_eur"], 99455.68)
        rows = {row["ticker"]: row for row in result["positions"]}
        vwce = rows["VWCE"]
        self.assertEqual(vwce["current_price_local"], 162.96000335)
        self.assertEqual(vwce["current_price_eur"], 162.96000335)
        self.assertEqual(vwce["market_value_local"], 24606.96)
        self.assertEqual(vwce["market_value_eur"], 24606.96)
        self.assertEqual(vwce["price_date"], "2026-07-31")
        self.assertEqual(vwce["pricing_close_date"], "2026-07-31")
        self.assertEqual(vwce["previous_price_local"], 164.28)
        self.assertEqual(vwce["previous_market_value_eur"], 24806.28)
        self.assertEqual(vwce["unrealized_pnl_eur"], -356.36)
        self.assertAlmostEqual(vwce["unrealized_pnl_pct"], -1.427532, places=6)
        self.assertEqual(vwce["portfolio_contribution_eur"], -199.32)
        self.assertEqual(vwce["last_valuation_report_date"], "2026-07-31")
        self.assertEqual(vwce["last_valuation_run_id"], "new-run")
        self.assertEqual(vwce["current_weight_pct"], vwce["weight_pct"])
        self.assertAlmostEqual(
            sum(float(row["portfolio_contribution_eur"]) for row in rows.values()),
            result["nav_eur"] - 99756.76,
            places=2,
        )


if __name__ == "__main__":
    unittest.main()
