from pathlib import Path

import pytest

from tools.validate_ucits_fundability_promotion_contract import validate_registry


def write_registry(path: Path, fundable_status: str = "not_funded_requires_broker_and_pricing_line_confirmation", investability_status: str = "verified_candidate_not_funded") -> None:
    path.write_text(
        f"""
schema_version: ucits_symbol_registry_v1
funds:
  - registry_id: core_us_equity_cspx
    us_research_proxy: SPY
    isin: IE00B5BMR087
    fund_name: iShares Core S&P 500 UCITS ETF USD (Acc)
    provider: iShares / BlackRock
    instrument_type: ETF
    ucits_status: confirmed
    priips_kid_status: available
    investability_status: {investability_status}
    fundable_status: {fundable_status}
    trading_lines:
      - exchange: Xetra
        exchange_ticker: SXR8
        trading_currency: EUR
        pricing_symbol_yahoo: SXR8.DE
""",
        encoding="utf-8",
    )


def test_bootstrap_candidate_not_funded_passes(tmp_path: Path):
    registry = tmp_path / "registry.yml"
    write_registry(registry)

    validate_registry(registry)


def test_fundable_candidate_without_separate_decision_fails(tmp_path: Path):
    registry = tmp_path / "registry.yml"
    write_registry(registry, fundable_status="fundable", investability_status="fundable")

    with pytest.raises(RuntimeError, match="current_bootstrap_registry_must_not_have_fundable_candidates"):
        validate_registry(registry)


def test_verified_candidate_not_funded_cannot_auto_promote(tmp_path: Path):
    registry = tmp_path / "registry.yml"
    write_registry(registry, fundable_status="fundable", investability_status="verified_candidate_not_funded")

    with pytest.raises(RuntimeError, match="verified_candidate_not_funded_must_not_be_auto_promoted"):
        validate_registry(registry)
