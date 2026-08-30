from __future__ import annotations

import copy
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
                    "ticker": "VWCE",
                    "exchange_ticker": "VWCE",
                    "isin": "IE00BK5BQT80",
                    "fund_name": "Vanguard FTSE All-World UCITS ETF USD Acc",
                    "portfolio_role": "Global core equity",
                    "shares": 100,
                    "market_value_eur": 17000.0,
                    "current_weight_pct": 16.831683,
                    "current_price_local": 170.0,
                    "price_date": "2026-08-28",
                    "pricing_status": "fresh_exact_unverified",
                    "verification_status": "primary_exact_close_verifier_missing",
                    "current_allocation_decision": "hold",
                    "fresh_cash_implication": "Hold",
                    "reunderwriting_complete": True,
                    "thesis_assessment": "Broad global equity remains the core anchor.",
                    "best_alternative": "None established",
                    "next_review_trigger": "Weekly re-underwriting",
                    "portfolio_contribution_eur": 100.0,
                    "source_run_id": "fixture",
                },
                {
                    "ticker": "EUNA",
                    "exchange_ticker": "EUNA",
                    "isin": "IE00BDBRDM35",
                    "fund_name": "iShares Core Global Aggregate Bond UCITS ETF EUR Hedged Acc",
                    "portfolio_role": "Stabilising aggregate bonds",
                    "shares": 1000,
                    "market_value_eur": 5000.0,
                    "current_weight_pct": 4.950495,
                    "current_price_local": 5.0,
                    "price_date": "2026-08-28",
                    "pricing_status": "fresh_exact_verified",
                    "verification_status": "verified",
                    "current_allocation_decision": "hold",
                    "fresh_cash_implication": "Hold",
                    "reunderwriting_complete": True,
                    "thesis_assessment": "Bond ballast remains useful.",
                    "best_alternative": "None established",
                    "next_review_trigger": "Weekly re-underwriting",
                    "portfolio_contribution_eur": -25.0,
                    "source_run_id": "fixture",
                },
            ],
        },
        "cash_policy": {"cash_after_explanation": "Keep cash as tactical reserve pending a stronger distinct opportunity."},
        "pricing_contract": {"pricing_authority_mode": "primary_exact_close_plus_optional_verification"},
        "donor_discovery_bridge": {"rows": []},
    }


def test_review_state_is_frozen_and_renderers_do_not_mutate(tmp_path: Path) -> None:
    comparator = tmp_path / "comparator.yml"
    comparator.write_text(
        """primary_comparator:\n  comparator_id: vwce\n  purpose: opportunity_cost\n  isin: IE00BK5BQT80\n  ticker: VWCE\n""",
        encoding="utf-8",
    )
    history = tmp_path / "history.csv"
    with history.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date", "portfolio_nav_eur", "comparator_close_eur", "comparator_index"])
        writer.writeheader()
        writer.writerow({"date": "2026-08-14", "portfolio_nav_eur": "100000", "comparator_close_eur": "168", "comparator_index": "100"})

    normalized = _normalized_state()
    review = build_review_state(
        normalized,
        comparator_config_path=comparator,
        accountability_history_path=history,
        report_date="2026-08-28",
        run_id="fixture-run",
        pricing_artifact="pricing.json",
    )
    assert review["state_valid"] is True
    assert review["semantic_state_frozen"] is True
    assert review["semantic_mutation_allowed_downstream"] is False
    assert review["accountability"]["status"] == "COMPLETE"
    assert review["accountability"]["active_return_pp"] < review["accountability"]["portfolio_period_return_pct"]
    assert all(row["action"] == "HOLD" for row in review["funded_position_decisions"])
    assert next(row for row in review["funded_position_decisions"] if row["ticker"] == "VWCE")["confidence"] == "MEDIUM"

    before = json.dumps(review, sort_keys=True)
    nl_md = render_markdown(review, "nl")
    en_md = render_markdown(review, "en")
    nl_html = render_html(review, "nl")
    en_html = render_html(review, "en")
    after = json.dumps(review, sort_keys=True)
    assert before == after
    for surface in (nl_md, en_md, nl_html, en_html):
        assert "€101,000.00" in surface
        assert "VWCE" in surface


def test_unresolved_position_fails_review_state(tmp_path: Path) -> None:
    comparator = tmp_path / "comparator.yml"
    comparator.write_text("primary_comparator:\n  comparator_id: vwce\n  isin: IE00BK5BQT80\n  ticker: VWCE\n", encoding="utf-8")
    history = tmp_path / "history.csv"
    history.write_text("date,portfolio_nav_eur,comparator_close_eur,comparator_index\n2026-08-14,100000,168,100\n", encoding="utf-8")
    normalized = _normalized_state()
    normalized["portfolio"]["positions"][1]["reunderwriting_complete"] = False
    review = build_review_state(
        normalized,
        comparator_config_path=comparator,
        accountability_history_path=history,
        report_date="2026-08-28",
        run_id="fixture-run",
        pricing_artifact="pricing.json",
    )
    assert review["state_valid"] is False
    assert any(item.startswith("position_unresolved:EUNA") for item in review["blockers"])
