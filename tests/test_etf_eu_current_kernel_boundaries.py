from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from runtime.current.discovery import build_discovery_bridge
from runtime.current.normalized_state import build_normalized_state
from runtime.current.pricing import find_exact_price_row, verification_status
from runtime.current.reunderwriting import apply_current_reunderwriting


REPORT_DATE = "2026-08-28"


def test_primary_only_exact_close_is_explicitly_unverified_but_usable() -> None:
    row = {
        "isin": "IE0000000000",
        "ticker": "TEST",
        "venue_code": "XETR",
        "currency": "EUR",
        "close_date": REPORT_DATE,
        "close_price": 10.0,
        "valuation_grade": True,
        "blockers": [],
        "agreeing_providers": ["primary"],
        "source_agreement_status": "primary_exact_close_verifier_missing",
    }
    pricing = {"rows": [row]}
    selected = find_exact_price_row(
        pricing,
        isin=row["isin"],
        ticker=row["ticker"],
        venue_code=row["venue_code"],
        currency=row["currency"],
        report_date=REPORT_DATE,
    )
    assert selected is row
    assert verification_status(selected) == "exact_close_primary_only_verifier_unavailable"


def test_disagreement_or_other_upstream_blocker_fails_closed() -> None:
    row = {
        "isin": "IE0000000000",
        "ticker": "TEST",
        "venue_code": "XETR",
        "currency": "EUR",
        "close_date": REPORT_DATE,
        "close_price": 10.0,
        "valuation_grade": False,
        "blockers": ["provider_disagreement"],
        "agreeing_providers": [],
        "source_agreement_status": "provider_disagreement",
    }
    with pytest.raises(RuntimeError, match="not valuation-grade|has blockers"):
        find_exact_price_row(
            {"rows": [row]},
            isin=row["isin"],
            ticker=row["ticker"],
            venue_code=row["venue_code"],
            currency=row["currency"],
            report_date=REPORT_DATE,
        )


