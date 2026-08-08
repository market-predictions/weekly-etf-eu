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
        funded: bool = True,
        identity_anchor: bool = True,
        qualification_status: str | None = None,
        qualification_isin_field: str = "expected_isin",
        ticker: str = "L0CK",
        isin: str = "IE00BG0J4C88",
        exposure_id: str = "cyber_security",
    ) -> tuple[Path, Path, Path, tempfile.TemporaryDirectory]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        transition = root / "transition.json"
        pricing = root / "pricing.json"
        qualification = root / "qualification.json"
        status = qualification_status or (
            "qualified_development_consensus" if len(set(providers)) >= 2 else "single_source_only"
        )
        transition_ticker = "LOCK" if ticker == "L0CK" else ticker

        transition.write_text(json.dumps({
            "report_date": "2026-08-05",
            "rows": [{
                "exposure_id": exposure_id,
                "isin": isin,
                "ticker": transition_ticker,
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
            }],
        }), encoding="utf-8")
        pricing.write_text(json.dumps({
            "report_date": "2026-08-05",
            "rows": [{
                "isin": isin,
                "ticker": ticker,
                "source_agreement_status": status,
                "agreeing_providers": providers,
                "close_date": "2026-08-05",
                "close_price": 10.93200008,
                "agreement_spread_pct": 0.00001 if len(set(providers)) >= 2 else None,
            }],
        }), encoding="utf-8")
        qualification_row = {
            qualification_isin_field: isin,
            "ticker": ticker,
            "funded": funded,
            "qualification_status": status,
            "identity_assurance_status": "metadata_anchored_exact_line" if identity_anchor else "unanchored_price_consensus",
            "identity_anchor_provider_count": 1 if identity_anchor else 0,
            "identity_anchor_providers": ["yahoo_chart"] if identity_anchor else [],
            "provider_results": [],
        }
        qualification.write_text(json.dumps({
            "report_date": "2026-08-05",
            "lines": [qualification_row],
        }), encoding="utf-8")
        return transition, pricing, qualification, tmp

    def test_native_funded_two_provider_consensus_updates_exact_line(self):
        transition, pricing, qualification, tmp = self._write_case(["alpha_vantage", "yahoo_chart"])
        try:
            apply(transition, pricing, qualification)
            payload = json.loads(transition.read_text(encoding="utf-8"))
        finally:
            tmp.cleanup()
        row = payload["rows"][0]
        self.assertEqual(row["status"], "priced_current_exact_line_consensus")
        self.assertTrue(row["wp11a_funded_line"])
        self.assertTrue(row["valuation_grade"])
        self.assertEqual(set(row["agreeing_providers"]), {"alpha_vantage", "yahoo_chart"})
        self.assertEqual(row["identity_assurance_status"], "metadata_anchored_exact_line")
        self.assertEqual(
            row["current_close_overlay"]["close_contract"],
            "funded_same_date_two_provider_consensus_with_exact_line_identity_anchor",
        )
        self.assertEqual(
            row["liquidity_evidence"]["twenty_day_metric_retained"]["median_daily_traded_value_eur_20d"],
            1200000.0,
        )
        self.assertTrue(payload["current_close_overlay"]["applied"])

    def test_unfunded_identity_anchored_single_source_updates_shadow_only(self):
        transition, pricing, qualification, tmp = self._write_case(
            ["yahoo_chart"], funded=False, ticker="VVSM", isin="IE00BMC38736", exposure_id="ai_compute_infrastructure"
        )
        try:
            apply(transition, pricing, qualification)
            payload = json.loads(transition.read_text(encoding="utf-8"))
        finally:
            tmp.cleanup()
        row = payload["rows"][0]
        self.assertEqual(row["status"], "priced_current_exact_line_identity_anchored_single_source")
        self.assertFalse(row["wp11a_funded_line"])
        self.assertFalse(row["valuation_grade"])
        self.assertFalse(row["funding_authority"])
        self.assertEqual(row["agreeing_providers"], ["yahoo_chart"])
        self.assertEqual(
            row["current_close_overlay"]["close_contract"],
            "unfunded_same_date_identity_anchored_single_source_shadow",
        )

    def test_funded_single_source_remains_rejected(self):
        transition, pricing, qualification, tmp = self._write_case(["yahoo_chart"], funded=True)
        try:
            apply(transition, pricing, qualification)
            payload = json.loads(transition.read_text(encoding="utf-8"))
        finally:
            tmp.cleanup()
        self.assertEqual(payload["rows"][0]["status"], "priced_non_authoritative")
        self.assertFalse(payload["current_close_overlay"]["applied"])

    def test_unanchored_unfunded_single_source_is_rejected(self):
        transition, pricing, qualification, tmp = self._write_case(
            ["yahoo_chart"], funded=False, identity_anchor=False, ticker="VVSM", isin="IE00BMC38736"
        )
        try:
            apply(transition, pricing, qualification)
            payload = json.loads(transition.read_text(encoding="utf-8"))
        finally:
            tmp.cleanup()
        self.assertEqual(payload["rows"][0]["status"], "priced_non_authoritative")
        self.assertFalse(payload["current_close_overlay"]["applied"])

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


if __name__ == "__main__":
    unittest.main()
