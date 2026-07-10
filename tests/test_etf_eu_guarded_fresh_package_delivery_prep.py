import json
from pathlib import Path

import pytest

from tools.prepare_etf_eu_guarded_fresh_package_delivery import _validate_inputs
from tools.validate_etf_eu_guarded_fresh_package_delivery_prep import validate

CONTRACT = Path("control/ETF_EU_GUARDED_FRESH_PACKAGE_DELIVERY_PREP_CONTRACT_V1.md")
PREP = Path("output/delivery_prep/etf_eu_guarded_fresh_package_delivery_prep_20260710_000000.json")
ROUTINE = Path("output/run_manifests/etf_eu_routine_run_manifest_2026-07-10_20260710_000000.json")


def _valid_payloads():
    package = {
        "source_of_truth_repo": "market-predictions/weekly-etf-eu",
        "reference_architecture_repo": "market-predictions/weekly-etf",
        "ready_for_controlled_delivery": True,
        "delivery_authorized": False,
        "send_executed": False,
        "transport_attempted": False,
        "transport_success": False,
        "receipt_confirmed": False,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
        "dutch_primary_markdown": "output/fresh_generation/weekly_etf_eu_review_nl_260710.md",
        "english_companion_markdown": "output/fresh_generation/weekly_etf_eu_review_260710.md",
        "dutch_primary_html": "output/fresh_generation/weekly_etf_eu_review_nl_260710.html",
        "english_companion_html": "output/fresh_generation/weekly_etf_eu_review_260710.html",
        "dutch_primary_pdf": "output/fresh_generation/weekly_etf_eu_review_nl_260710.pdf",
        "english_companion_pdf": "output/fresh_generation/weekly_etf_eu_review_260710.pdf",
    }
    ready = {
        "ready_for_controlled_delivery": True,
        "delivery_authorized": False,
        "send_executed": False,
        "transport_attempted": False,
        "receipt_confirmed": False,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
    }
    gate = {
        "readiness_gate_passed": True,
        "blockers": [],
        "delivery_authorized": False,
        "send_executed": False,
        "transport_attempted": False,
        "receipt_confirmed": False,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
    }
    routine = {
        "send_executed": False,
        "transport_attempted": False,
        "transport_success": False,
        "receipt_confirmed": False,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
    }
    return package, ready, gate, routine


def test_guarded_delivery_prep_contract_exists():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "explicit_user_authorization_required=true" in text
    assert "send_command_allowed=false" in text
    assert "workflow_dispatch_allowed=false" in text


@pytest.mark.parametrize(
    "payload_name,key,value",
    [
        ("package", "ready_for_controlled_delivery", False),
        ("ready", "delivery_authorized", True),
        ("ready", "send_executed", True),
        ("ready", "transport_attempted", True),
        ("ready", "receipt_confirmed", True),
        ("package", "valuation_grade", True),
        ("package", "funding_authority", True),
        ("package", "portfolio_mutation", True),
        ("package", "production_delivery_authority", True),
    ],
)
def test_builder_refuses_invalid_authority_states(payload_name, key, value):
    package, ready, gate, routine = _valid_payloads()
    payload = {"package": package, "ready": ready, "gate": gate, "routine": routine}[payload_name]
    payload[key] = value
    with pytest.raises(SystemExit):
        _validate_inputs(package, ready, gate, routine)


def test_delivery_prep_artifact_requires_explicit_authorization_and_blocks_send():
    data = json.loads(PREP.read_text(encoding="utf-8"))
    assert data["delivery_prep_created"] is True
    assert data["explicit_user_authorization_required"] is True
    assert data["guarded_send_confirmation_required"] is True
    assert data["send_command_allowed"] is False
    assert data["workflow_dispatch_allowed"] is False
    assert data["run_queue_allowed"] is False
    assert data["delivery_authorized"] is False
    assert data["recipient_plaintext_values_exposed"] is False
    assert data["secret_values_exposed"] is False


def test_validator_accepts_mvp26_delivery_prep_artifact():
    result = validate(PREP)
    assert result["status"] == "valid"
    assert result["ready_for_controlled_delivery"] is True
    assert result["delivery_authorized"] is False


def test_routine_run_manifest_handoff_is_updated():
    data = json.loads(ROUTINE.read_text(encoding="utf-8"))
    assert data["delivery_prep_artifact"] == str(PREP)
    assert data["routine_stage"] == "guarded_fresh_package_delivery_prep_created"
    assert data["transport_attempted"] is False
    assert data["receipt_confirmed"] is False
