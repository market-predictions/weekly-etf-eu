from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pricing import provider_secret_safety
from pricing.provider_secret_safety import enforce_provider_secret_safety
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

    def test_unrotated_alpha_secret_is_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "missing-rotation-marker.json"
            with patch.object(provider_secret_safety, "ALPHA_ROTATION_MARKER", marker):
                with patch.dict(os.environ, {"ALPHA_VANTAGE_API_KEY": "old-key"}, clear=False):
                    result = enforce_provider_secret_safety()
                    self.assertNotIn("ALPHA_VANTAGE_API_KEY", os.environ)
        self.assertTrue(result["alpha_vantage_secret_was_present"])
        self.assertFalse(result["alpha_vantage_rotation_confirmed"])
        self.assertFalse(result["alpha_vantage_live_enabled"])

    def test_rotated_alpha_secret_remains_available(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "rotation-marker.json"
            marker.write_text("{}", encoding="utf-8")
            with patch.object(provider_secret_safety, "ALPHA_ROTATION_MARKER", marker):
                with patch.dict(os.environ, {"ALPHA_VANTAGE_API_KEY": "rotated-key"}, clear=False):
                    result = enforce_provider_secret_safety()
                    self.assertEqual(os.environ.get("ALPHA_VANTAGE_API_KEY"), "rotated-key")
        self.assertTrue(result["alpha_vantage_rotation_confirmed"])
        self.assertTrue(result["alpha_vantage_live_enabled"])


if __name__ == "__main__":
    unittest.main()