def test_non_eur_funded_line_fails_closed_without_fx_evidence(tmp_path: Path) -> None:
    portfolio = tmp_path / "portfolio.json"
    pricing = tmp_path / "pricing.json"
    registry = tmp_path / "registry.yml"
    portfolio.write_text(
        json.dumps(
            {
                "base_currency": "EUR",
                "cash_eur": 1000.0,
                "positions": [
                    {
                        "ticker": "GBP1",
                        "exchange_ticker": "GBP1",
                        "isin": "IE0000000001",
                        "trading_currency": "GBP",
                        "investability_status": "funded_model_position",
                        "shares": 10,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    pricing.write_text(json.dumps({"report_date": REPORT_DATE, "report_pricing_gate_passed": True, "rows": []}), encoding="utf-8")
    registry.write_text("funds: []\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="FX valuation evidence is required"):
        build_normalized_state(
            portfolio_state_path=portfolio,
            pricing_artifact_path=pricing,
            registry_path=registry,
            report_date=REPORT_DATE,
            run_id="fixture",
        )


def test_discovery_accepts_valuation_grade_primary_without_second_provider(tmp_path: Path) -> None:
    donor = tmp_path / "donor.json"
    proxy_map = tmp_path / "proxy.yml"
    pricing = tmp_path / "pricing.json"
    portfolio = tmp_path / "portfolio.json"

    donor.write_text(
        json.dumps(
            {
                "report_date": REPORT_DATE,
                "discovery_engine_version": "fixture",
                "assessed_lanes": [
                    {
                        "lane_name": "Water",
                        "taxonomy_tag": "water",
                        "bucket": "thematic",
                        "primary_etf": "PHO",
                        "alternative_etf": "FIW",
                        "total_score": 4.6,
                        "promoted_to_live_radar": True,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    proxy_map.write_text(
        """proxy_mappings:
  - exposure_id: water
    donor_proxies: [PHO, FIW]
    status: mapped
    ucits_candidates:
      - fund_name: Fixture Water UCITS ETF
        isin: IE0000000002
        exchange_ticker: WATR
        exchange: Xetra
        identity_status: complete
""",
        encoding="utf-8",
    )
    pricing.write_text(
        json.dumps(
            {
                "report_date": REPORT_DATE,
                "report_pricing_gate_passed": True,
                "rows": [
                    {
                        "isin": "IE0000000002",
                        "ticker": "WATR",
                        "currency": "EUR",
                        "close_date": REPORT_DATE,
                        "close_price": 25.0,
                        "valuation_grade": True,
                        "blockers": [],
                        "agreeing_providers": ["primary"],
                        "source_agreement_status": "primary_exact_close_verifier_missing",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    portfolio.write_text(json.dumps({"positions": []}), encoding="utf-8")

    bridge = build_discovery_bridge(
        donor_lane_artifact=donor,
        proxy_map_path=proxy_map,
        pricing_artifact_path=pricing,
        portfolio_state_path=portfolio,
        report_date=REPORT_DATE,
    )

    challenger = bridge["best_fundable_challenger"]
    assert challenger["ticker"] == "WATR"
    assert challenger["fundability_status"] == "FUNDABLE_REQUIRES_ALLOCATION_DECISION"
    assert challenger["pricing_verification_status"] == "exact_close_primary_only_verifier_unavailable"
    assert bridge["authority"]["exact_primary_close_can_be_valuation_grade_without_verifier"] is True
    assert bridge["authority"]["explicit_allocation_decision_required"] is True


def test_reunderwriting_is_dynamic_for_arbitrary_funded_ticker(tmp_path: Path) -> None:
    history = tmp_path / "recommendation.csv"
    macro = tmp_path / "macro.json"
    evidence = tmp_path / "evidence.json"
    fieldnames = [
        "report_date",
        "run_id",
        "ticker",
        "isin",
        "reunderwriting_complete",
        "current_allocation_decision",
        "fresh_cash_implication",
        "thesis_score",
        "implementation_score",
        "thesis_assessment",
        "best_alternative",
        "factor_overlap_level",
        "factor_overlap_flag",
        "hedge_validity_status",
        "next_review_trigger",
    ]
    with history.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(
            {
                "report_date": "2026-08-21",
                "run_id": "prior",
                "ticker": "ZZZ1",
                "isin": "IE0000000003",
                "reunderwriting_complete": "True",
                "current_allocation_decision": "HOLD",
                "fresh_cash_implication": "Hold",
                "thesis_score": "4.2",
                "implementation_score": "4.4",
                "thesis_assessment": "Historical thesis memory.",
                "best_alternative": "None established",
                "factor_overlap_level": "Low",
                "factor_overlap_flag": "",
                "hedge_validity_status": "Not a hedge",
                "next_review_trigger": "Weekly review",
            }
        )
    macro.write_text(
        json.dumps({"donor_provenance": {"source_report_date": REPORT_DATE}, "regime_label": "fixture"}),
        encoding="utf-8",
    )
    normalized = {
        "schema_version": "fixture",
        "state_valid": True,
        "blockers": [],
        "portfolio": {
            "cash_eur": 10000.0,
            "nav_eur": 50000.0,
            "positions": [
                {
                    "ticker": "ZZZ1",
                    "exchange_ticker": "ZZZ1",
                    "isin": "IE0000000003",
                    "identity_binding_valid": True,
                    "pricing_status": "valuation_grade_exact_close",
                    "price_date": REPORT_DATE,
                    "verification_status": "exact_close_primary_only_verifier_unavailable",
                    "unrealized_pnl_pct": 1.0,
                }
            ],
        },
    }
    bridge = {
        "assessed_lanes": [],
        "fundable_challengers": [],
        "best_fundable_challenger": None,
    }

    result = apply_current_reunderwriting(
        normalized,
        recommendation_history_path=history,
        macro_pack_path=macro,
        discovery_bridge=bridge,
        report_date=REPORT_DATE,
        run_id="current",
        evidence_output_path=evidence,
    )

    position = result["portfolio"]["positions"][0]
    assert position["ticker"] == "ZZZ1"
    assert position["reunderwriting_complete"] is True
    assert position["current_allocation_decision"] == "hold"
    assert position["source_run_id"] == "current"
    assert result["current_reunderwriting"]["funded_position_count"] == 1
    assert result["current_reunderwriting"]["incomplete_tickers"] == []
    assert result["state_valid"] is True
