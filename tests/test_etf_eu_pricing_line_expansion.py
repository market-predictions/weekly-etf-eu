from __future__ import annotations

import json
from pathlib import Path

from tools.validate_etf_eu_pricing_line_expansion import validate_pricing_line_expansion

MANIFEST = Path("output/pricing/etf_eu_pricing_line_expansion_20260618_000000.json")


def _payload() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _candidate(candidate_id: str) -> dict:
    for candidate in _payload()["candidate_pricing_evidence"]:
        if candidate["candidate_id"] == candidate_id or candidate["isin"] == candidate_id:
            return candidate
    raise AssertionError(f"candidate not found: {candidate_id}")


def _symbols(candidate: dict) -> set[str]:
    found: set[str] = set()
    for line in candidate["trading_lines"]:
        found.add(line.get("pricing_symbol_yahoo", ""))
        found.add(line.get("exchange_ticker", ""))
    return found


def _proxies(candidate: dict) -> set[str]:
    return {proxy["us_proxy"] for proxy in candidate["research_proxies"]}


def test_pricing_expansion_manifest_passes_validator() -> None:
    result = validate_pricing_line_expansion(MANIFEST)
    assert result["status"] == "valid"
    assert result["selected_next_package"] == "WP14R"
    assert result["visible_candidate_count"] == "4"


def test_notes_file_and_source_paths_exist() -> None:
    payload = _payload()
    for key in [
        "notes_path",
        "source_enriched_cockpit_render_manifest_path",
        "source_universe_enrichment_manifest_path",
        "source_symbol_registry_path",
        "source_proxy_map_path",
        "authorization_decision_artifact_path",
    ]:
        assert Path(payload[key]).exists()


def test_candidate_pricing_evidence_has_four_entries() -> None:
    payload = _payload()
    assert payload["visible_candidate_count"] == 4
    assert len(payload["candidate_pricing_evidence"]) == 4


def test_core_sp500_candidate_preserves_cspx_and_sxr8_review_only() -> None:
    candidate = _candidate("IE00B5BMR087")
    assert {"CSPX.L", "SXR8.DE"} <= _symbols(candidate)
    assert candidate["pricing_line_status"] == "source_evidence_available"
    assert candidate["pricing_evidence_status"] == "usable_for_review_only"
    assert candidate["safe_for_cockpit_pricing_evidence"] is True
    assert candidate["safe_for_valuation_grade"] is False


def test_semiconductor_candidate_remains_ambiguous_and_unsafe() -> None:
    candidate = _candidate("IE00BMC38736")
    assert candidate["cockpit_status"] == "pricing_incomplete"
    assert candidate["pricing_line_status"] in {"pricing_symbol_ambiguous", "pricing_symbol_pending"}
    assert candidate["safe_for_cockpit_pricing_evidence"] is False
    assert "SMH" in _proxies(candidate)
    assert "exchange-specific" in candidate["next_pricing_action"]


def test_smh_is_not_treated_as_safe_ucits_pricing_evidence() -> None:
    candidate = _candidate("IE00BMC38736")
    for line in candidate["trading_lines"]:
        if line.get("exchange_ticker") == "SMH":
            assert line["safe_for_cockpit_pricing_evidence"] is False
            assert "U.S. ETF ticker" in line["ambiguity_reason"]


def test_gold_etc_remains_policy_blocked() -> None:
    candidate = _candidate("TBD-3-iShares Physical Gold ETC")
    assert candidate["fund_name"] == "iShares Physical Gold ETC"
    assert candidate["cockpit_status"] == "blocked_until_verified"
    assert candidate["pricing_line_status"] in {"policy_blocked", "pricing_symbol_pending"}
    assert candidate["safe_for_cockpit_pricing_evidence"] is False
    assert "GLD" in _proxies(candidate)
    assert "ETC policy" in candidate["next_pricing_action"]


def test_infrastructure_remains_identity_incomplete() -> None:
    candidate = _candidate("TBD-4-iShares Global Infrastructure UCITS ETF")
    assert candidate["fund_name"] == "iShares Global Infrastructure UCITS ETF"
    assert candidate["cockpit_status"] == "identity_incomplete"
    assert candidate["pricing_line_status"] in {"identity_incomplete", "pricing_symbol_pending"}
    assert candidate["safe_for_cockpit_pricing_evidence"] is False
    assert "PAVE" in _proxies(candidate)
    assert "ISIN" in candidate["next_pricing_action"]
    assert "issuer" in candidate["next_pricing_action"]


def test_research_proxies_remain_proxies_only() -> None:
    combined = json.dumps(_payload()["candidate_pricing_evidence"])
    for proxy in ["SPY", "SMH", "GLD", "PAVE"]:
        assert proxy in combined
    for candidate in _payload()["candidate_pricing_evidence"]:
        for proxy in candidate["research_proxies"]:
            assert proxy["purpose"] == "benchmark_reference_only"
            assert proxy["proxy_must_not_be_pricing_line"] is True
            assert proxy["proxy_must_not_be_funded"] is True


def test_all_candidates_block_valuation_funding_and_promotion() -> None:
    for candidate in _payload()["candidate_pricing_evidence"]:
        assert candidate["safe_for_valuation_grade"] is False
        assert candidate["safe_for_funding_decision"] is False
        assert candidate["safe_for_candidate_promotion"] is False


def test_delivery_and_portfolio_authority_remain_blocked() -> None:
    payload = _payload()
    assert payload["delivery_authorization_decision"] == "remain_blocked"
    assert payload["production_delivery"] is False
    assert payload["portfolio_mutation"] is False
    assert payload["candidate_promotion"] is False
    assert payload["funding_authority"] is False
    assert payload["valuation_grade"] is False


def test_pricing_evidence_cannot_be_interpreted_as_buy_or_fund_signal() -> None:
    forbidden = ["buy", "funding signal", "fundable", "portfolio_holding", "valuation_grade=true"]
    combined = json.dumps(_payload()).lower()
    for term in forbidden:
        assert term not in combined


def test_selected_next_package_is_recorded() -> None:
    payload = _payload()
    assert payload["selected_next_package"] == "WP14R"
