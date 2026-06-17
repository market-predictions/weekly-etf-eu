import json
from pathlib import Path

import pytest

from tools.validate_etf_eu_production_prerequisite_gap_review import (
    validate_production_prerequisite_gap_review,
)

SAMPLE_PATH = Path(
    "output/delivery/authority/etf_eu_production_prerequisite_gap_review_20260617_000000.json"
)

SAMPLE = {
    "schema_version": "etf_eu_production_prerequisite_gap_review_v1",
    "review_id": "20260617_000000",
    "created_at_utc": "2026-06-17T00:00:00Z",
    "status": "gap_review_completed",
    "review_scope": "production_prerequisites_review_only",
    "basis": [
        "WP13A review status is not granted",
        "WP13B selected WP13C as the next review-only step",
        "current prerequisite files are sample-only or inactive",
        "preflight readiness is not authority",
    ],
    "gap_domains": [
        {
            "domain": "recipient_policy",
            "current_state": "sample_only_inactive",
            "gap_status": "gap_open",
            "required_future_review": "production recipient policy contract and validator review",
            "implementation_allowed_in_this_package": False,
            "activation_allowed_in_this_package": False,
            "authority_created": False,
        },
        {
            "domain": "secure_transport_setup",
            "current_state": "sample_only_no_live_values",
            "gap_status": "gap_open",
            "required_future_review": "secure transport setup contract and validator review",
            "implementation_allowed_in_this_package": False,
            "activation_allowed_in_this_package": False,
            "authority_created": False,
        },
        {
            "domain": "receipt_proof_path",
            "current_state": "sample_only_not_delivery_proof",
            "gap_status": "gap_open",
            "required_future_review": "receipt proof contract and validator review",
            "implementation_allowed_in_this_package": False,
            "activation_allowed_in_this_package": False,
            "authority_created": False,
        },
    ],
    "recommended_gap_closure_sequence": [
        "WP13D recipient policy contract review-only",
        "WP13E secure transport setup contract review-only",
        "WP13F receipt proof contract review-only",
    ],
    "selected_next_package": "WP13D",
    "selected_next_package_title": "production recipient policy contract review, review-only",
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
    path = tmp_path / "gap_review.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def test_valid_gap_review_artifact_passes_from_repo_file():
    validate_production_prerequisite_gap_review(SAMPLE_PATH)


def test_valid_gap_review_artifact_passes(tmp_path: Path):
    result = validate_production_prerequisite_gap_review(_write(tmp_path, SAMPLE))
    assert result["selected_next_package"] == "WP13D"
    assert result["wp13_authority"] is False
    assert result["production_delivery"] is False


def test_unsupported_schema_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["schema_version"] = "bad"
    with pytest.raises(RuntimeError, match="unsupported schema_version"):
        validate_production_prerequisite_gap_review(_write(tmp_path, payload))


def test_wrong_status_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["status"] = "bad"
    with pytest.raises(RuntimeError, match="status must be gap_review_completed"):
        validate_production_prerequisite_gap_review(_write(tmp_path, payload))


def test_wrong_review_scope_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["review_scope"] = "bad"
    with pytest.raises(RuntimeError, match="review_scope must be production_prerequisites_review_only"):
        validate_production_prerequisite_gap_review(_write(tmp_path, payload))


def test_empty_basis_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["basis"] = []
    with pytest.raises(RuntimeError, match="basis must be a non-empty list"):
        validate_production_prerequisite_gap_review(_write(tmp_path, payload))


def test_missing_gap_domains_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["gap_domains"] = []
    with pytest.raises(RuntimeError, match="gap_domains must be a non-empty list"):
        validate_production_prerequisite_gap_review(_write(tmp_path, payload))


def test_missing_required_domain_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["gap_domains"] = [
        item for item in payload["gap_domains"] if item["domain"] != "recipient_policy"
    ]
    with pytest.raises(RuntimeError, match="missing required gap domain"):
        validate_production_prerequisite_gap_review(_write(tmp_path, payload))


def test_closed_gap_status_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["gap_domains"][0]["gap_status"] = "gap_closed"
    with pytest.raises(RuntimeError, match="gap_status must be gap_open"):
        validate_production_prerequisite_gap_review(_write(tmp_path, payload))


def test_implementation_allowed_true_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["gap_domains"][0]["implementation_allowed_in_this_package"] = True
    with pytest.raises(RuntimeError, match="implementation_allowed_in_this_package must remain false"):
        validate_production_prerequisite_gap_review(_write(tmp_path, payload))


def test_activation_allowed_true_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["gap_domains"][0]["activation_allowed_in_this_package"] = True
    with pytest.raises(RuntimeError, match="activation_allowed_in_this_package must remain false"):
        validate_production_prerequisite_gap_review(_write(tmp_path, payload))


def test_authority_created_true_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["gap_domains"][0]["authority_created"] = True
    with pytest.raises(RuntimeError, match="authority_created must remain false"):
        validate_production_prerequisite_gap_review(_write(tmp_path, payload))


def test_empty_recommended_gap_closure_sequence_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["recommended_gap_closure_sequence"] = []
    with pytest.raises(RuntimeError, match="recommended_gap_closure_sequence must be a non-empty list"):
        validate_production_prerequisite_gap_review(_write(tmp_path, payload))


def test_wrong_selected_next_package_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["selected_next_package"] = "WP13E"
    with pytest.raises(RuntimeError, match="selected_next_package must be WP13D"):
        validate_production_prerequisite_gap_review(_write(tmp_path, payload))


def test_wp13_authority_true_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["authority"]["wp13_authority"] = True
    with pytest.raises(RuntimeError, match="authority.wp13_authority must remain false"):
        validate_production_prerequisite_gap_review(_write(tmp_path, payload))


def test_production_delivery_true_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["authority"]["production_delivery"] = True
    with pytest.raises(RuntimeError, match="authority.production_delivery must remain false"):
        validate_production_prerequisite_gap_review(_write(tmp_path, payload))


def test_funding_authority_true_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["authority"]["funding_authority"] = True
    with pytest.raises(RuntimeError, match="authority.funding_authority must remain false"):
        validate_production_prerequisite_gap_review(_write(tmp_path, payload))


def test_operational_delivery_wording_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["basis"].append("production delivery enabled")
    with pytest.raises(RuntimeError, match="operational-delivery-like wording"):
        validate_production_prerequisite_gap_review(_write(tmp_path, payload))
