from __future__ import annotations

import json
from pathlib import Path

from tools.validate_etf_eu_cockpit_poc_coordinator_closeout import validate_coordinator_closeout

ARTIFACT = Path("output/client_surface/etf_eu_cockpit_poc_coordinator_closeout_20260618_000000.json")
READY = "ready_for_client_surface_review"
COORDINATOR_READY = "ready_for_coordinator_review"


def _payload() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_closeout_artifact_passes_validator() -> None:
    result = validate_coordinator_closeout(ARTIFACT)
    assert result["status"] == "valid"
    assert result["selected_next_package"] == "WP14V"


def test_closeout_checklist_exists() -> None:
    assert Path("output/client_surface/etf_eu_cockpit_poc_coordinator_closeout_checklist_20260618_000000.md").exists()


def test_all_review_files_exist() -> None:
    for path in _payload()["review_files"]:
        assert Path(path).exists()


def test_all_supporting_manifest_files_exist() -> None:
    for path in _payload()["supporting_manifest_files"]:
        assert Path(path).exists()


def test_acceptance_checklist_entries_are_true() -> None:
    checklist = _payload()["acceptance_checklist"]
    assert checklist
    for value in checklist.values():
        assert value is True


def test_coordinator_review_status() -> None:
    payload = _payload()
    assert payload["coordinator_review_status"] == COORDINATOR_READY
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


def test_selected_next_package_is_wp14v() -> None:
    assert _payload()["selected_next_package"] == "WP14V"
