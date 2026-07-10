import json
from argparse import Namespace
from pathlib import Path

import pytest

from tools.build_etf_eu_fresh_generation_dry_run import build_manifest, _reject_us_state
from tools.validate_etf_eu_fresh_generation_dry_run import validate

MANIFEST = Path("output/fresh_generation/etf_eu_fresh_generation_package_manifest_20260710_000000.json")


def test_builder_refuses_us_state_authority_paths():
    with pytest.raises(SystemExit):
        _reject_us_state("output/etf_portfolio_state.json", "portfolio_state")


def test_fresh_generation_manifest_exists_and_is_no_send_scaffold():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert data["fresh_generation_status"] == "scaffold_created"
    assert data["full_generation_status"] == "blocked_pending_renderer_or_pricing_integration"
    assert data["pdf_generation_status"] == "not_implemented_in_mvp23"
    assert data["ready_for_controlled_delivery"] is False
    assert data["send_executed"] is False
    assert data["transport_attempted"] is False
    assert data["receipt_confirmed"] is False


def test_fresh_generation_manifest_preserves_language_distinction_and_authority_boundaries():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert data["dutch_primary"] is True
    assert data["english_companion"] is True
    assert "_nl_" in data["dutch_primary_markdown"]
    assert "_nl_" not in data["english_companion_markdown"]
    for key in ["valuation_grade", "funding_authority", "portfolio_mutation", "production_delivery_authority"]:
        assert data[key] is False


def test_validator_accepts_committed_manifest():
    result = validate(MANIFEST)
    assert result["status"] == "valid"
    assert result["fresh_generation_status"] == "scaffold_created"
    assert result["ready_for_controlled_delivery"] is False


def test_validator_rejects_delivery_or_authority_promotion(tmp_path):
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    data["send_executed"] = True
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(AssertionError):
        validate(bad)


def test_routine_run_manifest_handoff_is_written():
    routine = json.loads(Path("output/run_manifests/etf_eu_routine_run_manifest_2026-07-10_20260710_000000.json").read_text(encoding="utf-8"))
    assert routine["routine_stage"] == "fresh_generation_dry_run_scaffold"
    assert routine["delivery_package_manifest"] == str(MANIFEST)
    assert routine["transport_attempted"] is False
    assert routine["receipt_confirmed"] is False
