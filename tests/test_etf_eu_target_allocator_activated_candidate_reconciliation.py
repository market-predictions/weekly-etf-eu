from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from runtime import build_etf_eu_target_allocator_shadow_v3 as base
from runtime import build_etf_eu_target_allocator_shadow_v3_policy_gate as gate


def candidate_row() -> dict:
    return {
        "exposure_id": "cyber_security",
        "preferred_ucits_candidate": {
            "fund_name": "iShares Digital Security UCITS ETF",
            "isin": "IE00BG0J4C88",
            "instrument_type": "UCITS ETF",
            "priips_kid_status": "available",
            "trading_lines": [
                {
                    "verification_status": "verified_ucits_trading_line_exact",
                    "exchange_ticker": "L0CK",
                    "exchange": "Xetra",
                    "trading_currency": "EUR",
                }
            ],
        },
    }


def stage_policy() -> dict:
    return {
        "candidate_exposures": ["ai_compute_infrastructure", "cyber_security"],
        "registry_expansion_must_not_reopen_stage_1_selection": True,
        "minimum_median_daily_traded_value_eur_20d": 500000.0,
        "maximum_price_age_calendar_days": 7,
    }


def portfolio() -> dict:
    return {
        "positions": [
            {
                "ticker": "L0CK",
                "isin": "IE00BG0J4C88",
                "shares": 930,
                "current_weight_pct": 10.26,
                "market_value_eur": 10166.76,
                "investability_status": "funded_model_position",
            }
        ]
    }


def evidence() -> dict:
    return {
        "status": "priced_current_exact_line_consensus",
        "completed_close": True,
        "close_price": 10.932,
        "price_age_calendar_days": 0,
        "median_daily_traded_value_eur_20d": 1200000.0,
        "candidate_role": "donor_target",
    }


class ActivatedCandidateReconciliationTests(unittest.TestCase):
    def test_already_funded_candidate_is_temporarily_removed_from_new_trade_budget(self):
        original = base.eligibility
        try:
            gate.install_candidate_gate({"stage_1": stage_policy()})
            gate.install_already_funded_gate(portfolio())
            eligible, blockers = base.eligibility(candidate_row(), evidence(), stage_policy())
        finally:
            base.eligibility = original
        self.assertFalse(eligible)
        self.assertEqual(blockers, [gate.ALREADY_FUNDED_BLOCKER])

    def test_unfunded_candidate_remains_normally_eligible(self):
        original = base.eligibility
        empty_portfolio = {"positions": []}
        try:
            gate.install_candidate_gate({"stage_1": stage_policy()})
            gate.install_already_funded_gate(empty_portfolio)
            eligible, blockers = base.eligibility(candidate_row(), evidence(), stage_policy())
        finally:
            base.eligibility = original
        self.assertTrue(eligible)
        self.assertEqual(blockers, [])

    def test_reconciliation_restores_strategy_eligibility_without_duplicate_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "allocator.json"
            output.write_text(
                json.dumps(
                    {
                        "variants": [
                            {
                                "variant_id": "staged_policy_driven_v1",
                                "allocation_rows": [
                                    {
                                        "exposure_id": "cyber_security",
                                        "candidate": {"isin": "IE00BG0J4C88", "ticker": "LOCK"},
                                        "eligible": False,
                                        "selected": False,
                                        "blockers": [gate.ALREADY_FUNDED_BLOCKER],
                                        "embedded_incumbent_exposure_lower_bound_pct_nav": 1.2,
                                        "effective_post_stage_exposure_lower_bound_pct_nav": 1.2,
                                        "effective_theme_cap_pct_nav": 15.0,
                                        "order": {
                                            "current_shares": 0,
                                            "target_shares": 0,
                                            "share_delta": 0,
                                            "side": "BLOCKED",
                                            "gross_trade_value_eur": 0.0,
                                            "estimated_cost_eur": 0.0,
                                            "target_market_value_eur": 0.0,
                                            "rounding_residual_eur": 10000.0,
                                        },
                                    }
                                ],
                                "policy_checks": {"effective_theme_caps_met": True},
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            gate.reconcile_already_funded_rows(output, portfolio())
            payload = json.loads(output.read_text(encoding="utf-8"))

        preferred = payload["variants"][0]
        row = preferred["allocation_rows"][0]
        self.assertTrue(row["eligible"])
        self.assertFalse(row["selected"])
        self.assertEqual(row["blockers"], [])
        self.assertTrue(row["already_funded_model_position"])
        self.assertAlmostEqual(row["existing_direct_position_weight_pct_nav"], 10.26)
        self.assertAlmostEqual(row["effective_post_stage_exposure_lower_bound_pct_nav"], 11.46)
        self.assertEqual(row["order"]["side"], "ALREADY_FUNDED_NO_NEW_TRADE")
        self.assertEqual(row["order"]["target_shares"], 0)
        self.assertEqual(row["order"]["share_delta"], 0)
        self.assertTrue(preferred["policy_checks"]["effective_theme_caps_met"])
        self.assertTrue(payload["activated_candidate_reconciliation"]["applied"])


if __name__ == "__main__":
    unittest.main()
