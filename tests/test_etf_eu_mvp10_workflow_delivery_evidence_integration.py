from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_mvp10_workflow_delivery_evidence_integration import GATE_NAME, RUN_BUNDLE_STEP, WORKFLOW, validate


def _workflow_text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def test_workflow_file_exists() -> None:
    assert WORKFLOW.exists()


def test_send_guard_remains_present_and_blocking() -> None:
    text = _workflow_text()
    assert "ETF_EU_SEND_MODE_REQUESTED" in text
    guard_index = text.index("Guard EU send mode until sender entrypoint is promoted")
    assert "exit 1" in text[guard_index:text.index("Validate EU control files exist")]


def test_delivery_mode_choices_are_unchanged() -> None:
    text = _workflow_text()
    for mode in ["validate_only", "dry_run", "send"]:
        assert f"          - {mode}" in text


def test_mvp10_evidence_gate_exists_after_run_bundle() -> None:
    text = _workflow_text()
    assert GATE_NAME in text
    assert text.index(GATE_NAME) > text.index(RUN_BUNDLE_STEP)


def test_mvp10_evidence_gate_calls_required_validators() -> None:
    text = _workflow_text()
    gate = text[text.index(GATE_NAME):text.index("Commit EU bootstrap report and pricing artifacts")]
    assert "tools/validate_etf_eu_delivery_evidence.py" in gate
    assert "tools/validate_etf_eu_run_bundle_delivery_evidence.py" in gate
    assert "tools/validate_etf_eu_mvp09_controlled_send_implementation_with_delivery_evidence.py" in gate


def test_existing_core_workflow_steps_remain_present() -> None:
    text = _workflow_text()
    assert "Build and validate blocked delivery manifest" in text
    assert "Build and validate run bundle manifest" in text
    assert "Validate inherited US production sender is disabled" in text
    assert "DISABLED_INHERITED_US_ETF_SEND_WORKFLOW" in text


def test_workflow_integration_validator_passes() -> None:
    result = validate()
    assert result["status"] == "valid"
    assert result["workflow_send_guard_present"] is True
    assert result["workflow_send_guard_removed"] is False
    assert result["workflow_send_guard_exit_present"] is True
    assert result["delivery_evidence_gate_added"] is True
    assert result["delivery_evidence_gate_after_run_bundle"] is True
    assert result["delivery_evidence_validator_called"] is True
    assert result["run_bundle_delivery_evidence_validator_called"] is True
    assert result["mvp09_package_validator_called"] is True
