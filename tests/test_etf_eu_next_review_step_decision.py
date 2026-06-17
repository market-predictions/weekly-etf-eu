import json
from pathlib import Path

import pytest

from tools.validate_etf_eu_next_review_step_decision import validate_next_review_step_decision

SAMPLE_PATH = Path("output/delivery/authority/etf_eu_next_review_step_decision_20260617_000000.json")

SAMPLE = {
    "schema_version": "etf_eu_next_review_step_decision_v1",
    "decision_id": "20260617_000000",
    "created_at_utc": "2026-06-17T00:00:00Z",
    "status": "next_review_step_selected",
    "selected_next_package": "WP13C",
    "selected_next_package_title": "production prerequisite gap review, review-only",
    "basis": [
        "WP13A review is closed",
        "review status is not granted",
        "preflight readiness is not authority",
        "current prerequisite files remain sample-only or inactive",
    ],
    "next_package_scope": [
        "review recipient policy requirements",
        "review secure transport setup requirements",
        "review receipt proof requirements",
        "define gap closure sequence",
    ],
    "explicitly_out_of_scope": [
        "review-only package",
        "no authority change",
        "no activation step",
        "no production state change",
        "no portfolio state change",
        "no candidate state change",
    ],
    "authority": {
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
        "candidate_promotion": False,
        "ready_for_wp13_preflight_only": True,
        "wp13_authority": False,
    },
}


def _copy_sample() -> dict:
    return json.loads(json.dumps(SAMPLE))


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "next_review_step.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def test_valid_decision_artifact_passes_from_repo_file():
    validate_next_review_step_decision(SAMPLE_PATH)


def test_valid_decision_artifact_passes(tmp_path: Path):
    result = validate_next_review_step_decision(_write(tmp_path, SAMPLE))
    assert result["selected_next_package"] == "WP13C"
    assert result["wp13_authority"] is False


def test_unsupported_schema_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["schema_version"] = "bad"
    with pytest.raises(RuntimeError, match="unsupported schema_version"):
        validate_next_review_step_decision(_write(tmp_path, payload))


def test_wrong_status_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["status"] = "wrong"
    with pytest.raises(RuntimeError, match="status must be next_review_step_selected"):
        validate_next_review_step_decision(_write(tmp_path, payload))


def test_missing_selected_next_package_fails(tmp_path: Path):
    payload = _copy_sample()
    del payload["selected_next_package"]
    with pytest.raises(RuntimeError, match="missing top-level key"):
        validate_next_review_step_decision(_write(tmp_path, payload))


def test_wrong_selected_next_package_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["selected_next_package"] = "WP13D"
    with pytest.raises(RuntimeError, match="selected_next_package must be WP13C"):
        validate_next_review_step_decision(_write(tmp_path, payload))


def test_empty_basis_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["basis"] = []
    with pytest.raises(RuntimeError, match="basis must be a non-empty list"):
        validate_next_review_step_decision(_write(tmp_path, payload))


def test_empty_next_package_scope_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["next_package_scope"] = []
    with pytest.raises(RuntimeError, match="next_package_scope must be a non-empty list"):
        validate_next_review_step_decision(_write(tmp_path, payload))


def test_empty_out_of_scope_list_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["explicitly_out_of_scope"] = []
    with pytest.raises(RuntimeError, match="explicitly_out_of_scope must be a non-empty list"):
        validate_next_review_step_decision(_write(tmp_path, payload))


def test_wp13_authority_true_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["authority"]["wp13_authority"] = True
    with pytest.raises(RuntimeError, match="authority.wp13_authority must remain false"):
        validate_next_review_step_decision(_write(tmp_path, payload))


def test_production_delivery_true_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["authority"]["production_delivery"] = True
    with pytest.raises(RuntimeError, match="authority.production_delivery must remain false"):
        validate_next_review_step_decision(_write(tmp_path, payload))


def test_funding_authority_true_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["authority"]["funding_authority"] = True
    with pytest.raises(RuntimeError, match="authority.funding_authority must remain false"):
        validate_next_review_step_decision(_write(tmp_path, payload))


def test_operational_delivery_wording_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["basis"].append("production delivery enabled")
    with pytest.raises(RuntimeError, match="operational-delivery-like wording"):
        validate_next_review_step_decision(_write(tmp_path, payload))
