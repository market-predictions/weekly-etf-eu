from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_mvp11_workflow_dry_run_verification_with_integrated_evidence_gate import (
    ARTIFACT,
    CONTRACT,
    NOTES,
    validate,
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_expected_files_exist() -> None:
    assert CONTRACT.exists()
    assert ARTIFACT.exists()
    assert NOTES.exists()


def test_artifact_identity_and_run_evidence() -> None:
    data = _artifact()
    assert data["work_package_id"] == "ETF-EU-MVP11"
    assert data["source_work_package"] == "ETF-EU-MVP10"
    assert data["workflow_run_id"] == "28963021481"
    assert data["workflow_status"] == "completed"
    assert data["workflow_conclusion"] == "success"
    assert data["run_mode"] == "dry_run"
    assert data["gate_passed"] is True


def test_next_package_is_mvp12() -> None:
    data = _artifact()
    assert data["selected_next_package"] == "ETF-EU-MVP12"
    assert not data["selected_next_package"].startswith("ETF-EU-WP15")
    assert data["selected_next_package"] != "OPERATOR_ACTION_REQUIRED"


def test_validator_passes() -> None:
    result = validate()
    assert result["status"] == "valid"
    assert result["work_package_id"] == "ETF-EU-MVP11"
    assert result["workflow_run_id"] == "28963021481"
    assert result["workflow_conclusion"] == "success"
    assert result["run_mode"] == "dry_run"
    assert result["gate_passed"] is True
    assert result["selected_next_package"] == "ETF-EU-MVP12"
