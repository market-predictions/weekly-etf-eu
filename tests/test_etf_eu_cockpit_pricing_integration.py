from __future__ import annotations

import json
from pathlib import Path

from tools.validate_etf_eu_cockpit_pricing_integration import validate_cockpit_pricing_integration

MANIFEST = Path("output/client_surface/etf_eu_cockpit_pricing_integration_20260618_000000.json")


def _payload() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


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


def test_pricing_integration_manifest_passes_validator() -> None:
    result = validate_cockpit_pricing_integration(MANIFEST)
    assert result["status"] == "valid"
    assert result["selected_next_package"] == "WP14S"
    assert result["visible_candidate_count"] == "4"


def test_all_source_and_output_paths_exist() -> None:
    payload = _payload()
    for key in [
        "source_enriched_cockpit_render_manifest_path",
        "source_universe_enrichment_manifest_path",
        "source_pricing_line_expansion_manifest_path",
        "source_pricing_line_expansion_notes_path",
        "authorization_decision_artifact_path",
        "english_pricing_integrated_cockpit_markdown_path",
        "dutch_pricing_integrated_cockpit_markdown_path",
        "english_pricing_integrated_cockpit_html_path",
        "dutch_pricing_integrated_cockpit_html_path",
    ]:
        assert Path(payload[key]).exists()


def test_required_sections_exist_in_english_markdown() -> None:
    text = Path(_payload()["english_pricing_integrated_cockpit_markdown_path"]).read_text(encoding="utf-8")
    for section in [
        "## Cockpit summary",
        "## Pricing evidence at a glance",
        "## Visible UCITS universe",
        "## Pricing-line evidence map",
        "## Unsafe or blocked pricing lines",
        "## Proxy separation map",
        "## Reader action map",
        "## Current blockers",
    ]:
        assert section in text


def test_required_sections_exist_in_dutch_markdown() -> None:
    text = Path(_payload()["dutch_pricing_integrated_cockpit_markdown_path"]).read_text(encoding="utf-8")
    for section in [
        "## Cockpitsamenvatting",
        "## Prijsbewijs in één oogopslag",
        "## Zichtbaar UCITS-universum",
        "## Prijsregel-bewijskaart",
        "## Onveilige of geblokkeerde prijsregels",
        "## Scheiding met researchproxy",
        "## Actiekaart voor de lezer",
        "## Huidige blokkades",
    ]:
        assert section in text


def test_visible_candidate_count_and_status_summary_preserved() -> None:
    payload = _payload()
    assert payload["visible_candidate_count"] == 4
    assert payload["pricing_line_status_summary"] == {
        "source_evidence_available": 1,
        "pricing_symbol_ambiguous": 1,
        "policy_blocked": 1,
        "identity_incomplete": 1,
    }


def test_cspx_and_sxr8_remain_review_only_baseline() -> None:
    candidate = _candidate("IE00B5BMR087")
    text = json.dumps(candidate)
    assert "CSPX.L" in text
    assert "SXR8.DE" in text
    assert candidate["pricing_evidence_status"] == "usable_for_review_only"
    assert candidate["safe_for_cockpit_pricing_evidence"] is True
    assert candidate["safe_for_valuation_grade"] is False


def test_semiconductor_smh_remains_ambiguous_and_unsafe() -> None:
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


def test_unsafe_pricing_symbols_are_rendered() -> None:
    payload = _payload()
    unsafe = json.dumps(payload["unsafe_pricing_symbols"])
    for symbol in ["SMH", "GLD", "PAVE"]:
        assert symbol in unsafe


def test_all_candidates_block_valuation_funding_and_promotion() -> None:
    for candidate in _pricing_payload()["candidate_pricing_evidence"]:
        assert candidate["safe_for_valuation_grade"] is False
        assert candidate["safe_for_funding_decision"] is False
        assert candidate["safe_for_candidate_promotion"] is False


def test_delivery_and_portfolio_flags_remain_blocked() -> None:
    payload = _payload()
    assert payload["delivery_authorization_decision"] == "remain_blocked"
    assert payload["production_delivery"] is False
    assert payload["portfolio_mutation"] is False
    assert payload["candidate_promotion"] is False
    assert payload["funding_authority"] is False
    assert payload["valuation_grade"] is False


def test_debug_like_terms_absent_from_main_body() -> None:
    payload = _payload()
    for key in ["english_pricing_integrated_cockpit_markdown_path", "dutch_pricing_integrated_cockpit_markdown_path"]:
        main = _main_body(Path(payload[key]).read_text(encoding="utf-8"))
        for term in ["tests/test_", "tools/validate_", "schema_version", "selected_next_package", "artifact="]:
            assert term not in main


def test_generated_html_has_no_external_assets_or_scripts() -> None:
    payload = _payload()
    for key in ["english_pricing_integrated_cockpit_html_path", "dutch_pricing_integrated_cockpit_html_path"]:
        text = Path(payload[key]).read_text(encoding="utf-8").lower()
        assert "<script" not in text
        assert "href=" not in text
        assert "src=" not in text


def test_selected_next_package_recorded() -> None:
    assert _payload()["selected_next_package"] == "WP14S"
