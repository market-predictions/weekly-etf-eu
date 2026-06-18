from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.validate_etf_eu_delivery_authorization_gate import (
    EtfEuDeliveryAuthorizationGateError,
    validate_delivery_authorization_gate,
)

ARTIFACT = Path("output/delivery/etf_eu_delivery_authorization_gate_20260618_000000.json")
RECIPIENT_POLICY = Path("control/ETF_EU_RECIPIENT_POLICY.md")
SECRETS_POLICY = Path("control/ETF_EU_SECRETS_POLICY.md")
DELIVERY_GATE = Path("control/ETF_EU_DELIVERY_AUTHORIZATION_GATE.md")


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "gate.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _payload() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _f(left: str, right: str) -> str:
    return left + right


def test_valid_authorization_gate_artifact_passes() -> None:
    result = validate_delivery_authorization_gate(ARTIFACT)
    assert result["status"] == "valid"
    assert result["selected_next_package"] == "WP14L"


def test_recipient_policy_file_exists_and_blocks_recipient_use() -> None:
    text = RECIPIENT_POLICY.read_text(encoding="utf-8")
    assert _f("real_", "recipients=false") in text
    assert _f("recipient_", "activation=false") in text
    assert _f("recipient_", "source=none") in text
    assert "future recipient list requires a separate explicit policy package" in text


def test_secrets_policy_file_exists_and_blocks_secret_use() -> None:
    text = SECRETS_POLICY.read_text(encoding="utf-8")
    assert _f("secrets_", "present=false") in text
    assert _f("mail_", "transport_enabled=false") in text
    assert _f("smtp_", "configured=false") in text
    assert "future delivery secret" in text


def test_delivery_gate_file_exists_and_blocks_delivery_authority() -> None:
    text = DELIVERY_GATE.read_text(encoding="utf-8")
    assert _f("delivery_", "authorized=false") in text
    assert _f("production_", "delivery=false") in text
    assert _f("real_", "receipt=false") in text
    assert "Delivery cannot be authorized by code alone" in text


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
        _f("mail_", "transport_enabled"),
        _f("smtp_", "configured"),
        _f("portfolio_", "mutation"),
        _f("candidate_", "promotion"),
        _f("funding_", "authority"),
        _f("valuation_", "grade"),
    ],
)
def test_validator_rejects_true_gate_flags(tmp_path: Path, field: str) -> None:
    payload = _payload()
    payload[field] = True
    artifact = _write(tmp_path, payload)
    with pytest.raises(EtfEuDeliveryAuthorizationGateError, match=f"{field} must be false"):
        validate_delivery_authorization_gate(artifact)


def test_validator_rejects_missing_recipient_policy(tmp_path: Path) -> None:
    payload = _payload()
    key = _f("recipient_", "policy_path")
    payload[key] = str(tmp_path / "missing_recipient_policy.md")
    artifact = _write(tmp_path, payload)
    with pytest.raises(EtfEuDeliveryAuthorizationGateError, match=f"{key} does not exist"):
        validate_delivery_authorization_gate(artifact)


def test_validator_rejects_missing_secrets_policy(tmp_path: Path) -> None:
    payload = _payload()
    key = _f("secrets_", "policy_path")
    payload[key] = str(tmp_path / "missing_secrets_policy.md")
    artifact = _write(tmp_path, payload)
    with pytest.raises(EtfEuDeliveryAuthorizationGateError, match=f"{key} does not exist"):
        validate_delivery_authorization_gate(artifact)


def test_validator_rejects_missing_delivery_gate_policy(tmp_path: Path) -> None:
    payload = _payload()
    key = _f("delivery_authorization_", "gate_path")
    payload[key] = str(tmp_path / "missing_delivery_gate.md")
    artifact = _write(tmp_path, payload)
    with pytest.raises(EtfEuDeliveryAuthorizationGateError, match=f"{key} does not exist"):
        validate_delivery_authorization_gate(artifact)


def test_validator_rejects_missing_previous_render_artifact(tmp_path: Path) -> None:
    payload = _payload()
    key = _f("html_pdf_render_dry_run_", "artifact_path")
    payload[key] = str(tmp_path / "missing_render.json")
    artifact = _write(tmp_path, payload)
    with pytest.raises(EtfEuDeliveryAuthorizationGateError, match=f"{key} does not exist"):
        validate_delivery_authorization_gate(artifact)


def test_selected_next_package_is_wp14l() -> None:
    payload = _payload()
    assert payload["selected_next_package"] == "WP14L"
    assert "authorization decision review" in payload["selected_next_package_title"]
