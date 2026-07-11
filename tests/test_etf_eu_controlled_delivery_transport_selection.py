from __future__ import annotations

import json
from pathlib import Path


def _load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_mvp28b_contract_exists() -> None:
    text = Path("control/ETF_EU_CONTROLLED_DELIVERY_TRANSPORT_SELECTION_CONTRACT_V1.md").read_text(encoding="utf-8")
    assert "MVP28B is not another authorization package" in text
    assert "Queue compatibility rule" in text
    assert "blocked_missing_eu_delivery_workflow_wiring" in text


def test_mvp28b_selection_artifact_records_workflow_wiring_gap() -> None:
    artifact = _load("output/delivery_control/etf_eu_controlled_delivery_transport_selection_20260710_000000.json")
    assert artifact["schema_version"] == "etf_eu_controlled_delivery_transport_selection_v1"
    assert artifact["artifact_type"] == "etf_eu_controlled_delivery_transport_selection"
    assert artifact["transport_selection_status"] == "blocked_missing_eu_delivery_workflow_wiring"
    assert artifact["selected_transport_mode"] == "none"
    assert artifact["next_package"] == "ETF-EU-MVP28C_EU_DELIVERY_WORKFLOW_WIRING"


def test_mvp28b_selection_preserves_no_delivery_activity() -> None:
    artifact = _load("output/delivery_control/etf_eu_controlled_delivery_transport_selection_20260710_000000.json")
    assert artifact["delivery_authorized"] is True
    assert artifact["send_command_allowed"] is True
    assert artifact["run_queue_created"] is False
    assert artifact["run_queue_allowed"] is False
    assert artifact["workflow_dispatch_allowed"] is False
    assert artifact["transport_execution_allowed"] is False
    assert artifact["transport_attempted"] is False
    assert artifact["receipt_confirmed"] is False


def test_routine_manifest_handoff_points_to_mvp28c() -> None:
    routine = _load("output/run_manifests/etf_eu_routine_run_manifest_2026-07-10_20260710_000000.json")
    assert routine["controlled_delivery_transport_selection_artifact"] == "output/delivery_control/etf_eu_controlled_delivery_transport_selection_20260710_000000.json"
    assert routine["transport_selection_status"] == "blocked_missing_eu_delivery_workflow_wiring"
    assert routine["next_package"] == "ETF-EU-MVP28C_EU_DELIVERY_WORKFLOW_WIRING"
