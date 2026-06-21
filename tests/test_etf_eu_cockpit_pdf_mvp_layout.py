from __future__ import annotations

from pathlib import Path

from tools.render_etf_eu_cockpit_pdf_mvp_layout import ORIGINAL_PDF, TARGET, render_pdf_mvp_layout
from tools.validate_etf_eu_cockpit_pdf_mvp_layout import NOTES, validate_layout_pdf

RENDERER = Path("tools/render_etf_eu_cockpit_pdf_mvp_layout.py")
VALIDATOR = Path("tools/validate_etf_eu_cockpit_pdf_mvp_layout.py")
TESTS = Path("tests/test_etf_eu_cockpit_pdf_mvp_layout.py")


def test_layout_renderer_creates_pdf() -> None:
    output = render_pdf_mvp_layout()
    assert output == TARGET
    assert output.exists()


def test_layout_validator_passes() -> None:
    render_pdf_mvp_layout()
    result = validate_layout_pdf(TARGET)
    assert result["status"] == "valid"
    assert result["selected_next_package"] == "WP15D"


def test_layout_pdf_header_and_size() -> None:
    render_pdf_mvp_layout()
    data = TARGET.read_bytes()
    assert data.startswith(b"%PDF")
    assert len(data) > 4000


def test_original_pdf_is_preserved() -> None:
    assert ORIGINAL_PDF.exists()
    assert ORIGINAL_PDF.read_bytes().startswith(b"%PDF")


def test_layout_support_files_exist() -> None:
    assert NOTES.exists()
    assert RENDERER.exists()
    assert VALIDATOR.exists()
    assert TESTS.exists()


def test_layout_pdf_contains_required_markers() -> None:
    render_pdf_mvp_layout()
    data = TARGET.read_bytes()
    for marker in [
        b"ETF EU Cockpit",
        b"proof-of-concept",
        b"review-only",
        b"delivery_authorization_decision=remain_blocked",
        b"production_delivery=false",
        b"portfolio_mutation=false",
        b"candidate_promotion=false",
        b"funding_authority=false",
        b"valuation_grade=false",
        b"IE00B5BMR087",
        b"CSPX.L",
        b"SXR8.DE",
        b"usable_for_review_only",
        b"pricing_symbol_ambiguous",
        b"policy_blocked",
        b"identity_incomplete",
        b"SPY=research_proxy_only",
        b"SMH=research_proxy_only_and_ambiguous_as_pricing_symbol",
        b"GLD=research_proxy_only_not_eu_holding",
        b"PAVE=research_proxy_only_not_eu_holding",
        b"selected_next_package=WP15D",
    ]:
        assert marker in data


def test_layout_notes_record_next_package_and_boundary() -> None:
    notes = NOTES.read_text(encoding="utf-8")
    assert "selected_next_package=WP15D" in notes
    for marker in [
        "delivery_authorization_decision=remain_blocked",
        "production_delivery=false",
        "portfolio_mutation=false",
        "candidate_promotion=false",
        "funding_authority=false",
        "valuation_grade=false",
    ]:
        assert marker in notes


def test_no_layout_delivery_artifact_created() -> None:
    render_pdf_mvp_layout()
    assert not Path("output/delivery/weekly_etf_eu_cockpit_mvp_layout_20260618_000000.json").exists()


def test_layout_pdf_keeps_state_markers_false() -> None:
    render_pdf_mvp_layout()
    data = TARGET.read_bytes()
    assert b"production_delivery=false" in data
    assert b"portfolio_mutation=false" in data
    assert b"candidate_promotion=false" in data
    assert b"funding_authority=false" in data
    assert b"valuation_grade=false" in data
