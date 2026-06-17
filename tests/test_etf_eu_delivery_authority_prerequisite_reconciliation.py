import json
from pathlib import Path

import pytest

from tools.validate_etf_eu_delivery_authority_prerequisite_reconciliation import (
    validate_delivery_authority_prerequisite_reconciliation,
)

SAMPLE_PATH = Path(
    "output/delivery/authority/etf_eu_delivery_authority_prerequisite_reconciliation_20260617_000000.json"
)

SAMPLE = {
    "schema_version": "etf_eu_delivery_authority_prerequisite_reconciliation_v1",
    "review_id": "20260617_000000",
    "created_at_utc": "2026-06-17T00:00:00Z",
    "status": "delivery_authority_prerequisite_reconciliation_completed",
    "review_scope": "delivery_authority_prerequisite_reconciliation_only",
    "basis": [
        "WP13D recipient policy review completed",
        "WP13E secure transport setup review completed",
        "WP13F receipt proof review completed",
        "WP13A authority review remains not granted",
        "preflight readiness is not authority",
    ],
    "prerequisite_domains": {
        "recipient_policy": {
            "review_artifact": "output/delivery/authority/etf_eu_recipient_policy_contract_review_20260617_000000.json",
            "review_status": "completed",
            "activation_status": "not_activated",
            "production_ready": False,
            "authority_created": False,
        },
        "secure_transport_setup": {
            "review_artifact": "output/delivery/authority/etf_eu_secure_transport_setup_contract_review_20260617_000000.json",
            "review_status": "completed",
            "activation_status": "not_activated",
            "production_ready": False,
            "authority_created": False,
        },
        "receipt_proof_path": {
            "review_artifact": "output/delivery/authority/etf_eu_receipt_proof_contract_review_20260617_000000.json",
            "review_status": "completed",
            "activation_status": "not_activated",
            "production_ready": False,
            "authority_created": False,
        },
    },
    "reconciliation_result": {
        "review_chain_complete": True,
        "operational_prerequisites_complete": False,
        "delivery_authority_can_be_granted": False,
        "delivery_authority_review_can_be_considered_later": True,
        "reason": "review chain exists while production inputs remain inactive",
    },
    "implementation_allowed_in_this_package": False,
    "activation_allowed_in_this_package": False,
    "authority_created": False,
    "selected_next_package": "WP13H",
    "selected_next_package_title": "explicit delivery authority decision review, review-only",
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
        "recipient_activation": False,
        "real_recipients": False,
        "smtp_configured": False,
        "secrets_present": False,
        "mail_transport_enabled": False,
        "external_mail_api_enabled": False,
        "real_receipt": False,
        "delivery_proof": False,
        "send_attempted": False,
        "delivery_authority": False,
        "ready_for_wp13_preflight_only": True,
        "wp13_authority": False,
    },
}


def _copy_sample() -> dict:
    return json.loads(json.dumps(SAMPLE))


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "delivery_authority_prerequisite_reconciliation.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def test_valid_reconciliation_artifact_passes_from_repo_file():
    validate_delivery_authority_prerequisite_reconciliation(SAMPLE_PATH)


def test_valid_reconciliation_artifact_passes(tmp_path: Path):
    result = validate_delivery_authority_prerequisite_reconciliation(_write(tmp_path, SAMPLE))
    assert result["selected_next_package"] == "WP13H"
    assert result["review_chain_complete"] is True
    assert result["operational_prerequisites_complete"] is False
    assert result["delivery_authority_can_be_granted"] is False


def test_unsupported_schema_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["schema_version"] = "bad"
    with pytest.raises(RuntimeError, match="unsupported schema_version"):
        validate_delivery_authority_prerequisite_reconciliation(_write(tmp_path, payload))


def test_wrong_status_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["status"] = "bad"
    with pytest.raises(RuntimeError, match="status must be delivery_authority_prerequisite_reconciliation_completed"):
        validate_delivery_authority_prerequisite_reconciliation(_write(tmp_path, payload))


def test_wrong_review_scope_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["review_scope"] = "bad"
    with pytest.raises(RuntimeError, match="review_scope must be delivery_authority_prerequisite_reconciliation_only"):
        validate_delivery_authority_prerequisite_reconciliation(_write(tmp_path, payload))


