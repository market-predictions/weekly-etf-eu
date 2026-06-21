from __future__ import annotations

import json
from pathlib import Path

from tools.validate_etf_eu_cockpit_pdf_premium_surface_plan import (
    ARTIFACT,
    LAYOUT_PDF,
    MARKDOWN_PLAN,
    ORIGINAL_PDF,
    REQUIRED_SECTIONS,
    validate_premium_surface_plan,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _markdown() -> str:
    return MARKDOWN_PLAN.read_text(encoding="utf-8")


def test_markdown_planning_artifact_exists() -> None:
    assert MARKDOWN_PLAN.exists()


def test_json_planning_artifact_exists() -> None:
    assert ARTIFACT.exists()


def test_pdf_evidence_artifacts_exist() -> None:
    assert ORIGINAL_PDF.exists()
    assert LAYOUT_PDF.exists()
    assert ORIGINAL_PDF.read_bytes().startswith(b"%PDF")
    assert LAYOUT_PDF.read_bytes().startswith(b"%PDF")


def test_markdown_contains_required_section_titles() -> None:
    markdown = _markdown()
    for section in REQUIRED_SECTIONS:
        assert section in markdown


def test_markdown_preserves_four_layer_distinction() -> None:
    markdown = _markdown()
    for marker in ["Decision framework", "Input/state contract", "Output contract", "Operational runbook"]:
        assert marker in markdown


def test_markdown_records_premium_surface_target_structure() -> None:
    markdown = _markdown()
    for marker in [
        "Page 1 — Executive cockpit cover",
        "Page 2 — Decision cockpit",
        "Page 3 — UCITS evidence cockpit",
        "Page 4 — Research proxy separation",
        "Page 5 — Action and validation checklist",
    ]:
        assert marker in markdown


def test_markdown_records_non_goals() -> None:
    markdown = _markdown()
    assert "## 14. Non-goals" in markdown
    for marker in ["create a new PDF", "render a new PDF", "fetch live data", "change ETF recommendation logic"]:
        assert marker in markdown


def test_json_records_package_identity() -> None:
    data = _artifact()
    assert data["work_package"] == "WP15E"
    assert data["source_work_package"] == "WP15D"
    assert data["status"] == "completed"


def test_json_records_planning_only_boundary() -> None:
    data = _artifact()
    assert data["planning_only"] is True
    assert data["new_pdf_created"] is False
    assert data["renderer_changed"] is False
    assert data["pricing_evidence_changed"] is False
    assert data["recommendation_logic_changed"] is False
    assert data["live_data_fetch_performed"] is False


def test_authority_boundary_remains_blocked() -> None:
    data = _artifact()
    assert data["delivery_authorization_decision"] == "remain_blocked"
    for key in ["production_delivery", "portfolio_mutation", "candidate_promotion", "funding_authority", "valuation_grade"]:
        assert data[key] is False


def test_selected_next_package_is_wp15f() -> None:
    data = _artifact()
    assert data["selected_next_package"] == "WP15F"


def test_validator_passes() -> None:
    result = validate_premium_surface_plan(ARTIFACT)
    assert result["status"] == "valid"
    assert result["selected_next_package"] == "WP15F"
