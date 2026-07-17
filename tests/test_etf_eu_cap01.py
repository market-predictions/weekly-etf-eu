from __future__ import annotations

import csv
import json
from pathlib import Path

from runtime.apply_etf_eu_guarded_capital_activation import apply
from runtime.build_etf_eu_allocation_decision import build_decision
from runtime.equity_curve_eu_contract import render_equity_curve_svg
from runtime.inject_etf_eu_funded_identity_strip import inject_funded_identity_strip
from runtime.render_etf_eu_client_grade_v2_funded import funded_overlay, patch_copy
from tools.validate_etf_eu_allocation_decision import validate
from tools.validate_etf_eu_client_grade_report_v2_standalone import funded_state_blockers, isin_surface_evidence

ROOT = Path(__file__).resolve().parents[1]


def test_cap01_dry_run_and_guarded_apply(tmp_path: Path) -> None:
    state = tmp_path / "state.json"
    state.write_text(json.dumps({"schema_version": "etf_eu_portfolio_state_v1", "portfolio_mode": "dutch_eu_ucits_model_bootstrap", "base_currency": "EUR", "valuation_source": "cash_only_bootstrap", "inception_date": "2026-05-30", "starting_capital_eur": 100000.0, "cash_eur": 100000.0, "invested_market_value_eur": 0.0, "nav_eur": 100000.0, "positions": []}) + "\n", encoding="utf-8")
    ledger = tmp_path / "ledger.csv"
    ledger.write_text("trade_id,trade_date,source_report,isin,exchange_ticker,action,shares_delta,previous_weight_pct,new_weight_pct,weight_change_pct,target_weight_pct,conviction_tier,portfolio_role,funding_source_note\n", encoding="utf-8")
    pricing = tmp_path / "pricing.json"
    pricing.write_text(json.dumps({"rows": [
        {"fund_name": "iShares Core S&P 500 UCITS ETF USD Acc", "isin": "IE00B5BMR087", "instrument_type": "UCITS ETF", "exchange": "Xetra", "ticker": "SXR8", "currency": "EUR", "verification_status": "verified_ucits_trading_line", "pricing_status": "priced_non_authoritative", "close_date": "2026-07-15", "close_price": 710.0},
        {"fund_name": "Vanguard FTSE All-World UCITS ETF USD Acc", "isin": "IE00BK5BQT80", "instrument_type": "UCITS ETF", "exchange": "Xetra", "ticker": "VWCE", "currency": "EUR", "verification_status": "candidate_requires_verification", "pricing_status": "priced_non_authoritative", "close_date": "2026-07-15", "close_price": 165.66},
    ]}) + "\n", encoding="utf-8")
    decision_path = tmp_path / "decision.json"
    decision = build_decision(policy_path=ROOT / "config/etf_eu_target_allocation.yml", portfolio_state_path=state, pricing_artifact_path=pricing, run_id="20260716_010500", report_date_raw="2026-07-16", output_path=decision_path)
    errors, _, evidence = validate(decision)
    assert not errors and evidence["allocation_decision_valid"] is True
    assert evidence["broker_neutral_model_authority_passed"] is True
    assert decision["authority"]["broker_specific_permission_required_for_model"] is False
    assert decision["authority"]["broker_permission_required_for_real_execution"] is True
    assert all("broker" not in str(blocker).lower() for row in decision["decisions"] for blocker in (row.get("blockers") or []))
    buys = [row for row in decision["decisions"] if row.get("action") == "buy"]
    assert len(buys) == 1 and buys[0]["exchange_ticker"] == "SXR8"
    assert "broker_permission_not_required_for_model" in buys[0]["reason_codes"]
    assert buys[0]["shares_delta"] == 10 and buys[0]["trade_value_eur"] == 7100.0
    assert decision["summary"]["projected_cash_eur"] == 92900.0
    validation_path = tmp_path / "validation.json"
    validation_path.write_text(json.dumps({"passed": True, "allocation_decision_valid": True}), encoding="utf-8")
    result = apply(decision_path=decision_path, validation_path=validation_path, portfolio_state_path=state, trade_ledger_path=ledger, confirmation="CONFIRM_ETF_EU_MODEL_CAPITAL_ACTIVATION", output_path=tmp_path / "result.json")
    assert result["status"] == "applied"
    updated = json.loads(state.read_text(encoding="utf-8"))
    assert updated["cash_eur"] == 92900.0 and updated["invested_market_value_eur"] == 7100.0 and updated["nav_eur"] == 100000.0
    assert updated["positions"][0]["shares"] == 10 and updated["positions"][0]["exchange_ticker"] == "SXR8"
    rows = list(csv.DictReader(ledger.open("r", encoding="utf-8", newline="")))
    assert any(row["exchange_ticker"] == "SXR8" and row["action"] == "Buy" for row in rows)
    second = apply(decision_path=decision_path, validation_path=validation_path, portfolio_state_path=state, trade_ledger_path=ledger, confirmation="CONFIRM_ETF_EU_MODEL_CAPITAL_ACTIVATION", output_path=tmp_path / "result2.json")
    assert second["status"] == "already_applied"
    assert len(list(csv.DictReader(ledger.open("r", encoding="utf-8", newline="")))) == len(rows)


