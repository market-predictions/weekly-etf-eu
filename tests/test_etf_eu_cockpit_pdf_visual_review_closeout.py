from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_cockpit_pdf_visual_review_closeout import CLOSEOUT, CLOSEOUT_NOTES, PDF, validate


def _closeout() -> dict:
    return json.loads(CLOSEOUT.read_text(encoding="utf-8"))


def test_expected_source_files_exist() -> None:
    assert PDF.exists()
    assert CLOSEOUT.exists()
    assert CLOSEOUT_NOTES.exists()


def test_pdf_page_count_and_decision() -> None:
    data = _closeout()
    assert data["pdf_exists"] is True
    assert data["pdf_page_count"] == 4
    assert data["visual_decision"] in {
        "accepted_for_review_only_foundation",
        "accepted_with_minor_visual_notes",
        "rejected_needs_pdf_render_fix",
        "blocked_pdf_missing_or_unreadable",
    }


def test_accepted_decision_selects_wp15ad() -> None:
    data = _closeout()
    if data["visual_decision"] in {"accepted_for_review_only_foundation", "accepted_with_minor_visual_notes"}:
        assert data["accepted_for_review_only_foundation"] is True
        assert data["selected_next_package"] == "ETF-EU-WP15AD"
    else:
        assert data["accepted_for_review_only_foundation"] is False
        assert data["selected_next_package"] == "ETF-EU-WP15AC-FIX"


def test_source_values_remain_fixed() -> None:
    data = _closeout()
    assert data["successful_rows_count"] == 2
    assert data["failed_rows_count"] == 0
    assert data["skipped_rows_count"] == 1
    assert data["first_successful_symbol"] == "SXR8.DE"
    assert data["first_successful_close"] == 706.119995
    assert data["second_successful_symbol"] == "CSPX.L"
    assert data["second_successful_close"] == 807.859985
    assert data["smh_status"] == "skipped_pending_registry_status"


def test_no_authority_flags_remain_false() -> None:
    data = _closeout()
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


def test_closeout_notes_contain_required_markers() -> None:
    text = CLOSEOUT_NOTES.read_text(encoding="utf-8")
    for marker in [
        "title visible",
        "review-only status visible",
        "two successful rows visible",
        "SXR8.DE close visible and correct",
        "CSPX.L close visible and correct",
        "SMH pending/skipped visible",
        "boundary caveat visible",
        "no U.S. proxy price shown as investable",
        "no funding or portfolio mutation implied",
        "no delivery-ready claim",
        "PDF path is separate from prior candidates",
    ]:
        assert marker in text


def test_validator_passes() -> None:
    result = validate()
    assert result["status"] == "valid"
    assert result["work_package_id"] == "ETF-EU-WP15AC"
    assert result["accepted_for_review_only_foundation"] is True
    assert result["selected_next_package"] == "ETF-EU-WP15AD"
