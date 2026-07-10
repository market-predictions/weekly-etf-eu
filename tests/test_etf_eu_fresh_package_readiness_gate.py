import json
from pathlib import Path

import pytest

from tools.validate_etf_eu_fresh_package_readiness_gate import evaluate

MANIFEST = Path("output/fresh_generation/etf_eu_fresh_generation_package_manifest_20260710_000000.json")
READY = Path("output/fresh_generation/etf_eu_ready_for_controlled_delivery_20260710_000000.json")
ROUTINE = Path("output/run_manifests/etf_eu_routine_run_manifest_2026-07-10_20260710_000000.json")
GATE = Path("output/fresh_generation/etf_eu_fresh_package_readiness_gate_20260710_000000.json")
CONTRACT = Path("control/ETF_EU_FRESH_PACKAGE_READINESS_GATE_CONTRACT_V1.md")


def test_package_readiness_contract_exists_and_documents_non_delivery():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "ETF_EU_FRESH_PACKAGE_READINESS_GATE_CONTRACT_V1" in text
    assert "ready_for_controlled_delivery=true" in text
    assert "delivery_authorized=true" in text
    assert "send_executed=true" in text
    assert "not delivery authorization" in text


def test_gate_artifact_passes_and_has_no_blockers():
    data = json.loads(GATE.read_text(encoding="utf-8"))
    assert data["readiness_gate_passed"] is True
    assert data["ready_for_controlled_delivery"] is True
    assert data["blockers"] == []
    assert data["delivery_authorized"] is False
    assert data["send_executed"] is False
    assert data["transport_attempted"] is False


def test_ready_artifact_is_not_send_authorization():
    data = json.loads(READY.read_text(encoding="utf-8"))
    assert data["ready_for_controlled_delivery"] is True
    assert data["delivery_authorized"] is False
    assert data["send_executed"] is False
    assert data["transport_attempted"] is False
    assert data["receipt_confirmed"] is False


def test_manifest_records_gate_and_preserves_authority_boundaries():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert data["package_readiness_gate"] == str(GATE)
    assert data["ready_for_controlled_delivery"] is True
    assert data["delivery_authorized"] is False
    assert data["send_executed"] is False
    assert data["transport_attempted"] is False
    assert data["receipt_confirmed"] is False
    assert data["valuation_grade"] is False
    assert data["funding_authority"] is False
    assert data["portfolio_mutation"] is False
    assert data["production_delivery_authority"] is False


def test_routine_run_manifest_handoff_is_updated():
    data = json.loads(ROUTINE.read_text(encoding="utf-8"))
    assert data["routine_stage"] == "fresh_package_readiness_gate_passed"
    assert data["workflow_status"] == "fresh_package_readiness_gate_passed"
    assert data["package_readiness_gate"] == str(GATE)
    assert data["ready_for_controlled_delivery"] is True
    assert data["transport_attempted"] is False
    assert data["transport_success"] is False
    assert data["receipt_confirmed"] is False


def test_evaluator_accepts_current_package_gate():
    gate, *_ = evaluate(MANIFEST, READY, ROUTINE)
    assert gate["readiness_gate_passed"] is True
    assert gate["markdown_gate_passed"] is True
    assert gate["html_gate_passed"] is True
    assert gate["pdf_gate_passed"] is True
    assert gate["authority_gate_passed"] is True


def test_evaluator_rejects_missing_markdown(tmp_path):
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["dutch_primary_markdown"] = "output/fresh_generation/missing.md"
    candidate = tmp_path / "manifest.json"
    candidate.write_text(json.dumps(manifest), encoding="utf-8")
    gate, *_ = evaluate(candidate, READY, ROUTINE)
    assert gate["readiness_gate_passed"] is False
    assert any("dutch_primary_markdown_not_found" in blocker for blocker in gate["blockers"])


def test_evaluator_rejects_send_or_transport_promotion(tmp_path):
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["send_executed"] = True
    manifest["transport_attempted"] = True
    candidate = tmp_path / "manifest.json"
    candidate.write_text(json.dumps(manifest), encoding="utf-8")
    gate, *_ = evaluate(candidate, READY, ROUTINE)
    assert gate["readiness_gate_passed"] is False
    assert "manifest_send_executed_must_be_false" in gate["blockers"]
    assert "manifest_transport_attempted_must_be_false" in gate["blockers"]


def test_evaluator_rejects_us_state_authority(tmp_path):
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["portfolio_state_path"] = "output/etf_portfolio_state.json"
    candidate = tmp_path / "manifest.json"
    candidate.write_text(json.dumps(manifest), encoding="utf-8")
    gate, *_ = evaluate(candidate, READY, ROUTINE)
    assert gate["readiness_gate_passed"] is False
    assert any("portfolio_state_path" in blocker for blocker in gate["blockers"])
