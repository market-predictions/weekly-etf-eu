from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_delivery_receipt_v1"
ALLOWED_STATUS = {"sample_only_not_delivery"}
ALLOWED_RECEIPT_TYPE = {"sample_only"}
ALLOWED_CHANNEL = {"none"}

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "run_id",
    "created_at_utc",
    "report_date",
    "status",
    "receipt_type",
    "delivery_attempted",
    "delivery_success",
    "send_attempted",
    "email_delivery",
    "production_delivery",
    "delivery_receipt",
    "pdf_generation",
    "recipient_activation",
    "mail_transport_enabled",
    "channel",
    "recipient_reference",
    "delivery_artifact_paths",
    "provider_confirmation",
    "transport_message_id",
    "blockers",
}

REQUIRED_FALSE_FLAGS = {
    "delivery_attempted",
    "delivery_success",
    "send_attempted",
    "email_delivery",
    "production_delivery",
    "delivery_receipt",
    "pdf_generation",
    "recipient_activation",
    "mail_transport_enabled",
}

REQUIRED_BLOCKERS = {
    "sample receipt only",
    "no delivery attempted",
    "no provider confirmation",
    "no recipient activation",
    "real delivery not authorized",
}

LIVE_PROOF_KEY_MARKERS = {
    "provider_confirmation",
    "transport_message_id",
    "message_id",
    "recipient_email",
    "recipient_address",
    "sent_at",
    "delivered_at",
    "delivery_timestamp",
}

LIVE_PROOF_VALUE_MARKERS = {
    "smtp",
    "sendgrid",
    "mailgun",
    "gmail",
    "outlook",
    "message-id",
    "@",
}


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("delivery receipt failed: JSON root must be an object")
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
        raise RuntimeError(f"delivery receipt failed: {key} must remain false")


def _looks_like_live_proof(key: str, value: Any) -> bool:
    lowered_key = key.lower()
    if lowered_key in LIVE_PROOF_KEY_MARKERS and value is not None:
        if value not in ([], {}, "", "none"):
            return True
    if lowered_key not in LIVE_PROOF_KEY_MARKERS and not lowered_key.startswith("metadata"):
        return False
    if isinstance(value, str):
        lowered_value = value.lower().strip()
        if not lowered_value:
            return False
        if lowered_value in {"none", "sample_only", "sample_only_not_delivery"}:
            return False
        if any(marker in lowered_value for marker in LIVE_PROOF_VALUE_MARKERS):
            return True
        if re.search(r"\b[A-Za-z0-9_-]{16,}\b", value):
            return True
    return False


def validate_delivery_receipt(path: Path) -> dict[str, Any]:
    payload = _load(path)

    missing_top = _missing(REQUIRED_TOP_LEVEL, payload)
    if missing_top:
        raise RuntimeError(
            "delivery receipt failed: missing top-level key(s): " + ", ".join(missing_top)
        )

    if payload["schema_version"] != SCHEMA_VERSION:
        raise RuntimeError(
            f"delivery receipt failed: unsupported schema_version={payload['schema_version']}"
        )

    if payload["status"] not in ALLOWED_STATUS:
        raise RuntimeError("delivery receipt failed: status must be sample_only_not_delivery")

    if payload["receipt_type"] not in ALLOWED_RECEIPT_TYPE:
        raise RuntimeError("delivery receipt failed: receipt_type must be sample_only")

    for key in REQUIRED_FALSE_FLAGS:
        _require_false(payload, key)

    if payload["channel"] not in ALLOWED_CHANNEL:
        raise RuntimeError("delivery receipt failed: channel must be none")

    if payload["recipient_reference"] is not None:
        raise RuntimeError("delivery receipt failed: recipient_reference must be null")

    if payload["provider_confirmation"] is not None:
        raise RuntimeError("delivery receipt failed: provider_confirmation must be null")

    if payload["transport_message_id"] is not None:
        raise RuntimeError("delivery receipt failed: transport_message_id must be null")

    if payload["delivery_artifact_paths"] != []:
        raise RuntimeError("delivery receipt failed: delivery_artifact_paths must be an empty list")

    blockers = payload["blockers"]
    if not isinstance(blockers, list):
        raise RuntimeError("delivery receipt failed: blockers must be a list")
    missing_blockers = sorted(REQUIRED_BLOCKERS - set(blockers))
    if missing_blockers:
        raise RuntimeError(
            "delivery receipt failed: missing blocker(s): " + ", ".join(missing_blockers)
        )

    for key, value in _iter_items(payload):
        if _looks_like_live_proof(key, value):
            raise RuntimeError(
                f"delivery receipt failed: {key} contains live-delivery-proof-like value"
            )

    result = {
        "schema_version": "etf_eu_delivery_receipt_validation_v1",
        "status": "sample_only_not_delivery_valid",
        "receipt_path": str(path),
        "delivery_attempted": False,
        "delivery_success": False,
        "send_attempted": False,
        "email_delivery": False,
        "delivery_receipt": False,
        "production_delivery": False,
        "pdf_generation": False,
        "recipient_activation": False,
        "mail_transport_enabled": False,
    }

    print(
        "ETF_EU_DELIVERY_RECEIPT_SAMPLE_OK | "
        f"receipt={path} | delivery_attempted=false | delivery_success=false | production_delivery=false"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt")
    args = parser.parse_args()
    validate_delivery_receipt(Path(args.receipt))


if __name__ == "__main__":
    main()
