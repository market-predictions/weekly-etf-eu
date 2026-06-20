from __future__ import annotations

import json
from pathlib import Path

from tools.validate_etf_eu_cockpit_pdf_mvp_closeout import ARTIFACT, NOTES, PDF, validate_closeout

RENDERER = Path("tools/render_etf_eu_cockpit_pdf_mvp.py")
PDF_VALIDATOR = Path("tools/validate_etf_eu_cockpit_pdf_mvp.py")
PDF_TESTS = Path("tests/test_etf_eu_cockpit_pdf_mvp.py")


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_closeout_artifact_exists() -> None:
    assert ARTIFACT.exists()


def test_review_notes_exist() -> None:
    assert NOTES.exists()


def test_pdf_exists_and_has_header() -> None:
    assert PDF.exists()
    assert PDF.read_bytes().startswith(b"%PDF")


def test_pdf_has_expected_size() -> None:
    assert PDF.stat().st_size > 2500


def test_closeout_records_source_and_status() -> None:
    data = _artifact()
    assert data["source_work_package"] == "WP15A"
    assert data["work_package"] == "WP15B"
    assert data["status"] == "completed"


def test_closeout_records_expected_paths() -> None:
    data = _artifact()
    assert data["pdf_mvp_path"] == str(PDF)
    assert data["renderer_path"] == str(RENDERER)
    assert data["validator_path"] == str(PDF_VALIDATOR)
    assert data["test_path"] == str(PDF_TESTS)
    assert RENDERER.exists()
    assert PDF_VALIDATOR.exists()
    assert PDF_TESTS.exists()


def test_core_boundary_flags_remain_false() -> None:
    data = _artifact()
    assert data["delivery_authorization_decision"] == "remain_blocked"
    for key in ["production_delivery", "portfolio_mutation", "candidate_promotion", "funding_authority", "valuation_grade"]:
        assert data[key] is False


def test_operational_safety_flags_remain_true() -> None:
    data = _artifact()
    for key in [
        "no_email_send",
        "no_delivery_receipt_created",
        "no_recipient_config_changed",
        "no_secrets_changed",
        "no_live_data_fetch",
        "no_pricing_evidence_update",
        "no_recommendation_logic_change",
    ]:
        assert data[key] is True


def test_selected_next_package_is_wp15c() -> None:
    data = _artifact()
    assert data["selected_next_package"] == "WP15C"
    assert data["selected_next_package_title"] == "ETF EU cockpit PDF MVP layout and readability iteration, no delivery"


def test_closeout_validator_passes() -> None:
    result = validate_closeout(ARTIFACT)
    assert result["status"] == "valid"
    assert result["selected_next_package"] == "WP15C"
