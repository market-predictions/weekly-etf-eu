from __future__ import annotations

from pathlib import Path

import pytest

from runtime.render_etf_eu_draft_report_from_ucits_smoke import build_report, render_report
from tools.validate_etf_eu_draft_report_surface import DraftReportSurfaceError, validate_draft_report_surface

REGISTRY = Path("config/ucits_symbol_registry.yml")
PRICING_ARTIFACT = Path("output/pricing/etf_eu_ucits_closing_price_smoke_20260618_000000.json")


def test_renderer_builds_first_eu_draft_from_committed_pricing_artifact():
    report = build_report(registry_path=REGISTRY, pricing_artifact_path=PRICING_ARTIFACT)
    assert "review_only=true" in report
    assert "production_delivery=false" in report
    assert "portfolio_mutation=false" in report
    assert "funding_authority=false" in report
    assert "valuation_grade=false" in report
    assert "CSPX.L" in report
    assert "SXR8.DE" in report
    assert "IE00B5BMR087" in report
    assert "U.S. ETFs are research proxies only" in report


def test_renderer_writes_report_that_validator_accepts(tmp_path: Path):
    output = tmp_path / "weekly_etf_eu_review_260618_draft.md"
    render_report(registry_path=REGISTRY, pricing_artifact_path=PRICING_ARTIFACT, output_path=output)
    result = validate_draft_report_surface(output)
    assert result["status"] == "valid"


def test_validator_rejects_missing_review_only_disclaimer(tmp_path: Path):
    output = tmp_path / "bad.md"
    output.write_text("# ETF EU Review\nproduction_delivery=false\nportfolio_mutation=false\n", encoding="utf-8")
    with pytest.raises(DraftReportSurfaceError, match="missing required report surface text"):
        validate_draft_report_surface(output)


def test_validator_rejects_true_authority_flag(tmp_path: Path):
    output = tmp_path / "bad.md"
    report = build_report(registry_path=REGISTRY, pricing_artifact_path=PRICING_ARTIFACT)
    output.write_text(report + "\nproduction_delivery=true\n", encoding="utf-8")
    with pytest.raises(DraftReportSurfaceError, match="forbidden authority flag"):
        validate_draft_report_surface(output)


def test_report_does_not_present_us_proxy_as_eu_holding():
    report = build_report(registry_path=REGISTRY, pricing_artifact_path=PRICING_ARTIFACT)
    assert "SPY funded holding" not in report
    assert "SMH funded holding" not in report
    assert "GLD funded holding" not in report
    assert "PAVE funded holding" not in report
