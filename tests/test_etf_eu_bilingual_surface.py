from __future__ import annotations

from pathlib import Path

import pytest

from runtime.polish_etf_eu_reports import bilingual_readiness_payload
from tools.validate_etf_eu_bilingual_surface import EtfEuBilingualSurfaceError, validate_bilingual_surface

ARTIFACT = Path("output/bilingual/etf_eu_bilingual_surface_readiness_20260618_000000.json")
REPORT = Path("output/weekly_etf_eu_review_260618_draft.md")


def test_bilingual_surface_validator_accepts_committed_readiness_artifact() -> None:
    result = validate_bilingual_surface(ARTIFACT)
    assert result["status"] == "valid"


def test_bilingual_payload_is_review_only_and_derived() -> None:
    payload = bilingual_readiness_payload(english_report_path=REPORT)
    assert payload["status"] == "minimal_readiness"
    assert payload["review_only"] is True
    assert payload["derived_from_english_eu_source_artifact"] is True
    assert payload["dutch_companion_independent_research_pass"] is False
    assert payload["production_delivery"] is False
    assert payload["portfolio_mutation"] is False
    assert payload["funding_authority"] is False
    assert payload["valuation_grade"] is False


def test_bilingual_validator_rejects_independent_research_pass_flag(tmp_path: Path) -> None:
    artifact = tmp_path / "bad_bilingual.json"
    payload = bilingual_readiness_payload(english_report_path=REPORT)
    payload["dutch_companion_independent_research_pass"] = True
    import json

    artifact.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    with pytest.raises(EtfEuBilingualSurfaceError, match="independent pass flag invalid"):
        validate_bilingual_surface(artifact)


def test_bilingual_validator_rejects_authority_promotion(tmp_path: Path) -> None:
    artifact = tmp_path / "bad_authority.json"
    payload = bilingual_readiness_payload(english_report_path=REPORT)
    payload["funding_authority"] = True
    import json

    artifact.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    with pytest.raises(EtfEuBilingualSurfaceError, match="funding_authority flag invalid"):
        validate_bilingual_surface(artifact)
