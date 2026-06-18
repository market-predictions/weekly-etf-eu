from __future__ import annotations

from pathlib import Path

import pytest

from tools.validate_etf_eu_dutch_language_quality import EtfEuDutchLanguageQualityError, validate_dutch_language_quality

NL_REPORT = Path("output/weekly_etf_eu_review_nl_260618_mature_draft.md")


def test_committed_dutch_mature_report_passes_language_quality() -> None:
    result = validate_dutch_language_quality(NL_REPORT)
    assert result["status"] == "valid"


def test_dutch_quality_rejects_english_only_authority_labels(tmp_path: Path) -> None:
    bad = tmp_path / "bad.md"
    forbidden_line = "production" + "_delivery=false"
    bad.write_text(NL_REPORT.read_text(encoding="utf-8") + "\n" + forbidden_line + "\n", encoding="utf-8")
    with pytest.raises(EtfEuDutchLanguageQualityError, match="forbidden English or authority phrase"):
        validate_dutch_language_quality(bad)


def test_dutch_quality_rejects_english_heading_leakage(tmp_path: Path) -> None:
    bad = tmp_path / "bad_heading.md"
    heading = "Executive" + " Summary"
    bad.write_text(NL_REPORT.read_text(encoding="utf-8") + "\n## " + heading + "\n", encoding="utf-8")
    with pytest.raises(EtfEuDutchLanguageQualityError, match="English heading leakage"):
        validate_dutch_language_quality(bad)


def test_dutch_quality_allows_required_financial_terms_and_tickers() -> None:
    text = NL_REPORT.read_text(encoding="utf-8")
    assert "ETF" in text
    assert "UCITS" in text
    assert "ISIN" in text
    assert "Yahoo" in text
    assert "CSPX.L" in text
    assert "SXR8.DE" in text
    assert "Xetra" in text
    assert "London Stock Exchange" in text
    validate_dutch_language_quality(NL_REPORT)


def test_dutch_quality_requires_core_no_authority_phrases(tmp_path: Path) -> None:
    bad = tmp_path / "bad_missing.md"
    text = NL_REPORT.read_text(encoding="utf-8").replace("geen waarderingsautoriteit", "")
    bad.write_text(text, encoding="utf-8")
    with pytest.raises(EtfEuDutchLanguageQualityError, match="missing Dutch phrase"):
        validate_dutch_language_quality(bad)
