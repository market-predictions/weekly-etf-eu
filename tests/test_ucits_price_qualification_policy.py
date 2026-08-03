from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pricing.ucits_price_qualification_policy import apply_identity_anchor_policy


class IdentityAnchorPolicyTests(unittest.TestCase):
    def _run(self, provider_results):
        payload = {
            "schema_version": "ucits_price_provider_qualification_v1",
            "funded_line_count": 1,
            "lines": [{
                "basket_id": "vwce_xetra_eur",
                "funded": True,
                "qualification_status": "qualified_development_consensus",
                "agreeing_providers": ["alpha_vantage", "yahoo_chart"],
                "provider_results": provider_results,
            }],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "qualification.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            return apply_identity_anchor_policy(path)

    def test_metadata_anchor_allows_consensus(self):
        result = self._run([
            {
                "provider": "alpha_vantage", "pricing_status": "priced",
                "provider_symbol": "VWCE.DEX", "returned_symbol": "VWCE.DEX",
                "venue_match": None, "currency_match": None,
            },
            {
                "provider": "yahoo_chart", "pricing_status": "priced",
                "provider_symbol": "VWCE.DE", "returned_symbol": "VWCE.DE",
                "venue_match": True, "currency_match": True,
            },
        ])
        line = result["lines"][0]
        self.assertEqual(line["qualification_status"], "qualified_development_consensus")
        self.assertEqual(line["identity_anchor_providers"], ["yahoo_chart"])
        self.assertTrue(result["report_pricing_gate_passed"])

    def test_unanchored_consensus_is_rejected(self):
        result = self._run([
            {
                "provider": "alpha_vantage", "pricing_status": "priced",
                "provider_symbol": "VWCE.DEX", "returned_symbol": "VWCE.DEX",
                "venue_match": None, "currency_match": None,
            },
            {
                "provider": "second", "pricing_status": "priced",
                "provider_symbol": "VWCE", "returned_symbol": None,
                "venue_match": None, "currency_match": None,
            },
        ])
        line = result["lines"][0]
        self.assertEqual(line["qualification_status"], "price_consensus_identity_unanchored")
        self.assertFalse(result["report_pricing_gate_passed"])


if __name__ == "__main__":
    unittest.main()
