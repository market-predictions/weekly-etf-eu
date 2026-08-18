from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pricing.ucits_funded_universe import resolve_provider_registry_funded_universe
from pricing.ucits_price_qualification_policy import apply_primary_verification_policy_payload
from pricing.ucits_provider_identity_binding import build_provider_identity_binding


REPORT_DATE = "2026-08-17"
OBSERVED = {
    "vwce_xetra_eur": ("VWCE", "VWCE.DEX", 169.06, "VWCE.DE", 168.88000488),
    "euna_xetra_eur": ("EUNA", "EUNA.DEX", 4.8914, "EUNA.DE", 4.89459991),
    "sxr8_xetra_eur": ("SXR8", "SXR8.DEX", 723.0, "SXR8.DE", 724.17999268),
    "l0ck_xetra_eur": ("L0CK", "L0CK.DEX", 11.038, "L0CK.DE", 11.22799969),
    "iqqq_xetra_eur": ("IQQQ", "IQQQ.DEX", 65.86, "IQQQ.DE", 66.38999939),
    "dfen_xetra_eur": ("DFEN", "DFEN.DEX", 58.67, "DFEN.DE", 58.74000168),
}


class August17FreshnessSplitRegressionTests(unittest.TestCase):
    def test_alpha_exact_yahoo_stale_authorizes_all_six_as_unverified(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            resolved = Path(tmp) / "resolved.yml"
            resolve_provider_registry_funded_universe(
                registry_path=Path("config/ucits_price_provider_registry.yml"),
                portfolio_state_path=Path("output/etf_eu_portfolio_state.json"),
                output_path=resolved,
            )
            binding = build_provider_identity_binding(
                symbol_registry_path=Path("config/ucits_symbol_registry.yml"),
                provider_registry_path=resolved,
                provider_scope=["alpha_vantage", "yahoo_chart"],
            )

        binding_by_id = {row["basket_id"]: row for row in binding["rows"] if row["funded"]}
        lines = []
        for basket_id, (ticker, alpha_symbol, alpha_close, yahoo_symbol, yahoo_close) in OBSERVED.items():
            bound = binding_by_id[basket_id]
            lines.append(
                {
                    "basket_id": basket_id,
                    "funded": True,
                    "ticker": ticker,
                    "expected_isin": bound["isin"],
                    "expected_venue_code": bound["venue_code"],
                    "expected_currency": bound["currency"],
                    "provider_results": [
                        {
                            "provider": "alpha_vantage",
                            "provider_symbol": alpha_symbol,
                            "pricing_status": "priced",
                            "close_date": REPORT_DATE,
                            "close_price": alpha_close,
                            "returned_symbol": alpha_symbol,
                            "returned_exchange": None,
                            "returned_currency": None,
                            "venue_match": None,
                            "currency_match": None,
                            "blockers": [],
                            "identity_evidence": [],
                        },
                        {
                            "provider": "yahoo_chart",
                            "provider_symbol": yahoo_symbol,
                            "pricing_status": "priced",
                            "close_date": "2026-08-14",
                            "close_price": yahoo_close,
                            "returned_symbol": yahoo_symbol,
                            "returned_exchange": "GER",
                            "returned_currency": "EUR",
                            "venue_match": True,
                            "currency_match": True,
                            "blockers": [],
                            "identity_evidence": [],
                        },
                    ],
                }
            )

        payload = {
            "schema_version": "ucits_price_provider_qualification_v1",
            "report_date": REPORT_DATE,
            "provider_order": ["alpha_vantage", "yahoo_chart"],
            "agreement_tolerance_pct": 1.0,
            "funded_line_count": 6,
            "lines": lines,
        }
        result = apply_primary_verification_policy_payload(payload, binding)

        self.assertTrue(result["report_pricing_gate_passed"])
        self.assertEqual(result["funded_pricing_authorized_count"], 6)
        self.assertEqual(result["funded_unverified_count"], 6)
        self.assertEqual(result["funded_verified_count"], 0)
        self.assertEqual(result["funded_static_identity_bound_count"], 6)
        for line in result["lines"]:
            self.assertEqual(line["qualification_status"], "fresh_exact_unverified")
            self.assertEqual(line["selected_close_date"], REPORT_DATE)
            self.assertEqual(line["primary_provider"], "alpha_vantage")
            self.assertEqual(line["stale_or_other_date_providers"], ["yahoo_chart"])
            self.assertTrue(line["valuation_grade"])


if __name__ == "__main__":
    unittest.main()
