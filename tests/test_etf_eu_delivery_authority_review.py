import json
from pathlib import Path

import pytest

from tools.validate_etf_eu_delivery_authority_review import (
    AUTHORITY_FALSE_FIELDS,
    validate_delivery_authority_review,
)

SAMPLE_PATH = Path("output/delivery/authority/etf_eu_delivery_authority_review_20260617_000000.json")

SAMPLE = {
    "schema_version": "etf_eu_delivery_authority_review_v1",
    "review_id": "20260617_000000",
    "created_at_utc": "2026-06-17T00:00:00Z",
    "status": "delivery_authority_not_granted",
    "decision": "do_not_prepare_delivery_authority_yet",
    "preflight_reference": "output/delivery/etf_eu_delivery_readiness_preflight_20260617_000001.json",
    "preflight_status": "ready_for_wp13_preflight_only",
    "preflight_ready_for_wp13": True,
    "authority_scope": "decision_review_only",
    "rationale": [
        "preflight readiness only confirms prerequisite paths exist",
        "recipient allowlist remains sample-only and inactive",
        "transport setup policy remains sample-only/no-live-values",
        "delivery receipt remains sample-only and not delivery proof",
        "real delivery is not authorized",
    ],
    "required_before_real_delivery": [
        "explicit recipient activation decision",
        "production recipient policy with validator",
        "secure non-repo transport setup decision",
        "real receipt path implementation",
        "receipt validation against independent operational proof",
        "explicit operational authority",
    ],
    "send_attempted": False,
    "email_delivery": False,
    "delivery_receipt": False,
    "production_delivery": False,
    "pdf_generation": False,
    "recipient_activation": False,
    "real_recipients": False,
    "mail_setup_active": False,
    "mail_transport_enabled": False,
    "external_mail_api_enabled": False,
    "funding_authority": False,
    "portfolio_mutation": False,
    "candidate_promotion": False,
    "valuation_grade_promotion": False,
}


def _copy_sample() -> dict:
    return json.loads(json.dumps(SAMPLE))


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "authority_review.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def test_recommended_decision_artifact_validates_from_repo_file():
    validate_delivery_authority_review(SAMPLE_PATH)


def test_recommended_decision_artifact_validates(tmp_path: Path):
    result = validate_delivery_authority_review(_write(tmp_path, SAMPLE))
    assert result["decision_status"] == "delivery_authority_not_granted"
    assert result["send_attempted"] is False
    assert result["production_delivery"] is False


def test_unsupported_schema_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["schema_version"] = "bad"
    with pytest.raises(RuntimeError, match="unsupported schema_version"):
        validate_delivery_authority_review(_write(tmp_path, payload))


def test_unsupported_status_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["status"] = "delivery_authority_granted"
    with pytest.raises(RuntimeError, match="unsupported status"):
        validate_delivery_authority_review(_write(tmp_path, payload))


def test_missing_preflight_reference_fails(tmp_path: Path):
    payload = _copy_sample()
    del payload["preflight_reference"]
    with pytest.raises(RuntimeError, match="missing top-level key"):
        validate_delivery_authority_review(_write(tmp_path, payload))


def test_wrong_preflight_status_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["preflight_status"] = "blocked_not_ready_for_wp13"
    with pytest.raises(RuntimeError, match="preflight_status must be ready_for_wp13_preflight_only"):
        validate_delivery_authority_review(_write(tmp_path, payload))


def test_preflight_ready_false_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["preflight_ready_for_wp13"] = False
    with pytest.raises(RuntimeError, match="preflight_ready_for_wp13 must be true"):
        validate_delivery_authority_review(_write(tmp_path, payload))


def test_wrong_authority_scope_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["authority_scope"] = "delivery_authority"
    with pytest.raises(RuntimeError, match="authority_scope must be decision_review_only"):
        validate_delivery_authority_review(_write(tmp_path, payload))


@pytest.mark.parametrize("flag", sorted(AUTHORITY_FALSE_FIELDS))
def test_each_authority_flag_true_fails(tmp_path: Path, flag: str):
    payload = _copy_sample()
    payload[flag] = True
    with pytest.raises(RuntimeError, match=f"{flag} must remain false"):
        validate_delivery_authority_review(_write(tmp_path, payload))


def test_missing_rationale_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["rationale"] = []
    with pytest.raises(RuntimeError, match="rationale must be a non-empty list"):
        validate_delivery_authority_review(_write(tmp_path, payload))


def test_missing_required_before_real_delivery_list_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["required_before_real_delivery"] = []
    with pytest.raises(RuntimeError, match="required_before_real_delivery must be a non-empty list"):
        validate_delivery_authority_review(_write(tmp_path, payload))


def test_delivery_success_like_wording_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["rationale"].append("delivery succeeded")
    with pytest.raises(RuntimeError, match="forbidden delivery-success-like wording"):
        validate_delivery_authority_review(_write(tmp_path, payload))


def test_preparation_allowed_still_cannot_set_send_or_delivery_flags_true(tmp_path: Path):
    payload = _copy_sample()
    payload["status"] = "delivery_authority_preparation_allowed"
    payload["decision"] = "prepare_delivery_authority_in_later_package_only"
    payload["send_attempted"] = True
    with pytest.raises(RuntimeError, match="send_attempted must remain false"):
        validate_delivery_authority_review(_write(tmp_path, payload))


def test_preparation_allowed_shape_validates_when_all_authority_flags_false(tmp_path: Path):
    payload = _copy_sample()
    payload["status"] = "delivery_authority_preparation_allowed"
    payload["decision"] = "prepare_delivery_authority_in_later_package_only"
    result = validate_delivery_authority_review(_write(tmp_path, payload))
    assert result["decision_status"] == "delivery_authority_preparation_allowed"
