from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from pricing.ucits_price_provider_engine import build_legacy_validation_artifact
from tools.build_etf_eu_routine_report_package_v2 import build as build_package
from tools.validate_etf_eu_client_grade_report_v2_standalone import validate as validate_client_package
from tools.validate_etf_eu_markdown_delivery_artifacts import validate as validate_markdown


FUNDED = [
    ("VWCE", "IE00BK5BQT80", 151, 14000.0),
    ("EUNA", "IE00BDBRDM35", 1526, 15000.0),
    ("SXR8", "IE00B5BMR087", 10, 7000.0),
    ("L0CK", "IE00BG0J4C88", 934, 13791.60),
]


def _portfolio() -> dict:
    return {
        "schema_version": "etf_eu_portfolio_state_v1",
        "portfolio_mode": "model_portfolio",
        "base_currency": "EUR",
        "inception_date": "2026-07-01",
        "starting_capital_eur": 100000.0,
        "cash_eur": 50208.40,
        "invested_market_value_eur": 49791.60,
        "nav_eur": 100000.0,
        "positions": [
            {
                "exchange_ticker": ticker,
                "ticker": ticker,
                "isin": isin,
                "venue_code": "XETR",
                "exchange": "Xetra",
                "currency": "EUR",
                "shares": shares,
                "market_value_eur": value,
                "current_weight_pct": value / 1000.0,
                "portfolio_role": {
                    "VWCE": "Global core",
                    "EUNA": "Bond stabiliser",
                    "SXR8": "U.S. equity overweight",
                    "L0CK": "Cybersecurity satellite",
                }[ticker],
            }
            for ticker, isin, shares, value in FUNDED
        ],
    }


def _qualification() -> dict:
    lines = []
    for index, (ticker, isin, _shares, _value) in enumerate(FUNDED, start=1):
        providers = [
            {
                "provider": "provider_a",
                "provider_symbol": ticker,
                "pricing_status": "priced",
                "close_date": "2026-08-07",
                "observed_at_utc": "2026-08-08T00:00:00Z",
                "blockers": [],
            },
            {
                "provider": "provider_b",
                "provider_symbol": ticker,
                "pricing_status": "priced",
                "close_date": "2026-08-07",
                "observed_at_utc": "2026-08-08T00:00:01Z",
                "blockers": [],
            },
        ]
        lines.append(
            {
                "basket_id": f"funded-{index}",
                "fund_name": ticker,
                "instrument_type": "UCITS ETF",
                "exchange": "Xetra",
                "ticker": ticker,
                "expected_isin": isin,
                "expected_venue_code": "XETR",
                "expected_currency": "EUR",
                "funded": True,
                "selected_close_date": "2026-08-07",
                "consensus_close_price": 100.0 + index,
                "same_date_provider_count": 2,
                "qualification_status": "qualified_development_consensus",
                "identity_assurance_status": "metadata_anchored_exact_line",
                "identity_anchor_provider_count": 1,
                "provider_results": providers,
                "agreeing_providers": ["provider_a", "provider_b"],
                "agreement_spread_pct": 0.1,
            }
        )
    return {
        "schema_version": "ucits_price_provider_qualification_v1",
        "generated_at_utc": "2026-08-08T00:00:02Z",
        "report_date": "2026-08-07",
        "provider_order": ["provider_a", "provider_b"],
        "provider_configuration": {},
        "funded_line_count": 4,
        "funded_consensus_count": 4,
        "funded_identity_anchor_count": 4,
        "report_pricing_gate_passed": True,
        "lines": lines,
    }


