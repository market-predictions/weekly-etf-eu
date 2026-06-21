from __future__ import annotations

from pathlib import Path

from tools.render_etf_eu_cockpit_pdf_premium_surface import LAYOUT_PDF, ORIGINAL_PDF, TARGET, render_premium_surface
from tools.validate_etf_eu_cockpit_pdf_premium_surface import (
    ACTION_MARKERS,
    AUTHORITY_MARKERS,
    EVIDENCE_AND_PROXY_MARKERS,
    NOTES,
    PAGE_MARKERS,
    RENDERER,
    TESTS,
    UCITS_PLACEHOLDER_MARKERS,
    VALIDATOR,
    validate_premium_surface_pdf,
)


def test_renderer_creates_premium_pdf() -> None:
    output = render_premium_surface()
    assert output == TARGET
    assert output.exists()


def test_validator_passes() -> None:
    render_premium_surface()
    result = validate_premium_surface_pdf(TARGET)
    assert result["status"] == "valid"
    assert result["selected_next_package"] == "WP15G"


def test_premium_pdf_header_and_size() -> None:
    render_premium_surface()
    data = TARGET.read_bytes()
    assert data.startswith(b"%PDF")
    assert len(data) > 8500


def test_source_pdf_evidence_is_preserved() -> None:
    assert ORIGINAL_PDF.exists()
    assert LAYOUT_PDF.exists()
    assert ORIGINAL_PDF.read_bytes().startswith(b"%PDF")
    assert LAYOUT_PDF.read_bytes().startswith(b"%PDF")


def test_support_files_exist() -> None:
    assert NOTES.exists()
    assert RENDERER.exists()
    assert VALIDATOR.exists()
    assert TESTS.exists()


def test_premium_pdf_contains_page_markers() -> None:
    render_premium_surface()
    data = TARGET.read_bytes()
    for marker in PAGE_MARKERS:
        assert marker in data


def test_premium_pdf_contains_authority_markers() -> None:
    render_premium_surface()
    data = TARGET.read_bytes()
    for marker in AUTHORITY_MARKERS:
        assert marker in data


def test_premium_pdf_contains_proxy_and_evidence_markers() -> None:
    render_premium_surface()
    data = TARGET.read_bytes()
    for marker in EVIDENCE_AND_PROXY_MARKERS:
        assert marker in data


def test_premium_pdf_contains_ucits_placeholder_markers() -> None:
    render_premium_surface()
    data = TARGET.read_bytes()
    for marker in UCITS_PLACEHOLDER_MARKERS:
        assert marker in data


def test_premium_pdf_contains_action_checklist_markers() -> None:
    render_premium_surface()
    data = TARGET.read_bytes()
    for marker in ACTION_MARKERS:
        assert marker in data


def test_no_distribution_artifact_created() -> None:
    render_premium_surface()
    assert not Path("output/delivery/weekly_etf_eu_cockpit_premium_surface_20260618_000000.json").exists()


def test_no_portfolio_candidate_funding_or_valuation_authority() -> None:
    render_premium_surface()
    data = TARGET.read_bytes()
    for marker in [
        b"portfolio_mutation=false",
        b"candidate_promotion=false",
        b"funding_authority=false",
        b"valuation_grade=false",
        b"live_data_fetch_performed=false",
        b"pricing_evidence_changed=false",
        b"recommendation_logic_changed=false",
    ]:
        assert marker in data
