from __future__ import annotations

import unittest

from pricing.ucits_close_price_validation_contract_v2 import validate_payload


class PrimaryVerificationLegacyContractTests(unittest.TestCase):
    def _artifact(self, *, close_date: str = "2026-08-17", status: str = "fresh_exact_unverified") -> dict:
        authorized = status in {"fresh_exact_verified", "fresh_exact_unverified"}
        verification_providers = ["yahoo_chart"] if status == "fresh_exact_verified" else []
        same_date_count = 2 if status == "fresh_exact_verified" else 1
        return {
            "schema_version": "ucits_close_price_validation_basket_results_v2",
            "report_date": "2026-08-17",
            "source_basket": "config/ucits_close_price_validation_basket.yml",
            "funding_authority": False,
            "portfolio_mutation": False,
            "production_delivery_authority": False,
            "line_count": 1,
            "priced_line_count": 1 if authorized else 0,
            "report_pricing_gate_passed": authorized,
            "valuation_grade": authorized,
            "pricing_authority_policy": {
                "mode": "donor_aligned_primary_plus_verification_v1",
                "second_provider_required_for_liveness": False,
                "same_date_disagreement_blocks": True,
            },
            "rows": [
                {
                    "basket_id": "vwce_xetra_eur",
                    "ticker": "VWCE",
                    "isin": "IE00BK5BQT80",
                    "pricing_status": "priced_non_authoritative" if authorized else "blocked",
                    "source_agreement_status": status,
                    "valuation_grade": authorized,
                    "static_identity_binding": True,
                    "identity_assurance_status": "static_registry_verified_exact_line",
                    "completed_close_on_requested_report_date": authorized,
                    "requested_report_date": "2026-08-17",
                    "close_date": close_date if authorized else None,
                    "close_price": 169.06 if authorized else None,
                    "primary_provider": "alpha_vantage" if authorized else None,
                    "same_date_provider_count": same_date_count if authorized else 0,
                    "verification_providers": verification_providers,
                }
            ],
        }

    def _portfolio(self) -> dict:
        return {"positions": [{"ticker": "VWCE", "isin": "IE00BK5BQT80"}]}

    def test_exact_primary_without_verifier_is_valid_valuation_input(self) -> None:
        result = validate_payload(
            self._artifact(),
            expected_report_date="2026-08-17",
            portfolio_state=self._portfolio(),
            require_funded_consensus=True,
        )
        self.assertTrue(result["valid"], result["blockers"])

    def test_verified_exact_primary_is_valid(self) -> None:
        result = validate_payload(
            self._artifact(status="fresh_exact_verified"),
            expected_report_date="2026-08-17",
            portfolio_state=self._portfolio(),
            require_funded_consensus=True,
        )
        self.assertTrue(result["valid"], result["blockers"])

    def test_non_exact_date_is_rejected_even_when_marked_unverified(self) -> None:
        result = validate_payload(
            self._artifact(close_date="2026-08-14"),
            expected_report_date="2026-08-17",
            portfolio_state=self._portfolio(),
            require_funded_consensus=True,
        )
        self.assertFalse(result["valid"])
        self.assertTrue(any("close_date_not_exact_requested_date" in item for item in result["blockers"]))


if __name__ == "__main__":
    unittest.main()
