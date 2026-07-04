from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_cockpit_multi_line_pricing_preview import MARKDOWN, PDF, PREVIEW, PRICING, validate


def _pricing() -> dict:
    return json.loads(PRICING.read_text(encoding="utf-8"))


def _preview() -> dict:
    return json.loads(PREVIEW.read_text(encoding="utf-8"))


def _sxr8(rows: list[dict]) -> dict:
    return next(row for row in rows if row["pricing_symbol"] == "SXR8.DE")


def test_expected_files_exist() -> None:
    assert PRICING.exists()
    assert PREVIEW.exists()
    assert MARKDOWN.exists()


def test_pricing_artifact_contains_rows() -> None:
    data = _pricing()
    assert data["pricing_rows"]
    assert data["successful_rows_count"] == 1
    assert data["skipped_rows_count"] == 2


def test_sxr8_success_row_is_present() -> None:
    row = _sxr8(_preview()["pricing_rows"])
    assert row["isin"] == "IE00B5BMR087"
    assert row["pricing_symbol"] == "SXR8.DE"
    assert row["latest_close_date"] == "2026-07-03"
    assert row["latest_close"] == 706.119995
    assert row["pricing_source"] == "yahoo_chart_v8"
    assert row["provider_status"] == "success"
    assert row["line_status"] == "success"


def test_markdown_preview_shows_sxr8_close() -> None:
    text = MARKDOWN.read_text(encoding="utf-8")
    assert "SXR8.DE" in text
    assert "706.119995" in text
    assert "2026-07-03" in text
    assert "yahoo_chart_v8" in text
    assert "beperkte multi-line koerspreview" in text


def test_skipped_rows_do_not_pass_as_successful_prices() -> None:
    rows = _preview()["pricing_rows"]
    skipped = [row for row in rows if row["line_status"].startswith("skipped")]
    assert skipped
    for row in skipped:
        assert row["latest_close"] is None
        assert row["provider_status"] == "skipped"


def test_no_us_proxy_symbols_pass_as_success() -> None:
    for row in _preview()["pricing_rows"]:
        if row["pricing_symbol"] in {"SPY", "QQQ", "GLD", "SMH", "PAVE"}:
            assert row["line_status"] != "success"


def test_pdf_path_is_separate_from_previous_preview_pdfs() -> None:
    data = _preview()
    assert data["pdf_preview_path"] == "output/client_surface/etf_eu_cockpit_multi_line_pricing_preview_20260703_000000.pdf"
    assert data["pdf_preview_path"] != "output/client_surface/etf_eu_cockpit_pdf_premium_dutch_refinement_candidate_20260703_000000.pdf"
    assert data["pdf_preview_path"] != "output/client_surface/etf_eu_cockpit_closing_price_preview_20260703_000000.pdf"
    assert data["pdf_created"] is False
    assert not PDF.exists()


def test_no_authority_flags_remain_false() -> None:
    data = _preview()
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
    assert result["work_package_id"] == "ETF-EU-WP15AA"
    assert result["selected_next_package"] == "ETF-EU-WP15AA-FIX"
