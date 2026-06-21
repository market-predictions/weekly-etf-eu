from __future__ import annotations

import json
from pathlib import Path

from tools.validate_etf_eu_cockpit_pdf_premium_surface_closeout import (
    ARTIFACT,
    LAYOUT_PDF,
    NOTES,
    ORIGINAL_PDF,
    PLAN_MD,
    PREMIUM_NOTES,
    PREMIUM_PDF,
    PREMIUM_TESTS,
    PREMIUM_VALIDATOR,
    RENDERER,
    validate_premium_surface_closeout,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_closeout_json_exists() -> None:
    assert ARTIFACT.exists()


def test_closeout_notes_exist() -> None:
    assert NOTES.exists()


def test_premium_pdf_exists_and_has_header_and_size() -> None:
    assert PREMIUM_PDF.exists()
    data = PREMIUM_PDF.read_bytes()
    assert data.startswith(b"%PDF")
    assert len(data) > 8500


def test_source_pdf_artifacts_are_preserved() -> None:
    assert ORIGINAL_PDF.exists()
    assert LAYOUT_PDF.exists()
    assert ORIGINAL_PDF.read_bytes().startswith(b"%PDF")
    assert LAYOUT_PDF.read_bytes().startswith(b"%PDF")


def test_planning_and_premium_support_artifacts_exist() -> None:
    assert PLAN_MD.exists()
    assert PREMIUM_NOTES.exists()
    assert RENDERER.exists()
    assert PREMIUM_VALIDATOR.exists()
    assert PREMIUM_TESTS.exists()


def test_closeout_records_package_identity() -> None:
    data = _artifact()
    assert data["work_package"] == "WP15G"
    assert data["source_work_package"] == "WP15F"
    assert data["status"] == "completed"


def test_closeout_records_premium_pdf_commit() -> None:
    data = _artifact()
    assert data["premium_pdf_commit"] == "fb7751026a70db355385946ee3882c68f9ec0e71"
    assert data["premium_pdf_path"] == str(PREMIUM_PDF)
    assert data["premium_pdf_surface_created"] is True
    assert data["premium_pdf_committed"] is True


def test_closeout_only_and_no_new_pdf_or_renderer_change() -> None:
    data = _artifact()
    assert data["closeout_only"] is True
    assert data["new_pdf_created"] is False
    assert data["renderer_changed"] is False


def test_no_distribution_or_manifest_claims_recorded() -> None:
    data = _artifact()
    assert data["outbound_path_enabled"] is False
    assert data["receipt_artifact_created"] is False
    assert data["production_manifest_created"] is False
    assert data["client_distribution_claimed"] is False


def test_authority_boundary_remains_blocked() -> None:
    data = _artifact()
    assert data["delivery_authorization_decision"] == "remain_blocked"
    for key in ["production_delivery", "portfolio_mutation", "candidate_promotion", "funding_authority", "valuation_grade"]:
        assert data[key] is False


def test_selected_next_package_is_wp15h() -> None:
    data = _artifact()
    assert data["selected_next_package"] == "WP15H"


def test_validator_passes() -> None:
    result = validate_premium_surface_closeout(ARTIFACT)
    assert result["status"] == "valid"
    assert result["selected_next_package"] == "WP15H"
