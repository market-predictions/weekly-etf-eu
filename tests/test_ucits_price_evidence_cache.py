from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pricing.ucits_price_evidence_cache import apply_provider_evidence_cache


class ProviderEvidenceCacheTests(unittest.TestCase):
    def _qualification(self):
        return {
            "report_date": "2026-07-31",
            "max_close_age_days": 7,
            "agreement_tolerance_pct": 1.0,
            "lines": [{
                "basket_id": "vwce_xetra_eur",
                "funded": True,
                "provider_results": [
                    {
                        "provider": "alpha_vantage", "provider_symbol": "VWCE.DEX",
                        "pricing_status": "fetch_failed", "blockers": ["provider_rate_or_quota_limit"],
                    },
                    {
                        "provider": "yahoo_chart", "provider_symbol": "VWCE.DE",
                        "pricing_status": "priced", "close_date": "2026-07-31", "close_price": 162.96000671,
                        "close_age_days": 0, "venue_match": True, "currency_match": True,
                    },
                ],
            }],
        }

    def _cache(self, report_date="2026-07-31"):
        return {
            "report_date": report_date,
            "provenance": {"artifact_id": 1, "artifact_sha256": "abc"},
            "authority": {"development_only": True, "valid_only_for_exact_report_date": True},
            "entries": [{
                "basket_id": "vwce_xetra_eur", "provider": "alpha_vantage",
                "provider_symbol": "VWCE.DEX", "report_date": report_date,
                "close_date": report_date, "close_price": 162.96,
                "returned_symbol": None, "returned_exchange": None,
                "returned_mic": None, "returned_currency": None,
                "venue_match": None, "currency_match": None,
            }],
        }

    def test_exact_date_cache_restores_consensus(self):
        with tempfile.TemporaryDirectory() as tmp:
            qualification = Path(tmp) / "qualification.json"
            cache = Path(tmp) / "cache.json"
            qualification.write_text(json.dumps(self._qualification()), encoding="utf-8")
            cache.write_text(json.dumps(self._cache()), encoding="utf-8")
            result = apply_provider_evidence_cache(qualification, cache)
        line = result["lines"][0]
        self.assertEqual(line["qualification_status"], "qualified_development_consensus")
        self.assertEqual(result["provider_cache_used_count"], 1)
        alpha = line["provider_results"][0]
        self.assertEqual(alpha["retrieval_mode"], "cached_accepted_historical_evidence")

    def test_wrong_date_cache_is_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            qualification = Path(tmp) / "qualification.json"
            cache = Path(tmp) / "cache.json"
            qualification.write_text(json.dumps(self._qualification()), encoding="utf-8")
            cache.write_text(json.dumps(self._cache("2026-07-30")), encoding="utf-8")
            result = apply_provider_evidence_cache(qualification, cache)
        self.assertEqual(result["provider_cache_status"], "ignored_report_date_mismatch")
        self.assertEqual(result["lines"][0]["provider_results"][0]["pricing_status"], "fetch_failed")


if __name__ == "__main__":
    unittest.main()
