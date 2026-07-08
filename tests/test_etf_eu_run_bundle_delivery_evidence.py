from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_etf_eu_run_bundle_delivery_evidence import validate
from tests.test_etf_eu_delivery_evidence_validator import _write_fixture


def _run_bundle_fixture(tmp_path: Path, evidence_path: Path, **updates: object) -> Path:
    payload = {
        "schema_version": "etf_eu_run_bundle_delivery_evidence_fixture_v1",
        "run_id": "20260708_000000",
        "delivery_evidence_path": str(evidence_path),
        "controlled_send_preflight_manifest": "output/delivery/etf_eu_controlled_send_preflight_manifest_20260708_000000.json",
        "delivery_evidence_status": "not_attempted",
        "delivery_success": False,
        "production_delivery": False,
        "email_delivery": False,
        "delivery_receipt": False,
        "workflow_guard_present": True,
        "workflow_guard_removed": False,
        "delivery_mode_send_unlocked": False,
    }
    payload.update(updates)
    path = tmp_path / "run_bundle_fixture.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_run_bundle_delivery_evidence_fixture_validates(tmp_path: Path) -> None:
    evidence_path = _write_fixture(tmp_path)
    fixture_path = _run_bundle_fixture(tmp_path, evidence_path)
    result = validate(fixture_path)
    assert result["status"] == "valid"
    assert result["delivery_evidence_status"] == "not_attempted"
    assert result["delivery_success"] is False
    assert result["workflow_guard_present"] is True
    assert result["workflow_guard_removed"] is False
    assert result["delivery_mode_send_unlocked"] is False


def test_run_bundle_validator_rejects_success_for_not_attempted(tmp_path: Path) -> None:
    evidence_path = _write_fixture(tmp_path)
    fixture_path = _run_bundle_fixture(tmp_path, evidence_path, delivery_success=True)
    with pytest.raises(AssertionError, match="success"):
        validate(fixture_path)


def test_run_bundle_validator_rejects_removed_guard(tmp_path: Path) -> None:
    evidence_path = _write_fixture(tmp_path)
    fixture_path = _run_bundle_fixture(tmp_path, evidence_path, workflow_guard_removed=True)
    with pytest.raises(AssertionError, match="workflow_guard_removed"):
        validate(fixture_path)
