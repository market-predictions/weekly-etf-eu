from __future__ import annotations

import json
from pathlib import Path

import pytest

from runtime.render_etf_eu_html_pdf_dry_run import build_manifest, render_dry_run_html
from tools.validate_etf_eu_html_pdf_dry_run import EtfEuHtmlPdfDryRunError, validate_html_pdf_dry_run

MANIFEST = Path("output/delivery/etf_eu_html_pdf_render_dry_run_20260618_000000.json")
EN_HTML = Path("output/delivery/weekly_etf_eu_review_260618_mature_dry_run.html")
NL_HTML = Path("output/delivery/weekly_etf_eu_review_nl_260618_mature_dry_run.html")
EN_MD = Path("output/weekly_etf_eu_review_260618_mature_draft.md")
NL_MD = Path("output/weekly_etf_eu_review_nl_260618_mature_draft.md")


def _write_manifest(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def test_valid_render_dry_run_manifest_passes() -> None:
    result = validate_html_pdf_dry_run(MANIFEST)
    assert result["status"] == "valid"
    assert result["selected_next_package"] == "WP14K"


def test_english_html_output_exists_and_contains_ucits_prices() -> None:
    text = EN_HTML.read_text(encoding="utf-8")
    assert "UCITS" in text
    assert "CSPX.L" in text
    assert "SXR8.DE" in text
    assert "U.S. ETFs are research proxies only" in text


def test_dutch_html_output_exists_and_contains_ucits_prices() -> None:
    text = NL_HTML.read_text(encoding="utf-8")
    assert "UCITS" in text
    assert "CSPX.L" in text
    assert "SXR8.DE" in text
    assert "Amerikaanse ETF's zijn alleen researchproxy" in text


def test_both_html_files_contain_dry_run_flags() -> None:
    for path in (EN_HTML, NL_HTML):
        text = path.read_text(encoding="utf-8")
        assert "dry_run_only=true" in text
        assert "production_delivery=false" in text
        assert "recipient_activation=false" in text
        assert "send_attempted=false" in text
        assert "real_receipt=false" in text


@pytest.mark.parametrize(
    "flag",
    [
        "production_delivery",
        "recipient_activation",
        "send_attempted",
        "real_receipt",
        "proof_claimed",
        "mail_transport_enabled",
        "smtp_configured",
        "secrets_present",
        "real_recipients",
        "portfolio_mutation",
        "candidate_promotion",
        "funding_authority",
        "valuation_grade",
    ],
)
def test_validator_rejects_true_manifest_flags(tmp_path: Path, flag: str) -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    payload[flag] = True
    path = _write_manifest(tmp_path, payload)
    with pytest.raises(EtfEuHtmlPdfDryRunError, match=f"{flag} must be false"):
        validate_html_pdf_dry_run(path)


def test_validator_rejects_script_tag(tmp_path: Path) -> None:
    bad_html = tmp_path / "bad.html"
    bad_html.write_text(EN_HTML.read_text(encoding="utf-8") + "\n<script></script>\n", encoding="utf-8")
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    payload["english_html_output_path"] = str(bad_html)
    path = _write_manifest(tmp_path, payload)
    with pytest.raises(EtfEuHtmlPdfDryRunError, match="forbidden HTML pattern"):
        validate_html_pdf_dry_run(path)


def test_validator_rejects_mailto_link(tmp_path: Path) -> None:
    bad_html = tmp_path / "bad_mail.html"
    bad_html.write_text(EN_HTML.read_text(encoding="utf-8") + '<a href="mai' + 'lto:test@example.com">x</a>', encoding="utf-8")
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    payload["english_html_output_path"] = str(bad_html)
    path = _write_manifest(tmp_path, payload)
    with pytest.raises(EtfEuHtmlPdfDryRunError, match="forbidden HTML pattern"):
        validate_html_pdf_dry_run(path)


def test_validator_rejects_missing_english_html_output(tmp_path: Path) -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    payload["english_html_output_path"] = str(tmp_path / "missing_en.html")
    path = _write_manifest(tmp_path, payload)
    with pytest.raises(EtfEuHtmlPdfDryRunError, match="english_html_output_path does not exist"):
        validate_html_pdf_dry_run(path)


def test_validator_rejects_missing_dutch_html_output(tmp_path: Path) -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    payload["dutch_html_output_path"] = str(tmp_path / "missing_nl.html")
    path = _write_manifest(tmp_path, payload)
    with pytest.raises(EtfEuHtmlPdfDryRunError, match="dutch_html_output_path does not exist"):
        validate_html_pdf_dry_run(path)


def test_render_function_generates_simple_html_without_remote_script() -> None:
    html = render_dry_run_html(EN_MD, language="en")
    assert "<script" not in html.lower()
    assert "mailto:" not in html.lower()
    assert "dry_run_only=true" in html
    assert "CSPX.L" in html
    assert "SXR8.DE" in html


def test_build_manifest_selects_wp14k() -> None:
    payload = build_manifest()
    assert payload["selected_next_package"] == "WP14K"
    assert payload["html_generation_status"] == "generated_dry_run_html"
    assert payload["pdf_generation_status"] == "not_generated_manifest_only"
