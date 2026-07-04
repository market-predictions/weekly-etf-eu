from __future__ import annotations

import json

from tools.validate_etf_eu_cockpit_closing_price_preview import ARTIFACT, MARKDOWN, PDF, SOURCE, validate


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_expected_files_exist() -> None:
    assert SOURCE.exists()
    assert ARTIFACT.exists()
    assert MARKDOWN.exists()


def test_artifact_reads_successful_source_close() -> None:
    data = _artifact()
    assert data["work_package_id"] == "ETF-EU-WP15Z"
    assert data["source_work_package"] == "ETF-EU-WP15Y-FIX"
    assert data["symbol"] == "SXR8.DE"
    assert data["isin"] == "IE00B5BMR087"
    assert data["latest_close_date"] == "2026-07-03"
    assert data["latest_close"] == 706.119995
    assert data["pricing_source"] == "yahoo_chart_v8"
    assert data["provider_status"] == "success"


def test_markdown_preview_shows_close() -> None:
    text = MARKDOWN.read_text(encoding="utf-8")
    assert "SXR8.DE" in text
    assert "706.119995" in text
    assert "2026-07-03" in text
    assert "yahoo_chart_v8" in text
    assert "Dit is een beperkte koers-POC" in text


def test_pdf_path_is_separate_from_prior_candidate() -> None:
    data = _artifact()
    assert data["pdf_preview_path"] == "output/client_surface/etf_eu_cockpit_closing_price_preview_20260703_000000.pdf"
    assert data["pdf_preview_path"] != "output/client_surface/etf_eu_cockpit_pdf_premium_dutch_refinement_candidate_20260703_000000.pdf"
    assert data["pdf_created"] is False
    assert not PDF.exists()


def test_no_authority_flags_remain_false() -> None:
    data = _artifact()
    for key in [
        "valuation_grade",
        "pricing_evidence_for_client_grade",
        "pricing_evidence_for_delivery_preflight",
        "production_delivery",
        "portfolio_mutation",
        "candidate_promotion",
        "funding_authority",
        "client_grade_claim",
        "delivery_ready",
        "delivery_preflight_allowed",
        "receipt_artifact_created",
        "production_manifest_created",
        "fake_price_used",
        "us_proxy_price_used",
    ]:
        assert data[key] is False


def test_validator_passes() -> None:
    result = validate()
    assert result["status"] == "valid"
    assert result["work_package_id"] == "ETF-EU-WP15Z"
    assert result["selected_next_package"] == "ETF-EU-WP15AA"
