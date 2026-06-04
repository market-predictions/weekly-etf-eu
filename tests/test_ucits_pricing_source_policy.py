from pathlib import Path

import yaml


def test_twelve_data_policy_defaults_stay_off():
    policy = yaml.safe_load(Path("config/ucits_pricing_source_policy.yml").read_text()) or {}

    assert policy["rules"]["twelve_data_default_accept_as_valuation_grade"] is False
    hierarchy = {row["source_id"]: row for row in policy["source_authority_hierarchy"]}
    assert hierarchy["twelve_data"]["valuation_grade_eligible"] is False


def test_twelve_data_line_entries_are_explicit():
    policy = yaml.safe_load(Path("config/ucits_pricing_source_policy.yml").read_text()) or {}
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
