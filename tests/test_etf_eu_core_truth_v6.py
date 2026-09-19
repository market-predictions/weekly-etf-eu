from __future__ import annotations

import unittest

from runtime.build_etf_eu_donor_discovery_bridge import _fundability
from runtime.reconcile_etf_eu_funded_markdown import render_funded_markdown, validate_funded_markdown
from runtime.render_etf_eu_client_grade_v2_funded import build_html
from runtime.revalue_etf_eu_model_portfolio import revalue_portfolio


REPORT_DATE = "2026-08-17"


def _candidate() -> dict:
    return {
        "isin": "IE00BK5BQT80",
        "exchange_ticker": "VWCE",
        "exchange": "Xetra",
        "identity_status": "verified",
    }


def _pricing(status: str) -> dict:
    return {
        "ticker": "VWCE",
        "isin": "IE00BK5BQT80",
        "completed_close_on_requested_report_date": True,
        "close_date": REPORT_DATE,
        "close_price": 169.06,
        "currency": "EUR",
        "source_agreement_status": status,
        "valuation_grade": status in {"fresh_exact_verified", "fresh_exact_unverified"},
        "static_identity_binding": True,
        "static_primary_provider_symbol_binding": True,
        "primary_provider": "alpha_vantage",
        "verification_providers": ["yahoo_chart"] if status == "fresh_exact_verified" else [],
    }


def _primary_only_state() -> dict:
    position = {
        "ticker": "VWCE",
        "isin": "IE00BK5BQT80",
        "shares": 2,
        "current_price_local": 169.06,
        "market_value_eur": 338.12,
        "current_weight_pct": 25.268286,
        "price_date": REPORT_DATE,
        "pricing_status": "fresh_exact_unverified",
        "verification_status": "fresh_exact_unverified",
        "primary_provider": "alpha_vantage",
        "verification_providers": [],
        "portfolio_role": "Diversified global equity core",
        "current_allocation_decision": "hold",
        "implementation_assessment": (
            "Verified Xetra UCITS implementation remains fit for the diversified core role. "
            "Exact completed-close primary pricing is authorized by the canonical pricing state; "
            "no current independent verifier is present, so confidence is lower but valuation authority remains valid."
        ),
        "required_next_action": "Hold current shares; no add without a separate current allocation decision.",
        "thesis_assessment": "Broad global equity remains the diversified core anchor.",
        "replaceable_status": "No",
        "best_alternative": "IWDA remains a comparator.",
        "replacement_duel_status": "Current holding retained",
        "next_review_trigger": "Re-underwrite on material thesis or implementation change.",
    }
    pricing_row = {
        "ticker": "VWCE",
        "fund_name": "Vanguard FTSE All-World UCITS ETF",
        "isin": "IE00BK5BQT80",
        "exchange": "Xetra",
        "close_date": REPORT_DATE,
        "close_price": 169.06,
        "currency": "EUR",
        "authority_status": "fresh_exact_unverified",
        "verification_status": "fresh_exact_unverified",
        "valuation_grade": True,
        "primary_provider": "alpha_vantage",
        "verification_providers": [],
    }
    return {
        "schema_version": "etf_eu_client_grade_report_state_v3",
        "state_valid": True,
        "blockers": [],
        "report_date": REPORT_DATE,
        "authority": {
            "portfolio_mutation": False,
            "trade_ledger_mutation": False,
            "real_broker_execution": False,
            "production_delivery_authority": False,
        },
        "portfolio": {
            "starting_capital_eur": 1500.0,
            "cash_eur": 1000.0,
            "invested_market_value_eur": 338.12,
            "nav_eur": 1338.12,
            "since_inception_return_pct": 0.0,
            "positions": [position],
            "position_count": 1,
            "cash_classification": "Tactical reserve",
            "derived_valuation": {
                "lines": [
                    {
                        "ticker": "VWCE",
                        "source_agreement_status": "fresh_exact_unverified",
                    }
                ]
            },
        },
        "pricing": {
            "rows": [pricing_row],
            "authorized_statuses": ["fresh_exact_unverified", "fresh_exact_verified"],
        },
        "verification_funnel": {
            "observed_lines": 1,
            "priced_lines": 1,
            "authorized_lines": 1,
            "verified_lines": 0,
            "primary_only_lines": 1,
            "unresolved_lines": 0,
        },
        "macro": {
            "regime": "Risk-on growth",
            "regime_nl": "Risk-on groei",
            "fresh_for_report": True,
            "source_report_date": REPORT_DATE,
            "fed": {},
            "ecb": {},
        },
        "opportunity_radar": [],
        "second_order_effects": [],
        "equity_curve": {
            "show_chart": False,
            "fallback_nl": "Onvoldoende historie voor een curve.",
            "fallback_en": "Insufficient history for a curve.",
        },
        "next_run_input": {},
        "current_reunderwriting": {
            "status": "COMPLETE",
            "cash_after_explanation": "Residual cash remains tactical reserve pending a distinct fully fundable lane.",
        },
    }


