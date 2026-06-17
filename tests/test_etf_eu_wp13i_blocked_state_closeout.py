import json
from pathlib import Path

import pytest

from tools.validate_etf_eu_wp13i_blocked_state_closeout import (
    validate_wp13i_blocked_state_closeout,
)

SAMPLE_PATH = Path(
    "output/delivery/authority/etf_eu_wp13i_blocked_state_closeout_20260617_000000.json"
)

SAMPLE = {
    "schema_version": "etf_eu_wp13i_blocked_state_closeout_v1",
    "review_id": "20260617_000000",
    "created_at_utc": "2026-06-17T00:00:00Z",
    "status": "blocked_state_closeout_completed",
    "review_scope": "blocked_state_closeout_review_only",
    "decision": "blocked_state_closed",
    "blocked_state_result": {
        "wp13_review_chain_complete": True,
        "delivery_authority_not_granted": True,
        "operational_prerequisites_complete": False,
        "production_delivery": False,
        "wp13_authority": False,
        "roadmap_loop_closed": True,
    },
    "closed_review_chain": [
        "WP13A",
        "WP13B",
        "WP13C",
        "WP13D",
        "WP13E",
        "WP13F",
        "WP13G",
        "WP13H",
    ],
    "roadmap_decision": {
        "next_phase": "post_wp13_blocked_state_review",
        "recommended_next_lane": "post_wp13_roadmap_lane_selection",
        "operational_delivery_allowed": False,
        "authority_review_reopen_allowed_only_after_new_inputs": True,
        "reason": "WP13 review chain is complete while production inputs remain inactive or sample-only",
    },
    "implementation_allowed_in_this_package": False,
    "activation_allowed_in_this_package": False,
    "authority_created": False,
    "selected_next_package": "WP14A",
    "selected_next_package_title": "post-WP13 roadmap lane selection, review-only",
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
        "proof_claimed": False,
        "send_attempted": False,
        "delivery_authority": False,
        "ready_for_wp13_preflight_only": True,
        "wp13_authority": False,
    },
}


def _copy_sample() -> dict:
    return json.loads(json.dumps(SAMPLE))


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "wp13i_blocked_state_closeout.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def test_valid_wp13i_artifact_passes_from_repo_file():
    validate_wp13i_blocked_state_closeout(SAMPLE_PATH)


def test_valid_wp13i_artifact_passes(tmp_path: Path):
    result = validate_wp13i_blocked_state_closeout(_write(tmp_path, SAMPLE))
    assert result["selected_next_package"] == "WP14A"
    assert result["decision"] == "blocked_state_closed"
    assert result["roadmap_loop_closed"] is True
    assert result["production_delivery"] is False


def test_unsupported_schema_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["schema_version"] = "bad"
    with pytest.raises(RuntimeError, match="unsupported schema_version"):
        validate_wp13i_blocked_state_closeout(_write(tmp_path, payload))


def test_wrong_status_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["status"] = "bad"
    with pytest.raises(RuntimeError, match="status must be blocked_state_closeout_completed"):
        validate_wp13i_blocked_state_closeout(_write(tmp_path, payload))


def test_wrong_review_scope_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["review_scope"] = "bad"
    with pytest.raises(RuntimeError, match="review_scope must be blocked_state_closeout_review_only"):
        validate_wp13i_blocked_state_closeout(_write(tmp_path, payload))


def test_wrong_decision_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["decision"] = "bad"
    with pytest.raises(RuntimeError, match="decision must be blocked_state_closed"):
        validate_wp13i_blocked_state_closeout(_write(tmp_path, payload))


def test_missing_blocked_state_result_fails(tmp_path: Path):
    payload = _copy_sample()
    del payload["blocked_state_result"]
    with pytest.raises(RuntimeError, match="missing top-level key"):
        validate_wp13i_blocked_state_closeout(_write(tmp_path, payload))


def test_wp13_review_chain_complete_false_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["blocked_state_result"]["wp13_review_chain_complete"] = False
    with pytest.raises(RuntimeError, match="wp13_review_chain_complete must be true"):
        validate_wp13i_blocked_state_closeout(_write(tmp_path, payload))


def test_delivery_authority_not_granted_false_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["blocked_state_result"]["delivery_authority_not_granted"] = False
    with pytest.raises(RuntimeError, match="delivery_authority_not_granted must be true"):
        validate_wp13i_blocked_state_closeout(_write(tmp_path, payload))


@pytest.mark.parametrize(
    "flag",
    [
        "operational_prerequisites_complete",
        "production_delivery",
        "wp13_authority",
    ],
)
def test_blocked_result_false_flags_true_fail(tmp_path: Path, flag: str):
    payload = _copy_sample()
    payload["blocked_state_result"][flag] = True
    with pytest.raises(RuntimeError, match=f"{flag} must remain false"):
        validate_wp13i_blocked_state_closeout(_write(tmp_path, payload))


def test_roadmap_loop_closed_false_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["blocked_state_result"]["roadmap_loop_closed"] = False
    with pytest.raises(RuntimeError, match="roadmap_loop_closed must be true"):
        validate_wp13i_blocked_state_closeout(_write(tmp_path, payload))


def test_missing_wp13_package_in_chain_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["closed_review_chain"].remove("WP13E")
    with pytest.raises(RuntimeError, match="closed_review_chain missing required package"):
        validate_wp13i_blocked_state_closeout(_write(tmp_path, payload))


def test_missing_roadmap_decision_fails(tmp_path: Path):
    payload = _copy_sample()
    del payload["roadmap_decision"]
    with pytest.raises(RuntimeError, match="missing top-level key"):
        validate_wp13i_blocked_state_closeout(_write(tmp_path, payload))


def test_operational_delivery_allowed_true_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["roadmap_decision"]["operational_delivery_allowed"] = True
    with pytest.raises(RuntimeError, match="operational_delivery_allowed must remain false"):
        validate_wp13i_blocked_state_closeout(_write(tmp_path, payload))


def test_authority_review_reopen_false_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["roadmap_decision"]["authority_review_reopen_allowed_only_after_new_inputs"] = False
    with pytest.raises(RuntimeError, match="authority_review_reopen_allowed_only_after_new_inputs must be true"):
        validate_wp13i_blocked_state_closeout(_write(tmp_path, payload))


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
        validate_wp13i_blocked_state_closeout(_write(tmp_path, payload))


def test_wrong_selected_next_package_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["selected_next_package"] = "WP13I"
    with pytest.raises(RuntimeError, match="selected_next_package must be WP14A"):
        validate_wp13i_blocked_state_closeout(_write(tmp_path, payload))


@pytest.mark.parametrize(
    "flag",
    [
        "wp13_authority",
        "production_delivery",
        "delivery_authority",
        "recipient_activation",
        "mail_transport_enabled",
    ],
)
def test_authority_flags_true_fail(tmp_path: Path, flag: str):
    payload = _copy_sample()
    payload["authority"][flag] = True
    with pytest.raises(RuntimeError, match=f"authority.{flag} must remain false"):
        validate_wp13i_blocked_state_closeout(_write(tmp_path, payload))


def test_operational_authority_wording_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["roadmap_decision"]["reason"] = "authority granted"
    with pytest.raises(RuntimeError, match="operational-authority-like wording"):
        validate_wp13i_blocked_state_closeout(_write(tmp_path, payload))
