from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

import tools.run_etf_eu_aug3_expanded_report_v6 as runner


class FreshPackagePricingRouteTests(unittest.TestCase):
    def test_legacy_pricing_entrypoint_routes_to_wp11a_compatibility_wrapper(self):
        with patch.object(runner, "run_with_compact_model_proposal", return_value="ok") as downstream:
            result = runner.run_with_activated_allocation_surface(
                "pricing/build_current_session_close_results.py",
                "--run-id",
                "TEST",
                cwd=Path("."),
                capture=False,
            )
        self.assertEqual(result, "ok")
        routed = downstream.call_args.args
        self.assertEqual(routed[0], "pricing/build_wp11a_current_session_compat.py")

    def test_unrelated_entrypoint_preserves_existing_route_contract(self):
        with patch.object(runner, "run_with_compact_model_proposal", return_value="ok") as downstream:
            runner.run_with_activated_allocation_surface(
                "runtime/build_shared_strategy_state.py",
                cwd=Path("."),
                capture=False,
            )
        self.assertEqual(downstream.call_args.args[0], "runtime/build_shared_strategy_state.py")


if __name__ == "__main__":
    unittest.main()
