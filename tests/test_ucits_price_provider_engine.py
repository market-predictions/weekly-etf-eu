from __future__ import annotations

import os
import unittest
from datetime import date
from unittest.mock import patch

from pricing.ucits_price_provider_engine import (
    AlphaVantageAdapter,
    EodhdAdapter,
    InstrumentLine,
    LeewayAdapter,
    MarketstackAdapter,
    YahooChartAdapter,
    qualify_line,
)


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, payloads):
        self.payloads = list(payloads)
        self.headers = {}
        self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append((url, params, timeout))
        payload = self.payloads.pop(0)
        return payload if isinstance(payload, FakeResponse) else FakeResponse(payload)


def line() -> InstrumentLine:
    return InstrumentLine(
        basket_id="vwce_xetra_eur",
        fund_name="Vanguard FTSE All-World UCITS ETF USD Acc",
        isin="IE00BK5BQT80",
        instrument_type="UCITS ETF",
        exchange="Xetra",
        venue_code="XETR",
        ticker="VWCE",
        currency="EUR",
        funded=True,
        provider_symbols={
            "leeway": "VWCE.XETRA",
            "eodhd": "VWCE.XETRA",
            "marketstack": "VWCE",
            "alpha_vantage": "VWCE.DEX",
            "yahoo_chart": "VWCE.DE",
        },
        provider_exchange_codes={
            "leeway": "XETRA",
            "eodhd": "XETRA",
            "marketstack": "XETR",
            "alpha_vantage": "DEX",
            "yahoo_chart": "GER",
        },
    )


class ProviderParsingTests(unittest.TestCase):
    def test_leeway_close(self):
        session = FakeSession([[{"date": "2026-07-31", "close": 162.96, "currency": "EUR", "exchange": "XETRA"}]])
        with patch.dict(os.environ, {"LEEWAY_API_TOKEN": "secret"}, clear=False):
            result = LeewayAdapter(session=session).fetch_close(line(), date(2026, 7, 31))
        self.assertEqual(result.pricing_status, "priced")
        self.assertEqual(result.close_price, 162.96)
        self.assertTrue(result.venue_match)
        self.assertTrue(result.currency_match)

    def test_eodhd_close(self):
        session = FakeSession([[{"date": "2026-07-31", "close": 162.95}]])
        with patch.dict(os.environ, {"EODHD_API_TOKEN": "secret"}, clear=False):
            result = EodhdAdapter(session=session).fetch_close(line(), date(2026, 7, 31))
        self.assertEqual(result.pricing_status, "priced")
        self.assertEqual(result.close_date, "2026-07-31")

    def test_marketstack_close(self):
        payload = {"data": [{"date": "2026-07-31T00:00:00+0000", "close": 162.94, "exchange": "XETR", "currency": "EUR"}]}
        session = FakeSession([payload])
        with patch.dict(os.environ, {"MARKETSTACK_ACCESS_KEY": "secret"}, clear=False):
            result = MarketstackAdapter(session=session).fetch_close(line(), date(2026, 7, 31))
        self.assertEqual(result.pricing_status, "priced")
        self.assertEqual(result.close_price, 162.94)

    def test_alpha_vantage_close(self):
        payload = {"Time Series (Daily)": {"2026-07-31": {"4. close": "162.93"}}}
        session = FakeSession([payload])
        with patch.dict(os.environ, {"ALPHA_VANTAGE_API_KEY": "secret"}, clear=False):
            result = AlphaVantageAdapter(session=session).fetch_close(line(), date(2026, 7, 31))
        self.assertEqual(result.pricing_status, "priced")
        self.assertEqual(result.close_price, 162.93)

    def test_yahoo_chart_close_and_identity(self):
        payload = {
            "chart": {
                "result": [{
                    "meta": {"symbol": "VWCE.DE", "exchangeName": "GER", "currency": "EUR"},
                    "timestamp": [1785456000],
                    "indicators": {"quote": [{"close": [162.96]}]},
                }],
                "error": None,
            }
        }
        session = FakeSession([payload])
        result = YahooChartAdapter(session=session).fetch_close(line(), date(2026, 7, 31))
        self.assertEqual(result.pricing_status, "priced")
        self.assertTrue(result.venue_match)
        self.assertTrue(result.currency_match)

    def test_missing_key_is_not_configured(self):
        with patch.dict(os.environ, {}, clear=True):
            result = LeewayAdapter(session=FakeSession([])).fetch_close(line(), date(2026, 7, 31))
        self.assertEqual(result.pricing_status, "not_configured")
        self.assertIn("missing_secret:LEEWAY_API_TOKEN", result.blockers)

    def test_two_provider_consensus(self):
        rows = [
            {
                "provider": "leeway", "pricing_status": "priced", "close_date": "2026-07-31",
                "close_price": 162.96, "close_age_days": 0, "venue_match": True, "currency_match": True,
            },
            {
                "provider": "eodhd", "pricing_status": "priced", "close_date": "2026-07-31",
                "close_price": 162.95, "close_age_days": 0, "venue_match": None, "currency_match": None,
            },
        ]
        result = qualify_line(line(), rows, date(2026, 7, 31), max_close_age_days=7, agreement_tolerance_pct=1.0)
        self.assertEqual(result["qualification_status"], "qualified_development_consensus")
        self.assertEqual(result["same_date_provider_count"], 2)


if __name__ == "__main__":
    unittest.main()
