from __future__ import annotations

import json
from pathlib import Path

from tools.validate_etf_eu_client_poc_surface import validate_client_poc_surface

MANIFEST = Path("output/client_surface/etf_eu_client_surface_20260618_000000.json")


def _payload() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_valid_client_surface_manifest_passes() -> None:
    result = validate_client_poc_surface(MANIFEST)
    assert result["status"] == "valid"
    assert result["selected_next_package"] == "WP14N"


def test_client_surface_files_exist() -> None:
    payload = _payload()
    for key in ["english_poc_markdown_path", "dutch_poc_markdown_path", "english_poc_html_path", "dutch_poc_html_path"]:
        assert Path(payload[key]).exists()


def test_ucits_identity_pricing_and_proxy_terms_are_present() -> None:
    payload = _payload()
    combined = Path(payload["english_poc_markdown_path"]).read_text(encoding="utf-8") + Path(payload["dutch_poc_markdown_path"]).read_text(encoding="utf-8")
    for term in ["UCITS", "IE00B5BMR087", "CSPX.L", "SXR8.DE", "SPY"]:
        assert term in combined


def test_client_surface_flags_are_preserved() -> None:
    payload = _payload()
    assert payload["delivery_authorization_decision"] == "remain_blocked"
    assert payload["client_surface_created"] is True
    assert payload["debug_surface_reduced"] is True
    assert payload["technical_evidence_moved_to_appendix"] is True
    assert payload["ucits_identity_preserved"] is True
    assert payload["proxy_separation_preserved"] is True
    assert payload["pricing_evidence_preserved"] is True


def test_authority_flags_remain_false() -> None:
    payload = _payload()
    for key in ["delivery_authorized", "production_delivery", "portfolio_mutation", "candidate_promotion", "funding_authority", "valuation_grade"]:
        assert payload[key] is False


def test_debug_like_terms_absent_from_main_report_body() -> None:
    payload = _payload()
    text = Path(payload["english_poc_markdown_path"]).read_text(encoding="utf-8")
    main = text.split("## Appendix", 1)[0]
    for term in ["ETF_EU_", "tests/test_", "tools/validate_", "selected_next_package", "schema_version", "artifact="]:
        assert term not in main


def test_technical_evidence_is_in_appendix() -> None:
    payload = _payload()
    text = Path(payload["english_poc_markdown_path"]).read_text(encoding="utf-8")
    assert "## Appendix" in text
    assert "Source report" in text.split("## Appendix", 1)[1]


def test_selected_next_package_is_wp14n() -> None:
    payload = _payload()
    assert payload["selected_next_package"] == "WP14N"
