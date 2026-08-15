from __future__ import annotations

import os
import unittest
from datetime import date
from unittest.mock import patch

from pricing import ucits_price_provider_engine as engine
from pricing.alpha_vantage_capacity_policy import (
    GovernedAlphaVantageAdapter,
    install_funded_only_alpha_policy,
)


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, payloads=None):
        self.payloads = list(payloads or [])
        self.headers = {}
        self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append((url, params, timeout))
        if not self.payloads:
            raise AssertionError("Unexpected network call")
        return FakeResponse(self.payloads.pop(0))


def make_line(*, funded: bool, ticker: str = "VWCE") -> engine.InstrumentLine:
    return engine.InstrumentLine(
        basket_id=f"{ticker.lower()}_xetra_eur",
        fund_name=ticker,
        isin="IE00BK5BQT80" if ticker == "VWCE" else "IE00BMC38736",
        instrument_type="UCITS ETF",
        exchange="Xetra",
        venue_code="XETR",
        ticker=ticker,
        currency="EUR",
        funded=funded,
        provider_symbols={"alpha_vantage": f"{ticker}.DEX", "yahoo_chart": f"{ticker}.DE"},
        provider_exchange_codes={"alpha_vantage": "DEX", "yahoo_chart": "GER"},
    )


class AlphaVantageCapacityPolicyTests(unittest.TestCase):
    def tearDown(self):
        install_funded_only_alpha_policy([])

    def test_bulk_identity_discovery_uses_zero_alpha_calls(self):
        session = FakeSession()
        with patch.dict(os.environ, {"ALPHA_VANTAGE_API_KEY": "secret"}, clear=False):
            adapter = GovernedAlphaVantageAdapter(session=session)
            results = adapter.bulk_discover(
                [make_line(funded=True), make_line(funded=False, ticker="VVSM")],
                date(2026, 8, 5),
            )
        self.assertEqual(session.calls, [])
        self.assertTrue(all(
            row.identity_status == "registry_declared_secondary_price_source_identity_not_queried"
            for row in results.values()
        ))

    def test_unfunded_non_candidate_uses_zero_alpha_close_calls(self):
        session = FakeSession()
        install_funded_only_alpha_policy([])
        with patch.dict(os.environ, {"ALPHA_VANTAGE_API_KEY": "secret"}, clear=False):
            result = GovernedAlphaVantageAdapter(session=session).fetch_close(
                make_line(funded=False, ticker="VVSM"), date(2026, 8, 5)
            )
        self.assertEqual(session.calls, [])
        self.assertEqual(result.pricing_status, "skipped_unfunded_capacity_preservation")
        self.assertIn(
            "alpha_vantage_live_close_reserved_for_funded_or_explicit_allocation_candidates",
            result.blockers,
        )

    def test_explicit_unfunded_allocation_candidate_makes_one_alpha_call(self):
        line = make_line(funded=False, ticker="VVSM")
        session = FakeSession([
            {"Time Series (Daily)": {"2026-08-05": {"4. close": "92.50"}}}
        ])
        install_funded_only_alpha_policy([line.basket_id])
        with patch.dict(os.environ, {"ALPHA_VANTAGE_API_KEY": "secret"}, clear=False):
            result = GovernedAlphaVantageAdapter(session=session).fetch_close(line, date(2026, 8, 5))
        self.assertEqual(len(session.calls), 1)
        self.assertEqual(session.calls[0][1]["function"], "TIME_SERIES_DAILY")
        self.assertEqual(result.pricing_status, "priced")
        self.assertEqual(result.close_price, 92.50)
        self.assertNotIn(
            "alpha_vantage_live_close_reserved_for_funded_positions",
            result.blockers,
        )

    def test_funded_line_makes_one_alpha_close_call(self):
        session = FakeSession([
            {"Time Series (Daily)": {"2026-08-05": {"4. close": "168.04"}}}
        ])
        install_funded_only_alpha_policy([])
        with patch.dict(os.environ, {"ALPHA_VANTAGE_API_KEY": "secret"}, clear=False):
            result = GovernedAlphaVantageAdapter(session=session).fetch_close(
                make_line(funded=True), date(2026, 8, 5)
            )
        self.assertEqual(len(session.calls), 1)
        self.assertEqual(session.calls[0][1]["function"], "TIME_SERIES_DAILY")
        self.assertEqual(result.pricing_status, "priced")
        self.assertEqual(result.close_price, 168.04)

    def test_install_replaces_shared_alpha_adapter(self):
        original = engine.ADAPTERS["alpha_vantage"]
        try:
            install_funded_only_alpha_policy([])
            self.assertIs(engine.ADAPTERS["alpha_vantage"], GovernedAlphaVantageAdapter)
        finally:
            engine.ADAPTERS["alpha_vantage"] = original


if __name__ == "__main__":
    unittest.main()
