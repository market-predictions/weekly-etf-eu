from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from pricing.ucits_price_qualification_policy import apply_primary_verification_policy_payload
from pricing.ucits_provider_identity_binding import build_provider_identity_binding


REPORT_DATE = "2026-08-17"


def provider_row(
    provider: str,
    close_date: str,
    close_price: float,
    *,
    symbol: str,
    returned_symbol: str | None = None,
    venue_match: bool | None = None,
    currency_match: bool | None = None,
) -> dict:
    return {
        "provider": provider,
        "provider_symbol": symbol,
        "pricing_status": "priced",
        "close_date": close_date,
        "close_price": close_price,
        "returned_symbol": returned_symbol if returned_symbol is not None else symbol,
        "venue_match": venue_match,
        "currency_match": currency_match,
        "blockers": [],
        "identity_evidence": [],
    }


def payload(rows: list[dict]) -> dict:
    return {
        "schema_version": "ucits_price_provider_qualification_v1",
        "report_date": REPORT_DATE,
        "provider_order": ["alpha_vantage", "yahoo_chart"],
        "agreement_tolerance_pct": 1.0,
        "lines": [
            {
                "basket_id": "vwce_xetra_eur",
                "funded": True,
                "ticker": "VWCE",
                "expected_isin": "IE00BK5BQT80",
                "expected_venue_code": "XETR",
                "expected_currency": "EUR",
                "provider_results": rows,
            }
        ],
    }


def binding(
    bound: bool = True,
    *,
    alpha_bound: bool = True,
    yahoo_bound: bool = True,
) -> dict:
    return {
        "schema_version": "ucits_provider_identity_binding_v1",
        "rows": [
            {
                "basket_id": "vwce_xetra_eur",
                "funded": True,
                "registry_id": "global_core",
                "static_identity_binding": bound,
                "binding_status": "verified_static_exact_line" if bound else "identity_binding_failed",
                "provider_symbol_bindings": {
                    "alpha_vantage": {
                        "matched": alpha_bound,
                        "provider_registry_symbol": "VWCE.DEX",
                        "canonical_registry_symbol": "VWCE.DEX",
                        "blockers": [] if alpha_bound else ["provider_symbol_mismatch"],
                    },
                    "yahoo_chart": {
                        "matched": yahoo_bound,
                        "provider_registry_symbol": "VWCE.DE",
                        "canonical_registry_symbol": "VWCE.DE",
                        "blockers": [] if yahoo_bound else ["provider_symbol_mismatch"],
                    },
                },
                "blockers": [] if bound else ["canonical_trading_line_match_count:0"],
            }
        ],
    }


