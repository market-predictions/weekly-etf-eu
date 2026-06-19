from __future__ import annotations

import json
from pathlib import Path

from tools.validate_etf_eu_premium_cockpit_surface import validate_premium_cockpit_surface

MANIFEST = Path("output/client_surface/etf_eu_premium_cockpit_surface_20260618_000000.json")


def _payload() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _main_body(text: str) -> str:
    for marker in ["## Appendix", "## Bijlage"]:
        if marker in text:
            return text.split(marker, 1)[0]
    return text


def test_valid_cockpit_manifest_passes() -> None:
    result = validate_premium_cockpit_surface(MANIFEST)
    assert result["status"] == "valid"
    assert result["selected_next_package"] == "WP14O"


def test_cockpit_files_exist() -> None:
    payload = _payload()
    for key in [
        "english_cockpit_markdown_path",
        "dutch_cockpit_markdown_path",
        "english_cockpit_html_path",
        "dutch_cockpit_html_path",
    ]:
        assert Path(payload[key]).exists()


def test_hero_cockpit_summary_exists() -> None:
    payload = _payload()
    text = Path(payload["english_cockpit_markdown_path"]).read_text(encoding="utf-8")
    assert "## Cockpit summary" in text
    assert "Report status" in text
    assert "Current stance" in text


def test_status_cards_exist() -> None:
    payload = _payload()
    text = Path(payload["english_cockpit_markdown_path"]).read_text(encoding="utf-8")
    assert "## At-a-glance cards" in text
    for term in ["UCITS visibility", "Pricing evidence", "Research proxies", "Delivery status", "Portfolio authority"]:
        assert term in text


def test_reader_action_map_exists() -> None:
    payload = _payload()
    text = Path(payload["english_cockpit_markdown_path"]).read_text(encoding="utf-8")
    assert "## Reader action map" in text
    assert "What is actionable now?" in text


def test_blocker_panel_exists() -> None:
    payload = _payload()
    text = Path(payload["english_cockpit_markdown_path"]).read_text(encoding="utf-8")
    assert "## Current blockers" in text
    assert "Delivery authority" in text
    assert "remain_blocked" in text


def test_ucits_identity_pricing_and_proxy_terms_are_preserved() -> None:
    payload = _payload()
    combined = (
        Path(payload["english_cockpit_markdown_path"]).read_text(encoding="utf-8")
        + Path(payload["dutch_cockpit_markdown_path"]).read_text(encoding="utf-8")
    )
    for term in ["UCITS", "IE00B5BMR087", "CSPX.L", "SXR8.DE", "SPY"]:
        assert term in combined


def test_spy_proxy_separation_is_preserved() -> None:
    payload = _payload()
    text = Path(payload["english_cockpit_markdown_path"]).read_text(encoding="utf-8")
    assert "SPY remains a benchmark and research proxy only" in text
    assert "not an EU investable holding" in text


def test_delivery_authorization_remains_blocked() -> None:
    payload = _payload()
    assert payload["delivery_authorization_decision"] == "remain_blocked"


def test_authority_flags_remain_false() -> None:
    payload = _payload()
    for key in ["production_delivery", "portfolio_mutation", "funding_authority", "valuation_grade", "candidate_promotion"]:
        assert payload[key] is False


def test_debug_like_terms_are_absent_from_main_cockpit_body() -> None:
    payload = _payload()
    for key in ["english_cockpit_markdown_path", "dutch_cockpit_markdown_path"]:
        main = _main_body(Path(payload[key]).read_text(encoding="utf-8"))
        for term in ["tests/test_", "tools/validate_", "schema_version", "selected_next_package", "artifact="]:
            assert term not in main


def test_selected_next_package_is_recorded() -> None:
    payload = _payload()
    assert payload["selected_next_package"] == "WP14O"
