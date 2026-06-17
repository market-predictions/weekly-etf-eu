import copy
import json
from pathlib import Path

import pytest

from tools.validate_etf_eu_wp14c_ucits_identity_audit import validate_wp14c_ucits_identity_audit

SAMPLE_PATH = Path("output/ucits_identity/etf_eu_wp14c_ucits_identity_audit_20260617_000000.json")
REQUIRED_FILES = [
    "control/UCITS_SYMBOL_REGISTRY_CONTRACT.md",
    "control/UCITS_ETF_REVIEW_CONTRACT_V1.md",
    "control/UCITS_INVESTABILITY_RULES.md",
    "control/UCITS_MIGRATION_PLAN.md",
    "config/ucits_symbol_registry.yml",
]
DIMENSIONS = [
    "isin_first_identity",
    "exchange_line_identity",
    "currency_identity",
    "fund_name_identity",
    "proxy_vs_candidate_separation",
    "investability_rule_alignment",
    "registry_schema_completeness",
    "validator_coverage",
    "fixture_coverage",
    "report_surface_dependency_risk",
]


def _finding(fid="UCITS-ID-001", dimension="isin_first_identity", severity="medium"):
    return {
        "id": fid,
        "dimension": dimension,
        "status": "gap",
        "severity": severity,
        "finding": "sample finding",
        "evidence_files": ["control/UCITS_SYMBOL_REGISTRY_CONTRACT.md"],
        "recommended_next_action": "sample next action",
        "implementation_allowed_in_wp14c": False,
    }


