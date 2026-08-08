from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pricing.provider_secret_safety as safety


class ProviderSecretSafetyTests(unittest.TestCase):
    def _run(self, marker_payload=None, marker_text=None):
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "alpha_vantage_key_rotation_confirmed.json"
            if marker_payload is not None:
                marker.write_text(json.dumps(marker_payload), encoding="utf-8")
            elif marker_text is not None:
                marker.write_text(marker_text, encoding="utf-8")
            with patch.object(safety, "ALPHA_ROTATION_MARKER", marker):
                with patch.dict(os.environ, {"ALPHA_VANTAGE_API_KEY": "rotated-secret"}, clear=True):
                    result = safety.enforce_provider_secret_safety()
                    remaining = os.environ.get("ALPHA_VANTAGE_API_KEY")
            return result, remaining

    def test_absent_marker_disables_present_secret(self):
        result, remaining = self._run()
        self.assertFalse(result["alpha_vantage_rotation_confirmed"])
        self.assertFalse(result["alpha_vantage_live_enabled"])
        self.assertEqual(result["rotation_marker_status"], "marker_absent")
        self.assertIsNone(remaining)

    def test_empty_or_invalid_marker_fails_closed(self):
        result, remaining = self._run(marker_text="{}")
        self.assertFalse(result["alpha_vantage_rotation_confirmed"])
        self.assertEqual(result["rotation_marker_status"], "marker_schema_mismatch")
        self.assertIsNone(remaining)

    def test_valid_non_secret_rotation_marker_enables_secret(self):
        result, remaining = self._run(marker_payload={
            "schema_version": "alpha_vantage_key_rotation_confirmation_v1",
            "rotation_confirmed": True,
            "secret_value_recorded": False,
            "repository_secret_name": "ALPHA_VANTAGE_API_KEY",
            "confirmed_at_utc": "2026-08-08T13:00:00Z",
            "reason": "rotated after prior response exposure",
        })
        self.assertTrue(result["alpha_vantage_rotation_confirmed"])
        self.assertTrue(result["alpha_vantage_live_enabled"])
        self.assertEqual(result["rotation_marker_status"], "valid_rotation_confirmation")
        self.assertEqual(remaining, "rotated-secret")

    def test_marker_claiming_secret_value_recorded_fails_closed(self):
        result, remaining = self._run(marker_payload={
            "schema_version": "alpha_vantage_key_rotation_confirmation_v1",
            "rotation_confirmed": True,
            "secret_value_recorded": True,
            "repository_secret_name": "ALPHA_VANTAGE_API_KEY",
            "confirmed_at_utc": "2026-08-08T13:00:00Z",
        })
        self.assertFalse(result["alpha_vantage_live_enabled"])
        self.assertEqual(result["rotation_marker_status"], "marker_secret_recording_contract_failed")
        self.assertIsNone(remaining)


if __name__ == "__main__":
    unittest.main()
