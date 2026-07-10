from argparse import Namespace
from pathlib import Path

import pytest

from tools.write_etf_eu_routine_run_manifest import build_manifest
from tools.validate_etf_eu_routine_run_manifest import validate


def _args(**overrides):
    base = {
        "output_dir": "output",
        "manifest_path": None,
        "run_id": "20260710_000000",
        "report_date": "2026-07-10",
        "report_suffix": "260710",
        "routine_stage": "planning_defined",
        "workflow_status": "planning_defined",
        "workflow_conclusion": None,
        "previous_delivery_closeout_manifest": "output/run_manifests/etf_eu_delivery_closeout_manifest_20260710_1755.json",
        "portfolio_state": "output/etf_eu_portfolio_state.json",
        "valuation_history": "output/etf_eu_valuation_history.csv",
        "trade_ledger": "output/etf_eu_trade_ledger.csv",
        "recommendation_scorecard": "output/etf_eu_recommendation_scorecard.csv",
        "pricing_artifact": None,
        "delivery_package_manifest": None,
        "ready_artifact": None,
        "delivery_closeout_manifest": None,
        "dutch_primary_markdown": None,
        "english_companion_markdown": None,
        "dutch_primary_html": None,
        "english_companion_html": None,
        "dutch_primary_pdf": None,
        "english_companion_pdf": None,
        "transport_attempted": "false",
        "transport_success": "false",
        "receipt_confirmed": "false",
        "valuation_grade": "false",
        "funding_authority": "false",
        "portfolio_mutation": "false",
        "production_delivery_authority": "false",
        "next_package": "ETF-EU-MVP23_FRESH_WEEKLY_EU_REPORT_GENERATION_DRY_RUN",
    }
    base.update(overrides)
    return Namespace(**base)


def test_routine_manifest_can_be_built_without_sending():
    manifest = build_manifest(_args())
    assert manifest["transport_attempted"] is False
    assert manifest["transport_success"] is False
    assert manifest["receipt_confirmed"] is False
    assert manifest["portfolio_state_path"] == "output/etf_eu_portfolio_state.json"


def test_writer_rejects_transport_success_without_attempt():
    with pytest.raises(SystemExit):
        build_manifest(_args(transport_success="true", transport_attempted="false"))


def test_writer_rejects_receipt_without_closeout():
    with pytest.raises(SystemExit):
        build_manifest(_args(receipt_confirmed="true", delivery_closeout_manifest=None))


def test_writer_rejects_us_portfolio_state_authority():
    with pytest.raises(SystemExit):
        build_manifest(_args(portfolio_state="output/etf_portfolio_state.json"))


def test_validator_accepts_committed_planning_manifest():
    result = validate(Path("output/run_manifests/etf_eu_routine_run_manifest_2026-07-10_20260710_000000.json"))
    assert result["status"] == "valid"
    assert result["transport_attempted"] is False
    assert result["transport_success"] is False


def test_validator_rejects_authority_promotion(tmp_path):
    source = Path("output/run_manifests/etf_eu_routine_run_manifest_2026-07-10_20260710_000000.json")
    target = tmp_path / "bad.json"
    text = source.read_text(encoding="utf-8").replace('"valuation_grade": false', '"valuation_grade": true')
    target.write_text(text, encoding="utf-8")
    with pytest.raises(AssertionError):
        validate(target)
