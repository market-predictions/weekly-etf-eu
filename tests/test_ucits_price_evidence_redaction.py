from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pricing.ucits_price_qualification_policy import apply_identity_anchor_policy


class ProviderEvidenceRedactionTests(unittest.TestCase):
    def test_provider_message_body_is_never_persisted(self):
        secret = "example-secret-value"
        payload = {
            "funded_line_count": 1,
            "lines": [{
                "basket_id": "vwce_xetra_eur",
                "funded": True,
                "qualification_status": "single_source_only",
                "agreeing_providers": ["yahoo_chart"],
                "provider_results": [{
                    "provider": "alpha_vantage",
                    "pricing_status": "fetch_failed",
                    "provider_symbol": "VWCE.DEX",
                    "returned_symbol": None,
                    "venue_match": None,
                    "currency_match": None,
                    "blockers": [f"provider_message:We detected your API key as {secret} and rate limit applies"],
                    "identity_evidence": [{"api_key": secret, "symbol": "VWCE.DEX"}],
                }],
            }],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "qualification.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            result = apply_identity_anchor_policy(path)
            text = path.read_text(encoding="utf-8")
        row = result["lines"][0]["provider_results"][0]
        self.assertNotIn(secret, text)
        self.assertEqual(row["blockers"], ["provider_rate_or_quota_limit"])
        self.assertEqual(row["identity_evidence"], [{"symbol": "VWCE.DEX"}])
        self.assertTrue(result["secret_redaction_applied"])


if __name__ == "__main__":
    unittest.main()
