import json
from pathlib import Path

import pytest

from tools.validate_etf_eu_receipt_proof_contract_review import (
    validate_receipt_proof_contract_review,
)

SAMPLE_PATH = Path(
    "output/delivery/authority/etf_eu_receipt_proof_contract_review_20260617_000000.json"
)

SAMPLE = {
    "schema_version": "etf_eu_receipt_proof_contract_review_v1",
    "review_id": "20260617_000000",
    "created_at_utc": "2026-06-17T00:00:00Z",
    "status": "receipt_proof_contract_review_completed",
    "review_scope": "receipt_proof_review_only",
    "basis": [
        "WP13E selected WP13F",
        "sample evidence remains non-authoritative",
        "preflight readiness is not authority",
    ],
    "current_receipt_state": {
        "source_path": "output/delivery/etf_eu_delivery_receipt_sample_20260617_000000.json",
        "status": "sample_only_not_delivery_proof",
        "real_receipt": False,
        "delivery_proof": False,
        "production_delivery": False,
    },
    "required_future_production_controls": [
        "future contract",
        "future validator",
        "authority reference",
        "artifact reference",
        "manifest reference",
        "independent evidence rule",
    ],
    "implementation_allowed_in_this_package": False,
    "activation_allowed_in_this_package": False,
    "real_receipt_allowed_in_this_package": False,
    "delivery_proof_allowed_in_this_package": False,
    "authority_created": False,
    "selected_next_package": "WP13G",
    "selected_next_package_title": "delivery authority prerequisite reconciliation, review-only",
    "authority": {
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
        "candidate_promotion": False,
        "real_receipt": False,
        "delivery_proof": False,
        "ready_for_wp13_preflight_only": True,
        "wp13_authority": False,
    },
}


def _copy_sample() -> dict:
    return json.loads(json.dumps(SAMPLE))


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "receipt_proof_review.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def test_valid_receipt_proof_review_artifact_passes_from_repo_file():
    validate_receipt_proof_contract_review(SAMPLE_PATH)


def test_valid_receipt_proof_review_artifact_passes(tmp_path: Path):
    result = validate_receipt_proof_contract_review(_write(tmp_path, SAMPLE))
    assert result["selected_next_package"] == "WP13G"
    assert result["receipt_state"] == "sample_only_not_delivery_proof"
    assert result["real_receipt"] is False
    assert result["delivery_proof"] is False


def test_unsupported_schema_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["schema_version"] = "bad"
    with pytest.raises(RuntimeError, match="unsupported schema_version"):
        validate_receipt_proof_contract_review(_write(tmp_path, payload))


def test_wrong_status_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["status"] = "bad"
    with pytest.raises(RuntimeError, match="status must be receipt_proof_contract_review_completed"):
        validate_receipt_proof_contract_review(_write(tmp_path, payload))


def test_wrong_review_scope_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["review_scope"] = "bad"
    with pytest.raises(RuntimeError, match="review_scope must be receipt_proof_review_only"):
        validate_receipt_proof_contract_review(_write(tmp_path, payload))


def test_empty_basis_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["basis"] = []
    with pytest.raises(RuntimeError, match="basis must be a non-empty list"):
        validate_receipt_proof_contract_review(_write(tmp_path, payload))


def test_missing_current_receipt_state_fails(tmp_path: Path):
    payload = _copy_sample()
    del payload["current_receipt_state"]
    with pytest.raises(RuntimeError, match="missing top-level key"):
        validate_receipt_proof_contract_review(_write(tmp_path, payload))


def test_wrong_current_receipt_status_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["current_receipt_state"]["status"] = "active"
    with pytest.raises(RuntimeError, match="status must be sample_only_not_delivery_proof"):
        validate_receipt_proof_contract_review(_write(tmp_path, payload))


@pytest.mark.parametrize("flag", ["real_receipt", "delivery_proof", "production_delivery"])
def test_current_receipt_state_true_fails(tmp_path: Path, flag: str):
    payload = _copy_sample()
    payload["current_receipt_state"][flag] = True
    with pytest.raises(RuntimeError, match=f"current_receipt_state.{flag} must remain false"):
        validate_receipt_proof_contract_review(_write(tmp_path, payload))


def test_empty_required_future_controls_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["required_future_production_controls"] = []
    with pytest.raises(RuntimeError, match="required_future_production_controls must be a non-empty list"):
        validate_receipt_proof_contract_review(_write(tmp_path, payload))


@pytest.mark.parametrize(
    "flag",
    [
        "implementation_allowed_in_this_package",
        "activation_allowed_in_this_package",
        "real_receipt_allowed_in_this_package",
        "delivery_proof_allowed_in_this_package",
        "authority_created",
    ],
)
def test_top_level_authority_or_activation_flags_true_fail(tmp_path: Path, flag: str):
    payload = _copy_sample()
    payload[flag] = True
    with pytest.raises(RuntimeError, match=f"{flag} must remain false"):
        validate_receipt_proof_contract_review(_write(tmp_path, payload))


def test_wrong_selected_next_package_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["selected_next_package"] = "WP13F"
    with pytest.raises(RuntimeError, match="selected_next_package must be WP13G"):
        validate_receipt_proof_contract_review(_write(tmp_path, payload))


def test_wp13_authority_true_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["authority"]["wp13_authority"] = True
    with pytest.raises(RuntimeError, match="authority.wp13_authority must remain false"):
        validate_receipt_proof_contract_review(_write(tmp_path, payload))


@pytest.mark.parametrize("flag", ["real_receipt", "delivery_proof", "production_delivery"])
def test_authority_receipt_or_delivery_flags_true_fail(tmp_path: Path, flag: str):
    payload = _copy_sample()
    payload["authority"][flag] = True
    with pytest.raises(RuntimeError, match=f"authority.{flag} must remain false"):
        validate_receipt_proof_contract_review(_write(tmp_path, payload))


def test_operational_receipt_wording_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["basis"].append("real receipt created")
    with pytest.raises(RuntimeError, match="operational-receipt-like wording"):
        validate_receipt_proof_contract_review(_write(tmp_path, payload))
