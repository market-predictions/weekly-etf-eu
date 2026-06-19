from __future__ import annotations

import json
from pathlib import Path

from tools.validate_etf_eu_cockpit_poc_package import validate_cockpit_poc_package

ARTIFACT = Path("output/client_surface/etf_eu_cockpit_poc_package_20260618_000000.json")
READY = "ready_for_client_surface_review"


def _payload() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_package_manifest_passes_validator() -> None:
    result = validate_cockpit_poc_package(ARTIFACT)
    assert result["status"] == "valid"
    assert result["selected_next_package"] == "WP14U"


def test_package_index_exists() -> None:
    assert Path(_payload()["recommended_first_review_file"]).exists()


def test_all_client_facing_review_files_exist() -> None:
    for path in _payload()["client_facing_review_files"]:
        assert Path(path).exists()


def test_all_supporting_manifest_files_exist() -> None:
    for path in _payload()["supporting_manifest_files"]:
        assert Path(path).exists()


def test_all_validator_and_test_files_exist() -> None:
    payload = _payload()
    for key in ["validator_files", "test_files"]:
        for path in payload[key]:
            assert Path(path).exists()


def test_package_flags_are_true() -> None:
    payload = _payload()
    for key in [
        "package_created",
        "proof_of_concept_package_created",
        "client_surface_package_index_created",
        "readiness_gate_preserved",
        "pricing_integration_preserved",
        "pricing_line_evidence_preserved",
        "authority_boundary_preserved",
        "proxy_separation_preserved",
        "debug_surface_hygiene_preserved",
    ]:
        assert payload[key] is True


def test_readiness_and_candidate_count_preserved() -> None:
    payload = _payload()
    assert payload["overall_readiness_status"] == READY
    assert payload["visible_candidate_count"] == 4


def test_pricing_baseline_preserved() -> None:
    baseline = _payload()["current_pricing_baseline"]
    assert baseline["isin"] == "IE00B5BMR087"
    assert baseline["pricing_evidence_status"] == "usable_for_review_only"
    assert baseline["review_only"] is True
    assert "CSPX.L" in baseline["pricing_symbols"]
    assert "SXR8.DE" in baseline["pricing_symbols"]


def test_blocked_or_incomplete_lanes_preserved() -> None:
    lanes = {lane["fund_name"]: lane for lane in _payload()["blocked_or_incomplete_lanes"]}
    assert lanes["VanEck Semiconductor UCITS ETF"]["status"] == "pricing_symbol_ambiguous"
    assert lanes["iShares Physical Gold ETC"]["status"] == "policy_blocked"
    assert lanes["iShares Global Infrastructure UCITS ETF"]["status"] == "identity_incomplete"


def test_research_proxy_map_preserved() -> None:
    proxy_map = _payload()["research_proxy_map"]
    assert proxy_map["SPY"] == "research_proxy_only"
    assert proxy_map["SMH"] == "research_proxy_only_and_ambiguous_as_pricing_symbol"
    assert proxy_map["GLD"] == "research_proxy_only_not_eu_holding"
    assert proxy_map["PAVE"] == "research_proxy_only_not_eu_holding"


def test_authority_flags_remain_false_or_blocked() -> None:
    payload = _payload()
    assert payload["delivery_authorization_decision"] == "remain_blocked"
    for key in ["production_delivery", "portfolio_mutation", "candidate_promotion", "funding_authority", "valuation_grade"]:
        assert payload[key] is False


def test_selected_next_package_is_wp14u() -> None:
    assert _payload()["selected_next_package"] == "WP14U"
