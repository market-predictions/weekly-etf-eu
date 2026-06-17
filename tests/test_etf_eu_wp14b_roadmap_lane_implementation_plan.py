import json
from pathlib import Path

import pytest

from tools.validate_etf_eu_wp14b_roadmap_lane_implementation_plan import (
    validate_wp14b_roadmap_lane_implementation_plan,
)

SAMPLE_PATH = Path(
    "output/roadmap/etf_eu_wp14b_roadmap_lane_implementation_plan_20260617_000000.json"
)

SAMPLE = {
    "schema_version": "etf_eu_wp14b_roadmap_lane_implementation_plan_v1",
    "review_id": "20260617_000000",
    "created_at_utc": "2026-06-17T00:00:00Z",
    "status": "roadmap_lane_implementation_plan_completed",
    "review_scope": "post_wp13_implementation_plan_review_only",
    "basis": [
        "WP14A completed roadmap lane selection framework",
        "WP13 blocked-state loop remains closed",
        "authority remains not granted",
        "operational prerequisites remain incomplete",
        "delivery inputs lane is inactive",
    ],
    "input_state": {
        "wp13_review_chain_complete": True,
        "authority_not_granted": True,
        "operational_prerequisites_complete": False,
        "production_delivery": False,
        "wp13_authority": False,
        "roadmap_loop_closed": True,
        "lane_selection_deferred_to_wp14b": True,
    },
    "lane_decision": {
        "selected_implementation_lane": "ucits_instrument_identity_lane",
        "delivery_inputs_lane_selected": False,
        "product_quality_lane_selected": False,
        "ucits_instrument_identity_lane_selected": True,
        "report_surface_quality_lane_selected": False,
        "reason": "UCITS instrument identity is foundational for EU ETF report correctness and can be planned without operational activation",
    },
    "implementation_plan": {
        "plan_only": True,
        "implementation_allowed_in_wp14b": False,
        "recommended_next_package": "WP14C",
        "recommended_next_package_title": "UCITS instrument identity audit and plan, review-only",
        "required_future_files_to_review": [
            "control/UCITS_SYMBOL_REGISTRY_CONTRACT.md",
            "control/UCITS_ETF_REVIEW_CONTRACT_V1.md",
            "control/UCITS_INVESTABILITY_RULES.md",
            "config/ucits_symbol_registry.yml",
        ],
        "future_work_items": [
            "audit UCITS instrument identity contract coverage",
            "verify ISIN-first identity expectations",
            "verify exchange-line/proxy/candidate separation",
            "identify missing identity validators",
            "identify fixture gaps",
            "produce a non-mutating WP14C audit artifact",
        ],
    },
    "implementation_allowed_in_this_package": False,
    "activation_allowed_in_this_package": False,
    "authority_created": False,
    "selected_next_package": "WP14C",
    "selected_next_package_title": "UCITS instrument identity audit and plan, review-only",
    "explicitly_out_of_scope": [
        "review-only package",
        "no authority change",
        "no activation step",
        "no production state change",
        "no portfolio state change",
        "no candidate state change",
        "no lane implementation in WP14B",
        "no registry mutation in WP14B",
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
    path = tmp_path / "wp14b_plan.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def test_valid_repo_artifact_passes():
    validate_wp14b_roadmap_lane_implementation_plan(SAMPLE_PATH)


def test_valid_sample_passes(tmp_path: Path):
    result = validate_wp14b_roadmap_lane_implementation_plan(_write(tmp_path, SAMPLE))
    assert result["selected_implementation_lane"] == "ucits_instrument_identity_lane"
    assert result["selected_next_package"] == "WP14C"
    assert result["plan_only"] is True


def test_unsupported_schema_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["schema_version"] = "bad"
    with pytest.raises(RuntimeError, match="unsupported schema_version"):
        validate_wp14b_roadmap_lane_implementation_plan(_write(tmp_path, payload))


def test_wrong_status_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["status"] = "bad"
    with pytest.raises(RuntimeError, match="bad status"):
        validate_wp14b_roadmap_lane_implementation_plan(_write(tmp_path, payload))


def test_wrong_review_scope_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["review_scope"] = "bad"
    with pytest.raises(RuntimeError, match="bad review_scope"):
        validate_wp14b_roadmap_lane_implementation_plan(_write(tmp_path, payload))


def test_empty_basis_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["basis"] = []
    with pytest.raises(RuntimeError, match="basis must be non-empty list"):
        validate_wp14b_roadmap_lane_implementation_plan(_write(tmp_path, payload))


def test_missing_input_state_fails(tmp_path: Path):
    payload = _copy_sample()
    del payload["input_state"]
    with pytest.raises(RuntimeError, match="missing top-level"):
        validate_wp14b_roadmap_lane_implementation_plan(_write(tmp_path, payload))


@pytest.mark.parametrize(
    "flag",
    ["wp13_review_chain_complete", "authority_not_granted", "roadmap_loop_closed", "lane_selection_deferred_to_wp14b"],
)
def test_input_true_flags_false_fail(tmp_path: Path, flag: str):
    payload = _copy_sample()
    payload["input_state"][flag] = False
    with pytest.raises(RuntimeError, match=f"input_state.{flag} must be true"):
        validate_wp14b_roadmap_lane_implementation_plan(_write(tmp_path, payload))


@pytest.mark.parametrize("flag", ["operational_prerequisites_complete", "production_delivery", "wp13_authority"])
def test_input_false_flags_true_fail(tmp_path: Path, flag: str):
    payload = _copy_sample()
    payload["input_state"][flag] = True
    with pytest.raises(RuntimeError, match=f"input_state.{flag} must remain false"):
        validate_wp14b_roadmap_lane_implementation_plan(_write(tmp_path, payload))


def test_missing_lane_decision_fails(tmp_path: Path):
    payload = _copy_sample()
    del payload["lane_decision"]
    with pytest.raises(RuntimeError, match="missing top-level"):
        validate_wp14b_roadmap_lane_implementation_plan(_write(tmp_path, payload))


def test_wrong_selected_implementation_lane_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["lane_decision"]["selected_implementation_lane"] = "product_quality_lane"
    with pytest.raises(RuntimeError, match="selected_implementation_lane must be ucits_instrument_identity_lane"):
        validate_wp14b_roadmap_lane_implementation_plan(_write(tmp_path, payload))


def test_ucits_lane_selected_false_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["lane_decision"]["ucits_instrument_identity_lane_selected"] = False
    with pytest.raises(RuntimeError, match="ucits lane selected must be true"):
        validate_wp14b_roadmap_lane_implementation_plan(_write(tmp_path, payload))


@pytest.mark.parametrize(
    "flag",
    ["delivery_inputs_lane_selected", "product_quality_lane_selected", "report_surface_quality_lane_selected"],
)
def test_other_lane_selected_true_fails(tmp_path: Path, flag: str):
    payload = _copy_sample()
    payload["lane_decision"][flag] = True
    with pytest.raises(RuntimeError, match=f"{flag} must remain false"):
        validate_wp14b_roadmap_lane_implementation_plan(_write(tmp_path, payload))


def test_missing_implementation_plan_fails(tmp_path: Path):
    payload = _copy_sample()
    del payload["implementation_plan"]
    with pytest.raises(RuntimeError, match="missing top-level"):
        validate_wp14b_roadmap_lane_implementation_plan(_write(tmp_path, payload))


def test_plan_only_false_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["implementation_plan"]["plan_only"] = False
    with pytest.raises(RuntimeError, match="plan_only must be true"):
        validate_wp14b_roadmap_lane_implementation_plan(_write(tmp_path, payload))


def test_implementation_allowed_in_wp14b_true_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["implementation_plan"]["implementation_allowed_in_wp14b"] = True
    with pytest.raises(RuntimeError, match="implementation_allowed_in_wp14b must remain false"):
        validate_wp14b_roadmap_lane_implementation_plan(_write(tmp_path, payload))


def test_wrong_recommended_next_package_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["implementation_plan"]["recommended_next_package"] = "WP14B"
    with pytest.raises(RuntimeError, match="recommended_next_package must be WP14C"):
        validate_wp14b_roadmap_lane_implementation_plan(_write(tmp_path, payload))


@pytest.mark.parametrize("key", ["required_future_files_to_review", "future_work_items"])
def test_empty_future_lists_fail(tmp_path: Path, key: str):
    payload = _copy_sample()
    payload["implementation_plan"][key] = []
    with pytest.raises(RuntimeError, match=f"{key} must be non-empty list"):
        validate_wp14b_roadmap_lane_implementation_plan(_write(tmp_path, payload))


@pytest.mark.parametrize(
    "flag",
    ["implementation_allowed_in_this_package", "activation_allowed_in_this_package", "authority_created"],
)
def test_top_level_false_flags_true_fail(tmp_path: Path, flag: str):
    payload = _copy_sample()
    payload[flag] = True
    with pytest.raises(RuntimeError, match=f"{flag} must remain false"):
        validate_wp14b_roadmap_lane_implementation_plan(_write(tmp_path, payload))


def test_wrong_selected_next_package_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["selected_next_package"] = "WP14B"
    with pytest.raises(RuntimeError, match="selected_next_package must be WP14C"):
        validate_wp14b_roadmap_lane_implementation_plan(_write(tmp_path, payload))


@pytest.mark.parametrize("flag", ["wp14_authority", "production_delivery", "authority_granted"])
def test_authority_flags_true_fail(tmp_path: Path, flag: str):
    payload = _copy_sample()
    payload["authority"][flag] = True
    with pytest.raises(RuntimeError, match=f"authority.{flag} must remain false"):
        validate_wp14b_roadmap_lane_implementation_plan(_write(tmp_path, payload))


@pytest.mark.parametrize("phrase", ["authority granted", "lane was implemented", "registry mutation occurred"])
def test_forbidden_positive_wording_fails(tmp_path: Path, phrase: str):
    payload = _copy_sample()
    payload["basis"].append(phrase)
    with pytest.raises(RuntimeError, match="forbidden positive wording"):
        validate_wp14b_roadmap_lane_implementation_plan(_write(tmp_path, payload))
