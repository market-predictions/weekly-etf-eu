from __future__ import annotations

import unittest

from runtime.build_etf_eu_transition_replay import current_composition, normalize_ticker, panel_frame


class TransitionReplayIdentityNormalizationTests(unittest.TestCase):
    def test_lock_alias_normalizes_to_l0ck(self):
        self.assertEqual(normalize_ticker("LOCK"), "L0CK")
        self.assertEqual(normalize_ticker("L0CK"), "L0CK")

    def test_panel_and_portfolio_share_canonical_l0ck_column(self):
        panel = {
            "rows": [
                {"date": "2026-07-23", "adjusted_close_eur": {"LOCK": 10.0, "VWCE": 160.0}},
                {"date": "2026-07-24", "adjusted_close_eur": {"LOCK": 10.2, "VWCE": 161.0}},
            ]
        }
        frame = panel_frame(panel)
        self.assertIn("L0CK", frame.columns)
        self.assertNotIn("LOCK", frame.columns)
        portfolio = {
            "nav_eur": 100000.0,
            "cash_eur": 50000.0,
            "positions": [
                {"ticker": "L0CK", "market_value_eur": 10000.0},
                {"ticker": "VWCE", "market_value_eur": 40000.0},
            ],
        }
        composition = current_composition(portfolio)
        self.assertEqual(set(composition["asset_values_eur"]), {"L0CK", "VWCE"})

    def test_alias_collision_fails_closed(self):
        panel = {
            "rows": [
                {"date": "2026-07-24", "adjusted_close_eur": {"LOCK": 10.0, "L0CK": 10.0}},
            ]
        }
        with self.assertRaisesRegex(RuntimeError, "ticker alias collision"):
            panel_frame(panel)


if __name__ == "__main__":
    unittest.main()