class PrimaryVerificationPolicyTests(unittest.TestCase):
    def test_exact_primary_with_stale_verifier_is_authorized_unverified(self) -> None:
        result = apply_primary_verification_policy_payload(
            payload(
                [
                    provider_row("alpha_vantage", REPORT_DATE, 169.06, symbol="VWCE.DEX"),
                    provider_row(
                        "yahoo_chart",
                        "2026-08-14",
                        168.88,
                        symbol="VWCE.DE",
                        venue_match=True,
                        currency_match=True,
                    ),
                ]
            ),
            binding(),
        )
        line = result["lines"][0]
        self.assertEqual(line["qualification_status"], "fresh_exact_unverified")
        self.assertEqual(line["primary_provider"], "alpha_vantage")
        self.assertEqual(line["selected_close_price"], 169.06)
        self.assertTrue(line["static_primary_provider_symbol_binding"])
        self.assertEqual(line["stale_or_other_date_providers"], ["yahoo_chart"])
        self.assertTrue(line["valuation_grade"])
        self.assertTrue(result["report_pricing_gate_passed"])
        self.assertEqual(result["funded_unverified_count"], 1)
        self.assertEqual(result["funded_verified_count"], 0)

    def test_two_exact_sources_within_tolerance_are_verified(self) -> None:
        result = apply_primary_verification_policy_payload(
            payload(
                [
                    provider_row("alpha_vantage", REPORT_DATE, 169.06, symbol="VWCE.DEX"),
                    provider_row(
                        "yahoo_chart",
                        REPORT_DATE,
                        169.07,
                        symbol="VWCE.DE",
                        venue_match=True,
                        currency_match=True,
                    ),
                ]
            ),
            binding(),
        )
        line = result["lines"][0]
        self.assertEqual(line["qualification_status"], "fresh_exact_verified")
        self.assertEqual(line["primary_provider"], "alpha_vantage")
        self.assertEqual(line["verification_providers"], ["yahoo_chart"])
        self.assertEqual(line["selected_close_price"], 169.06)
        self.assertTrue(result["report_pricing_gate_passed"])
        self.assertEqual(result["funded_verified_count"], 1)

    def test_two_exact_sources_outside_tolerance_fail_closed(self) -> None:
        result = apply_primary_verification_policy_payload(
            payload(
                [
                    provider_row("alpha_vantage", REPORT_DATE, 169.06, symbol="VWCE.DEX"),
                    provider_row(
                        "yahoo_chart",
                        REPORT_DATE,
                        160.00,
                        symbol="VWCE.DE",
                        venue_match=True,
                        currency_match=True,
                    ),
                ]
            ),
            binding(),
        )
        line = result["lines"][0]
        self.assertEqual(line["qualification_status"], "provider_disagreement")
        self.assertIsNone(line["selected_close_price"])
        self.assertFalse(line["valuation_grade"])
        self.assertFalse(result["report_pricing_gate_passed"])

    def test_stale_only_prices_fail_closed(self) -> None:
        result = apply_primary_verification_policy_payload(
            payload(
                [
                    provider_row("alpha_vantage", "2026-08-14", 168.88, symbol="VWCE.DEX"),
                    provider_row(
                        "yahoo_chart",
                        "2026-08-14",
                        168.88,
                        symbol="VWCE.DE",
                        venue_match=True,
                        currency_match=True,
                    ),
                ]
            ),
            binding(),
        )
        self.assertEqual(result["lines"][0]["qualification_status"], "no_exact_close")
        self.assertFalse(result["report_pricing_gate_passed"])

    def test_explicit_live_identity_mismatch_rejects_provider(self) -> None:
        result = apply_primary_verification_policy_payload(
            payload(
                [
                    provider_row(
                        "alpha_vantage",
                        REPORT_DATE,
                        169.06,
                        symbol="VWCE.DEX",
                        returned_symbol="WRONG.DEX",
                    ),
                    provider_row(
                        "yahoo_chart",
                        "2026-08-14",
                        168.88,
                        symbol="VWCE.DE",
                        venue_match=True,
                        currency_match=True,
                    ),
                ]
            ),
            binding(),
        )
        line = result["lines"][0]
        self.assertEqual(line["qualification_status"], "no_exact_close")
        self.assertEqual(line["rejected_provider_prices"], ["alpha_vantage"])
        self.assertFalse(result["report_pricing_gate_passed"])

    def test_static_line_identity_binding_is_mandatory(self) -> None:
        result = apply_primary_verification_policy_payload(
            payload([provider_row("alpha_vantage", REPORT_DATE, 169.06, symbol="VWCE.DEX")]),
            binding(False),
        )
        self.assertEqual(result["lines"][0]["qualification_status"], "identity_binding_failed")
        self.assertFalse(result["report_pricing_gate_passed"])

    def test_broken_verifier_symbol_binding_does_not_block_bound_primary(self) -> None:
        result = apply_primary_verification_policy_payload(
            payload(
                [
                    provider_row("alpha_vantage", REPORT_DATE, 169.06, symbol="VWCE.DEX"),
                    provider_row(
                        "yahoo_chart",
                        REPORT_DATE,
                        169.07,
                        symbol="VWCE.DE",
                        venue_match=True,
                        currency_match=True,
                    ),
                ]
            ),
            binding(yahoo_bound=False),
        )
        line = result["lines"][0]
        self.assertEqual(line["qualification_status"], "fresh_exact_unverified")
        self.assertEqual(line["primary_provider"], "alpha_vantage")
        self.assertEqual(line["provider_symbol_binding_failures"], ["yahoo_chart"])
        self.assertTrue(result["report_pricing_gate_passed"])

    def test_unbound_primary_symbol_is_rejected(self) -> None:
        result = apply_primary_verification_policy_payload(
            payload(
                [
                    provider_row("alpha_vantage", REPORT_DATE, 169.06, symbol="VWCE.DEX"),
                    provider_row(
                        "yahoo_chart",
                        "2026-08-14",
                        168.88,
                        symbol="VWCE.DE",
                        venue_match=True,
                        currency_match=True,
                    ),
                ]
            ),
            binding(alpha_bound=False),
        )
        line = result["lines"][0]
        self.assertEqual(line["qualification_status"], "no_exact_close")
        self.assertEqual(line["provider_symbol_binding_failures"], ["alpha_vantage"])
        self.assertFalse(result["report_pricing_gate_passed"])


