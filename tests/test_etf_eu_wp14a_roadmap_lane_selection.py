import json
from pathlib import Path

import pytest

from tools.validate_etf_eu_wp14a_roadmap_lane_selection import (
    validate_wp14a_roadmap_lane_selection,
)

SAMPLE_PATH = Path(
    "output/roadmap/etf_eu_wp14a_roadmap_lane_selection_20260617_000000.json"
)

SAMPLE = {
    "schema_version": "etf_eu_wp14a_roadmap_lane_selection_v1",
    "review_id": "20260617_000000",
    "created_at_utc": "2026-06-17T00:00:00Z",
    "status": "roadmap_lane_selection_completed",
    "review_scope": "post_wp13_roadmap_lane_selection_only",
    "basis": [
        "WP13I completed blocked-state closeout",
        "WP13 review chain is complete",
        "authority remains not granted",
        "operational prerequisites remain incomplete",
        "roadmap loop is closed",
    ],
    "input_state": {
        "wp13_review_chain_complete": True,
        "authority_not_granted": True,
        "operational_prerequisites_complete": False,
        "production_delivery": False,
        "wp13_authority": False,
        "roadmap_loop_closed": True,
    },
    "candidate_lanes": {
        "delivery_inputs_lane": {
            "allowed_now": False,
            "reason": "would require separate authority and operational design",
        },
        "product_quality_lane": {
            "allowed_now": True,
            "reason": "safe review-only improvement lane",
        },
        "ucits_instrument_identity_lane": {
            "allowed_now": True,
            "reason": "safe data-contract improvement lane",
        },
        "report_surface_quality_lane": {
            "allowed_now": True,
            "reason": "safe output-contract improvement lane",
        },
    },
    "selected_lane": "post_wp13_roadmap_lane_selection",
    "selected_lane_result": {
        "delivery_inputs_lane_selected": False,
        "product_quality_lane_selected": False,
        "ucits_instrument_identity_lane_selected": False,
        "report_surface_quality_lane_selected": False,
        "lane_selection_deferred_to_wp14b": True,
        "reason": "WP14A records the lane-selection framework; WP14B should choose the implementation lane",
    },
    "implementation_allowed_in_this_package": False,
    "activation_allowed_in_this_package": False,
    "authority_created": False,
    "selected_next_package": "WP14B",
    "selected_next_package_title": "post-WP13 roadmap lane implementation plan, review-only",
    "explicitly_out_of_scope": [
        "review-only package",
        "no authority change",
        "no activation step",
        "no production state change",
        "no portfolio state change",
        "no candidate state change",
        "no lane implementation in WP14A",
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
        "authority_granted": False,
        "ready_for_wp13_preflight_only": True,
        "wp14_authority": False,
    },
}


def _copy_sample() -> dict:
    return json.loads(json.dumps(SAMPLE))


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "wp14a_roadmap_lane_selection.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def test_valid_wp14a_artifact_passes_from_repo_file():
    validate_wp14a_roadmap_lane_selection(SAMPLE_PATH)


def test_valid_wp14a_artifact_passes(tmp_path: Path):
    result = validate_wp14a_roadmap_lane_selection(_write(tmp_path, SAMPLE))
    assert result["selected_next_package"] == "WP14B"
    assert result["lane_selection_deferred_to_wp14b"] is True
    assert result["production_delivery"] is False


def test_unsupported_schema_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["schema_version"] = "bad"
    with pytest.raises(RuntimeError, match="unsupported schema_version"):
        validate_wp14a_roadmap_lane_selection(_write(tmp_path, payload))


def test_wrong_status_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["status"] = "bad"
    with pytest.raises(RuntimeError, match="status must be roadmap_lane_selection_completed"):
        validate_wp14a_roadmap_lane_selection(_write(tmp_path, payload))


def test_wrong_review_scope_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["review_scope"] = "bad"
    with pytest.raises(RuntimeError, match="review_scope must be post_wp13_roadmap_lane_selection_only"):
        validate_wp14a_roadmap_lane_selection(_write(tmp_path, payload))


def test_empty_basis_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["basis"] = []
    with pytest.raises(RuntimeError, match="basis must be a non-empty list"):
        validate_wp14a_roadmap_lane_selection(_write(tmp_path, payload))


def test_missing_input_state_fails(tmp_path: Path):
    payload = _copy_sample()
    del payload["input_state"]
    with pytest.raises(RuntimeError, match="missing top-level key"):
        validate_wp14a_roadmap_lane_selection(_write(tmp_path, payload))


def test_wp13_review_chain_complete_false_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["input_state"]["wp13_review_chain_complete"] = False
    with pytest.raises(RuntimeError, match="wp13_review_chain_complete must be true"):
        validate_wp14a_roadmap_lane_selection(_write(tmp_path, payload))


