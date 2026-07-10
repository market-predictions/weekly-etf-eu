import json
from pathlib import Path

import pytest

from tools.build_etf_eu_fresh_generation_package import _reject_us_state
from tools.validate_etf_eu_fresh_generation_package import validate

MANIFEST = Path("output/fresh_generation/etf_eu_fresh_generation_package_manifest_20260710_000000.json")


def test_builder_refuses_us_state_authority_paths():
    with pytest.raises(SystemExit):
        _reject_us_state("output/etf_portfolio_state.json", "portfolio_state")


def test_fresh_generation_package_manifest_is_renderer_integrated_no_send():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert data["fresh_generation_status"] == "full_package_generated"
    assert data["full_generation_status"] == "renderer_integrated"
    assert data["pdf_generation_status"] == "generated"
    assert data["send_executed"] is False
    assert data["transport_attempted"] is False
    assert data["receipt_confirmed"] is False
    assert data["valuation_grade"] is False
    assert data["funding_authority"] is False
    assert data["portfolio_mutation"] is False
    assert data["production_delivery_authority"] is False


def test_validator_accepts_renderer_integrated_package():
    result = validate(MANIFEST)
    assert result["status"] == "valid"
    assert result["pdf_generation_status"] == "generated"


def test_package_preserves_dutch_primary_and_english_companion_paths():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert "_nl_" in data["dutch_primary_markdown"]
    assert "_nl_" not in data["english_companion_markdown"]
    assert data["dutch_primary_pdf"].endswith(".pdf")
    assert data["english_companion_pdf"].endswith(".pdf")
