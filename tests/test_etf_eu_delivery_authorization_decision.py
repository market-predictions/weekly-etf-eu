from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.validate_etf_eu_delivery_authorization_decision import (
    EtfEuDeliveryAuthorizationDecisionError,
    validate_delivery_authorization_decision,
)

ARTIFACT = Path("output/delivery/etf_eu_delivery_authorization_decision_20260618_000000.json")


def _payload() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "decision.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _f(left: str, right: str) -> str:
    return left + right


def test_valid_decision_artifact_passes() -> None:
    result = validate_delivery_authorization_decision(ARTIFACT)
    assert result["status"] == "valid"
    assert result["decision"] == "remain_blocked"
    assert result["selected_next_package"] == "WP14M"


def test_decision_is_remain_blocked() -> None:
    payload = _payload()
    assert payload[_f("delivery_authorization_", "decision")] == "remain_blocked"


def test_send_design_allowed_is_false() -> None:
    payload = _payload()
    assert payload[_f("send_design_", "allowed")] is False


def test_delivery_authorized_is_false() -> None:
    payload = _payload()
    assert payload[_f("delivery_", "authorized")] is False


@pytest.mark.parametrize(
    "field",
    [
        _f("delivery_", "authorized"),
        _f("production_", "delivery"),
        _f("recipient_", "activation"),
        _f("send_", "attempted"),
        _f("real_", "receipt"),
        _f("proof_", "claimed"),
        _f("real_", "recipients"),
        _f("secrets_", "present"),
        _f("smtp_", "configured"),
        _f("send_design_", "allowed"),
        _f("mail_", "transport_enabled"),
        _f("portfolio_", "mutation"),
        _f("candidate_", "promotion"),
        _f("funding_", "authority"),
        _f("valuation_", "grade"),
    ],
)
def test_validator_rejects_true_decision_flags(tmp_path: Path, field: str) -> None:
    payload = _payload()
    payload[field] = True
    artifact = _write(tmp_path, payload)
    with pytest.raises(EtfEuDeliveryAuthorizationDecisionError, match=f"{field} must be false"):
        validate_delivery_authorization_decision(artifact)


def test_validator_rejects_decision_other_than_remain_blocked(tmp_path: Path) -> None:
    payload = _payload()
    payload[_f("delivery_authorization_", "decision")] = "defer_send_design"
    artifact = _write(tmp_path, payload)
    with pytest.raises(EtfEuDeliveryAuthorizationDecisionError, match="delivery_authorization_decision must be remain_blocked"):
        validate_delivery_authorization_decision(artifact)


def test_validator_rejects_missing_authorization_gate_artifact(tmp_path: Path) -> None:
    payload = _payload()
    key = _f("input_authorization_gate_", "artifact_path")
    payload[key] = str(tmp_path / "missing_gate.json")
    artifact = _write(tmp_path, payload)
    with pytest.raises(EtfEuDeliveryAuthorizationDecisionError, match=f"{key} does not exist"):
        validate_delivery_authorization_decision(artifact)


def test_validator_rejects_missing_recipient_policy(tmp_path: Path) -> None:
    payload = _payload()
    key = _f("recipient_", "policy_path")
    payload[key] = str(tmp_path / "missing_recipient_policy.md")
    artifact = _write(tmp_path, payload)
    with pytest.raises(EtfEuDeliveryAuthorizationDecisionError, match=f"{key} does not exist"):
        validate_delivery_authorization_decision(artifact)


def test_selected_next_package_is_wp14m() -> None:
    payload = _payload()
    assert payload["selected_next_package"] == "WP14M"
    assert "client-surface cleanup" in payload["selected_next_package_title"]
