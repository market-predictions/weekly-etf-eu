from __future__ import annotations

import json
from pathlib import Path

from tools.validate_etf_eu_cockpit_universe_enrichment import validate_cockpit_universe_enrichment

MANIFEST = Path("output/client_surface/etf_eu_cockpit_universe_enrichment_20260618_000000.json")


def _payload() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _main_body(text: str) -> str:
    for marker in ["## Appendix", "## Bijlage"]:
        if marker in text:
            return text.split(marker, 1)[0]
    return text


def test_valid_enrichment_manifest_passes() -> None:
    result = validate_cockpit_universe_enrichment(MANIFEST)
    assert result["status"] == "valid"
    assert result["selected_next_package"] == "WP14P"
    assert result["visible_candidate_count"] == "4"


def test_enriched_cockpit_files_exist() -> None:
    payload = _payload()
    for key in [
        "english_enriched_cockpit_markdown_path",
        "dutch_enriched_cockpit_markdown_path",
        "english_enriched_cockpit_html_path",
        "dutch_enriched_cockpit_html_path",
    ]:
        assert Path(payload[key]).exists()


def test_enriched_cockpit_summary_exists() -> None:
    payload = _payload()
    text = Path(payload["english_enriched_cockpit_markdown_path"]).read_text(encoding="utf-8")
    assert "## Cockpit summary" in text
    assert "UCITS universe status" in text
    assert "Main evidence gaps" in text


def test_at_a_glance_cards_exist() -> None:
    payload = _payload()
    text = Path(payload["english_enriched_cockpit_markdown_path"]).read_text(encoding="utf-8")
    assert "## At-a-glance cards" in text
    for term in ["UCITS universe", "Identity evidence", "Pricing evidence", "Proxy separation", "Delivery status", "Portfolio authority"]:
        assert term in text


def test_visible_ucits_universe_and_candidate_evidence_map_exist() -> None:
    payload = _payload()
    text = Path(payload["english_enriched_cockpit_markdown_path"]).read_text(encoding="utf-8")
    assert "## Visible UCITS universe" in text
    assert "## Candidate evidence map" in text
    assert payload["visible_candidate_count"] >= 2


def test_proxy_reader_and_blocker_panels_exist() -> None:
    payload = _payload()
    text = Path(payload["english_enriched_cockpit_markdown_path"]).read_text(encoding="utf-8")
    assert "## Proxy separation map" in text
    assert "## Reader action map" in text
    assert "## Current blockers" in text
    assert "remain_blocked" in text


def test_ucits_identity_pricing_and_proxy_terms_are_preserved() -> None:
    payload = _payload()
    combined = (
        Path(payload["english_enriched_cockpit_markdown_path"]).read_text(encoding="utf-8")
        + Path(payload["dutch_enriched_cockpit_markdown_path"]).read_text(encoding="utf-8")
        + json.dumps(payload["visible_candidates"])
    )
    for term in ["UCITS", "IE00B5BMR087", "CSPX.L", "SXR8.DE", "SPY"]:
        assert term in combined


def test_spy_proxy_separation_is_preserved() -> None:
    payload = _payload()
    text = Path(payload["english_enriched_cockpit_markdown_path"]).read_text(encoding="utf-8")
    assert "| SPY | IE00B5BMR087 through CSPX.L and SXR8.DE |" in text
    assert "EU holding or funding source" in text


def test_delivery_authorization_remains_blocked() -> None:
    payload = _payload()
    assert payload["delivery_authorization_decision"] == "remain_blocked"


def test_authority_flags_remain_false() -> None:
    payload = _payload()
    for key in [
        "production_delivery",
        "portfolio_mutation",
        "candidate_promotion",
        "funding_authority",
        "valuation_grade",
    ]:
        assert payload[key] is False


def test_debug_like_terms_are_absent_from_main_cockpit_body() -> None:
    payload = _payload()
    for key in ["english_enriched_cockpit_markdown_path", "dutch_enriched_cockpit_markdown_path"]:
        main = _main_body(Path(payload[key]).read_text(encoding="utf-8"))
        for term in ["tests/test_", "tools/validate_", "schema_version", "selected_next_package", "artifact="]:
            assert term not in main


def test_selected_next_package_is_recorded() -> None:
    payload = _payload()
    assert payload["selected_next_package"] == "WP14P"