class StaticIdentityBindingTests(unittest.TestCase):
    def _write(self, root: Path, provider_symbol: str) -> tuple[Path, Path]:
        symbol_registry = {
            "schema_version": "ucits_symbol_registry_v3",
            "canonical_identity": "isin_plus_exact_trading_line",
            "funds": [
                {
                    "registry_id": "global_core",
                    "isin": "IE00BK5BQT80",
                    "trading_lines": [
                        {
                            "exchange": "Xetra",
                            "venue_code": "XETR",
                            "exchange_ticker": "VWCE",
                            "trading_currency": "EUR",
                            "provider_symbol_alpha_vantage": "VWCE.DEX",
                            "pricing_symbol_yahoo": "VWCE.DE",
                            "line_verification_status": "verified_ucits_trading_line",
                        }
                    ],
                }
            ],
        }
        provider_registry = {
            "trading_lines": [
                {
                    "basket_id": "vwce_xetra_eur",
                    "funded": True,
                    "isin": "IE00BK5BQT80",
                    "exchange": "Xetra",
                    "venue_code": "XETR",
                    "ticker": "VWCE",
                    "currency": "EUR",
                    "provider_symbols": {
                        "alpha_vantage": provider_symbol,
                        "yahoo_chart": "VWCE.DE",
                    },
                }
            ]
        }
        symbol_path = root / "symbols.yml"
        provider_path = root / "providers.yml"
        symbol_path.write_text(yaml.safe_dump(symbol_registry, sort_keys=False), encoding="utf-8")
        provider_path.write_text(yaml.safe_dump(provider_registry, sort_keys=False), encoding="utf-8")
        return symbol_path, provider_path

    def test_provider_symbols_are_bound_to_verified_static_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            symbol_path, provider_path = self._write(Path(tmp), "VWCE.DEX")
            result = build_provider_identity_binding(
                symbol_registry_path=symbol_path,
                provider_registry_path=provider_path,
                provider_scope=["alpha_vantage", "yahoo_chart"],
            )
        self.assertTrue(result["all_funded_identity_bound"])
        self.assertTrue(result["all_funded_provider_scope_bound"])
        self.assertTrue(result["rows"][0]["static_identity_binding"])

    def test_provider_symbol_drift_does_not_invalidate_static_line_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            symbol_path, provider_path = self._write(Path(tmp), "WRONG.DEX")
            result = build_provider_identity_binding(
                symbol_registry_path=symbol_path,
                provider_registry_path=provider_path,
                provider_scope=["alpha_vantage", "yahoo_chart"],
            )
        self.assertTrue(result["all_funded_identity_bound"])
        self.assertFalse(result["all_funded_provider_scope_bound"])
        row = result["rows"][0]
        self.assertTrue(row["static_identity_binding"])
        self.assertFalse(row["provider_symbol_bindings"]["alpha_vantage"]["matched"])
        self.assertIn("provider_symbol_mismatch", row["provider_symbol_bindings"]["alpha_vantage"]["blockers"])


if __name__ == "__main__":
    unittest.main()
