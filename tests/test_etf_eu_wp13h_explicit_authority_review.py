import json
from pathlib import Path

import pytest

from tools.validate_etf_eu_wp13h_explicit_authority_review import (
    validate_wp13h_explicit_authority_review,
)

SAMPLE_PATH = Path(
    "output/delivery/authority/etf_eu_wp13h_explicit_authority_review_20260617_000000.json"
)

SAMPLE = {
    "schema_version": "etf_eu_wp13h_explicit_authority_review_v1",
    "review_id": "20260617_000000",
    "created_at_utc": "2026-06-17T00:00:00Z",
    "status": "explicit_authority_review_completed",
    "review_scope": "authority_decision_review_only",
    "decision": "not_granted",
    "decision_reason": [
        "WP13G reconciliation completed the review chain",
        "operational prerequisites remain incomplete",
        "authority cannot be granted",
        "preflight readiness is not authority",
    ],
    "input_state": {
        "review_chain_complete": True,
        "operational_prerequisites_complete": False,
        "authority_can_be_granted": False,
        "recipient_policy_reviewed": True,
        "secure_transport_setup_reviewed": True,
        "receipt_proof_path_reviewed": True,
        "recipient_activation": False,
        "real_recipients": False,
        "mail_transport_enabled": False,
        "external_mail_api_enabled": False,
        "real_receipt": False,
        "proof_claimed": False,
        "send_attempted": False,
    },
    "decision_result": {
        "authority_granted": False,
        "wp13_authority": False,
        "production_delivery": False,
        "operational_package_allowed": False,
        "activation_allowed": False,
        "future_review_allowed_after_new_authority": True,
    },
    "implementation_allowed_in_this_package": False,
    "activation_allowed_in_this_package": False,
    "authority_created": False,
    "selected_next_package": "WP13I",
    "selected_next_package_title": "blocked-state closeout and roadmap decision, review-only",
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
        "real_receipt": False,
        "proof_claimed": False,
        "send_attempted": False,
        "authority_granted": False,
        "ready_for_wp13_preflight_only": True,
        "wp13_authority": False,
    },
}


def _copy_sample() -> dict:
    return json.loads(json.dumps(SAMPLE))


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "wp13h_explicit_authority_review.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def test_valid_wp13h_artifact_passes_from_repo_file():
    validate_wp13h_explicit_authority_review(SAMPLE_PATH)


def test_valid_wp13h_artifact_passes(tmp_path: Path):
    result = validate_wp13h_explicit_authority_review(_write(tmp_path, SAMPLE))
    assert result["selected_next_package"] == "WP13I"
    assert result["decision"] == "not_granted"
    assert result["authority_granted"] is False
    assert result["production_delivery"] is False


def test_unsupported_schema_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["schema_version"] = "bad"
    with pytest.raises(RuntimeError, match="unsupported schema_version"):
        validate_wp13h_explicit_authority_review(_write(tmp_path, payload))


def test_wrong_status_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["status"] = "bad"
    with pytest.raises(RuntimeError, match="status must be explicit_authority_review_completed"):
        validate_wp13h_explicit_authority_review(_write(tmp_path, payload))


def test_wrong_review_scope_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["review_scope"] = "bad"
    with pytest.raises(RuntimeError, match="review_scope must be authority_decision_review_only"):
        validate_wp13h_explicit_authority_review(_write(tmp_path, payload))


def test_wrong_decision_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["decision"] = "granted"
    with pytest.raises(RuntimeError, match="decision must be not_granted"):
        validate_wp13h_explicit_authority_review(_write(tmp_path, payload))


def test_empty_decision_reason_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["decision_reason"] = []
    with pytest.raises(RuntimeError, match="decision_reason must be a non-empty list"):
        validate_wp13h_explicit_authority_review(_write(tmp_path, payload))


def test_missing_input_state_fails(tmp_path: Path):
    payload = _copy_sample()
    del payload["input_state"]
    with pytest.raises(RuntimeError, match="missing top-level key"):
        validate_wp13h_explicit_authority_review(_write(tmp_path, payload))


