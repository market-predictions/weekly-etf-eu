from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml

SCHEMA_VERSION = "etf_eu_smtp_secrets_policy_v1"
ALLOWED_STATUS = {"sample_only_no_secrets"}
PLACEHOLDER_HOST = "placeholder.invalid"
PLACEHOLDER_VALUE = "placeholder_only"
FUTURE_PLACEHOLDER = "FUTURE_PLACEHOLDER"

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "status",
    "smtp_configured",
    "secrets_present",
    "mail_transport_enabled",
    "external_mail_api_enabled",
    "send_attempted",
    "email_delivery",
    "production_delivery",
    "delivery_receipt",
    "secret_storage_policy",
    "transport_policy",
    "notes",
}

REQUIRED_FALSE_FLAGS = {
    "smtp_configured",
    "secrets_present",
    "mail_transport_enabled",
    "external_mail_api_enabled",
    "send_attempted",
    "email_delivery",
    "production_delivery",
    "delivery_receipt",
}

REQUIRED_STORAGE_FIELDS = {
    "storage_location",
    "repo_plaintext_secrets_allowed",
    "secret_values_in_repo_allowed",
    "required_future_secret_names",
}

REQUIRED_TRANSPORT_FIELDS = {
    "smtp_host",
    "smtp_port",
    "smtp_username",
    "smtp_secret_reference",
    "provider",
    "active",
    "delivery_enabled",
}

PROVIDER_MARKERS = {
    "gmail",
    "outlook",
    "sendgrid",
    "mailgun",
    "office365",
    "hotmail",
    "yahoo",
    "smtp2go",
    "postmark",
    "mailchimp",
    "mandrill",
}

FORBIDDEN_KEYS = {
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
}


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("SMTP/secrets policy failed: YAML root must be an object")
    return payload


def _missing(required: set[str], payload: dict[str, Any]) -> list[str]:
    return sorted(required - set(payload))


def _iter_items(value: Any):
    if isinstance(value, dict):
        for key, nested in value.items():
            yield str(key), nested
            yield from _iter_items(nested)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_items(item)


def _require_false(payload: dict[str, Any], key: str) -> None:
    if payload.get(key) is not False:
        raise RuntimeError(f"SMTP/secrets policy failed: {key} must remain false")


def _looks_like_real_secret(value: str) -> bool:
    text = value.strip()
    if not text:
        return False
    if text in {PLACEHOLDER_HOST, PLACEHOLDER_VALUE, "github_actions_secrets_future_only"}:
        return False
    if FUTURE_PLACEHOLDER in text:
        return False
    if "@" in text:
        return True
    if re.search(r"[A-Za-z0-9+/]{24,}={0,2}", text) and "_" not in text:
        return True
    if any(marker in text.lower() for marker in PROVIDER_MARKERS):
        return True
    if "." in text and text != PLACEHOLDER_HOST:
        return True
    return False


def _reject_forbidden_keys(payload: dict[str, Any]) -> None:
    seen_keys = {key.lower() for key, _ in _iter_items(payload)}
    forbidden = sorted(FORBIDDEN_KEYS & seen_keys)
    if forbidden:
        raise RuntimeError(
            "SMTP/secrets policy failed: forbidden live-delivery key(s): " + ", ".join(forbidden)
        )


def _reject_realistic_values(payload: dict[str, Any]) -> None:
    for key, value in _iter_items(payload):
        if key == "notes":
            continue
        if isinstance(value, str) and _looks_like_real_secret(value):
            raise RuntimeError(
                f"SMTP/secrets policy failed: {key} contains a non-placeholder or provider-like value"
            )