SAMPLE = {
    "schema_version": "etf_eu_wp14c_ucits_identity_audit_v1",
    "review_id": "20260617_000000",
    "created_at_utc": "2026-06-17T00:00:00Z",
    "status": "ucits_identity_audit_completed",
    "review_scope": "ucits_identity_audit_review_only",
    "basis": ["WP14B selected ucits_instrument_identity_lane"],
    "input_state": {
        "wp13_review_chain_complete": True,
        "authority_not_granted": True,
        "operational_prerequisites_complete": False,
        "production_delivery": False,
        "wp13_authority": False,
        "roadmap_loop_closed": True,
        "selected_implementation_lane": "ucits_instrument_identity_lane",
        "plan_only": True,
    },
    "audited_files": REQUIRED_FILES,
    "audit_dimensions": {dimension: "reviewed" for dimension in DIMENSIONS},
    "findings": [
        _finding("UCITS-ID-001", "isin_first_identity", "high"),
        _finding("UCITS-ID-002", "validator_coverage", "medium"),
        _finding("UCITS-ID-003", "fixture_coverage", "low"),
    ],
    "summary": {
        "total_findings": 3,
        "high_severity_findings": 1,
        "medium_severity_findings": 1,
        "low_severity_findings": 1,
        "implementation_required": True,
        "registry_mutation_required_later": "unknown_until_wp14d",
        "safe_to_continue_to_wp14d": True,
    },
    "implementation_allowed_in_this_package": False,
    "registry_mutation_allowed_in_this_package": False,
    "report_renderer_mutation_allowed_in_this_package": False,
    "activation_allowed_in_this_package": False,
    "authority_created": False,
    "selected_next_package": "WP14D",
    "selected_next_package_title": "UCITS identity contract/validator implementation, review-only",
    "explicitly_out_of_scope": ["review-only package", "no registry mutation in WP14C"],
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


def _copy():
    return copy.deepcopy(SAMPLE)


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "audit.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def test_valid_repo_artifact_passes():
    result = validate_wp14c_ucits_identity_audit(SAMPLE_PATH)
    assert result["total_findings"] == 9
    assert result["selected_next_package"] == "WP14D"


def test_valid_sample_passes(tmp_path: Path):
    result = validate_wp14c_ucits_identity_audit(_write(tmp_path, SAMPLE))
    assert result["high_severity_findings"] == 1
    assert result["medium_severity_findings"] == 1
    assert result["low_severity_findings"] == 1


def test_unsupported_schema_fails(tmp_path: Path):
    payload = _copy()
    payload["schema_version"] = "bad"
    with pytest.raises(RuntimeError, match="unsupported schema_version"):
        validate_wp14c_ucits_identity_audit(_write(tmp_path, payload))


def test_wrong_status_fails(tmp_path: Path):
    payload = _copy()
    payload["status"] = "bad"
    with pytest.raises(RuntimeError, match="bad status"):
        validate_wp14c_ucits_identity_audit(_write(tmp_path, payload))


def test_wrong_review_scope_fails(tmp_path: Path):
    payload = _copy()
    payload["review_scope"] = "bad"
    with pytest.raises(RuntimeError, match="bad review_scope"):
        validate_wp14c_ucits_identity_audit(_write(tmp_path, payload))


def test_empty_basis_fails(tmp_path: Path):
    payload = _copy()
    payload["basis"] = []
    with pytest.raises(RuntimeError, match="basis must be non-empty list"):
        validate_wp14c_ucits_identity_audit(_write(tmp_path, payload))


def test_missing_input_state_fails(tmp_path: Path):
    payload = _copy()
    del payload["input_state"]
    with pytest.raises(RuntimeError, match="input_state must be object"):
        validate_wp14c_ucits_identity_audit(_write(tmp_path, payload))


def test_wrong_selected_implementation_lane_fails(tmp_path: Path):
    payload = _copy()
    payload["input_state"]["selected_implementation_lane"] = "product_quality_lane"
    with pytest.raises(RuntimeError, match="wrong selected lane"):
        validate_wp14c_ucits_identity_audit(_write(tmp_path, payload))


def test_plan_only_false_fails(tmp_path: Path):
    payload = _copy()
    payload["input_state"]["plan_only"] = False
    with pytest.raises(RuntimeError, match="plan_only must be true"):
        validate_wp14c_ucits_identity_audit(_write(tmp_path, payload))


@pytest.mark.parametrize("flag", ["production_delivery", "wp13_authority", "operational_prerequisites_complete"])
def test_input_false_flags_true_fail(tmp_path: Path, flag: str):
    payload = _copy()
    payload["input_state"][flag] = True
    with pytest.raises(RuntimeError, match=f"input_state.{flag} must remain false"):
        validate_wp14c_ucits_identity_audit(_write(tmp_path, payload))


def test_missing_audited_files_fails(tmp_path: Path):
    payload = _copy()
    del payload["audited_files"]
    with pytest.raises(RuntimeError, match="audited_files must be non-empty list"):
        validate_wp14c_ucits_identity_audit(_write(tmp_path, payload))


def test_missing_required_audited_file_fails(tmp_path: Path):
    payload = _copy()
    payload["audited_files"] = REQUIRED_FILES[:-1]
    with pytest.raises(RuntimeError, match="audited_files missing"):
        validate_wp14c_ucits_identity_audit(_write(tmp_path, payload))


def test_missing_audit_dimension_fails(tmp_path: Path):
    payload = _copy()
    del payload["audit_dimensions"]["currency_identity"]
    with pytest.raises(RuntimeError, match="audit_dimensions missing"):
        validate_wp14c_ucits_identity_audit(_write(tmp_path, payload))


def test_dimension_not_reviewed_fails(tmp_path: Path):
    payload = _copy()
    payload["audit_dimensions"]["currency_identity"] = "pending"
    with pytest.raises(RuntimeError, match="dimension currency_identity must be reviewed"):
        validate_wp14c_ucits_identity_audit(_write(tmp_path, payload))


def test_empty_findings_fails(tmp_path: Path):
    payload = _copy()
    payload["findings"] = []
    with pytest.raises(RuntimeError, match="findings must be non-empty list"):
        validate_wp14c_ucits_identity_audit(_write(tmp_path, payload))


def test_finding_missing_field_fails(tmp_path: Path):
    payload = _copy()
    del payload["findings"][0]["severity"]
    with pytest.raises(RuntimeError, match="finding missing"):
        validate_wp14c_ucits_identity_audit(_write(tmp_path, payload))


def test_invalid_finding_status_fails(tmp_path: Path):
    payload = _copy()
    payload["findings"][0]["status"] = "bad"
    with pytest.raises(RuntimeError, match="invalid finding status"):
        validate_wp14c_ucits_identity_audit(_write(tmp_path, payload))


def test_invalid_severity_fails(tmp_path: Path):
    payload = _copy()
    payload["findings"][0]["severity"] = "bad"
    with pytest.raises(RuntimeError, match="invalid finding severity"):
        validate_wp14c_ucits_identity_audit(_write(tmp_path, payload))


def test_finding_implementation_allowed_true_fails(tmp_path: Path):
    payload = _copy()
    payload["findings"][0]["implementation_allowed_in_wp14c"] = True
    with pytest.raises(RuntimeError, match="finding implementation flag must remain false"):
        validate_wp14c_ucits_identity_audit(_write(tmp_path, payload))


def test_summary_count_mismatch_fails(tmp_path: Path):
    payload = _copy()
    payload["summary"]["total_findings"] = 99
    with pytest.raises(RuntimeError, match="summary count mismatch"):
        validate_wp14c_ucits_identity_audit(_write(tmp_path, payload))


@pytest.mark.parametrize(
    "flag",
    [
        "implementation_allowed_in_this_package",
        "registry_mutation_allowed_in_this_package",
        "report_renderer_mutation_allowed_in_this_package",
        "activation_allowed_in_this_package",
        "authority_created",
    ],
)
def test_top_level_false_flags_true_fail(tmp_path: Path, flag: str):
    payload = _copy()
    payload[flag] = True
    with pytest.raises(RuntimeError, match=f"{flag} must remain false"):
        validate_wp14c_ucits_identity_audit(_write(tmp_path, payload))


def test_wrong_selected_next_package_fails(tmp_path: Path):
    payload = _copy()
    payload["selected_next_package"] = "WP14C"
    with pytest.raises(RuntimeError, match="selected_next_package must be WP14D"):
        validate_wp14c_ucits_identity_audit(_write(tmp_path, payload))


@pytest.mark.parametrize("flag", ["wp14_authority", "production_delivery", "authority_granted"])
def test_authority_flags_true_fail(tmp_path: Path, flag: str):
    payload = _copy()
    payload["authority"][flag] = True
    with pytest.raises(RuntimeError, match=f"authority.{flag} must remain false"):
        validate_wp14c_ucits_identity_audit(_write(tmp_path, payload))


@pytest.mark.parametrize("phrase", ["authority granted", "registry was mutated", "report renderer was changed"])
def test_forbidden_wording_fails(tmp_path: Path, phrase: str):
    payload = _copy()
    payload["basis"].append(phrase)
    with pytest.raises(RuntimeError, match="forbidden wording"):
        validate_wp14c_ucits_identity_audit(_write(tmp_path, payload))
