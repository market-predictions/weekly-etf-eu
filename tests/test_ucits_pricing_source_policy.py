from pathlib import Path

import yaml


POLICY_PATH = Path("config/ucits_pricing_source_policy.yml")


def _load_policy() -> dict:
    return yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))


def _iter_sources(policy: dict):
    for source in policy.get("source_authority_hierarchy") or []:
        yield source
    for line in policy.get("trading_line_policies") or []:
        for source in line.get("source_order") or []:
            yield source


def test_yahoo_policy_is_connectivity_display_only_not_valuation_authority():
    policy = _load_policy()
    rules = policy["rules"]

    assert policy["pricing_authority_mode"] == "valuation_grade_pending"
    assert rules["yfinance_default_authority"] == "non_authoritative_connectivity_only"
    assert rules["yahoo_counts_for_market_close_agreement"] is False
    assert rules["yahoo_display_or_connectivity_only"] is True

    yahoo_sources = [source for source in _iter_sources(policy) if source.get("source_id") == "yahoo_yfinance"]
    assert yahoo_sources

    for source in yahoo_sources:
        assert source["authority"] == "non_authoritative_connectivity_only"
        assert source["valuation_grade_eligible"] is False
        assert source.get("accept_as_valuation_grade", False) is False
        assert source["counts_for_market_close_agreement"] is False


def test_no_trading_line_accepts_yahoo_as_agreement_gate_valuation_grade():
    policy = _load_policy()

    for line in policy.get("trading_line_policies") or []:
        yahoo = [source for source in line.get("source_order") or [] if source.get("source_id") == "yahoo_yfinance"]
        for source in yahoo:
            assert source["status"] == "temporary_connectivity_display_fallback"
            assert "not agreement-gate valuation authority" in source["notes"]
