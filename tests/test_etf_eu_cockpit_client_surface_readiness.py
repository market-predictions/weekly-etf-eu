from __future__ import annotations

import json
from pathlib import Path

from tools.validate_etf_eu_cockpit_client_surface_readiness import validate_client_surface_readiness

ARTIFACT = Path("output/client_surface/etf_eu_cockpit_client_surface_readiness_20260618_000000.json")
READY = "ready_for_client_surface_review"


def _payload() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _pricing_payload() -> dict:
    return json.loads(Path(_payload()["source_pricing_line_expansion_manifest_path"]).read_text(encoding="utf-8"))


def _candidate(candidate_id: str) -> dict:
    for candidate in _pricing_payload()["candidate_pricing_evidence"]:
        if candidate["candidate_id"] == candidate_id or candidate["isin"] == candidate_id:
            return candidate
    raise AssertionError(f"candidate not found: {candidate_id}")


def _main_body(text: str) -> str:
    for marker in ["## Appendix", "## Bijlage"]:
        if marker in text:
            return text.split(marker, 1)[0]
    return text


def test_readiness_artifact_passes_validator() -> None:
    result = validate_client_surface_readiness(ARTIFACT)
    assert result["status"] == "valid"
    assert result["overall_readiness_status"] == READY
    assert result["selected_next_package"] == "WP14T"


def test_readiness_notes_and_source_paths_exist() -> None:
    payload = _payload()
    for key in [
        "readiness_notes_path",
        "source_pricing_integration_manifest_path",
        "source_pricing_line_expansion_manifest_path",
        "source_english_pricing_integrated_cockpit_markdown_path",
        "source_dutch_pricing_integrated_cockpit_markdown_path",
        "source_english_pricing_integrated_cockpit_html_path",
        "source_dutch_pricing_integrated_cockpit_html_path",
        "authorization_decision_artifact_path",
    ]:
        assert Path(payload[key]).exists()


def test_overall_readiness_status_and_dimensions_are_ready() -> None:
    payload = _payload()
    assert payload["overall_readiness_status"] == READY
    for dimension in payload["readiness_dimensions"].values():
        assert dimension["status"] == READY
        assert dimension["evidence"]


def test_visible_candidate_count_is_four() -> None:
    assert _payload()["visible_candidate_count"] == 4


def test_cspx_sxr8_and_core_candidate_remain_review_only() -> None:
    candidate = _candidate("IE00B5BMR087")
    combined = json.dumps(candidate)
    assert "CSPX.L" in combined
    assert "SXR8.DE" in combined
    assert candidate["pricing_evidence_status"] == "usable_for_review_only"
    assert candidate["safe_for_valuation_grade"] is False


def test_semiconductor_smh_remains_ambiguous_or_unsafe() -> None:
    candidate = _candidate("IE00BMC38736")
    assert candidate["pricing_line_status"] in {"pricing_symbol_ambiguous", "pricing_symbol_pending"}
    assert candidate["safe_for_cockpit_pricing_evidence"] is False
    assert candidate["safe_for_valuation_grade"] is False
    assert "SMH" in json.dumps(candidate)


def test_gold_etc_and_infrastructure_remain_blocked_or_incomplete() -> None:
    gold = _candidate("TBD-3-iShares Physical Gold ETC")
    infrastructure = _candidate("TBD-4-iShares Global Infrastructure UCITS ETF")
    assert gold["pricing_line_status"] == "policy_blocked"
    assert infrastructure["pricing_line_status"] == "identity_incomplete"
    assert gold["safe_for_candidate_promotion"] is False
    assert infrastructure["safe_for_candidate_promotion"] is False


def test_research_proxies_remain_proxies_only() -> None:
    combined = json.dumps(_pricing_payload())
    for proxy in ["SPY", "SMH", "GLD", "PAVE"]:
        assert proxy in combined
    for candidate in _pricing_payload()["candidate_pricing_evidence"]:
        for proxy in candidate["research_proxies"]:
            assert proxy["purpose"] == "benchmark_reference_only"
            assert proxy["proxy_must_not_be_pricing_line"] is True
            assert proxy["proxy_must_not_be_funded"] is True


def test_authority_flags_remain_false_or_blocked() -> None:
    payload = _payload()
    assert payload["delivery_authorization_decision"] == "remain_blocked"
    for key in ["production_delivery", "portfolio_mutation", "candidate_promotion", "funding_authority", "valuation_grade"]:
        assert payload[key] is False


def test_readiness_does_not_create_delivery_funding_valuation_promotion_or_portfolio_mutation() -> None:
    combined = json.dumps(_payload()).lower()
    for forbidden in [
        "delivery authorization granted",
        "production_delivery=true",
        "portfolio_mutation=true",
        "candidate_promotion=true",
        "funding_authority=true",
        "valuation_grade=true",
        "buy signal",
        "fund decision",
    ]:
        assert forbidden not in combined


def test_debug_like_terms_are_absent_from_main_body() -> None:
    payload = _payload()
    for key in ["source_english_pricing_integrated_cockpit_markdown_path", "source_dutch_pricing_integrated_cockpit_markdown_path"]:
        main = _main_body(Path(payload[key]).read_text(encoding="utf-8"))
        for term in ["tests/test_", "tools/validate_", "schema_version", "selected_next_package", "artifact="]:
            assert term not in main


def test_selected_next_package_recorded() -> None:
    assert _payload()["selected_next_package"] == "WP14T"
