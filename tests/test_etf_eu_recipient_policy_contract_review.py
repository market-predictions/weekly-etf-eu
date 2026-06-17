import json
from pathlib import Path

import pytest

from tools.validate_etf_eu_recipient_policy_contract_review import (
    validate_recipient_policy_contract_review,
)

SAMPLE_PATH = Path(
    "output/delivery/authority/etf_eu_recipient_policy_contract_review_20260617_000000.json"
)

SAMPLE = {
    "schema_version": "etf_eu_recipient_policy_contract_review_v1",
    "review_id": "20260617_000000",
    "created_at_utc": "2026-06-17T00:00:00Z",
    "status": "recipient_policy_contract_review_completed",
    "review_scope": "recipient_policy_review_only",
    "basis": [
        "WP13C selected WP13D as the next review-only step",
        "recipient policy gap remains open",
        "current recipient allowlist is sample-only and inactive",
        "preflight readiness is not authority",
    ],
    "current_recipient_policy_state": {
        "source_path": "config/etf_eu_recipient_allowlist.sample.yml",
        "status": "sample_only_inactive",
        "recipient_activation": False,
        "real_recipients": False,
        "production_policy_exists": False,
    },
    "required_future_production_controls": [
        "production recipient policy contract",
        "production recipient validator",
        "recipient owner or approver field",
        "recipient role classification",
        "approval evidence reference",
        "recipient activation decision artifact",
        "scope per recipient",
        "deactivation procedure",
        "audit evidence for any future activation",
    ],
    "future_policy_required_fields": [
        "schema_version",
        "status",
        "recipient_activation",
        "real_recipients",
        "production_policy",
        "recipients",
        "approval_reference",
        "deactivation_runbook",
        "authority_reference",
    ],
    "implementation_allowed_in_this_package": False,
    "activation_allowed_in_this_package": False,
    "authority_created": False,
    "selected_next_package": "WP13E",
    "selected_next_package_title": "secure transport setup contract review, review-only",
    "explicitly_out_of_scope": [
        "review-only package",
        "no authority change",
        "no activation step",
        "no recipient state change",
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
        "recipient_activation": False,
        "real_recipients": False,
        "ready_for_wp13_preflight_only": True,
        "wp13_authority": False,
    },
}


def _copy_sample() -> dict:
    return json.loads(json.dumps(SAMPLE))


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "recipient_policy_review.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def test_valid_recipient_policy_review_artifact_passes_from_repo_file():
    validate_recipient_policy_contract_review(SAMPLE_PATH)


def test_valid_recipient_policy_review_artifact_passes(tmp_path: Path):
    result = validate_recipient_policy_contract_review(_write(tmp_path, SAMPLE))
    assert result["selected_next_package"] == "WP13E"
    assert result["recipient_policy_state"] == "sample_only_inactive"
    assert result["recipient_activation"] is False
    assert result["real_recipients"] is False


def test_unsupported_schema_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["schema_version"] = "bad"
    with pytest.raises(RuntimeError, match="unsupported schema_version"):
        validate_recipient_policy_contract_review(_write(tmp_path, payload))


def test_wrong_status_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["status"] = "bad"
    with pytest.raises(RuntimeError, match="status must be recipient_policy_contract_review_completed"):
        validate_recipient_policy_contract_review(_write(tmp_path, payload))


def test_wrong_review_scope_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["review_scope"] = "bad"
    with pytest.raises(RuntimeError, match="review_scope must be recipient_policy_review_only"):
        validate_recipient_policy_contract_review(_write(tmp_path, payload))


def test_empty_basis_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["basis"] = []
    with pytest.raises(RuntimeError, match="basis must be a non-empty list"):
        validate_recipient_policy_contract_review(_write(tmp_path, payload))


def test_missing_current_recipient_policy_state_fails(tmp_path: Path):
    payload = _copy_sample()
    del payload["current_recipient_policy_state"]
    with pytest.raises(RuntimeError, match="missing top-level key"):
        validate_recipient_policy_contract_review(_write(tmp_path, payload))


def test_wrong_current_recipient_status_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["current_recipient_policy_state"]["status"] = "active"
    with pytest.raises(RuntimeError, match="status must be sample_only_inactive"):
        validate_recipient_policy_contract_review(_write(tmp_path, payload))


def test_current_state_recipient_activation_true_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["current_recipient_policy_state"]["recipient_activation"] = True
    with pytest.raises(RuntimeError, match="recipient_activation must remain false"):
        validate_recipient_policy_contract_review(_write(tmp_path, payload))


def test_current_state_real_recipients_true_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["current_recipient_policy_state"]["real_recipients"] = True
    with pytest.raises(RuntimeError, match="real_recipients must remain false"):
        validate_recipient_policy_contract_review(_write(tmp_path, payload))


def test_current_state_production_policy_exists_true_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["current_recipient_policy_state"]["production_policy_exists"] = True
    with pytest.raises(RuntimeError, match="production_policy_exists must remain false"):
        validate_recipient_policy_contract_review(_write(tmp_path, payload))


def test_empty_required_future_controls_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["required_future_production_controls"] = []
    with pytest.raises(RuntimeError, match="required_future_production_controls must be a non-empty list"):
        validate_recipient_policy_contract_review(_write(tmp_path, payload))


def test_empty_future_required_fields_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["future_policy_required_fields"] = []
    with pytest.raises(RuntimeError, match="future_policy_required_fields must be a non-empty list"):
        validate_recipient_policy_contract_review(_write(tmp_path, payload))


def test_implementation_allowed_true_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["implementation_allowed_in_this_package"] = True
    with pytest.raises(RuntimeError, match="implementation_allowed_in_this_package must remain false"):
        validate_recipient_policy_contract_review(_write(tmp_path, payload))


def test_activation_allowed_true_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["activation_allowed_in_this_package"] = True
    with pytest.raises(RuntimeError, match="activation_allowed_in_this_package must remain false"):
        validate_recipient_policy_contract_review(_write(tmp_path, payload))


def test_authority_created_true_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["authority_created"] = True
    with pytest.raises(RuntimeError, match="authority_created must remain false"):
        validate_recipient_policy_contract_review(_write(tmp_path, payload))


def test_wrong_selected_next_package_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["selected_next_package"] = "WP13D"
    with pytest.raises(RuntimeError, match="selected_next_package must be WP13E"):
        validate_recipient_policy_contract_review(_write(tmp_path, payload))


def test_wp13_authority_true_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["authority"]["wp13_authority"] = True
    with pytest.raises(RuntimeError, match="authority.wp13_authority must remain false"):
        validate_recipient_policy_contract_review(_write(tmp_path, payload))


def test_authority_recipient_activation_true_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["authority"]["recipient_activation"] = True
    with pytest.raises(RuntimeError, match="authority.recipient_activation must remain false"):
        validate_recipient_policy_contract_review(_write(tmp_path, payload))


def test_authority_real_recipients_true_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["authority"]["real_recipients"] = True
    with pytest.raises(RuntimeError, match="authority.real_recipients must remain false"):
        validate_recipient_policy_contract_review(_write(tmp_path, payload))


def test_operational_recipient_wording_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["basis"].append("recipient activation enabled")
    with pytest.raises(RuntimeError, match="operational-recipient-like wording"):
        validate_recipient_policy_contract_review(_write(tmp_path, payload))
