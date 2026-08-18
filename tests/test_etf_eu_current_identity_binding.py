from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pricing.ucits_funded_universe import resolve_provider_registry_funded_universe
from pricing.ucits_provider_identity_binding import build_provider_identity_binding


class CurrentFundedIdentityBindingTests(unittest.TestCase):
    def test_current_six_funded_lines_bind_to_alpha_and_yahoo_symbols(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            resolved = Path(tmp) / "resolved.yml"
            authority = resolve_provider_registry_funded_universe(
                registry_path=Path("config/ucits_price_provider_registry.yml"),
                portfolio_state_path=Path("output/etf_eu_portfolio_state.json"),
                output_path=resolved,
            )
            binding = build_provider_identity_binding(
                symbol_registry_path=Path("config/ucits_symbol_registry.yml"),
                provider_registry_path=resolved,
                provider_scope=["alpha_vantage", "yahoo_chart"],
            )
        self.assertEqual(authority["funded_position_count"], 6)
        self.assertEqual(binding["funded_line_count"], 6)
        self.assertEqual(binding["funded_bound_line_count"], 6)
        self.assertTrue(binding["all_funded_identity_bound"])
        funded = [row for row in binding["rows"] if row["funded"]]
        self.assertEqual(
            sorted(row["ticker"] for row in funded),
            ["DFEN", "EUNA", "IQQQ", "L0CK", "SXR8", "VWCE"],
        )
        for row in funded:
            self.assertTrue(row["provider_symbol_bindings"]["alpha_vantage"]["matched"])
            self.assertTrue(row["provider_symbol_bindings"]["yahoo_chart"]["matched"])


if __name__ == "__main__":
    unittest.main()
