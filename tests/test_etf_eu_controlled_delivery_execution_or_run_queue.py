from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

DECISION = Path("output/delivery_control/etf_eu_controlled_delivery_decision_20260710_000000.json")
CONTRACT = Path("control/ETF_EU_CONTROLLED_DELIVERY_EXECUTION_OR_RUN_QUEUE_CONTRACT_V1.md")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_controlled_delivery_contract_exists() -> None:
    assert CONTRACT.exists()
    assert "blocked_no_transport_selected" in CONTRACT.read_text(encoding="utf-8")


def test_decision_only_artifact_keeps_transport_flags_false() -> None:
    data = read_json(DECISION)
    assert data["controlled_delivery_decision_status"] == "blocked_no_transport_selected"
    assert data["delivery_authorized"] is True
    assert data["send_command_allowed"] is True
    assert data["workflow_dispatch_allowed"] is False
    assert data["run_queue_allowed"] is False
    assert data["run_queue_created"] is False
    assert data["transport_execution_allowed"] is False
    assert data["send_executed"] is False
    assert data["transport_attempted"] is False
    assert data["transport_success"] is False
    assert data["receipt_confirmed"] is False


def test_decision_artifact_redaction_and_secret_boundaries() -> None:
    data = read_json(DECISION)
    assert data["recipient_plaintext_values_exposed"] is False
    assert data["secret_values_exposed"] is False
    assert data["raw_receipt_pdf_stored_in_github"] is False


def test_validator_accepts_committed_decision() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/validate_etf_eu_controlled_delivery_execution_or_run_queue.py",
            "--decision",
            str(DECISION),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "ETF_EU_CONTROLLED_DELIVERY_DECISION_VALID" in result.stdout
