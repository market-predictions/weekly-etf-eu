from __future__ import annotations

import unittest

from pricing.ucits_price_qualification_policy import apply_primary_verification_policy_payload


class PrimaryVerificationIdentityPolicyTests(unittest.TestCase):
    def _binding(self, bound: bool = True) -> dict:
        return {
            "rows": [
                {
                    "basket_id": "vwce_xetra_eur",
                    "funded": True,
                    "registry_id": "global_core",
                    "static_identity_binding": bound,
                    "binding_status": "verified_static_exact_line" if bound else "identity_binding_failed",
                    "provider_symbol_bindings": {
                        "alpha_vantage": {
                            "matched": True,
                            "provider_registry_symbol": "VWCE.DEX",
                            "canonical_registry_symbol": "VWCE.DEX",
                            "blockers": [],
                        },
                        "yahoo_chart": {
                            "matched": True,
                            "provider_registry_symbol": "VWCE.DE",
                            "canonical_registry_symbol": "VWCE.DE",
                            "blockers": [],
                        },
                    },
                    "blockers": [] if bound else ["canonical_trading_line_match_count:0"],
                }
            ]
        }

    def _run(self, provider_results, *, bound: bool = True):
        payload = {
            "schema_version": "ucits_price_provider_qualification_v1",
            "report_date": "2026-08-17",
            "provider_order": ["alpha_vantage", "yahoo_chart"],
            "agreement_tolerance_pct": 1.0,
            "funded_line_count": 1,
            "lines": [
                {
                    "basket_id": "vwce_xetra_eur",
                    "funded": True,
                    "provider_results": provider_results,
                }
            ],
        }
        return apply_primary_verification_policy_payload(payload, self._binding(bound))

    def test_static_identity_allows_exact_primary_without_live_metadata_anchor(self):
        result = self._run(
            [
                {
                    "provider": "alpha_vantage",
                    "pricing_status": "priced",
                    "provider_symbol": "VWCE.DEX",
                    "returned_symbol": "VWCE.DEX",
                    "close_date": "2026-08-17",
                    "close_price": 169.06,
                    "venue_match": None,
                    "currency_match": None,
                    "blockers": [],
                },
                {
                    "provider": "yahoo_chart",
                    "pricing_status": "priced",
                    "provider_symbol": "VWCE.DE",
                    "returned_symbol": "VWCE.DE",
                    "close_date": "2026-08-14",
                    "close_price": 168.88,
                    "venue_match": True,
                    "currency_match": True,
                    "blockers": [],
                },
            ]
        )
        line = result["lines"][0]
        self.assertEqual(line["qualification_status"], "fresh_exact_unverified")
        self.assertEqual(line["identity_assurance_status"], "static_registry_verified_exact_line")
        self.assertTrue(line["static_primary_provider_symbol_binding"])
        self.assertEqual(line["identity_anchor_providers"], ["yahoo_chart"])
        self.assertTrue(result["report_pricing_gate_passed"])

    def test_live_metadata_anchor_is_supplemental_when_two_sources_verify(self):
        result = self._run(
            [
                {
                    "provider": "alpha_vantage",
                    "pricing_status": "priced",
                    "provider_symbol": "VWCE.DEX",
                    "returned_symbol": "VWCE.DEX",
                    "close_date": "2026-08-17",
                    "close_price": 169.06,
                    "venue_match": None,
                    "currency_match": None,
                    "blockers": [],
                },
                {
                    "provider": "yahoo_chart",
                    "pricing_status": "priced",
                    "provider_symbol": "VWCE.DE",
                    "returned_symbol": "VWCE.DE",
                    "close_date": "2026-08-17",
                    "close_price": 169.07,
                    "venue_match": True,
                    "currency_match": True,
                    "blockers": [],
                },
            ]
        )
        line = result["lines"][0]
        self.assertEqual(line["qualification_status"], "fresh_exact_verified")
        self.assertEqual(line["identity_anchor_providers"], ["yahoo_chart"])
        self.assertEqual(line["verification_providers"], ["yahoo_chart"])
        self.assertTrue(result["report_pricing_gate_passed"])

    def test_static_identity_failure_blocks_even_with_exact_price(self):
        result = self._run(
            [
                {
                    "provider": "alpha_vantage",
                    "pricing_status": "priced",
                    "provider_symbol": "VWCE.DEX",
                    "returned_symbol": "VWCE.DEX",
                    "close_date": "2026-08-17",
                    "close_price": 169.06,
                    "venue_match": None,
                    "currency_match": None,
                    "blockers": [],
                }
            ],
            bound=False,
        )
        self.assertEqual(result["lines"][0]["qualification_status"], "identity_binding_failed")
        self.assertFalse(result["report_pricing_gate_passed"])


if __name__ == "__main__":
    unittest.main()
