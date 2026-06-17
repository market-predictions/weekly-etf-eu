from pathlib import Path

import pytest
import yaml

from tools.validate_etf_eu_smtp_secrets_policy import validate_smtp_secrets_policy

SAMPLE = {
    "schema_version": "etf_eu_smtp_secrets_policy_v1",
    "status": "sample_only_no_secrets",
    "smtp_configured": False,
    "secrets_present": False,
    "mail_transport_enabled": False,
    "external_mail_api_enabled": False,
    "send_attempted": False,
    "email_delivery": False,
    "production_delivery": False,
    "delivery_receipt": False,
    "secret_storage_policy": {
        "storage_location": "github_actions_secrets_future_only",
        "repo_plaintext_secrets_allowed": False,
        "secret_values_in_repo_allowed": False,
        "required_future_secret_names": [
            "ETF_EU_SMTP_HOST_FUTURE_PLACEHOLDER",
            "ETF_EU_SMTP_PORT_FUTURE_PLACEHOLDER",
            "ETF_EU_SMTP_USER_FUTURE_PLACEHOLDER",
            "ETF_EU_SMTP_SECRET_FUTURE_PLACEHOLDER",
        ],
    },
    "transport_policy": {
        "smtp_host": "placeholder.invalid",
        "smtp_port": 0,
        "smtp_username": "placeholder_only",
        "smtp_secret_reference": "placeholder_only",
        "provider": "placeholder_only",
        "active": False,
        "delivery_enabled": False,
    },
    "notes": "Sample policy only. No real mail host, account, credential or provider value is present.",
}


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "smtp_policy.yml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return path


def _copy_sample() -> dict:
    return yaml.safe_load(yaml.safe_dump(SAMPLE))


def test_sample_smtp_policy_validates_from_repo_file():
    validate_smtp_secrets_policy(Path("config/etf_eu_smtp_secrets_policy.sample.yml"))


def test_sample_smtp_policy_validates(tmp_path: Path):
    result = validate_smtp_secrets_policy(_write(tmp_path, SAMPLE))
    assert result["status"] == "sample_only_no_secrets_valid"
    assert result["smtp_configured"] is False
    assert result["secrets_present"] is False
    assert result["production_delivery"] is False


@pytest.mark.parametrize(
    "flag",
    [
        "smtp_configured",
        "secrets_present",
        "mail_transport_enabled",
        "external_mail_api_enabled",
        "send_attempted",
        "email_delivery",
        "production_delivery",
        "delivery_receipt",
    ],
)
def test_top_level_authority_flags_true_fail(tmp_path: Path, flag: str):
    payload = _copy_sample()
    payload[flag] = True
    with pytest.raises(RuntimeError, match=f"{flag} must remain false"):
        validate_smtp_secrets_policy(_write(tmp_path, payload))


def test_repo_plaintext_secrets_allowed_true_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["secret_storage_policy"]["repo_plaintext_secrets_allowed"] = True
    with pytest.raises(RuntimeError, match="repo_plaintext_secrets_allowed must remain false"):
        validate_smtp_secrets_policy(_write(tmp_path, payload))


def test_secret_values_in_repo_allowed_true_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["secret_storage_policy"]["secret_values_in_repo_allowed"] = True
    with pytest.raises(RuntimeError, match="secret_values_in_repo_allowed must remain false"):
        validate_smtp_secrets_policy(_write(tmp_path, payload))


def test_real_looking_smtp_hostname_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["transport_policy"]["smtp_host"] = "smtp.example.com"
    with pytest.raises(RuntimeError, match="non-placeholder or provider-like value|smtp_host must be placeholder"):
        validate_smtp_secrets_policy(_write(tmp_path, payload))


def test_real_looking_username_email_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["transport_policy"]["smtp_username"] = "operator@example.invalid"
    with pytest.raises(RuntimeError, match="non-placeholder or provider-like value|smtp_username must be placeholder"):
        validate_smtp_secrets_policy(_write(tmp_path, payload))


def test_real_looking_secret_token_value_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["transport_policy"]["smtp_secret_reference"] = "abcd1234abcd1234abcd1234abcd1234"
    with pytest.raises(RuntimeError, match="non-placeholder or provider-like value|smtp_secret_reference must be placeholder"):
        validate_smtp_secrets_policy(_write(tmp_path, payload))


def test_real_provider_name_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["transport_policy"]["provider"] = "gmail"
    with pytest.raises(RuntimeError, match="non-placeholder or provider-like value|provider must be placeholder"):
        validate_smtp_secrets_policy(_write(tmp_path, payload))


def test_missing_required_field_fails(tmp_path: Path):
    payload = _copy_sample()
    del payload["transport_policy"]["smtp_host"]
    with pytest.raises(RuntimeError, match="missing required field"):
        validate_smtp_secrets_policy(_write(tmp_path, payload))


def test_non_placeholder_port_fails(tmp_path: Path):
    payload = _copy_sample()
    payload["transport_policy"]["smtp_port"] = 587
    with pytest.raises(RuntimeError, match="smtp_port must remain 0"):
        validate_smtp_secrets_policy(_write(tmp_path, payload))


@pytest.mark.parametrize(
    "forbidden_key",
    [
        "smtp_" + "pass" + "word",
        "pass" + "word",
        "api" + "_" + "key",
        "token",
        "access_token",
        "client_secret",
        "mail_transport",
        "sendgrid",
        "mailgun",
        "gmail",
        "outlook",
    ],
)
def test_forbidden_live_delivery_keys_fail(tmp_path: Path, forbidden_key: str):
    payload = _copy_sample()
    payload[forbidden_key] = "placeholder_only"
    with pytest.raises(RuntimeError, match="forbidden live-delivery key"):
        validate_smtp_secrets_policy(_write(tmp_path, payload))


def test_sample_evidence_output_can_be_generated_without_secrets(tmp_path: Path):
    path = _write(tmp_path, SAMPLE)
    result = validate_smtp_secrets_policy(path)
    evidence = tmp_path / "evidence.json"
    evidence.write_text(yaml.safe_dump(result, sort_keys=False), encoding="utf-8")
    text = evidence.read_text(encoding="utf-8")
    assert "sample_only_no_secrets_valid" in text
    assert "placeholder.invalid" in text
    assert "smtp.example.com" not in text
