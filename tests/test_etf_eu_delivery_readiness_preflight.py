import json
from pathlib import Path

import pytest

from runtime.build_etf_eu_delivery_readiness_preflight import (
    AUTHORITY_FALSE_FIELDS,
    build_delivery_readiness_preflight,
    write_delivery_readiness_preflight,
)
from tools.validate_etf_eu_delivery_readiness_preflight import validate_delivery_readiness_preflight


def test_default_preflight_artifact_is_valid_and_blocked(tmp_path: Path):
    path = write_delivery_readiness_preflight(
        tmp_path,
        run_id="20260617_000000",
        report_date="2026-06-17",
        created_at_utc="2026-06-17T00:00:00Z",
    )

    validate_delivery_readiness_preflight(path)

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert path == tmp_path / "etf_eu_delivery_readiness_preflight_20260617_000000.json"
    assert payload["schema_version"] == "etf_eu_delivery_readiness_preflight_v1"
    assert payload["status"] == "blocked_not_ready_for_wp13"
    assert payload["ready_for_wp13"] is False
    assert payload["recipient_allowlist_status"] == "missing"
    assert payload["smtp_secrets_policy_status"] == "missing"
    assert payload["delivery_receipt_validator_status"] == "missing"
    assert payload["send_attempted"] is False
    assert payload["email_delivery"] is False
    assert payload["delivery_receipt"] is False
    assert payload["production_delivery"] is False
    assert payload["pdf_generation"] is False
    assert payload["funding_authority"] is False
    assert payload["portfolio_mutation"] is False
    assert payload["candidate_promotion"] is False
    assert payload["valuation_grade_promotion"] is False


def test_missing_recipient_allowlist_keeps_ready_for_wp13_false(tmp_path: Path):
    path = write_delivery_readiness_preflight(
        tmp_path,
        run_id="20260617_000001",
        report_date="2026-06-17",
        smtp_secrets_policy_path="control/future_smtp_secrets_policy.md",
        delivery_receipt_validator_path="tools/future_delivery_receipt_validator.py",
        created_at_utc="2026-06-17T00:00:00Z",
    )

    validate_delivery_readiness_preflight(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["recipient_allowlist_status"] == "missing"
    assert payload["ready_for_wp13"] is False
    assert payload["status"] == "blocked_not_ready_for_wp13"


def test_missing_smtp_secrets_policy_keeps_ready_for_wp13_false(tmp_path: Path):
    path = write_delivery_readiness_preflight(
        tmp_path,
        run_id="20260617_000002",
        report_date="2026-06-17",
        recipient_allowlist_path="control/future_recipient_allowlist.yml",
        delivery_receipt_validator_path="tools/future_delivery_receipt_validator.py",
        created_at_utc="2026-06-17T00:00:00Z",
    )

    validate_delivery_readiness_preflight(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["smtp_secrets_policy_status"] == "missing"
    assert payload["ready_for_wp13"] is False
    assert payload["status"] == "blocked_not_ready_for_wp13"


def test_missing_delivery_receipt_validator_keeps_ready_for_wp13_false(tmp_path: Path):
    path = write_delivery_readiness_preflight(
        tmp_path,
        run_id="20260617_000003",
        report_date="2026-06-17",
        recipient_allowlist_path="control/future_recipient_allowlist.yml",
        smtp_secrets_policy_path="control/future_smtp_secrets_policy.md",
        created_at_utc="2026-06-17T00:00:00Z",
    )

    validate_delivery_readiness_preflight(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["delivery_receipt_validator_status"] == "missing"
    assert payload["ready_for_wp13"] is False
    assert payload["status"] == "blocked_not_ready_for_wp13"


@pytest.mark.parametrize(
    "flag",
    [
        "send_attempted",
        "email_delivery",
        "delivery_receipt",
        "production_delivery",
        "pdf_generation",
        "funding_authority",
        "portfolio_mutation",
        "candidate_promotion",
        "valuation_grade_promotion",
    ],
)
def test_any_top_level_authority_flag_true_fails_validation(tmp_path: Path, flag: str):
    payload = build_delivery_readiness_preflight(
        run_id="20260617_000004",
        report_date="2026-06-17",
        created_at_utc="2026-06-17T00:00:00Z",
    )
    payload[flag] = True
    artifact = tmp_path / "preflight.json"
    artifact.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(RuntimeError, match=f"{flag} must remain false"):
        validate_delivery_readiness_preflight(artifact)


def test_ready_for_wp13_true_with_missing_prerequisites_fails_validation(tmp_path: Path):
    payload = build_delivery_readiness_preflight(
        run_id="20260617_000005",
        report_date="2026-06-17",
        created_at_utc="2026-06-17T00:00:00Z",
    )
    payload["ready_for_wp13"] = True
    payload["status"] = "ready_for_wp13_preflight_only"
    artifact = tmp_path / "preflight.json"
    artifact.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(RuntimeError, match="ready_for_wp13=true requires all prerequisites present"):
        validate_delivery_readiness_preflight(artifact)


def test_future_ready_shape_requires_all_prerequisites_but_does_not_enable_send_authority(tmp_path: Path):
    path = write_delivery_readiness_preflight(
        tmp_path,
        run_id="20260617_000006",
        report_date="2026-06-17",
        recipient_allowlist_path="control/future_recipient_allowlist.yml",
        smtp_secrets_policy_path="control/future_smtp_secrets_policy.md",
        delivery_receipt_validator_path="tools/future_delivery_receipt_validator.py",
        created_at_utc="2026-06-17T00:00:00Z",
    )

    validate_delivery_readiness_preflight(path)

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["status"] == "ready_for_wp13_preflight_only"
    assert payload["ready_for_wp13"] is True
    assert payload["recipient_allowlist_status"] == "present"
    assert payload["smtp_secrets_policy_status"] == "present"
    assert payload["delivery_receipt_validator_status"] == "present"
    for flag in AUTHORITY_FALSE_FIELDS:
        assert payload[flag] is False
        assert payload["authority"][flag] is False
