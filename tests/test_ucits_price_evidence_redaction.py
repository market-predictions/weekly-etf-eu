from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pricing import provider_secret_safety
from pricing.provider_secret_safety import enforce_provider_secret_safety
from pricing.ucits_price_qualification_policy import apply_primary_verification_policy_payload


class ProviderEvidenceRedactionTests(unittest.TestCase):
    def test_provider_message_body_is_never_persisted(self):
        secret = "example-secret-value"
        payload = {
            "schema_version": "ucits_price_provider_qualification_v1",
            "report_date": "2026-08-17",
            "provider_order": ["alpha_vantage", "yahoo_chart"],
            "agreement_tolerance_pct": 1.0,
            "funded_line_count": 1,
            "lines": [{
                "basket_id": "vwce_xetra_eur",
                "funded": True,
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
        identity_binding = {
            "rows": [{
                "basket_id": "vwce_xetra_eur",
                "funded": True,
                "registry_id": "global_core",
                "static_identity_binding": True,
                "binding_status": "verified_static_exact_line",
                "blockers": [],
            }]
        }
        result = apply_primary_verification_policy_payload(payload, identity_binding)
        text = json.dumps(result, sort_keys=True)
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
            marker.write_text(json.dumps({
                "schema_version": "alpha_vantage_key_rotation_confirmation_v1",
                "rotation_confirmed": True,
                "secret_value_recorded": False,
                "repository_secret_name": "ALPHA_VANTAGE_API_KEY",
                "confirmed_at_utc": "2026-08-08T13:00:00Z",
                "reason": "test fixture only",
            }), encoding="utf-8")
            with patch.object(provider_secret_safety, "ALPHA_ROTATION_MARKER", marker):
                with patch.dict(os.environ, {"ALPHA_VANTAGE_API_KEY": "rotated-key"}, clear=False):
                    result = enforce_provider_secret_safety()
                    self.assertEqual(os.environ.get("ALPHA_VANTAGE_API_KEY"), "rotated-key")
        self.assertTrue(result["alpha_vantage_rotation_confirmed"])
        self.assertTrue(result["alpha_vantage_live_enabled"])
        self.assertEqual(result["rotation_marker_status"], "valid_rotation_confirmation")


if __name__ == "__main__":
    unittest.main()
