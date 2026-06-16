from pathlib import Path

import pytest
import yaml

from tools.validate_etf_eu_recipient_allowlist import validate_recipient_allowlist

SAMPLE = {
    "schema_version": "etf_eu_recipient_allowlist_v1",
    "status": "sample_only_inactive",
    "recipient_activation": False,
    "real_recipients": False,
    "send_attempted": False,
    "email_delivery": False,
    "production_delivery": False,
    "delivery_receipt": False,
    "recipients": [
        {
            "recipient_id": "sample_operator",
            "display_name": "Sample Operator",
            "email": "sample-operator@example.invalid",
            "role": "operator_review_only",
            "active": False,
            "delivery_enabled": False,
            "notes": "Sample placeholder only. Not a real recipient.",
        },
        {
            "recipient_id": "sample_client",
            "display_name": "Sample Client",
            "email": "sample-client@example.invalid",
            "role": "client_placeholder_only",
            "active": False,
            "delivery_enabled": False,
            "notes": "Sample placeholder only. Not a real recipient.",
        },
    ],
}


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "allowlist.yml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return path


def test_sample_allowlist_validates_from_repo_file():
    validate_recipient_allowlist(Path("config/etf_eu_recipient_allowlist.sample.yml"))


def test_sample_allowlist_validates(tmp_path: Path):
    path = _write(tmp_path, SAMPLE)
    result = validate_recipient_allowlist(path)
    assert result["status"] == "sample_only_inactive_valid"
    assert result["recipient_count"] == 2
    assert result["recipient_activation"] is False
    assert result["real_recipients"] is False
    assert result["production_delivery"] is False


def test_empty_recipient_list_fails(tmp_path: Path):
    payload = {**SAMPLE, "recipients": []}
    path = _write(tmp_path, payload)
    with pytest.raises(RuntimeError, match="recipients must be a non-empty list"):
        validate_recipient_allowlist(path)


@pytest.mark.parametrize(
    "flag",
    [
        "recipient_activation",
        "real_recipients",
        "send_attempted",
        "email_delivery",
        "production_delivery",
        "delivery_receipt",
    ],
)
def test_top_level_delivery_or_recipient_authority_true_fails(tmp_path: Path, flag: str):
    payload = {**SAMPLE, flag: True}
    path = _write(tmp_path, payload)
    with pytest.raises(RuntimeError, match=f"{flag} must remain false"):
        validate_recipient_allowlist(path)


def test_recipient_active_true_fails(tmp_path: Path):
    payload = yaml.safe_load(yaml.safe_dump(SAMPLE))
    payload["recipients"][0]["active"] = True
    path = _write(tmp_path, payload)
    with pytest.raises(RuntimeError, match=r"recipient\[0\].active must remain false"):
        validate_recipient_allowlist(path)


def test_recipient_delivery_enabled_true_fails(tmp_path: Path):
    payload = yaml.safe_load(yaml.safe_dump(SAMPLE))
    payload["recipients"][0]["delivery_enabled"] = True
    path = _write(tmp_path, payload)
    with pytest.raises(RuntimeError, match=r"recipient\[0\].delivery_enabled must remain false"):
        validate_recipient_allowlist(path)


def test_non_placeholder_email_domain_fails(tmp_path: Path):
    payload = yaml.safe_load(yaml.safe_dump(SAMPLE))
    payload["recipients"][0]["email"] = "sample@example.com"
    path = _write(tmp_path, payload)
    with pytest.raises(RuntimeError, match="email must end with @example.invalid"):
        validate_recipient_allowlist(path)


def test_missing_required_recipient_field_fails(tmp_path: Path):
    payload = yaml.safe_load(yaml.safe_dump(SAMPLE))
    del payload["recipients"][0]["notes"]
    path = _write(tmp_path, payload)
    with pytest.raises(RuntimeError, match="missing required field"):
        validate_recipient_allowlist(path)


@pytest.mark.parametrize(
    "forbidden_key",
    [
        "smtp_host",
        "smtp_user",
        "smtp_" + "password",
        "api_" + "key",
        "mail_transport",
        "sendgrid",
        "mailgun",
        "gmail",
        "outlook",
    ],
)
def test_forbidden_smtp_or_mail_transport_keys_fail(tmp_path: Path, forbidden_key: str):
    payload = yaml.safe_load(yaml.safe_dump(SAMPLE))
    payload[forbidden_key] = "forbidden"
    path = _write(tmp_path, payload)
    with pytest.raises(RuntimeError, match="forbidden live-delivery key"):
        validate_recipient_allowlist(path)
