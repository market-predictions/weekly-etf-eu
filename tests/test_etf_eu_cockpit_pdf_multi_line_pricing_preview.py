from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_cockpit_pdf_multi_line_pricing_preview import ARTIFACT, NOTES, PDF, RENDERER, validate


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_expected_files_exist() -> None:
    assert RENDERER.exists()
    assert ARTIFACT.exists()
    assert NOTES.exists()


def test_pdf_exists_when_created() -> None:
    data = _artifact()
    assert data["pdf_created"] is True
    assert PDF.exists()
    assert PDF.stat().st_size > 1000


def test_pdf_path_is_dedicated() -> None:
    data = _artifact()
    assert data["pdf_preview_path"] == "output/client_surface/etf_eu_cockpit_pdf_multi_line_pricing_preview_20260703_000000.pdf"
    assert data["pdf_preview_path"] != "output/client_surface/etf_eu_cockpit_pdf_premium_dutch_refinement_candidate_20260703_000000.pdf"
    assert data["pdf_preview_path"] != "output/client_surface/etf_eu_cockpit_closing_price_preview_20260703_000000.pdf"
    assert data["pdf_preview_path"] != "output/client_surface/etf_eu_cockpit_multi_line_pricing_preview_20260703_000000.pdf"


def test_artifact_records_rows() -> None:
    data = _artifact()
    assert data["successful_rows_count"] == 2
    assert data["failed_rows_count"] == 0
    assert data["skipped_rows_count"] == 1
    assert data["first_successful_symbol"] == "SXR8.DE"
    assert data["first_successful_close_date"] == "2026-07-03"
    assert data["first_successful_close"] == 706.119995
    assert data["second_successful_symbol"] == "CSPX.L"
    assert data["second_successful_close_date"] == "2026-07-03"
    assert data["second_successful_close"] == 807.859985


def test_visual_review_notes_decision() -> None:
    text = NOTES.read_text(encoding="utf-8")
    assert "accepted_for_review_only_continuation" in text
    assert "SXR8.DE" in text
    assert "CSPX.L" in text
    assert "SMH" in text


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
    assert result["work_package_id"] == "ETF-EU-WP15AB"
    assert result["pdf_created"] is True
    assert result["selected_next_package"] == "ETF-EU-WP15AC"