def validate_smtp_secrets_policy(path: Path) -> dict[str, Any]:
    payload = _load_yaml(path)

    _reject_forbidden_keys(payload)
    _reject_realistic_values(payload)

    missing_top = _missing(REQUIRED_TOP_LEVEL, payload)
    if missing_top:
        raise RuntimeError(
            "SMTP/secrets policy failed: missing top-level key(s): " + ", ".join(missing_top)
        )

    if payload["schema_version"] != SCHEMA_VERSION:
        raise RuntimeError(
            f"SMTP/secrets policy failed: unsupported schema_version={payload['schema_version']}"
        )

    if payload["status"] not in ALLOWED_STATUS:
        raise RuntimeError("SMTP/secrets policy failed: status must be sample_only_no_secrets")

    for key in REQUIRED_FALSE_FLAGS:
        _require_false(payload, key)

    storage = payload["secret_storage_policy"]
    if not isinstance(storage, dict):
        raise RuntimeError("SMTP/secrets policy failed: secret_storage_policy must be an object")
    missing_storage = _missing(REQUIRED_STORAGE_FIELDS, storage)
    if missing_storage:
        raise RuntimeError(
            "SMTP/secrets policy failed: secret_storage_policy missing required field(s): "
            + ", ".join(missing_storage)
        )

    if storage["repo_plaintext_secrets_allowed"] is not False:
        raise RuntimeError(
            "SMTP/secrets policy failed: repo_plaintext_secrets_allowed must remain false"
        )
    if storage["secret_values_in_repo_allowed"] is not False:
        raise RuntimeError(
            "SMTP/secrets policy failed: secret_values_in_repo_allowed must remain false"
        )

    future_names = storage["required_future_secret_names"]
    if not isinstance(future_names, list) or not future_names:
        raise RuntimeError("SMTP/secrets policy failed: required_future_secret_names must be a non-empty list")
    for index, name in enumerate(future_names):
        if not isinstance(name, str) or FUTURE_PLACEHOLDER not in name:
            raise RuntimeError(
                f"SMTP/secrets policy failed: required_future_secret_names[{index}] must contain FUTURE_PLACEHOLDER"
            )

    transport = payload["transport_policy"]
    if not isinstance(transport, dict):
        raise RuntimeError("SMTP/secrets policy failed: transport_policy must be an object")
    missing_transport = _missing(REQUIRED_TRANSPORT_FIELDS, transport)
    if missing_transport:
        raise RuntimeError(
            "SMTP/secrets policy failed: transport_policy missing required field(s): "
            + ", ".join(missing_transport)
        )

    if transport["smtp_host"] != PLACEHOLDER_HOST:
        raise RuntimeError("SMTP/secrets policy failed: transport_policy.smtp_host must be placeholder.invalid")
    if transport["smtp_port"] != 0:
        raise RuntimeError("SMTP/secrets policy failed: transport_policy.smtp_port must remain 0")
    if transport["smtp_username"] != PLACEHOLDER_VALUE:
        raise RuntimeError("SMTP/secrets policy failed: transport_policy.smtp_username must be placeholder_only")
    if transport["smtp_secret_reference"] != PLACEHOLDER_VALUE:
        raise RuntimeError(
            "SMTP/secrets policy failed: transport_policy.smtp_secret_reference must be placeholder_only"
        )
    if transport["provider"] != PLACEHOLDER_VALUE:
        raise RuntimeError("SMTP/secrets policy failed: transport_policy.provider must be placeholder_only")
    if transport["active"] is not False:
        raise RuntimeError("SMTP/secrets policy failed: transport_policy.active must remain false")
    if transport["delivery_enabled"] is not False:
        raise RuntimeError("SMTP/secrets policy failed: transport_policy.delivery_enabled must remain false")

    result = {
        "schema_version": "etf_eu_smtp_secrets_policy_validation_v1",
        "status": "sample_only_no_secrets_valid",
        "policy_path": str(path),
        "smtp_configured": False,
        "secrets_present": False,
        "mail_transport_enabled": False,
        "external_mail_api_enabled": False,
        "send_attempted": False,
        "email_delivery": False,
        "delivery_receipt": False,
        "production_delivery": False,
        "placeholder_host": PLACEHOLDER_HOST,
    }
    print(
        "ETF_EU_SMTP_SECRETS_POLICY_OK | "
        f"policy={path} | smtp_configured=false | secrets_present=false | production_delivery=false"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("policy")
    parser.add_argument("--evidence-output")
    args = parser.parse_args()

    result = validate_smtp_secrets_policy(Path(args.policy))
    if args.evidence_output:
        evidence_path = Path(args.evidence_output)
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
