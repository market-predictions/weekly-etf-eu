from pathlib import Path

import yaml


POLICY_PATH = Path("config/ucits_pricing_source_policy.yml")


def _load_policy() -> dict:
    return yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8")) or {}


def _iter_sources(policy: dict):
    for source in policy.get("source_authority_hierarchy") or []:
        yield source
    for line in policy.get("trading_line_policies") or []:
        for source in line.get("source_order") or []:
            yield source


def test_twelve_data_policy_defaults_stay_off():
    policy = _load_policy()

    assert policy["rules"]["twelve_data_default_accept_as_valuation_grade"] is False
    hierarchy = {row["source_id"]: row for row in policy["source_authority_hierarchy"]}
    assert hierarchy["twelve_data"]["valuation_grade_eligible"] is False


def test_twelve_data_line_entries_are_explicit():
    policy = _load_policy()
    rows = []
    for line in policy["trading_line_policies"]:
        rows += [source for source in line["source_order"] if source.get("source_id") == "twelve_data"]

    assert rows
    for row in rows:
        assert row["symbol"]
        assert row["exchange"]
        assert row["expected_currency"]
        assert row["accept_as_valuation_grade"] is False
        assert row["valuation_grade_eligible"] is False


def test_yahoo_policy_remains_connectivity_display_only():
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
        assert source.get("status", "temporary_connectivity_display_fallback") == "temporary_connectivity_display_fallback"
