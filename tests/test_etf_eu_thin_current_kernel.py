from __future__ import annotations

import csv
import json
from pathlib import Path

from runtime.current.render import render_html, render_markdown
from runtime.current.review_state import build_review_state


def _normalized_state() -> dict:
    return {
        "schema_version": "test_normalized_state",
        "state_valid": True,
        "sources": {"protected_portfolio_state": "output/etf_eu_portfolio_state.json"},
        "portfolio": {
            "nav_eur": 101000.0,
            "cash_eur": 21000.0,
            "invested_market_value_eur": 80000.0,
            "positions": [
                {
                    "ticker": "SXR8", "exchange_ticker": "SXR8", "isin": "IE00B5BMR087",
                    "fund_name": "iShares Core S&P 500 UCITS ETF USD Acc", "portfolio_role": "US equity overweight",
                    "shares": 10, "market_value_eur": 6500.0, "current_weight_pct": 6.435644,
                    "current_price_local": 650.0, "price_date": "2026-08-28", "pricing_status": "valuation_grade_exact_close",
                    "verification_status": "exact_close_primary_only_verifier_unavailable", "identity_binding_valid": True,
                    "current_allocation_decision": "hold", "fresh_cash_implication": "Hold", "reunderwriting_complete": True,
                    "thesis_assessment": "US equity overweight remains explicit rather than diversification.",
                    "best_alternative": "No superior replacement established", "next_review_trigger": "Weekly re-underwriting",
                    "portfolio_contribution_eur": 100.0, "source_run_id": "fixture",
                },
                {
                    "ticker": "EUNA", "exchange_ticker": "EUNA", "isin": "IE00BDBRDM35",
                    "fund_name": "iShares Core Global Aggregate Bond UCITS ETF EUR Hedged Acc", "portfolio_role": "Stabilising aggregate bonds",
                    "shares": 1000, "market_value_eur": 5000.0, "current_weight_pct": 4.950495,
                    "current_price_local": 5.0, "price_date": "2026-08-28", "pricing_status": "valuation_grade_exact_close",
                    "verification_status": "exact_close_independently_verified", "identity_binding_valid": True,
                    "current_allocation_decision": "hold", "fresh_cash_implication": "Hold", "reunderwriting_complete": True,
                    "thesis_assessment": "Bond ballast remains useful.", "best_alternative": "None established",
                    "next_review_trigger": "Weekly re-underwriting", "portfolio_contribution_eur": -25.0, "source_run_id": "fixture",
                },
            ],
        },
        "cash_policy": {"cash_after_explanation": "Keep cash as tactical reserve pending a stronger distinct opportunity."},
        "pricing_contract": {"pricing_authority_mode": "primary_exact_close_plus_optional_verification"},
        "donor_discovery_bridge": {
            "best_fundable_challenger": {"ticker": "IQQQ", "isin": "IE00B1TXK627", "fund_name": "iShares Global Water UCITS ETF", "donor_total_score": 4.5},
            "assessed_lanes": [],
        },
    }


def _write_pricing(path: Path) -> None:
    path.write_text(json.dumps({
        "report_date": "2026-08-28",
        "report_pricing_gate_passed": True,
        "rows": [{
            "isin": "IE00BK5BQT80", "ticker": "VWCE", "venue_code": "XETR", "currency": "EUR",
            "close_date": "2026-08-28", "close_price": 170.0, "valuation_grade": True, "blockers": [],
            "agreeing_providers": ["primary"], "source_agreement_status": "primary_exact_close_verifier_missing",
            "source_id": "fixture", "source_name": "Fixture", "source_quality_status": "qualified",
        }],
    }), encoding="utf-8")


def _write_comparator(path: Path) -> None:
    path.write_text(
        """primary_comparator:\n  comparator_id: vwce\n  purpose: opportunity_cost\n  isin: IE00BK5BQT80\n  ticker: VWCE\n  mic: XETR\n  currency: EUR\n  effective_date: 2026-08-30\n""",
        encoding="utf-8",
    )


def _write_history(path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date", "portfolio_nav_eur", "comparator_close_eur", "comparator_index"])
        writer.writeheader()
        writer.writerow({"date": "2026-08-14", "portfolio_nav_eur": "100000", "comparator_close_eur": "168", "comparator_index": "100"})


def test_review_state_is_frozen_and_comparator_need_not_be_funded(tmp_path: Path) -> None:
    comparator = tmp_path / "comparator.yml"
    pricing = tmp_path / "pricing.json"
    history = tmp_path / "history.csv"
    _write_comparator(comparator)
    _write_pricing(pricing)
    _write_history(history)

    review = build_review_state(
        _normalized_state(), comparator_config_path=comparator, accountability_history_path=history,
        report_date="2026-08-28", run_id="fixture-run", pricing_artifact=str(pricing),
    )
    assert review["state_valid"] is True
    assert review["semantic_state_frozen"] is True
    assert review["semantic_mutation_allowed_downstream"] is False
    assert review["accountability"]["status"] == "COMPLETE"
    assert review["accountability"]["comparator_ticker"] == "VWCE"
    assert "VWCE" not in {row["ticker"] for row in review["funded_position_decisions"]}
    assert all(row["action"] == "HOLD" for row in review["funded_position_decisions"])
    assert next(row for row in review["funded_position_decisions"] if row["ticker"] == "SXR8")["confidence"] == "MEDIUM"

    before = json.dumps(review, sort_keys=True)
    surfaces = [render_markdown(review, "nl"), render_markdown(review, "en"), render_html(review, "nl"), render_html(review, "en")]
    assert before == json.dumps(review, sort_keys=True)
    for surface in surfaces:
        assert "€101,000.00" in surface
        assert "VWCE" in surface


def test_unresolved_position_fails_review_state(tmp_path: Path) -> None:
    comparator = tmp_path / "comparator.yml"
    pricing = tmp_path / "pricing.json"
    history = tmp_path / "history.csv"
    _write_comparator(comparator)
    _write_pricing(pricing)
    _write_history(history)
    normalized = _normalized_state()
    normalized["portfolio"]["positions"][1]["reunderwriting_complete"] = False
    review = build_review_state(
        normalized, comparator_config_path=comparator, accountability_history_path=history,
        report_date="2026-08-28", run_id="fixture-run", pricing_artifact=str(pricing),
    )
    assert review["state_valid"] is False
    assert any(item.startswith("position_unresolved:EUNA") for item in review["blockers"])
