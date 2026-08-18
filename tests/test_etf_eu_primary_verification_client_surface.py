from __future__ import annotations

import unittest

from tools.build_etf_eu_routine_report_package import _lane_summary, _status_label


class PrimaryVerificationClientSurfaceTests(unittest.TestCase):
    def test_verified_exact_close_has_explicit_client_label(self) -> None:
        row = {
            "pricing_status": "priced_non_authoritative",
            "source_agreement_status": "fresh_exact_verified",
            "verification_status": "verified_same_date_within_tolerance",
        }
        self.assertEqual(_status_label(row, language="nl"), "Exacte slotkoers, onafhankelijk geverifieerd")
        self.assertEqual(_status_label(row, language="en"), "Exact close, independently verified")

    def test_unverified_exact_close_describes_price_verification_not_identity(self) -> None:
        row = {
            "pricing_status": "priced_non_authoritative",
            "source_agreement_status": "fresh_exact_unverified",
            "verification_status": "unverified_no_same_date_verifier",
        }
        nl = _status_label(row, language="nl")
        en = _status_label(row, language="en")
        self.assertEqual(nl, "Exacte slotkoers, niet onafhankelijk geverifieerd")
        self.assertEqual(en, "Exact close, not independently verified")
        self.assertNotIn("handelslijn", nl.casefold())
        self.assertNotIn("trading line", en.casefold())

    def test_summary_separates_verified_and_unverified_exact_closes(self) -> None:
        rows = [
            {
                "pricing_status": "priced_non_authoritative",
                "close_price": 100.0,
                "source_agreement_status": "fresh_exact_verified",
            },
            {
                "pricing_status": "priced_non_authoritative",
                "close_price": 101.0,
                "source_agreement_status": "fresh_exact_unverified",
            },
            {
                "pricing_status": "blocked",
                "close_price": None,
                "source_agreement_status": "no_exact_close",
            },
        ]
        nl = _lane_summary(rows, dutch=True)
        en = _lane_summary(rows, dutch=False)
        self.assertIn("onafhankelijke actuele verificatie:** 1", nl)
        self.assertIn("zonder tweede actuele verifier:** 1", nl)
        self.assertIn("Geblokkeerd of niet opgelost:** 1", nl)
        self.assertIn("independent current verification:** 1", en)
        self.assertIn("without a second current verifier:** 1", en)
        self.assertIn("Blocked or unresolved:** 1", en)

    def test_blocked_disagreement_has_client_safe_label(self) -> None:
        row = {
            "pricing_status": "blocked",
            "source_agreement_status": "provider_disagreement",
            "verification_status": "blocked_same_date_provider_disagreement",
        }
        self.assertEqual(_status_label(row, language="nl"), "Prijsconflict tussen bronnen")
        self.assertEqual(_status_label(row, language="en"), "Price disagreement between sources")


if __name__ == "__main__":
    unittest.main()
