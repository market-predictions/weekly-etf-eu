from __future__ import annotations

import csv
import json
from pathlib import Path

from runtime.apply_etf_eu_guarded_capital_activation import apply
from runtime.build_etf_eu_allocation_decision import build_decision
from tools.validate_etf_eu_allocation_decision import validate

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
