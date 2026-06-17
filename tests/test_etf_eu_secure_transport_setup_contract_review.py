import json
from pathlib import Path

import pytest

from tools.validate_etf_eu_secure_transport_setup_contract_review import (
    validate_secure_transport_setup_contract_review,
)

SAMPLE_PATH = Path(
    "output/delivery/authority/etf_eu_secure_transport_setup_contract_review_20260617_000000.json"
)

SAMPLE = {
    "schema_version": "etf_eu_secure_transport_setup_contract_review_v1",
    "review_id": "20260617_000000",
    "created_at_utc": "2026-06-17T00:00:00Z",
    "status": "secure_transport_setup_contract_review_completed",
    "review_scope": "secure_transport_setup_review_only",
    "basis": [
        "WP13D selected WP13E as the next review-only step",
        "secure transport setup gap remains open",
        "current transport policy is sample-only and contains no live values",
        "preflight readiness is not authority",
    ],
    "current_transport_state": {
        "source_path": "config/etf_eu_smtp_secrets_policy.sample.yml",
        "status": "sample_only_no_secrets",
        "smtp_configured": False,
        "secrets_present": False,
        "mail_transport_enabled": False,
        "external_mail_api_enabled": False,
        "production_transport_exists": False,
    },
    "required_future_production_controls": [
        "production transport policy contract",
        "production transport validator",
        "non-repo credential storage policy",
        "named credential reference convention",
        "transport provider classification",
        "secure connection requirements",
        "send authorization reference",
        "dry-run versus future live separation",
        "timeout and retry policy",
        "receipt correlation requirements",
        "transport disable or rollback runbook",
        "audit evidence for any future activation",
    ],
    "future_policy_required_fields": [
        "schema_version",
        "status",
        "smtp_configured",
        "secrets_present",
        "mail_transport_enabled",
        "external_mail_api_enabled",
        "credential_storage_policy",
        "transport_policy",
        "send_authority_reference",
        "receipt_correlation_policy",
        "disable_runbook",
        "authority_reference",
    ],
    "implementation_allowed_in_this_package": False,
    "activation_allowed_in_this_package": False,
    "secrets_allowed_in_repo": False,
    "live_transport_values_allowed": False,
    "authority_created": False,
    "selected_next_package": "WP13F",
    "selected_next_package_title": "receipt proof contract review, review-only",
    "explicitly_out_of_scope": [
        "review-only package",
        "no authority change",
        "no activation step",
        "no transport state change",
        "no credential state change",
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
        "smtp_configured": False,
        "secrets_present": False,
        "mail_transport_enabled": False,
        "external_mail_api_enabled": False,
        "ready_for_wp13_preflight_only": True,
        "wp13_authority": False,
    },
}


def _copy_sample() -> dict:
    return json.loads(json.dumps(SAMPLE))


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "secure_transport_review.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def test_valid_secure_transport_review_artifact_passes_from_repo_file():
    validate_secure_transport_setup_contract_review(SAMPLE_PATH)


def test_valid_secure_transport_review_artifact_passes(tmp_path: Path):
    result = validate_secure_transport_setup_contract_review(_write(tmp_path, SAMPLE))
    assert result["selected_next_package"] == "WP13F"
    assert result["transport_state"] == "sample_only_no_secrets"
    assert result["smtp_configured"] is False
    assert result["secrets_present"] is False


def test_unsupported_schema_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["schema_version"] = "bad"
    with pytest.raises(RuntimeError, match="unsupported schema_version"):
        validate_secure_transport_setup_contract_review(_write(tmp_path, payload))


def test_wrong_status_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["status"] = "bad"
    with pytest.raises(RuntimeError, match="status must be secure_transport_setup_contract_review_completed"):
        validate_secure_transport_setup_contract_review(_write(tmp_path, payload))


def test_wrong_review_scope_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["review_scope"] = "bad"
    with pytest.raises(RuntimeError, match="review_scope must be secure_transport_setup_review_only"):
        validate_secure_transport_setup_contract_review(_write(tmp_path, payload))


def test_empty_basis_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["basis"] = []
    with pytest.raises(RuntimeError, match="basis must be a non-empty list"):
        validate_secure_transport_setup_contract_review(_write(tmp_path, payload))


def test_missing_current_transport_state_fails(tmp_path: Path):
    payload = _copy_sample()
    del payload["current_transport_state"]
    with pytest.raises(RuntimeError, match="missing top-level key"):
        validate_secure_transport_setup_contract_review(_write(tmp_path, payload))


def test_wrong_current_transport_status_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["current_transport_state"]["status"] = "active"
    with pytest.raises(RuntimeError, match="status must be sample_only_no_secrets"):
        validate_secure_transport_setup_contract_review(_write(tmp_path, payload))


@pytest.mark.parametrize(
    "flag",
    [
        "smtp_configured",
        "secrets_present",
        "mail_transport_enabled",
        "external_mail_api_enabled",
        "production_transport_exists",
    ],
)
def test_current_transport_state_true_fails(tmp_path: Path, flag: str):
    payload = _copy_sample()
    payload["current_transport_state"][flag] = True
    with pytest.raises(RuntimeError, match=f"current_transport_state.{flag} must remain false"):
        validate_secure_transport_setup_contract_review(_write(tmp_path, payload))


def test_empty_required_future_controls_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["required_future_production_controls"] = []
    with pytest.raises(RuntimeError, match="required_future_production_controls must be a non-empty list"):
        validate_secure_transport_setup_contract_review(_write(tmp_path, payload))


def test_empty_future_required_fields_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["future_policy_required_fields"] = []
    with pytest.raises(RuntimeError, match="future_policy_required_fields must be a non-empty list"):
        validate_secure_transport_setup_contract_review(_write(tmp_path, payload))


@pytest.mark.parametrize(
    "flag",
    [
        "implementation_allowed_in_this_package",
        "activation_allowed_in_this_package",
        "secrets_allowed_in_repo",
        "live_transport_values_allowed",
        "authority_created",
    ],
)
def test_top_level_authority_or_activation_flags_true_fail(tmp_path: Path, flag: str):
    payload = _copy_sample()
    payload[flag] = True
    with pytest.raises(RuntimeError, match=f"{flag} must remain false"):
        validate_secure_transport_setup_contract_review(_write(tmp_path, payload))


def test_wrong_selected_next_package_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["selected_next_package"] = "WP13E"
    with pytest.raises(RuntimeError, match="selected_next_package must be WP13F"):
        validate_secure_transport_setup_contract_review(_write(tmp_path, payload))


def test_wp13_authority_true_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["authority"]["wp13_authority"] = True
    with pytest.raises(RuntimeError, match="authority.wp13_authority must remain false"):
        validate_secure_transport_setup_contract_review(_write(tmp_path, payload))


@pytest.mark.parametrize(
    "flag",
    [
        "mail_transport_enabled",
        "external_mail_api_enabled",
        "secrets_present",
        "smtp_configured",
    ],
)
def test_authority_transport_or_secret_flags_true_fail(tmp_path: Path, flag: str):
    payload = _copy_sample()
    payload["authority"][flag] = True
    with pytest.raises(RuntimeError, match=f"authority.{flag} must remain false"):
        validate_secure_transport_setup_contract_review(_write(tmp_path, payload))


def test_operational_transport_wording_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["basis"].append("mail transport enabled")
    with pytest.raises(RuntimeError, match="operational-transport-like wording"):
        validate_secure_transport_setup_contract_review(_write(tmp_path, payload))
