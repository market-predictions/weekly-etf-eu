from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pricing.apply_current_close_results_to_transition_evidence import apply


class CurrentCloseTransitionOverlayTests(unittest.TestCase):
    def _write_case(
        self,
        providers: list[str],
        *,
        identity_anchor: bool = True,
        qualification_isin_field: str = "expected_isin",
    ) -> tuple[Path, Path, Path, tempfile.TemporaryDirectory]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        transition = root / "transition.json"
        pricing = root / "pricing.json"
        qualification = root / "qualification.json"

        transition.write_text(
            json.dumps(
                {
                    "report_date": "2026-08-05",
                    "rows": [
                        {
                            "exposure_id": "cyber_security",
                            "isin": "IE00BG0J4C88",
                            "ticker": "LOCK",
                            "status": "priced_non_authoritative",
                            "completed_close": True,
                            "close_date": "2026-08-04",
                            "close_price": 10.90,
                            "median_daily_volume_20d": 100000,
                            "median_daily_traded_value_eur_20d": 1200000.0,
                            "annualized_close_volatility_pct_20d": 22.0,
                            "liquidity_window_rows": 20,
                            "source": "prior connectivity evidence",
                            "source_quality": "non_authoritative_connectivity_only",
                            "blockers": [],
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        pricing.write_text(
            json.dumps(
                {
                    "report_date": "2026-08-05",
                    "rows": [
                        {
                            "isin": "IE00BG0J4C88",
                            "ticker": "L0CK",
                            "source_agreement_status": "qualified_development_consensus",
                            "agreeing_providers": providers,
                            "close_date": "2026-08-05",
                            "close_price": 10.93200008,
                            "agreement_spread_pct": 0.00001,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        qualification_row = {
            qualification_isin_field: "IE00BG0J4C88",
            "ticker": "L0CK",
            "qualification_status": "qualified_development_consensus",
            "identity_anchor_passed": identity_anchor,
            "identity_anchor_providers": ["yahoo_chart"] if identity_anchor else [],
            "provider_results": [],
        }
        qualification.write_text(
            json.dumps(
                {
                    "report_date": "2026-08-05",
                    "lines": [qualification_row],
                }
            ),
            encoding="utf-8",
        )
        return transition, pricing, qualification, tmp

    def test_native_wp11a_expected_isin_updates_exact_line(self):
        transition, pricing, qualification, tmp = self._write_case(["alpha_vantage", "yahoo_chart"])
        try:
            apply(transition, pricing, qualification)
            payload = json.loads(transition.read_text(encoding="utf-8"))
        finally:
            tmp.cleanup()
        row = payload["rows"][0]
        self.assertEqual(row["status"], "priced_current_exact_line_consensus")
        self.assertEqual(row["close_date"], "2026-08-05")
        self.assertAlmostEqual(row["close_price"], 10.93200008)
        self.assertEqual(set(row["agreeing_providers"]), {"alpha_vantage", "yahoo_chart"})
        self.assertTrue(row["identity_anchor_passed"])
        self.assertEqual(
            row["current_close_overlay"]["close_contract"],
            "same_date_two_provider_consensus_with_exact_line_identity_anchor",
        )
        self.assertEqual(
            row["liquidity_evidence"]["twenty_day_metric_retained"]["median_daily_traded_value_eur_20d"],
            1200000.0,
        )
        self.assertTrue(payload["current_close_overlay"]["applied"])
        self.assertEqual(payload["current_close_overlay"]["updated_row_count"], 1)

    def test_legacy_isin_alias_remains_replay_compatible(self):
        transition, pricing, qualification, tmp = self._write_case(
            ["alpha_vantage", "yahoo_chart"], qualification_isin_field="isin"
        )
        try:
            apply(transition, pricing, qualification)
            payload = json.loads(transition.read_text(encoding="utf-8"))
        finally:
            tmp.cleanup()
        self.assertTrue(payload["current_close_overlay"]["applied"])

    def test_single_source_consensus_is_rejected(self):
        transition, pricing, qualification, tmp = self._write_case(["yahoo_chart"])
        try:
            apply(transition, pricing, qualification)
            payload = json.loads(transition.read_text(encoding="utf-8"))
        finally:
            tmp.cleanup()
        row = payload["rows"][0]
        self.assertEqual(row["status"], "priced_non_authoritative")
        self.assertFalse(payload["current_close_overlay"]["applied"])

    def test_unanchored_consensus_is_rejected(self):
        transition, pricing, qualification, tmp = self._write_case(
            ["alpha_vantage", "yahoo_chart"], identity_anchor=False
        )
        try:
            apply(transition, pricing, qualification)
            payload = json.loads(transition.read_text(encoding="utf-8"))
        finally:
            tmp.cleanup()
        row = payload["rows"][0]
        self.assertEqual(row["status"], "priced_non_authoritative")
        self.assertFalse(payload["current_close_overlay"]["applied"])


if __name__ == "__main__":
    unittest.main()