def test_authority_not_granted_false_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["input_state"]["authority_not_granted"] = False
    with pytest.raises(RuntimeError, match="authority_not_granted must be true"):
        validate_wp14a_roadmap_lane_selection(_write(tmp_path, payload))


@pytest.mark.parametrize("flag", ["operational_prerequisites_complete", "production_delivery", "wp13_authority"])
def test_input_false_flags_true_fail(tmp_path: Path, flag: str):
    payload = _copy_sample()
    payload["input_state"][flag] = True
    with pytest.raises(RuntimeError, match=f"input_state.{flag} must remain false"):
        validate_wp14a_roadmap_lane_selection(_write(tmp_path, payload))


def test_roadmap_loop_closed_false_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["input_state"]["roadmap_loop_closed"] = False
    with pytest.raises(RuntimeError, match="roadmap_loop_closed must be true"):
        validate_wp14a_roadmap_lane_selection(_write(tmp_path, payload))


def test_missing_candidate_lanes_fails(tmp_path: Path):
    payload = _copy_sample()
    del payload["candidate_lanes"]
    with pytest.raises(RuntimeError, match="missing top-level key"):
        validate_wp14a_roadmap_lane_selection(_write(tmp_path, payload))


def test_delivery_inputs_lane_allowed_now_true_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["candidate_lanes"]["delivery_inputs_lane"]["allowed_now"] = True
    with pytest.raises(RuntimeError, match="delivery_inputs_lane.allowed_now must remain false"):
        validate_wp14a_roadmap_lane_selection(_write(tmp_path, payload))


@pytest.mark.parametrize("lane", ["product_quality_lane", "ucits_instrument_identity_lane", "report_surface_quality_lane"])
def test_safe_lane_allowed_now_false_fails(tmp_path: Path, lane: str):
    payload = _copy_sample()
    payload["candidate_lanes"][lane]["allowed_now"] = False
    with pytest.raises(RuntimeError, match=f"{lane}.allowed_now must be true"):
        validate_wp14a_roadmap_lane_selection(_write(tmp_path, payload))


def test_wrong_selected_lane_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["selected_lane"] = "product_quality_lane"
    with pytest.raises(RuntimeError, match="selected_lane must be post_wp13_roadmap_lane_selection"):
        validate_wp14a_roadmap_lane_selection(_write(tmp_path, payload))


def test_lane_selection_deferred_false_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["selected_lane_result"]["lane_selection_deferred_to_wp14b"] = False
    with pytest.raises(RuntimeError, match="lane_selection_deferred_to_wp14b must be true"):
        validate_wp14a_roadmap_lane_selection(_write(tmp_path, payload))


@pytest.mark.parametrize(
    "flag",
    [
        "delivery_inputs_lane_selected",
        "product_quality_lane_selected",
        "ucits_instrument_identity_lane_selected",
        "report_surface_quality_lane_selected",
    ],
)
def test_concrete_lane_selected_fails(tmp_path: Path, flag: str):
    payload = _copy_sample()
    payload["selected_lane_result"][flag] = True
    with pytest.raises(RuntimeError, match=f"{flag} must remain false in WP14A"):
        validate_wp14a_roadmap_lane_selection(_write(tmp_path, payload))


@pytest.mark.parametrize(
    "flag",
    ["implementation_allowed_in_this_package", "activation_allowed_in_this_package", "authority_created"],
)
def test_top_level_flags_true_fail(tmp_path: Path, flag: str):
    payload = _copy_sample()
    payload[flag] = True
    with pytest.raises(RuntimeError, match=f"{flag} must remain false"):
        validate_wp14a_roadmap_lane_selection(_write(tmp_path, payload))


def test_wrong_selected_next_package_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["selected_next_package"] = "WP14A"
    with pytest.raises(RuntimeError, match="selected_next_package must be WP14B"):
        validate_wp14a_roadmap_lane_selection(_write(tmp_path, payload))


@pytest.mark.parametrize("flag", ["wp14_authority", "production_delivery", "authority_granted"])
def test_authority_flags_true_fail(tmp_path: Path, flag: str):
    payload = _copy_sample()
    payload["authority"][flag] = True
    with pytest.raises(RuntimeError, match=f"authority.{flag} must remain false"):
        validate_wp14a_roadmap_lane_selection(_write(tmp_path, payload))


def test_operational_roadmap_wording_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["basis"].append("authority granted")
    with pytest.raises(RuntimeError, match="operational-roadmap-like wording"):
        validate_wp14a_roadmap_lane_selection(_write(tmp_path, payload))
