from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import yaml

from pricing.ucits_funded_universe import resolve_provider_registry_funded_universe


class FundedUniverseTests(unittest.TestCase):
    def test_portfolio_state_overrides_stale_registry_flags(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = root / "registry.yml"
            portfolio = root / "portfolio.json"
            resolved = root / "resolved.yml"

            registry.write_text(yaml.safe_dump({
                "provider_order": ["yahoo_chart"],
                "trading_lines": [
                    {"basket_id": "vwce_xetra_eur", "funded": True, "isin": "IE00BK5BQT80", "ticker": "VWCE", "exchange": "Xetra", "currency": "EUR"},
                    {"basket_id": "l0ck_xetra_eur", "funded": False, "isin": "IE00BG0J4C88", "ticker": "L0CK", "exchange": "Xetra", "currency": "EUR"},
                    {"basket_id": "watch_xetra_eur", "funded": True, "isin": "IE0000000001", "ticker": "WATCH", "exchange": "Xetra", "currency": "EUR"},
                ],
            }, sort_keys=False), encoding="utf-8")
            portfolio.write_text(json.dumps({
                "schema_version": "etf_eu_portfolio_state_v2",
                "portfolio_mode": "dutch_eu_ucits_model_active",
                "model_portfolio_only": True,
                "real_broker_execution": False,
                "positions": [
                    {"investability_status": "funded_model_position", "isin": "IE00BK5BQT80", "exchange_ticker": "VWCE", "primary_exchange": "Xetra", "trading_currency": "EUR"},
                    {"investability_status": "funded_model_position", "isin": "IE00BG0J4C88", "exchange_ticker": "L0CK", "primary_exchange": "Xetra", "trading_currency": "EUR"},
                ],
            }), encoding="utf-8")

            authority = resolve_provider_registry_funded_universe(
                registry_path=registry,
                portfolio_state_path=portfolio,
                output_path=resolved,
            )
            payload = yaml.safe_load(resolved.read_text(encoding="utf-8"))
            flags = {row["basket_id"]: row["funded"] for row in payload["trading_lines"]}

            self.assertEqual(authority["funded_position_count"], 2)
            self.assertEqual(flags["vwce_xetra_eur"], True)
            self.assertEqual(flags["l0ck_xetra_eur"], True)
            self.assertEqual(flags["watch_xetra_eur"], False)
            self.assertEqual(
                authority["stale_registry_funded_flags_overridden"],
                ["l0ck_xetra_eur", "watch_xetra_eur"],
            )

    def test_unmatched_funded_position_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = root / "registry.yml"
            portfolio = root / "portfolio.json"
            resolved = root / "resolved.yml"
            registry.write_text(yaml.safe_dump({
                "trading_lines": [
                    {"basket_id": "vwce_xetra_eur", "funded": True, "isin": "IE00BK5BQT80", "ticker": "VWCE", "exchange": "Xetra", "currency": "EUR"},
                ],
            }), encoding="utf-8")
            portfolio.write_text(json.dumps({
                "positions": [
                    {"investability_status": "funded_model_position", "isin": "IE00BG0J4C88", "exchange_ticker": "L0CK", "primary_exchange": "Xetra", "trading_currency": "EUR"},
                ],
            }), encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "PORTFOLIO_FUNDED_LINE_NOT_EXACTLY_ONE_REGISTRY_MATCH"):
                resolve_provider_registry_funded_universe(
                    registry_path=registry,
                    portfolio_state_path=portfolio,
                    output_path=resolved,
                )


if __name__ == "__main__":
    unittest.main()