def test_funded_report_reconciles_three_positions_and_removes_broker_model_gates() -> None:
    positions = [
        {"exchange_ticker": "VWCE", "shares": 151, "current_weight_pct": 24.959177, "strategic_target_weight_pct": 50.0, "shares_delta_this_run": 151, "price_date": "2026-07-16"},
        {"exchange_ticker": "EUNA", "shares": 1526, "current_weight_pct": 7.495996, "strategic_target_weight_pct": 15.0, "shares_delta_this_run": 1526, "price_date": "2026-07-15"},
        {"exchange_ticker": "SXR8", "shares": 10, "current_weight_pct": 7.115419, "strategic_target_weight_pct": 15.0, "shares_delta_this_run": 0, "price_date": "2026-07-16"},
    ]
    state = {
        "portfolio": {"positions": positions, "nav_eur": 100016.60, "cash_eur": 60439.44, "invested_market_value_eur": 39577.16},
        "opportunity_radar": [
            {"lane_id": "core_us_equity", "candidate_tickers": ["CSPX", "SXR8"], "status": "operationally_mature_not_funded", "next_confirmation_nl": "Bevestig brokerbeschikbaarheid", "next_confirmation_en": "Confirm broker availability"},
            {"lane_id": "global_equity", "candidate_tickers": ["VWCE", "EUNL", "IWDA"], "status": "operationally_mature_not_funded", "next_confirmation_nl": "Bevestig brokerbeschikbaarheid", "next_confirmation_en": "Confirm broker availability"},
            {"lane_id": "aggregate_bonds", "candidate_tickers": ["EUNA"], "status": "operationally_mature_not_funded", "next_confirmation_nl": "Bevestig brokerbeschikbaarheid", "next_confirmation_en": "Confirm broker availability"},
        ],
        "verification_funnel": {"funded_positions": 1},
        "next_run_input": {"required_actions": ["verify broker availability"], "priority_candidates": []},
        "risks": [{"invalidation_nl": "Geen financiering vóór identiteit, KID, handelslijn en brokerbeschikbaarheid zijn bevestigd.", "invalidation_en": "No funding before identity, KID, trading line and broker availability are confirmed."}],
        "macro": {"portfolio_implications": ["Retain cash until the selected UCITS trading line, broker availability and current pricing are jointly verified."]},
        "authority": {"canonical_identity": "isin_first", "us_etfs_research_only": True, "valuation_grade": False, "funding_authority": False, "portfolio_mutation": False, "production_delivery_authority": False},
    }
    reconciled = funded_overlay(state)
    assert funded_state_blockers(reconciled) == []
    assert reconciled["funded_consistency"]["position_count"] == 3
    assert reconciled["funded_consistency"]["funded_tickers"] == ["VWCE", "EUNA", "SXR8"]
    assert all(lane["status"] == "funded_model_position_active" for lane in reconciled["opportunity_radar"])
    serialized = json.dumps(reconciled, ensure_ascii=False).casefold()
    assert "brokerbeschikbaarheid" not in serialized
    assert "broker availability" not in serialized

    base_nl = "Cash behouden. Deze week: geen portefeuilletransactie; de EU-modelportefeuille blijft volledig in cash. <p>Position analysis active.</p>"
    rendered_nl = patch_copy(base_nl, reconciled, "nl")
    assert "3 modelposities actief" in rendered_nl
    assert "151 VWCE" in rendered_nl and "1.526 EUNA" in rendered_nl
    assert "SXR8 aangehouden" in rendered_nl
    assert "<td>SXR8</td>" in rendered_nl and "<td>10</td>" in rendered_nl
    assert "Eerste modelpositie actief" not in rendered_nl
    assert "Peildatum" in rendered_nl