def test_review_chain_complete_false_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["input_state"]["review_chain_complete"] = False
    with pytest.raises(RuntimeError, match="input_state.review_chain_complete must be true"):
        validate_wp13h_explicit_authority_review(_write(tmp_path, payload))


def test_operational_prerequisites_complete_true_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["input_state"]["operational_prerequisites_complete"] = True
    with pytest.raises(RuntimeError, match="input_state.operational_prerequisites_complete must remain false"):
        validate_wp13h_explicit_authority_review(_write(tmp_path, payload))


def test_authority_can_be_granted_true_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["input_state"]["authority_can_be_granted"] = True
    with pytest.raises(RuntimeError, match="input_state.authority_can_be_granted must remain false"):
        validate_wp13h_explicit_authority_review(_write(tmp_path, payload))


@pytest.mark.parametrize(
    "flag",
    [
        "recipient_activation",
        "real_recipients",
        "mail_transport_enabled",
        "external_mail_api_enabled",
        "real_receipt",
        "proof_claimed",
        "send_attempted",
    ],
)
def test_operational_input_flags_true_fail(tmp_path: Path, flag: str):
    payload = _copy_sample()
    payload["input_state"][flag] = True
    with pytest.raises(RuntimeError, match=f"input_state.{flag} must remain false"):
        validate_wp13h_explicit_authority_review(_write(tmp_path, payload))


def test_missing_decision_result_fails(tmp_path: Path):
    payload = _copy_sample()
    del payload["decision_result"]
    with pytest.raises(RuntimeError, match="missing top-level key"):
        validate_wp13h_explicit_authority_review(_write(tmp_path, payload))


@pytest.mark.parametrize(
    "flag",
    [
        "authority_granted",
        "wp13_authority",
        "production_delivery",
        "operational_package_allowed",
        "activation_allowed",
    ],
)
def test_decision_result_false_flags_true_fail(tmp_path: Path, flag: str):
    payload = _copy_sample()
    payload["decision_result"][flag] = True
    with pytest.raises(RuntimeError, match=f"decision_result.{flag} must remain false"):
        validate_wp13h_explicit_authority_review(_write(tmp_path, payload))


def test_future_review_allowed_false_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["decision_result"]["future_review_allowed_after_new_authority"] = False
    with pytest.raises(RuntimeError, match="future_review_allowed_after_new_authority must be true"):
        validate_wp13h_explicit_authority_review(_write(tmp_path, payload))


@pytest.mark.parametrize(
    "flag",
    [
        "implementation_allowed_in_this_package",
        "activation_allowed_in_this_package",
        "authority_created",
    ],
)
def test_top_level_authority_or_activation_flags_true_fail(tmp_path: Path, flag: str):
    payload = _copy_sample()
    payload[flag] = True
    with pytest.raises(RuntimeError, match=f"{flag} must remain false"):
        validate_wp13h_explicit_authority_review(_write(tmp_path, payload))


def test_wrong_selected_next_package_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["selected_next_package"] = "WP13H"
    with pytest.raises(RuntimeError, match="selected_next_package must be WP13I"):
        validate_wp13h_explicit_authority_review(_write(tmp_path, payload))


@pytest.mark.parametrize(
    "flag",
    [
        "wp13_authority",
        "production_delivery",
        "authority_granted",
    ],
)
def test_authority_flags_true_fail(tmp_path: Path, flag: str):
    payload = _copy_sample()
    payload["authority"][flag] = True
    with pytest.raises(RuntimeError, match=f"authority.{flag} must remain false"):
        validate_wp13h_explicit_authority_review(_write(tmp_path, payload))


def test_operational_authority_wording_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["decision_reason"].append("authority granted")
    with pytest.raises(RuntimeError, match="operational-authority-like wording"):
        validate_wp13h_explicit_authority_review(_write(tmp_path, payload))
