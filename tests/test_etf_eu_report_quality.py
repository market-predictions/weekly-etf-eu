from __future__ import annotations

from pathlib import Path

import pytest

from runtime.polish_etf_eu_reports import polish_english
from runtime.render_etf_eu_report_from_state import build_etf_eu_report_state
from tools.validate_etf_eu_report_quality import EtfEuReportQualityError, validate_report_quality

REPORT = Path("output/weekly_etf_eu_review_260618_draft.md")


def test_eu_report_quality_validator_accepts_committed_draft() -> None:
    result = validate_report_quality(REPORT)
    assert result["status"] == "valid"


def test_eu_polish_adds_decision_cockpit_without_us_assumptions() -> None:
    source = REPORT.read_text(encoding="utf-8")
    result = polish_english(source, runtime_state={})
    assert "### EU decision cockpit" in result
    assert "UCITS exchange-line close evidence" in result
    assert "U.S. ETFs remain research proxies only" in result
    assert "SMH concentration remains above the soft position cap" not in result
    assert "SPY versus SMH overlap" not in result


def test_eu_polish_keeps_authority_flags_false() -> None:
    result = polish_english("# ETF EU Review\n", runtime_state={})
    assert "production_delivery=false" in result
    assert "portfolio_mutation=false" in result
    assert "funding_authority=false" in result
    assert "valuation_grade=false" in result
    assert "production_delivery=true" not in result


def test_eu_report_state_bridge_reads_eu_artifacts_only() -> None:
    state = build_etf_eu_report_state()
    assert state["schema_version"] == "etf_eu_report_state_bridge_v1"
    assert state["source_files"]["ucits_registry"] == "config/ucits_symbol_registry.yml"
    assert state["source_files"]["pricing_artifact"] == "output/pricing/etf_eu_ucits_closing_price_smoke_20260618_000000.json"
    assert state["source_files"]["draft_report"] == "output/weekly_etf_eu_review_260618_draft.md"
    assert state["summary"]["pricing_symbols"] == ["CSPX.L", "SXR8.DE"]
    assert "output/etf_portfolio_state.json" not in str(state)


def test_eu_report_quality_validator_rejects_true_authority_flag(tmp_path: Path) -> None:
    bad = tmp_path / "bad.md"
    bad.write_text(REPORT.read_text(encoding="utf-8") + "\nvaluation_grade=true\n", encoding="utf-8")
    with pytest.raises(EtfEuReportQualityError, match="forbidden authority flag"):
        validate_report_quality(bad)


def test_eu_report_quality_validator_rejects_proxy_funded_context(tmp_path: Path) -> None:
    bad = tmp_path / "bad_proxy.md"
    bad.write_text(REPORT.read_text(encoding="utf-8") + "\nSPY funded holding\n", encoding="utf-8")
    with pytest.raises(EtfEuReportQualityError, match="forbidden proxy context"):
        validate_report_quality(bad)
