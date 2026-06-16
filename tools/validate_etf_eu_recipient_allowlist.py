from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

SCHEMA_VERSION = "etf_eu_recipient_allowlist_v1"
ALLOWED_STATUS = {"sample_only_inactive"}
PLACEHOLDER_EMAIL_SUFFIX = "@example.invalid"

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "status",
    "recipient_activation",
    "real_recipients",
    "send_attempted",
    "email_delivery",
    "production_delivery",
    "delivery_receipt",
    "recipients",
}

REQUIRED_FALSE_FLAGS = {
    "recipient_activation",
    "real_recipients",
    "send_attempted",
    "email_delivery",
    "production_delivery",
    "delivery_receipt",
}

REQUIRED_RECIPIENT_FIELDS = {
    "recipient_id",
    "display_name",
    "email",
    "role",
    "active",
    "delivery_enabled",
    "notes",
}

FORBIDDEN_DELIVERY_KEYS = {
    "smtp_host",
    "smtp_user",
    "smtp_" + "password",
    "api_" + "key",
    "mail_transport",
    "sendgrid",
    "mailgun",
    "gmail",
    "outlook",
}


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("recipient allowlist failed: YAML root must be an object")
    return payload


def _missing(required: set[str], payload: dict[str, Any]) -> list[str]:
    return sorted(required - set(payload))


def _iter_keys(value: Any):
    if isinstance(value, dict):
        for key, nested in value.items():
            yield str(key)
            yield from _iter_keys(nested)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_keys(item)


def _require_false(payload: dict[str, Any], key: str) -> None:
    if payload.get(key) is not False:
        raise RuntimeError(f"recipient allowlist failed: {key} must remain false")


def validate_recipient_allowlist(path: Path) -> dict[str, Any]:
    payload = _load_yaml(path)

    forbidden = sorted(FORBIDDEN_DELIVERY_KEYS & {key.lower() for key in _iter_keys(payload)})
    if forbidden:
        raise RuntimeError(f"recipient allowlist failed: forbidden live-delivery key(s): {', '.join(forbidden)}")

    missing_top = _missing(REQUIRED_TOP_LEVEL, payload)
    if missing_top:
        raise RuntimeError(
            "recipient allowlist failed: missing top-level key(s): " + ", ".join(missing_top)
        )

    if payload["schema_version"] != SCHEMA_VERSION:
        raise RuntimeError(
            f"recipient allowlist failed: unsupported schema_version={payload['schema_version']}"
        )

    if payload["status"] not in ALLOWED_STATUS:
        raise RuntimeError("recipient allowlist failed: status must be sample_only_inactive")

    for key in REQUIRED_FALSE_FLAGS:
        _require_false(payload, key)

    recipients = payload["recipients"]
    if not isinstance(recipients, list) or not recipients:
        raise RuntimeError("recipient allowlist failed: recipients must be a non-empty list")

    seen_ids: set[str] = set()
    for index, recipient in enumerate(recipients):
        if not isinstance(recipient, dict):
            raise RuntimeError(f"recipient allowlist failed: recipient[{index}] must be an object")
        missing_recipient = _missing(REQUIRED_RECIPIENT_FIELDS, recipient)
        if missing_recipient:
            raise RuntimeError(
                f"recipient allowlist failed: recipient[{index}] missing required field(s): "
                + ", ".join(missing_recipient)
            )

        recipient_id = recipient["recipient_id"]
        if not isinstance(recipient_id, str) or not recipient_id.strip():
            raise RuntimeError(f"recipient allowlist failed: recipient[{index}].recipient_id must be non-empty")
        if recipient_id in seen_ids:
            raise RuntimeError(f"recipient allowlist failed: duplicate recipient_id={recipient_id}")
        seen_ids.add(recipient_id)

        for field in ("display_name", "role", "notes"):
            value = recipient[field]
            if not isinstance(value, str) or not value.strip():
                raise RuntimeError(f"recipient allowlist failed: recipient[{index}].{field} must be non-empty")

        email = recipient["email"]
        if not isinstance(email, str) or not email.strip():
            raise RuntimeError(f"recipient allowlist failed: recipient[{index}].email must be non-empty")
        if not email.endswith(PLACEHOLDER_EMAIL_SUFFIX):
            raise RuntimeError(
                f"recipient allowlist failed: recipient[{index}].email must end with {PLACEHOLDER_EMAIL_SUFFIX}"
            )

        if recipient["active"] is not False:
            raise RuntimeError(f"recipient allowlist failed: recipient[{index}].active must remain false")
        if recipient["delivery_enabled"] is not False:
            raise RuntimeError(
                f"recipient allowlist failed: recipient[{index}].delivery_enabled must remain false"
            )

    result = {
        "schema_version": "etf_eu_recipient_allowlist_validation_v1",
        "status": "sample_only_inactive_valid",
        "allowlist_path": str(path),
        "recipient_count": len(recipients),
        "recipient_activation": False,
        "real_recipients": False,
        "send_attempted": False,
        "email_delivery": False,
        "delivery_receipt": False,
        "production_delivery": False,
        "placeholder_domain": "example.invalid",
    }
    print(
        "ETF_EU_RECIPIENT_ALLOWLIST_OK | "
        f"allowlist={path} | recipient_count={len(recipients)} | "
        "recipient_activation=false | real_recipients=false | production_delivery=false"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("allowlist")
    parser.add_argument("--evidence-output")
    args = parser.parse_args()

    result = validate_recipient_allowlist(Path(args.allowlist))
    if args.evidence_output:
        evidence_path = Path(args.evidence_output)
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
