from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tools.render_etf_eu_enriched_cockpit import render_enriched_cockpit
from tools.validate_etf_eu_enriched_cockpit_render import validate_enriched_cockpit_render

SOURCE = Path("output/client_surface/etf_eu_cockpit_universe_enrichment_20260618_000000.json")
MANIFEST = Path("output/client_surface/etf_eu_enriched_cockpit_render_20260618_000000.json")


def _payload() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _source_payload() -> dict:
    return json.loads(SOURCE.read_text(encoding="utf-8"))


def _main_body(text: str) -> str:
    for marker in ["## Appendix", "## Bijlage"]:
        if marker in text:
            return text.split(marker, 1)[0]
    return text


def _hashes(payload: dict) -> dict[str, str]:
    return {
        key: hashlib.sha256(Path(payload[key]).read_bytes()).hexdigest()
        for key in [
            "english_rendered_cockpit_markdown_path",
            "dutch_rendered_cockpit_markdown_path",
            "english_rendered_cockpit_html_path",
            "dutch_rendered_cockpit_html_path",
        ]
    }


def test_renderer_creates_all_expected_outputs() -> None:
    render_enriched_cockpit(SOURCE)
    payload = _payload()
    for key in [
        "english_rendered_cockpit_markdown_path",
        "dutch_rendered_cockpit_markdown_path",
        "english_rendered_cockpit_html_path",
        "dutch_rendered_cockpit_html_path",
    ]:
        assert Path(payload[key]).exists()


def test_render_manifest_passes_validator() -> None:
    result = validate_enriched_cockpit_render(MANIFEST)
    assert result["status"] == "valid"
    assert result["selected_next_package"] == "WP14Q"


def test_rendered_cockpit_summary_and_cards_exist() -> None:
    payload = _payload()
    text = Path(payload["english_rendered_cockpit_markdown_path"]).read_text(encoding="utf-8")
    assert "## Cockpit summary" in text
    assert "## At-a-glance cards" in text
    assert "review-only" in text


def test_rendered_sections_exist() -> None:
    payload = _payload()
    text = Path(payload["english_rendered_cockpit_markdown_path"]).read_text(encoding="utf-8")
    for section in [
        "## Visible UCITS universe",
        "## Candidate evidence map",
        "## Pricing and identity gaps",
        "## Proxy separation map",
        "## Reader action map",
        "## Current blockers",
    ]:
        assert section in text


def test_candidate_universe_count_is_preserved() -> None:
    payload = _payload()
    source = _source_payload()
    assert payload["visible_candidate_count"] == source["visible_candidate_count"]
    assert payload["visible_candidate_count"] == 4


def test_candidate_statuses_remain_allowed_and_preserved() -> None:
    payload = _payload()
    source_statuses = sorted(candidate["cockpit_status"] for candidate in _source_payload()["visible_candidates"])
    assert sorted(payload["visible_candidate_statuses"].values()) == source_statuses
    allowed = {
        "visible_review_candidate",
        "identity_incomplete",
        "pricing_incomplete",
        "proxy_only_mapping",
        "blocked_until_verified",
    }
    assert set(payload["visible_candidate_statuses"].values()) <= allowed


def test_ucits_identity_and_key_candidates_are_preserved() -> None:
    payload = _payload()
    combined = (
        Path(payload["english_rendered_cockpit_markdown_path"]).read_text(encoding="utf-8")
        + Path(payload["dutch_rendered_cockpit_markdown_path"]).read_text(encoding="utf-8")
    )
    for term in ["UCITS", "IE00B5BMR087", "IE00BMC38736"]:
        assert term in combined


def test_pricing_and_proxy_separation_terms_are_preserved() -> None:
    payload = _payload()
    combined = (
        Path(payload["english_rendered_cockpit_markdown_path"]).read_text(encoding="utf-8")
        + Path(payload["dutch_rendered_cockpit_markdown_path"]).read_text(encoding="utf-8")
    )
    for term in ["CSPX.L", "SXR8.DE", "SPY", "SMH", "GLD", "PAVE"]:
        assert term in combined
    assert "research proxy only" in combined or "researchproxy" in combined


def test_authority_flags_remain_blocked_or_false() -> None:
    payload = _payload()
    assert payload["delivery_authorization_decision"] == "remain_blocked"
    for key in [
        "production_delivery",
        "portfolio_mutation",
        "candidate_promotion",
        "funding_authority",
        "valuation_grade",
    ]:
        assert payload[key] is False


def test_debug_like_terms_are_absent_from_main_body() -> None:
    payload = _payload()
    for key in ["english_rendered_cockpit_markdown_path", "dutch_rendered_cockpit_markdown_path"]:
        main = _main_body(Path(payload[key]).read_text(encoding="utf-8"))
        for term in ["tests/test_", "tools/validate_", "schema_version", "selected_next_package", "artifact="]:
            assert term not in main


def test_renderer_is_deterministic_for_unchanged_source() -> None:
    render_enriched_cockpit(SOURCE)
    first_payload = _payload()
    first_hashes = _hashes(first_payload)
    first_manifest = MANIFEST.read_text(encoding="utf-8")

    render_enriched_cockpit(SOURCE)
    second_payload = _payload()
    second_hashes = _hashes(second_payload)
    second_manifest = MANIFEST.read_text(encoding="utf-8")

    assert first_hashes == second_hashes
    assert first_manifest == second_manifest


def test_generated_html_has_no_external_assets_or_scripts() -> None:
    payload = _payload()
    for key in ["english_rendered_cockpit_html_path", "dutch_rendered_cockpit_html_path"]:
        html = Path(payload[key]).read_text(encoding="utf-8").lower()
        assert "<script" not in html
        assert "href=" not in html
        assert "src=" not in html