def test_empty_basis_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["basis"] = []
    with pytest.raises(RuntimeError, match="basis must be a non-empty list"):
        validate_delivery_authority_prerequisite_reconciliation(_write(tmp_path, payload))


def test_missing_prerequisite_domains_fails(tmp_path: Path):
    payload = _copy_sample()
    del payload["prerequisite_domains"]
    with pytest.raises(RuntimeError, match="missing top-level key"):
        validate_delivery_authority_prerequisite_reconciliation(_write(tmp_path, payload))


def test_missing_required_domain_fails(tmp_path: Path):
    payload = _copy_sample()
    del payload["prerequisite_domains"]["recipient_policy"]
    with pytest.raises(RuntimeError, match="missing required domain"):
        validate_delivery_authority_prerequisite_reconciliation(_write(tmp_path, payload))


def test_domain_review_status_not_completed_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["prerequisite_domains"]["recipient_policy"]["review_status"] = "pending"
    with pytest.raises(RuntimeError, match="recipient_policy.review_status must be completed"):
        validate_delivery_authority_prerequisite_reconciliation(_write(tmp_path, payload))


def test_domain_activation_status_not_not_activated_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["prerequisite_domains"]["recipient_policy"]["activation_status"] = "activated"
    with pytest.raises(RuntimeError, match="recipient_policy.activation_status must be not_activated"):
        validate_delivery_authority_prerequisite_reconciliation(_write(tmp_path, payload))


def test_domain_production_ready_true_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["prerequisite_domains"]["recipient_policy"]["production_ready"] = True
    with pytest.raises(RuntimeError, match="recipient_policy.production_ready must remain false"):
        validate_delivery_authority_prerequisite_reconciliation(_write(tmp_path, payload))


def test_domain_authority_created_true_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["prerequisite_domains"]["recipient_policy"]["authority_created"] = True
    with pytest.raises(RuntimeError, match="recipient_policy.authority_created must remain false"):
        validate_delivery_authority_prerequisite_reconciliation(_write(tmp_path, payload))


def test_review_chain_complete_false_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["reconciliation_result"]["review_chain_complete"] = False
    with pytest.raises(RuntimeError, match="review_chain_complete must be true"):
        validate_delivery_authority_prerequisite_reconciliation(_write(tmp_path, payload))


def test_operational_prerequisites_complete_true_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["reconciliation_result"]["operational_prerequisites_complete"] = True
    with pytest.raises(RuntimeError, match="operational_prerequisites_complete must remain false"):
        validate_delivery_authority_prerequisite_reconciliation(_write(tmp_path, payload))


def test_delivery_authority_can_be_granted_true_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["reconciliation_result"]["delivery_authority_can_be_granted"] = True
    with pytest.raises(RuntimeError, match="delivery_authority_can_be_granted must remain false"):
        validate_delivery_authority_prerequisite_reconciliation(_write(tmp_path, payload))


def test_delivery_authority_review_can_be_considered_later_false_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["reconciliation_result"]["delivery_authority_review_can_be_considered_later"] = False
    with pytest.raises(RuntimeError, match="delivery_authority_review_can_be_considered_later must be true"):
        validate_delivery_authority_prerequisite_reconciliation(_write(tmp_path, payload))


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
        validate_delivery_authority_prerequisite_reconciliation(_write(tmp_path, payload))


def test_wrong_selected_next_package_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["selected_next_package"] = "WP13G"
    with pytest.raises(RuntimeError, match="selected_next_package must be WP13H"):
        validate_delivery_authority_prerequisite_reconciliation(_write(tmp_path, payload))


@pytest.mark.parametrize(
    "flag",
    [
        "wp13_authority",
        "production_delivery",
        "delivery_authority",
        "recipient_activation",
        "mail_transport_enabled",
        "real_receipt",
    ],
)
def test_authority_flags_true_fail(tmp_path: Path, flag: str):
    payload = _copy_sample()
    payload["authority"][flag] = True
    with pytest.raises(RuntimeError, match=f"authority.{flag} must remain false"):
        validate_delivery_authority_prerequisite_reconciliation(_write(tmp_path, payload))


def test_operational_authority_wording_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["basis"].append("delivery authority granted")
    with pytest.raises(RuntimeError, match="operational-authority-like wording"):
        validate_delivery_authority_prerequisite_reconciliation(_write(tmp_path, payload))
