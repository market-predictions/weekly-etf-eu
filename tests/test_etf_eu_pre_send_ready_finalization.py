import json
from pathlib import Path

import pytest

from tools.finalize_etf_eu_pre_send_ready import finalize_pre_send_ready


def _write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _fixtures(tmp_path: Path):
    run_id = "20260918_900128"
    report_date = "2026-09-18"
    common = {
        "run_id": run_id,
        "report_date": report_date,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
        "send_executed": False,
        "transport_attempted": False,
    }
    package = tmp_path / "package.json"
    ready = tmp_path / "ready.json"
    routine = tmp_path / "routine.json"
    strict = tmp_path / "strict.json"
    machine = tmp_path / "machine.json"
    _write(package, {**common, "ready_for_controlled_delivery": False, "delivery_authorized": False})
    _write(ready, {**common, "ready_for_controlled_delivery": False, "delivery_authorized": False})
    _write(routine, {**common, "workflow_conclusion": None})
    _write(
        strict,
        {
            "run_id": run_id,
            "report_date": report_date,
            "client_grade_v2_passed": True,
            "funded_state_consistency_passed": True,
            "blockers": [],
            "dutch": {"passed": True, "blockers": []},
            "english": {"passed": True, "blockers": []},
        },
    )
    _write(
        machine,
        {
            "source_run_id": run_id,
            "pdf_client_grade_passed": True,
            "client_surface_clean": True,
            "authority_metadata_absent": True,
            "raw_status_enums_absent": True,
            "blockers": [],
        },
    )
    return package, ready, routine, strict, machine


def test_finalizes_machine_validated_generation_without_granting_delivery_authority(tmp_path):
    paths = _fixtures(tmp_path)
    finalize_pre_send_ready(*paths)

    package = json.loads(paths[0].read_text(encoding="utf-8"))
    ready = json.loads(paths[1].read_text(encoding="utf-8"))
    routine = json.loads(paths[2].read_text(encoding="utf-8"))

    for payload in (package, ready, routine):
        assert payload["pre_send_ready"] is True
        assert payload["full_generation_status"] == "PRE_SEND_READY"
        assert payload["funding_authority"] is False
        assert payload["portfolio_mutation"] is False
        assert payload["production_delivery_authority"] is False
        assert payload["send_executed"] is False
        assert payload["transport_attempted"] is False

    assert ready["ready_for_controlled_delivery"] is False
    assert ready["delivery_authorized"] is False
    assert ready["next_action"] == "INDEPENDENT_RELEASE_ASSURANCE"
    assert routine["workflow_status"] == "PRE_SEND_READY"
    assert routine["workflow_conclusion"] == "PASS"
    assert routine["next_package"] == "INDEPENDENT_RELEASE_ASSURANCE"


def test_refuses_failed_quality_gate_without_mutating_current_truth(tmp_path):
    paths = _fixtures(tmp_path)
    strict = json.loads(paths[3].read_text(encoding="utf-8"))
    strict["client_grade_v2_passed"] = False
    strict["blockers"] = ["synthetic_failure"]
    _write(paths[3], strict)
    before = [path.read_text(encoding="utf-8") for path in paths[:3]]

    with pytest.raises(ValueError, match="PRE_SEND_READY_STRICT_GATE_FAILED"):
        finalize_pre_send_ready(*paths)

    assert [path.read_text(encoding="utf-8") for path in paths[:3]] == before


def test_refuses_unsafe_authority_state(tmp_path):
    paths = _fixtures(tmp_path)
    ready = json.loads(paths[1].read_text(encoding="utf-8"))
    ready["send_executed"] = True
    _write(paths[1], ready)

    with pytest.raises(ValueError, match="PRE_SEND_READY_UNSAFE_SEND_EXECUTED:ready"):
        finalize_pre_send_ready(*paths)
