from __future__ import annotations

import json
from pathlib import Path

import pytest

from runtime.render_etf_eu_mature_report import render_mature_english
from runtime.render_etf_eu_report_nl import render_dutch_companion
from tools.validate_etf_eu_mature_bilingual_report import EtfEuMatureBilingualReportError, validate_mature_bilingual_report

ARTIFACT = Path("output/bilingual/etf_eu_bilingual_report_surface_20260618_000000.json")
EN_REPORT = Path("output/weekly_etf_eu_review_260618_mature_draft.md")
NL_REPORT = Path("output/weekly_etf_eu_review_nl_260618_mature_draft.md")


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "surface.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def test_committed_bilingual_surface_artifact_validates() -> None:
    result = validate_mature_bilingual_report(ARTIFACT)
    assert result["status"] == "valid"
    assert result["selected_next_package"] == "WP14J"


def test_english_mature_report_is_generated_from_eu_artifacts() -> None:
    report = render_mature_english()
    assert "ETF EU mature draft status" in report
    assert "output/pricing/etf_eu_ucits_closing_price_smoke_20260618_000000.json" in report
    assert "CSPX.L" in report
    assert "SXR8.DE" in report
    assert "IE00B5BMR087" in report
    assert "U.S. ETFs remain research proxies only" in report
    assert "output/etf_portfolio_state.json" not in report


def test_dutch_mature_report_is_generated_from_eu_artifacts() -> None:
    report = render_dutch_companion()
    assert "ETF EU-review" in report
    assert "UCITS-prijsbewijs" in report
    assert "CSPX.L" in report
    assert "SXR8.DE" in report
    assert "IE00B5BMR087" in report
    assert "Amerikaanse ETF's zijn alleen researchproxy's" in report
    assert "geen productielevering" in report
    assert "geen portefeuillemutatie" in report


def test_both_committed_reports_include_ucits_pricing_and_proxy_separation() -> None:
    en = EN_REPORT.read_text(encoding="utf-8")
    nl = NL_REPORT.read_text(encoding="utf-8")
    for text in (en, nl):
        assert "UCITS" in text
        assert "CSPX.L" in text
        assert "SXR8.DE" in text
        assert "SPY" in text
    assert "U.S. ETFs are research proxies only" in en
    assert "Amerikaanse ETF's zijn alleen researchproxy's" in nl


def test_bilingual_artifact_confirms_derived_dutch_companion() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["derived_from_english_eu_source_artifact"] is True
    assert payload["dutch_companion_independent_research_pass"] is False
    assert payload["meaning_parity_checked"] is True
    assert payload["production_delivery"] is False
    assert payload["recipient_activation"] is False
    assert payload["send_attempted"] is False
    assert payload["valuation_grade"] is False


@pytest.mark.parametrize("field", ["production_delivery", "recipient_activation", "send_attempted", "valuation_grade"])
def test_validator_rejects_authority_or_delivery_flag(tmp_path: Path, field: str) -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    payload[field] = True
    artifact = _write(tmp_path, payload)
    with pytest.raises(EtfEuMatureBilingualReportError, match=f"{field} must be false"):
        validate_mature_bilingual_report(artifact)


def test_validator_rejects_independent_dutch_research_pass(tmp_path: Path) -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    payload["dutch_companion_independent_research_pass"] = True
    artifact = _write(tmp_path, payload)
    with pytest.raises(EtfEuMatureBilingualReportError, match="Dutch companion independent pass must be false"):
        validate_mature_bilingual_report(artifact)
