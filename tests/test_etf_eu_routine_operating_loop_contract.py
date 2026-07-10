from pathlib import Path


def test_routine_operating_loop_contract_exists_and_mentions_upstream_first():
    path = Path("control/ETF_EU_ROUTINE_WEEKLY_OPERATING_LOOP_V1.md")
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "upstream_pattern_adapted=weekly-etf routine workflow and run-manifest pattern" in text
    assert "source_of_truth_repo=market-predictions/weekly-etf-eu" in text
    assert "reference_architecture_repo=market-predictions/weekly-etf" in text


def test_routine_contract_keeps_four_layers_separate():
    text = Path("control/ETF_EU_ROUTINE_WEEKLY_OPERATING_LOOP_V1.md").read_text(encoding="utf-8")
    assert "### 1. Decision framework" in text
    assert "### 2. Input/state contract" in text
    assert "### 3. Output contract" in text
    assert "### 4. Operational runbook" in text


def test_routine_contract_blocks_us_state_and_authority_promotion():
    text = Path("control/ETF_EU_ROUTINE_WEEKLY_OPERATING_LOOP_V1.md").read_text(encoding="utf-8")
    assert "u_s_portfolio_state_authority=false" in text
    assert "valuation_grade=false" in text
    assert "funding_authority=false" in text
    assert "portfolio_mutation=false" in text
    assert "production_delivery_authority=false" in text
