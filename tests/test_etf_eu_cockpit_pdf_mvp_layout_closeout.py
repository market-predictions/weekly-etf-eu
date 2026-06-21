from __future__ import annotations

import json
from pathlib import Path

from tools.validate_etf_eu_cockpit_pdf_mvp_layout_closeout import (
    ARTIFACT,
    LAYOUT_NOTES,
    LAYOUT_PDF,
    LAYOUT_RENDERER,
    LAYOUT_TESTS,
    LAYOUT_VALIDATOR,
    NOTES,
    ORIGINAL_PDF,
    validate_layout_closeout,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_layout_closeout_artifact_exists() -> None:
    assert ARTIFACT.exists()


def test_layout_closeout_notes_exist() -> None:
    assert NOTES.exists()


def test_original_pdf_exists_and_has_header() -> None:
    assert ORIGINAL_PDF.exists()
    assert ORIGINAL_PDF.read_bytes().startswith(b"%PDF")


def test_layout_pdf_exists_and_has_header() -> None:
    assert LAYOUT_PDF.exists()
    assert LAYOUT_PDF.read_bytes().startswith(b"%PDF")


def test_layout_pdf_has_expected_size() -> None:
    assert LAYOUT_PDF.stat().st_size > 4000


def test_layout_support_files_exist() -> None:
    assert LAYOUT_NOTES.exists()
    assert LAYOUT_RENDERER.exists()
    assert LAYOUT_VALIDATOR.exists()
    assert LAYOUT_TESTS.exists()


def test_closeout_records_source_and_status() -> None:
    data = _artifact()
    assert data["source_work_package"] == "WP15C"
    assert data["work_package"] == "WP15D"
    assert data["status"] == "completed"


def test_closeout_records_pdf_preservation_and_layout_output() -> None:
    data = _artifact()
    assert data["original_pdf_mvp_preserved"] is True
    assert data["original_pdf_mvp_path"] == str(ORIGINAL_PDF)
    assert data["layout_pdf_created"] is True
    assert data["layout_pdf_committed"] is True
    assert data["layout_pdf_path"] == str(LAYOUT_PDF)


def test_authority_boundary_flags() -> None:
    data = _artifact()
    assert data["delivery_authorization_decision"] == "remain_blocked"
    for key in ["production_delivery", "portfolio_mutation", "candidate_promotion", "funding_authority", "valuation_grade"]:
        assert data[key] is False


def test_operational_boundary_flags() -> None:
    data = _artifact()
    for key in [
        "outbound_path_enabled",
        "receipt_artifact_created",
        "recipient_configuration_changed",
        "credential_configuration_changed",
        "live_data_fetch_performed",
        "pricing_evidence_changed",
        "recommendation_logic_changed",
    ]:
        assert data[key] is False


def test_layout_improvements_are_recorded() -> None:
    data = _artifact()
    assert data["layout_improvements_confirmed"] is True
    assert isinstance(data["layout_improvements"], list)
    assert len(data["layout_improvements"]) >= 5


def test_selected_next_package_is_wp15e() -> None:
    data = _artifact()
    assert data["selected_next_package"] == "WP15E"
    assert data["selected_next_package_title"] == "ETF EU cockpit PDF MVP premium surface planning, no delivery"


def test_layout_closeout_validator_passes() -> None:
    result = validate_layout_closeout(ARTIFACT)
    assert result["status"] == "valid"
    assert result["selected_next_package"] == "WP15E"