def _funded_portfolio() -> dict:
    return {
        "base_currency": "EUR",
        "cash_eur": 1000.0,
        "positions": [
            {
                "ticker": "VWCE",
                "exchange_ticker": "VWCE",
                "isin": "IE00BK5BQT80",
                "shares": 2,
                "trading_currency": "EUR",
                "avg_entry_local": 160.0,
                "current_price_local": 165.0,
                "market_value_local": 330.0,
                "market_value_eur": 330.0,
                "current_weight_pct": 24.81203,
            }
        ],
    }


class CoreTruthV6RegressionTests(unittest.TestCase):
    def test_primary_only_and_verified_authority_reach_fundability(self) -> None:
        for status in ("fresh_exact_unverified", "fresh_exact_verified"):
            with self.subTest(status=status):
                self.assertEqual(
                    _fundability(_candidate(), "verified_candidate", _pricing(status), False),
                    "FUNDABLE_REQUIRES_ALLOCATION_DECISION",
                )

    def test_disagreement_remains_fail_closed_for_fundability(self) -> None:
        disagreement = _pricing("provider_disagreement")
        disagreement["valuation_grade"] = False
        self.assertEqual(
            _fundability(_candidate(), "verified_candidate", disagreement, False),
            "PRICING_AUTHORITY_REQUIRED",
        )

    def test_revaluation_projects_provider_evidence_onto_normalized_position(self) -> None:
        pricing = {
            "run_id": "core-truth-provider-evidence",
            "report_date": REPORT_DATE,
            "report_pricing_gate_passed": True,
            "rows": [_pricing("fresh_exact_verified")],
        }
        derived = revalue_portfolio(_funded_portfolio(), pricing, report_date=REPORT_DATE)
        position = derived["positions"][0]
        self.assertEqual(position["primary_provider"], "alpha_vantage")
        self.assertEqual(position["verification_providers"], ["yahoo_chart"])
        self.assertEqual(position["agreeing_providers"], ["alpha_vantage", "yahoo_chart"])
        self.assertEqual(position["pricing_status"], "fresh_exact_verified")

    def test_primary_only_markdown_is_native_and_bilingual(self) -> None:
        state = _primary_only_state()
        nl = render_funded_markdown(state, language="nl")
        en = render_funded_markdown(state, language="en")

        self.assertIn("Exacte slotkoers · geen actuele onafhankelijke verifier", nl)
        self.assertIn("Exact close · no current independent verifier", en)
        self.assertIn("alpha_vantage (geen actuele verifier)", nl)
        self.assertIn("alpha_vantage (no current verifier)", en)
        self.assertNotIn("Exacte slotkoers · onafhankelijk geverifieerd", nl)
        self.assertNotIn("Exact close · independently verified", en)
        self.assertNotIn("qualified_development_consensus", nl + en)
        self.assertNotIn("qualified_completed_close_primary_plus_verification", nl + en)
        self.assertEqual(validate_funded_markdown(nl, state, language="nl"), [])
        self.assertEqual(validate_funded_markdown(en, state, language="en"), [])

    def test_primary_only_html_matches_canonical_confidence_semantics(self) -> None:
        state = _primary_only_state()
        nl = build_html(state, "nl")
        en = build_html(state, "en")

        self.assertIn("Exacte slotkoers · geen actuele onafhankelijke verifier", nl)
        self.assertIn("Exact close · no current independent verifier", en)
        self.assertNotIn("Exacte slotkoers · onafhankelijk geverifieerd", nl)
        self.assertNotIn("Exact close · independently verified", en)
        for retired in (
            "qualified_development_consensus",
            "qualified_completed_close_primary_plus_verification",
            "two-provider completed-close consensus",
        ):
            self.assertNotIn(retired, nl + en)


if __name__ == "__main__":
    unittest.main()