def test_isin_surface_uses_canonical_identity_not_raw_token_count() -> None:
    state = {
        "portfolio": {
            "positions": [
                {"isin": "IE00BK5BQT80"},
                {"isin": "IE00BDBRDM35"},
                {"isin": "IE00B5BMR087"},
            ]
        },
        "pricing": {
            "rows": [
                {"isin": "IE00BK5BQT80"},
                {"isin": "IE00BDBRDM35"},
                {"isin": "IE00B5BMR087"},
                {"isin": "IE00BMC38736"},
            ]
        },
    }
    html_text = "<th>ISIN</th> IE00BK5BQT80 IE00BDBRDM35 IE00B5BMR087 IE00BMC38736"
    extracted = "ISIN\nIE00BK5BQT80\nIE00BDBRDM35\nIE00B5BMR087"
    assert (html_text + extracted).upper().count("ISIN") < 8
    evidence = isin_surface_evidence(state, html_text, extracted)
    assert evidence["passed"] is True
    assert evidence["missing_html_isins"] == []
    assert evidence["missing_pdf_funded_isins"] == []

    missing = isin_surface_evidence(state, html_text.replace("IE00BDBRDM35", ""), extracted)
    assert missing["passed"] is False
    assert missing["missing_html_isins"] == ["IE00BDBRDM35"]


def test_funded_identity_strip_is_visible_bilingual_idempotent_and_print_safe() -> None:
    rows = (
        "<tr><td>VWCE</td><td>Vanguard</td><td>IE00BK5BQT80</td><td>151</td><td>€ 165,32</td><td>2026-07-16</td><td>€ 24.963,32</td><td>24,96%</td><td>25,00%</td><td>Modelpositie · geen brokerorder</td></tr>"
        "<tr><td>EUNA</td><td>iShares Bonds</td><td>IE00BDBRDM35</td><td>1.526</td><td>€ 4,91</td><td>2026-07-14</td><td>€ 7.497,24</td><td>7,50%</td><td>7,50%</td><td>Modelpositie · geen brokerorder</td></tr>"
        "<tr><td>SXR8</td><td>iShares S&P 500</td><td>IE00B5BMR087</td><td>10</td><td>€ 711,66</td><td>2026-07-16</td><td>€ 7.116,60</td><td>7,12%</td><td>7,50%</td><td>Modelpositie · geen brokerorder</td></tr>"
    )
    history = "Three-position funded-aware non-delivery preview"
    nl = f'<html><head></head><body>{history}<section><span>Review huidige posities</span><div class="note-box">Model</div><table class="data-table">{rows}</table></section></body></html>'
    en = f'<html><head></head><body>{history}<section><span>Current-position review</span><div class="note-box">Model</div><table class="data-table">{rows}</table></section></body></html>'

    polished_nl = inject_funded_identity_strip(nl, language="nl")
    polished_en = inject_funded_identity_strip(en, language="en")
    for output in [polished_nl, polished_en]:
        assert output.count('class="funded-identity-strip"') == 1
        assert 'class="data-table funded-position-table"' in output
        assert ".funded-position-table" in output and ".pricing-table" in output
        assert "VWCE" in output and "IE00BK5BQT80" in output
        assert "EUNA" in output and "IE00BDBRDM35" in output
        assert "SXR8" in output and "IE00B5BMR087" in output
    assert "Gefinancierde ISIN-identiteiten" in polished_nl
    assert "Funded ISIN identities" in polished_en
    assert "Preview zonder levering met drie gefinancierde posities" in polished_nl
    assert history not in polished_nl and history in polished_en
    assert "Model · geen brokerorder" in polished_nl
    assert inject_funded_identity_strip(polished_nl, language="nl") == polished_nl


def test_equity_curve_suppresses_colliding_date_ticks_but_keeps_endpoints() -> None:
    state = {
        "equity_curve": {
            "show_chart": True,
            "latest_nav_matches_state": True,
            "points": [
                {"date": "2026-05-30", "nav_eur": 100000.0},
                {"date": "2026-07-16", "nav_eur": 100016.6},
                {"date": "2026-07-17", "nav_eur": 100016.6},
            ],
        }
    }
    nl_svg = render_equity_curve_svg(state, language="nl")
    en_svg = render_equity_curve_svg(state, language="en")
    assert "30-05-2026" in nl_svg and "17-07-2026" in nl_svg
    assert "16-07-2026" not in nl_svg
    assert "2026-05-30" in en_svg and "2026-07-17" in en_svg
    assert "2026-07-16" not in en_svg
    assert 'text-anchor="start"' in nl_svg and 'text-anchor="end"' in nl_svg
