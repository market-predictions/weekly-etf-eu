from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_email_dry_run_v1"
ALLOWED_STATUS = {"design_only_blocked"}
ALLOWED_RECIPIENT_ALLOWLIST_STATUS = {
    "not_configured",
    "placeholder_only",
    "configured_but_inactive",
}
ALLOWED_DELIVERY_MANIFEST_STATUS = {"not_available", "placeholder", "available"}
ALLOWED_PDF_STATUS = {"not_available", "shadow_paths_available"}

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "run_id",
    "created_at_utc",
    "report_date",
    "status",
    "recipient_allowlist_status",
    "subject_preview",
    "body_preview",
    "attachment_paths",
    "delivery_manifest_path",
    "delivery_manifest_status",
    "pdf_paths_or_null",
    "pdf_status",
    "send_attempted",
    "email_delivery",
    "delivery_receipt",
    "production_delivery",
    "authority",
    "blockers",
}

REQUIRED_AUTHORITY_FALSE = {
    "mail_transport_configured",
    "external_mail_api_enabled",
    "send_function_present",
    "recipient_activation",
    "pdf_generation",
    "email_delivery",
    "delivery_receipt",
    "production_delivery",
}

FORBIDDEN_TOP_LEVEL_KEYS = {
    "mail_transport_config",
    "live_delivery_config",
    "active_recipient_list",
    "receipt_proof_path",
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _missing(required: set[str], payload: dict[str, Any]) -> list[str]:
    return sorted(required - set(payload))


def _require_false(payload: dict[str, Any], key: str) -> None:
    if payload.get(key) is not False:
        raise RuntimeError(f"email dry-run failed: {key} must remain false")


def validate_email_dry_run(path: Path) -> None:
    payload = _load(path)

    missing_top = _missing(REQUIRED_TOP_LEVEL, payload)
    if missing_top:
        raise RuntimeError(f"email dry-run failed: missing top-level key(s): {', '.join(missing_top)}")

    forbidden = sorted(FORBIDDEN_TOP_LEVEL_KEYS & set(payload))
    if forbidden:
        raise RuntimeError(f"email dry-run failed: forbidden delivery key(s): {', '.join(forbidden)}")

    if payload["schema_version"] != SCHEMA_VERSION:
        raise RuntimeError(f"email dry-run failed: unsupported schema_version={payload['schema_version']}")

    if payload["status"] not in ALLOWED_STATUS:
        raise RuntimeError(f"email dry-run failed: unsupported status={payload['status']}")

    if payload["recipient_allowlist_status"] not in ALLOWED_RECIPIENT_ALLOWLIST_STATUS:
        raise RuntimeError(
            "email dry-run failed: recipient_allowlist_status must remain inactive for WP12"
        )

    for key in ("subject_preview", "body_preview", "run_id", "report_date", "created_at_utc"):
        if not isinstance(payload[key], str) or not payload[key].strip():
            raise RuntimeError(f"email dry-run failed: {key} must be a non-empty string")

    if not isinstance(payload["attachment_paths"], list):
        raise RuntimeError("email dry-run failed: attachment_paths must be a list")

    if payload["delivery_manifest_status"] not in ALLOWED_DELIVERY_MANIFEST_STATUS:
        raise RuntimeError(
            f"email dry-run failed: unsupported delivery_manifest_status={payload['delivery_manifest_status']}"
        )

    delivery_manifest_path = payload["delivery_manifest_path"]
    if delivery_manifest_path is not None and not isinstance(delivery_manifest_path, str):
        raise RuntimeError("email dry-run failed: delivery_manifest_path must be a string or null")
    if delivery_manifest_path in ("",):
        raise RuntimeError("email dry-run failed: delivery_manifest_path must use null, not an empty string")
    if delivery_manifest_path is None and payload["delivery_manifest_status"] != "not_available":
        raise RuntimeError(
            "email dry-run failed: missing delivery_manifest_path requires delivery_manifest_status=not_available"
        )

    if payload["pdf_status"] not in ALLOWED_PDF_STATUS:
        raise RuntimeError(f"email dry-run failed: unsupported pdf_status={payload['pdf_status']}")

    pdf_paths = payload["pdf_paths_or_null"]
    if pdf_paths is not None and not isinstance(pdf_paths, list):
        raise RuntimeError("email dry-run failed: pdf_paths_or_null must be a list or null")
    if pdf_paths is None and payload["pdf_status"] != "not_available":
        raise RuntimeError("email dry-run failed: null pdf paths require pdf_status=not_available")

    for key in ("send_attempted", "email_delivery", "delivery_receipt", "production_delivery"):
        _require_false(payload, key)

    authority = payload["authority"]
    if not isinstance(authority, dict):
        raise RuntimeError("email dry-run failed: authority must be an object")

    missing_authority = _missing(REQUIRED_AUTHORITY_FALSE, authority)
    if missing_authority:
        raise RuntimeError(
            f"email dry-run failed: authority missing required key(s): {', '.join(missing_authority)}"
        )

    for key in REQUIRED_AUTHORITY_FALSE:
        if authority[key] is not False:
            raise RuntimeError(f"email dry-run failed: authority.{key} must remain false")

    blockers = payload["blockers"]
    if not isinstance(blockers, list) or not blockers:
        raise RuntimeError("email dry-run failed: blockers must be a non-empty list")

    if "send_attempted=false" not in blockers:
        raise RuntimeError("email dry-run failed: blockers must include send_attempted=false")
    if payload["delivery_manifest_status"] == "not_available" and "delivery_manifest_status=not_available" not in blockers:
        raise RuntimeError("email dry-run failed: missing delivery manifest blocker")
    if payload["pdf_status"] == "not_available" and "pdf_status=not_available" not in blockers:
        raise RuntimeError("email dry-run failed: missing PDF blocker")

    print(
        "ETF_EU_EMAIL_DRY_RUN_OK | "
        f"artifact={path} | send_attempted=false | email_delivery=false | production_delivery=false"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_email_dry_run(Path(args.artifact))


if __name__ == "__main__":
    main()