def test_full_candidate_package_builds_and_validates_all_six_client_artifacts(tmp_path: Path) -> None:
    run_id = "e2e-full-pr91-repair"
    suffix = "260807e2e"
    pricing_qualification = tmp_path / "qualification.json"
    pricing_artifact = tmp_path / "pricing.json"
    portfolio_state = tmp_path / "portfolio.json"
    valuation_history = tmp_path / "valuation.csv"
    trade_ledger = tmp_path / "ledger.csv"
    scorecard = tmp_path / "scorecard.csv"
    macro_pack = tmp_path / "macro.json"
    previous_manifest = tmp_path / "previous_manifest.json"
    previous_closeout = tmp_path / "previous_closeout.json"
    output_dir = tmp_path / "client"

    pricing_qualification.write_text(json.dumps(_qualification()), encoding="utf-8")
    portfolio_state.write_text(json.dumps(_portfolio()), encoding="utf-8")
    valuation_history.write_text("date,nav_eur,cash_eur,invested_market_value_eur\n", encoding="utf-8")
    trade_ledger.write_text("date,ticker,action\n", encoding="utf-8")
    previous_manifest.write_text("{}", encoding="utf-8")
    previous_closeout.write_text("{}", encoding="utf-8")
    macro_pack.write_text(
        json.dumps(
            {
                "report_date": "2026-08-07",
                "generated_at_utc": "2026-08-08T00:00:00Z",
                "regime": {"label": "Policy transition / mixed regime", "confidence": 0.7},
                "central_banks": {},
                "policy_catalysts": [],
                "donor_provenance": {
                    "source_report_date": "2026-08-07",
                    "source_generated_at_utc": "2026-08-08T00:00:00Z",
                },
            }
        ),
        encoding="utf-8",
    )

    build_legacy_validation_artifact(
        qualification_path=pricing_qualification,
        output_path=pricing_artifact,
        source_basket="config/ucits_close_price_validation_basket.yml",
        run_id=run_id,
    )

    outputs = build_package(
        Namespace(
            run_id=run_id,
            report_date="2026-08-07",
            report_suffix=suffix,
            pricing_artifact=str(pricing_artifact),
            macro_pack=str(macro_pack),
            registry="config/ucits_symbol_registry.yml",
            proxy_map="config/ucits_benchmark_proxy_map.yml",
            donor_lane_artifact=None,
            output_dir=str(output_dir),
            portfolio_state=str(portfolio_state),
            valuation_history=str(valuation_history),
            trade_ledger=str(trade_ledger),
            recommendation_scorecard=str(scorecard),
            previous_routine_manifest=str(previous_manifest),
            previous_delivery_closeout_manifest=str(previous_closeout),
        )
    )

    state_path = outputs["state"]
    nl_md = output_dir / f"weekly_etf_eu_review_nl_{suffix}.md"
    en_md = output_dir / f"weekly_etf_eu_review_{suffix}.md"
    nl_html = output_dir / f"weekly_etf_eu_review_nl_{suffix}.html"
    en_html = output_dir / f"weekly_etf_eu_review_{suffix}.html"
    nl_pdf = output_dir / f"weekly_etf_eu_review_nl_{suffix}.pdf"
    en_pdf = output_dir / f"weekly_etf_eu_review_{suffix}.pdf"

    for path in (nl_md, en_md, nl_html, en_html, nl_pdf, en_pdf, state_path, scorecard):
        assert Path(path).exists(), path
        assert Path(path).stat().st_size > 0, path

    state = json.loads(Path(state_path).read_text(encoding="utf-8"))
    assert state["schema_version"] == "etf_eu_client_grade_report_state_v2"
    assert state["pricing_contract"]["report_pricing_gate_passed"] is True
    assert state["pricing_contract"]["funded_position_count"] == 4

    markdown_result = validate_markdown(Path(state_path), nl_md, en_md)
    assert markdown_result["passed"] is True, markdown_result["blockers"]
    assert markdown_result["funded_tickers"] == ["EUNA", "L0CK", "SXR8", "VWCE"]

    nl_text = nl_md.read_text(encoding="utf-8")
    en_text = en_md.read_text(encoding="utf-8")
    assert "4 gefinancierde UCITS-posities" in nl_text
    assert "4 funded UCITS positions" in en_text
    assert "L0CK" in nl_text and "L0CK" in en_text
    assert "drie gefinancierde UCITS-posities" not in nl_text
    assert "three funded UCITS positions" not in en_text

    validation = validate_client_package(
        Namespace(
            state=str(state_path),
            dutch_html=str(nl_html),
            dutch_pdf=str(nl_pdf),
            english_html=str(en_html),
            english_pdf=str(en_pdf),
            output=str(tmp_path / "client_validation.json"),
            strict=True,
        )
    )
    assert validation["client_grade_v2_passed"] is True, validation["blockers"]
