from __future__ import annotations

import json
from pathlib import Path

from tools.render_etf_eu_cockpit_pdf_mvp import TARGET, render_pdf_mvp
from tools.validate_etf_eu_cockpit_pdf_mvp import validate_pdf_mvp

CLOSEOUT = Path("output/client_surface/etf_eu_cockpit_poc_coordinator_closeout_20260618_000000.json")
POC_PACKAGE = Path("output/client_surface/etf_eu_cockpit_poc_package_20260618_000000.json")
DUTCH_MD = Path("output/client_surface/weekly_etf_eu_review_nl_260618_cockpit_pricing_integrated.md")
ENGLISH_MD = Path("output/client_surface/weekly_etf_eu_review_260618_cockpit_pricing_integrated.md")


def _closeout() -> dict:
    return json.loads(CLOSEOUT.read_text(encoding="utf-8"))


def test_renderer_creates_pdf() -> None:
    output = render_pdf_mvp()
    assert output == TARGET
    assert output.exists()


def test_validator_passes() -> None:
    render_pdf_mvp()
    result = validate_pdf_mvp(TARGET)
    assert result["status"] == "valid"
    assert result["pdf"] == str(TARGET)


def test_pdf_header_and_size() -> None:
    render_pdf_mvp()
    data = TARGET.read_bytes()
    assert data.startswith(b"%PDF")
    assert len(data) > 2500


def test_source_files_exist() -> None:
    for path in [CLOSEOUT, POC_PACKAGE, DUTCH_MD, ENGLISH_MD]:
        assert path.exists()


def test_authority_boundary_remains_blocked() -> None:
    closeout = _closeout()
    assert closeout["delivery_authorization_decision"] == "remain_blocked"
    for key in ["production_delivery", "portfolio_mutation", "candidate_promotion", "funding_authority", "valuation_grade"]:
        assert closeout[key] is False


def test_expected_target_path_is_used_exactly() -> None:
    assert str(TARGET) == "output/client_surface/weekly_etf_eu_cockpit_mvp_20260618_000000.pdf"


def test_pdf_contains_required_markers() -> None:
    render_pdf_mvp()
    data = TARGET.read_bytes()
    for marker in [b"proof_of_concept_pdf_mvp", b"IE00B5BMR087", b"CSPX.L", b"SXR8.DE", b"usable_for_review_only", b"SPY=research_proxy_only"]:
        assert marker in data


def test_no_email_or_delivery_artifact_is_created() -> None:
    render_pdf_mvp()
    assert b"no_email_action_occurred=true" in TARGET.read_bytes()
    assert not Path("output/delivery/weekly_etf_eu_cockpit_mvp_20260618_000000.json").exists()


def test_no_portfolio_state_is_modified_by_pdf_mvp() -> None:
    render_pdf_mvp()
    assert b"portfolio_state_modified=false" in TARGET.read_bytes()


def test_no_candidate_funding_or_valuation_authority_changes() -> None:
    render_pdf_mvp()
    data = TARGET.read_bytes()
    assert b"candidate_promoted=false" in data
    assert b"funding_authority=false" in data
    assert b"valuation_grade=false" in data
