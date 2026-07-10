from pathlib import Path


CONTRACT = Path("control/ETF_EU_FRESH_GENERATION_DRY_RUN_CONTRACT_V1.md")


def test_fresh_generation_contract_exists_and_references_upstream_first_reuse():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "ETF_EU_FRESH_GENERATION_DRY_RUN_CONTRACT_V1" in text
    assert "upstream_pattern_adapted=weekly-etf fresh-generation/runtime/report-manifest concept" in text
    assert "source_of_truth_repo=market-predictions/weekly-etf-eu" in text
    assert "reference_architecture_repo=market-predictions/weekly-etf" in text


def test_fresh_generation_contract_preserves_no_delivery_authority():
    text = CONTRACT.read_text(encoding="utf-8")
    for token in [
        "send_executed=false",
        "transport_attempted=false",
        "receipt_confirmed=false",
        "valuation_grade=false",
        "funding_authority=false",
        "portfolio_mutation=false",
        "production_delivery_authority=false",
    ]:
        assert token in text


def test_fresh_generation_contract_rejects_us_authority_inputs():
    text = CONTRACT.read_text(encoding="utf-8")
    for token in [
        "output/etf_portfolio_state.json",
        "output/etf_valuation_history.csv",
        "output/etf_trade_ledger.csv",
        "output/etf_recommendation_scorecard.csv",
        "weekly_analysis_pro_*.md as EU source truth",
    ]:
        assert token in text
